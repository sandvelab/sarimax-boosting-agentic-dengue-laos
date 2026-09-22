"""Phase E's evaluation design: how the sealed 2010 file is scored, fixed before it opens.

**Nothing here reads the holdout file.** This module is the design and the machinery; the
rows it will be run over are frozen by `06_stability/scripts/07_plan_holdout_manifest.py`, and
the one script that opens 2010 is phase E's own (ledger row 17), which passes the holdout rows
in as an argument. Batch 16 builds and verifies all of this *before* the freeze, so that no
code is written or corrected in response to a number from the held-out year -- which is what
plan §3's "opened once, across a manifest frozen beforehand" costs if the runner is built after
the file is open.

**The evaluation design, and the alternative rejected.** The holdout is twelve months, so the
project's fixed scheme (`n_periods=3`, `stride=3`, expanding window ending at the file's last
period -- `lib.backtest`) resolves over the combined 1998-01..2010-12 span to `n_splits=4`:
four successive three-month blocks covering 2010-01..2010-12 exactly once, trained on
everything up to the block's own origin. Each of the last three blocks therefore trains on the
holdout months that have already been forecast, which is what a forecaster operating through
2010 would have had, and it keeps the horizon set h = 1..3 that stage 2 is trained on
(plan §4b, 2026-09-21). The alternative -- one origin at 2009-12 forecasting h = 1..12 -- was
rejected: it scores the year at horizons no model here was built or evaluated for, and the
project's own horizon coupling is to `n_periods`, not to the length of the held-out file.

**The province set is development's, not the holdout's.** `development_provinces` derives the
modelable set from the development months alone, and the rows handed to the pipeline are
restricted to it before anything is fitted. A set re-derived from the combined file could
change when 2010 opened -- LA-VI is excluded on development data and carries 2010 rows -- and
a cell set that moves when the year opens is a set chosen after the fact.

**What the two-stage pipeline is.** `two_stage` is `lib.stage2_perturb.run_combination`, the
same function the development stability runner is gated on, with the rows restricted and the
scheme supplied. No pipeline code is duplicated and none is parameterised further, so the
holdout cannot drift from what development measured.

**What the baselines are.** The two required baselines (plan §2, §4) were implemented in
`03_baselines` against the development file and the stored split schedule; those scripts are
closed records and cannot take another file. `persistence` and `climatology` below are the same
two forecasts with the file and the scheme as arguments. They are a second implementation, and
the only thing that makes them trustworthy is that they reproduce `03_baselines`' stored
per-cell scores value for value on development data -- which
`06_stability/scripts/06_verify_holdout_runner.py` checks before the manifest is frozen, and
which is the same gate the development combination runner had to pass.

Seeds: none drawn here. The gradient-boosted rows seed `random_state` from the project seed
inside `lib.stage2_perturb.make_model`, unchanged.
"""
from __future__ import annotations

import statistics
from dataclasses import replace

import pandas as pd

from lib.backtest import rolling_splits
from lib.crps import crps_gaussian
from lib.stage2_perturb import (
    SchemeConfig, Stage1Config, Stage2Config, configs_as_dict, load_actuals, load_series,
    modelable_provinces, run_combination,
)

Z90 = 1.6448536269514722
MIN_SIGMA = 1e-6  # the sigma floor 03_baselines uses; kept identical so the gate can pass

# The scheme the holdout is evaluated under: the project's fixed n_periods and stride
# (plan §4), with n_splits set by the length of the held-out file rather than chosen.
HOLDOUT_SCHEME = SchemeConfig(n_periods=3, n_splits=4, stride=3)


# ---- the cell set, fixed from development ------------------------------------------------------

def development_provinces(dev_rows: list[dict], min_modelable_months: int) -> list[str]:
    """The modelable province set, derived from the development months only."""
    return modelable_provinces(dev_rows, min_modelable_months)


