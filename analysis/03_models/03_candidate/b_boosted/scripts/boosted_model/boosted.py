"""The gradient-boosted candidate: its configuration, features, fit and forecast.

Imported by `train.py` and `predict.py`, which are thin, for the reason candidate 1's
module gives: a design matrix built twice is a design matrix that will eventually be
built two different ways.

## The model

Two pieces, and the split between them is the whole shape of this candidate:

1. **where the count sits.** Histogram gradient-boosted regression trees over a feature
   matrix of lagged climate, lagged counts and province size. Trees make no functional
   assumption at all: no link between covariate and count beyond monotone splits, no
   additivity, no assumption that the effect of rainfall is the same in a large province
   and a small one. What they cannot do is extrapolate — a tree's prediction outside the
   range of its training data is the value of the nearest leaf, forever.
2. **how wide the distribution around it is.** A boosted tree returns one number per cell,
   so unlike candidate 1 this family does not produce a predictive distribution as a
   by-product of being fitted. The distribution has to be constructed, and `02_head` is
   the choice of how. **This is where batch 4 said the family fails**, and it is why the
   head is a fork rather than a decision inside the code.

## The two choices, and where they come from

Every option below is decided by one fork node above this model and reaches it in a file.
This module implements them; it chooses none of them.

| option | values | fork |
|---|---|---|
| `features`, `count_lags`, `climate_lags`, `climate_columns` | see `MLproject` | `01_features` |
| `head` | `negative_binomial`, `quantile_ensemble` | `02_head` |

**`negative_binomial` derives the width from the level.** One booster is fitted for the
conditional mean under a Poisson deviance loss, and a single negative-binomial dispersion
is estimated by maximum likelihood on the training fit. Every cell then gets the same
mean–variance relation, so a cell the model is unsure about is wide only in so far as its
predicted level is high. Candidate 1's diagnosis was that its own width was wrong locally
rather than on average; this head cannot repair that by construction, and saying so before
running it is what makes the comparison with the sibling worth making.

**`quantile_ensemble` learns the width per cell.** A ladder of boosters, each fitted to a
different quantile of the same target under the pinball loss, traces out a whole
conditional distribution; the forecast is drawn from it by inverting the ladder. Nothing
ties the levels together during fitting, so the fitted quantiles can cross, and the repair
is stated here rather than hidden: they are made monotone by a cumulative maximum before
anything is drawn, and how much repair was needed is recorded in the fitted object.

## What is a fork here and what is not

`01_features` and `02_head` are forks. The boosting hyper-parameters — shrinkage, tree
size, leaf minimum, L2 penalty, rounds — are **not**, and that is a decision with a
reason rather than an omission. They are set once, at values that are conventional for a
few thousand rows, and the number of rounds is then chosen by the data through a
time-ordered early-stopping split. Making them forks would enumerate a grid whose siblings
all have to be re-run in phase D and on the holdout, to answer a question about tuning
rather than about a judgment call an analyst would plausibly make differently. The plan's
§3 asks that every judgment call be a node **or** a logged decision; this is the second,
and it is logged in the node's claim, in this docstring and in the specification the fork
children write.

**No standardisation anywhere.** A tree splits on order, so centring and scaling a column
changes nothing about the fit. Candidate 1 standardises because a coefficient on an
unstandardised column is not comparable with another; here there are no coefficients.

**Missing values are handled by the trees rather than by us.** The boosters learn a
default direction for a missing feature at every split, so a row whose lag falls before
the start of the record is a usable row rather than a dropped one. Candidate 1 drops those
rows. It is a real difference between the families and not a tuning choice: this model is
fitted on every month that reports a count, and candidate 1 is not.

## Where the fitted model is stored, and why it is not a pickle

`AGENTS.md` Rule 5 forbids a language-specific pickle for anything outliving the session,
and the fitted object outlives it — chap-core writes it between `train` and `predict`, and
the node copies it into `results/`. So the fitted ensembles are **written out as JSON**:
one record per tree, holding the split feature, the threshold, the direction a missing
value takes, the two children and the leaf values, as parallel arrays.

`raw_predict` below walks that structure. It is not a re-implementation of the fit — the
fit is scikit-learn's — but it is a second prediction path, and a second path is a path
that can disagree. So `fit_model` checks it: every booster's stored form is evaluated on
the training rows and compared with what scikit-learn's own `predict` returns, and the
largest absolute difference is recorded in the fitted object. A run whose difference is
not at machine precision fails rather than being quietly forecast from.

What this buys is that the fitted model is a document. Batch 21 found that the greedy
branch's rule selected a configuration under which the model has no stored fitted object
at all, and that a rule selecting on development CRPS cannot see that. Here the object is
not merely stored but readable without scikit-learn installed.

## Seeds

Nothing here draws except `draw`, which is handed a generator by `predict.py`. That
generator is seeded with the `seed` option — derived from the project seed and written
into the configuration file by the node above this model. The boosters take the same seed
as their `random_state`; with early stopping disabled and no subsampling they are
deterministic regardless, and setting it is belt and braces rather than a requirement.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# scikit-learn is imported inside `_booster`, not here. Everything this module does with a
# model that has already been fitted -- reading the stored form, walking its trees,
# drawing from a head -- needs only numpy and pandas, and the docstring above promises
# that the fitted object can be read without scikit-learn. A module-level import would
# make that promise false for anyone importing the module rather than the file.

# Harmonics of the annual cycle offered to `rich_calendar`. Two, matching candidate 1, so
# that the calendar is described to the two families in the same terms.
HARMONICS = 2

# Windows, in months, of the rolling summaries `rich_calendar` adds. Each ends at the
# freshest lag the forecast can see, so a rolling mean never contains a month the
# forecast's own horizon puts out of reach.
ROLLING_WINDOWS = (3, 6, 12)

# The shortest lag of the target a model serving all three horizons may use. Chap asks
# for three months at a time, so the freshest count the third month of a block can see is
# three months old. Enforced in `read_options`, not merely declared in `MLproject`.
MIN_COUNT_LAG = 3

# The ladder `quantile_ensemble` fits. It carries 0.10, 0.25, 0.75 and 0.90 because those
# are the levels the project's calibration numbers are computed at, so the head's own
# nominal intervals are ones it was fitted to rather than ones interpolated between
# neighbours; and it carries 0.01 and 0.99 because a dengue month's upper tail is where
# a count model is most easily wrong and a ladder stopping at 0.95 would leave the top of
# every forecast to the extrapolation rule below rather than to a fitted value.
QUANTILES = (0.01, 0.05, 0.10, 0.20, 0.25, 0.30, 0.40, 0.50,
             0.60, 0.70, 0.75, 0.80, 0.90, 0.95, 0.99)

# The linear predictor of the mean head is exponentiated; the same clip candidate 1 uses,
# and for the same reason. e^30 is 10^13 cases.
ETA_CLIP = 30.0

DEFAULTS = {
    "features": "lag_block",
    "head": "negative_binomial",
    "count_lags": [3, 4, 5, 6, 12],
    "climate_lags": [0, 1, 2, 3],
    "climate_columns": ["rainfall", "mean_temperature", "mean_relative_humidity"],
    "learning_rate": 0.05,
    "max_iter": 400,
    "max_leaf_nodes": 15,
    "min_samples_leaf": 20,
    "l2_regularization": 1.0,
    "validation_fraction": 0.15,
    "seed": 0,
}

# Which option values this code implements. A sibling of a fork that has not been built
# must fail loudly rather than be silently served the main path's behaviour: a run that
# reported a quantile ensemble and fitted a negative binomial would be wrong in a way
# nothing downstream could detect.
IMPLEMENTED = {
    "features": ("lag_block", "rich_calendar"),
    "head": ("negative_binomial", "quantile_ensemble"),
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

    options["count_lags"] = sorted({int(v) for v in options["count_lags"]})
    options["climate_lags"] = sorted({int(v) for v in options["climate_lags"]})
    options["climate_columns"] = list(options["climate_columns"])
    if not options["climate_columns"]:
        options["climate_lags"] = []
    # The horizon constraint, checked rather than trusted. A configuration asking for the
    # previous month's count would fit beautifully and could not be evaluated at the
    # third month of any block, which is the kind of error that shows up as an
    # unexplained score rather than as a failure.
    too_fresh = [lag for lag in options["count_lags"] if lag < MIN_COUNT_LAG]
    if too_fresh:
        raise SystemExit(
            f"count_lags {too_fresh} are shorter than {MIN_COUNT_LAG} months. Chap asks "
            f"for {MIN_COUNT_LAG} months at a time, so a model serving every horizon "
            f"cannot see a count fresher than that at the last of them.")
    options["seed"] = int(options["seed"])
    return options


# --------------------------------------------------------------------------- features


def month_index(period: str) -> int:
    """Months since year 0, so that adjacency is arithmetic rather than string order."""
    text = str(period)
    year, month = int(text[:4]), int(text[5:7]) if "-" in text else int(text[4:6])
    return year * 12 + (month - 1)


def climate_columns(options: dict) -> list[tuple[str, str, int]]:
    """(column name, source column, lag) for every configured climate-and-lag pair."""
    return [(f"{c}_lag{lag}", c, lag)
            for c in options["climate_columns"] for lag in options["climate_lags"]]


def count_columns(options: dict) -> list[tuple[str, int]]:
    """(column name, lag) for every configured lag of the target itself."""
    return [(f"cases_lag{lag}", lag) for lag in options["count_lags"]]


def rolling_columns(options: dict) -> list[tuple[str, int]]:
    """(column name, window) for the rolling summaries `rich_calendar` adds."""
    if options["features"] != "rich_calendar":
        return []
    return [(f"cases_mean{w}_from_lag{MIN_COUNT_LAG}", w) for w in ROLLING_WINDOWS]


def _lagged(out: pd.DataFrame, source: str, lag: int, name: str) -> None:
    """Write `source` shifted `lag` months into `name`, per province.

    Through a (location, month-index) lookup rather than a row shift, so a frame that is
    out of order or has a gap gives a missing value rather than a wrong one silently
    borrowed from a neighbouring province. The same construction candidate 1 uses.
    """
    lookup = dict(zip(zip(out["location"], out["_m"], strict=True),
                      pd.to_numeric(out[source], errors="coerce"), strict=True))
    out[name] = [lookup.get((location, m - lag), np.nan)
                 for location, m in zip(out["location"], out["_m"], strict=True)]


def _rolling(out: pd.DataFrame, window: int, name: str) -> None:
    """Mean of log1p(count) over `window` months ending at the freshest visible lag.

    The window ends at `MIN_COUNT_LAG`, not at the previous month, so a rolling summary
    never contains a month the forecast's own horizon puts out of reach. A window with no
    observed month in it is missing rather than zero.
    """
    lookup = dict(zip(zip(out["location"], out["_m"], strict=True),
                      np.log1p(pd.to_numeric(out["disease_cases"], errors="coerce")),
                      strict=True))
    values = []
    for location, m in zip(out["location"], out["_m"], strict=True):
        seen = [lookup.get((location, m - MIN_COUNT_LAG - k)) for k in range(window)]
        seen = [v for v in seen if v is not None and np.isfinite(v)]
        values.append(float(np.mean(seen)) if seen else np.nan)
    out[name] = values


def add_features(frame: pd.DataFrame, options: dict) -> pd.DataFrame:
    """Month bookkeeping, the lagged columns and any rolling summary."""
    out = frame.copy()
    out["_m"] = [month_index(p) for p in out["time_period"]]
    out["_month"] = [(m % 12) + 1 for m in out["_m"]]
    out["_year"] = [m // 12 for m in out["_m"]]
    for name, source, lag in climate_columns(options):
        if source not in out.columns:
            raise SystemExit(f"climate column {source!r} is configured but is not a "
                             f"column of the frame handed to this model")
        _lagged(out, source, lag, name)
    if "disease_cases" not in out.columns:
        raise SystemExit("this model always uses lagged counts and the frame handed to "
                         "it has no disease_cases column")
    for name, lag in count_columns(options):
        _lagged(out, "disease_cases", lag, name)
    for name, window in rolling_columns(options):
        _rolling(out, window, name)
    return out


def feature_names(options: dict) -> list[str]:
    """The design's columns, in the order `design` builds them.

    Stored in the fitted model and checked at predict time, because a booster applied to
    a matrix whose columns are in a different order is a booster giving confident wrong
    answers rather than an error.
    """
    names = [name for name, _, _ in climate_columns(options)]
    names += [f"log1p_{name}" for name, _ in count_columns(options)]
    names += ["log_population"]
    if options["features"] == "rich_calendar":
        names += [f"cos{k}" for k in range(1, HARMONICS + 1)]
        names += [f"sin{k}" for k in range(1, HARMONICS + 1)]
        names += ["year_index", "province_code"]
        names += [f"log1p_{name}" for name, _ in rolling_columns(options)]
    return names


def design(frame: pd.DataFrame, options: dict, provinces: list[str],
           year_base: int) -> np.ndarray:
    """The feature matrix. No standardisation: a tree splits on order.

    `provinces` and `year_base` come from the fit, so a province the training frame never
    held gets a missing code rather than a new one, and the year index at predict time is
    measured from the same origin the fit used.
    """
    n = len(frame)
    code = {p: float(i) for i, p in enumerate(provinces)}
    columns: list[np.ndarray] = []

    for name, _, _ in climate_columns(options):
        columns.append(pd.to_numeric(frame[name], errors="coerce").to_numpy(float))
    for name, _ in count_columns(options):
        columns.append(np.log1p(pd.to_numeric(frame[name], errors="coerce").to_numpy(float)))
    columns.append(np.log(pd.to_numeric(frame["population"], errors="coerce").to_numpy(float)))

    if options["features"] == "rich_calendar":
        month = frame["_month"].to_numpy(float)
        for k in range(1, HARMONICS + 1):
            columns.append(np.cos(2 * np.pi * k * month / 12))
        for k in range(1, HARMONICS + 1):
            columns.append(np.sin(2 * np.pi * k * month / 12))
        # A trend the trees cannot extrapolate: every forecast year is beyond the last
        # training year, so this column puts every forecast row in the last bin the fit
        # saw. That is a property of the family and the reason the fork exists, not a
        # defect to be patched here.
        columns.append(frame["_year"].to_numpy(float) - year_base)
        columns.append(np.array([code.get(p, np.nan) for p in frame["location"]]))
        for name, _ in rolling_columns(options):
            columns.append(pd.to_numeric(frame[name], errors="coerce").to_numpy(float))

    matrix = np.column_stack(columns) if columns else np.empty((n, 0))
    names = feature_names(options)
    if matrix.shape[1] != len(names):
        raise SystemExit(f"design built {matrix.shape[1]} columns and names {len(names)}; "
                         f"the two are written from the same options and must agree")
    return matrix


# ------------------------------------------------------------- the boosters, stored


def _tree(nodes) -> dict:
    """One fitted tree as parallel arrays: what `raw_predict` needs and nothing else.

    Parallel arrays rather than a record per node, because the fitted object is stored on
    disk once per combination and the difference is several megabytes.
    """
    if nodes["is_categorical"].any():
        raise SystemExit("a fitted tree has a categorical split; this model passes no "
                         "categorical features and the stored form does not carry the "
                         "bitsets such a split would need")
    return {
        "feature": [int(v) for v in nodes["feature_idx"]],
        "threshold": [float(v) for v in nodes["num_threshold"]],
        "missing_left": [int(v) for v in nodes["missing_go_to_left"]],
        "left": [int(v) for v in nodes["left"]],
        "right": [int(v) for v in nodes["right"]],
        "value": [float(v) for v in nodes["value"]],
        "is_leaf": [int(v) for v in nodes["is_leaf"]],
    }


def dump_booster(booster, link: str) -> dict:
    """A fitted booster in a form that needs no scikit-learn to evaluate."""
    trees = [_tree(predictor.nodes)
             for stage in booster._predictors for predictor in stage]
    return {
        "baseline": float(np.asarray(booster._baseline_prediction).ravel()[0]),
        "link": link,
        "n_trees": len(trees),
        "n_nodes": sum(len(t["value"]) for t in trees),
        "trees": trees,
    }


def _tree_predict(tree: dict, X: np.ndarray) -> np.ndarray:
    """Walk one stored tree for every row of `X` at once."""
    feature = np.asarray(tree["feature"], dtype=np.int64)
    threshold = np.asarray(tree["threshold"], dtype=float)
    missing_left = np.asarray(tree["missing_left"], dtype=bool)
    left = np.asarray(tree["left"], dtype=np.int64)
    right = np.asarray(tree["right"], dtype=np.int64)
    value = np.asarray(tree["value"], dtype=float)
    is_leaf = np.asarray(tree["is_leaf"], dtype=bool)

    node = np.zeros(len(X), dtype=np.int64)
    while True:
        moving = np.flatnonzero(~is_leaf[node])
        if not len(moving):
            return value[node]
        here = node[moving]
        seen = X[moving, feature[here]]
        go_left = np.where(np.isnan(seen), missing_left[here], seen <= threshold[here])
        node[moving] = np.where(go_left, left[here], right[here])


def raw_predict(dump: dict, X: np.ndarray) -> np.ndarray:
    """The booster's output on its own scale, from the stored form alone."""
    out = np.full(len(X), dump["baseline"], dtype=float)
    for tree in dump["trees"]:
        out += _tree_predict(tree, X)
    return out


