#!/usr/bin/env python3
"""Stage 1: a per-province SARIMAX, backtested on the development data.

First, defensible default specification (plan §4b, this batch): SARIMAX(1,1,1) with a
seasonal AR(1) term at lag 12 (the annual dengue cycle), fitted directly on raw
`disease_cases` -- no transform. A log1p transform was considered and deferred rather than
silently skipped: scoring a transformed forecast against the raw target correctly needs
either a bias-corrected back-transform or CRPS computed on the transformed scale, and this
batch's verified metric (00_metric) is Gaussian CRPS on whatever scale the forecast and
observation share. Fitting on the raw scale keeps that scale-match exact for this first
default; it is expected to be a weak model for the zero-heavy provinces (predictable
over-dispersion, occasional negative forecast means treated at face value by the Gaussian
CRPS) and the transform is logged here as a fork for a later batch, not hidden.

Refit at every split (expanding window, matching the prior project's own "n_retrain=1"
convention, reused for comparability -- plan §4b). Missing months are left as NaN; the
Kalman filter statsmodels' state-space SARIMAX runs on handles missing observations natively.
"""
from __future__ import annotations

import csv
import json
import sys
import warnings
from pathlib import Path

import pandas as pd
import statsmodels.api as sm

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[0] / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402

DATA_NODE = NODE.parent / "01_data"
DEV_CSV = DATA_NODE / "01_prepare" / "results" / "development.csv"
MODELABILITY = DATA_NODE / "02_characterise" / "results" / "modelability_summary.json"
SCHEDULE_CSV = DATA_NODE / "03_backtest_scheme" / "results" / "split_schedule.csv"
RESULTS = NODE / "results"

ORDER = (1, 1, 1)
SEASONAL_ORDER = (1, 0, 0, 12)


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
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = sm.tsa.statespace.SARIMAX(
                        series, order=ORDER, seasonal_order=SEASONAL_ORDER,
                        enforce_stationarity=False, enforce_invertibility=False,
                    )
                    fit = model.fit(disp=False)
                    forecast = fit.get_forecast(steps=len(split["test_months"]))
                    fc = forecast.summary_frame()
            except Exception as exc:  # noqa: BLE001 - a fit failure is a recorded outcome
                n_fit_failures += 1
                for month in split["test_months"]:
                    per_cell.append({
                        "province": province, "split": split["split"], "month": month,
                        "actual": actuals.get(month), "forecast_mean": None,
                        "forecast_se": None, "crps": None, "fit_failed": True,
                        "error": str(exc)[:200],
                    })
                continue

            for month, (_, row) in zip(split["test_months"], fc.iterrows()):
                mu, sigma = float(row["mean"]), float(row["mean_se"])
                actual = actuals.get(month)
                crps = crps_gaussian(actual, mu, max(sigma, 1e-6)) if actual is not None else None
                per_cell.append({
                    "province": province, "split": split["split"], "month": month,
                    "actual": actual, "forecast_mean": mu, "forecast_se": sigma,
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
        "model": f"SARIMAX{ORDER}x{SEASONAL_ORDER}, raw disease_cases, refit every split",
        "n_provinces": len(modelable), "n_splits": len(schedule),
        "n_cells_total": len(per_cell), "n_cells_scored": len(scored),
        "n_fit_failures": n_fit_failures, "mean_crps": mean_crps,
    }
    (RESULTS / "conclusion.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
