"""Fit the parametric persistence baseline: the dispersion of a negative binomial.

The point forecast of a persistence model is the last observed value and needs no fitting.
What needs fitting is the *spread* around it, and this is the second of the two published
constructions for that: a negative binomial whose mean is the previous observation, floored
so the distribution does not collapse when nothing was observed, and whose dispersion is
estimated by maximum likelihood from the last few observations. The sibling
`a_empiricalChange` is the non-parametric construction and is the main path; what the two
disagree about is this node's claim.

**The constants are the source's, not ours.** The floor of 0.2, the window of five
observations and the maximum-likelihood fit all come from the KIT baseline for the German
COVID-19 Forecast Hub (<https://github.com/KITmetricslab/KIT-baseline>, read 2026-08-26
and re-read 2026-08-29), which states them as: set the predictive mean to the observed
number in the previous period; if none was observed set it to 0.2, "necessary to avoid zero
variance in parametric predictive distribution"; and "estimate overdispersion parameter of a
negative binomial distribution from the last five observations (maximum likelihood; with the
respective means as defined above)". Choosing any of them ourselves would let the path not
taken be tuned against the path taken, which is the one thing a stability fork must not
permit.

**What this script stores, and what `predict.py` does instead.** The construction estimates
the dispersion from *the last five observations*, which at forecast time means the last five
available then. chap-core fits this model once and hands `predict` an expanding historic
window at every split, so `predict.py` re-estimates there — the same treatment the sibling
gives its anchor, and the only reading under which the mean and the dispersion come from the
same window, as they do in the source. This script therefore stores the estimate as it
stood at the end of the *training* frame: it is the record of what the model knew at fitting
time, and it is the fallback for a province the historic frame cannot fit.

Seeds: none. The fit is a deterministic search on a fixed grid and `predict.py` turns the
fitted distribution into draws by evaluating its quantile function at fixed levels rather
than by sampling. Rule 6 is satisfied by there being nothing to seed, and project seed
20260822 has no surface in this model. Verified rather than asserted:
`AI-internal/useful-scripts/verify_model_determinism.sh`.

The fitted object is JSON, not a pickle: it outlives the session (`AGENTS.md` Rule 5).

Usage:  python train.py <train_data.csv> <model_out.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from negbinom import R_MAX, R_MIN, fit_dispersion

# The floor on the predictive mean, from the source named above. It is what stops the
# distribution collapsing when the previous observation is zero -- which on this dataset is
# 56 % of observed months, so it is the constant this node's claim says is doing visible
# work, and it is the source's rather than ours.
FLOOR = 0.2

# The window the dispersion is estimated from, from the same source. Five *weekly*
# observations there and five *monthly* ones here: the window is much longer in time and
# much thinner in dengue seasons, and that difference is a property of transplanting the
# construction, not something to be repaired by choosing a different number.
RECENT = 5

# Below this many usable pairs a province gets the pooled estimate instead. Two is the
# fewest from which a dispersion is estimated at all rather than read off one residual.
MIN_PAIRS = 2


def month_index(period: str) -> int:
    """Months since year 0, so that adjacency is arithmetic rather than string order."""
    text = str(period)
    year, month = int(text[:4]), int(text[5:7]) if "-" in text else int(text[4:6])
    return year * 12 + (month - 1)


def recent_pairs(frame: pd.DataFrame, window: int = RECENT) -> tuple[list[float], list[float]]:
    """The last `window` pairs (mean = previous month floored, observed) in one province.

    Consecutive months only: a pair whose previous month is missing has no mean under this
    construction, so it is not a pair. The pairs are taken from the end of the frame,
    which is what "the last five observations" means.
    """
    observed = frame.dropna(subset=["disease_cases"])
    by_month = {month_index(p): float(v) for p, v
                in zip(observed["time_period"], observed["disease_cases"], strict=True)}
    pairs = [(max(by_month[m - 1], FLOOR), by_month[m])
             for m in sorted(by_month) if m - 1 in by_month]
    tail = pairs[-window:]
    return [y for _, y in tail], [mu for mu, _ in tail]


def fit(train_data_path: str, model_path: str) -> dict:
    frame = pd.read_csv(train_data_path)
    provinces = sorted(frame["location"].unique())

    per_province: dict[str, dict] = {}
    fallback: list[str] = []
    pooled_y: list[float] = []
    pooled_mu: list[float] = []

    for province in provinces:
        y, mu = recent_pairs(frame[frame["location"] == province])
        pooled_y.extend(y)
        pooled_mu.extend(mu)
        if len(y) >= MIN_PAIRS:
            per_province[province] = fit_dispersion(y, mu)
        else:
            fallback.append(province)

    if not pooled_y:
        raise SystemExit("no province has two consecutive observed months in the "
                         "training frame; the dispersion cannot be estimated")
    pooled = fit_dispersion(pooled_y, pooled_mu)

    at_bound = {where: sorted(p for p, f in per_province.items() if f["at_bound"] == where)
                for where in ("lower", "upper")}
    observed = frame["disease_cases"].notna()
    model = {
        "model": "persistence_negbinomial_floor",
        "construction": "negative binomial about the last observed count, mean floored at "
                        f"{FLOOR}, dispersion by maximum likelihood from the last "
                        f"{RECENT} observations",
        "source": "KIT baseline, German COVID-19 Forecast Hub "
                  "(https://github.com/KITmetricslab/KIT-baseline)",
        "floor": FLOOR,
        "recent_observations": RECENT,
        "min_pairs_for_own_dispersion": MIN_PAIRS,
        "dispersion_bounds": [R_MIN, R_MAX],
        "dispersion_window": "training frame; predict.py re-estimates from the historic "
                             "frame at each split and falls back to this",
        "training": {
            "rows": int(len(frame)),
            "provinces": len(provinces),
            "first_period": str(frame["time_period"].min()),
            "last_period": str(frame["time_period"].max()),
            "observed_target_cells": int(observed.sum()),
            "missing_target_cells": int((~observed).sum()),
        },
        "provinces_at_a_dispersion_bound": at_bound,
        "provinces_on_pooled_fallback": fallback,
        "dispersion_pooled": pooled,
        "dispersion_by_province": per_province,
    }

    Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))
    print(
        f"persistence_negbinomial_floor fitted on {model['training']['rows']} rows "
        f"({model['training']['first_period']}..{model['training']['last_period']}), "
        f"{len(provinces)} provinces; {len(at_bound['lower'])} at the lower dispersion "
        f"bound, {len(at_bound['upper'])} at the upper -> {model_path}"
    )
    return model


if __name__ == "__main__":
    fit(sys.argv[1], sys.argv[2])