def response_predict(dump: dict, X: np.ndarray) -> np.ndarray:
    """The booster's output on the scale of what it was fitted to."""
    raw = raw_predict(dump, X)
    return np.exp(np.clip(raw, -ETA_CLIP, ETA_CLIP)) if dump["link"] == "log" else raw


# ------------------------------------------------------------------------- the fit


def _booster(options: dict, loss: str, rounds: int, quantile: float | None = None):
    """One booster at this node's fixed hyper-parameters.

    `early_stopping=False` always: the number of rounds is chosen by `_rounds` on a
    time-ordered split and then passed in here, rather than by scikit-learn's own
    randomly drawn validation set. A stopping decision made on rows interleaved with the
    training rows is made on months the model has effectively seen.
    """
    from sklearn.ensemble import HistGradientBoostingRegressor

    return HistGradientBoostingRegressor(
        loss=loss,
        quantile=quantile,
        learning_rate=options["learning_rate"],
        max_iter=rounds,
        max_leaf_nodes=options["max_leaf_nodes"],
        min_samples_leaf=options["min_samples_leaf"],
        l2_regularization=options["l2_regularization"],
        early_stopping=False,
        random_state=options["seed"],
    )


def _poisson_deviance(y: np.ndarray, mu: np.ndarray) -> float:
    mu = np.maximum(mu, 1e-9)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(y > 0, y * np.log(y / mu), 0.0)
    return float(2.0 * np.sum(term - (y - mu)))


