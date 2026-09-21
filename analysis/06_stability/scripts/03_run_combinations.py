#!/usr/bin/env python3
"""`/perturb run`: execute every planned tier-2 row of the frozen development manifest, around
the main path the manifest was planned for.

**Order of operations, and why.** (1) The manifest is re-hashed and compared with
`results/manifest_freeze.json`; a moved manifest stops the run. (2) The main path is read from
`04_stage2/claim.md` and must be the one the manifest was frozen for. (3) The gate row
(`main<tag>`: every parameter at its main-path value) is run first and compared value for
value with the main path's stored `per_cell_scores.csv` on the columns both carry; if it does
not reproduce the main path exactly, nothing else runs. (4) Every row with tier 2 and status
`planned` is mapped to its configuration (`COMBINATIONS` -- the manifest names a row, this
dictionary says what it means, and the run refuses a mismatch either way), run, and written
to `results/<combination>/`. Rows marked superseded are not re-run; their results stand.
(5) `results/run_log.csv` and `results/run_summary.json` record wall-clock per combination
and where the budget line fell.

**Versions.** v1 (batch 12) ran around `g_oosErrorBoosting` with unsuffixed names; v2 (batch
15) runs around `h_levelOnlyBoosting` with names suffixed `@h`. `MAIN_CONFIGS` gives each
main path's Stage2Config; every v2 row is that config with one change.

**Seeds**: gradient-boosted rows pin `random_state` to the main path's component seed (or the
alternative component for the seed row); everything else is deterministic.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
from dataclasses import replace
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/06_stability
ANALYSIS = NODE.parents[0]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.stage2_perturb import Stage1Config, SchemeConfig, Stage2Config, run_combination  # noqa: E402

RESULTS = NODE / "results"
DEV_CSV = ANALYSIS / "01_data" / "01_prepare" / "results" / "development.csv"
STAGE2_CLAIM = ANALYSIS / "04_stage2" / "claim.md"
COMPARE_COLUMNS = ["province", "split", "month", "h", "actual", "stage1_mean", "stage1_se",
                   "stage2_correction", "final_mean", "final_se", "crps"]

S1, SC = Stage1Config, SchemeConfig
TAG = {"g_oosErrorBoosting": "", "h_levelOnlyBoosting": "@h"}
MAIN_CONFIGS = {"g_oosErrorBoosting": Stage2Config(), "h_levelOnlyBoosting": Stage2Config(features="level_only")}


def gbm(**over):
    base = dict(n_estimators=150, max_depth=3, learning_rate=0.05, subsample=0.8, min_samples_leaf=20)
    base.update(over)
    return base


def combinations(main: str) -> dict[str, tuple[Stage1Config, SchemeConfig, Stage2Config]]:
    """Every row the manifest may name for `main`, as (stage 1, scheme, stage 2) configurations."""
    t = TAG[main]
    M = MAIN_CONFIGS[main]
    s2 = lambda **kw: replace(M, **kw)  # noqa: E731
    rows = {
        f"main{t}": (S1(), SC(), M),
        # stage 1 specification
        f"stage1=airline_011x011{t}": (S1(order=(0, 1, 1), seasonal_order=(0, 1, 1, 12)), SC(), M),
        f"stage1=nodiff_101x100{t}": (S1(order=(1, 0, 1)), SC(), M),
        f"stage1=enforce_stationarity{t}": (S1(enforce=True), SC(), M),
        # window, scheme, modelability
        f"window=rolling_72m{t}": (S1(window="rolling", window_months=72), SC(), M),
        f"window=start_2002{t}": (S1(window="start", window_start="2002-01"), SC(), M),
        f"scheme=chap_default_7x1{t}": (S1(), SC(n_splits=7, stride=1), M),
        f"modelable=36_months{t}": (S1(), SC(min_modelable_months=36), M),
        # hyperparameters, seed, error construction (same names in both versions)
        f"stage2=g_depth2{t}" if not t else f"stage2=depth2{t}": (S1(), SC(), s2(gbm_params=gbm(max_depth=2))),
        f"stage2=g_depth4_300trees{t}" if not t else f"stage2=depth4_300trees{t}": (S1(), SC(), s2(gbm_params=gbm(max_depth=4, n_estimators=300))),
        f"stage2=g_lr0.1{t}" if not t else f"stage2=lr0.1{t}": (S1(), SC(), s2(gbm_params=gbm(learning_rate=0.1))),
        f"stage2=g_min_leaf50{t}" if not t else f"stage2=min_leaf50{t}": (S1(), SC(), s2(gbm_params=gbm(min_samples_leaf=50))),
        f"stage2=g_alt_seed{t}" if not t else f"stage2=alt_seed{t}": (S1(), SC(), s2(seed_component="04_stage2/g_oosErrorBoosting/alt")),
        f"stage2=g_warmup12{t}" if not t else f"stage2=warmup12{t}": (S1(), SC(), s2(warmup=12)),
        f"stage2=g_warmup36{t}" if not t else f"stage2=warmup36{t}": (S1(), SC(), s2(warmup=36)),
        f"stage2=g_rolling_refit_oos{t}" if not t else f"stage2=rolling_refit_oos{t}": (S1(), SC(), s2(oos_mode="rolling_refit")),
        f"stage2=g_min_train_rows1000{t}" if not t else f"stage2=min_train_rows1000{t}": (S1(), SC(), s2(min_train_rows=1000)),
        f"stage2=g_no_clip{t}" if not t else f"stage2=no_clip{t}": (S1(), SC(), s2(clip_at_zero=False)),
        f"stage2=g_zclip2{t}" if not t else f"stage2=zclip2{t}": (S1(), SC(), s2(zclip=2.0)),
        f"stage2=g_zclip5{t}" if not t else f"stage2=zclip5{t}": (S1(), SC(), s2(zclip=5.0)),
        f"stage2=g_no_winsorisation{t}" if not t else f"stage2=no_winsorisation{t}": (S1(), SC(), s2(zclip=None)),
        f"stage2=g_scale_by_residual_rms{t}" if not t else f"stage2=scale_by_residual_rms{t}": (S1(), SC(), s2(standardise="resid_rms")),
        f"stage2=g_per_horizon{t}" if not t else f"stage2=per_horizon{t}": (S1(), SC(), s2(per_horizon=True)),
    }
    if not t:  # v1-only rows, around g
        rows.update({
            "stage2=g_bounded_correction": (S1(), SC(), s2(bounded_correction=True)),
            "stage2=g_no_cross_province": (S1(), SC(), s2(features="no_cross_province")),
            "stage2=g_no_incidence_terms": (S1(), SC(), s2(features="no_incidence")),
            "stage2=g_level_month_horizon_only": (S1(), SC(), s2(features="level_only")),
            "stage2=g_with_climate_anomalies": (S1(), SC(), s2(features="with_climate")),
            "stage2=f_alpha1": (S1(), SC(), s2(family="ridge", ridge_alpha=1.0)),
            "stage2=f_alpha100": (S1(), SC(), s2(family="ridge", ridge_alpha=100.0)),
        })
    else:  # v2 rows around h: the bound without its floor, and the dropped feature groups added back
        rows.update({
            f"stage2=bounded_floor0{t}": (S1(), SC(), s2(bounded_correction=True, bound_floor=0.0)),
            f"stage2=plus_recent_and_incidence{t}": (S1(), SC(), s2(features="no_cross_province")),
            f"stage2=plus_recent_and_cross{t}": (S1(), SC(), s2(features="no_incidence")),
            f"stage2=full_plus_climate{t}": (S1(), SC(), s2(features="with_climate")),
        })
    return rows


def write_combination(name: str, per_cell: list[dict], conclusion: dict) -> None:
    out = RESULTS / name
    out.mkdir(parents=True, exist_ok=True)
    fields = ["province", "split", "month", "h", "actual", "stage1_mean", "stage1_se", "stage2_correction",
              "final_mean", "final_se", "crps_stage1", "crps", "fit_failed", "error"]
    with (out / "per_cell_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(per_cell)
    (out / "conclusion.json").write_text(json.dumps({"combination": name, **conclusion}, indent=2) + "\n")


def compare_with_main_path(per_cell: list[dict], main_cells: Path) -> dict:
    with main_cells.open(newline="") as f:
        ref = list(csv.DictReader(f))
    ours = [{k: ("" if r[k] is None else str(r[k])) for k in COMPARE_COLUMNS} for r in per_cell]
    theirs = [{k: r[k] for k in COMPARE_COLUMNS} for r in ref]
    mismatches = [(i, k, a[k], b[k]) for i, (a, b) in enumerate(zip(ours, theirs)) for k in COMPARE_COLUMNS if a[k] != b[k]]
    return {"compared_with": str(main_cells.relative_to(ANALYSIS.parent)), "n_rows_ours": len(ours),
            "n_rows_main_path": len(theirs), "n_mismatched_values": len(mismatches),
            "identical_on_shared_columns": bool(len(ours) == len(theirs) and not mismatches), "first_mismatches": mismatches[:5]}


def main() -> None:
    freeze = json.loads((RESULTS / "manifest_freeze.json").read_text())
    if hashlib.sha256((RESULTS / "manifest.csv").read_bytes()).hexdigest() != freeze["sha256"]:
        raise RuntimeError("manifest.csv does not hash to the frozen digest -- the set has moved; refusing to run")
    m = re.search(r"^main-path:\s*(\S+)", STAGE2_CLAIM.read_text(), re.M)
    main_path = m.group(1) if m else None
    if main_path != freeze.get("main_path", "g_oosErrorBoosting"):
        raise RuntimeError(f"the tree's main path is {main_path!r} but the manifest was frozen for {freeze.get('main_path')!r}")
    tag = TAG[main_path]
    combos = combinations(main_path)
    with (RESULTS / "manifest.csv").open(newline="") as f:
        manifest = list(csv.DictReader(f))
    planned = [r["combination"] for r in manifest if r["tier"] == "2" and r["status"] == "planned"]
    missing = [c for c in planned if c not in combos]
    extra = [c for c in combos if c != f"main{tag}" and c not in planned]
    if missing or extra:
        raise RuntimeError(f"manifest/runner disagree: rows without configuration {missing}; configurations without row {extra}")

    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    main_cells = ANALYSIS / "04_stage2" / main_path / "results" / "per_cell_scores.csv"

    log = []
    t0 = time.perf_counter()
    per_cell, conclusion = run_combination(dev_rows, *combos[f"main{tag}"])
    gate = compare_with_main_path(per_cell, main_cells)
    conclusion["verification_vs_main_path"] = gate
    write_combination(f"main{tag}", per_cell, conclusion)
    log.append({"combination": f"main{tag}", "status": "gate", "wall_seconds": round(time.perf_counter() - t0, 1),
                "two_stage_mean_crps": conclusion["two_stage"]["mean_crps"]})
    if not gate["identical_on_shared_columns"]:
        raise RuntimeError(f"the runner does not reproduce the main path: {gate}")

    for name in planned:
        t0 = time.perf_counter()
        per_cell, conclusion = run_combination(dev_rows, *combos[name])
        write_combination(name, per_cell, conclusion)
        log.append({"combination": name, "status": "run", "wall_seconds": round(time.perf_counter() - t0, 1),
                    "two_stage_mean_crps": conclusion["two_stage"]["mean_crps"]})
        print(f"{name:42s} {log[-1]['wall_seconds']:7.1f}s  stage1 {conclusion['stage1_alone']['mean_crps']:.3f}  "
              f"two-stage {conclusion['two_stage']['mean_crps']:.3f}  ({conclusion['pct_change_vs_stage1']:+.2f}%)  "
              f"cov {conclusion['stage1_alone']['coverage_90']:.3f}->{conclusion['two_stage']['coverage_90']:.3f}", flush=True)

    with (RESULTS / "run_log.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["combination", "status", "wall_seconds", "two_stage_mean_crps"], lineterminator="\n")
        w.writeheader()
        w.writerows(log)
    summary = {"version": freeze.get("version", 1), "main_path": main_path, "n_planned": len(planned),
               "n_run": sum(1 for r in log if r["status"] == "run"),
               "total_wall_seconds": round(sum(r["wall_seconds"] for r in log), 1), "gate": gate}
    (RESULTS / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
