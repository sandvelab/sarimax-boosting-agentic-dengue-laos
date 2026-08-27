"""Stage 6 of the candidate's configuration: the province-year effect's variance.

**One variance per province**, estimated from that province's own annual effects, so a
province whose epidemic years swing hard gets a wider forecast than one whose record
is flat.

This is the structural half of the repair batch 8's diagnosis pointed at. The candidate
had the best point forecast in the project and the wrong width, and the width was wrong
in opposite directions in different provinces -- too wide where the burden was largest,
too narrow where the epidemic years were sharpest. A single shared variance is the
feature that makes both failures the same failure, and this child removes it.

It also separates the two explanations batch 8 could not separate. If the width is
wrong because the variance is shared, this child fixes it. If it is wrong because the
Laplace approximation is symmetric on the log scale, this child changes nothing and the
repair is a sampler and a much larger dependency. That is a cheap test of an expensive
question, and it is the reason this fork was placed rather than the model quietly
changed.

What it costs: a variance estimated from as few as three or four annual effects for the
thinnest records, with no pooling across provinces to steady it. The premise records
how many years each province actually has to estimate from.

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
        "choice": "b_provinceScaled",
        "description": "one province-year variance per province, from that province's own years",
        "user_option_values": {"year_variance": "province_scaled"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"yearVariance/b_provinceScaled[{COMBO}]: one variance per province; the "
          f"widest province's annual spread is "
          f"{premise['log_annual_spread_ratio_max_to_min']:.1f} times the narrowest "
          f"-> {out}")



if __name__ == "__main__":
    main()