def _pinball(y: np.ndarray, prediction: np.ndarray, level: float) -> float:
    error = y - prediction
    return float(np.sum(np.maximum(level * error, (level - 1.0) * error)))


def _rounds(X: np.ndarray, y: np.ndarray, later: np.ndarray, options: dict,
            loss: str, quantile: float | None) -> dict:
    """How many boosting rounds, chosen on the latest months of the training frame.

    Fit on the earlier rows, score every round on the later ones, take the round with the
    lowest loss. The split is by month, not at random: the question the backtest asks is
    how the model does on the period after the one it was fitted on, and a stopping rule
    that does not ask the same question is choosing a model for a different problem.

    Falls back to the configured maximum when the split leaves nothing to score on, which
    is what happens if a combination ever fits on so few months that 15 % of them is
    none. The fallback is recorded rather than silent.
    """
    earlier = ~later
    if not later.any() or not earlier.any():
        return {"rounds": options["max_iter"], "chosen_on": "the configured maximum: "
                "the time-ordered split left one side empty", "loss_at_chosen": None}

    trial = _booster(options, loss, options["max_iter"], quantile)
    trial.fit(X[earlier], y[earlier])
    score = _poisson_deviance if loss == "poisson" else (
        lambda a, b: _pinball(a, b, quantile))
    losses = [score(y[later], prediction)
              for prediction in trial.staged_predict(X[later])]
    best = int(np.argmin(losses))
    return {"rounds": best + 1,
            "chosen_on": f"{int(later.sum())} rows in the latest months of the "
                         f"training frame, scored at every round",
            "loss_at_chosen": float(losses[best]),
            "loss_at_max_rounds": float(losses[-1])}


