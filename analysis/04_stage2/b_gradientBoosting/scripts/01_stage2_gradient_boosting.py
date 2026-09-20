#!/usr/bin/env python3
"""Stage 2, tree-based candidate: gradient-boosted regression trees on stage 1's residual.

**The contract** (plan Sec.1, unchanged from `a_linearLags`): stage 2 never sees the raw
target, only stage 1's residual series and calendar information; its prediction is added to
stage 1's forecast mean, never averaged with it.

**Inputs kept identical to `a_linearLags`** (lag-12 in-sample residual, cyclical calendar
month) rather than exploring a different input set here -- a deliberate choice to isolate the
model-family comparison (linear vs. tree) from the input-set question. Plan's ledger names
"what stage 2 is allowed to see" as its own fork, explored separately in later batches; folding
both changes into one candidate would leave it unclear which change caused any difference in
score. Lag-1 was rejected for the same leakage reason `a_linearLags` recorded: it is only
observed at forecast time for the first of the 3 test months in a split, not the second or
third, so using it would require either leaking future actuals or an asymmetric feature set
across test-month position -- not attempted here. (agent-autonomous)

**Verification before trusting the in-sample residuals** (Rule 1): reuses
`lib/stage1_model.py`, the same re-derivation of stage 1's exact spec `a_linearLags` verified
against `02_stage1`'s own stored forecast. This script re-runs that same verification itself
(rather than trusting the sibling node's check) since 02_stage1's stored file, not
a_linearLags's result, is the ground truth being checked against.

**Model**: `sklearn.ensemble.GradientBoostingRegressor`, regularised for the very small
per-province-per-split training windows here (as few as ~24 present months for some
provinces, `MIN_TRAIN_ROWS` further below that): shallow trees (`max_depth=2`), a small
ensemble (`n_estimators=50`) and a conservative learning rate (`learning_rate=0.05`), rather
than scikit-learn's defaults (`n_estimators=100`, unlimited depth via `max_depth=3` with much
more capacity than ~12-40 training rows can support without memorising them). This is a
logged judgment call, not a search over hyperparameters -- a first, defensible default for
the tree family, in the same spirit as stage 1's SARIMAX order. (agent-autonomous)

**Determinism**: `subsample=1.0` and `max_features=None` (all 3 features used, no random
feature subsampling) mean this configuration draws no real randomness during fit -- verified
below by fitting one province/split's model twice with different `random_state` values and
confirming identical predictions, the same spot-check discipline stage 1 used. A seeded
`random_state` (Rule 6, `lib/project_seed.py`) is still passed, for defensiveness against a
future change to these settings that would introduce real randomness.

**Sigma is left unchanged from stage 1** (same judgment call and same reasoning as
`a_linearLags`, for direct comparability): stage 2 corrects the Gaussian's mean only; interval
coverage is reported alongside CRPS for both stages so an overconfident combination would show
up in a file, not be assumed away.

**Stage 2 abstains** (correction = 0, recorded) when a province/split has too few valid
training rows or the lag-12 residual needed for a given test month is itself unavailable --
identical abstention contract to `a_linearLags`.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/b_gradientBoosting
ANALYSIS = NODE.parents[1]  # analysis/
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402
from lib.project_seed import component_seed  # noqa: E402
from lib.stage1_model import fit_and_forecast  # noqa: E402

DATA_NODE = ANALYSIS / "01_data"
STAGE1_NODE = ANALYSIS / "02_stage1"
DEV_CSV = DATA_NODE / "01_prepare" / "results" / "development.csv"
MODELABILITY = DATA_NODE / "02_characterise" / "results" / "modelability_summary.json"
SCHEDULE_CSV = DATA_NODE / "03_backtest_scheme" / "results" / "split_schedule.csv"
STAGE1_CELLS_CSV = STAGE1_NODE / "results" / "per_cell_scores.csv"
RESULTS = NODE / "results"

LAG = 12
MIN_TRAIN_ROWS = 12  # same threshold as a_linearLags, for comparability
VERIFY_ATOL = 1e-6  # bit-for-bit tolerance vs 02_stage1's own stored forecast

SEED = component_seed("04_stage2/b_gradientBoosting")
GBM_PARAMS = dict(
    n_estimators=50, max_depth=2, learning_rate=0.05,
    subsample=1.0, max_features=None, random_state=SEED,
)


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


def build_training_rows(resid: pd.Series, train_months: list[str]) -> tuple[np.ndarray, np.ndarray]:
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
        rows.append([x_lag, s, c])
        targets.append(y)
    return np.array(rows), np.array(targets)


def fit_stage2(resid: pd.Series, train_months: list[str]) -> GradientBoostingRegressor | None:
    X, y = build_training_rows(resid, train_months)
    if len(X) < MIN_TRAIN_ROWS:
        return None
    model = GradientBoostingRegressor(**GBM_PARAMS)
    model.fit(X, y)
    return model


def predict_correction(
    model: GradientBoostingRegressor | None, resid: pd.Series, month: pd.Period
) -> tuple[float, bool]:
    if model is None:
        return 0.0, True
    lag_t = month - LAG
    x_lag = resid.get(lag_t)
    if x_lag is None or pd.isna(x_lag):
        return 0.0, True
    s, c = calendar_features(month)
    x = np.array([[x_lag, s, c]])
    return float(model.predict(x)[0]), False


def check_determinism(resid: pd.Series, train_months: list[str]) -> tuple[bool, bool]:
    """Fit twice with different random_state; GBM_PARAMS draws no real randomness
    (subsample=1.0, max_features=None), so predictions must match bit-for-bit regardless.
    Returns (a real check was performed, the two fits agreed)."""
    X, y = build_training_rows(resid, train_months)
    if len(X) < MIN_TRAIN_ROWS:
        return False, True  # too few rows here to check; try the next province/split
    params_a = {**GBM_PARAMS, "random_state": 1}
    params_b = {**GBM_PARAMS, "random_state": 2}
    pred_a = GradientBoostingRegressor(**params_a).fit(X, y).predict(X)
    pred_b = GradientBoostingRegressor(**params_b).fit(X, y).predict(X)
    return True, bool(np.allclose(pred_a, pred_b, atol=1e-12))


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
    determinism_checked = False
    determinism_ok = True

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

            if not determinism_checked:
                determinism_checked, determinism_ok = check_determinism(resid, train_months)

            model = fit_stage2(resid, train_months)
            if model is None:
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
                correction, abstained = predict_correction(model, resid, month_period)
                if abstained and model is not None:
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
    if not determinism_ok:
        raise RuntimeError(
            "gradient-boosting fit is not deterministic under a fixed feature/subsample "
            "configuration -- refusing to report a score that cannot be reproduced"
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
        "model": "stage1 SARIMAX(1,1,1)x(1,0,0,12) + GradientBoostingRegressor(lag12 residual, "
                 "sin/cos month; n_estimators=50, max_depth=2, learning_rate=0.05), additive "
                 "correction to the mean, sigma unchanged from stage 1",
        "seed": SEED,
        "gbm_params": {k: v for k, v in GBM_PARAMS.items()},
        "determinism_check": {"performed": determinism_checked, "identical_across_random_state": determinism_ok},
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
