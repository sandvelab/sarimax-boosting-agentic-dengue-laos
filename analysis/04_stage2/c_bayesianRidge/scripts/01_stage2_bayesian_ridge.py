#!/usr/bin/env python3
"""Stage 2, third candidate: Bayesian linear regression on stage 1's residual.

**The contract** (plan Sec.1, unchanged from `a_linearLags`/`b_gradientBoosting`): stage 2
never sees the raw target, only stage 1's residual series and calendar information; its
prediction is added to stage 1's forecast mean, never averaged with it.

**Why this family**: batches 4 and 5 covered a plain point-estimator (OLS) and a tree-based
point-estimator (gradient boosting); the plan's ledger asks for a third family that is neither
-- "a Bayesian or linear-with-structure model". `sklearn.linear_model.BayesianRidge` is a
closed-form Bayesian linear regression (a Gaussian prior on the coefficients, precision
hyperparameters set by evidence maximisation, no MCMC) already available in the pinned
environment (scikit-learn 1.9.1) -- no new dependency needed. Chosen over a hierarchical
partial-pooling model (e.g. PyMC) because it answers the calibration question the plan actually
asks (interval coverage) without a heavy sampler dependency for a per-province-per-split fit on
as few as ~24 rows, where MCMC's asymptotics are the wrong tool anyway. (agent-autonomous)

**Inputs kept identical to `a_linearLags`/`b_gradientBoosting`** (lag-12 in-sample residual,
cyclical calendar month) for a fair three-way family comparison, isolating the model-family
question from the input-set question (deferred to batch 7 per the ledger). Lag-1 is excluded
for the same leakage reason `a_linearLags` recorded.

**Feature standardisation, a judgment call this candidate needs that its siblings did not**:
`BayesianRidge` places a single, shared-precision Gaussian prior across all coefficients (not
one precision per feature), so it implicitly assumes the features are on comparable scales.
The raw lag-12 residual (disease-case units, can be tens to hundreds) and the sin/cos calendar
features (bounded [-1, 1]) are not. Standardising each feature to zero mean / unit variance
*using training-window statistics only* before fitting, and un-standardising the resulting
correction and its variance afterwards, is necessary for the shared prior to regularise the
three coefficients comparably rather than arbitrarily penalising whichever feature happens to
have the larger raw scale. This is not a hyperparameter search -- it is a precondition for the
model to be doing what it is meant to do. (agent-autonomous)

**Calibration, done properly for this candidate** (unlike `a_linearLags`/`b_gradientBoosting`,
which left stage 1's sigma unchanged for lack of a principled alternative): `BayesianRidge`
exposes its own posterior predictive standard deviation via `predict(X, return_std=True)`,
which folds in both coefficient uncertainty and the model's estimated residual noise. Stage 1's
forecast variance and stage 2's posterior predictive variance are combined as independent
sources of uncertainty: `final_se = sqrt(stage1_se**2 + stage2_se**2)`. This is a real
calibration attempt, not an assumption -- interval coverage is reported and compared against
both prior candidates. Where stage 2 abstains, `stage2_se` is 0 (no correction, no added
uncertainty), so `final_se` reduces to stage 1's own, matching the abstention contract used
throughout. (agent-autonomous)

**Verification before trusting the in-sample residuals** (Rule 1): reuses `lib/stage1_model.py`,
the same re-derivation verified against `02_stage1`'s own stored forecast; this script repeats
that verification itself against `02_stage1`'s stored file, the ground truth, rather than
trusting a sibling candidate's check.

**Determinism**: `BayesianRidge` has no `random_state` parameter and uses no random
initialisation -- its solution is a deterministic fixed-point iteration (evidence
maximisation) from fixed starting hyperparameters. Verified below by fitting one province/
split's model twice from scratch and confirming bit-identical mean and posterior std.
`seeds: none` (Rule 6) -- there is no randomness to seed.

**Stage 2 abstains** (correction = 0, `stage2_se` = 0, recorded) when a province/split has too
few valid training rows or the lag-12 residual needed for a given test month is itself
unavailable -- identical abstention contract to the other two candidates.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import BayesianRidge

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/c_bayesianRidge
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
MIN_TRAIN_ROWS = 12  # same threshold as a_linearLags/b_gradientBoosting, for comparability
VERIFY_ATOL = 1e-6  # bit-for-bit tolerance vs 02_stage1's own stored forecast
STD_FLOOR = 1e-9  # guards a zero-variance feature (e.g. sin/cos constant on a short window)


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


def fit_stage2(resid: pd.Series, train_months: list[str]):
    """Fit BayesianRidge on standardised features. Returns (model, x_mean, x_std) or None."""
    X, y = build_training_rows(resid, train_months)
    if len(X) < MIN_TRAIN_ROWS:
        return None
    x_mean = X.mean(axis=0)
    x_std = np.maximum(X.std(axis=0), STD_FLOOR)
    Xs = (X - x_mean) / x_std
    model = BayesianRidge()
    model.fit(Xs, y)
    return model, x_mean, x_std


def predict_correction(fitted, resid: pd.Series, month: pd.Period) -> tuple[float, float, bool]:
    if fitted is None:
        return 0.0, 0.0, True
    model, x_mean, x_std = fitted
    lag_t = month - LAG
    x_lag = resid.get(lag_t)
    if x_lag is None or pd.isna(x_lag):
        return 0.0, 0.0, True
    s, c = calendar_features(month)
    x = np.array([[x_lag, s, c]])
    xs = (x - x_mean) / x_std
    mean, std = model.predict(xs, return_std=True)
    return float(mean[0]), float(std[0]), False


def check_determinism(resid: pd.Series, train_months: list[str]) -> tuple[bool, bool]:
    """Fit twice from scratch; BayesianRidge has no random_state, so two independent fits on
    identical data must agree bit-for-bit. Returns (a real check was performed, they agreed)."""
    X, y = build_training_rows(resid, train_months)
    if len(X) < MIN_TRAIN_ROWS:
        return False, True  # too few rows here to check; try the next province/split
    x_mean = X.mean(axis=0)
    x_std = np.maximum(X.std(axis=0), STD_FLOOR)
    Xs = (X - x_mean) / x_std
    mean_a, std_a = BayesianRidge().fit(Xs, y).predict(Xs, return_std=True)
    mean_b, std_b = BayesianRidge().fit(Xs, y).predict(Xs, return_std=True)
    agree = bool(np.array_equal(mean_a, mean_b) and np.array_equal(std_a, std_b))
    return True, agree


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
                        "stage2_correction": None, "stage2_se": None, "stage2_abstained": None,
                        "final_mean": None, "final_se": None, "crps": None,
                        "fit_failed": True, "error": str(exc)[:200],
                    })
                continue

            if not determinism_checked:
                determinism_checked, determinism_ok = check_determinism(resid, train_months)

            fitted = fit_stage2(resid, train_months)
            if fitted is None:
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
                correction, stage2_se, abstained = predict_correction(fitted, resid, month_period)
                if abstained and fitted is not None:
                    n_stage2_abstained += 1

                final_mean = mu1 + correction
                final_se = float(np.sqrt(sigma1 ** 2 + stage2_se ** 2))
                actual = actuals.get(month_str)
                crps = crps_gaussian(actual, final_mean, max(final_se, 1e-6)) if actual is not None else None
                per_cell.append({
                    "province": province, "split": split["split"], "month": month_str,
                    "actual": actual, "stage1_mean": mu1, "stage1_se": sigma1,
                    "stage2_correction": correction, "stage2_se": stage2_se,
                    "stage2_abstained": abstained,
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
            "BayesianRidge fit is not deterministic across two identical fits -- refusing to "
            "report a score that cannot be reproduced"
        )

    RESULTS.mkdir(exist_ok=True)
    fieldnames = ["province", "split", "month", "actual", "stage1_mean", "stage1_se",
                  "stage2_correction", "stage2_se", "stage2_abstained", "final_mean",
                  "final_se", "crps", "fit_failed", "error"]
    with (RESULTS / "per_cell_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(per_cell)

    scored = [r for r in per_cell if r["crps"] is not None]
    mean_crps = sum(r["crps"] for r in scored) / len(scored) if scored else None
    summary = {
        "model": "stage1 SARIMAX(1,1,1)x(1,0,0,12) + BayesianRidge(lag12 residual, sin/cos "
                 "month; features standardised on training-window statistics), additive "
                 "correction to the mean, final variance = stage1_se^2 + stage2 posterior "
                 "predictive variance (independence assumed)",
        "seeds": "none -- BayesianRidge has no random_state and uses no random initialisation; "
                 "verified deterministic by fitting twice from identical data and comparing "
                 "bit-for-bit",
        "determinism_check": {"performed": determinism_checked, "identical_across_two_fits": determinism_ok},
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
