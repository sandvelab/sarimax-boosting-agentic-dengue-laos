#!/usr/bin/env python3
"""Stage 2, pooled-random-forest candidate, adapted from an external community model.

**Where this came from** (plan §3/§4: information gathering is recorded): the human pointed
at `github.com/chap-models`, a collection of forecasting models built to run inside the Chap
platform, and asked for one of them to be tried as a stage-2 family. `chap-models/
rwanda_random_forest` (Python, `sklearn.ensemble.RandomForestRegressor`) was picked from that
org over the R-based alternatives inspected (`XGBoost_for_Malawi`, `ewars_plus_template`,
`Vietnam-dengue-superensemble`) because it needs no new environment dependency -- this project
already pins `scikit-learn` (batch 5) -- and because its central structural idea, a **pooled**
model fit across every location at once rather than one model per location, is exactly the
"cross-province pooling" fork `04_stage2/claim.md` logged as untried at the end of batch 7.
`information: agent-retrieved` (fetched the org's repo listing and read
`rwanda_random_forest/train.py` and its README directly, not from memory); the choice of
*which* repo among the many available is `agent-autonomous`.

**What is reused from it, and what is not** -- this is an adaptation, not a port, and the
deviations are logged here rather than silently assumed:

1. **Reused**: the pooling idea itself (one `RandomForestRegressor` per backtest split, fit on
   every modelable province's training rows together, rather than `a_linearLags`/
   `b_gradientBoosting`/`c_bayesianRidge`/`d_linearClimate`'s independent per-province fits),
   and the choice of algorithm family (random forest -- bagging, not `b_gradientBoosting`'s
   boosting).
2. **Not reused: the original repo's own feature set** (rainfall/temperature at lags 1-3,
   plus the *target's own* lags 1-3). Lags 1-3 of the residual are leakage-unsafe for the
   second and third month of this project's 3-month test window -- the same argument
   `a_linearLags` made in batch 4 and every sibling candidate has followed since. This
   candidate uses `d_linearClimate`'s exact input instead (lag-12 residual, cyclical calendar
   month, lag-12 rainfall/temperature/humidity), so that pooling is the one axis this
   candidate changes relative to `d_linearClimate`, not pooling-and-a-different-input at once.
3. **Not reused: the original repo's malaria-incidence transform** (cases per 10,000
   population, log1p). This project's stage-2 contract (plan §1) is to predict stage 1's
   *residual*, not the raw target, and a residual is already a well-behaved, roughly
   zero-centred quantity -- no population normalisation or log transform is needed or
   appropriate for it.
4. **Not reused: the original repo's `RandomizedSearchCV` hyperparameter search** (60
   iterations, up to 1000 trees, depth up to 40, chosen by cross-validated RMSE). Run inside
   an 8-split backtest, a fresh randomized search per split would be expensive, would need its
   own seeding and reproducibility argument on top of the model's, and risks fitting to CV
   noise on data this small. A fixed, modest, regularised configuration is used instead, in
   the same spirit `b_gradientBoosting` used for its own tree-based candidate (shallow trees,
   few estimators) rather than searching a large hyperparameter space with in effect one
   backtest as the objective.

**The contract, calibration and abstention conventions are unchanged** from every stage-2
sibling: additive correction to stage 1's mean, sigma left at stage 1's value, corrections
recorded per cell rather than absorbed, and stage 1's forecast re-derived and verified
bit-for-bit against `02_stage1`'s stored output before its residuals are trusted.

**Seeding (Rule 6)**: unlike `b_gradientBoosting`'s configuration (`subsample=1.0`,
`max_features=None`, which draws no real randomness regardless of `random_state`), a random
forest's bootstrap resampling and per-split feature subsampling are real randomness, pinned by
`random_state=SEED` and `n_jobs=1` (avoids any thread-scheduling-order sensitivity in the
aggregation). Verified, per `/seed`, by running this script twice end to end and diffing
`results/per_cell_scores.csv` byte for byte -- recorded in this node's provenance, not
re-run automatically on every future invocation (that would double this node's cost forever
for a property that a fixed seed already guarantees deterministically).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/e_pooledRandomForest
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
CLIMATE_COLS = ["rainfall", "mean_temperature", "mean_relative_humidity"]
MIN_POOLED_ROWS = 60  # pooling ~17 provinces should clear this easily; a safety net, not a tune
VERIFY_ATOL = 1e-6  # bit-for-bit tolerance vs 02_stage1's own stored forecast

SEED = component_seed("04_stage2/e_pooledRandomForest")
RF_PARAMS = dict(
    n_estimators=200, max_depth=5, min_samples_leaf=5, max_features="sqrt",
    bootstrap=True, random_state=SEED, n_jobs=1,
)


def load_series(province: str, months: list[str], dev_rows: list[dict]) -> pd.Series:
    idx = pd.PeriodIndex(months, freq="M")
    values = {r["time_period"]: r["disease_cases"] for r in dev_rows if r["location"] == province}
    data = [float(values[m]) if values.get(m, "") not in ("", None) else float("nan")
            for m in months]
    return pd.Series(data, index=idx)


def load_climate(province: str, dev_rows: list[dict]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for r in dev_rows:
        if r["location"] != province:
            continue
        out[r["time_period"]] = {c: float(r[c]) for c in CLIMATE_COLS}
    return out


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


def climate_features(month_str: str, climate: dict[str, dict[str, float]]) -> list[float] | None:
    lag_month = str(pd.Period(month_str, freq="M") - LAG)
    row = climate.get(lag_month)
    if row is None:
        return None
    return [row[c] for c in CLIMATE_COLS]


def feature_row(t: pd.Period, resid: pd.Series, climate: dict[str, dict[str, float]]) -> list[float] | None:
    lag_t = t - LAG
    x_lag = resid.get(lag_t)
    if x_lag is None or pd.isna(x_lag):
        return None
    clim = climate_features(str(t), climate)
    if clim is None:
        return None
    s, c = calendar_features(t)
    return [x_lag, s, c, *clim]


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    all_months = sorted({r["time_period"] for r in dev_rows})
    modelable = json.loads(MODELABILITY.read_text())["modelable_provinces"]
    schedule = read_schedule()
    stage1_cells = load_stage1_cells()

    climate_by_province = {p: load_climate(p, dev_rows) for p in modelable}
    actuals_by_province = {p: load_actuals(p, dev_rows) for p in modelable}

    per_cell = []
    n_fit_failures = 0
    n_stage2_abstained = 0
    max_abs_diff_mean = 0.0
    max_abs_diff_se = 0.0
    n_verified = 0

    for split in schedule:
        train_end = split["train_end"]
        train_months = [m for m in all_months if m <= train_end]

        # Pass 1: per-province stage-1 fit + residuals for this split (needed regardless,
        # for stage1_mean/sigma1 and the verification check every sibling candidate runs).
        province_state: dict[str, tuple[pd.DataFrame, pd.Series] | Exception] = {}
        for province in modelable:
            series = load_series(province, train_months, dev_rows)
            try:
                province_state[province] = fit_and_forecast(series, len(split["test_months"]))
            except Exception as exc:  # noqa: BLE001 - a fit failure is a recorded outcome
                province_state[province] = exc

        # Pass 2: pool every province's training rows for this split into one training set.
        pooled_X, pooled_y = [], []
        for province in modelable:
            state = province_state[province]
            if isinstance(state, Exception):
                continue
            _, resid = state
            climate = climate_by_province[province]
            idx = pd.PeriodIndex(train_months, freq="M")
            for t in idx:
                lag_t = t - LAG
                if lag_t not in resid.index:
                    continue
                y = resid.get(t)
                if pd.isna(y):
                    continue
                row = feature_row(t, resid, climate)
                if row is None:
                    continue
                pooled_X.append(row)
                pooled_y.append(y)

        model = None
        if len(pooled_X) >= MIN_POOLED_ROWS:
            model = RandomForestRegressor(**RF_PARAMS)
            model.fit(np.array(pooled_X), np.array(pooled_y))

        # Pass 3: score every province's test months for this split with the split's one
        # shared model.
        for province in modelable:
            state = province_state[province]
            actuals = actuals_by_province[province]
            if isinstance(state, Exception):
                n_fit_failures += 1
                for month in split["test_months"]:
                    per_cell.append({
                        "province": province, "split": split["split"], "month": month,
                        "actual": actuals.get(month), "stage1_mean": None, "stage1_se": None,
                        "stage2_correction": None, "stage2_abstained": None,
                        "final_mean": None, "final_se": None, "crps": None,
                        "fit_failed": True, "error": str(state)[:200],
                    })
                continue

            fc, resid = state
            climate = climate_by_province[province]
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
                feat = feature_row(month_period, resid, climate) if model is not None else None
                if model is None or feat is None:
                    correction, abstained = 0.0, True
                    if model is not None:
                        n_stage2_abstained += 1
                else:
                    correction = float(model.predict(np.array([feat]))[0])
                    abstained = False

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
        "model": "stage1 SARIMAX(1,1,1)x(1,0,0,12) + RandomForestRegressor pooled across "
                 "provinces (one shared model per split; lag12 residual, sin/cos month, "
                 "lag12 rainfall/temperature/humidity), additive correction to the mean, "
                 "sigma unchanged from stage 1 -- adapted from chap-models/rwanda_random_forest",
        "seed": SEED, "rf_params": {k: v for k, v in RF_PARAMS.items()},
        "climate_columns": CLIMATE_COLS, "climate_lag": LAG,
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
