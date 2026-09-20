#!/usr/bin/env python3
"""Baseline: seasonal climatology (next month = mean of that calendar month in the
training window), through the same native pipeline.

Point forecast per test month: the mean of `disease_cases` across all training-window years
sharing that calendar month, for the given province, using only months observed by
`train_end` (an expanding window, matching every other model in this project).

As with persistence, CRPS needs a distributional forecast and climatology has none natively.
Sigma here is the empirical standard deviation of that same calendar month's training-window
values -- the spread the climatology mean itself already summarises, not a separate estimate
from a different quantity (logged judgment call, batch 3, agent-autonomous). A calendar month
with a single training-window observation (std undefined) falls back to the sigma floor.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[1] / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402

DATA_NODE = NODE.parents[1] / "01_data"
DEV_CSV = DATA_NODE / "01_prepare" / "results" / "development.csv"
MODELABILITY = DATA_NODE / "02_characterise" / "results" / "modelability_summary.json"
SCHEDULE_CSV = DATA_NODE / "03_backtest_scheme" / "results" / "split_schedule.csv"
RESULTS = NODE / "results"

MIN_SIGMA = 1e-6


def load_actuals(province: str, dev_rows: list[dict]) -> dict[str, float]:
    return {
        r["time_period"]: float(r["disease_cases"])
        for r in dev_rows
        if r["location"] == province and r["disease_cases"] != ""
    }


def read_schedule() -> list[dict]:
    with SCHEDULE_CSV.open(newline="") as f:
        return [
            {**row, "test_months": row["test_months"].split(";")}
            for row in csv.DictReader(f)
        ]


def calendar_month(period: str) -> str:
    return period.split("-")[1]


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    modelable = json.loads(MODELABILITY.read_text())["modelable_provinces"]
    schedule = read_schedule()

    per_cell = []
    n_fit_failures = 0
    for province in modelable:
        actuals = load_actuals(province, dev_rows)
        for split in schedule:
            train_end = split["train_end"]
            train_actuals = {m: v for m, v in actuals.items() if m <= train_end}
            for month in split["test_months"]:
                cm = calendar_month(month)
                same_month_values = [v for m, v in train_actuals.items() if calendar_month(m) == cm]
                actual = actuals.get(month)
                if not same_month_values:
                    n_fit_failures += 1
                    per_cell.append({
                        "province": province, "split": split["split"], "month": month,
                        "actual": actual, "forecast_mean": None, "forecast_se": None,
                        "crps": None, "fit_failed": True,
                        "error": "no training-window observation for this calendar month",
                    })
                    continue

                mean_val = statistics.fmean(same_month_values)
                sigma = (statistics.stdev(same_month_values)
                         if len(same_month_values) >= 2 else float("nan"))
                if not (sigma > 0):
                    sigma = MIN_SIGMA
                crps = crps_gaussian(actual, mean_val, max(sigma, MIN_SIGMA)) if actual is not None else None
                per_cell.append({
                    "province": province, "split": split["split"], "month": month,
                    "actual": actual, "forecast_mean": mean_val, "forecast_se": sigma,
                    "crps": crps, "fit_failed": False, "error": None,
                })

    RESULTS.mkdir(exist_ok=True)
    fieldnames = ["province", "split", "month", "actual", "forecast_mean",
                  "forecast_se", "crps", "fit_failed", "error"]
    with (RESULTS / "per_cell_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(per_cell)

    scored = [r for r in per_cell if r["crps"] is not None]
    mean_crps = sum(r["crps"] for r in scored) / len(scored) if scored else None
    summary = {
        "model": "seasonal climatology (mean of same calendar month in training window), "
                 "sigma = std of same calendar month's training-window values",
        "n_provinces": len(modelable), "n_splits": len(schedule),
        "n_cells_total": len(per_cell), "n_cells_scored": len(scored),
        "n_fit_failures": n_fit_failures, "mean_crps": mean_crps,
    }
    (RESULTS / "conclusion.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
