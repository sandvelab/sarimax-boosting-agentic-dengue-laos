#!/usr/bin/env python3
"""Stage 2, first candidate: linear regression on stage 1's lag-12 residual + calendar month.

**The contract** (plan Sec.1): stage 2 never sees the raw target, only stage 1's residual
series and calendar information; its prediction is added to stage 1's forecast mean, never
averaged with it.

**Why lag-12 only, not lag-1** (a leakage check made and rejected during this batch, not
silently skipped): the backtest scheme forecasts 3 months per split. Lag-1 residual is
available for the first test month of a split (it is the last training residual), but for the
second and third test months lag-1 would be the *previous test month's* residual -- unknown
at forecast time in a real deployment, since it depends on an actual that has not been
observed yet. Lag-12 has no such problem: 12 months before *any* test month in this scheme
still falls inside the training window (the test window is only 3 months wide), so it is
always known at forecast time regardless of which of the 3 test months is being predicted.
This keeps stage 2 to information genuinely available at forecast time.

**Verification before trusting the in-sample residuals** (Rule 1): `lib/stage1_model.py`
re-derives stage 1's exact spec rather than importing 02_stage1's script (that node's script
and results are its own closed record, AGENTS.md Sec.1). Before this script trusts the
re-derived residuals, it checks the re-derived out-of-sample forecast against 02_stage1's own
stored `per_cell_scores.csv`, cell for cell, and refuses to proceed if they disagree beyond
floating-point tolerance.

**Sigma is left unchanged from stage 1** (logged judgment call, agent-autonomous): stage 2
corrects the Gaussian's mean; it does not attempt to characterise the spread of its own
correction's error, which would need a second, nested resampling within an already-small
per-province-per-split training window (as few as ~24 present months for some provinces).
This is deferred rather than hidden -- interval coverage is computed for both stage 1 alone
and the two-stage ensemble (`compare_to_stage1.py`) precisely so that if this default makes
the combined forecast overconfident, it shows up in a file rather than being assumed away.

**Stage 2 abstains rather than guesses** when a province/split has too few valid training rows
(fewer than MIN_TRAIN_ROWS) or the lag-12 residual needed for a specific test month is itself
unavailable (missing actual 12 months back) -- the correction is 0 for that cell, and the
abstention is recorded, not silently absorbed into the score.
"""
from __future__ import annotations

import csv
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/a_linearLags
ANALYSIS = NODE.parents[1]  # analysis/
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402
from lib.stage1_model import fit_and_forecast  # noqa: E402

DATA_NODE = ANALYSIS / "01_data"
STAGE1_NODE = ANALYSIS / "02_stage1"
DEV_CSV = DATA_NODE / "01_prepare" / "results" / "development.csv"
MODELABILITY = DATA_NODE / "02_characterise" / "results" / "modelability_summary.json"
SCHEDULE_CSV = DATA_NODE / "03_backtest_scheme" / "results" / "split_schedule.csv"
STAGE1_CELLS_CSV = STAGE1_NODE / "results" / "per_cell_scores.csv"
RESULTS = NODE / "results"

LAG = 12
MIN_TRAIN_ROWS = 12  # 4 regression parameters; require >=3x that many valid rows
VERIFY_ATOL = 1e-6  # bit-for-bit tolerance vs 02_stage1's own stored forecast


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


def load_stage1_cells() -> dict[tuple[str, str, str], dict]:
    with STAGE1_CELLS_CSV.open(newline="") as f:
        return {
            (r["province"], r["split"], r["month"]): r
            for r in csv.DictReader(f)
        }


def calendar_features(period: pd.Period) -> tuple[float, float]:
    angle = 2 * np.pi * period.month / 12
    return np.sin(angle), np.cos(angle)


def fit_stage2(resid: pd.Series, train_months: list[str]) -> np.ndarray | None:
    """OLS on [1, lag12_resid, sin(month), cos(month)] -> resid(t), training rows only."""
    idx = pd.PeriodIndex(train_months, freq="M")
    rows, targets = [], []
    for t in idx:
        lag_t = t - LAG
        if lag_t not in resid.index:
            continue
        y = resid.get(t)
        x_lag = resid.get(lag_t)
        if pd.isna(y) or pd.isna(x_lag):
            continue
        s, c = calendar_features(t)
        rows.append([1.0, x_lag, s, c])
        targets.append(y)
    if len(rows) < MIN_TRAIN_ROWS:
        return None
    X = np.array(rows)
    y = np.array(targets)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef


