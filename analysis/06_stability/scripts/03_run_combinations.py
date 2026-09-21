#!/usr/bin/env python3
"""`/perturb run`: execute every planned tier-2 row of the frozen development manifest.

**Order of operations, and why.** (1) The manifest is re-hashed and compared with
`results/manifest_freeze.json`; a moved manifest stops the run. (2) The `main` combination --
every parameter at its main-path value -- is run first and compared value for value with
`04_stage2/g_oosErrorBoosting/results/per_cell_scores.csv` on the columns both carry; if it
does not reproduce the main path exactly, nothing else runs. That gate is what lets a reader
trust that a perturbation's difference from the main path is the perturbation and not the
runner. (3) Every row with status `planned` and tier 2 is mapped to its configuration
(`COMBINATIONS` below -- the manifest names a row, this dictionary says what it means, and
the run refuses a manifest row without a configuration or a configuration without a row),
run, and written to `results/<combination>/per_cell_scores.csv` and `conclusion.json`.
(4) `results/run_log.csv` records wall-clock per combination and whether it ran, so where the
budget line actually fell is a file, not a recollection.

Tier-1 rows are not run here: their results are their own nodes' (`01_measure_run_costs.py`
re-ran them all, byte-identically). `04_collect_conclusions.py` gathers everything.

**Seeds**: the gradient-boosted combinations pin `random_state` to the component seed of the
main path (or, for the seed perturbation, to a different derived component); every other
step is deterministic.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/06_stability
ANALYSIS = NODE.parents[0]
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.stage2_perturb import Stage1Config, SchemeConfig, Stage2Config, run_combination  # noqa: E402

RESULTS = NODE / "results"
DEV_CSV = ANALYSIS / "01_data" / "01_prepare" / "results" / "development.csv"
MAIN_CELLS = ANALYSIS / "04_stage2" / "g_oosErrorBoosting" / "results" / "per_cell_scores.csv"
COMPARE_COLUMNS = ["province", "split", "month", "h", "actual", "stage1_mean", "stage1_se",
                   "stage2_correction", "final_mean", "final_se", "crps"]

S1, SC, S2 = Stage1Config, SchemeConfig, Stage2Config


def gbm(**over):
    base = dict(n_estimators=150, max_depth=3, learning_rate=0.05, subsample=0.8, min_samples_leaf=20)
    base.update(over)
    return base


COMBINATIONS: dict[str, tuple[Stage1Config, SchemeConfig, Stage2Config]] = {
    "main": (S1(), SC(), S2()),
    # stage 1 specification
    "stage1=airline_011x011": (S1(order=(0, 1, 1), seasonal_order=(0, 1, 1, 12)), SC(), S2()),
    "stage1=nodiff_101x100": (S1(order=(1, 0, 1)), SC(), S2()),
    "stage1=enforce_stationarity": (S1(enforce=True), SC(), S2()),
    # window, scheme, modelability
    "window=rolling_72m": (S1(window="rolling", window_months=72), SC(), S2()),
    "window=start_2002": (S1(window="start", window_start="2002-01"), SC(), S2()),
    "scheme=chap_default_7x1": (S1(), SC(n_splits=7, stride=1), S2()),
    "modelable=36_months": (S1(), SC(min_modelable_months=36), S2()),
    # stage 2 target and combination rule
    "stage2=g_no_clip": (S1(), SC(), S2(clip_at_zero=False)),
    "stage2=g_zclip2": (S1(), SC(), S2(zclip=2.0)),
    "stage2=g_zclip5": (S1(), SC(), S2(zclip=5.0)),
    "stage2=g_no_winsorisation": (S1(), SC(), S2(zclip=None)),
    "stage2=g_scale_by_residual_rms": (S1(), SC(), S2(standardise="resid_rms")),
    "stage2=g_bounded_correction": (S1(), SC(), S2(bounded_correction=True)),
    "stage2=g_per_horizon": (S1(), SC(), S2(per_horizon=True)),
    # stage 2 features
    "stage2=g_no_cross_province": (S1(), SC(), S2(features="no_cross_province")),
    "stage2=g_no_incidence_terms": (S1(), SC(), S2(features="no_incidence")),
    "stage2=g_level_month_horizon_only": (S1(), SC(), S2(features="level_only")),
    "stage2=g_with_climate_anomalies": (S1(), SC(), S2(features="with_climate")),
    # stage 2 family hyperparameters and seed
    "stage2=g_depth2": (S1(), SC(), S2(gbm_params=gbm(max_depth=2))),
    "stage2=g_depth4_300trees": (S1(), SC(), S2(gbm_params=gbm(max_depth=4, n_estimators=300))),
    "stage2=g_lr0.1": (S1(), SC(), S2(gbm_params=gbm(learning_rate=0.1))),
    "stage2=g_min_leaf50": (S1(), SC(), S2(gbm_params=gbm(min_samples_leaf=50))),
    "stage2=g_alt_seed": (S1(), SC(), S2(seed_component="04_stage2/g_oosErrorBoosting/alt")),
    "stage2=f_alpha1": (S1(), SC(), S2(family="ridge", ridge_alpha=1.0)),
    "stage2=f_alpha100": (S1(), SC(), S2(family="ridge", ridge_alpha=100.0)),
    # how the training errors are made
    "stage2=g_warmup12": (S1(), SC(), S2(warmup=12)),
    "stage2=g_warmup36": (S1(), SC(), S2(warmup=36)),
    "stage2=g_rolling_refit_oos": (S1(), SC(), S2(oos_mode="rolling_refit")),
    "stage2=g_min_train_rows1000": (S1(), SC(), S2(min_train_rows=1000)),
}


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


def compare_with_main_path(per_cell: list[dict]) -> dict:
    """Value-for-value comparison with g_oosErrorBoosting's stored per-cell file on the columns
    both carry (line endings differ by construction, so bytes are not compared)."""
    with MAIN_CELLS.open(newline="") as f:
        ref = list(csv.DictReader(f))
    ours = [{k: ("" if r[k] is None else str(r[k])) for k in COMPARE_COLUMNS} for r in per_cell]
    theirs = [{k: r[k] for k in COMPARE_COLUMNS} for r in ref]
    mismatches = [(i, k, a[k], b[k]) for i, (a, b) in enumerate(zip(ours, theirs)) for k in COMPARE_COLUMNS if a[k] != b[k]]
    return {"n_rows_ours": len(ours), "n_rows_main_path": len(theirs), "n_mismatched_values": len(mismatches),
            "identical_on_shared_columns": bool(len(ours) == len(theirs) and not mismatches),
            "first_mismatches": mismatches[:5]}


def main() -> None:
    freeze = json.loads((RESULTS / "manifest_freeze.json").read_text())
    manifest_bytes = (RESULTS / "manifest.csv").read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != freeze["sha256"]:
        raise RuntimeError("manifest.csv does not hash to the frozen digest -- the set has moved; refusing to run")
    with (RESULTS / "manifest.csv").open(newline="") as f:
        manifest = list(csv.DictReader(f))
    planned = [r["combination"] for r in manifest if r["tier"] == "2" and r["status"] == "planned"]
    missing = [c for c in planned if c not in COMBINATIONS]
    extra = [c for c in COMBINATIONS if c != "main" and c not in planned]
    if missing or extra:
        raise RuntimeError(f"manifest/runner disagree: rows without configuration {missing}; configurations without row {extra}")

    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))

    log = []
    t0 = time.perf_counter()
    per_cell, conclusion = run_combination(dev_rows, *COMBINATIONS["main"])
    gate = compare_with_main_path(per_cell)
    conclusion["verification_vs_main_path"] = gate
    write_combination("main", per_cell, conclusion)
    log.append({"combination": "main", "status": "run", "wall_seconds": round(time.perf_counter() - t0, 1),
                "two_stage_mean_crps": conclusion["two_stage"]["mean_crps"]})
    if not gate["identical_on_shared_columns"]:
        (RESULTS / "run_log.csv").write_text("gate failed\n")
        raise RuntimeError(f"the runner does not reproduce the main path: {gate}")

    for name in planned:
        t0 = time.perf_counter()
        per_cell, conclusion = run_combination(dev_rows, *COMBINATIONS[name])
        write_combination(name, per_cell, conclusion)
        log.append({"combination": name, "status": "run", "wall_seconds": round(time.perf_counter() - t0, 1),
                    "two_stage_mean_crps": conclusion["two_stage"]["mean_crps"]})
        print(f"{name:40s} {log[-1]['wall_seconds']:7.1f}s  stage1 {conclusion['stage1_alone']['mean_crps']:.3f}  "
              f"two-stage {conclusion['two_stage']['mean_crps']:.3f}  ({conclusion['pct_change_vs_stage1']:+.2f}%)  "
              f"cov {conclusion['stage1_alone']['coverage_90']:.3f}->{conclusion['two_stage']['coverage_90']:.3f}", flush=True)

    with (RESULTS / "run_log.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["combination", "status", "wall_seconds", "two_stage_mean_crps"], lineterminator="\n")
        w.writeheader()
        w.writerows(log)
    summary = {"n_planned": len(planned), "n_run": sum(1 for r in log if r["status"] == "run" and r["combination"] != "main"),
               "total_wall_seconds": round(sum(r["wall_seconds"] for r in log), 1),
               "budget_wall_seconds": None, "gate": gate}
    (RESULTS / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
