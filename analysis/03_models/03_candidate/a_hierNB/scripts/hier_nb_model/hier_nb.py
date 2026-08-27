"""The hierarchical negative-binomial GLM: its configuration, design, fit and forecast.

Imported by `train.py` and `predict.py`, which are thin: everything that both of them
have to agree about lives here, because a design matrix built twice is a design matrix
that will eventually be built two different ways.

## The model

For province `i` and month `t`, the reported count is a draw from a count distribution
whose mean is log-linear:

    y[i,t] ~ Count(mean = m[i,t], dispersion = phi)

    log m[i,t] = log(population[i])                       # offset, if population=offset
               + a                                        # global level
               + sum_k ( c_k cos(2 pi k month / 12)
                       + s_k sin(2 pi k month / 12) )      # shared annual season, k = 1, 2
               + sum_(c,L) g_(c,L) * z[c, i, t - L]        # standardised lagged climate
               + h * z[log1p(y[i, t - 3])]                 # if autoregressive = lag3
               + u[i]                                     # province level
               + v[i, year(t)]                            # province-year level

`u` and `v` are the hierarchy. They are not free parameters: each is penalised toward zero
by a variance estimated from the data, so a province with a short or noisy record is pulled
toward the common level and a province with twelve full years is not. That is what "pooled
toward a common level" means, and it is why the model has around 200 parameters on about
1 900 observations without being hopeless.

`v` is also where the forecast gets its width. A forecast month lies in a year the fit
never saw, so `v[i, year]` cannot be estimated for it and is drawn from its own estimated
distribution instead. The spread of annual dengue activity around a province's own average
therefore enters every forecast as uncertainty rather than being quietly set to zero.

## The six choices, and where they come from

Every option below is decided by one fork node above this model and reaches it in a file.
This module implements them; it chooses none of them.

| option | values | fork |
|---|---|---|
| `observation` | `negative_binomial`, `zero_inflated`, `hurdle` | `01_observation` |
| `covariates`, `covariate_lags` | column names, lags in months | `02_covariates` |
| `population` | `offset`, `covariate`, `ignored` | `03_population` |
| `fit_time` | `train`, `predict` | `04_fitTime` |
| `autoregressive` | `none`, `lag3` | `05_autoregressive` |
| `year_variance` | `shared`, `province_scaled` | `06_yearVariance` |

**The three observation models are three positions on the zeros.** A plain negative
binomial says the zeros and the over-dispersion are the same fact and one stretched
distribution carries both. `zero_inflated` says a share of the zeros come from a reporting
process that never had a chance to record a case, and mixes a point mass at zero with the
same negative binomial. `hurdle` says the decision to report anything at all and the size
of what is reported are two different processes, and fits them separately: a logistic model
for whether the month is non-zero, and a count model for how large it is given that it is.

The hurdle's positive part is a negative binomial on `y - 1`, which is a shifted count
distribution rather than a zero-truncated one. It is the cheaper of the two standard
constructions and it uses this module's existing fit unchanged; what it gives up is that
the positive part's mean is not the same functional as the plain model's, so its
coefficients are not comparable with the other two observation models'. They were never
going to be compared -- the fork is compared on what it forecasts.

**`autoregressive = lag3` is available at every horizon and that is why it is lag 3.**
Chap asks for three months at a time, so the most recent count a forecast month can see is
three months old at the longest lead and no fresher at the shortest, if the same model is
to serve all three. A shorter lag would be a model that cannot forecast the third month.

**`year_variance = province_scaled` estimates one annual variance per province** instead of
one shared by all. On the log scale a shared variance is a constant *multiplicative* width,
which is the same relative uncertainty for a province reporting thousands of cases a year
and one reporting four. Whether that is too crude is a question about this dataset, and the
fork is where it gets answered rather than assumed.

## How it is fitted

Penalised maximum likelihood by Fisher scoring, with the variances and any distributional
parameter re-estimated between rounds:

1. given the variances and `phi`, maximise the penalised log-likelihood over all
   coefficients -- one linear solve per round, since both families used here have an
   analytic score and expected information under a canonical-enough link;
2. update each variance from the fitted effects plus their posterior variances, which is
   the EM update and is what stops the estimate collapsing to zero;
3. update `phi` by a one-dimensional search on the profile likelihood, and, where the
   observation model has one, the zero-inflation probability by its EM update.

Repeat until nothing moves. This is an empirical-Bayes fit, not a sampler: the posterior is
then approximated by a normal centred at the fitted coefficients with the inverse of the
penalised information as its covariance -- the Laplace approximation. Forecast draws come
from that normal, from the prior on `v`, and from the observation model on top of both.

What is given up by not sampling: the approximation is symmetric on the log scale and takes
no account of skewness in the posterior of the variance components themselves. What is
bought: a fit in about a second, on three pinned dependencies, exactly reproducible from a
seed. The sibling families in the tree are where a different bargain gets struck.

## Seeds

Nothing here draws except `draw`, which is handed a generator by `predict.py`. That
generator is seeded with the `seed` option -- derived from the project seed and written
into the configuration file by the node above this model.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Harmonics in the shared annual cycle. Two gives a peak and a shoulder, which is the
# shape of a monsoon dengue season; more would start fitting the training years' own
# noise, and the seasonal shape is not what any fork of this node is about.
HARMONICS = 2

# The linear predictor is exponentiated. Clipping keeps a bad step during fitting from
# producing an inf and losing the whole fit; the bound is far outside any plausible log
# rate for this data (e^30 is 10^13 cases).
ETA_CLIP = 30.0

# Which lags of the target each autoregressive option puts in the design. Three months is
# the shortest lag a three-month-ahead forecast can use without seeing its own past
# forecasts, so it is the only one available to a model that serves all three horizons.
AR_LAGS = {"none": (), "lag3": (3,)}

DEFAULTS = {
    "observation": "negative_binomial",
    "covariates": ["rainfall", "mean_temperature"],
    "covariate_lags": [2],
    "population": "offset",
    "fit_time": "train",
    "autoregressive": "none",
    "year_variance": "shared",
    "seed": 0,
}

# Which option values this code implements. A sibling of a fork that has not been built
# must fail loudly here rather than be silently served the main path's behaviour: a run
# that reported a zero-inflated model and fitted a plain one would be wrong in a way
# nothing downstream could detect.
IMPLEMENTED = {
    "observation": ("negative_binomial", "zero_inflated", "hurdle"),
    "population": ("offset", "covariate", "ignored"),
    "fit_time": ("train", "predict"),
    "autoregressive": tuple(AR_LAGS),
    "year_variance": ("shared", "province_scaled"),
}


def read_options(path: str | Path) -> dict:
    """The model configuration, as chap-core hands it to the entry points."""
    document = yaml.safe_load(Path(path).read_text()) or {}
    values = document.get("user_option_values") or {}
    unknown = sorted(set(values) - set(DEFAULTS))
    if unknown:
        raise SystemExit(f"unknown model option(s) {unknown}; this model declares "
                         f"{sorted(DEFAULTS)} in its MLproject")
    options = {**DEFAULTS, **values}
    for key, allowed in IMPLEMENTED.items():
        if options[key] not in allowed:
            raise SystemExit(
                f"option {key}={options[key]!r} is declared but not implemented; "
                f"this model implements {list(allowed)}. The sibling node that would "
                f"take this path has to bring its own code.")
    options["covariates"] = list(options["covariates"])
    # With no covariates there are no lags of them, whatever the file says. A lag list
    # left over from another child would otherwise show up in the specification of a
    # model that has no climate term at all.
    options["covariate_lags"] = (sorted({int(v) for v in options["covariate_lags"]})
                                 if options["covariates"] else [])
    options["seed"] = int(options["seed"])
    return options


# --------------------------------------------------------------------------- features


def month_index(period: str) -> int:
    """Months since year 0, so that adjacency is arithmetic rather than string order."""
    text = str(period)
    year, month = int(text[:4]), int(text[5:7]) if "-" in text else int(text[4:6])
    return year * 12 + (month - 1)


def covariate_columns(options: dict) -> list[tuple[str, str, int]]:
    """(column name, source column, lag) for every configured covariate-and-lag pair."""
    return [(f"{c}_lag{lag}", c, lag)
            for c in options["covariates"] for lag in options["covariate_lags"]]


def target_columns(options: dict) -> list[tuple[str, int]]:
    """(column name, lag) for every configured lag of the target itself."""
    return [(f"cases_lag{lag}", lag) for lag in AR_LAGS[options["autoregressive"]]]


def _lagged(out: pd.DataFrame, source: str, lag: int, name: str) -> None:
    """Write `source` shifted `lag` months into `name`, per province.

    The lag is taken through a (location, month-index) lookup rather than a row shift, so
    a frame that is out of order or has a gap gives a missing value rather than a wrong
    one silently borrowed from a neighbouring province.
    """
    lookup = dict(zip(zip(out["location"], out["_m"], strict=True),
                      pd.to_numeric(out[source], errors="coerce"), strict=True))
    out[name] = [lookup.get((location, m - lag), np.nan)
                 for location, m in zip(out["location"], out["_m"], strict=True)]


def add_features(frame: pd.DataFrame, options: dict) -> pd.DataFrame:
    """Month bookkeeping, the lagged covariate columns and any lagged target column."""
    out = frame.copy()
    out["_m"] = [month_index(p) for p in out["time_period"]]
    out["_month"] = [(m % 12) + 1 for m in out["_m"]]
    out["_year"] = [m // 12 for m in out["_m"]]
    for name, source, lag in covariate_columns(options):
        if source not in out.columns:
            raise SystemExit(f"covariate {source!r} is configured but is not a column "
                             f"of the frame handed to this model")
        _lagged(out, source, lag, name)
    for name, lag in target_columns(options):
        if "disease_cases" not in out.columns:
            raise SystemExit("an autoregressive term is configured but the frame handed "
                             "to this model has no disease_cases column")
        _lagged(out, "disease_cases", lag, name)
    return out


def lag_columns(options: dict) -> list[str]:
    """Every column a row must have in order to be usable at fit time."""
    return ([name for name, _, _ in covariate_columns(options)]
            + [name for name, _ in target_columns(options)])


def standardisation(frame: pd.DataFrame, options: dict) -> dict:
    """Centre and scale for every continuous column, computed on the training frame only.

    Stored in the fitted model and applied unchanged at predict time. Computing it again
    from the expanded historic frame would let information from after the training period
    into the fit through the back door.
    """
    stats: dict[str, dict[str, float]] = {}

    def record(key: str, column: np.ndarray) -> None:
        finite = column[np.isfinite(column)]
        spread = float(finite.std(ddof=0))
        stats[key] = {"mean": float(finite.mean()), "sd": spread if spread > 0 else 1.0}

    for name, _, _ in covariate_columns(options):
        record(name, pd.to_numeric(frame[name], errors="coerce").to_numpy(float))
    for name, _ in target_columns(options):
        counts = pd.to_numeric(frame[name], errors="coerce").to_numpy(float)
        record(name, np.log1p(counts))
    if options["population"] == "covariate":
        record("log_population", np.log(frame["population"].to_numpy(float)))
    return stats


def fixed_design(frame: pd.DataFrame, options: dict, stats: dict) -> tuple[np.ndarray, list[str]]:
    """The columns whose coefficients are not penalised: level, season, covariates."""
    n = len(frame)
    columns = [np.ones(n)]
    names = ["intercept"]
    month = frame["_month"].to_numpy(float)
    for k in range(1, HARMONICS + 1):
        columns += [np.cos(2 * np.pi * k * month / 12), np.sin(2 * np.pi * k * month / 12)]
        names += [f"cos{k}", f"sin{k}"]
    for name, _, lag in covariate_columns(options):
        raw = pd.to_numeric(frame[name], errors="coerce").to_numpy(float)
        z = (raw - stats[name]["mean"]) / stats[name]["sd"]
        # A missing lag becomes the standardised mean, which is this covariate
        # contributing nothing. Training rows with a missing lag are dropped instead;
        # this branch is for forecast rows, where dropping is not an option and the
        # count of them is reported by the caller.
        columns.append(np.nan_to_num(z, nan=0.0))
        names.append(f"{name}_z")
    for name, lag in target_columns(options):
        raw = pd.to_numeric(frame[name], errors="coerce").to_numpy(float)
        z = (np.log1p(raw) - stats[name]["mean"]) / stats[name]["sd"]
        columns.append(np.nan_to_num(z, nan=0.0))
        names.append(f"cases_log1p_lag{lag}_z")
    if options["population"] == "covariate":
        column = np.log(frame["population"].to_numpy(float))
        columns.append((column - stats["log_population"]["mean"]) / stats["log_population"]["sd"])
        names.append("log_population_z")
    return np.column_stack(columns), names


def offset(frame: pd.DataFrame, options: dict) -> np.ndarray:
    """log(population) where population is an offset; zero otherwise."""
    if options["population"] == "offset":
        return np.log(frame["population"].to_numpy(float))
    return np.zeros(len(frame))


# ------------------------------------------------------------------------ likelihoods


def _count_table(y: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Unique counts and the weight on each, so the log-gamma terms are cheap.

    Every log-gamma term in the negative-binomial likelihood depends on the row only
    through its count, so summing the weights per distinct count turns a sum over two
    thousand rows into a sum over a few hundred values -- which matters because the
    dispersion search evaluates the likelihood sixty times per round.
    """
    values = np.unique(y)
    index = np.searchsorted(values, y)
    counts = np.bincount(index, weights=weights, minlength=len(values))
    return values, counts.astype(float)