def predict_correction(coef: np.ndarray | None, resid: pd.Series, month: pd.Period) -> tuple[float, bool]:
    if coef is None:
        return 0.0, True
    lag_t = month - LAG
    x_lag = resid.get(lag_t)
    if x_lag is None or pd.isna(x_lag):
        return 0.0, True
    s, c = calendar_features(month)
    x = np.array([1.0, x_lag, s, c])
    return float(coef @ x), False


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    all_months = sorted({r["time_period"] for r in dev_rows})
    modelable = json.loads(MODELABILITY.read_text())["modelable_provinces"]
    schedule = read_schedule()
    stage1_cells = load_stage1_cells()

    per_cell = []
    n_fit_failures = 0
    n_stage2_abstained = 0
    max_abs_diff_mean = 0.0
    max_abs_diff_se = 0.0
    n_verified = 0

    for province in modelable:
        actuals = load_actuals(province, dev_rows)
        for split in schedule:
            train_end = split["train_end"]
            train_months = [m for m in all_months if m <= train_end]
            series = load_series(province, train_months, dev_rows)
            try:
                fc, resid = fit_and_forecast(series, len(split["test_months"]))
            except Exception as exc:  # noqa: BLE001 - a fit failure is a recorded outcome
                n_fit_failures += 1
                for month in split["test_months"]:
                    per_cell.append({
                        "province": province, "split": split["split"], "month": month,
                        "actual": actuals.get(month), "stage1_mean": None, "stage1_se": None,
                        "stage2_correction": None, "stage2_abstained": None,
                        "final_mean": None, "final_se": None, "crps": None,
                        "fit_failed": True, "error": str(exc)[:200],
                    })
                continue

            coef = fit_stage2(resid, train_months)
            if coef is None:
                n_stage2_abstained += len(split["test_months"])

            for month_str, (_, row) in zip(split["test_months"], fc.iterrows()):
                mu1, sigma1 = float(row["mean"]), float(row["mean_se"])

                ref = stage1_cells.get((province, split["split"], month_str))
                if ref is not None and ref["fit_failed"] == "False":
                    ref_mu, ref_se = float(ref["forecast_mean"]), float(ref["forecast_se"])
                    max_abs_diff_mean = max(max_abs_diff_mean, abs(mu1 - ref_mu))
                    max_abs_diff_se = max(max_abs_diff_se, abs(sigma1 - ref_se))
                    n_verified += 1

                month_period = pd.Period(month_str, freq="M")
                correction, abstained = predict_correction(coef, resid, month_period)
                if abstained and coef is not None:
                    n_stage2_abstained += 1

                final_mean = mu1 + correction
                final_se = sigma1  # unchanged from stage 1 -- see module docstring
                actual = actuals.get(month_str)
                crps = crps_gaussian(actual, final_mean, max(final_se, 1e-6)) if actual is not None else None
                per_cell.append({
                    "province": province, "split": split["split"], "month": month_str,
                    "actual": actual, "stage1_mean": mu1, "stage1_se": sigma1,
                    "stage2_correction": correction, "stage2_abstained": abstained,
                    "final_mean": final_mean, "final_se": final_se, "crps": crps,
                    "fit_failed": False, "error": None,
                })

    if n_verified == 0:
        raise RuntimeError("no cells verified against 02_stage1's stored forecast -- refusing to proceed")
    if max_abs_diff_mean > VERIFY_ATOL or max_abs_diff_se > VERIFY_ATOL:
        raise RuntimeError(
            f"re-derived stage-1 forecast disagrees with 02_stage1's stored per_cell_scores.csv "
            f"beyond tolerance: max|Δmean|={max_abs_diff_mean:.3e}, max|Δse|={max_abs_diff_se:.3e} "
            f"over {n_verified} cells -- refusing to trust the re-derived residuals"
        )

    RESULTS.mkdir(exist_ok=True)
    fieldnames = ["province", "split", "month", "actual", "stage1_mean", "stage1_se",
                  "stage2_correction", "stage2_abstained", "final_mean", "final_se",
                  "crps", "fit_failed", "error"]
    with (RESULTS / "per_cell_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(per_cell)

    scored = [r for r in per_cell if r["crps"] is not None]
    mean_crps = sum(r["crps"] for r in scored) / len(scored) if scored else None
    summary = {
        "model": "stage1 SARIMAX(1,1,1)x(1,0,0,12) + linear(lag12 residual, sin/cos month), "
                 "additive correction to the mean, sigma unchanged from stage 1",
        "n_provinces": len(modelable), "n_splits": len(schedule),
        "n_cells_total": len(per_cell), "n_cells_scored": len(scored),
        "n_fit_failures": n_fit_failures, "n_stage2_abstained": n_stage2_abstained,
        "mean_crps": mean_crps,
        "verification_vs_stage1_stored_forecast": {
            "n_cells_verified": n_verified,
            "max_abs_diff_mean": max_abs_diff_mean,
            "max_abs_diff_se": max_abs_diff_se,
            "tolerance": VERIFY_ATOL,
        },
    }
    (RESULTS / "conclusion.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