def _fit_dispersion(y: np.ndarray, mu: np.ndarray,
                    low: float = -6.0, high: float = 9.0, rounds: int = 80) -> float:
    """The negative binomial's dispersion by maximum likelihood at fixed means.

    A ternary search on log-dispersion. The profile log-likelihood in this parameter is
    unimodal, so a bracketing search needs no derivative and cannot walk off; the bounds
    are the ones candidate 1's dispersion search uses, for the same reason.
    """
    def loglik(log_phi: float) -> float:
        phi = math.exp(log_phi)
        return float(np.sum(
            [math.lgamma(v + phi) for v in y]
        ) - len(y) * math.lgamma(phi)
            - float(np.sum([math.lgamma(v + 1.0) for v in y]))
            + len(y) * phi * math.log(phi)
            - float(np.sum((y + phi) * np.log(phi + mu)))
            + float(np.sum(y * np.log(np.maximum(mu, 1e-12)))))

    for _ in range(rounds):
        a = low + (high - low) / 3.0
        b = high - (high - low) / 3.0
        if loglik(a) < loglik(b):
            low = a
        else:
            high = b
    return math.exp((low + high) / 2.0)


def _later_months(frame: pd.DataFrame, fraction: float) -> np.ndarray:
    """A boolean mask on the latest whole months making up about `fraction` of the rows."""
    months = np.sort(frame["_m"].unique())
    wanted = fraction * len(frame)
    taken, cut = 0, len(months)
    for position in range(len(months) - 1, -1, -1):
        taken += int((frame["_m"] == months[position]).sum())
        cut = position
        if taken >= wanted:
            break
    return (frame["_m"] >= months[cut]).to_numpy(bool) if cut < len(months) else \
        np.zeros(len(frame), dtype=bool)


