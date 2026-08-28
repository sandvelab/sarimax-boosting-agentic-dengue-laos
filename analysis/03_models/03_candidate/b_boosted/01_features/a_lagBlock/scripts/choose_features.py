"""Stage 1 of candidate 2's configuration: a block of lags and nothing else.

The climate columns at every lag from zero to three, the province's own counts at lags
three to six and at twelve, and the log of its population. Time and place reach the model
only through what those numbers imply about them: there is no month, no year, no province
identifier, and no rolling summary. The sibling `b_richCalendar` adds all four.

**Why climate may be taken at lag zero and counts may not.** Chap hands the model the
covariate values of the months it is being asked to forecast — rainfall in a forecast month
is known, because it comes from the same climate reanalysis whether or not a case has been
reported. The count is what is unknown. So the lag structure is asymmetric, and the
asymmetry is a property of the forecasting problem rather than a choice: the shortest count
lag a model serving all three horizons can use is three months, because the third month of
a block sees nothing fresher.

**Why these count lags.** Three, four, five and six are the season's own recent history at
the freshest resolution available; twelve is the same month a year earlier, which is the
only way a model with no calendar feature can learn that dengue in this country has an
annual cycle. That last one is what makes this child a fair sibling rather than a straw
man: dropping it would leave `b_richCalendar` to win on the fact of having a season at all
rather than on how the season is described.

**Why no lag is standardised and none is dropped for being missing.** A tree splits on
order, so centring and scaling change nothing; and the boosters learn a direction for a
missing feature at every split, so the first year of the record — where the twelve-month
lag does not exist — is fitted on rather than discarded.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

NODE = Path(__file__).resolve().parents[1]

# The choice this node *is*. Named here rather than carried in from another step.
CLIMATE_COLUMNS = ("rainfall", "mean_temperature", "mean_relative_humidity")
CLIMATE_LAGS = (0, 1, 2, 3)
COUNT_LAGS = (3, 4, 5, 6, 12)


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
from combos import resolve  # noqa: E402


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    dataset, dataset_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})

    missing = [c for c in CLIMATE_COLUMNS if c not in frame.columns]
    if missing:
        raise SystemExit(f"the assembled dataset has no column(s) {missing}; this child "
                         f"cannot be taken on combination {COMBO!r}")

    # How much of each feature the earliest months cannot have. Recorded because this
    # child's argument for keeping the twelve-month lag is that a missing lag costs a
    # direction at a split rather than a row, and the size of what is being kept belongs
    # in the record beside the argument.
    per_province = frame.groupby("location").size()
    unbuildable = {f"cases_lag{lag}": int((per_province.clip(upper=lag)).sum())
                   for lag in COUNT_LAGS}

    spec = {
        "combo": COMBO,
        "input_from_combo": dataset_combo,
        "stage": "features",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_lagBlock",
        "description": (f"{len(CLIMATE_COLUMNS)} climate columns at lags "
                        f"{list(CLIMATE_LAGS)}, counts at lags {list(COUNT_LAGS)}, "
                        f"and log population; no calendar and no province identifier"),
        "user_option_values": {
            "features": "lag_block",
            "climate_columns": list(CLIMATE_COLUMNS),
            "climate_lags": list(CLIMATE_LAGS),
            "count_lags": list(COUNT_LAGS),
        },
        "additional_continuous_covariates": list(CLIMATE_COLUMNS),
        "premise": {
            "rows": int(len(frame)),
            "provinces": int(frame["location"].nunique()),
            "climate_columns_present": list(CLIMATE_COLUMNS),
            "climate_missing_values": {c: int(frame[c].isna().sum())
                                       for c in CLIMATE_COLUMNS},
            "target_missing_values": int(frame["disease_cases"].isna().sum()),
            "rows_whose_count_lag_falls_before_the_record": unbuildable,
            "n_features": (len(CLIMATE_COLUMNS) * len(CLIMATE_LAGS)
                           + len(COUNT_LAGS) + 1),
        },
        "why_climate_at_lag_zero": (
            "chap eval hands the model the covariates of the months it is asked to "
            "forecast, so a climate value in a forecast month is known; only the target "
            "is unknown, which is why only the target is lagged by three"),
    }
    (out / "model_option_spec.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"features/a_lagBlock[{COMBO}]: {spec['premise']['n_features']} features; "
          f"climate {list(CLIMATE_LAGS)}, counts {list(COUNT_LAGS)} -> {out}")


if __name__ == "__main__":
    main()
