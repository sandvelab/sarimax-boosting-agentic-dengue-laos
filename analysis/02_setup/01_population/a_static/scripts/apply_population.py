"""Stage 1 of the common setup: the population column, taken as the archive supplies it.

The source file carries one population figure per province for the whole 1998-2010
record. It is a 2020 snapshot, so it is wrong by a decade of growth at the start of the
period and by a decade of decline in nothing at all -- population rose throughout. Any
model that uses population as an offset is therefore working with a denominator that is
too large early and about right late, and the same is true for the reference.

This child takes the column unchanged. That is the honest reading of "what the dataset
says", and it is what every published run of this dataset has used; the sibling that
back-casts a per-year series from a published growth rate is the alternative, and the
stability run is where the difference is measured rather than argued.

The transformation is the identity on the data. What this script contributes is the
**check** that the column really is constant per province, which the description above
assumes and which nothing had verified.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves this stage
  setup_spec.json        what this stage chose, and what it did to the data
"""

from __future__ import annotations

import hashlib
import json
import os
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
SOURCE = ROOT / "analysis/01_data/01_partition/results/development_1998-01_2009-12.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(SOURCE, dtype={"time_period": str})

    # The property the choice rests on, checked rather than assumed.
    per_province = frame.groupby("location")["population"].nunique()
    varying = sorted(per_province[per_province > 1].index)

    frame.to_csv(out / "analysis_dataset.csv", index=False)

    spec = {
        "combo": COMBO,
        "stage": "population",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_static",
        "description": "the archived population column, one constant per province",
        "dataset_transform": "identity",
        "input": str(SOURCE.relative_to(ROOT)),
        "input_sha256": sha256(SOURCE),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": int(len(frame)),
        "rows_out": int(len(frame)),
        "locations": int(frame["location"].nunique()),
        "period_first": str(frame["time_period"].min()),
        "period_last": str(frame["time_period"].max()),
        "population_constant_per_province": not varying,
        "provinces_with_varying_population": varying,
        "population_min": int(frame["population"].min()),
        "population_max": int(frame["population"].max()),
        "eval_flags": {},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"population/a_static: {len(frame)} rows, constant per province "
          f"{spec['population_constant_per_province']} -> {out}")


if __name__ == "__main__":
    main()