def usable_rows(prepared: pd.DataFrame) -> pd.DataFrame:
    """Every month that reports a count, in a fixed order.

    A missing lag does not disqualify a row: the boosters learn a direction for a missing
    feature at every split, so the earliest months of the record are fitted on rather than
    dropped. Sorting by (location, month) makes the training matrix a function of the
    frame's contents and not of the order it arrived in.
    """
    target = pd.to_numeric(prepared["disease_cases"], errors="coerce")
    return (prepared[target.notna()]
            .sort_values(["location", "_m"]).reset_index(drop=True))


def fit_model(frame: pd.DataFrame, options: dict) -> dict:
    """Fit the whole model on `frame` and return the object `draw` needs."""
    prepared = add_features(frame, options)
    used = usable_rows(prepared)
    if used.empty:
        raise SystemExit("no row of the training frame reports a count")

    provinces = sorted(used["location"].unique())
    year_base = int(used["_year"].min())
    X = design(used, options, provinces, year_base)
    y = pd.to_numeric(used["disease_cases"], errors="coerce").to_numpy(float)
    later = _later_months(used, options["validation_fraction"])

    boosters: list[dict] = []
    stopping: list[dict] = []
    checks: list[float] = []

    def fit_one(loss: str, link: str, target: np.ndarray,
                quantile: float | None = None) -> dict:
        chosen = _rounds(X, target, later, options, loss, quantile)
        booster = _booster(options, loss, chosen["rounds"], quantile)
        booster.fit(X, target)
        dump = dump_booster(booster, link)
        # The stored form is a second prediction path, and a second path can disagree.
        # Checked here on the training rows rather than trusted.
        checks.append(float(np.max(np.abs(
            response_predict(dump, X) - booster.predict(X)))))
        stopping.append({"quantile": quantile, **chosen})
        return dump

    if options["head"] == "negative_binomial":
        boosters.append(fit_one("poisson", "log", y))
        mu = response_predict(boosters[0], X)
        dispersion = _fit_dispersion(y, mu)
        quantile_levels: list[float] = []
        crossing = None
    else:
        # The ladder is fitted to log1p(count). A quantile is equivariant under a monotone
        # transform, so the quantile of the transformed target back-transforms exactly to
        # the quantile of the count -- which a mean would not. Fitting on the raw scale
        # would let one province reporting thousands set the loss for all sixteen.
        target = np.log1p(y)
        quantile_levels = list(QUANTILES)
        for level in quantile_levels:
            boosters.append(fit_one("quantile", "identity", target, quantile=level))
        ladder = np.column_stack([np.maximum(raw_predict(d, X), 0.0) for d in boosters])
        repaired = np.maximum.accumulate(ladder, axis=1)
        # How much repair the crossing needed, on the training rows. A ladder needing a
        # great deal of it is a head whose quantiles were fitted without reference to
        # each other and are behaving like it, and that belongs in the record.
        crossing = {
            "rows": int(len(ladder)),
            "rows_with_a_crossing": int(np.sum(np.any(repaired > ladder + 1e-12, axis=1))),
            "max_repair_log1p": float(np.max(repaired - ladder)),
            "mean_repair_log1p": float(np.mean(repaired - ladder)),
        }
        dispersion = None

    worst_check = max(checks)
    if not worst_check < 1e-6:
        raise SystemExit(
            f"the stored form of a booster does not reproduce scikit-learn's own "
            f"prediction: largest absolute difference {worst_check:g}. The fitted model "
            f"is written as JSON and read back by this module's own traversal, so a "
            f"disagreement here means the forecast would not be the fitted model's.")

    return {
        "model": "boosted_candidate",
        "construction": (
            "histogram gradient-boosted regression trees over lagged climate, lagged "
            "counts and province size, with the predictive distribution built around "
            f"them by the {options['head']} head"),
        "options": options,
        "head": options["head"],
        "features": options["features"],
        "feature_names": feature_names(options),
        "provinces": provinces,
        "year_base": year_base,
        "boosters": boosters,
        "quantile_levels": quantile_levels,
        "dispersion": dispersion,
        "quantile_crossing_on_training_rows": crossing,
        "training": {
            "rows": int(len(frame)),
            "rows_used": int(len(used)),
            "rows_dropped_missing_target": int(len(prepared) - len(used)),
            "rows_with_a_missing_feature": int(np.sum(np.any(~np.isfinite(X), axis=1))),
            "provinces": len(provinces),
            "first_period": str(used["time_period"].min()),
            "last_period": str(used["time_period"].max()),
            "observed_zero_share": float((y == 0).mean()),
            "early_stopping_rows": int(later.sum()),
            "early_stopping_first_period": (str(used.loc[later, "time_period"].min())
                                            if later.any() else None),
        },
        "fit": {
            "boosters": len(boosters),
            "rounds": [s["rounds"] for s in stopping],
            "rounds_cap": options["max_iter"],
            "hit_the_cap": [s["rounds"] == options["max_iter"] for s in stopping],
            "early_stopping": stopping,
            "stored_form_max_abs_difference": worst_check,
            "trees": sum(d["n_trees"] for d in boosters),
            "nodes": sum(d["n_nodes"] for d in boosters),
        },
    }


