#!/usr/bin/env python3
"""Resolve the fixed backtest scheme to concrete train/test month windows.

Reads only the sorted list of distinct `time_period` values in the development file --
never disease_cases itself, and definitely never the holdout.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[1] / "scripts"))
from lib.backtest import rolling_splits  # noqa: E402

DEV_CSV = NODE.parent / "01_prepare" / "results" / "development.csv"
RESULTS = NODE / "results"
N_PERIODS, N_SPLITS, STRIDE = 3, 8, 3


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        months = sorted({r["time_period"] for r in csv.DictReader(f)})

    splits = rolling_splits(months, N_PERIODS, N_SPLITS, STRIDE)

    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "split_schedule.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["split", "train_start", "train_end", "test_start", "test_end",
                    "n_train_months", "test_months"])
        for s in splits:
            w.writerow([
                s["split"], s["train_months"][0], s["train_months"][-1],
                s["test_months"][0], s["test_months"][-1],
                len(s["train_months"]), ";".join(s["test_months"]),
            ])

    evaluated = sorted({m for s in splits for m in s["test_months"]})
    summary = {
        "n_periods": N_PERIODS, "n_splits": N_SPLITS, "stride": STRIDE,
        "n_months_development": len(months),
        "evaluated_span": [evaluated[0], evaluated[-1]],
        "n_evaluated_months": len(evaluated),
    }
    (RESULTS / "schedule_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