def restrict(rows: list[dict], provinces: list[str]) -> list[dict]:
    keep = set(provinces)
    return [r for r in rows if r["location"] in keep]


def months_of(rows: list[dict]) -> list[str]:
    return sorted({r["time_period"] for r in rows})


# ---- the two-stage pipeline --------------------------------------------------------------------

def two_stage(rows: list[dict], dev_rows: list[dict], s1: Stage1Config, sc: SchemeConfig,
              s2: Stage2Config) -> tuple[list[dict], dict]:
    """One combination, scored over whatever span `rows` covers, on development's province set."""
    provinces = development_provinces(dev_rows, sc.min_modelable_months)
    per_cell, conclusion = run_combination(restrict(rows, provinces), s1, sc, s2)
    conclusion["province_set"] = {"source": "development months, min_modelable_months="
                                            f"{sc.min_modelable_months}", "provinces": provinces}
    conclusion["evaluated_months"] = sorted({c["month"] for c in per_cell})
    return per_cell, conclusion


# ---- the two required baselines -----------------------------------------------------------------

def _baseline_conclusion(model: str, per_cell: list[dict], provinces: list[str],
                         splits: list[dict], n_fit_failures: int) -> dict:
    scored = [r for r in per_cell if r["crps"] is not None]
    by_split = {}
    for sp in sorted({r["split"] for r in scored}):
        sub = [r for r in scored if r["split"] == sp]
        by_split[f"split{sp}"] = sum(r["crps"] for r in sub) / len(sub)
    return {
        "model": model, "n_provinces": len(provinces), "n_splits": len(splits),
        "n_cells_total": len(per_cell), "n_cells_scored": len(scored),
        "n_fit_failures": n_fit_failures,
        "mean_crps": sum(r["crps"] for r in scored) / len(scored) if scored else None,
        "coverage_90": (sum(abs(r["actual"] - r["forecast_mean"]) <= Z90 * r["forecast_se"]
                            for r in scored) / len(scored)) if scored else None,
        "evaluated_months": sorted({r["month"] for r in per_cell}),
        "by_split": by_split,
    }


def persistence(rows: list[dict], dev_rows: list[dict], sc: SchemeConfig) -> tuple[list[dict], dict]:
    """Last observed value at the split's origin, held flat; sigma from the training window's
    one-step differences. The same forecast as `03_baselines/01_persistence`."""
    provinces = development_provinces(dev_rows, sc.min_modelable_months)
    rows = restrict(rows, provinces)
    all_months = months_of(rows)
    splits = rolling_splits(all_months, sc.n_periods, sc.n_splits, sc.stride)

    per_cell, n_fit_failures = [], 0
    for province in provinces:
        actuals = load_actuals(province, rows)
        for split in splits:
            train_months = split["train_months"]
            observed = load_series(province, train_months, rows).dropna()
            if observed.empty:
                n_fit_failures += 1
                for month in split["test_months"]:
                    per_cell.append({"province": province, "split": split["split"], "month": month,
                                     "actual": actuals.get(month), "forecast_mean": None,
                                     "forecast_se": None, "crps": None, "fit_failed": True,
                                     "error": "no observed value in training window"})
                continue
            last_value = float(observed.iloc[-1])
            step_errors = observed.diff().dropna()
            sigma = float(step_errors.std(ddof=1)) if len(step_errors) >= 2 else float("nan")
            if not (sigma > 0):
                sigma = MIN_SIGMA
            for month in split["test_months"]:
                actual = actuals.get(month)
                crps = crps_gaussian(actual, last_value, max(sigma, MIN_SIGMA)) if actual is not None else None
                per_cell.append({"province": province, "split": split["split"], "month": month,
                                 "actual": actual, "forecast_mean": last_value, "forecast_se": sigma,
                                 "crps": crps, "fit_failed": False, "error": None})
    model = ("persistence (last observed, held flat), sigma = std of training-window "
             "one-step differences")
    return per_cell, _baseline_conclusion(model, per_cell, provinces, splits, n_fit_failures)


