#!/usr/bin/env python3
"""`/perturb plan`: enumerate the judgment calls made in batches 1-10, name a reasonable
alternative for each, cost it from measured run times, rank by expected informativeness, and
write the development perturbation manifest -- then freeze it.

**Three tiers**, so that the absence of a perturbation is always a visible decision
(AGENTS.md §4, §6):

- **Tier 1** -- alternatives already in the tree as not-taken siblings of a main path. Derived
  from the tree itself, never typed: every child of an alternatives node other than its main
  path. The stability run executes them by calling their own `run.sh`, and `/validate
  invariants` (`combos`) refuses a manifest whose tier-1 rows disagree with the tree.
- **Tier 2** -- judgment calls that were made as constants or code paths rather than nodes:
  stage 1's order and options, the training window and warm-up, the backtest scheme, and
  every constant in the main-path stage 2 (winsorisation bound, clipping, feature set,
  standardisation, per-horizon vs pooled fitting, hyperparameters, seed). Each row names the
  node the change applies to, the parameter, its main-path value and the alternative value,
  the basis for calling the alternative reasonable, and an informativeness rank with its
  reason. They are run by the stability node's own combination runner (batch 12), which
  recomputes stage 1 and stage 2 for one combination and writes `results/<combination>/`
  here; its `main` combination must reproduce the main path's stored per-cell scores byte
  for byte before any other combination is trusted.
- **Tier 3** -- alternatives that are reasonable but need machinery this project has not
  built (a new verified metric, a new data acquisition, a new combination design). Listed
  with the reason they are not run, so a reader sees the line and what is below it.

**Budget.** `readme-at-start.md` left the stability compute budget to be set once per-run
cost was known. `results/run_costs.csv` (from `01_measure_run_costs.py`) gives it: the whole
existing tree re-runs in about two minutes, so compute is not the binding constraint;
development effort per perturbation is. BUDGET_WALL_SECONDS below is a provisional ceiling
(agent-autonomous, for the human to revise) and the manifest records where the cumulative
cost of the ranked rows crosses it; at the measured costs no tier-2 row falls below the line.

**Freeze.** `results/manifest_freeze.json` records the manifest's sha256, the commit it was
planned at and the date. Once committed, a change to the development manifest is a recorded
decision in the plan's §4b, not an edit. (The holdout manifest is frozen separately, row 14.)

Seeds: none drawn.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/06_stability
ANALYSIS = NODE.parents[0]
ROOT = ANALYSIS.parent
RESULTS = NODE / "results"
RUN_COSTS = RESULTS / "run_costs.csv"

BUDGET_WALL_SECONDS = 3600  # provisional ceiling on stability compute; see docstring
MAIN_STAGE2 = "g_oosErrorBoosting"
ROLLING_REFIT_EXTRA_SECONDS = 17 * 8 * 110 * 0.05  # provinces x splits x origins x one SARIMAX fit


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    v = m.group(1).strip() if m else ""
    return None if v in ("", "-", "none") else v


def tier1_from_tree() -> list[dict]:
    rows = []
    for claim in sorted(ANALYSIS.rglob("claim.md")):
        node = claim.parent
        text = claim.read_text()
        if field(text, "kind") != "alternatives":
            continue
        main = field(text, "main-path")
        for kid in sorted(p.name for p in node.iterdir() if p.is_dir() and (p / "claim.md").exists()):
            if kid == main:
                continue
            rows.append({"fork": str(node.relative_to(ROOT)), "child": kid,
                         "combination": f"{node.name}={kid}",
                         "node": f"{node.relative_to(ROOT)}/{kid}"})
    return rows


def read_costs() -> dict[str, float]:
    with RUN_COSTS.open(newline="") as f:
        return {r["node"]: float(r["wall_seconds"]) for r in csv.DictReader(f)}


def tier2(costs: dict[str, float]) -> list[dict]:
    t_g = costs[f"analysis/04_stage2/{MAIN_STAGE2}"]
    t_s1 = costs["analysis/02_stage1"]
    t_f = costs["analysis/04_stage2/f_oosErrorRidge"]
    s2 = f"analysis/04_stage2/{MAIN_STAGE2}"
    S1 = "analysis/02_stage1"
    # (combination, node, parameter, main_value, value, basis, rank, rank_reason, est_cost)
    spec = [
        # -- stage 1 specification -----------------------------------------------------------
        ("stage1=airline_011x011", S1, "SARIMAX order", "(1,1,1)x(1,0,0,12)", "(0,1,1)x(0,1,1,12)",
         "the airline model is the standard seasonal default and differs in the seasonal component (MA on a seasonal difference vs AR on a level)",
         1, "changes the residual stage 2 corrects; most likely of the stage-1 forks to move the conclusion", t_s1 + t_g),
        ("stage1=nodiff_101x100", S1, "SARIMAX order", "(1,1,1)x(1,0,0,12)", "(1,0,1)x(1,0,0,12)",
         "d=1 was chosen without a unit-root test; a level-stationary AR is equally defensible on bounded counts",
         3, "the level-dependent over-prediction stage 2 learned may be a differencing artefact", t_s1 + t_g),
        ("stage1=enforce_stationarity", S1, "enforce_stationarity/invertibility", "False/False", "True/True",
         "statsmodels' defaults; batch 2 turned them off for convergence on sparse provinces",
         12, "mostly changes fits in sparse provinces, which carry little CRPS", t_s1 + t_g),
        # -- data, window, scheme --------------------------------------------------------------
        ("window=rolling_72m", "analysis/02_stage1", "training window", "expanding from 1998-01", "rolling, last 72 months",
         "a rolling window forgets the 2003 epidemic and the pre-2008 reporting regime, which the diagnostics found dominate the errors",
         2, "directly tests whether the regime breaks, not the model, drive the result", t_s1 + t_g),
        ("window=start_2002", "analysis/02_stage1", "training window start", "1998-01", "2002-01",
         "the zero-heavy early years are a zero-handling judgment call the plan names explicitly",
         6, "the zero-handling fork the plan asks for", t_s1 + t_g),
        ("scheme=chap_default_7x1", "analysis/01_data/03_backtest_scheme", "n_splits/stride", "8/3", "7/1 (Chap's evaluate defaults, n_periods 3 unchanged)",
         "the scheme was reused from the prior project for comparability; Chap's own default evaluates 7 consecutive quarters",
         4, "a different cell set; says whether the gain is a property of these 24 test months", t_s1 + t_g),
        ("modelable=36_months", "analysis/01_data/02_characterise", "min modelable months", "24", "36",
         "the modelability threshold was set once, unexamined",
         14, "changes which sparse provinces enter; small CRPS mass", t_s1 + t_g),
        # -- stage 2: target and combination rule ----------------------------------------------
        ("stage2=g_no_clip", s2, "CLIP_AT_ZERO", "True", "False",
         "clipping is a combination-rule choice; its effect is already decomposed in comparison.json",
         9, "known to be worth ~0.5%; confirms the decomposition under the frozen run", t_g),
        ("stage2=g_zclip2", s2, "ZCLIP (winsorisation bound)", "3", "2",
         "the bound was set by judgment; a tighter one bounds corrections at two standard errors",
         5, "the bound decides how much the regime-break cells shape the fit", t_g),
        ("stage2=g_zclip5", s2, "ZCLIP", "3", "5", "a looser bound", 7, "as above, other direction", t_g),
        ("stage2=g_no_winsorisation", s2, "ZCLIP", "3", "none",
         "fitting the raw standardised error is the naive choice", 8, "shows what the bound is protecting against", t_g),
        ("stage2=g_scale_by_residual_rms", s2, "target standardisation", "stage 1 se", "province in-sample residual RMS",
         "the diagnostics kept both; the se inflates corrections where stage 1's spread is miscalibrated (Savannakhet)",
         2, "targets the understood failure mode; could move the province distribution of gains", t_g),
        ("stage2=g_bounded_correction", s2, "correction bound", "|zhat| <= 3", "additionally |correction| <= max(stage1 mean, 10)",
         "the refinement batch 10 logged as untried after the Savannakhet diagnosis",
         1, "the one refinement directly motivated by an understood loss", t_g),
        ("stage2=g_per_horizon", s2, "fitting", "one pooled model, horizon indicators", "one model per horizon",
         "the direct multi-step design (Ben Taieb & Hyndman 2014) fits each horizon separately",
         4, "the horizon coupling the human asked to be sure of", t_g),
        # -- stage 2: features -------------------------------------------------------------------
        ("stage2=g_no_cross_province", s2, "features", "full set", "drop nat_last3",
         "the cross-province mean had the weakest diagnostic signal", 10, "isolates the pooling-as-information axis", t_g),
        ("stage2=g_no_incidence_terms", s2, "features", "full set", "drop cum12_anom, zero_frac24",
         "the literature-motivated incidence terms had weak marginal correlations", 8, "isolates the reporting-level term", t_g),
        ("stage2=g_level_month_horizon_only", s2, "features", "full set", "h, month, level_log, level_log_x_h only",
         "the diagnostics' cross-validated test found only the level features beat stage 1",
         3, "the minimal model; if it matches the full one the rest is decoration", t_g),
        ("stage2=g_with_climate_anomalies", s2, "features", "no climate", "add lag-h rainfall/temperature/humidity anomalies (origin and 3-month mean)",
         "climate was excluded on diagnostic evidence; the fork must be run, not argued", 6, "closes the climate question on the right target", t_g),
        # -- stage 2: family hyperparameters and seed --------------------------------------------
        ("stage2=g_depth2", s2, "max_depth", "3", "2", "a fixed, unsearched configuration; neighbours must be tried", 7, "", t_g),
        ("stage2=g_depth4_300trees", s2, "max_depth/n_estimators", "3/150", "4/300", "as above, more capacity", 7, "", t_g),
        ("stage2=g_lr0.1", s2, "learning_rate", "0.05", "0.1", "as above", 9, "", t_g),
        ("stage2=g_min_leaf50", s2, "min_samples_leaf", "20", "50", "as above, stronger smoothing", 9, "", t_g),
        ("stage2=g_alt_seed", s2, "component seed", "component_seed('04_stage2/g_oosErrorBoosting')", "component_seed('04_stage2/g_oosErrorBoosting/alt')",
         "subsample randomness is real; the seed is a judgment call like any other", 5, "cheap; a seed-sensitive margin is not a margin", t_g),
        ("stage2=f_alpha1", "analysis/04_stage2/f_oosErrorRidge", "RIDGE_ALPHA", "10", "1", "unsearched penalty", 10, "the linear sibling's own sensitivity", t_f),
        ("stage2=f_alpha100", "analysis/04_stage2/f_oosErrorRidge", "RIDGE_ALPHA", "10", "100", "unsearched penalty", 10, "", t_f),
        # -- stage 2: how the training errors are made -------------------------------------------
        ("stage2=g_warmup12", s2, "WARMUP_MONTHS", "24", "12", "the diffuse-initialisation warm-up was set by judgment", 11, "", t_g),
        ("stage2=g_warmup36", s2, "WARMUP_MONTHS", "24", "36", "as above", 11, "", t_g),
        ("stage2=g_rolling_refit_oos", s2, "in-window error construction", "parameters fixed at the window's estimates", "true rolling refit at every origin",
         "the fixed-parameter shortcut is mildly optimistic, logged as such in every record", 3,
         "the one approximation in the new candidates' construction; costly but affordable", t_g + ROLLING_REFIT_EXTRA_SECONDS),
        ("stage2=g_min_train_rows1000", s2, "MIN_TRAIN_ROWS", "200", "1000", "abstention threshold set by judgment", 13, "never binds at ~5,000 rows; confirms that", t_g),
    ]
    rows = []
    for combo, node, param, main_v, alt_v, basis, rank, why, cost in spec:
        rows.append({"combination": combo, "tier": 2, "fork": "-", "child": "-", "node": node,
                     "parameter": param, "main_value": main_v, "value": alt_v, "basis": basis,
                     "informativeness_rank": rank, "rank_reason": why, "est_cost_s": round(cost, 1)})
    return rows


def tier3() -> list[dict]:
    spec = [
        ("stage1=log1p_transform", "analysis/02_stage1", "target transform", "raw counts", "log1p, bias-corrected back-transform",
         "the plan logged this fork in batch 2", "needs a verified CRPS on the transformed or lognormal scale (an extension of 00_metric); development cost, not compute"),
        ("stage1=negative_binomial_family", "analysis/02_stage1", "predictive family", "Gaussian", "negative binomial or zero-truncated normal",
         "the diagnostics show the coverage deficit is a heavy tail a Gaussian cannot carry; the literature's count models reach nominal coverage",
         "needs a verified count-distribution CRPS and a different stage-2 contract (correction on a non-Gaussian mean); the most consequential fork not run"),
        ("stage2=g_multiplicative", "analysis/04_stage2/g_oosErrorBoosting", "combination rule", "additive", "multiplicative on the log scale",
         "Wang et al. (2013) find multiplicative hybrids more accurate", "undefined where stage 1's mean is near or below zero; needs a design decision"),
        ("stage2=g_enso_covariate", "analysis/04_stage2/g_oosErrorBoosting", "features", "dataset columns only", "add ONI/Nino3.4 at lags 3-6 months",
         "the literature's one climate signal with multi-month lead in Laos", "a new data acquisition and a data-governance decision (plan §4); human call"),
        ("evaluation=chap_native", "analysis/00_metric", "harness", "native Python CRPS", "chap-core evaluation",
         "the prior project's route", "decided against in plan §4 (agent-autonomous, batch 1); reopening it is a plan change, not a perturbation"),
    ]
    return [{"combination": c, "tier": 3, "fork": "-", "child": "-", "node": n, "parameter": p, "main_value": m,
             "value": v, "basis": b, "informativeness_rank": "-", "rank_reason": "", "est_cost_s": "-",
             "status": "not_run", "reason_if_not_run": r} for c, n, p, m, v, b, r in spec]


def main() -> None:
    costs = read_costs()
    t1 = tier1_from_tree()
    for r in t1:
        r.update({"tier": 1, "parameter": "stage-2 family / input (a node)", "main_value": MAIN_STAGE2,
                  "value": r["child"], "basis": "a sibling built and scored in batches 4-10; its own claim.md holds the argument",
                  "informativeness_rank": 0, "rank_reason": "already run; results in the sibling's own results/",
                  "est_cost_s": round(costs.get(f"analysis/04_stage2/{r['child']}", 0.0), 1)})
    t2 = tier2(costs)

    # Rank tier 2 and place the budget line on cumulative cost (tier 1 is already run and costs nothing new).
    t2.sort(key=lambda r: (r["informativeness_rank"], r["combination"]))
    cumulative = 0.0
    line_index = None
    for i, r in enumerate(t2):
        cumulative += r["est_cost_s"]
        r["cumulative_cost_s"] = round(cumulative, 1)
        if cumulative <= BUDGET_WALL_SECONDS:
            r["status"] = "planned"
        else:
            r["status"] = "below_budget_line"
            line_index = i if line_index is None else line_index
        r["reason_if_not_run"] = "" if r["status"] == "planned" else f"cumulative cost exceeds BUDGET_WALL_SECONDS={BUDGET_WALL_SECONDS}"
    for r in t1:
        r.update({"status": "planned", "reason_if_not_run": "", "cumulative_cost_s": "-"})
    t3 = tier3()
    for r in t3:
        r["cumulative_cost_s"] = "-"

    fieldnames = ["combination", "tier", "fork", "child", "node", "parameter", "main_value", "value", "basis",
                  "informativeness_rank", "rank_reason", "est_cost_s", "cumulative_cost_s", "status", "reason_if_not_run"]
    RESULTS.mkdir(exist_ok=True)
    rows = t1 + t2 + t3
    with (RESULTS / "manifest.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    manifest_bytes = (RESULTS / "manifest.csv").read_bytes()
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    planned_cost = sum(r["est_cost_s"] for r in t2 if r["status"] == "planned")
    summary = {
        "n_rows": len(rows), "n_tier1": len(t1), "n_tier2": len(t2), "n_tier3_not_run": len(t3),
        "n_tier2_planned": sum(r["status"] == "planned" for r in t2),
        "n_tier2_below_budget_line": sum(r["status"] == "below_budget_line" for r in t2),
        "budget_wall_seconds": BUDGET_WALL_SECONDS,
        "planned_tier2_cost_s": round(planned_cost, 1),
        "where_the_line_fell": ("below every tier-2 row: nothing planned is excluded for budget" if line_index is None
                                 else f"after ranked row {line_index} ({t2[line_index]['combination']})"),
        "measured_costs_s": costs,
        "run_design_for_batch_12": (
            "tier 1: call each sibling's run.sh and read its results; tier 2: a combination runner in this node "
            "recomputes stage 1 (with the combination's stage-1 settings) and the main-path stage 2 (with the "
            "combination's stage-2 settings) for the combination's schedule, writes results/<combination>/, and is "
            "trusted only after its 'main' combination reproduces 04_stage2/g_oosErrorBoosting/results/per_cell_scores.csv "
            "byte for byte; conclusions are collected per combination as (mean CRPS stage 1, mean CRPS two-stage, "
            "coverage of each, sign of the difference) and reported as a distribution"),
    }
    (RESULTS / "manifest_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    freeze = {
        "frozen_file": "results/manifest.csv",
        "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "rows": len(rows),
        "frozen_at_commit": head,
        "frozen_on": time.strftime("%Y-%m-%d"),
        "note": "The development perturbation set. A later change is a recorded decision in the plan's §4b, not an edit. "
                "The holdout manifest is frozen separately before the holdout opens (plan §3, ledger row 14).",
    }
    (RESULTS / "manifest_freeze.json").write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "measured_costs_s"}, indent=2))
    print(json.dumps(freeze, indent=2))


if __name__ == "__main__":
    main()
