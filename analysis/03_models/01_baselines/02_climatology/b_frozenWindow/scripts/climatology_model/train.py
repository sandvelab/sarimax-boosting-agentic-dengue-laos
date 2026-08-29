"""Fit the frozen seasonal climatology baseline: what each province usually did this month.

A climatology forecast needs no fitting in the sense a regression does. What it needs is a
table -- for each province and each calendar month, the counts observed in that month across
the years available -- and the predictive distribution is that table's empirical
distribution, which is a distribution already rather than a point that has to have one
wrapped around it.

**This table is the model.** Unlike the sibling construction, which rebuilds the table from
the expanding historic frame chap-core hands `predict` at every split, this child freezes it
here: what the model knows is what was in the training frame, and it knows nothing more for
the rest of the backtest. That is what a model fitted once and deployed actually has, and it
is the question this fork asks. On this dataset the training period ends 2007-12 and the
evaluation runs to 2009-12, so the frozen table ignores two years of a series whose reporting
has been improving throughout -- which is why the difference between the two children is a
result and not an implementation detail.

The two children therefore carry the same table build. It is duplicated rather than shared
because a Chap contract directory is copied whole into the run directory and a library
outside it does not travel with the model; the fork's substance is in `predict.py`, and both
`train.py` files are the same computation under different values of one recorded field.

Seeds: none. Nothing here is random -- the fit is a table of observed counts, and
`predict.py` turns them into draws by evaluating a quantile function at fixed levels rather
than by sampling. So Rule 6 is satisfied by there being nothing to seed, and the project seed
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

# A province-month needs at least this many observed years to get its own distribution.
# Below it, the province's whole observed record is used instead -- the same fallback
# shape the persistence baseline uses, and recorded rather than silent.
MIN_YEARS = 3


def calendar_month(period: str) -> int:
    text = str(period)
    return int(text[5:7]) if "-" in text else int(text[4:6])


def fit(train_data_path: str, model_path: str) -> dict:
    frame = pd.read_csv(train_data_path)
    frame = frame.dropna(subset=["disease_cases"]).copy()
    frame["month"] = [calendar_month(p) for p in frame["time_period"]]

    provinces = sorted(frame["location"].unique())
    by_province: dict[str, dict[str, list[int]]] = {}
    province_pooled: dict[str, list[int]] = {}
    fallback: dict[str, list[str]] = {}

    for province in provinces:
        block = frame[frame["location"] == province]
        province_pooled[province] = sorted(int(round(v)) for v in block["disease_cases"])
        for month in range(1, 13):
            values = sorted(int(round(v)) for v in block[block["month"] == month]["disease_cases"])
            if len(values) >= MIN_YEARS:
                by_province.setdefault(province, {})[str(month)] = values
            else:
                fallback.setdefault(province, []).append(str(month))

    model = {
        "model": "seasonal_climatology_frozen",
        "construction": "empirical distribution of the counts observed in the same "
                        "calendar month, within the same province",
        "window": "frozen: the table this script builds is the one predict.py uses at every split",
        "min_years_for_own_distribution": MIN_YEARS,
        "training": {
            "observed_rows": int(len(frame)),
            "provinces": len(provinces),
            "first_period": str(frame["time_period"].min()),
            "last_period": str(frame["time_period"].max()),
        },
        "province_months_on_fallback": fallback,
        "values_by_province_month": by_province,
        "values_by_province": province_pooled,
    }

    Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))
    print(
        f"seasonal_climatology_frozen fitted on {model['training']['observed_rows']} observed rows "
        f"({model['training']['first_period']}..{model['training']['last_period']}), "
        f"{len(provinces)} provinces -> {model_path}"
    )
    return model


if __name__ == "__main__":
    fit(sys.argv[1], sys.argv[2])
