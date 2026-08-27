"""The hierarchical negative-binomial GLM: its configuration, design, fit and forecast.

Imported by `train.py` and `predict.py`, which are thin: everything that both of them
have to agree about lives here, because a design matrix built twice is a design matrix
that will eventually be built two different ways.

## The model

For province `i` and month `t`, the reported count is a negative-binomial draw whose mean
is log-linear:

    y[i,t] ~ NegBin(mean = m[i,t], dispersion = phi)

    log m[i,t] = log(population[i])                       # offset, if population=offset
               + a                                        # global level
               + sum_k ( c_k cos(2 pi k month / 12)
                       + s_k sin(2 pi k month / 12) )      # shared annual season, k = 1, 2
               + sum_c g_c * z[c, i, t - L]                # standardised lagged climate
               + u[i]                                     # province level
               + v[i, year(t)]                            # province-year level

`u` and `v` are the hierarchy. They are not free parameters: each is penalised toward zero
by a variance estimated from the data, so a province with a short or noisy record is pulled
toward the common level and a province with twelve full years is not. That is what "pooled
toward a common level" means, and it is why the model has 194 parameters on about 1 900
observations without being hopeless.

`v` is also where the forecast gets its width. A forecast month lies in a year the fit
never saw, so `v[i, year]` cannot be estimated for it and is drawn from its own estimated
distribution instead. The spread of annual dengue activity around a province's own average
therefore enters every forecast as uncertainty rather than being quietly set to zero. The
reference model this project is measured against carries a per-district, per-year effect
for the same reason, and batch 7 found both of this project's baselines badly
under-dispersed -- 0.65 coverage against a nominal 0.80 -- which is the failure this term
is there to avoid.

## How it is fitted

Penalised maximum likelihood by Fisher scoring, with the two variances and the dispersion
re-estimated between rounds:

1. given the variances and `phi`, maximise the penalised log-likelihood over all
   coefficients -- one linear solve per round, since the negative binomial with a log link
   has an analytic score and expected information;
2. update each variance from the fitted effects plus their posterior variances, which is
   the EM update and is what stops the estimate collapsing to zero;
3. update `phi` by a one-dimensional search on the profile likelihood.

Repeat until the variances and `phi` stop moving. This is an empirical-Bayes fit, not a
sampler: the posterior is then approximated by a normal centred at the fitted coefficients
with the inverse of the penalised information as its covariance -- the Laplace
approximation. Forecast draws come from that normal, from the prior on `v`, and from the
negative binomial on top of both.

What is given up by not sampling: the approximation is symmetric on the log scale and
takes no account of skewness in the posterior of the variance components themselves. What
is bought: a fit in under a second, on three pinned dependencies, that is exactly
reproducible from a seed. The sibling families in the tree are where a different bargain
gets struck.

## Seeds

Nothing here draws. All randomness is in `predict.py`, from one NumPy generator seeded with
the `seed` option -- derived from the project seed and written into the configuration file
by the node above this model.
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

DEFAULTS = {
    "observation": "negative_binomial",
    "covariates": ["rainfall", "mean_temperature"],
    "covariate_lag_months": 2,
    "population": "offset",
    "fit_time": "train",
    "seed": 0,
}

# Which option values this code actually implements. A sibling of a fork that has not been
# built yet must fail loudly here rather than be silently served the main path's
# behaviour: a run that reported a zero-inflated model and fitted a plain one would be
# wrong in a way nothing downstream could detect.
IMPLEMENTED = {
    "observation": ("negative_binomial",),
    "population": ("offset", "covariate", "ignored"),
    "fit_time": ("train",),
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
    options["covariate_lag_months"] = int(options["covariate_lag_months"])
    options["seed"] = int(options["seed"])
    return options


def month_index(period: str) -> int:
    """Months since year 0, so that adjacency is arithmetic rather than string order."""
    text = str(period)
    year, month = int(text[:4]), int(text[5:7]) if "-" in text else int(text[4:6])
    return year * 12 + (month - 1)


def add_features(frame: pd.DataFrame, options: dict) -> pd.DataFrame:
    """Month bookkeeping and the per-province lagged covariate columns.

    The lag is taken through a (location, month-index) lookup rather than a row shift, so
    a frame that is out of order or has a gap gives a missing value rather than a wrong
    one silently borrowed from a neighbouring province.
    """
    out = frame.copy()
    out["_m"] = [month_index(p) for p in out["time_period"]]
    out["_month"] = [(m % 12) + 1 for m in out["_m"]]
    out["_year"] = [m // 12 for m in out["_m"]]
    lag = options["covariate_lag_months"]
    for covariate in options["covariates"]:
        if covariate not in out.columns:
            raise SystemExit(f"covariate {covariate!r} is configured but is not a column "
                             f"of the frame handed to this model")
        lookup = dict(zip(zip(out["location"], out["_m"], strict=True),
                          pd.to_numeric(out[covariate], errors="coerce"), strict=True))
        out[f"{covariate}_lag"] = [
            lookup.get((location, m - lag), np.nan)
            for location, m in zip(out["location"], out["_m"], strict=True)
        ]
    return out


def standardisation(frame: pd.DataFrame, options: dict) -> dict:
    """Centre and scale for every continuous column, computed on the training frame only.

    Stored in the fitted model and applied unchanged at predict time. Computing it again
    from the expanded historic frame would let information from after the training period
    into the fit through the back door.
    """
    stats: dict[str, dict[str, float]] = {}
    for covariate in options["covariates"]:
        column = pd.to_numeric(frame[f"{covariate}_lag"], errors="coerce").to_numpy(float)
        finite = column[np.isfinite(column)]
        spread = float(finite.std(ddof=0))
        stats[covariate] = {"mean": float(finite.mean()), "sd": spread if spread > 0 else 1.0}
    if options["population"] == "covariate":
        column = np.log(frame["population"].to_numpy(float))
        spread = float(column.std(ddof=0))
        stats["log_population"] = {"mean": float(column.mean()),
                                   "sd": spread if spread > 0 else 1.0}
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
    lag = options["covariate_lag_months"]
    for covariate in options["covariates"]:
        raw = pd.to_numeric(frame[f"{covariate}_lag"], errors="coerce").to_numpy(float)
        z = (raw - stats[covariate]["mean"]) / stats[covariate]["sd"]
        # A missing lag becomes the standardised mean, which is this covariate
        # contributing nothing. Training rows with a missing lag are dropped instead;
        # this branch is for forecast rows, where dropping is not an option and the
        # count of them is reported by the caller.
        columns.append(np.nan_to_num(z, nan=0.0))
        names.append(f"{covariate}_lag{lag}_z")
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


def _count_table(y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Unique counts and how often each occurs, so the log-gamma terms are cheap."""
    values, counts = np.unique(y, return_counts=True)
    return values, counts.astype(float)


