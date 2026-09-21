"""Training and test rows for a stage 2 that predicts stage 1's *h-step out-of-sample error*
from forecast-time features -- the design batch 10's diagnostics (`05_residualStructure`) and
literature search point to, shared by the `04_stage2` candidates built on it so that they
differ only in the model family fitted to identical rows.

**Horizon.** The set of horizons stage 2 is trained on is *the evaluation scheme's*: every
h from 1 to `n_ahead`, where `n_ahead` is the backtest scheme's `n_periods` (plan §4: 3
months, the Chap default this project's scheme reuses), read from the schedule by the caller
and passed in -- never fixed here. A stage 2 trained on fewer horizons than the evaluation
scores, or on one-step errors only, would be corrected for the wrong task; a caller that
passes a horizon set different from the one it forecasts is refused by `check_horizons`.

**Target.** For an origin o inside a split's training window and a horizon h in 1..n_ahead,
stage 1's forecast of month o+h made at o with parameters fixed at the window's estimates
(`residual_features.pseudo_oos_errors`), and the standardised error

    z = (actual - forecast mean) / forecast se,

winsorised at +/-ZCLIP. Standardising by stage 1's own predictive se puts every province and
horizon on one footing so they can be pooled; the prediction z-hat converts back to a
correction z-hat * se on the province's own scale, so a low-count province cannot receive a
high-count province's correction (the failure `e_pooledRandomForest` had). Winsorising keeps
the handful of reporting-regime breaks (|z| in the tens to hundreds, `05_residualStructure/
results/error_structure.json`) from owning the fit; it also bounds any correction at ZCLIP
standard errors.

**Features, all computable at the origin** (the leakage rule `a_linearLags` fixed in batch 4):
horizon and target-month indicators; stage 1's own forecast level relative to the province's
residual scale (log-compressed, plus a below-zero indicator) -- the strongest single
co-variate of the error in the diagnostics; the last and last-three in-sample residuals at
the origin, standardised; their cross-province mean at the same origin; the trailing-12-month
incidence against the window's typical year (a susceptibility proxy) and the trailing-24-month
zero fraction (reporting level). Climate anomalies are deliberately not included: the
diagnostics found no usable correlation at lags 1-3 and the dengue-forecasting literature
finds climate adds little beyond incidence at these horizons; that exclusion is a logged
fork, not an oversight.

Nothing here reads a test month. `05_residualStructure` computes the same kinds of quantity
on the *test* cells for diagnosis; this module computes them inside the training window for
fitting, and for the test cells only from data at or before the origin.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from lib.residual_features import WARMUP_MONTHS, pseudo_oos_errors, recent_residuals

ZCLIP = 3.0


def horizons(n_ahead: int) -> tuple[int, ...]:
    """Every horizon the evaluation scores, 1..n_ahead."""
    if n_ahead < 1:
        raise ValueError(f"n_ahead must be >= 1, got {n_ahead}")
    return tuple(range(1, n_ahead + 1))


def features(n_ahead: int) -> list[str]:
    """The design-matrix columns, in order, for a given evaluation horizon."""
    return (
        [f"h{h}" for h in horizons(n_ahead)]
        + [f"m{k}" for k in range(1, 13)]
        + ["level_log", "pred_negative", "level_log_x_h", "log_train_mean",
           "r_last", "r_last3", "nat_last3", "cum12_anom", "zero_frac24"]
    )


def check_horizons(schedule: list[dict], schedule_summary: dict) -> int:
    """The one horizon set this run may use: the schedule's test-window length, which must be
    the same for every split and equal to the scheme's recorded `n_periods`. Returns it."""
    lengths = {len(s["test_months"]) for s in schedule}
    if len(lengths) != 1:
        raise RuntimeError(f"splits have unequal test windows {sorted(lengths)}; one horizon set is required")
    n_ahead = lengths.pop()
    if n_ahead != int(schedule_summary["n_periods"]):
        raise RuntimeError(f"schedule test window {n_ahead} != scheme n_periods {schedule_summary['n_periods']}")
    return n_ahead


def wins(x: float, bound: float = ZCLIP) -> float:
    if x is None or np.isnan(x):
        return 0.0  # a feature missing at forecast time carries no information
    return float(min(max(x, -bound), bound))


