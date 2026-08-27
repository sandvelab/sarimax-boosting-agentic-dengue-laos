"""Stage 3 of the candidate's configuration: how population enters the model.

**As an estimated coefficient** on standardised log population, not as a fixed offset.
An offset asserts that reported cases scale proportionally with population -- a
coefficient of exactly one, never estimated and never checked. This child estimates it
instead, so a systematic departure from proportionality is absorbed by the model
rather than pushed into the province effects.

There is a reason to expect a departure. Reporting is not population, and the column
itself is a single 2020 snapshot applied to thirteen years -- which is what the
`02_setup/01_population` fork is about, one level up and re-scoring every model. This
fork is only about what our model does with whatever it was handed.

The premise is the check the offset never makes: the slope of log mean reported cases
on log population across provinces. An offset is the assertion that this number is
one. It is computed here rather than asserted, on the dataset this combination
assembled, and it is a description of the data rather than a fitted model -- the
fitted coefficient is not this number, because the fit also carries seasonality,
climate and pooled province effects.

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

    observed = frame.dropna(subset=["disease_cases"])
    by_province = observed.groupby("location").agg(
        mean_cases=("disease_cases", "mean"), population=("population", "first"))
    x = np.log(by_province["population"].to_numpy(float))
    y = np.log(by_province["mean_cases"].to_numpy(float) + 1.0)
    slope, intercept = np.polyfit(x, y, 1)

    premise = {
        "provinces": int(len(by_province)),
        "population_min": int(by_province["population"].min()),
        "population_max": int(by_province["population"].max()),
        # An offset is the assertion that this slope is 1. Described, not fitted:
        # the model's own coefficient also carries season, climate and pooling.
        "slope_of_log_mean_cases_on_log_population": float(slope),
        "intercept": float(intercept),
        "correlation": float(np.corrcoef(x, y)[0, 1]),
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "population",
        "order": 3,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_covariate",
        "description": "standardised log population as an estimated coefficient",
        "user_option_values": {"population": "covariate"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"population/b_covariate[{COMBO}]: estimated coefficient; across provinces "
          f"log mean cases rises {premise['slope_of_log_mean_cases_on_log_population']:.2f} "
          f"per unit of log population, where an offset asserts 1.00 -> {out}")



if __name__ == "__main__":
    main()