def climatology(rows: list[dict], dev_rows: list[dict], sc: SchemeConfig) -> tuple[list[dict], dict]:
    """Mean of the same calendar month in the training window; sigma its standard deviation.
    The same forecast as `03_baselines/02_climatology`."""
    provinces = development_provinces(dev_rows, sc.min_modelable_months)
    rows = restrict(rows, provinces)
    all_months = months_of(rows)
    splits = rolling_splits(all_months, sc.n_periods, sc.n_splits, sc.stride)

    per_cell, n_fit_failures = [], 0
    for province in provinces:
        actuals = load_actuals(province, rows)
        for split in splits:
            train_end = split["train_months"][-1]
            train_actuals = {m: v for m, v in actuals.items() if m <= train_end}
            for month in split["test_months"]:
                cm = month.split("-")[1]
                same_month = [v for m, v in train_actuals.items() if m.split("-")[1] == cm]
                actual = actuals.get(month)
                if not same_month:
                    n_fit_failures += 1
                    per_cell.append({"province": province, "split": split["split"], "month": month,
                                     "actual": actual, "forecast_mean": None, "forecast_se": None,
                                     "crps": None, "fit_failed": True,
                                     "error": "no training-window observation for this calendar month"})
                    continue
                mean_val = statistics.fmean(same_month)
                sigma = statistics.stdev(same_month) if len(same_month) >= 2 else float("nan")
                if not (sigma > 0):
                    sigma = MIN_SIGMA
                crps = crps_gaussian(actual, mean_val, max(sigma, MIN_SIGMA)) if actual is not None else None
                per_cell.append({"province": province, "split": split["split"], "month": month,
                                 "actual": actual, "forecast_mean": mean_val, "forecast_se": sigma,
                                 "crps": crps, "fit_failed": False, "error": None})
    model = ("seasonal climatology (mean of same calendar month in training window), "
             "sigma = std of same calendar month's training-window values")
    return per_cell, _baseline_conclusion(model, per_cell, provinces, splits, n_fit_failures)


# ---- the frozen row set -------------------------------------------------------------------------

SUFFIX = "__holdout"
MAIN = "h_levelOnlyBoosting"
MAIN_CONFIG = Stage2Config(features="level_only")
S1, SC = Stage1Config, HOLDOUT_SCHEME


def gbm(**over) -> dict:
    base = dict(n_estimators=150, max_depth=3, learning_rate=0.05, subsample=0.8, min_samples_leaf=20)
    base.update(over)
    return base


