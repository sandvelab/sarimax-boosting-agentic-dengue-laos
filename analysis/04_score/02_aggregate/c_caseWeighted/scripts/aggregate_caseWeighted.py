"""Summarise the per-cell scores: the mean weighted by the cases observed in each cell.

The unweighted mean spends as much of itself on a province-month in which nothing
happened as on the peak of an outbreak. For a dengue early-warning system that is close
to backwards: the months worth forecasting well are the months with cases in them, and a
model can look good on the headline by being calm during the long quiet stretches this
record is mostly made of.

Weighting by the observed count is the summary that asks how the models did where the
disease was. It has a cost, and the cost is the reason this is a sibling rather than the
main path: the weight is a function of the outcome, so cells with no observed cases drop
out of the mean entirely and the effective sample shrinks to the outbreak months. A model
that is well calibrated at zero gets no credit for it here, and a summary that cannot see
the zeros is not a better summary than one dominated by them -- it is a different one,
with the opposite blind spot. `weighting_notes.json` reports how many cells the weighting
silences and how concentrated what remains is, so the shrinkage is a number rather than a
caveat.

**The weight is the cell's own observed count**, read from the same per-cell file the
scores come from, so it is the value the models were scored against and not a second
extraction of the data. Cells whose observed count is zero carry weight zero; a group all
of whose cells are zero has no weighted mean and is reported as missing rather than as
zero, because a mean over nothing is not zero.

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

NODE = Path(__file__).resolve().parents[1]
COMBO = os.environ.get("COMBO", "main")
WEIGHTING = "cases"

sys.path.insert(0, str(NODE.parents[1] / "scripts" / "lib"))
import aggregate  # noqa: E402


def main() -> None:
    cells = aggregate.cells_for(NODE, COMBO)

    # `observed` is a property of the cell, so every model and every lead time sees the
    # same value for it. Checked rather than assumed: if it were not, the weight would
    # depend on which model happened to be first and the comparison would be void.
    per_cell = cells.groupby(aggregate.CELL_KEYS)["observed"].nunique()
    inconsistent = sorted(per_cell[per_cell > 1].index)
    if inconsistent:
        raise SystemExit(
            f"{len(inconsistent)} cells carry more than one observed value, for example "
            f"{inconsistent[:3]}. The case weighting would then depend on which model's "
            f"row was read.")

    weights = (cells.groupby(aggregate.CELL_KEYS, as_index=False)["observed"].first()
               .rename(columns={"observed": "weight"}))
    weights["weight"] = weights["weight"].astype(float)

    aggregate.write(
        NODE, COMBO, WEIGHTING, weights=weights,
        weight_basis="observed dengue cases per province-month, from the same per-cell "
                     "file the scores are read from")


if __name__ == "__main__":
    main()