def _nb_loglik(table: tuple[np.ndarray, np.ndarray], y: np.ndarray, mu: np.ndarray,
               phi: float) -> float:
    """Negative-binomial log-likelihood at mean `mu` and dispersion `phi`."""
    values, counts = table
    n = float(counts.sum())
    lgamma_y_plus_phi = float(sum(c * math.lgamma(v + phi) for v, c in zip(values, counts, strict=True)))
    lgamma_y_plus_one = float(sum(c * math.lgamma(v + 1.0) for v, c in zip(values, counts, strict=True)))
    return (lgamma_y_plus_phi
            - n * math.lgamma(phi)
            - lgamma_y_plus_one
            + n * phi * math.log(phi)
            - float(np.sum((y + phi) * np.log(phi + mu)))
            + float(np.sum(y * np.log(np.maximum(mu, 1e-12)))))


def _fit_dispersion(table, y: np.ndarray, mu: np.ndarray,
                    low: float = -6.0, high: float = 9.0, rounds: int = 60) -> float:
    """The `phi` maximising the profile likelihood, by golden-section search on log phi.

    A one-dimensional bounded search rather than a Newton step on the digamma score: it
    needs no derivative of the log-gamma function, and sixty rounds close the interval far
    past the precision anything downstream cares about.
    """
    ratio = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = low, high
    c, d = b - ratio * (b - a), a + ratio * (b - a)
    fc, fd = _nb_loglik(table, y, mu, math.exp(c)), _nb_loglik(table, y, mu, math.exp(d))
    for _ in range(rounds):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - ratio * (b - a)
            fc = _nb_loglik(table, y, mu, math.exp(c))
        else:
            a, c, fc = c, d, fd
            d = a + ratio * (b - a)
            fd = _nb_loglik(table, y, mu, math.exp(d))
    return math.exp((a + b) / 2.0)


def _fisher_scoring(X: np.ndarray, y: np.ndarray, off: np.ndarray, penalty: np.ndarray,
                    phi: float, theta: np.ndarray, rounds: int = 200,
                    tol: float = 1e-9) -> tuple[np.ndarray, np.ndarray, int]:
    """Maximise the penalised log-likelihood over all coefficients. Returns theta and H.

    `H` is the penalised expected information at the maximum, which is both the matrix
    the step is solved against and the inverse covariance of the Laplace approximation.
    """
    for round_index in range(1, rounds + 1):
        eta = np.clip(X @ theta + off, -ETA_CLIP, ETA_CLIP)
        mu = np.exp(eta)
        weight = mu * phi / (phi + mu)
        score = (y - mu) * phi / (phi + mu)
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
    mu = np.exp(eta)
    weight = mu * phi / (phi + mu)
    H = X.T @ (X * weight[:, None])
    H[np.diag_indices_from(H)] += penalty
    return theta, H, round_index


