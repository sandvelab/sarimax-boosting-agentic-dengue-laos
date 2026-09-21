"""The perturbable two-stage pipeline for the stability node (batch 12).

`06_stability/results/manifest.csv` names 29 tier-2 perturbations of judgment calls that live
as constants or code paths in `02_stage1`, `01_data` and the main-path stage 2
(`04_stage2/g_oosErrorBoosting`). Those nodes' scripts are closed records that fix their
constants and refuse a stage-1 forecast different from `02_stage1`'s stored one, so they
cannot run a perturbation of stage 1. This module is the same pipeline with every one of
those choices exposed as a parameter: stage 1's specification and training window, the
backtest scheme and modelability threshold, and the stage-2 target, features, family,
standardisation, bounds, combination rule, warm-up, in-window error construction and seed.

**The gate that makes it trustworthy**: with every parameter at its main-path value
(`Stage1Config()`, `SchemeConfig()`, `Stage2Config()`), `run_combination` must reproduce
`04_stage2/g_oosErrorBoosting/results/per_cell_scores.csv` value for value, and the runner
script checks that before any other combination is run. Wherever this module builds the same
quantity as `lib.stage2_oos` or `lib.residual_features`, it calls those functions rather than
re-deriving them, so the two cannot drift apart silently; `_row` is re-implemented here only
because the feature set itself is one of the perturbed choices, and its "full" set is
`stage2_oos.features(n_ahead)` in the same order.

Nothing here reads the holdout file.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field, asdict
from typing import Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from lib.backtest import rolling_splits
from lib.crps import crps_gaussian
from lib.project_seed import component_seed
from lib.residual_features import (
    CLIMATE_COLS, climate_anomaly, mean_anomaly, monthly_climatology, recent_residuals,
)
from lib.stage2_oos import ZCLIP as MAIN_ZCLIP, incidence_state, national_index, wins

Z90 = 1.6448536269514722


@dataclass
class Stage1Config:
    order: tuple = (1, 1, 1)
    seasonal_order: tuple = (1, 0, 0, 12)
    enforce: bool = False                       # enforce_stationarity and enforce_invertibility
    window: Literal["expanding", "rolling", "start"] = "expanding"
    window_months: int = 72                     # for "rolling"
    window_start: str = "2002-01"               # for "start"


@dataclass
class SchemeConfig:
    n_periods: int = 3
    n_splits: int = 8
    stride: int = 3
    min_modelable_months: int = 24


@dataclass
class Stage2Config:
    family: Literal["gbm", "ridge"] = "gbm"
    gbm_params: dict = field(default_factory=lambda: dict(
        n_estimators=150, max_depth=3, learning_rate=0.05, subsample=0.8, min_samples_leaf=20))
    ridge_alpha: float = 10.0
    seed_component: str = "04_stage2/g_oosErrorBoosting"
    zclip: float | None = MAIN_ZCLIP            # None = no winsorisation
    clip_at_zero: bool = True
    standardise: Literal["se", "resid_rms"] = "se"
    bounded_correction: bool = False            # |correction| <= max(stage-1 mean, BOUND_FLOOR)
    bound_floor: float = 10.0
    per_horizon: bool = False
    features: Literal["full", "no_cross_province", "no_incidence", "level_only", "with_climate"] = "full"
    warmup: int = 24
    oos_mode: Literal["fixed", "rolling_refit"] = "fixed"
    min_train_rows: int = 200


def configs_as_dict(s1: Stage1Config, sc: SchemeConfig, s2: Stage2Config) -> dict:
    return {"stage1": asdict(s1), "scheme": asdict(sc), "stage2": asdict(s2)}


# ---- data -------------------------------------------------------------------------------------

def modelable_provinces(dev_rows: list[dict], min_months: int) -> list[str]:
    present: dict[str, int] = {}
    for r in dev_rows:
        present.setdefault(r["location"], 0)
        if r["disease_cases"] != "":
            present[r["location"]] += 1
    return sorted(p for p, n in present.items() if n >= min_months)


def load_series(province: str, months: list[str], dev_rows: list[dict]) -> pd.Series:
    values = {r["time_period"]: r["disease_cases"] for r in dev_rows if r["location"] == province}
    data = [float(values[m]) if values.get(m, "") not in ("", None) else float("nan") for m in months]
    return pd.Series(data, index=pd.PeriodIndex(months, freq="M"))


def load_actuals(province: str, dev_rows: list[dict]) -> dict[str, float]:
    return {r["time_period"]: float(r["disease_cases"])
            for r in dev_rows if r["location"] == province and r["disease_cases"] != ""}


def load_climate(province: str, dev_rows: list[dict]) -> dict[str, dict[str, float]]:
    return {r["time_period"]: {c: float(r[c]) for c in CLIMATE_COLS} for r in dev_rows if r["location"] == province}


def training_months(all_months: list[str], train_end: str, s1: Stage1Config) -> list[str]:
    months = [m for m in all_months if m <= train_end]
    if s1.window == "rolling":
        return months[-s1.window_months:]
    if s1.window == "start":
        return [m for m in months if m >= s1.window_start]
    return months


# ---- stage 1 ----------------------------------------------------------------------------------

def fit_stage1(series: pd.Series, s1: Stage1Config):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = sm.tsa.statespace.SARIMAX(
            series, order=s1.order, seasonal_order=s1.seasonal_order,
            enforce_stationarity=s1.enforce, enforce_invertibility=s1.enforce,
        )
        return model.fit(disp=False)


def residual_scale(resid: pd.Series, warmup: int) -> float:
    r = resid.iloc[warmup:].dropna()
    if len(r) < 12:
        r = resid.dropna()
    rms = float(np.sqrt(np.mean(np.square(r.to_numpy())))) if len(r) else float("nan")
    return rms if rms > 0 else float("nan")


def in_window_errors(fit, series: pd.Series, s1: Stage1Config, s2: Stage2Config, n_ahead: int) -> list[dict]:
    """h-step errors from every origin after the warm-up: parameters fixed (the main path) or
    a fresh SARIMAX fit on the series up to the origin (`rolling_refit`)."""
    n = len(series)
    out = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for o in range(s2.warmup, n - 1):
            end = min(o + n_ahead, n - 1)
            if s2.oos_mode == "fixed":
                pr = fit.get_prediction(start=o + 1, end=end, dynamic=True).summary_frame()
            else:
                try:
                    sub = fit_stage1(series.iloc[: o + 1], s1)
                except Exception:  # noqa: BLE001 -- an origin whose refit fails contributes no rows
                    continue
                pr = sub.get_forecast(steps=end - o).summary_frame()
            for h, (_, row) in enumerate(pr.iterrows(), start=1):
                target = o + h
                y = series.iloc[target]
                if pd.isna(y):
                    continue
                mu, se = float(row["mean"]), float(row["mean_se"])
                if not (np.isfinite(mu) and np.isfinite(se)):
                    continue  # a refit that diverged at this origin contributes no row; counted by the caller
                out.append({"origin": o, "target": target, "h": h, "actual": float(y),
                            "pred_mean": mu, "pred_se": se, "error": float(y) - mu})
    return out


def finite_row(row: dict, names: list[str]) -> bool:
    return all(np.isfinite(row[f]) for f in names) and np.isfinite(row.get("z", 0.0))


def zero_nonfinite(row: dict, names: list[str]) -> dict:
    """A test-time feature that is not finite carries no information: set it to 0."""
    for f in names:
        if not np.isfinite(row[f]):
            row[f] = 0.0
    return row


# ---- stage 2 rows -----------------------------------------------------------------------------

def feature_names(n_ahead: int, s2: Stage2Config) -> list[str]:
    hs = [f"h{h}" for h in range(1, n_ahead + 1)] if not s2.per_horizon else []
    months = [f"m{k}" for k in range(1, 13)]
    level = ["level_log", "pred_negative", "level_log_x_h", "log_train_mean"]
    recent = ["r_last", "r_last3"]
    cross = ["nat_last3"]
    inc = ["cum12_anom", "zero_frac24"]
    clim = ["rain_anom", "temp_anom", "hum_anom", "rain_anom3", "temp_anom3", "hum_anom3"]
    if s2.features == "full":
        return hs + months + level + recent + cross + inc
    if s2.features == "no_cross_province":
        return hs + months + level + recent + inc
    if s2.features == "no_incidence":
        return hs + months + level + recent + cross
    if s2.features == "level_only":
        return hs + months + ["level_log", "level_log_x_h"]
    if s2.features == "with_climate":
        return hs + months + level + recent + cross + inc + clim
    raise ValueError(s2.features)


def make_row(h: int, n_ahead: int, target: pd.Period, mu: float, scale: float, log_train_mean: float,
             r_last: float, r_last3: float, nat_last3: float, cum12_anom: float, zero_frac24: float,
             clim0: dict | None, clim3: dict | None, zclip: float | None) -> dict:
    level_log = float(np.log1p(max(mu, 0.0) / scale))
    w = (lambda x: wins(x, zclip)) if zclip is not None else (lambda x: 0.0 if x is None or np.isnan(x) else float(x))
    row = {f"h{k}": float(k == h) for k in range(1, n_ahead + 1)}
    row.update({f"m{k}": float(target.month == k) for k in range(1, 13)})
    row.update({"level_log": level_log, "pred_negative": float(mu < 0), "level_log_x_h": level_log * h,
                "log_train_mean": log_train_mean, "r_last": w(r_last), "r_last3": w(r_last3),
                "nat_last3": w(nat_last3), "cum12_anom": cum12_anom, "zero_frac24": zero_frac24})
    row.update({"rain_anom": clim0["rainfall"] if clim0 else 0.0,
                "temp_anom": clim0["mean_temperature"] if clim0 else 0.0,
                "hum_anom": clim0["mean_relative_humidity"] if clim0 else 0.0,
                "rain_anom3": clim3["rainfall"] if clim3 else 0.0,
                "temp_anom3": clim3["mean_temperature"] if clim3 else 0.0,
                "hum_anom3": clim3["mean_relative_humidity"] if clim3 else 0.0})
    return row


def target_value(e: dict, scale_denominator: float, s2: Stage2Config) -> float:
    z = e["error"] / max(scale_denominator, 1e-6)
    return wins(z, s2.zclip) if s2.zclip is not None else float(z)


def make_model(s2: Stage2Config):
    if s2.family == "ridge":
        return make_pipeline(StandardScaler(), Ridge(alpha=s2.ridge_alpha))
    return GradientBoostingRegressor(**s2.gbm_params, random_state=component_seed(s2.seed_component))


def matrix(rows: list[dict], names: list[str]) -> np.ndarray:
    return np.array([[r[f] for f in names] for r in rows], dtype=float)


# ---- the whole pipeline for one combination -----------------------------------------------------

def run_combination(dev_rows: list[dict], s1: Stage1Config, sc: SchemeConfig, s2: Stage2Config) -> tuple[list[dict], dict]:
    all_months = sorted({r["time_period"] for r in dev_rows})
    provinces = modelable_provinces(dev_rows, sc.min_modelable_months)
    splits = rolling_splits(all_months, sc.n_periods, sc.n_splits, sc.stride)
    n_ahead = sc.n_periods
    names = feature_names(n_ahead, s2)
    actuals = {p: load_actuals(p, dev_rows) for p in provinces}
    climates = {p: load_climate(p, dev_rows) for p in provinces} if s2.features == "with_climate" else {}
    zclip_pred = s2.zclip if s2.zclip is not None else np.inf

    per_cell: list[dict] = []
    n_fit_failures = n_abstained = n_rows_dropped_nonfinite = 0
    n_train_rows = {}

    for split in splits:
        months = training_months(all_months, split["train_months"][-1], s1)
        origin = pd.Period(months[-1], freq="M")
        state = {}
        for p in provinces:
            series = load_series(p, months, dev_rows)
            try:
                fit = fit_stage1(series, s1)
                fc = fit.get_forecast(steps=n_ahead).summary_frame()
            except Exception as exc:  # noqa: BLE001 -- a recorded outcome
                n_fit_failures += 1
                state[p] = exc
                continue
            resid = series - fit.fittedvalues
            scale = residual_scale(resid, s2.warmup)
            clim = monthly_climatology(climates[p], months) if climates else None
            state[p] = dict(series=series, fit=fit, fc=fc, resid=resid, scale=scale, clim=clim,
                            log_train_mean=float(np.log1p(max(series.iloc[s2.warmup:].mean(), 0))))
        ok = {p: s for p, s in state.items() if isinstance(s, dict) and np.isfinite(s["scale"])}
        nat = national_index({p: s["resid"] for p, s in ok.items()}, {p: s["scale"] for p, s in ok.items()},
                             pd.PeriodIndex(months, freq="M"))

        rows = []
        for p, s in ok.items():
            series, resid = s["series"], s["resid"]
            for e in in_window_errors(s["fit"], series, s1, s2, n_ahead):
                o = series.index[e["origin"]]
                r_last, r_last3 = recent_residuals(resid, o, s["scale"])
                cum12, zf = incidence_state(series, e["origin"])
                c0 = climate_anomaly(climates[p], s["clim"], str(o)) if climates else None
                c3 = mean_anomaly(climates[p], s["clim"], [str(o - i) for i in range(3)]) if climates else None
                row = make_row(e["h"], n_ahead, series.index[e["target"]], e["pred_mean"], s["scale"],
                               s["log_train_mean"], r_last, r_last3, nat.get(o, 0.0), cum12, zf, c0, c3, s2.zclip)
                denom = e["pred_se"] if s2.standardise == "se" else s["scale"]
                row["z"] = target_value(e, denom, s2)
                row["h"] = e["h"]
                if finite_row(row, names):
                    rows.append(row)
                else:
                    n_rows_dropped_nonfinite += 1
        n_train_rows[split["split"]] = len(rows)

        models: dict = {}
        if len(rows) >= s2.min_train_rows:
            if s2.per_horizon:
                for h in range(1, n_ahead + 1):
                    sub = [r for r in rows if r["h"] == h]
                    m = make_model(s2)
                    m.fit(matrix(sub, names), np.array([r["z"] for r in sub]))
                    models[h] = m
            else:
                m = make_model(s2)
                m.fit(matrix(rows, names), np.array([r["z"] for r in rows]))
                models["pooled"] = m

        for p in provinces:
            s = state[p]
            if not isinstance(s, dict):
                for month in split["test_months"]:
                    per_cell.append({"province": p, "split": split["split"], "month": month, "h": None,
                                     "actual": actuals[p].get(month), "stage1_mean": None, "stage1_se": None,
                                     "stage2_correction": None, "final_mean": None, "final_se": None,
                                     "crps_stage1": None, "crps": None, "fit_failed": True, "error": str(s)[:200]})
                continue
            series, resid = s["series"], s["resid"]
            can_correct = models and p in ok
            if can_correct:
                r_last, r_last3 = recent_residuals(resid, origin, s["scale"])
                cum12, zf = incidence_state(series, len(series) - 1)
                c0 = climate_anomaly(climates[p], s["clim"], str(origin)) if climates else None
                c3 = mean_anomaly(climates[p], s["clim"], [str(origin - i) for i in range(3)]) if climates else None
                trows = [zero_nonfinite(make_row(h, n_ahead, pd.Period(month, freq="M"), float(r["mean"]), s["scale"],
                                                 s["log_train_mean"], r_last, r_last3, nat.get(origin, 0.0), cum12, zf, c0, c3,
                                                 s2.zclip), names)
                         for h, (month, (_, r)) in enumerate(zip(split["test_months"], s["fc"].iterrows()), start=1)]
                if s2.per_horizon:
                    zhat = np.array([float(np.clip(models[h].predict(matrix([trows[h - 1]], names))[0], -zclip_pred, zclip_pred))
                                     for h in range(1, n_ahead + 1)])
                else:
                    zhat = np.clip(models["pooled"].predict(matrix(trows, names)), -zclip_pred, zclip_pred)
            for h, (month, (_, r)) in enumerate(zip(split["test_months"], s["fc"].iterrows()), start=1):
                mu1, se1 = float(r["mean"]), float(r["mean_se"])
                if not can_correct:
                    corr = 0.0
                    n_abstained += 1
                else:
                    zh = float(zhat[h - 1])
                    corr = zh * (se1 if s2.standardise == "se" else s["scale"])
                    if s2.bounded_correction:
                        bound = max(mu1, s2.bound_floor)
                        corr = float(min(max(corr, -bound), bound))
                unclipped = mu1 + corr
                final_mean = max(unclipped, 0.0) if s2.clip_at_zero else unclipped
                actual = actuals[p].get(month)
                crps1 = crps_gaussian(actual, mu1, max(se1, 1e-6)) if actual is not None else None
                crps = crps_gaussian(actual, final_mean, max(se1, 1e-6)) if actual is not None else None
                per_cell.append({"province": p, "split": split["split"], "month": month, "h": h,
                                 "actual": actual, "stage1_mean": mu1, "stage1_se": se1,
                                 "stage2_correction": corr, "final_mean": final_mean, "final_se": se1,
                                 "crps_stage1": crps1, "crps": crps, "fit_failed": False, "error": None})

    scored = [c for c in per_cell if c["crps"] is not None]
    c1 = float(np.mean([c["crps_stage1"] for c in scored]))
    c2 = float(np.mean([c["crps"] for c in scored]))
    cov1 = float(np.mean([abs(c["actual"] - c["stage1_mean"]) <= Z90 * c["stage1_se"] for c in scored]))
    cov2 = float(np.mean([abs(c["actual"] - c["final_mean"]) <= Z90 * c["final_se"] for c in scored]))
    by_h = {}
    for h in range(1, n_ahead + 1):
        sub = [c for c in scored if c["h"] == h]
        if sub:
            by_h[f"h{h}"] = {"stage1": float(np.mean([c["crps_stage1"] for c in sub])),
                             "two_stage": float(np.mean([c["crps"] for c in sub]))}
    by_split = {}
    for sp in sorted({c["split"] for c in scored}):
        sub = [c for c in scored if c["split"] == sp]
        by_split[f"split{sp}"] = {"stage1": float(np.mean([c["crps_stage1"] for c in sub])),
                                  "two_stage": float(np.mean([c["crps"] for c in sub]))}
    conclusion = {
        "config": configs_as_dict(s1, sc, s2),
        "n_provinces": len(provinces), "n_splits": len(splits), "horizon_months": n_ahead,
        "n_cells_scored": len(scored), "n_fit_failures": n_fit_failures, "n_stage2_abstained": n_abstained,
        "n_training_rows_by_split": n_train_rows, "n_training_rows_dropped_nonfinite": n_rows_dropped_nonfinite,
        "stage1_alone": {"mean_crps": c1, "coverage_90": cov1},
        "two_stage": {"mean_crps": c2, "coverage_90": cov2},
        "delta_crps": c2 - c1, "pct_change_vs_stage1": 100 * (c2 - c1) / c1,
        "two_stage_beats_stage1_on_crps": bool(c2 < c1),
        "coverage_not_worse_than_stage1": bool(cov2 >= cov1 - 1e-12),
        "n_splits_improved": sum(1 for v in by_split.values() if v["two_stage"] < v["stage1"]),
        "share_cells_improved": float(np.mean([c["crps"] < c["crps_stage1"] for c in scored])),
        "by_horizon": by_h, "by_split": by_split,
    }
    return per_cell, conclusion
