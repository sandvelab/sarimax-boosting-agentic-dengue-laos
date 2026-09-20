#!/usr/bin/env python3
"""What are stage 1's forecast errors, and what -- known at forecast time -- co-varies with them?

**Why this node exists** (batch 10): five stage-2 candidates were built on one unexamined
premise -- that stage 1's in-sample one-step residual, twelve months back, plus the calendar
month, carries the signal a correction needs. Four lost to stage 1 alone; the fifth won on
mean CRPS and lost on calibration. Before building a sixth, this node asks what the errors a
stage 2 must correct actually look like, on the stored development backtest (`02_stage1`'s
371 scored test cells), and which forecast-time-available quantities co-vary with them.

**Two objects are distinguished throughout**, because conflating them is the likeliest
reason the earlier candidates found nothing:

1. the **in-sample one-step residual** `series - fittedvalues` -- what every earlier
   candidate trained on;
2. the **out-of-sample h-step forecast error** `actual - forecast_mean` for h = 1, 2, 3 --
   what a stage 2 actually has to predict and add back.

For (2) this script also computes the same h-step error *inside* each split's training
window with stage 1's parameters fixed (`lib.residual_features.pseudo_oos_errors`), which
is what a leakage-safe stage 2 can train on; the comparison of its spread to the true test
errors' spread says whether an in-window estimate is a usable proxy.

**Outputs** (all read by `02_predictability.py` or reported directly, never carried by hand):
- `results/test_cells.csv`: one row per scored test cell with its error, its standardised
  error z = error / stage-1 se, its horizon, and every candidate forecast-time feature;
- `results/error_structure.json`: bias, spread calibration and coverage by horizon; error
  by calendar month and by province scale; cross-province synchrony of the standardised
  errors; the share of stage-1 means below zero and what clipping them at zero would do to
  CRPS; feature-error correlations; the in-sample vs out-of-sample scale comparison;
- `results/insample_residual_acf.csv`: autocorrelation of the in-sample residuals at lags
  1-12, per province, on the final split's training window -- how much serial structure
  stage 1 leaves behind at all.

**Verification (Rule 1)**: stage 1 is re-fit here per province per split via the shared
library, and the re-derived test forecast is checked cell for cell against `02_stage1`'s
stored `per_cell_scores.csv` before any residual from the re-fit is used.

**Seeds**: this script draws no randomness.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

NODE = Path(__file__).resolve().parents[1]  # analysis/05_residualStructure
ANALYSIS = NODE.parents[0]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.crps import crps_gaussian  # noqa: E402
from lib.residual_features import (  # noqa: E402
    CLIMATE_COLS, WARMUP_MONTHS, calendar_features, climate_anomaly, fit_stage1,
    insample_residuals, mean_anomaly, monthly_climatology, pseudo_oos_errors,
    recent_residuals, residual_scale,
)

DATA_NODE = ANALYSIS / "01_data"
DEV_CSV = DATA_NODE / "01_prepare" / "results" / "development.csv"
MODELABILITY = DATA_NODE / "02_characterise" / "results" / "modelability_summary.json"
SCHEDULE_CSV = DATA_NODE / "03_backtest_scheme" / "results" / "split_schedule.csv"
STAGE1_CELLS_CSV = ANALYSIS / "02_stage1" / "results" / "per_cell_scores.csv"
RESULTS = NODE / "results"

VERIFY_ATOL = 1e-6
NOMINAL = 0.90
Z90 = 1.6448536269514722  # norm.ppf(0.95); the same interval every compare script uses
LAG12 = 12
ACF_LAGS = 12
RECENT_MONTHS = 24  # "recent" in-window origins, for the recency check on spread calibration
ZCLIP = 3.0  # winsorisation bound for the robust summaries (|z| > 3 is already outside a 99.7% interval)


def q90_factor(zvals) -> float:
    """The multiplier on sigma that would put the 90th percentile of |z| at the nominal 90%
    interval's half-width -- a quantile-based (tail-robust) calibration factor, unlike rms_z."""
    zvals = np.asarray(zvals, float)
    return float(np.quantile(np.abs(zvals), 0.90) / Z90) if len(zvals) else float("nan")


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    if len(x) < 3:
        return None, int(len(x))
    rx, ry = pd.Series(x).rank().to_numpy(), pd.Series(y).rank().to_numpy()
    if rx.std() == 0 or ry.std() == 0:
        return None, int(len(x))
    return float(np.corrcoef(rx, ry)[0, 1]), int(len(x))


