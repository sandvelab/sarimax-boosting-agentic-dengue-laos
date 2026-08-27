"""Stage 2 of the candidate's configuration: which climate covariates, at which lags.

**None.** The shared annual harmonics, the province effect and the province-year
effect carry the whole of the seasonal and interannual signal, and no weather column
enters the mean at all.

This is the sibling that is worth running whatever it scores. If a model with no
climate term forecasts as well as one with rainfall and temperature in it, then on
this dataset the covariates are decoration and the annual cycle is being learned from
the calendar -- which is a finding about the data, not about the model, and it bears
directly on a reference model whose whole premise is that climate drives an early
warning. Batch 8 already saw the first sign of it: the fitted climate coefficients
were an order of magnitude smaller than the seasonal terms.

It is also the only child of this fork that costs the fit nothing. With no lagged
column required, no row is dropped for a lag falling before the record starts, so this
child fits on every observed month -- which the premise records, because a comparison
on a different number of training rows is worth knowing about.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]



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

    dataset, input_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})

    available = [c for c in ("rainfall", "mean_temperature", "mean_relative_humidity")
                 if c in frame.columns]
    provinces = int(frame["location"].nunique())

    premise = {
        "columns_left_out": available,
        "rows": int(len(frame)),
        "observed_rows": int(frame["disease_cases"].notna().sum()),
        # No lagged column means no row is dropped for a lag that falls before the
        # province's record begins. The main path loses two months per province.
        "rows_a_two_month_lag_would_have_cost": 2 * provinces,
        "provinces": provinces,
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "covariates",
        "order": 2,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "c_climateFree",
        "description": "no climate covariates; the seasonal harmonics carry the annual cycle alone",
        "user_option_values": {"covariates": [], "covariate_lags": []},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"covariates/c_climateFree[{COMBO}]: no climate columns; "
          f"{premise['columns_left_out']} left out, "
          f"{premise['rows_a_two_month_lag_would_have_cost']} rows the main path drops "
          f"are kept -> {out}")



if __name__ == "__main__":
    main()
