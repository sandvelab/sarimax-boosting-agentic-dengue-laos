"""Stage 1 of the candidate's configuration: the observation model for the counts.

A **hurdle**: two processes, fitted separately on the same design. A logistic model
for whether a province-month reports anything at all, and a count model for how large
the report is given that there is one. Reporting and magnitude are then allowed to
depend on the season, the climate and the province differently, which neither the
plain negative binomial nor the zero-inflated mixture permits -- in both of those the
same linear predictor drives the zeros and the large counts.

The premise below is what makes the split worth trying: the months that report at all
and the months that do not are not a small perturbation of each other on this dataset.
The mean of the positive months is far from the mean over all months, so a single mean
function is being asked to serve two rather different regimes.

What the construction gives up is stated where it is implemented: the positive part is
a negative binomial on `y - 1` rather than a zero-truncated negative binomial, which
is the cheaper of the two standard hurdles and makes the positive part's coefficients
incomparable with the other two children's. They were never going to be compared --
the fork is decided on what the model forecasts.

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

    counts = frame["disease_cases"].dropna()
    positive = counts[counts > 0]

    premise = {
        "observed_cells": int(len(counts)),
        "zero_share": float((counts == 0).mean()),
        "mean_over_all_months": float(counts.mean()),
        # The two regimes the hurdle separates. A single mean function has to sit
        # between these, and the gap is what the fork is asking about.
        "mean_over_reporting_months": float(positive.mean()),
        "median_over_reporting_months": float(positive.median()),
        "largest_month": int(counts.max()),
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "observation",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "c_hurdle",
        "description": "a logistic model for reporting at all and a count model for how much",
        "user_option_values": {"observation": "hurdle"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"observation/c_hurdle[{COMBO}]: hurdle; zeros "
          f"{premise['zero_share']:.2f}, mean over all months "
          f"{premise['mean_over_all_months']:.1f} against "
          f"{premise['mean_over_reporting_months']:.1f} over reporting months -> {out}")



if __name__ == "__main__":
    main()