def incidence_state(series: pd.Series, upto: int) -> tuple[float, float]:
    """(cum12_anom, zero_frac24) from the series up to and including position `upto`."""
    vals = series.to_numpy(float)[: upto + 1]
    base = vals[WARMUP_MONTHS:] if len(vals) > WARMUP_MONTHS + 12 else vals
    annual_typical = float(np.nanmean(base) * 12) if np.isfinite(np.nanmean(base)) else 0.0
    cum12 = float(np.nansum(vals[-12:]))
    z24 = vals[-24:]
    z24 = z24[~np.isnan(z24)]
    zero_frac = float(np.mean(z24 == 0)) if len(z24) else 0.0
    return float(np.log1p(cum12) - np.log1p(max(annual_typical, 0.0))), zero_frac


def _row(h: int, n_ahead: int, target: pd.Period, mu: float, scale: float, log_train_mean: float,
         r_last: float, r_last3: float, nat_last3: float, cum12_anom: float, zero_frac24: float) -> dict:
    level_log = float(np.log1p(max(mu, 0.0) / scale))
    row = {f"h{k}": float(k == h) for k in horizons(n_ahead)}
    row.update({f"m{k}": float(target.month == k) for k in range(1, 13)})
    row.update({
        "level_log": level_log, "pred_negative": float(mu < 0), "level_log_x_h": level_log * h,
        "log_train_mean": log_train_mean,
        "r_last": wins(r_last), "r_last3": wins(r_last3), "nat_last3": wins(nat_last3),
        "cum12_anom": cum12_anom, "zero_frac24": zero_frac24,
    })
    return row


def national_index(resids: dict[str, pd.Series], scales: dict[str, float], months: pd.PeriodIndex) -> dict[pd.Period, float]:
    """Mean across provinces of the winsorised, standardised last-three-month residual at
    every month -- the cross-province signal, known at that month."""
    out = {}
    for m in months:
        vals = []
        for p, r in resids.items():
            _, r3 = recent_residuals(r, m, scales[p])
            if not np.isnan(r3):
                vals.append(wins(r3))
        out[m] = float(np.mean(vals)) if vals else 0.0
    return out


def training_rows(province: str, fit, series: pd.Series, resid: pd.Series, scale: float,
                  log_train_mean: float, nat: dict[pd.Period, float], n_ahead: int) -> list[dict]:
    """One row per (origin, h) for h = 1..n_ahead -- the full evaluation horizon."""
    rows = []
    for e in pseudo_oos_errors(fit, series, n_ahead=n_ahead):
        origin = series.index[e["origin"]]
        r_last, r_last3 = recent_residuals(resid, origin, scale)
        cum12_anom, zero_frac24 = incidence_state(series, e["origin"])
        row = _row(e["h"], n_ahead, series.index[e["target"]], e["pred_mean"], scale, log_train_mean,
                   r_last, r_last3, nat.get(origin, 0.0), cum12_anom, zero_frac24)
        row.update({"province": province, "origin": str(origin), "target": e["target_month"],
                    "z": wins(e["z"]), "z_raw": e["z"]})
        rows.append(row)
    return rows


def test_rows(province: str, fc: pd.DataFrame, test_months: list[str], series: pd.Series,
              resid: pd.Series, scale: float, log_train_mean: float, nat: dict[pd.Period, float],
              n_ahead: int) -> list[dict]:
    """One row per test month, at its horizon 1..n_ahead; refuses a forecast frame or test
    window whose length is not the horizon set the model was trained on."""
    if len(test_months) != n_ahead or len(fc) != n_ahead:
        raise RuntimeError(f"{province}: test window {len(test_months)} / forecast rows {len(fc)} "
                           f"!= trained horizon set {n_ahead}")
    origin = series.index[-1]
    r_last, r_last3 = recent_residuals(resid, origin, scale)
    cum12_anom, zero_frac24 = incidence_state(series, len(series) - 1)
    rows = []
    for h, (month, (_, r)) in enumerate(zip(test_months, fc.iterrows()), start=1):
        row = _row(h, n_ahead, pd.Period(month, freq="M"), float(r["mean"]), scale, log_train_mean,
                   r_last, r_last3, nat.get(origin, 0.0), cum12_anom, zero_frac24)
        row.update({"province": province, "month": month, "h": h,
                    "mu1": float(r["mean"]), "se1": float(r["mean_se"])})
        rows.append(row)
    return rows


def design_matrix(rows: list[dict], n_ahead: int) -> np.ndarray:
    return np.array([[row[f] for f in features(n_ahead)] for row in rows], dtype=float)
