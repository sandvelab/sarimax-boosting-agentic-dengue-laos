"""Stage 1's fit object, its multi-step *forecast errors inside the training window*, and the
forecast-time features a stage 2 may use -- shared by `05_residualStructure` and by the
stage-2 candidates built on its findings (batch 10).

Why this module exists beside `stage1_model.py` rather than inside it: every stage-2
candidate before batch 10 trained on stage 1's **in-sample one-step-ahead residuals**
(`series - fittedvalues`), which `stage1_model.fit_and_forecast` exposes. But the quantity a
stage 2 has to correct at test time is stage 1's **h-step-ahead out-of-sample forecast
error** (h = 1, 2, 3 in this project's backtest scheme), which differs from the one-step
in-sample residual in scale (it grows with h), in structure (it accumulates model error over
h steps) and in what predicts it. Training on one target to correct another is a mismatch
this module removes. `stage1_model.py` is left untouched because earlier nodes' provenance
records hash it (AGENTS.md §1: never edit a file you produced); this module imports its
specification constants so the two cannot drift apart.

`pseudo_oos_errors` produces, for one fitted stage-1 model, the h-step-ahead forecast made
from every origin inside the training window with the parameters *fixed* at their full-window
estimates (`get_prediction(..., dynamic=True)`, verified equal to `apply(refit=False)` on
the truncated series -- see `05_residualStructure`'s provenance). These are "pseudo" out-of-
sample: the parameters saw the whole training window, so the errors are mildly optimistic
relative to a true rolling refit, but they never see a test month and cost milliseconds
each rather than a refit. A true rolling refit inside every training window is the
alternative considered and rejected on cost (17 provinces x 8 splits x ~100 origins of
SARIMAX fits per candidate), logged here rather than silently.

All features returned by the helpers below are computable from data at or before the
forecast origin, for every one of the 3 test months -- the leakage rule `a_linearLags`
established in batch 4, applied uniformly.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

from lib.stage1_model import ORDER, SEASONAL_ORDER

CLIMATE_COLS = ["rainfall", "mean_temperature", "mean_relative_humidity"]
WARMUP_MONTHS = 24  # diffuse-initialisation warm-up excluded from residual-scale estimates


def fit_stage1(series: pd.Series):
    """Stage 1's exact specification, returning the statsmodels results object.

    Identical model and options to `stage1_model.fit_and_forecast`; a caller that needs
    the forecast for verification calls `.get_forecast(n).summary_frame()` on the result.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = sm.tsa.statespace.SARIMAX(
            series, order=ORDER, seasonal_order=SEASONAL_ORDER,
            enforce_stationarity=False, enforce_invertibility=False,
        )
        return model.fit(disp=False)


def insample_residuals(fit, series: pd.Series) -> pd.Series:
    """Observed minus one-step-ahead fitted value, as `stage1_model` defines it."""
    return series - fit.fittedvalues


def residual_scale(resid: pd.Series) -> float:
    """Root-mean-square of the in-sample residuals after the warm-up -- the province's own
    residual scale, used to standardise features so provinces can be pooled."""
    r = resid.iloc[WARMUP_MONTHS:].dropna()
    if len(r) < 12:
        r = resid.dropna()
    rms = float(np.sqrt(np.mean(np.square(r.to_numpy())))) if len(r) else float("nan")
    return rms if rms > 0 else float("nan")


def pseudo_oos_errors(fit, series: pd.Series, n_ahead: int = 3,
                      min_origin: int = WARMUP_MONTHS) -> list[dict]:
    """h-step-ahead forecasts from every origin inside the training window, parameters fixed.

    One row per (origin, h) with the target month actually observed. `origin` is the
    integer position of the last month used; the target is `origin + h`.
    """
    n = len(series)
    out: list[dict] = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for o in range(min_origin, n - 1):
            end = min(o + n_ahead, n - 1)
            pr = fit.get_prediction(start=o + 1, end=end, dynamic=True).summary_frame()
            for h, (_, row) in enumerate(pr.iterrows(), start=1):
                target = o + h
                y = series.iloc[target]
                if pd.isna(y):
                    continue
                mu, se = float(row["mean"]), float(row["mean_se"])
                out.append({
                    "origin": o, "target": target, "h": h,
                    "target_month": str(series.index[target]),
                    "actual": float(y), "pred_mean": mu, "pred_se": se,
                    "error": float(y) - mu, "z": (float(y) - mu) / max(se, 1e-6),
                })
    return out


def monthly_climatology(climate: dict[str, dict[str, float]], months: list[str]) -> dict[int, dict[str, float]]:
    """Per calendar month, the mean of each climate column over `months` (the training
    window) -- so an anomaly is relative to what the training data say is normal."""
    acc: dict[int, dict[str, list[float]]] = {}
    for m in months:
        row = climate.get(m)
        if row is None:
            continue
        cm = pd.Period(m, freq="M").month
        bucket = acc.setdefault(cm, {c: [] for c in CLIMATE_COLS})
        for c in CLIMATE_COLS:
            bucket[c].append(row[c])
    return {cm: {c: float(np.mean(v[c])) if v[c] else float("nan") for c in CLIMATE_COLS}
            for cm, v in acc.items()}


def climate_anomaly(climate: dict[str, dict[str, float]], climatology: dict[int, dict[str, float]],
                    month: str) -> dict[str, float] | None:
    row = climate.get(month)
    if row is None:
        return None
    cm = pd.Period(month, freq="M").month
    clim = climatology.get(cm)
    if clim is None:
        return None
    return {c: row[c] - clim[c] for c in CLIMATE_COLS}


def mean_anomaly(climate, climatology, months: list[str]) -> dict[str, float] | None:
    anoms = [a for a in (climate_anomaly(climate, climatology, m) for m in months) if a is not None]
    if not anoms:
        return None
    return {c: float(np.mean([a[c] for a in anoms])) for c in CLIMATE_COLS}


def calendar_features(period: pd.Period) -> tuple[float, float]:
    angle = 2 * np.pi * period.month / 12
    return float(np.sin(angle)), float(np.cos(angle))


def recent_residuals(resid: pd.Series, origin: pd.Period, scale: float, k: int = 3) -> tuple[float, float]:
    """(last residual, mean of the last k residuals) at the origin, standardised by `scale`;
    NaN where unavailable. Both are known at forecast time for every test month."""
    last = resid.get(origin)
    window = [resid.get(origin - i) for i in range(k)]
    window = [w for w in window if w is not None and not pd.isna(w)]
    r_last = float(last) / scale if last is not None and not pd.isna(last) else float("nan")
    r_mean = float(np.mean(window)) / scale if window else float("nan")
    return r_last, r_mean
