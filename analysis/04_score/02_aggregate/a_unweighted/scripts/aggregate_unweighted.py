"""Summarise the per-cell scores: the plain unweighted mean over evaluable cells.

Every cell counts once. This is what Chap's own evaluation reports and what the project's
success criterion is defined against, which is the reason it is the main path -- not a
belief that it is the best summary. It is not: the provinces differ in burden by four
orders of magnitude, so an unweighted mean over cells is dominated by the arithmetic of
large-count provinces where absolute errors are large, and it says nothing about how well
the small provinces are served. The siblings that weight by population and by cases are
the other summaries of the same numbers, and re-weighting is a re-aggregation of this
node's input rather than a re-run of anything -- which is what makes this the cheapest
fork in the project and the one with no excuse for going unexamined.

Everything here is a `groupby` on `01_collect/results/$COMBO/metrics_cell.csv`, performed
by `04_score/scripts/lib/aggregate.py`, which is the one implementation the three
children of this fork share. No value is recomputed and none is typed.

Writes, under results/$COMBO/: the five tables `aggregate.write` documents.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
COMBO = os.environ.get("COMBO", "main")
WEIGHTING = "unweighted"

sys.path.insert(0, str(NODE.parents[1] / "scripts" / "lib"))
import aggregate  # noqa: E402


def main() -> None:
    aggregate.write(NODE, COMBO, WEIGHTING, weights=None)


if __name__ == "__main__":
    main()
