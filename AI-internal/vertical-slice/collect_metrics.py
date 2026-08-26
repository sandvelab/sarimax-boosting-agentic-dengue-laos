"""Turn one Chap evaluation file into the contract files the claim tree consumes.

This is the routine that `analysis/04_score/01_collect` will run once the tree exists;
the vertical slice exercises it here so that the file contract designed in batch 5 has
been written and read before it has to carry alternatives.

**No metric is implemented here.** Every value comes from chap-core's own registered
metric, asked for by id; the only thing this script chooses is the level of
aggregation, and the split label, which is recovered by the arithmetic batch 2
established:

    split (first predicted period) = time_period - (horizon_distance - 1)

Two files are the contract:

  metrics_cell.csv     one row per (model, location, time_period, horizon_distance) --
                       the platform's finest resolution, with the observed value beside
                       the scores, so everything downstream is a pure aggregation of it
  metrics_summary.csv  one row per (model, weighting)

The remaining files are the reporting resolutions the plan asks for beside the mean.
Rows accumulate: a model already present in an existing file is replaced, models
already there are kept, so the same call adds each model to a shared leaderboard
without any value being retyped between steps.

Usage:
  python collect_metrics.py --evaluation eval.nc --model NAME --out-dir DIR [--combo main]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from chap_core.assessment.evaluation import Evaluation
from chap_core.assessment.flat_representations import DataDimension
from chap_core.assessment.metrics import get_metric

# The headline metric and the secondaries the plan names beside it.
METRIC_IDS = ("crps", "mae", "coverage_10_90", "coverage_25_75")

# Column name in metrics_cell.csv for each metric id.
CELL_COLUMN = {
    "crps": "crps",
    "mae": "abs_error",
    "coverage_10_90": "in_10_90",
    "coverage_25_75": "in_25_75",
}

CELL_KEYS = ["location", "time_period", "horizon_distance"]


def shift_period(period: str, back: int) -> str:
    """The monthly period `back` months before `period` (YYYYMM in, YYYYMM out)."""
    year, month = int(str(period)[:4]), int(str(period)[4:])
    index = year * 12 + (month - 1) - back
    return f"{index // 12:04d}{index % 12 + 1:02d}"


def cell_table(evaluation: Path, model: str) -> pd.DataFrame:
    """The finest-resolution table: every metric for every evaluable cell."""
    flat = Evaluation.from_file(evaluation).to_flat()
    observations = pd.DataFrame(flat.observations)
    forecasts = pd.DataFrame(flat.forecasts)

    table: pd.DataFrame | None = None
    for metric_id in METRIC_IDS:
        # `get_metric` returns the metric *class*; the aggregations are instance methods.
        detailed = get_metric(metric_id)().get_detailed_metric(observations, forecasts)
        detailed = detailed.rename(columns={"metric": CELL_COLUMN[metric_id]})
        table = detailed if table is None else table.merge(detailed, on=CELL_KEYS, how="outer")

    table = table.merge(
        observations.rename(columns={"disease_cases": "observed"}),
        on=["location", "time_period"],
        how="left",
    )
    table["split_first_period"] = [
        shift_period(period, int(horizon) - 1)
        for period, horizon in zip(table.time_period, table.horizon_distance, strict=True)
    ]
    table["n_samples"] = (
        forecasts.groupby(CELL_KEYS).size().reindex(pd.MultiIndex.from_frame(table[CELL_KEYS])).to_numpy()
    )
    table.insert(0, "model", model)
    return table.sort_values(["model", "location", "time_period", "horizon_distance"])


def summarise(cells: pd.DataFrame) -> pd.DataFrame:
    """The headline row per model, at the unweighted aggregation the plan fixes."""
    grouped = cells.groupby("model", as_index=False).agg(
        n_cells=("crps", "size"),
        mean_crps=("crps", "mean"),
        mae=("abs_error", "mean"),
        coverage_10_90=("in_10_90", "mean"),
        coverage_25_75=("in_25_75", "mean"),
        n_locations=("location", "nunique"),
        n_splits=("split_first_period", "nunique"),
    )
    grouped.insert(1, "weighting", "unweighted")
    return grouped


def resolutions(cells: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """The per-region and per-split values the plan requires beside the mean."""
    return {
        "crps_by_location": cells.groupby(["model", "location"], as_index=False)
        .agg(n_cells=("crps", "size"), mean_crps=("crps", "mean"),
             mae=("abs_error", "mean"), coverage_10_90=("in_10_90", "mean"),
             coverage_25_75=("in_25_75", "mean"), observed_total=("observed", "sum")),
        "crps_by_split": cells.groupby(["model", "split_first_period"], as_index=False)
        .agg(n_cells=("crps", "size"), mean_crps=("crps", "mean")),
        "crps_by_region_split": cells.groupby(
            ["model", "location", "split_first_period"], as_index=False
        ).agg(n_cells=("crps", "size"), mean_crps=("crps", "mean")),
        "crps_by_horizon": cells.groupby(["model", "horizon_distance"], as_index=False)
        .agg(n_cells=("crps", "size"), mean_crps=("crps", "mean")),
    }


def accumulate(path: Path, frame: pd.DataFrame, model: str) -> pd.DataFrame:
    """Replace this model's rows in an existing file, keep every other model's."""
    if path.exists():
        existing = pd.read_csv(path, dtype={"time_period": str, "split_first_period": str})
        frame = pd.concat([existing[existing.model != model], frame], ignore_index=True)
    return frame.sort_values([c for c in ("model", "location", "split_first_period",
                                          "time_period", "horizon_distance") if c in frame])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--model", required=True, help="leaderboard name for this evaluation")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--combo", default="main", help="combination id; results go to <out-dir>/<combo>")
    args = parser.parse_args()

    out = args.out_dir / args.combo
    out.mkdir(parents=True, exist_ok=True)

    cells = cell_table(args.evaluation, args.model)
    written = {"metrics_cell": cells, **resolutions(cells)}
    for name, frame in written.items():
        path = out / f"{name}.csv"
        accumulate(path, frame, args.model).to_csv(path, index=False)

    all_cells = pd.read_csv(out / "metrics_cell.csv", dtype={"time_period": str, "split_first_period": str})
    summarise(all_cells).to_csv(out / "metrics_summary.csv", index=False)

    print(f"{args.model}: {len(cells)} cells -> {out}/  "
          f"(mean CRPS {cells.crps.mean():.4f} over {cells.location.nunique()} locations)")


if __name__ == "__main__":
    main()