def load_series(province, months, dev_rows):
    idx = pd.PeriodIndex(months, freq="M")
    values = {r["time_period"]: r["disease_cases"] for r in dev_rows if r["location"] == province}
    data = [float(values[m]) if values.get(m, "") not in ("", None) else float("nan") for m in months]
    return pd.Series(data, index=idx)


def load_climate(province, dev_rows):
    return {r["time_period"]: {c: float(r[c]) for c in CLIMATE_COLS}
            for r in dev_rows if r["location"] == province}


def load_actuals(province, dev_rows):
    return {r["time_period"]: float(r["disease_cases"])
            for r in dev_rows if r["location"] == province and r["disease_cases"] != ""}


def read_schedule():
    with SCHEDULE_CSV.open(newline="") as f:
        return [{**row, "test_months": row["test_months"].split(";")} for row in csv.DictReader(f)]


def load_stage1_cells():
    with STAGE1_CELLS_CSV.open(newline="") as f:
        return {(r["province"], r["split"], r["month"]): r for r in csv.DictReader(f)}


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    x, y = x[ok], y[ok]
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return None, int(len(x))
    return float(np.corrcoef(x, y)[0, 1]), int(len(x))


def incidence_features(series: pd.Series) -> dict[str, float]:
    """Forecast-time incidence features from the training-window series alone."""
    vals = series.to_numpy(float)
    months = np.array([p.month for p in series.index])
    clim = {m: float(np.nanmean(vals[months == m])) for m in range(1, 13)}
    last3 = vals[-3:]
    clim3 = np.array([clim[m] for m in months[-3:]])
    ok = ~np.isnan(last3)
    inc_anom3 = float(np.mean(np.log1p(np.maximum(last3[ok], 0)) - np.log1p(np.maximum(clim3[ok], 0)))) if ok.any() else float("nan")
    annual_typical = float(np.nanmean(vals[WARMUP_MONTHS:]) * 12) if len(vals) > WARMUP_MONTHS else float(np.nanmean(vals) * 12)
    cum12 = float(np.nansum(vals[-12:]))
    cum36 = float(np.nansum(vals[-36:]))
    n36 = int(np.sum(~np.isnan(vals[-36:])))
    zero24 = vals[-24:]
    zero24 = zero24[~np.isnan(zero24)]
    return {
        "inc_anom3": inc_anom3,
        "cum12_anom": float(np.log1p(cum12) - np.log1p(max(annual_typical, 0))),
        "cum36_anom": float(np.log1p(cum36 * 12 / max(n36, 1)) - np.log1p(max(annual_typical, 0))),
        "zero_frac24": float(np.mean(zero24 == 0)) if len(zero24) else float("nan"),
    }


def acf(values: np.ndarray, lags: int) -> list[float]:
    v = values[~np.isnan(values)]
    v = v - v.mean()
    denom = float(np.dot(v, v))
    out = []
    for k in range(1, lags + 1):
        out.append(float(np.dot(v[k:], v[:-k]) / denom) if denom > 0 and len(v) > k else float("nan"))
    return out


