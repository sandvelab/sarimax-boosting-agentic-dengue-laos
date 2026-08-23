#!/usr/bin/env python
"""Score a Chap evaluation `.nc` at every resolution the project reports on.

Batch-4 reconnaissance. `describe_evaluation.py` answered *what* Chap's CRPS is; this
script is the routine form of the same discipline, applied to a real model on the real
development dataset: it takes an evaluation file and writes the headline mean, the
per-region values, the per-split values, the per-cell detail, and the secondary metrics
the plan asks for beside CRPS (MAE and the two interval-coverage metrics).

As in batch 2, **the score is always chap-core's own**. Nothing here implements a metric;
`get_metric` is asked for the registered metric by id and only the aggregation level is
ours. The split label is recovered by the arithmetic batch 2 established:

    split first predicted period = time_period - (horizon_distance - 1)

Dual interface, per the repository convention: importable functions plus a CLI.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from chap_core.assessment.evaluation import Evaluation
from chap_core.assessment.flat_representations import DataDimension
from chap_core.assessment.metrics import get_metric

# The headline metric, and the secondaries the plan names beside it (§4 "Metric").
METRIC_IDS = ("crps", "mae", "coverage_10_90", "coverage_25_75")


def shift_period(period: str, back: int) -> str:
    """Return the monthly period `back` months before `period` (YYYYMM in, YYYYMM out)."""
    year, month = int(period[:4]), int(period[4:])
    index = year * 12 + (month - 1) - back
    return f"{index // 12:04d}{index % 12 + 1:02d}"


def flat_frames(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Observations and forecasts of an evaluation file, as flat frames."""
    flat = Evaluation.from_file(path).to_flat()
    return pd.DataFrame(flat.observations), pd.DataFrame(flat.forecasts)


def with_split(detailed: pd.DataFrame) -> pd.DataFrame:
    """Add the recovered split label (first predicted period of the split) to a detail frame."""
    return detailed.assign(
        split_first_period=[
            shift_period(str(period), int(horizon) - 1)
            for period, horizon in zip(detailed.time_period, detailed.horizon_distance, strict=True)
        ]
    )


def score_frames(path: Path) -> dict[str, pd.DataFrame]:
    """Every table this project reports from one evaluation file."""
    observations, forecasts = flat_frames(path)
    frames: dict[str, pd.DataFrame] = {}

    globals_rows = []
    for metric_id in METRIC_IDS:
        # `get_metric` returns the metric *class*; the aggregation methods are instance methods.
        metric = get_metric(metric_id)()
        global_frame = metric.get_global_metric(observations, forecasts)
        globals_rows.append({"metric": metric_id, "value": float(global_frame["metric"].iloc[0])})
        frames[f"{metric_id}_by_location"] = metric.get_metric(
            observations, forecasts, dimensions=(DataDimension.location,)
        )

    frames["metrics_global"] = pd.DataFrame(globals_rows)

    # CRPS at the platform's finest resolution, and the two aggregations the plan reports.
    detailed = with_split(get_metric("crps")().get_detailed_metric(observations, forecasts))
    frames["crps_detailed"] = detailed
    frames["crps_by_split"] = detailed.groupby("split_first_period", as_index=False)["metric"].mean()
    frames["crps_by_region_split"] = detailed.groupby(
        ["location", "split_first_period"], as_index=False
    )["metric"].mean()

    # What the headline mean is actually a mean over, on this dataset and this scheme.
    frames["evaluable_cells"] = (
        detailed.groupby("location", as_index=False)
        .size()
        .rename(columns={"size": "n_cells"})
        .sort_values("location")
    )
    frames["samples_per_cell"] = (
        forecasts.groupby(["location", "time_period", "horizon_distance"], as_index=False)
        .size()
        .rename(columns={"size": "n_samples"})
    )
    return frames


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True, help="Path to a chap eval .nc file")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory to write the tables into")
    parser.add_argument("--prefix", required=True, help="Filename prefix identifying the run")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in score_frames(args.evaluation).items():
        frame.to_csv(args.out_dir / f"{args.prefix}_{name}.csv", index=False)


if __name__ == "__main__":
    main()
