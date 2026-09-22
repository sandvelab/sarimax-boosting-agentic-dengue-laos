#!/usr/bin/env python3
"""`/perturb plan`: enumerate the judgment calls, name a reasonable alternative for each, cost
it from measured run times, rank by expected informativeness, write the development
perturbation manifest -- and freeze it.

**Versions.** The manifest is planned *around the main path*: the tier-2 rows perturb the main
path's constants, and the main path is read from `04_stage2/claim.md`, never typed here.
Batch 11 planned v1 around `g_oosErrorBoosting` (rows without a suffix); batch 14 annotated
`h_levelOnlyBoosting` as the main path and this script now plans **v2 around it** (rows
suffixed `@h`). **v1's rows stay in the manifest, marked `superseded_by_v2`**, so that their
`results/<combination>/` directories remain named and the v1 report (batch 13) stays a true
record of g's stability; nothing from v1 is deleted or rewritten. A later change of main path
gets a v3 the same way.

**Three tiers**, so that the absence of a perturbation is always a visible decision:

- **Tier 1** -- the not-taken siblings of the main path, derived from the tree; `/validate
  invariants` (`combos`) refuses a manifest whose tier-1 rows disagree with the tree.
- **Tier 2** -- judgment calls that live as constants or code paths: stage 1's order and
  options, the training window and warm-up, the backtest scheme, and every constant of the
  main-path stage 2. Run by `03_run_combinations.py`, whose `main@h` gate must reproduce the
  main path's stored per-cell scores before any other row is trusted.
- **Tier 3** -- reasonable alternatives that need machinery not built; listed with the reason.

**Budget.** BUDGET_WALL_SECONDS is the provisional ceiling set in batch 11 (agent-autonomous,
revisable); costs come from `results/run_costs.csv`, and the manifest records where the
cumulative cost of the ranked rows crosses the ceiling.

**Freeze.** `results/manifest_freeze.json` records the manifest's sha256, the planning commit,
the date, and the digest and commit of the version it supersedes.

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
STAGE2_CLAIM = ANALYSIS / "04_stage2" / "claim.md"

BUDGET_WALL_SECONDS = 3600  # provisional ceiling on stability compute, agent-autonomous, revisable by the human
ROLLING_REFIT_EXTRA_SECONDS = 17 * 8 * 110 * 0.05  # provinces x splits x origins x one SARIMAX fit
TAG = {"g_oosErrorBoosting": "", "h_levelOnlyBoosting": "@h", "i_boundedBoosting": "@i", "j_levelOnlyBoundedBoosting": "@j"}


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    v = m.group(1).strip() if m else ""
    return None if v in ("", "-", "none") else v


def main_stage2() -> str:
    main = field(STAGE2_CLAIM.read_text(), "main-path")
    if main not in TAG:
        raise RuntimeError(f"no tier-2 specification is written for main path {main!r}; extend TAG and tier2()")
    return main


def tier1_from_tree(main: str) -> list[dict]:
    rows = []
    for claim in sorted(ANALYSIS.rglob("claim.md")):
        node = claim.parent
        text = claim.read_text()
        if field(text, "kind") != "alternatives":
            continue
        node_main = field(text, "main-path")
        for kid in sorted(p.name for p in node.iterdir() if p.is_dir() and (p / "claim.md").exists()):
            if kid == node_main:
                continue
            rows.append({"fork": str(node.relative_to(ROOT)), "child": kid,
                         "combination": f"{node.name}={kid}", "node": f"{node.relative_to(ROOT)}/{kid}"})
    return rows


def read_costs() -> dict[str, float]:
    with RUN_COSTS.open(newline="") as f:
        return {r["node"]: float(r["wall_seconds"]) for r in csv.DictReader(f)}


def tier2(costs: dict[str, float], main: str) -> list[dict]:
    """The perturbation rows around `main`. Written for h_levelOnlyBoosting (v2); the v1 rows
    around g are kept as superseded history by main(), not regenerated here."""
    tag = TAG[main]
    s2 = f"analysis/04_stage2/{main}"
    S1 = "analysis/02_stage1"
    t_m = costs[s2]
    t_s1 = costs[S1]
    # (combination, node, parameter, main_value, value, basis, rank, rank_reason, est_cost)
    spec = [
        ("stage1=airline_011x011", S1, "SARIMAX order", "(1,1,1)x(1,0,0,12)", "(0,1,1)x(0,1,1,12)",
         "the airline model is the standard seasonal default and differs in the seasonal component", 1,
         "changes the residual stage 2 corrects; in v1 it moved the margin most", t_s1 + t_m),
        ("stage1=nodiff_101x100", S1, "SARIMAX order", "(1,1,1)x(1,0,0,12)", "(1,0,1)x(1,0,0,12)",
         "d=1 was chosen without a unit-root test", 3, "the level effect stage 2 learns may be a differencing artefact", t_s1 + t_m),
        ("stage1=enforce_stationarity", S1, "enforce_stationarity/invertibility", "False/False", "True/True",
         "statsmodels' defaults; turned off in batch 2 for convergence", 8, "in v1 it moved the margin by 5 points", t_s1 + t_m),
        ("window=rolling_72m", S1, "training window", "expanding from 1998-01", "rolling, last 72 months",
         "forgets the 2003 epidemic and the pre-2008 reporting regime", 2, "in v1 the row with the weakest split agreement (3 of 8)", t_s1 + t_m),
        ("window=start_2002", S1, "training window start", "1998-01", "2002-01", "the zero-heavy early years", 4,
         "in v1 the second-smallest margin (-0.92%)", t_s1 + t_m),
        ("scheme=chap_default_7x1", "analysis/01_data/03_backtest_scheme", "n_splits/stride", "8/3", "7/1 (Chap's evaluate defaults)",
         "the scheme was reused from the prior project; Chap's own default is a different cell set", 4, "", t_s1 + t_m),
        ("modelable=36_months", "analysis/01_data/02_characterise", "min modelable months", "24", "36",
         "set once, unexamined; in v1 it changed nothing (every included province has >= 96 months)", 14, "", t_s1 + t_m),
        ("stage2=no_clip", s2, "CLIP_AT_ZERO", "True", "False", "a combination-rule choice", 9, "", t_m),
        ("stage2=zclip2", s2, "ZCLIP", "3", "2", "a tighter winsorisation bound", 5, "", t_m),
        ("stage2=zclip5", s2, "ZCLIP", "3", "5", "a looser bound", 7, "", t_m),
        ("stage2=no_winsorisation", s2, "ZCLIP", "3", "none", "the naive target", 6, "in v1 the third-smallest margin", t_m),
        ("stage2=scale_by_residual_rms", s2, "target standardisation", "stage 1 se", "province residual RMS",
         "the se inflates corrections where stage 1's spread is miscalibrated", 5, "", t_m),
        ("stage2=per_horizon", s2, "fitting", "one pooled model, horizon indicators", "one model per horizon",
         "the direct multi-step design", 4, "the horizon coupling the human asked to be sure of", t_m),
        ("stage2=bounded_floor0", s2, "correction bound", "none (j_levelOnlyBoundedBoosting is the floor-10 bound, tier 1)",
         "|correction| <= stage-1 mean, no floor", "the bound's floor was a judgment call", 6, "", t_m),
        ("stage2=plus_recent_and_incidence", s2, "features", "level-only", "add r_last, r_last3, cum12_anom, zero_frac24",
         "the features h dropped, added back without the cross-province term", 2, "says which dropped feature cost g its margin", t_m),
        ("stage2=plus_recent_and_cross", s2, "features", "level-only", "add r_last, r_last3, nat_last3",
         "the features h dropped, added back without the incidence terms", 3, "", t_m),
        ("stage2=full_plus_climate", s2, "features", "level-only", "g's full set plus lag-h climate anomalies",
         "the climate fork on the full input (v1: -5.78% around g)", 6, "", t_m),
        ("stage2=depth2", s2, "max_depth", "3", "2", "unsearched configuration", 7, "", t_m),
        ("stage2=depth4_300trees", s2, "max_depth/n_estimators", "3/150", "4/300", "unsearched configuration", 7, "", t_m),
        ("stage2=lr0.1", s2, "learning_rate", "0.05", "0.1", "unsearched configuration", 9, "", t_m),
        ("stage2=min_leaf50", s2, "min_samples_leaf", "20", "50", "unsearched configuration", 9, "", t_m),
        ("stage2=alt_seed", s2, "component seed", "component_seed('04_stage2/g_oosErrorBoosting')",
         "component_seed('04_stage2/g_oosErrorBoosting/alt')", "the seed is a judgment call", 5, "", t_m),
        ("stage2=warmup12", s2, "WARMUP_MONTHS", "24", "12", "set by judgment", 11, "", t_m),
        ("stage2=warmup36", s2, "WARMUP_MONTHS", "24", "36", "set by judgment", 11, "", t_m),
        ("stage2=rolling_refit_oos", s2, "in-window error construction", "parameters fixed", "true rolling refit at every origin",
         "the one approximation in the construction; in v1 the smallest margin (-0.70%)", 1,
         "the conservative reading of the margin", t_m + ROLLING_REFIT_EXTRA_SECONDS),
        ("stage2=min_train_rows1000", s2, "MIN_TRAIN_ROWS", "200", "1000", "never binds", 13, "", t_m),
    ]
    rows = []
    for combo, node, param, main_v, alt_v, basis, rank, why, cost in spec:
        rows.append({"combination": combo + tag, "tier": 2, "fork": "-", "child": "-", "node": node,
                     "parameter": param, "main_value": main_v, "value": alt_v, "basis": basis,
                     "informativeness_rank": rank, "rank_reason": why, "est_cost_s": round(cost, 1)})
    return rows


def tier3() -> list[dict]:
    spec = [
        ("stage1=log1p_transform", "analysis/02_stage1", "target transform", "raw counts", "log1p, bias-corrected back-transform",
         "the plan logged this fork in batch 2", "stage 1 is not repaired (human-set, 2026-09-21); would also need a verified CRPS on the transformed scale"),
        ("stage1=negative_binomial_family", "analysis/02_stage1", "predictive family", "Gaussian", "negative binomial or zero-truncated normal",
         "the coverage deficit is a heavy tail a Gaussian cannot carry", "stage 1 is not repaired (human-set, 2026-09-21); the most consequential fork not run"),
        ("stage2=multiplicative", "analysis/04_stage2", "combination rule", "additive", "multiplicative on the log scale",
         "Wang et al. (2013)", "undefined where stage 1's mean is near or below zero; needs a design decision"),
        ("stage2=enso_covariate", "analysis/04_stage2", "features", "dataset columns only", "add ONI/Nino3.4 at lags 3-6 months",
         "the literature's one climate signal with multi-month lead in Laos", "a new data acquisition and a governance decision; human call"),
        ("evaluation=chap_native", "analysis/00_metric", "harness", "native Python CRPS", "chap-core evaluation",
         "the prior project's route", "decided against in plan §4"),
    ]
    return [{"combination": c, "tier": 3, "fork": "-", "child": "-", "node": n, "parameter": p, "main_value": m,
             "value": v, "basis": b, "informativeness_rank": "-", "rank_reason": "", "est_cost_s": "-",
             "cumulative_cost_s": "-", "status": "not_run", "reason_if_not_run": r} for c, n, p, m, v, b, r in spec]


def superseded_rows(previous_manifest: Path, current_main: str) -> list[dict]:
    """v1's tier-2 rows, kept so their results directories stay named and the v1 report stays
    grounded; tier-1 and tier-3 rows of the previous version are regenerated, not kept."""
    if not previous_manifest.exists():
        return []
    with previous_manifest.open(newline="") as f:
        prev = list(csv.DictReader(f))
    out = []
    for r in prev:
        if r["tier"] != "2" or r["combination"].endswith(TAG[current_main]) and TAG[current_main]:
            continue
        r = dict(r)
        if r["status"] == "planned":
            r["status"] = "superseded_by_v2 (run in batch 12 around g_oosErrorBoosting; results kept)"
        out.append(r)
    return out


def render(rows: list[dict], fieldnames: list[str]) -> bytes:
    """The bytes the manifest would have, without touching the file."""
    import io
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode()


def diff_columns(current: bytes, replanned: bytes, fieldnames: list[str]) -> list[str]:
    """Which columns a re-plan would change. Rows are compared by combination, so a set that
    gained or lost a row shows up as the sentinel `<row set>` rather than as a column."""
    def table(b: bytes) -> dict[str, dict]:
        return {r["combination"]: r for r in csv.DictReader(b.decode().splitlines())}
    a, b = table(current), table(replanned)
    if set(a) != set(b):
        return ["<row set>"]
    return sorted({f for k in a for f in fieldnames if a[k].get(f) != b[k].get(f)})


def main() -> None:
    main = main_stage2()
    costs = read_costs()
    previous = superseded_rows(RESULTS / "manifest.csv", main)
    t1 = tier1_from_tree(main)
    for r in t1:
        r.update({"tier": 1, "parameter": "stage-2 family / input / combination rule (a node)", "main_value": main,
                  "value": r["child"], "basis": "a sibling built and scored in batches 4-14; its own claim.md holds the argument",
                  "informativeness_rank": 0, "rank_reason": "already run; results in the sibling's own results/",
                  "est_cost_s": round(costs.get(f"analysis/04_stage2/{r['child']}", 0.0), 1),
                  "status": "planned", "reason_if_not_run": "", "cumulative_cost_s": "-"})
    gate = [{"combination": "main" + TAG[main], "tier": 0, "fork": "-", "child": "-", "node": f"analysis/04_stage2/{main}",
             "parameter": "gate", "main_value": main, "value": "every parameter at its main-path value",
             "basis": "the runner must reproduce the main path's stored per-cell scores before any row is trusted",
             "informativeness_rank": "-", "rank_reason": "", "est_cost_s": round(costs[f"analysis/04_stage2/{main}"], 1),
             "cumulative_cost_s": "-", "status": "gate", "reason_if_not_run": ""}]
    t2 = tier2(costs, main)
    t2.sort(key=lambda r: (r["informativeness_rank"], r["combination"]))
    cumulative, line_index = 0.0, None
    for i, r in enumerate(t2):
        cumulative += r["est_cost_s"]
        r["cumulative_cost_s"] = round(cumulative, 1)
        r["status"] = "planned" if cumulative <= BUDGET_WALL_SECONDS else "below_budget_line"
        if r["status"] != "planned" and line_index is None:
            line_index = i
        r["reason_if_not_run"] = "" if r["status"] == "planned" else f"cumulative cost exceeds BUDGET_WALL_SECONDS={BUDGET_WALL_SECONDS}"
    t3 = tier3()

    fieldnames = ["combination", "tier", "fork", "child", "node", "parameter", "main_value", "value", "basis",
                  "informativeness_rank", "rank_reason", "est_cost_s", "cumulative_cost_s", "status", "reason_if_not_run"]
    rows = gate + t1 + t2 + t3 + previous
    old_freeze = json.loads((RESULTS / "manifest_freeze.json").read_text()) if (RESULTS / "manifest_freeze.json").exists() else None
    RESULTS.mkdir(exist_ok=True)

    # A frozen set is not rewritten by a re-run. `est_cost_s` is measured wall-clock, so
    # re-planning on a differently loaded machine changes the manifest's bytes while changing
    # nothing about what it plans -- and the digest in manifest_freeze.json would then be a
    # record of a file that no longer exists. Batch 16 found this while building the phase-E
    # freeze: every full run of analysis/run.sh silently moved the development set.
    # A new version is still planned, because that is a recorded decision, not a re-run: the
    # rewrite path is taken when there is no freeze yet, or when the tree's main path is no
    # longer the one the freeze was written for (batch 14's v1 -> v2).
    if old_freeze and (RESULTS / "manifest.csv").exists() and old_freeze.get("main_path") == main:
        current = (RESULTS / "manifest.csv").read_bytes()
        replanned = render(rows, fieldnames)
        check = {"checked_on": time.strftime("%Y-%m-%d"), "version": old_freeze.get("version"),
                 "main_path": main, "frozen_sha256": old_freeze.get("sha256"),
                 "current_sha256": hashlib.sha256(current).hexdigest(),
                 "still_the_frozen_file": hashlib.sha256(current).hexdigest() == old_freeze.get("sha256"),
                 "replanned_sha256": hashlib.sha256(replanned).hexdigest(),
                 "replanned_differs_only_in": diff_columns(current, replanned, fieldnames),
                 "note": "The frozen development set is not rewritten by a re-run. Differences "
                         "confined to est_cost_s/cumulative_cost_s are re-measured wall-clock and "
                         "change nothing the manifest plans; a difference anywhere else is a "
                         "change to the set and must be a recorded decision (plan §4b)."}
        (RESULTS / "manifest_freeze_check.json").write_text(json.dumps(check, indent=2) + "\n")
        print(json.dumps(check, indent=2))
        if not check["still_the_frozen_file"]:
            raise RuntimeError("manifest.csv no longer hashes to manifest_freeze.json's digest")
        beyond_cost = set(check["replanned_differs_only_in"]) - {"est_cost_s", "cumulative_cost_s"}
        if beyond_cost:
            raise RuntimeError(f"re-planning would change the frozen set beyond measured cost: "
                               f"{sorted(beyond_cost)}")
        return

    with (RESULTS / "manifest.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    manifest_bytes = (RESULTS / "manifest.csv").read_bytes()
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    summary = {
        "version": 2 if previous else 1, "main_path": main, "tag": TAG[main],
        "n_rows": len(rows), "n_gate": len(gate), "n_tier1": len(t1), "n_tier2_current": len(t2),
        "n_tier2_planned": sum(r["status"] == "planned" for r in t2),
        "n_tier2_below_budget_line": sum(r["status"] == "below_budget_line" for r in t2),
        "n_tier3_not_run": len(t3), "n_superseded_rows_kept": len(previous),
        "budget_wall_seconds": BUDGET_WALL_SECONDS,
        "planned_tier2_cost_s": round(sum(r["est_cost_s"] for r in t2 if r["status"] == "planned"), 1),
        "where_the_line_fell": ("below every tier-2 row: nothing planned is excluded for budget" if line_index is None
                                 else f"after ranked row {line_index} ({t2[line_index]['combination']})"),
        "measured_costs_s": costs,
        "run_design": (f"gate: run main{TAG[main]} and compare value for value with {main}'s stored per_cell_scores.csv; "
                       "tier 1: each sibling's own results; tier 2: 03_run_combinations.py recomputes stage 1 and the main-path "
                       "stage 2 under each row's settings into results/<combination>/; superseded rows are not re-run"),
    }
    (RESULTS / "manifest_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    freeze = {
        "frozen_file": "results/manifest.csv", "version": summary["version"], "main_path": main,
        "sha256": hashlib.sha256(manifest_bytes).hexdigest(), "rows": len(rows),
        "frozen_at_commit": head, "frozen_on": time.strftime("%Y-%m-%d"),
        "supersedes": ({k: old_freeze.get(k) for k in ("version", "sha256", "frozen_at_commit", "frozen_on", "main_path")}
                       if old_freeze else None),
        "note": "The development perturbation set. A later change is a recorded decision in the plan's §4b, not an edit; "
                "a change of main path produces a new version with the previous rows kept as superseded. The holdout "
                "manifest is frozen separately before the holdout opens (plan §3).",
    }
    (RESULTS / "manifest_freeze.json").write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "measured_costs_s"}, indent=2))
    print(json.dumps(freeze, indent=2))


if __name__ == "__main__":
    main()