# ---------------------------------------------------------------------------- forecast


def _ladder(model: dict, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The monotone quantile ladder for every row, and the levels it sits at.

    Two repairs, both stated: predictions below zero on the log1p scale are raised to
    zero, because log1p of a count cannot be negative; and the levels are made
    non-decreasing across the ladder by a cumulative maximum, because the boosters were
    fitted independently and nothing during fitting stopped the 0.30 booster predicting
    above the 0.40 one.
    """
    ladder = np.column_stack([np.maximum(raw_predict(d, X), 0.0)
                             for d in model["boosters"]])
    return np.maximum.accumulate(ladder, axis=1), np.asarray(model["quantile_levels"])


def draw(model: dict, rows: pd.DataFrame, options: dict, rng: np.random.Generator,
         n_samples: int) -> np.ndarray:
    """`n_rows x n_samples` integer forecast draws, under the configured head."""
    X = design(rows, options, model["provinces"], model["year_base"])
    if model["feature_names"] != feature_names(options):
        raise SystemExit("the feature matrix at predict time does not have the columns "
                         "the model was fitted on; refusing to forecast")

    if model["head"] == "negative_binomial":
        mu = response_predict(model["boosters"][0], X)
        phi = float(model["dispersion"])
        return rng.negative_binomial(phi, phi / (phi + mu[:, None]),
                                     size=(len(X), n_samples))

    ladder, levels = _ladder(model, X)
    # The ladder is extended to both ends before it is inverted. Below the lowest fitted
    # level it runs down to a count of zero, which is where the data's own lower tail is.
    # Above the highest it continues at the slope of the last fitted segment, so the top
    # of the distribution keeps growing at the rate the fit last measured rather than
    # stopping flat at the 0.99 quantile.
    slope = ((ladder[:, -1] - ladder[:, -2]) / (levels[-1] - levels[-2])).clip(min=0.0)
    grid = np.concatenate(([0.0], levels, [1.0]))
    values = np.column_stack([
        np.zeros(len(X)), ladder, ladder[:, -1] + slope * (1.0 - levels[-1])])

    uniform = rng.random((len(X), n_samples))
    drawn = np.empty((len(X), n_samples))
    for position in range(len(X)):
        drawn[position] = np.interp(uniform[position], grid, values[position])
    return np.rint(np.expm1(drawn)).clip(min=0).astype(int)
