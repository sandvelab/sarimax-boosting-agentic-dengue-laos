"""Summarise the per-cell scores: the mean weighted by the population of each cell.

The main path counts every province-month once. That makes the headline a statement
about administrative units rather than about people, and the units differ by twenty
times in size: Phongsaly with forty thousand residents moves the mean as much as
Vientiane Capital with nearly a million. A forecasting system is deployed to serve a
population, so weighting a cell by the people it describes is at least as defensible a
summary of the same scores, and it is the summary a health ministry would ask for.

It is not obviously better, which is why it is a sibling and not a promotion. Weighting
by population concentrates the mean on the large provinces, where absolute case counts
and therefore absolute CRPS are largest anyway, so it pushes in the same direction as the
unweighted mean's existing bias rather than correcting it. What it buys is that the
concentration becomes explicit and measurable: `weighting_notes.json` reports how much of
the total weight sits where, so the reader can see what the number is a statement about.

**The weight is the cell's own population**, taken per province and per month from the
assembled dataset that combination was evaluated on -- not from a constant here. That
matters for one combination in particular: under the population fork's back-cast child
the column is a per-year series, and this weighting then follows it without a line of
code changing.

Everything here is a `groupby` on `01_collect/results/$COMBO/metrics_cell.csv`, performed
by `04_score/scripts/lib/aggregate.py`, which is the one implementation the three
children of this fork share.

Writes, under results/$COMBO/: the five tables `aggregate.write` documents, plus
`weights.csv` and `weighting_notes.json`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
COMBO = os.environ.get("COMBO", "main")
WEIGHTING = "population"


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
sys.path.insert(0, str(NODE.parents[1] / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
import aggregate  # noqa: E402
from combos import resolve  # noqa: E402


def main() -> None:
    # The dataset the models were evaluated on. A scoring combination re-runs no model,
    # so it inherits the assembled dataset from its base and records which one answered.
    path, from_combo = resolve(ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(path, dtype={"time_period": str})

    # `01_collect` writes periods as YYYYMM; the setup chain carries them as YYYY-MM.
    weights = frame[["location", "time_period", "population"]].copy()
    weights["time_period"] = weights["time_period"].str.replace("-", "", regex=False)
    weights = weights.rename(columns={"population": "weight"})
    weights["weight"] = weights["weight"].astype(float)

    aggregate.write(
        NODE, COMBO, WEIGHTING, weights=weights,
        weight_basis=f"population per province-month, from "
                     f"{path.relative_to(ROOT)} (combination {from_combo!r})")


if __name__ == "__main__":
    main()