def holdout_combinations() -> dict[str, tuple]:
    """Every row the frozen phase-E manifest may name, as an executable configuration.

    A two-stage row is `(Stage1Config, SchemeConfig, Stage2Config)`; a baseline row is
    `("baseline", <callable>)`. The manifest names rows and this dictionary says what they
    mean, and the planner refuses a disagreement in either direction -- the same contract the
    development runner has, so a frozen row can never be a row nobody can run.

    The 26 tier-2 rows are the development v2 set (`06_stability/results/manifest.csv`) under
    holdout names and the holdout scheme, so every one of them is paired with a development
    measurement of the same judgment call.
    """
    M = MAIN_CONFIG
    s2 = lambda **kw: replace(M, **kw)  # noqa: E731
    t = SUFFIX
    rows: dict[str, tuple] = {
        # tier 0 -- the reported comparison
        f"main@h{t}": (S1(), SC, M),
        f"baseline=persistence{t}": ("baseline", persistence),
        f"baseline=climatology{t}": ("baseline", climatology),
        # tier 1 -- the not-taken stage-2 siblings the parametrised pipeline expresses
        f"04_stage2=f_oosErrorRidge{t}": (S1(), SC, s2(family="ridge", ridge_alpha=10.0, features="full")),
        f"04_stage2=g_oosErrorBoosting{t}": (S1(), SC, s2(features="full")),
        f"04_stage2=i_boundedBoosting{t}": (S1(), SC, s2(features="full", bounded_correction=True)),
        f"04_stage2=j_levelOnlyBoundedBoosting{t}": (S1(), SC, s2(bounded_correction=True)),
        # tier 2 -- stage 1's specification
        f"stage1=airline_011x011@h{t}": (S1(order=(0, 1, 1), seasonal_order=(0, 1, 1, 12)), SC, M),
        f"stage1=nodiff_101x100@h{t}": (S1(order=(1, 0, 1)), SC, M),
        f"stage1=enforce_stationarity@h{t}": (S1(enforce=True), SC, M),
        # tier 2 -- training window, scheme, modelability
        f"window=rolling_72m@h{t}": (S1(window="rolling", window_months=72), SC, M),
        f"window=start_2002@h{t}": (S1(window="start", window_start="2002-01"), SC, M),
        f"scheme=chap_default_7x1@h{t}": (S1(), replace(SC, n_splits=7, stride=1), M),
        f"modelable=36_months@h{t}": (S1(), replace(SC, min_modelable_months=36), M),
        # tier 2 -- the stage-2 target, features, combination rule and tuning
        f"stage2=no_clip@h{t}": (S1(), SC, s2(clip_at_zero=False)),
        f"stage2=zclip2@h{t}": (S1(), SC, s2(zclip=2.0)),
        f"stage2=zclip5@h{t}": (S1(), SC, s2(zclip=5.0)),
        f"stage2=no_winsorisation@h{t}": (S1(), SC, s2(zclip=None)),
        f"stage2=scale_by_residual_rms@h{t}": (S1(), SC, s2(standardise="resid_rms")),
        f"stage2=per_horizon@h{t}": (S1(), SC, s2(per_horizon=True)),
        f"stage2=bounded_floor0@h{t}": (S1(), SC, s2(bounded_correction=True, bound_floor=0.0)),
        f"stage2=plus_recent_and_incidence@h{t}": (S1(), SC, s2(features="no_cross_province")),
        f"stage2=plus_recent_and_cross@h{t}": (S1(), SC, s2(features="no_incidence")),
        f"stage2=full_plus_climate@h{t}": (S1(), SC, s2(features="with_climate")),
        f"stage2=depth2@h{t}": (S1(), SC, s2(gbm_params=gbm(max_depth=2))),
        f"stage2=depth4_300trees@h{t}": (S1(), SC, s2(gbm_params=gbm(max_depth=4, n_estimators=300))),
        f"stage2=lr0.1@h{t}": (S1(), SC, s2(gbm_params=gbm(learning_rate=0.1))),
        f"stage2=min_leaf50@h{t}": (S1(), SC, s2(gbm_params=gbm(min_samples_leaf=50))),
        f"stage2=alt_seed@h{t}": (S1(), SC, s2(seed_component="04_stage2/g_oosErrorBoosting/alt")),
        f"stage2=warmup12@h{t}": (S1(), SC, s2(warmup=12)),
        f"stage2=warmup36@h{t}": (S1(), SC, s2(warmup=36)),
        f"stage2=rolling_refit_oos@h{t}": (S1(), SC, s2(oos_mode="rolling_refit")),
        f"stage2=min_train_rows1000@h{t}": (S1(), SC, s2(min_train_rows=1000)),
    }
    return rows


def run_row(name: str, rows: list[dict], dev_rows: list[dict]) -> tuple[list[dict], dict]:
    """Execute one frozen row. The only entry point phase E's runner needs."""
    spec = holdout_combinations()[name]
    if spec[0] == "baseline":
        per_cell, conclusion = spec[1](rows, dev_rows, HOLDOUT_SCHEME)
        conclusion["config"] = {"scheme": configs_as_dict(Stage1Config(), HOLDOUT_SCHEME,
                                                          Stage2Config())["scheme"]}
        return per_cell, conclusion
    return two_stage(rows, dev_rows, *spec)
