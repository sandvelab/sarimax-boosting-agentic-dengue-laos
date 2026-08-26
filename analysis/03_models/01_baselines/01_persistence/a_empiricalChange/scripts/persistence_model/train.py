"""Fit the persistence baseline: the empirical distribution of h-step changes.

The point forecast of a persistence model is the last observed value and needs no
fitting. What needs fitting is the *spread* around it, and this script estimates it
the way the field's standard hub baseline does -- from the empirical distribution of
past h-step changes, symmetrised by including each change and its negation so that the
predictive median is exactly the last observed value.

Two published constructions exist for this baseline and they disagree; see README.md.
This is the non-parametric one. It is chosen here because it estimates nothing, needs
no floor to avoid a degenerate distribution at zero counts, and therefore has no
tuning surface at all -- which is what a baseline should have. The parametric
alternative is retained as a documented sibling for the stability work.

Changes are pooled **within a province**, not across provinces: burdens on this
dataset differ by four orders of magnitude, so a pooled absolute-change distribution
would be set by the capital and would be absurdly wide for a province reporting four
cases in twelve years. A province with too few observed pairs falls back to the pooled
distribution, and the fallback is recorded in the fitted model rather than left silent.

Seeds: none. Nothing here is random -- the fit is a set of observed differences, and
`predict.py` turns them into draws by evaluating a quantile function at fixed levels
rather than by sampling. So Rule 6 is satisfied by there being nothing to seed, and the
project seed 20260822 has no surface in this model. Verified rather than asserted:
`AI-internal/useful-scripts/verify_model_determinism.sh`.

The fitted object is JSON, not a pickle: it outlives the session (`AGENTS.md` Rule 5).

Usage:  python train.py <train_data.csv> <model_out.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

# The evaluation horizon. Fixed at 3 by the reference model the project is measured
# against, so the model never needs changes at a longer lead than this.
MAX_HORIZON = 3

# A province needs at least this many observed (y_t, y_t+h) pairs to get its own
# change distribution; below it, the pooled distribution is used instead.
MIN_PAIRS = 10


def month_index(period: str) -> int:
    """Months since year 0, so that adjacency is arithmetic rather than string order."""
    text = str(period)
    year, month = int(text[:4]), int(text[5:7]) if "-" in text else int(text[4:6])
    return year * 12 + (month - 1)


def h_step_changes(frame: pd.DataFrame, horizon: int) -> list[int]:
    """Observed y[t+h] - y[t] within one province, over pairs where both are observed."""
    observed = frame.dropna(subset=["disease_cases"]).copy()
    observed["m"] = [month_index(p) for p in observed["time_period"]]
    by_month = dict(zip(observed["m"], observed["disease_cases"], strict=True))
    return [
        int(round(by_month[m + horizon] - value))
        for m, value in by_month.items()
        if m + horizon in by_month
    ]


def symmetrise(changes: list[int]) -> list[int]:
    """Each change and its negation, sorted.

    Including the negations is what makes the predictive median the last observed
    value: the distribution of changes on a rising epidemic curve is not centred on
    zero, and a baseline that inherited that drift would no longer be a persistence
    forecast.
    """
    return sorted(changes + [-c for c in changes])


def fit(train_data_path: str, model_path: str) -> dict:
    frame = pd.read_csv(train_data_path)
    provinces = sorted(frame["location"].unique())

    per_province: dict[str, dict[str, list[int]]] = {}
    pooled: dict[str, list[int]] = {}
    fallback: dict[str, list[str]] = {}

    for horizon in range(1, MAX_HORIZON + 1):
        key = str(horizon)
        all_changes: list[int] = []
        for province in provinces:
            changes = h_step_changes(frame[frame["location"] == province], horizon)
            all_changes.extend(changes)
            if len(changes) >= MIN_PAIRS:
                per_province.setdefault(province, {})[key] = symmetrise(changes)
            else:
                fallback.setdefault(key, []).append(province)
        pooled[key] = symmetrise(all_changes)

    observed = frame["disease_cases"].notna()
    model = {
        "model": "persistence_baseline",
        "construction": "empirical symmetrised h-step changes, truncated at zero",
        "max_horizon": MAX_HORIZON,
        "min_pairs_for_own_distribution": MIN_PAIRS,
        "training": {
            "rows": int(len(frame)),
            "provinces": len(provinces),
            "first_period": str(frame["time_period"].min()),
            "last_period": str(frame["time_period"].max()),
            "observed_target_cells": int(observed.sum()),
            "missing_target_cells": int((~observed).sum()),
        },
        "pairs_per_horizon": {
            key: sum(len(v[key]) // 2 for v in per_province.values() if key in v)
            for key in pooled
        },
        "provinces_on_pooled_fallback": fallback,
        "changes_pooled": pooled,
        "changes_by_province": per_province,
    }

    Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))
    print(
        f"persistence_baseline fitted on {model['training']['rows']} rows "
        f"({model['training']['first_period']}..{model['training']['last_period']}), "
        f"{len(provinces)} provinces -> {model_path}"
    )
    return model


if __name__ == "__main__":
    fit(sys.argv[1], sys.argv[2])
