#!/usr/bin/env python
"""Describe a Chap evaluation `.nc` and recover its metrics at every resolution.

This exists to answer one question the project cannot proceed without: what exactly is the
number Chap calls CRPS, and are the per-region and per-split values behind it recoverable?
It answers it by *using chap-core's own metric classes* rather than by reimplementing the
score. A CRPS we computed ourselves is the one number we could most easily bend without it
being visible, so the metric stays the platform's and only the aggregation level changes.

Chap's finest metric resolution is (location, time_period, horizon_distance); there is no
split dimension. The split is nevertheless recoverable, because a rolling-origin backtest
predicts `time_period` from an origin `horizon_distance` steps earlier:

    split first predicted period = time_period - (horizon_distance - 1)

which this script derives and writes out, so per-split values are available downstream
without anyone having to re-derive the arithmetic.

Dual interface, per the repository convention: importable functions plus a CLI.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import xarray as xr
from chap_core.assessment.evaluation import Evaluation
from chap_core.assessment.flat_representations import DataDimension
from chap_core.assessment.metrics import CRPSMetric, list_metrics


def shift_period(period: str, back: int) -> str:
    """Return the monthly period `back` months before `period` (YYYYMM in, YYYYMM out)."""
    year, month = int(period[:4]), int(period[4:])
    index = year * 12 + (month - 1) - back
    return f"{index // 12:04d}{index % 12 + 1:02d}"


def describe_structure(path: Path) -> str:
    """Human-readable dump of the NetCDF's dimensions, variables and global attributes."""
    ds = xr.open_dataset(path)
    lines = [f"file: {path.name}", "", "=== xarray structure ===", repr(ds), "", "=== global attributes ==="]
    lines += [f"{key}: {value}" for key, value in ds.attrs.items()]
    ds.close()
    return "\n".join(lines) + "\n"


def crps_frames(path: Path) -> dict[str, pd.DataFrame]:
    """CRPS from one evaluation file at four resolutions, plus the recovered split label."""
    evaluation = Evaluation.from_file(path)
    flat = evaluation.to_flat()
    observations = pd.DataFrame(flat.observations)
    forecasts = pd.DataFrame(flat.forecasts)
    crps = CRPSMetric()

    detailed = crps.get_detailed_metric(observations, forecasts)
    detailed = detailed.assign(
        split_first_period=[
            shift_period(str(period), int(horizon) - 1)
            for period, horizon in zip(detailed.time_period, detailed.horizon_distance, strict=True)
        ]
    )
    by_split = detailed.groupby("split_first_period", as_index=False)["metric"].mean()

    return {
        "smoke_crps_global": crps.get_global_metric(observations, forecasts),
        "smoke_crps_by_location": crps.get_metric(observations, forecasts, dimensions=(DataDimension.location,)),
        "smoke_crps_by_split": by_split,
        "smoke_crps_detailed": detailed,
        "smoke_samples_per_cell": (
            forecasts.groupby(["location", "time_period", "horizon_distance"], as_index=False)
            .size()
            .rename(columns={"size": "n_samples"})
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True, help="Path to a chap eval .nc file")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory to write the description into")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "smoke_eval_structure.txt").write_text(describe_structure(args.evaluation))

    for name, frame in crps_frames(args.evaluation).items():
        frame.to_csv(args.out_dir / f"{name}.csv", index=False)

    pd.DataFrame(list_metrics()).to_csv(args.out_dir / "chap_metrics_registry.csv", index=False)


if __name__ == "__main__":
    main()