def main() -> None:
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    all_months = sorted({r["time_period"] for r in dev_rows})
    modelable = json.loads(MODELABILITY.read_text())["modelable_provinces"]
    schedule = read_schedule()
    stage1_cells = load_stage1_cells()
    climate_by_p = {p: load_climate(p, dev_rows) for p in modelable}
    actuals_by_p = {p: load_actuals(p, dev_rows) for p in modelable}

    cells: list[dict] = []
    pseudo_by_h: dict[int, list[float]] = defaultdict(list)        # z of in-window h-step errors
    pseudo_rmse_by_h: dict[int, list[float]] = defaultdict(list)   # raw errors, for scale comparison
    pseudo_recent_by_h: dict[int, list[float]] = defaultdict(list)  # z, origins in the last RECENT months
    insample_rms_all: list[float] = []
    acf_rows: list[dict] = []
    n_verified, max_dm, max_ds = 0, 0.0, 0.0
    n_fit_failures = 0

    for split in schedule:
        train_months = [m for m in all_months if m <= split["train_end"]]
        origin = pd.Period(split["train_end"], freq="M")
        n_test = len(split["test_months"])

        # Pass 1: fit every province, verify, keep residuals.
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
            scale = residual_scale(resid)
            clim = monthly_climatology(climate_by_p[p], train_months)
            pseudo = pseudo_oos_errors(fit, series, n_ahead=n_test)
            for row in pseudo:
                pseudo_by_h[row["h"]].append(row["z"])
                pseudo_rmse_by_h[row["h"]].append(row["error"])
                if row["origin"] >= len(series) - 1 - RECENT_MONTHS:
                    pseudo_recent_by_h[row["h"]].append(row["z"])
            insample_rms_all.append(scale)
            state[p] = dict(series=series, fit=fit, fc=fc, resid=resid, scale=scale,
                            clim=clim, train_mean=float(series.iloc[WARMUP_MONTHS:].mean()))
            if split["split"] == schedule[-1]["split"]:
                r = resid.iloc[WARMUP_MONTHS:].to_numpy(float)
                a = acf(r, ACF_LAGS)
                n_eff = int(np.sum(~np.isnan(r)))
                acf_rows.append({"province": p, "n": n_eff, "two_se": 2 / np.sqrt(n_eff),
                                 **{f"lag{k}": a[k - 1] for k in range(1, ACF_LAGS + 1)}})

        # National index at this origin: mean standardised recent residual across provinces.
        nat = [recent_residuals(s["resid"], origin, s["scale"])[1]
               for s in state.values() if isinstance(s, dict)]
        nat = [v for v in nat if not np.isnan(v)]
        nat_last3 = float(np.mean(nat)) if nat else float("nan")

        # Incidence-derived features the dengue literature favours (batch 10's search, logged
        # in this node's provenance): recent-incidence anomaly against the province's own
        # monthly climatology, its national mean, cumulative incidence over the trailing 12
        # and 36 months against the training window's typical value (a susceptibility proxy),
        # and the trailing-24-month zero fraction (reporting level). All from the training
        # window only.
        inc_feats = {}
        for p, s in state.items():
            if not isinstance(s, dict):
                continue
            inc_feats[p] = incidence_features(s["series"])
        nat_inc = [v["inc_anom3"] for v in inc_feats.values() if not np.isnan(v["inc_anom3"])]
        nat_inc_anom3 = float(np.mean(nat_inc)) if nat_inc else float("nan")

        # Pass 2: the test cells with their features.
        for p in modelable:
            s = state[p]
            if not isinstance(s, dict):
                continue
            r_last, r_last3 = recent_residuals(s["resid"], origin, s["scale"])
            an0 = climate_anomaly(climate_by_p[p], s["clim"], str(origin))
            an3 = mean_anomaly(climate_by_p[p], s["clim"], [str(origin - i) for i in range(3)])
            for h, (month, (_, row)) in enumerate(zip(split["test_months"], s["fc"].iterrows()), start=1):
                actual = actuals_by_p[p].get(month)
                if actual is None:
                    continue
                mu, se = float(row["mean"]), float(row["mean_se"])
                t = pd.Period(month, freq="M")
                sin_m, cos_m = calendar_features(t)
                r12 = s["resid"].get(t - LAG12)
                r12 = float(r12) / s["scale"] if r12 is not None and not pd.isna(r12) else float("nan")
                err = actual - mu
                cells.append({
                    "province": p, "split": split["split"], "month": month, "h": h,
                    "actual": actual, "mu1": mu, "se1": se, "error": err, "z": err / max(se, 1e-6),
                    "crps1": crps_gaussian(actual, mu, max(se, 1e-6)),
                    "train_mean_cases": s["train_mean"], "scale": s["scale"],
                    "level_std": mu / s["scale"], "log_train_mean": float(np.log1p(max(s["train_mean"], 0))),
                    "r_last": r_last, "r_last3": r_last3, "r_lag12": r12, "nat_last3": nat_last3,
                    "rain_anom": an0["rainfall"] if an0 else float("nan"),
                    "temp_anom": an0["mean_temperature"] if an0 else float("nan"),
                    "hum_anom": an0["mean_relative_humidity"] if an0 else float("nan"),
                    "rain_anom3": an3["rainfall"] if an3 else float("nan"),
                    "temp_anom3": an3["mean_temperature"] if an3 else float("nan"),
                    "hum_anom3": an3["mean_relative_humidity"] if an3 else float("nan"),
                    "sin_m": sin_m, "cos_m": cos_m,
                    **inc_feats[p], "nat_inc_anom3": nat_inc_anom3,
                })

    if n_verified == 0 or max_dm > VERIFY_ATOL or max_ds > VERIFY_ATOL:
        raise RuntimeError(f"re-derived stage-1 forecast disagrees with 02_stage1's stored output: "
                           f"n={n_verified}, max|dmean|={max_dm:.3e}, max|dse|={max_ds:.3e}")

    RESULTS.mkdir(exist_ok=True)
    fieldnames = list(cells[0].keys())
    with (RESULTS / "test_cells.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(cells)
    with (RESULTS / "insample_residual_acf.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(acf_rows[0].keys()))
        w.writeheader()
        w.writerows(acf_rows)

    # ---- summaries ----------------------------------------------------------------------
    df = pd.DataFrame(cells)
    z = df["z"].to_numpy()
    err = df["error"].to_numpy()
    covered = (np.abs(z) <= Z90)

    def horizon_block(sub: pd.DataFrame) -> dict:
        zz, ee, se = sub["z"].to_numpy(), sub["error"].to_numpy(), sub["se1"].to_numpy()
        return {
            "n": int(len(sub)),
            "bias_mean_error": float(ee.mean()),
            "median_error": float(np.median(ee)),
            "share_error_positive": float((ee > 0).mean()),
            "mae": float(np.abs(ee).mean()),
            "rmse": float(np.sqrt(np.mean(ee ** 2))),
            "mean_stage1_se": float(se.mean()),
            "rms_z": float(np.sqrt(np.mean(zz ** 2))),
            "rms_z_winsorised": float(np.sqrt(np.mean(np.clip(zz, -ZCLIP, ZCLIP) ** 2))),
            "median_abs_z": float(np.median(np.abs(zz))),
            "q90_abs_z": float(np.quantile(np.abs(zz), 0.90)),
            "q90_calibration_factor": q90_factor(zz),
            "mean_z": float(zz.mean()),
            "median_z": float(np.median(zz)),
            "coverage_90": float((np.abs(zz) <= Z90).mean()),
            "mean_crps_stage1": float(sub["crps1"].mean()),
        }

    def pseudo_block(pz, pe=None) -> dict:
        pz = np.asarray(pz, float)
        out = {"n": int(len(pz)), "rms_z": float(np.sqrt(np.mean(pz ** 2))),
               "median_abs_z": float(np.median(np.abs(pz))), "q90_abs_z": float(np.quantile(np.abs(pz), 0.90)),
               "q90_calibration_factor": q90_factor(pz), "coverage_90": float((np.abs(pz) <= Z90).mean())}
        if pe is not None:
            out["rmse"] = float(np.sqrt(np.mean(np.asarray(pe, float) ** 2)))
        return out

    by_h = {}
    for h in sorted(df["h"].unique()):
        sub = df[df["h"] == h]
        block = horizon_block(sub)
        block["in_window_pseudo_oos_all_origins"] = pseudo_block(pseudo_by_h[int(h)], pseudo_rmse_by_h[int(h)])
        block[f"in_window_pseudo_oos_last_{RECENT_MONTHS}_origins"] = pseudo_block(pseudo_recent_by_h[int(h)])
        by_h[f"h{int(h)}"] = block

    # Spread and sign fixes, scored on the test cells. Two kinds of factor are shown for
    # sigma: rms_z (moment-based; ruined by the tail) and the q90 factor (quantile-based).
    # Both are *oracles* here -- estimated on the cells they are scored on -- so they bound
    # what a spread correction could give; they are not achievable scores. Clipping the mean
    # at zero needs nothing estimated and is achievable as is.
    rms_by_h = {int(h): by_h[f"h{int(h)}"]["rms_z"] for h in df["h"].unique()}
    q90_by_h = {int(h): by_h[f"h{int(h)}"]["q90_calibration_factor"] for h in df["h"].unique()}

    def crps_under(mu_fn, sig_fn):
        return float(np.mean([crps_gaussian(a, mu_fn(m), max(sig_fn(s, int(h)), 1e-6))
                              for a, m, s, h in zip(df["actual"], df["mu1"], df["se1"], df["h"])]))

    def cov_under(sig_fn):
        return float(np.mean([abs(a - m) <= Z90 * sig_fn(s, int(h))
                              for a, m, s, h in zip(df["actual"], df["mu1"], df["se1"], df["h"])]))

    fixes = {
        "note": "sigma factors are oracle upper bounds (estimated on the scored cells); clipping is achievable.",
        "mean_crps_stage1": float(df["crps1"].mean()),
        "coverage_90_stage1": float((np.abs(z) <= Z90).mean()),
        "mean_crps_mean_clipped_at_zero": crps_under(lambda m: max(m, 0.0), lambda s, h: s),
        "mean_crps_sigma_x_rms_z_by_h": crps_under(lambda m: m, lambda s, h: s * rms_by_h[h]),
        "mean_crps_sigma_x_q90_factor_by_h": crps_under(lambda m: m, lambda s, h: s * q90_by_h[h]),
        "coverage_90_sigma_x_q90_factor_by_h": cov_under(lambda s, h: s * q90_by_h[h]),
        "mean_crps_clip_and_q90_factor": crps_under(lambda m: max(m, 0.0), lambda s, h: s * q90_by_h[h]),
        "rms_z_by_h": rms_by_h, "q90_factor_by_h": q90_by_h,
        "share_stage1_mean_negative": float((df["mu1"] < 0).mean()),
        "share_cells_actual_zero": float((df["actual"] == 0).mean()),
    }

    by_month = {}
    for cm, sub in df.assign(cm=df["month"].str[5:7].astype(int)).groupby("cm"):
        ee = sub["error"].to_numpy()
        by_month[int(cm)] = {"n": int(len(sub)), "mean_z": float(sub["z"].mean()),
                             "median_z": float(sub["z"].median()),
                             "mean_error": float(ee.mean()), "median_error": float(np.median(ee)),
                             "share_error_positive": float((ee > 0).mean()),
                             "mean_actual": float(sub["actual"].mean()),
                             "mean_crps_stage1": float(sub["crps1"].mean())}

    by_province = []
    total_crps = float(df["crps1"].sum())
    for p, sub in df.groupby("province"):
        zz = sub["z"].to_numpy()
        by_province.append({
            "province": p, "n": int(len(sub)), "train_mean_cases_split0": float(sub["train_mean_cases"].iloc[0]),
            "mean_actual_test": float(sub["actual"].mean()), "bias_mean_error": float(sub["error"].mean()),
            "median_error": float(sub["error"].median()),
            "rms_z": float(np.sqrt(np.mean(zz ** 2))), "median_abs_z": float(np.median(np.abs(zz))),
            "coverage_90": float((np.abs(zz) <= Z90).mean()),
            "share_stage1_mean_negative": float((sub["mu1"] < 0).mean()),
            "mean_crps_stage1": float(sub["crps1"].mean()),
            "share_of_total_crps": float(sub["crps1"].sum() / total_crps),
        })
    by_province.sort(key=lambda r: -r["share_of_total_crps"])

    # Heteroscedasticity: does |z| grow with the forecast level (relative to the province's
    # own residual scale)? A Gaussian with the right sigma would give no relation.
    r_absz_level, _ = pearson(np.abs(df["z"]), df["level_std"])
    rs_absz_level, _ = spearman(np.abs(df["z"]), df["level_std"])
    r_abserr_mu, _ = pearson(np.abs(df["error"]), df["mu1"])

    # Synchrony: z as a province x test-month matrix. Each province's row is standardised
    # first (otherwise one heavy-tailed province owns the first component); then the mean
    # off-diagonal correlation, the share of z variance explained by the test-month mean
    # (one-way R^2, on winsorised z), and the first principal component's share.
    mat = df.pivot_table(index="province", columns="month", values="z").dropna(axis=0, how="any")
    m_np = np.clip(mat.to_numpy(), -ZCLIP, ZCLIP)
    m_std = (m_np - m_np.mean(axis=1, keepdims=True)) / np.where(m_np.std(axis=1, keepdims=True) > 0,
                                                                 m_np.std(axis=1, keepdims=True), 1)
    corr = np.corrcoef(m_std)
    off = corr[~np.eye(len(corr), dtype=bool)]
    zw = np.clip(df["z"], -ZCLIP, ZCLIP)
    month_means = zw.groupby(df["month"]).transform("mean")
    r2_month = float(1 - np.sum((zw - month_means) ** 2) / np.sum((zw - zw.mean()) ** 2))
    sv = np.linalg.svd(m_std, compute_uv=False)
    pc1_share = float(sv[0] ** 2 / np.sum(sv ** 2))

    features = ["r_last", "r_last3", "r_lag12", "nat_last3", "rain_anom", "temp_anom", "hum_anom",
                "rain_anom3", "temp_anom3", "hum_anom3", "level_std", "log_train_mean", "sin_m", "cos_m", "h",
                "inc_anom3", "nat_inc_anom3", "cum12_anom", "cum36_anom", "zero_frac24"]
    feature_corr = {}
    for feat in features:
        r_all, n_all = pearson(df[feat], df["z"])
        rs_all, _ = spearman(df[feat], df["z"])
        rw_all, _ = pearson(df[feat], zw)
        per_h = {}
        for h in sorted(df["h"].unique()):
            sub = df[df["h"] == h]
            r_h, n_h = pearson(sub[feat], sub["z"])
            rs_h, _ = spearman(sub[feat], sub["z"])
            per_h[f"h{int(h)}"] = {"pearson": r_h, "spearman": rs_h, "n": n_h}
        feature_corr[feat] = {"pearson_with_z": r_all, "spearman_with_z": rs_all,
                              "pearson_with_winsorised_z": rw_all, "n": n_all, "by_horizon": per_h}

    # In-sample one-step residual scale vs the out-of-sample error scale a stage 2 corrects.
    acf_df = pd.DataFrame(acf_rows)
    acf_summary = {
        f"lag{k}": {
            "mean_acf": float(acf_df[f"lag{k}"].mean()),
            "n_provinces_beyond_2se": int((acf_df[f"lag{k}"].abs() > acf_df["two_se"]).sum()),
        } for k in range(1, ACF_LAGS + 1)
    }

    summary = {
        "n_cells": int(len(df)),
        "n_fit_failures": n_fit_failures,
        "verification_vs_stage1_stored_forecast": {"n_cells_verified": n_verified,
                                                   "max_abs_diff_mean": max_dm, "max_abs_diff_se": max_ds,
                                                   "tolerance": VERIFY_ATOL},
        "overall": {**horizon_block(df), "coverage_nominal": NOMINAL},
        "by_horizon": by_h,
        "spread_and_sign_fixes_on_test_cells": fixes,
        "by_calendar_month": by_month,
        "by_province": by_province,
        "heteroscedasticity": {
            "pearson_abs_z_vs_level_std": r_absz_level,
            "spearman_abs_z_vs_level_std": rs_absz_level,
            "pearson_abs_error_vs_mu1": r_abserr_mu,
        },
        "cross_province_synchrony_of_z": {
            "note": f"z winsorised at +/-{ZCLIP} and standardised per province before the matrix statistics",
            "n_provinces_in_matrix": int(len(mat)), "n_test_months": int(mat.shape[1]),
            "mean_pairwise_correlation": float(off.mean()),
            "share_variance_explained_by_test_month_mean": r2_month,
            "first_pc_share_of_variance": pc1_share,
        },
        "insample_vs_oos_scale": {
            "mean_insample_one_step_residual_rms": float(np.mean(insample_rms_all)),
            "oos_rmse_by_horizon": {k: v["rmse"] for k, v in by_h.items()},
            "in_window_pseudo_oos_rmse_by_horizon": {k: v["in_window_pseudo_oos_all_origins"]["rmse"]
                                                     for k, v in by_h.items()},
        },
        "insample_residual_acf_final_split": acf_summary,
        "feature_correlations_with_z": feature_corr,
    }
    (RESULTS / "error_structure.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("overall", "by_horizon", "spread_and_sign_fixes_on_test_cells",
                                              "by_calendar_month", "heteroscedasticity",
                                              "cross_province_synchrony_of_z", "insample_vs_oos_scale")}, indent=2))


if __name__ == "__main__":
    main()
