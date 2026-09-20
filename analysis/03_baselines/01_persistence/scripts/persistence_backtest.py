#!/usr/bin/env python3
"""Baseline: persistence (next month = last observed), through the same native pipeline.

Point forecast, all steps of a split: the last observed value at or before the split's
`train_end`, held flat across the whole test window (a genuine multi-step persistence
forecast, not re-anchored on true values the model would not have in a real forecast).

CRPS needs a distributional forecast (every model in this project is scored as Gaussian --
`analysis/scripts/lib/crps.py`), and persistence has none natively. Sigma here is the
empirical standard deviation of the province's own one-step persistence errors
(`value[t] - value[t-1]`) over the training window available at that split -- the historical
spread a naive forecaster would actually have seen, not a free parameter. This is a logged
judgment call (batch 3, agent-autonomous): a fixed small sigma or a per-horizon-scaled sigma
were both rejected as arbitrary next to an estimate the training data itself supports.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[1] / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402

DATA_NODE = NODE.parents[1] / "01_data"
DEV_CSV = DATA_NODE / "01_prepare" / "results" / "development.csv"
MODELABILITY = DATA_NODE / "02_characterise" / "results" / "modelability_summary.json"
SCHEDULE_CSV = DATA_NODE / "03_backtest_scheme" / "results" / "split_schedule.csv"
RESULTS = NODE / "results"

MIN_SIGMA = 1e-6


def load_series(province: str, months: list[str], dev_rows: list[dict]) -> pd.Series:
    idx = pd.PeriodIndex(months, freq="M")
    values = {r["time_period"]: r["disease_cases"] for r in dev_rows if r["location"] == province}
    data = [float(values[m]) if values.get(m, "") not in ("", None) else float("nan")
            for m in months]
    return pd.Series(data, index=idx)


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


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    all_months = sorted({r["time_period"] for r in dev_rows})
    modelable = json.loads(MODELABILITY.read_text())["modelable_provinces"]
    schedule = read_schedule()

    per_cell = []
    n_fit_failures = 0
    for province in modelable:
        actuals = load_actuals(province, dev_rows)
        for split in schedule:
            train_end = split["train_end"]
            train_months = [m for m in all_months if m <= train_end]
            series = load_series(province, train_months, dev_rows)
            observed = series.dropna()
            if observed.empty:
                n_fit_failures += 1
                for month in split["test_months"]:
                    per_cell.append({
                        "province": province, "split": split["split"], "month": month,
                        "actual": actuals.get(month), "forecast_mean": None,
                        "forecast_se": None, "crps": None, "fit_failed": True,
                        "error": "no observed value in training window",
                    })
                continue

            last_value = float(observed.iloc[-1])
            step_errors = observed.diff().dropna()
            sigma = float(step_errors.std(ddof=1)) if len(step_errors) >= 2 else float("nan")
            if not (sigma > 0):
                sigma = MIN_SIGMA

            for month in split["test_months"]:
                actual = actuals.get(month)
                crps = crps_gaussian(actual, last_value, max(sigma, MIN_SIGMA)) if actual is not None else None
                per_cell.append({
                    "province": province, "split": split["split"], "month": month,
                    "actual": actual, "forecast_mean": last_value, "forecast_se": sigma,
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
        "model": "persistence (last observed, held flat), sigma = std of training-window "
                 "one-step differences",
        "n_provinces": len(modelable), "n_splits": len(schedule),
        "n_cells_total": len(per_cell), "n_cells_scored": len(scored),
        "n_fit_failures": n_fit_failures, "mean_crps": mean_crps,
    }
    (RESULTS / "conclusion.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
