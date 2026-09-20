"""Stage 1's SARIMAX fit, factored out so stage 2 can obtain its in-sample residuals.

`analysis/02_stage1`'s own script and results are that batch's closed record (AGENTS.md
Sec.1: never edit a file you produced), so this module re-derives the identical spec --
SARIMAX(1,1,1)x(1,0,0,12) on raw `disease_cases`, refit per province per split -- rather than
importing anything from 02_stage1. A stage-2 candidate that uses this module must first
verify it reproduces 02_stage1's own stored per-cell forecast (mean, se) before trusting the
in-sample residuals this module additionally exposes; that check belongs in the candidate's
own provenance, not here. Matches plan Sec.4's requirement that model code be written once and
used identically for every candidate.
"""
from __future__ import annotations

import warnings

import pandas as pd
import statsmodels.api as sm

ORDER = (1, 1, 1)
SEASONAL_ORDER = (1, 0, 0, 12)


def fit_and_forecast(series: pd.Series, n_test: int):
    """Fit the stage-1 spec on `series` and forecast `n_test` steps ahead.

    Returns (forecast_summary_frame, insample_residuals): `insample_residuals` is observed
    minus statsmodels' one-step-ahead fitted value on the training window (plan Sec.1's
    residual series), indexed the same as `series`, with NaN wherever `series` or the fitted
    value is unavailable (missing observations, diffuse-initialization warm-up). Raises on
    fit failure -- the caller records it, matching 02_stage1's own contract.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = sm.tsa.statespace.SARIMAX(
            series, order=ORDER, seasonal_order=SEASONAL_ORDER,
            enforce_stationarity=False, enforce_invertibility=False,
        )
        fit = model.fit(disp=False)
        forecast = fit.get_forecast(steps=n_test)
    insample_residuals = series - fit.fittedvalues
    return forecast.summary_frame(), insample_residuals
