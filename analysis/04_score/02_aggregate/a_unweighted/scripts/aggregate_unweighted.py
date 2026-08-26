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

Everything here is a `groupby` on `01_collect/results/$COMBO/metrics_cell.csv`. No value
is recomputed and none is typed.

Writes, under results/$COMBO/:
  metrics_summary.csv      one row per model -- the headline figures
  crps_by_location.csv     per province, where the aggregate hides the most
  crps_by_split.csv        per backtest split
  crps_by_region_split.csv per province and split, which is what a paired test needs
  crps_by_horizon.csv      per lead time
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
COMBO = os.environ.get("COMBO", "main")
WEIGHTING = "unweighted"


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)
    source = NODE.parents[1] / "01_collect" / "results" / COMBO / "metrics_cell.csv"
    cells = pd.read_csv(source, dtype={"time_period": str, "split_first_period": str})

    summary = cells.groupby("model", as_index=False).agg(
        n_cells=("crps", "size"),
        mean_crps=("crps", "mean"),
        mae=("abs_error", "mean"),
        coverage_10_90=("in_10_90", "mean"),
        coverage_25_75=("in_25_75", "mean"),
        n_locations=("location", "nunique"),
        n_splits=("split_first_period", "nunique"),
        observed_total=("observed", "sum"),
    )
    summary.insert(1, "weighting", WEIGHTING)
    summary.sort_values("mean_crps").to_csv(out / "metrics_summary.csv", index=False)

    resolutions = {
        "crps_by_location": cells.groupby(["model", "location"], as_index=False).agg(
            n_cells=("crps", "size"), mean_crps=("crps", "mean"),
            mae=("abs_error", "mean"), coverage_10_90=("in_10_90", "mean"),
            coverage_25_75=("in_25_75", "mean"), observed_total=("observed", "sum")),
        "crps_by_split": cells.groupby(["model", "split_first_period"], as_index=False).agg(
            n_cells=("crps", "size"), mean_crps=("crps", "mean")),
        "crps_by_region_split": cells.groupby(
            ["model", "location", "split_first_period"], as_index=False).agg(
            n_cells=("crps", "size"), mean_crps=("crps", "mean")),
        "crps_by_horizon": cells.groupby(["model", "horizon_distance"], as_index=False).agg(
            n_cells=("crps", "size"), mean_crps=("crps", "mean")),
    }
    for name, frame in resolutions.items():
        frame.insert(1, "weighting", WEIGHTING)
        frame.to_csv(out / f"{name}.csv", index=False)

    best = summary.sort_values("mean_crps").iloc[0]
    print(f"aggregate/a_unweighted[{COMBO}]: {len(summary)} models over "
          f"{int(best.n_cells)} cells; best {best.model} at CRPS {best.mean_crps:.3f}")


if __name__ == "__main__":
    main()