def _nb_loglik(table: tuple[np.ndarray, np.ndarray], y: np.ndarray, mu: np.ndarray,
               phi: float, weights: np.ndarray) -> float:
    """Weighted negative-binomial log-likelihood at mean `mu` and dispersion `phi`."""
    values, counts = table
    n = float(counts.sum())
    lgamma_y_plus_phi = float(sum(c * math.lgamma(v + phi) for v, c in zip(values, counts, strict=True)))
    lgamma_y_plus_one = float(sum(c * math.lgamma(v + 1.0) for v, c in zip(values, counts, strict=True)))
    return (lgamma_y_plus_phi
            - n * math.lgamma(phi)
            - lgamma_y_plus_one
            + n * phi * math.log(phi)
            - float(np.sum(weights * (y + phi) * np.log(phi + mu)))
            + float(np.sum(weights * y * np.log(np.maximum(mu, 1e-12)))))


def _fit_dispersion(table, y: np.ndarray, mu: np.ndarray, weights: np.ndarray,
                    low: float = -6.0, high: float = 9.0, rounds: int = 60) -> float:
    """The `phi` maximising the profile likelihood, by golden-section search on log phi.

    A one-dimensional bounded search rather than a Newton step on the digamma score: it
    needs no derivative of the log-gamma function, and sixty rounds close the interval far
    past the precision anything downstream cares about.
    """
    ratio = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = low, high
    c, d = b - ratio * (b - a), a + ratio * (b - a)
    fc = _nb_loglik(table, y, mu, math.exp(c), weights)
    fd = _nb_loglik(table, y, mu, math.exp(d), weights)
    for _ in range(rounds):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - ratio * (b - a)
            fc = _nb_loglik(table, y, mu, math.exp(c), weights)
        else:
            a, c, fc = c, d, fd
            d = a + ratio * (b - a)
            fd = _nb_loglik(table, y, mu, math.exp(d), weights)
    return math.exp((a + b) / 2.0)


