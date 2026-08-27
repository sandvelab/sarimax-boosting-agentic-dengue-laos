"""Stage 6 of the candidate's configuration: the province-year effect's variance.

**One variance for the whole country.** Every province's annual effect is penalised
toward zero by the same estimated variance, pooling all of them into one estimate.

This is the main path, and it is what batch 8 fitted. It is also what batch 8
diagnosed: on the log scale a shared variance is a constant *multiplicative* width, so
every province's forecast interval is equally wide in relative terms. In Vientiane
Capital that interval covered every observed outcome, and in Salavan it covered an
eighth of them, and the aggregate coverage of 0.720 sat between two failures and
described neither.

The case for pooling is not nothing. Most provinces have twelve annual effects and
some far fewer, and a variance estimated from four numbers is a poor estimate; sharing
one across the country is the standard remedy for exactly that. What the fork asks is
whether the remedy costs more than the disease here.

The premise is the quantity the shared variance is a single number for: how much each
province's annual totals move around its own average, on the log scale. A shared
variance is the assertion that these are all the same.

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

    observed = frame.dropna(subset=["disease_cases"]).assign(
        year=lambda f: f["time_period"].str[:4])
    annual = observed.groupby(["location", "year"])["disease_cases"].sum()
    # The spread of a province's annual totals on the log scale is the quantity the
    # province-year effect's variance is: how much a year departs from that province's
    # own average, in relative terms. Provinces with fewer than three years of record
    # are left out of the comparison, not out of the model.
    spread = (np.log1p(annual).groupby(level=0).agg(["std", "count"])
              .query("count >= 3")["std"].dropna())

    premise = {
        "provinces_compared": int(len(spread)),
        "province_years": int(len(annual)),
        "log_annual_spread_min": float(spread.min()),
        "log_annual_spread_max": float(spread.max()),
        # A shared variance is the assertion that this ratio is 1.
        "log_annual_spread_ratio_max_to_min": float(spread.max() / spread.min()),
        "log_annual_spread_median": float(spread.median()),
        "by_province": {p: float(v) for p, v in spread.sort_values().items()},
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "year_variance",
        "order": 6,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_shared",
        "description": "one province-year variance for every province, pooled",
        "user_option_values": {"year_variance": "shared"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"yearVariance/a_shared[{COMBO}]: one pooled variance; across "
          f"{premise['provinces_compared']} provinces the log annual spread runs "
          f"{premise['log_annual_spread_min']:.2f} to "
          f"{premise['log_annual_spread_max']:.2f} -> {out}")



if __name__ == "__main__":
    main()