def fit(design: dict, rounds: int = 200, tol: float = 1e-7) -> dict:
    """The empirical-Bayes fit. `design` comes from `build_design`."""
    X, y, off = design["X"], design["y"], design["offset"]
    n_fixed, n_province, n_province_year = (
        design["n_fixed"], design["n_province"], design["n_province_year"])
    province_slice = slice(n_fixed, n_fixed + n_province)
    province_year_slice = slice(n_fixed + n_province, X.shape[1])

    table = _count_table(y)
    theta = np.zeros(X.shape[1])
    sigma2_province, sigma2_province_year, phi = 1.0, 1.0, 1.0
    history = []

    for outer in range(1, rounds + 1):
        penalty = np.concatenate([
            np.zeros(n_fixed),
            np.full(n_province, 1.0 / sigma2_province),
            np.full(n_province_year, 1.0 / sigma2_province_year),
        ])
        theta, H, inner = _fisher_scoring(X, y, off, penalty, phi, theta)
        covariance = np.linalg.inv(H)

        u = theta[province_slice]
        v = theta[province_year_slice]
        # The EM update: the fitted effects understate the variance on their own, because
        # they are shrunken point estimates. Adding their posterior variances is what
        # keeps the estimate from collapsing toward zero round after round.
        new_province = max(
            (float(u @ u) + float(np.trace(covariance[province_slice, province_slice])))
            / max(n_province, 1), 1e-8)
        new_province_year = max(
            (float(v @ v) + float(np.trace(covariance[province_year_slice, province_year_slice])))
            / max(n_province_year, 1), 1e-8)

        mu = np.exp(np.clip(X @ theta + off, -ETA_CLIP, ETA_CLIP))
        new_phi = _fit_dispersion(table, y, mu)

        moved = max(
            abs(new_province - sigma2_province) / max(sigma2_province, 1e-8),
            abs(new_province_year - sigma2_province_year) / max(sigma2_province_year, 1e-8),
            abs(new_phi - phi) / max(phi, 1e-8),
        )
        sigma2_province, sigma2_province_year, phi = new_province, new_province_year, new_phi
        history.append({"round": outer, "inner_rounds": inner,
                        "sigma_province": math.sqrt(sigma2_province),
                        "sigma_province_year": math.sqrt(sigma2_province_year),
                        "dispersion": phi,
                        "loglik": _nb_loglik(table, y, mu, phi)})
        if moved < tol:
            break

    penalty = np.concatenate([
        np.zeros(n_fixed),
        np.full(n_province, 1.0 / sigma2_province),
        np.full(n_province_year, 1.0 / sigma2_province_year),
    ])
    theta, H, _ = _fisher_scoring(X, y, off, penalty, phi, theta)
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
        "sigma2_province_year": sigma2_province_year,
        "dispersion": phi,
        "cholesky": chol,
        "converged": bool(moved < tol),
        "rounds": outer,
        "history": history,
        "loglik": history[-1]["loglik"],
    }


def build_design(frame: pd.DataFrame, options: dict, stats: dict) -> dict:
    """The training design: fixed columns, province dummies, province-year dummies.

    Rows are used only where the target and every configured covariate lag are present.
    Dropping a row for a missing lag rather than imputing it is the conservative choice
    at fit time -- it costs the first two months of each province's record and leaves the
    coefficient estimated on data that actually exists.
    """
    prepared = add_features(frame, options)
    lag_columns = [f"{c}_lag" for c in options["covariates"]]
    usable = prepared["disease_cases"].notna()
    for column in lag_columns:
        usable &= pd.to_numeric(prepared[column], errors="coerce").notna()
    used = prepared[usable].sort_values(["location", "_m"]).reset_index(drop=True)
    if used.empty:
        raise SystemExit("no usable training rows: every row is missing the target or a "
                         "configured covariate lag")

    provinces = sorted(used["location"].unique())
    province_index = {p: i for i, p in enumerate(provinces)}
    province_years = sorted({(p, int(y)) for p, y in zip(used["location"], used["_year"],
                                                         strict=True)})
    province_year_index = {k: i for i, k in enumerate(province_years)}

    F, fixed_names = fixed_design(used, options, stats)
    n = len(used)
    U = np.zeros((n, len(provinces)))
    U[np.arange(n), [province_index[p] for p in used["location"]]] = 1.0
    V = np.zeros((n, len(province_years)))
    V[np.arange(n), [province_year_index[(p, int(y))]
                     for p, y in zip(used["location"], used["_year"], strict=True)]] = 1.0

    return {
        "X": np.hstack([F, U, V]),
        "y": used["disease_cases"].to_numpy(float),
        "offset": offset(used, options),
        "n_fixed": F.shape[1],
        "n_province": len(provinces),
        "n_province_year": len(province_years),
        "fixed_names": fixed_names,
        "provinces": provinces,
        "province_years": [[p, y] for p, y in province_years],
        "rows_used": n,
        "rows_dropped": int(len(prepared) - n),
        "first_period": str(used["time_period"].min()),
        "last_period": str(used["time_period"].max()),
    }
