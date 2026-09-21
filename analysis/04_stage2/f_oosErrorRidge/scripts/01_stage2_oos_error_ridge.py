#!/usr/bin/env python3
"""Stage 2, sixth candidate: a pooled ridge regression on stage 1's h-step *out-of-sample*
forecast error, standardised by stage 1's own predictive se.

**What changes relative to every earlier candidate, and why** (batch 10; the evidence is in
`analysis/05_residualStructure/results/` and the literature the batch report cites):

1. **The target.** Candidates a-e were trained on stage 1's in-sample one-step residual,
   `series - fittedvalues`. `05_residualStructure` finds that residual essentially white
   (mean autocorrelation within +/-0.06 at every lag 1-12 on the final training window), so
   there was nothing in it to learn -- which is the stacking literature's standard warning
   against fitting a second level on in-sample fits (Wolpert 1992; Breiman 1996), and the
   hybrid-ARIMA literature's explanation of why residual bolt-ons often fail (Taskaya-Temizel
   & Casey 2005). What a stage 2 must correct is the 1-, 2- and 3-step-ahead out-of-sample
   error, whose scale grows with the horizon and whose structure is not white: stage 1
   over-predicts in two thirds of cells, more so at high forecast levels and in the
   off-season months, and under-predicts in the May-July onset. This candidate trains on
   exactly that quantity, computed inside each split's training window from every origin with
   stage 1's parameters fixed (`lib.residual_features.pseudo_oos_errors`), one row per
   (province, origin, horizon), for every horizon h = 1..n_ahead the evaluation scores (the
   scheme's n_periods, read from the schedule: 3 months, Chap's default) -- roughly 5,000 rows
   per split instead of ~100 per province.
   Horizon-specific correction of a recursive base forecast is the design of Ben Taieb &
   Hyndman (2014).

2. **The scale.** The target is z = error / se, winsorised at +/-3, and the correction is
   z-hat * se: pooled across all provinces (the one axis `e_pooledRandomForest` showed helps)
   but returned to each province's own scale, so the low-count provinces cannot receive a
   high-count province's correction -- the mechanism that broke `e_pooledRandomForest`'s
   calibration. Winsorising keeps the reporting-regime breaks of 2008-09 (|z| up to 164) from
   owning the fit and bounds every correction at three standard errors.

3. **The inputs.** Forecast-time features only (`lib.stage2_oos.features(n_ahead)`): horizon and
   target-month indicators, stage 1's forecast level relative to the province's residual
   scale, recent standardised residuals and their cross-province mean at the origin, trailing
   incidence against the typical year, trailing zero fraction. No climate: the diagnostics
   found no usable correlation with the error at lags 1-3 and the literature finds climate
   adds little beyond incidence at these horizons (Johansson et al. 2016, 2019; Benedum et al.
   2020) -- logged as a fork not taken.

4. **The family.** Ridge regression (alpha = RIDGE_ALPHA on standardised features): the
   diagnostics' cross-validated predictability test found the linear family competitive with
   trees on these features, and a linear pooled corrector is the recommended first step for
   global models (Montero-Manso & Hyndman 2021). `g_oosErrorBoosting` fits the non-linear
   sibling on identical rows.

**Combination rule.** final_mean = stage 1 mean + z-hat * se, then clipped at zero
(CLIP_AT_ZERO): a negative expected case count is impossible, and moving a Gaussian's mean
toward a non-negative observation can only lower its CRPS. The unclipped mean is stored per
cell as well, so `02_compare_to_stage1.py` reports the clip and the correction as separate
effects rather than one bundled number. Sigma is left at stage 1's value: `05_residualStructure`
shows that inflating it -- even with an oracle factor fixed on the test cells -- raises CRPS
from 26.05 to 35.65 while reaching 89.5% coverage, because the coverage deficit is a heavy
tail of regime-break cells, not a uniformly narrow interval; that finding rules the spread
fork out for this batch and is recorded in the node's provenance.

**Verification (Rule 1)** as every sibling: stage 1 is re-derived and checked cell for cell
against `02_stage1`'s stored forecast before any residual from it is used.

**Seeds (Rule 6)**: ridge regression is deterministic; no randomness is drawn.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NODE = Path(__file__).resolve().parents[1]  # analysis/04_stage2/f_oosErrorRidge
ANALYSIS = NODE.parents[1]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402
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
SEED = None  # no seed: ridge regression and SARIMAX maximum likelihood are deterministic
RIDGE_ALPHA = 10.0
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
    return make_pipeline(StandardScaler(), Ridge(alpha=RIDGE_ALPHA))


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
            ridge = model.named_steps["ridge"]
            coef_rows.append({"split": split["split"], "intercept": float(ridge.intercept_),
                              **{f: float(c) for f, c in zip(feature_names, ridge.coef_)}})

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
    with (RESULTS / "ridge_coefficients.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(coef_rows[0].keys()))
        w.writeheader()
        w.writerows(coef_rows)

    scored = [r for r in per_cell if r["crps"] is not None]
    summary = {
        "model": "stage1 SARIMAX(1,1,1)x(1,0,0,12) + ridge regression pooled across provinces on the "
                 "standardised h-step in-window out-of-sample error (z = error/se, winsorised at +/-3), "
                 "forecast-time features only; correction = zhat*se added to stage 1's mean, clipped at "
                 "zero; sigma unchanged from stage 1",
        "ridge_alpha": RIDGE_ALPHA, "zclip": ZCLIP, "clip_at_zero": CLIP_AT_ZERO, "features": feature_names,
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
