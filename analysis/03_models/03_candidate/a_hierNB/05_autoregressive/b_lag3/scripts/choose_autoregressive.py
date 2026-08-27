"""Stage 5 of the candidate's configuration: whether the recent case history enters.

**The count three months back**, as standardised log1p, entering the linear predictor
like any other covariate.

Why three and not one. Chap asks for three months at a time, and the same fitted model
has to forecast all three. At the third month, the freshest observed count is three
months old; a model using a one-month lag would have to feed on its own forecasts to
reach that far, which is a different model with a different error structure. Three is
therefore the shortest lag one model can use at every horizon, and using it costs the
first three months of each province's record at fit time.

What the term is for: a seasonal regression forecasts the average year. The last
observed count is what would tell it whether this year is one of the bad ones -- the
same information the persistence baseline has and, batch 7 found, the reason
persistence is level with the reference model at one month's lead.

The premise is the autocorrelation of log1p counts within a province at lags one, two,
three and twelve. The comparison that decides whether this term can carry anything is
lag three against lag twelve: a lagged count that mostly says what month of the year
it is says nothing the seasonal harmonics have not already said.

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

    import numpy as np

    observed = frame.dropna(subset=["disease_cases"]).copy()
    # The file writes periods as YYYY-MM; the index below has to be arithmetic, so that
    # "three months earlier" is subtraction rather than string manipulation.
    compact = observed["time_period"].str.replace("-", "", regex=False)
    observed["_m"] = (compact.str[:4].astype(int) * 12
                      + compact.str[4:6].astype(int) - 1)
    observed = observed.sort_values(["location", "_m"])

    # Matched on (province, month index) rather than by row position, so a gap in a
    # province's record cannot pair a month with the wrong predecessor.
    earlier = dict(zip(zip(observed["location"], observed["_m"], strict=True),
                       observed["disease_cases"], strict=True))
    correlations, pairs = {}, {}
    for lag in (1, 2, 3, 12):
        now, before = [], []
        for location, m, value in zip(observed["location"], observed["_m"],
                                      observed["disease_cases"], strict=True):
            previous = earlier.get((location, m - lag))
            if previous is not None:
                now.append(value)
                before.append(previous)
        pairs[f"lag_{lag}"] = len(now)
        correlations[f"lag_{lag}"] = float(
            np.corrcoef(np.log1p(now), np.log1p(before))[0, 1])

    premise = {
        "observed_cells": int(len(observed)),
        # On log1p, within province. The comparison that matters is lag 3 against lag
        # 12: a lagged count that only tells the model what month of the year it is
        # tells it nothing the seasonal harmonics do not already say.
        "autocorrelation_of_log1p_cases": correlations,
        "pairs_available": pairs,
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "autoregressive",
        "order": 5,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_lag3",
        "description": "standardised log1p of the count three months back",
        "user_option_values": {"autoregressive": "lag3"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"autoregressive/b_lag3[{COMBO}]: log1p cases at lag 3; autocorrelation "
          f"{premise['autocorrelation_of_log1p_cases']['lag_3']:.3f} at lag 3 against "
          f"{premise['autocorrelation_of_log1p_cases']['lag_12']:.3f} at lag 12 -> {out}")



if __name__ == "__main__":
    main()