def _bernoulli_loglik(y: np.ndarray, eta: np.ndarray) -> float:
    """Log-likelihood of the presence indicator under the logistic model."""
    p = np.clip(1.0 / (1.0 + np.exp(-eta)), 1e-12, 1 - 1e-12)
    return float(np.sum(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))


def _nb_zero_probability(mu: np.ndarray, phi: float) -> np.ndarray:
    """P(y = 0) under a negative binomial with mean `mu` and dispersion `phi`."""
    return np.exp(phi * (math.log(phi) - np.log(phi + mu)))


def _score_and_weight(family: str, y: np.ndarray, eta: np.ndarray, phi: float,
                      weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The Fisher-scoring score and working weight, per observation.

    Two families are needed. The negative binomial with a log link carries every count
    model here; the Bernoulli with a logit link carries the hurdle's presence part.
    """
    if family == "negative_binomial":
        mu = np.exp(eta)
        return (weights * (y - mu) * phi / (phi + mu),
                weights * mu * phi / (phi + mu))
    p = 1.0 / (1.0 + np.exp(-eta))
    return weights * (y - p), weights * p * (1.0 - p)


def _fisher_scoring(X: np.ndarray, y: np.ndarray, off: np.ndarray, penalty: np.ndarray,
                    phi: float, theta: np.ndarray, family: str, weights: np.ndarray,
                    rounds: int = 200, tol: float = 1e-9) -> tuple[np.ndarray, np.ndarray, int]:
    """Maximise the penalised log-likelihood over all coefficients. Returns theta and H.

    `H` is the penalised expected information at the maximum, which is both the matrix
    the step is solved against and the inverse covariance of the Laplace approximation.
    """
    for round_index in range(1, rounds + 1):
        eta = np.clip(X @ theta + off, -ETA_CLIP, ETA_CLIP)
        score, weight = _score_and_weight(family, y, eta, phi, weights)
        H = X.T @ (X * weight[:, None])
        H[np.diag_indices_from(H)] += penalty
        gradient = X.T @ score - penalty * theta
        step = np.linalg.solve(H, gradient)
        # A first step from a cold start can be enormous on the log scale. Capping its
        # length costs an iteration or two and removes the only way this loop diverges.
        largest = float(np.max(np.abs(step)))
        if largest > 2.0:
            step = step * (2.0 / largest)
        theta = theta + step
        if largest < tol:
            break
    eta = np.clip(X @ theta + off, -ETA_CLIP, ETA_CLIP)
    _, weight = _score_and_weight(family, y, eta, phi, weights)
    H = X.T @ (X * weight[:, None])
    H[np.diag_indices_from(H)] += penalty
    return theta, H, round_index


# -------------------------------------------------------------------------------- fit


def _year_penalty(design: dict, sigma2_year: np.ndarray) -> np.ndarray:
    """One inverse variance per province-year column, from its province's variance."""
    return 1.0 / sigma2_year[design["province_year_owner"]]


def fit(design: dict, options: dict, family: str = "negative_binomial",
        rounds: int = 200, tol: float = 1e-7) -> dict:
    """The empirical-Bayes fit. `design` comes from `build_design`.

    `family` selects the observation family of *this block*: the count blocks use the
    negative binomial, the hurdle's presence block the Bernoulli. `options` decides the
    variance structure and whether a zero-inflation probability is estimated alongside.
    """
    X, y, off = design["X"], design["y"], design["offset"]
    n_fixed, n_province, n_province_year = (
        design["n_fixed"], design["n_province"], design["n_province_year"])
    province_slice = slice(n_fixed, n_fixed + n_province)
    province_year_slice = slice(n_fixed + n_province, X.shape[1])
    owner = design["province_year_owner"]
    per_province = options["year_variance"] == "province_scaled"
    zero_inflated = family == "negative_binomial" and options["observation"] == "zero_inflated"

    theta = np.zeros(X.shape[1])
    sigma2_province = 1.0
    sigma2_year = np.ones(n_province)
    phi = 1.0
    # The mixing weight starts away from zero on purpose. At exactly zero the E-step
    # gives every zero month a responsibility of one, the M-step returns zero again, and
    # the mixture would sit at the plain negative binomial for ever while reporting
    # itself as zero-inflated. A tenth is a starting value, not an estimate.
    zero_inflation = 0.1 if zero_inflated else 0.0
    weights = np.ones(len(y))
    table = _count_table(y, weights)
    history = []
    moved = float("inf")

    for outer in range(1, rounds + 1):
        penalty = np.concatenate([
            np.zeros(n_fixed),
            np.full(n_province, 1.0 / sigma2_province),
            _year_penalty(design, sigma2_year),
        ])
        theta, H, inner = _fisher_scoring(X, y, off, penalty, phi, theta, family, weights)
        covariance = np.linalg.inv(H)

        u = theta[province_slice]
        v = theta[province_year_slice]
        # The EM update: the fitted effects understate the variance on their own, because
        # they are shrunken point estimates. Adding their posterior variances is what
        # keeps the estimate from collapsing toward zero round after round.
        posterior_u = float(np.trace(covariance[province_slice, province_slice]))
        new_province = max((float(u @ u) + posterior_u) / max(n_province, 1), 1e-8)

        posterior_v = np.diag(covariance)[province_year_slice]
        if per_province:
            # One variance per province, over that province's own year effects. A
            # province with a handful of years gets a noisy estimate and that is the
            # honest cost of the choice; the floor is the only regularisation.
            total = np.bincount(owner, weights=v * v + posterior_v, minlength=n_province)
            count = np.bincount(owner, minlength=n_province)
            new_year = np.maximum(total / np.maximum(count, 1), 1e-8)
        else:
            pooled = max(
                (float(v @ v) + float(np.trace(covariance[province_year_slice, province_year_slice])))
                / max(n_province_year, 1), 1e-8)
            new_year = np.full(n_province, pooled)

        eta = np.clip(X @ theta + off, -ETA_CLIP, ETA_CLIP)
        if family == "negative_binomial":
            mu = np.exp(eta)
            new_phi = _fit_dispersion(table, y, mu, weights)
            if zero_inflated:
                # The E-step: how much of each zero the count model is asked to explain.
                # A positive count can only have come from the count process, so its
                # responsibility is one and its weight never moves.
                f0 = _nb_zero_probability(mu, new_phi)
                mixed = zero_inflation + (1.0 - zero_inflation) * f0
                responsibility = np.where(
                    y > 0, 1.0, (1.0 - zero_inflation) * f0 / np.maximum(mixed, 1e-300))
                new_zero_inflation = float(np.mean(1.0 - responsibility))
                weights = responsibility
                table = _count_table(y, weights)
            else:
                new_zero_inflation = 0.0
        else:
            new_phi, new_zero_inflation = phi, 0.0

        moved = max(
            abs(new_province - sigma2_province) / max(sigma2_province, 1e-8),
            float(np.max(np.abs(new_year - sigma2_year) / np.maximum(sigma2_year, 1e-8))),
            abs(new_phi - phi) / max(phi, 1e-8),
            abs(new_zero_inflation - zero_inflation),
        )
        sigma2_province, sigma2_year = new_province, new_year
        phi, zero_inflation = new_phi, new_zero_inflation
        history.append({"round": outer, "inner_rounds": inner,
                        "sigma_province": math.sqrt(sigma2_province),
                        "sigma_province_year": math.sqrt(float(np.mean(sigma2_year))),
                        "dispersion": phi,
                        "zero_inflation": zero_inflation,
                        "loglik": _nb_loglik(table, y, np.exp(eta), phi, weights)
                        if family == "negative_binomial"
                        else _bernoulli_loglik(y, eta)})
        if moved < tol:
            break

    penalty = np.concatenate([
        np.zeros(n_fixed),
        np.full(n_province, 1.0 / sigma2_province),
        _year_penalty(design, sigma2_year),
    ])
    theta, H, _ = _fisher_scoring(X, y, off, penalty, phi, theta, family, weights)
    covariance = np.linalg.inv(H)

    # Only the level parts are needed at forecast time: the province-year effect of a
    # future year is drawn from its prior, not from the posterior of a year the fit saw.
    keep = np.r_[0:n_fixed, province_slice]
    block = covariance[np.ix_(keep, keep)]
    block = (block + block.T) / 2.0
    jitter = 1e-10 * float(np.trace(block)) / block.shape[0]
    chol = np.linalg.cholesky(block + jitter * np.eye(block.shape[0]))

    return {
        "theta": theta,
        "sigma2_province": sigma2_province,
        "sigma2_year": sigma2_year,
        "dispersion": phi,
        "zero_inflation": zero_inflation,
        "cholesky": chol,
        "converged": bool(moved < tol),
        "rounds": outer,
        "history": history,
        "loglik": history[-1]["loglik"],
    }


def usable_rows(prepared: pd.DataFrame, options: dict) -> pd.DataFrame:
    """The rows a fit may use: target and every configured lag present.

    Dropping a row for a missing lag rather than imputing it is the conservative choice
    at fit time -- it costs the first months of each province's record and leaves the
    coefficient estimated on data that actually exists.
    """
    usable = prepared["disease_cases"].notna()
    for column in lag_columns(options):
        usable &= pd.to_numeric(prepared[column], errors="coerce").notna()
    used = prepared[usable].sort_values(["location", "_m"]).reset_index(drop=True)
    if used.empty:
        raise SystemExit("no usable training rows: every row is missing the target or a "
                         "configured lag")
    return used


def build_design(used: pd.DataFrame, options: dict, stats: dict,
                 y: np.ndarray | None = None, with_offset: bool = True) -> dict:
    """The design for one fitted block: fixed columns, province and province-year dummies.

    `used` has already been through `usable_rows`. `y` overrides the target, which is what
    the hurdle needs: its presence block regresses an indicator and its positive block a
    shifted count, both on the same design.
    """
    provinces = sorted(used["location"].unique())
    province_index = {p: i for i, p in enumerate(provinces)}
    province_years = sorted({(p, int(year)) for p, year in
                             zip(used["location"], used["_year"], strict=True)})
    province_year_index = {k: i for i, k in enumerate(province_years)}

    F, fixed_names = fixed_design(used, options, stats)
    n = len(used)
    U = np.zeros((n, len(provinces)))
    U[np.arange(n), [province_index[p] for p in used["location"]]] = 1.0
    V = np.zeros((n, len(province_years)))
    V[np.arange(n), [province_year_index[(p, int(year))]
                     for p, year in zip(used["location"], used["_year"], strict=True)]] = 1.0

    return {
        "X": np.hstack([F, U, V]),
        "y": used["disease_cases"].to_numpy(float) if y is None else np.asarray(y, float),
        "offset": offset(used, options) if with_offset else np.zeros(n),
        "n_fixed": F.shape[1],
        "n_province": len(provinces),
        "n_province_year": len(province_years),
        # Which province each province-year column belongs to. It is what lets the
        # annual variance be estimated per province instead of once for all of them.
        "province_year_owner": np.array([province_index[p] for p, _ in province_years]),
        "fixed_names": fixed_names,
        "provinces": provinces,
        "province_years": [[p, y] for p, y in province_years],
        "rows_used": n,
        "first_period": str(used["time_period"].min()),
        "last_period": str(used["time_period"].max()),
    }


def _block(design: dict, fitted: dict) -> dict:
    """One fitted block, as it is stored in the model file."""
    theta = fitted["theta"]
    n_fixed, n_province = design["n_fixed"], design["n_province"]
    provinces = design["provinces"]
    sigma_year = np.sqrt(fitted["sigma2_year"])
    return {
        "fixed_names": design["fixed_names"],
        "fixed_effects": dict(zip(design["fixed_names"],
                                  [float(x) for x in theta[:n_fixed]], strict=True)),
        "provinces": provinces,
        "province_effects": {p: float(x) for p, x in
                             zip(provinces, theta[n_fixed:n_fixed + n_province], strict=True)},
        "sigma_province": math.sqrt(fitted["sigma2_province"]),
        "sigma_province_year": float(np.mean(sigma_year)),
        "sigma_province_year_by_province": {p: float(s) for p, s in
                                            zip(provinces, sigma_year, strict=True)},
        "dispersion": fitted["dispersion"],
        "zero_inflation": fitted["zero_inflation"],
        # Lower-triangular Cholesky factor of the Laplace covariance of the fixed effects
        # and the province effects, in that order. It is what `draw` samples coefficient
        # vectors from, and storing the factor rather than the covariance means the
        # forecast never has to re-decompose anything.
        "level_cholesky": [[float(x) for x in row] for row in fitted["cholesky"]],
        "level_names": design["fixed_names"] + [f"province[{p}]" for p in provinces],
        "province_years_seen": design["province_years"],
        "province_year_effects": {
            f"{p}:{year}": float(x) for (p, year), x in
            zip([tuple(k) for k in design["province_years"]],
                theta[n_fixed + n_province:], strict=True)},
        "fit": {"converged": fitted["converged"], "outer_rounds": fitted["rounds"],
                "loglik": fitted["loglik"], "history": fitted["history"]},
    }


def presence_options(options: dict) -> dict:
    """The options the hurdle's presence block is fitted under.

    A population offset is a statement about a rate on the log-mean scale and has no
    meaning on the logit scale, so the presence block takes population as an estimated
    coefficient wherever the count block takes it at all. Saying that here rather than
    inside the fit keeps it a stated choice rather than a branch nobody reads.
    """
    if options["population"] == "ignored":
        return options
    return {**options, "population": "covariate"}


def fit_model(frame: pd.DataFrame, options: dict) -> dict:
    """Fit the whole model on `frame` and return the object `draw` needs.

    Called by `train.py` under `fit_time = train`, and by `predict.py` on the expanded
    historic frame under `fit_time = predict`. One function, so the two cannot drift.
    """
    prepared = add_features(frame, options)
    stats = standardisation(prepared, options)
    used = usable_rows(prepared, options)
    counts = used["disease_cases"].to_numpy(float)

    design = build_design(used, options, stats)
    fitted = fit(design, options)
    model = {
        "model": "hier_nb_candidate",
        "construction": ("hierarchical negative-binomial GLM, empirical-Bayes fit by "
                         "Fisher scoring with EM updates for the variance components"),
        "options": options,
        "observation": options["observation"],
        "standardisation": stats,
        **_block(design, fitted),
        "training": {
            "rows": int(len(frame)),
            "rows_used": design["rows_used"],
            "rows_dropped_missing_target_or_lag": int(len(prepared) - design["rows_used"]),
            "provinces": design["n_province"],
            "province_years": design["n_province_year"],
            "first_period": design["first_period"],
            "last_period": design["last_period"],
            "observed_zero_share": float((counts == 0).mean()),
        },
        "fit": {"converged": fitted["converged"], "outer_rounds": fitted["rounds"],
                "loglik": fitted["loglik"], "history": fitted["history"]},
    }

    if options["observation"] == "hurdle":
        # Two processes, fitted separately on the same rows: whether the month reports
        # anything, and how much it reports given that it does. The count block is
        # refitted on the positive rows against `y - 1`, so the stored top-level block
        # describes the positive part and `presence` the other.
        presence_opts = presence_options(options)
        presence_stats = standardisation(prepared, presence_opts)
        presence_design = build_design(used, presence_opts, presence_stats,
                                       y=(counts > 0).astype(float), with_offset=False)
        presence_fit = fit(presence_design, options, family="bernoulli")

        positive = used[counts > 0].reset_index(drop=True)
        positive_design = build_design(positive, options, stats,
                                       y=positive["disease_cases"].to_numpy(float) - 1.0)
        positive_fit = fit(positive_design, options)

        model["standardisation_presence"] = presence_stats
        model["presence"] = _block(presence_design, presence_fit)
        model.update(_block(positive_design, positive_fit))
        model["training"]["rows_positive"] = int(len(positive))
        model["fit"] = {"converged": bool(presence_fit["converged"] and positive_fit["converged"]),
                        "outer_rounds": max(presence_fit["rounds"], positive_fit["rounds"]),
                        "loglik": positive_fit["loglik"],
                        "history": positive_fit["history"]}
    return model


# ---------------------------------------------------------------------------- forecast


def _linear_predictor(block: dict, rows: pd.DataFrame, options: dict, stats: dict,
                      rng: np.random.Generator, n_samples: int,
                      with_offset: bool) -> np.ndarray:
    """`n_rows x n_samples` draws of the linear predictor for one fitted block.

    Three sources of spread, and each answers a different question about what is not
    known: the coefficients, drawn jointly from the Laplace approximation to their
    posterior; the province-year effect, drawn from its estimated distribution because a
    forecast month lies in a year the fit never saw; and, further out, the observation
    model the caller puts on top.

    The draws are taken in a fixed order -- level, then province-year, then unseen
    provinces -- so that a run is reproducible from the seed alone.
    """
    F, _ = fixed_design(rows, options, stats)
    off = offset(rows, options) if with_offset else np.zeros(len(rows))

    n_fixed = len(block["fixed_names"])
    provinces = list(block["provinces"])
    province_index = {p: i for i, p in enumerate(provinces)}
    mean_level = np.array(
        [block["fixed_effects"][name] for name in block["fixed_names"]]
        + [block["province_effects"][p] for p in provinces])
    cholesky = np.array(block["level_cholesky"])

    level = mean_level[:, None] + cholesky @ rng.standard_normal((len(mean_level), n_samples))
    fixed_draws = level[:n_fixed]
    province_draws = level[n_fixed:]

    sigma_year = block["sigma_province_year_by_province"]
    pooled_year = block["sigma_province_year"]
    sigma_province = block["sigma_province"]

    keys = sorted({(location, int(year)) for location, year in
                   zip(rows["location"], rows["_year"], strict=True)})
    # Drawn once per (province, year) so that the months of a split share it within a
    # sample rather than moving independently.
    province_year_draws = {
        key: rng.standard_normal(n_samples) * sigma_year.get(key[0], pooled_year)
        for key in keys}

    unseen = sorted({p for p in rows["location"] if p not in province_index})
    unseen_draws = {p: rng.standard_normal(n_samples) * sigma_province for p in unseen}

    eta = np.empty((len(rows), n_samples))
    for position in range(len(rows)):
        location = rows.at[position, "location"]
        year = int(rows.at[position, "_year"])
        level_term = (province_draws[province_index[location]]
                      if location in province_index else unseen_draws[location])
        eta[position] = (off[position] + F[position] @ fixed_draws + level_term
                         + province_year_draws[(location, year)])
    return np.clip(eta, -ETA_CLIP, ETA_CLIP)


def draw(model: dict, rows: pd.DataFrame, options: dict, rng: np.random.Generator,
         n_samples: int) -> np.ndarray:
    """`n_rows x n_samples` integer forecast draws, under the configured observation model."""
    eta = _linear_predictor(model, rows, options, model["standardisation"], rng,
                            n_samples, with_offset=True)
    mu = np.exp(eta)
    dispersion = model["dispersion"]
    counts = rng.negative_binomial(dispersion, dispersion / (dispersion + mu))

    if options["observation"] == "zero_inflated":
        # The share of months the fit attributed to a process that reports nothing at
        # all. Applied as a mask, which is what the mixture is.
        counts = np.where(rng.random(counts.shape) < model["zero_inflation"], 0, counts)
    elif options["observation"] == "hurdle":
        presence_eta = _linear_predictor(
            model["presence"], rows, presence_options(options),
            model["standardisation_presence"], rng, n_samples, with_offset=False)
        reports = rng.random(counts.shape) < 1.0 / (1.0 + np.exp(-presence_eta))
        # The count block was fitted on `y - 1` over the positive months, so a month that
        # reports at all reports at least one case.
        counts = np.where(reports, counts + 1, 0)
    return counts
