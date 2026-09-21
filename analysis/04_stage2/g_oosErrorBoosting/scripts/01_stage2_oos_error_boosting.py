#!/usr/bin/env python3
"""Stage 2, seventh candidate: shallow gradient-boosted trees on the identical rows as
`f_oosErrorRidge` -- stage 1's h-step in-window out-of-sample error, standardised by its own
predictive se and winsorised at +/-3, pooled across provinces, forecast-time features only.

The only axis this candidate changes relative to `f_oosErrorRidge` is the model family: a
non-linear learner can represent interactions the ridge cannot (e.g. the forecast-level
effect differing by month or horizon, or a threshold in the trailing zero fraction that marks
a province switching from non-reporting to reporting). Everything else -- target, features,
training rows, combination rule (correction = zhat*se added to stage 1's mean, clipped at
zero, sigma unchanged), verification against `02_stage1`, abstention -- is `f_oosErrorRidge`'s
and is documented in that script's docstring rather than repeated here.

**Configuration** (agent-autonomous, a fixed modest setting rather than a search, as
`b_gradientBoosting` and `e_pooledRandomForest` chose for the same reproducibility and
overfitting reasons): GBM_PARAMS below -- depth-3 trees, slow learning rate, row subsampling,
a floor on leaf size. Trees are fitted to a winsorised target, so their output is already
bounded; the prediction is clipped at +/-ZCLIP regardless, as the ridge's is.

**Seeds (Rule 6)**: row subsampling (`subsample` < 1) is real randomness, pinned via
`random_state = component_seed("04_stage2/g_oosErrorBoosting")`.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/g_oosErrorBoosting
ANALYSIS = NODE.parents[1]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402
from lib.project_seed import component_seed  # noqa: E402
from lib.residual_features import WARMUP_MONTHS, fit_stage1, insample_residuals, residual_scale  # noqa: E402
from lib.stage2_oos import ZCLIP, check_horizons, design_matrix, features, national_index, test_rows, training_rows  # noqa: E402

DATA_NODE = ANALYSIS / "01_data"
DEV_CSV = DATA_NODE / "01_prepare" / "results" / "development.csv"
MODELABILITY = DATA_NODE / "02_characterise" / "results" / "modelability_summary.json"
SCHEDULE_CSV = DATA_NODE / "03_backtest_scheme" / "results" / "split_schedule.csv"
SCHEDULE_SUMMARY = DATA_NODE / "03_backtest_scheme" / "results" / "schedule_summary.json"
STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
RESULTS = NODE / "results"

VERIFY_ATOL = 1e-6
SEED = component_seed("04_stage2/g_oosErrorBoosting")
GBM_PARAMS = dict(n_estimators=150, max_depth=3, learning_rate=0.05, subsample=0.8,
                  min_samples_leaf=20, random_state=SEED)
CLIP_AT_ZERO = True
MIN_TRAIN_ROWS = 200


def load_series(province, months, dev_rows):
    idx = pd.PeriodIndex(months, freq="M")
    values = {r["time_period"]: r["disease_cases"] for r in dev_rows if r["location"] == province}
    data = [float(values[m]) if values.get(m, "") not in ("", None) else float("nan") for m in months]
    return pd.Series(data, index=idx)


def load_actuals(province, dev_rows):
    return {r["time_period"]: float(r["disease_cases"])
            for r in dev_rows if r["location"] == province and r["disease_cases"] != ""}


def read_schedule():
    with SCHEDULE_CSV.open(newline="") as f:
        return [{**row, "test_months": row["test_months"].split(";")} for row in csv.DictReader(f)]


def load_stage1_cells():
    with STAGE1_CELLS_CSV.open(newline="") as f:
        return {(r["province"], r["split"], r["month"]): r for r in csv.DictReader(f)}


def make_model():
    return GradientBoostingRegressor(**GBM_PARAMS)


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    all_months = sorted({r["time_period"] for r in dev_rows})
    modelable = json.loads(MODELABILITY.read_text())["modelable_provinces"]
    schedule = read_schedule()
    # The horizon set stage 2 is trained on is the evaluation scheme's, read from the
    # schedule (plan §4: n_periods = 3, the Chap default this project's scheme reuses) --
    # every horizon the backtest scores, and refused if the splits disagree with the scheme.
    n_ahead = check_horizons(schedule, json.loads(SCHEDULE_SUMMARY.read_text()))
    feature_names = features(n_ahead)
    stage1_cells = load_stage1_cells()
    actuals_by_p = {p: load_actuals(p, dev_rows) for p in modelable}

    per_cell, coef_rows = [], []
    n_fit_failures = n_abstained = n_verified = 0
    max_dm = max_ds = 0.0
    n_train_rows_by_split = {}

    for split in schedule:
        train_months = [m for m in all_months if m <= split["train_end"]]
        n_test = len(split["test_months"])  # == n_ahead, guaranteed by check_horizons
        state = {}
        for p in modelable:
            series = load_series(p, train_months, dev_rows)
            try:
                fit = fit_stage1(series)
            except Exception as exc:  # noqa: BLE001 -- a recorded outcome
                n_fit_failures += 1
                state[p] = exc
                continue
            fc = fit.get_forecast(steps=n_test).summary_frame()
            for month, (_, row) in zip(split["test_months"], fc.iterrows()):
                ref = stage1_cells.get((p, split["split"], month))
                if ref is not None and ref["fit_failed"] == "False":
                    max_dm = max(max_dm, abs(float(row["mean"]) - float(ref["forecast_mean"])))
                    max_ds = max(max_ds, abs(float(row["mean_se"]) - float(ref["forecast_se"])))
                    n_verified += 1
            resid = insample_residuals(fit, series)
            state[p] = dict(series=series, fit=fit, fc=fc, resid=resid, scale=residual_scale(resid),
                            log_train_mean=float(np.log1p(max(series.iloc[WARMUP_MONTHS:].mean(), 0))))

        ok = {p: s for p, s in state.items() if isinstance(s, dict) and np.isfinite(s["scale"])}
        nat = national_index({p: s["resid"] for p, s in ok.items()}, {p: s["scale"] for p, s in ok.items()},
                             pd.PeriodIndex(train_months, freq="M"))

        rows = []
        for p, s in ok.items():
            rows += training_rows(p, s["fit"], s["series"], s["resid"], s["scale"], s["log_train_mean"], nat,
                                  n_ahead)
        n_train_rows_by_split[split["split"]] = len(rows)
        model = None
        if len(rows) >= MIN_TRAIN_ROWS:
            model = make_model()
            model.fit(design_matrix(rows, n_ahead), np.array([r["z"] for r in rows]))
            coef_rows.append({"split": split["split"],
                              **{f: float(c) for f, c in zip(feature_names, model.feature_importances_)}})

        for p in modelable:
            s = state[p]
            if not isinstance(s, dict):
                for month in split["test_months"]:
                    per_cell.append({"province": p, "split": split["split"], "month": month, "h": None,
                                     "actual": actuals_by_p[p].get(month), "stage1_mean": None, "stage1_se": None,
                                     "stage2_zhat": None, "stage2_correction": None, "stage2_abstained": None,
                                     "final_mean_unclipped": None, "final_mean": None, "final_se": None,
                                     "crps": None, "fit_failed": True, "error": str(s)[:200]})
                continue
            trows = test_rows(p, s["fc"], split["test_months"], s["series"], s["resid"], s["scale"],
                              s["log_train_mean"], nat, n_ahead) if p in ok else None
            zhat = (np.clip(model.predict(design_matrix(trows, n_ahead)), -ZCLIP, ZCLIP)
                    if (model is not None and trows is not None) else None)
            for h, (month, (_, row)) in enumerate(zip(split["test_months"], s["fc"].iterrows()), start=1):
                mu1, se1 = float(row["mean"]), float(row["mean_se"])
                if zhat is None:
                    zh, corr, abstained = 0.0, 0.0, True
                    n_abstained += 1
                else:
                    zh = float(zhat[h - 1])
                    corr, abstained = zh * se1, False
                unclipped = mu1 + corr
                final_mean = max(unclipped, 0.0) if CLIP_AT_ZERO else unclipped
                actual = actuals_by_p[p].get(month)
                crps = crps_gaussian(actual, final_mean, max(se1, 1e-6)) if actual is not None else None
                per_cell.append({"province": p, "split": split["split"], "month": month, "h": h,
                                 "actual": actual, "stage1_mean": mu1, "stage1_se": se1,
                                 "stage2_zhat": zh, "stage2_correction": corr, "stage2_abstained": abstained,
                                 "final_mean_unclipped": unclipped, "final_mean": final_mean, "final_se": se1,
                                 "crps": crps, "fit_failed": False, "error": None})

    if n_verified == 0 or max_dm > VERIFY_ATOL or max_ds > VERIFY_ATOL:
        raise RuntimeError(f"re-derived stage-1 forecast disagrees with 02_stage1's stored output: "
                           f"n={n_verified}, max|dmean|={max_dm:.3e}, max|dse|={max_ds:.3e}")

    RESULTS.mkdir(exist_ok=True)
    fieldnames = ["province", "split", "month", "h", "actual", "stage1_mean", "stage1_se", "stage2_zhat",
                  "stage2_correction", "stage2_abstained", "final_mean_unclipped", "final_mean", "final_se",
                  "crps", "fit_failed", "error"]
    with (RESULTS / "per_cell_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(per_cell)
    with (RESULTS / "feature_importances.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(coef_rows[0].keys()))
        w.writeheader()
        w.writerows(coef_rows)

    scored = [r for r in per_cell if r["crps"] is not None]
    summary = {
        "model": "stage1 SARIMAX(1,1,1)x(1,0,0,12) + gradient-boosted trees pooled across provinces on "
                 "the standardised h-step in-window out-of-sample error (z = error/se, winsorised at +/-3), "
                 "forecast-time features only; correction = zhat*se added to stage 1's mean, clipped at "
                 "zero; sigma unchanged from stage 1",
        "seed": SEED, "gbm_params": GBM_PARAMS, "zclip": ZCLIP, "clip_at_zero": CLIP_AT_ZERO, "features": feature_names,
        "horizon_months": n_ahead,
        "horizon_source": "01_data/03_backtest_scheme/results/schedule_summary.json n_periods (plan §4: the "
                          "evaluation scheme's default, Chap's n_periods = 3); stage 2 is trained on h = 1..horizon_months",
        "n_training_rows_by_split": n_train_rows_by_split,
        "n_provinces": len(modelable), "n_splits": len(schedule),
        "n_cells_total": len(per_cell), "n_cells_scored": len(scored),
        "n_fit_failures": n_fit_failures, "n_stage2_abstained": n_abstained,
        "mean_crps": sum(r["crps"] for r in scored) / len(scored) if scored else None,
        "verification_vs_stage1_stored_forecast": {"n_cells_verified": n_verified, "max_abs_diff_mean": max_dm,
                                                   "max_abs_diff_se": max_ds, "tolerance": VERIFY_ATOL},
    }
    (RESULTS / "conclusion.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
