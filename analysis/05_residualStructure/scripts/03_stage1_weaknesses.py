#!/usr/bin/env python3
"""Stage 1's weaknesses, documented in one file-grounded place -- not repaired.

The human fixed this after phase D (plan §4b, 2026-09-21): stage 1 stays the per-province
SARIMAX(1,1,1)x(1,0,0,12) on raw counts, because the project's question is whether a second
stage earns its place on top of a SARIMAX, and the first stage is the premise. What this
script does is collect, from files this node and its siblings already wrote, every weakness
the diagnostics and the stability run found, each with its evidence and with what it implies
for a stage 2 that has to live with it. Nothing is recomputed from raw data; every number is
read from `results/test_cells.csv`, `results/error_structure.json`,
`../02_stage1/results/conclusion.json` and `../03_baselines/results/comparison.json` -- all
of them produced earlier in `analysis/run.sh`'s order, so this script never reads a result a
later node writes (the stability node's alternative-specification scores are cited by path
in the prose, not read here).

Output: `results/stage1_weaknesses.json` -- a list of weaknesses, each with a statement, its
evidence (numbers with the file they come from), what it does to the forecasts, whether a
stage 2 can address it, and the fork that would address it at stage 1 (not taken, by the
human's decision).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

NODE = Path(__file__).resolve().parents[1]
ANALYSIS = NODE.parents[0]
RESULTS = NODE / "results"
ES = json.loads((RESULTS / "error_structure.json").read_text())
STAGE1 = json.loads((ANALYSIS / "02_stage1" / "results" / "conclusion.json").read_text())
BASELINES = json.loads((ANALYSIS / "03_baselines" / "results" / "comparison.json").read_text())
Z90 = 1.6448536269514722


def main() -> None:
    with (RESULTS / "test_cells.csv").open(newline="") as f:
        cells = list(csv.DictReader(f))
    z = np.array([float(c["z"]) for c in cells])
    mu = np.array([float(c["mu1"]) for c in cells])
    se = np.array([float(c["se1"]) for c in cells])
    actual = np.array([float(c["actual"]) for c in cells])
    absz = np.abs(z)
    by_h = ES["by_horizon"]
    fixes = ES["spread_and_sign_fixes_on_test_cells"]
    prov = {p["province"]: p for p in ES["by_province"]}

    weaknesses = [
        {
            "id": "W1", "weakness": "Interval coverage below nominal, and the deficit is a heavy tail a Gaussian cannot carry",
            "evidence": {
                "coverage_90_by_horizon": {h: by_h[h]["coverage_90"] for h in by_h},
                "median_abs_z": float(np.median(absz)), "q90_abs_z": float(np.quantile(absz, 0.90)),
                "q99_abs_z": float(np.quantile(absz, 0.99)), "max_abs_z": float(absz.max()),
                "share_cells_abs_z_above_3": float(np.mean(absz > 3)),
                "sigma_factor_for_nominal_coverage_by_horizon": fixes["q90_factor_by_h"],
                "mean_crps_if_sigma_scaled_by_that_factor (oracle)": fixes["mean_crps_sigma_x_q90_factor_by_h"],
                "mean_crps_stage1": fixes["mean_crps_stage1"],
                "source": "results/error_structure.json, results/test_cells.csv",
            },
            "effect": "Most cells are over-covered (median |z| about 0.3) while a few percent are far outside any interval; "
                      "scaling sigma to reach 90% coverage raises mean CRPS from 26.05 to 35.65.",
            "stage2_can_address": "No -- a stage 2 that adds to the mean cannot change the shape of the predictive distribution.",
            "stage1_fork_not_taken": "A count or heavier-tailed predictive family (negative binomial, zero-truncated normal), "
                                     "with a verified CRPS for it (plan §4b 2026-09-21: not taken, human-set).",
        },
        {
            "id": "W2", "weakness": "Negative forecast means for a count",
            "evidence": {"share_test_cells_stage1_mean_negative": fixes["share_stage1_mean_negative"],
                         "mean_crps_if_mean_clipped_at_zero": fixes["mean_crps_mean_clipped_at_zero"],
                         "provinces_with_most_negative_means": sorted(((p, v["share_stage1_mean_negative"]) for p, v in prov.items()),
                                                                     key=lambda t: -t[1])[:3],
                         "source": "results/error_structure.json"},
            "effect": "4.0% of stage 1's forecast means are below zero, concentrated in Savannakhet after its 2008 collapse; "
                      "clipping them alone lowers mean CRPS by 0.56%.",
            "stage2_can_address": "Partly -- every stage-2 candidate from batch 10 on clips the corrected mean at zero.",
            "stage1_fork_not_taken": "A non-negative predictive family, or a log1p transform with bias-corrected back-transform.",
        },
        {
            "id": "W3", "weakness": "The standard error does not grow with the forecast level as a count's variance does",
            "evidence": {"spearman_abs_z_vs_level": ES["heteroscedasticity"]["spearman_abs_z_vs_level_std"],
                         "pearson_abs_error_vs_mu1": ES["heteroscedasticity"]["pearson_abs_error_vs_mu1"],
                         "example_savannakhet_se_range_2008_09": [float(se[[c["province"] == "LA-SV" for c in cells]].min()),
                                                                  float(se[[c["province"] == "LA-SV" for c in cells]].max())],
                         "example_savannakhet_mean_actual_2008_09": float(actual[[c["province"] == "LA-SV" for c in cells]].mean()),
                         "source": "results/error_structure.json, results/test_cells.csv"},
            "effect": "The se is set by the training window's innovation variance, so a province whose level collapsed keeps an "
                      "se tens of times its current level (Savannakhet: se 200-414, mean actual 8), and a province whose level "
                      "rose has an se far too small (|z| up to 164). A standardised correction inherits this: the same z-hat is "
                      "130-190 cases in Savannakhet and under one case in Xiangkhouang.",
            "stage2_can_address": "Partly -- bounding the correction relative to the forecast level (i_boundedBoosting) limits the "
                                  "damage; it does not fix the interval.",
            "stage1_fork_not_taken": "A variance that scales with the mean (count family), or a multiplicative model.",
        },
        {
            "id": "W4", "weakness": "Systematic multi-step bias: over-prediction at high forecast levels and in November-April, under-prediction in the June-July onset",
            "evidence": {"share_test_cells_error_positive_by_horizon": {h: by_h[h]["share_error_positive"] for h in by_h},
                         "median_error_by_horizon": {h: by_h[h]["median_error"] for h in by_h},
                         "mean_error_by_horizon": {h: by_h[h]["bias_mean_error"] for h in by_h},
                         "share_error_positive_by_calendar_month": {m: v["share_error_positive"] for m, v in ES["by_calendar_month"].items()},
                         "spearman_z_vs_forecast_level": ES["feature_correlations_with_z"]["level_std"]["spearman_with_z"],
                         "source": "results/error_structure.json"},
            "effect": "Two thirds of forecasts are too high; the few that are too low are far too low. The seasonal AR term "
                      "carries last year's level into the off-season and lags the onset.",
            "stage2_can_address": "Yes -- this is the structure the batch-10 candidates learned (forecast level, month, horizon), "
                                  "and the reason they earn their place at 2-3 months ahead.",
            "stage1_fork_not_taken": "A different seasonal specification (the airline model was run as a perturbation: stage 1 "
                                     "alone worse, corrected forecast similar), or a transform.",
        },
        {
            "id": "W5", "weakness": "Reporting-regime breaks in the test years that no province's own history predicts",
            "evidence": {"provinces": {p: {"train_mean_cases_split0": prov[p]["train_mean_cases_split0"], "mean_actual_test": prov[p]["mean_actual_test"],
                                            "share_of_total_crps": prov[p]["share_of_total_crps"], "coverage_90": prov[p]["coverage_90"]}
                                       for p in ("LA-SV", "LA-BK", "LA-SL", "LA-XI", "LA-XE") if p in prov},
                         "context": "Laos moved from paper-based reporting to the electronic EWARN system in 2008 and not all provinces "
                                    "reported before 2010 (Khampapongpane et al. 2014, WPSAR; batch 10 report)",
                         "source": "results/error_structure.json"},
            "effect": "Savannakhet fell from 166 to 8 cases a month between the training window and 2008-09; Bokeo rose from 0.7 to "
                      "39, Salavan from 4 to 61. These cells are the coverage deficit and much of the CRPS.",
            "stage2_can_address": "Only after the break is a few months old (recent-residual and reporting-level features); not at the break.",
            "stage1_fork_not_taken": "A level-shift or intervention term; a rolling window (run as a perturbation: stage 1 alone "
                                     "better at 23.99, and the corrected forecast still ahead).",
        },
        {
            "id": "W6", "weakness": "The specification was a first default, not a selected one",
            "evidence": {"stage1_spec": STAGE1["model"], "mean_crps_stage1": STAGE1["mean_crps"],
                         "vs_baselines": BASELINES,
                         "alternative_specifications_scored_at": "../06_stability/results/perturbation_effects.csv "
                                                                 "(rows stage1=* and window=*: stage-1-alone mean CRPS under each)",
                         "source": "../02_stage1/results/conclusion.json, ../03_baselines/results/comparison.json"},
            "effect": "Stage 1 alone beats both required baselines (03_baselines/results/comparison.json). Its own score moves "
                      "materially under alternative orders and windows (06_stability/results/perturbation_effects.csv); the "
                      "stage-2 margin survives every one of them, but the absolute level of the two-stage forecast depends on them.",
            "stage2_can_address": "Not applicable -- this is a statement about what the premise is.",
            "stage1_fork_not_taken": "Order selection by information criterion or by backtest; both are selection on the same "
                                     "development data and were deliberately not done (plan §4b, 2026-09-21).",
        },
    ]
    out = {"decision": "stage 1 is not repaired (human-set, 2026-09-21); these weaknesses are documented, not fixed",
           "n_weaknesses": len(weaknesses), "weaknesses": weaknesses}
    (RESULTS / "stage1_weaknesses.json").write_text(json.dumps(out, indent=2) + "\n")
    for w in weaknesses:
        print(w["id"], w["weakness"])


if __name__ == "__main__":
    main()
