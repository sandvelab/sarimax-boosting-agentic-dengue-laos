#!/usr/bin/env python3
"""Phase E: open the held-out year, once, and run exactly the frozen set.

**This is the only script in the repository that reads a case value from 2010.** Everything it
executes was written and gated in batch 16, before the file was opened; what this script adds is
the file. It refuses to start unless all four of these hold:

1. `results/manifest_holdout.csv` hashes to the digest in `results/holdout_freeze.json` -- the
   set has not moved since it was frozen;
2. `results/holdout_runner_verification.json` hashes to the digest the freeze recorded for it,
   and records three identical reproductions of stored development results -- the machinery is
   the machinery that was gated;
3. `01_data/01_prepare/results/holdout.csv` hashes to the digest the freeze recorded -- the file
   being opened is the file that was sealed;
4. every planned row has an executable configuration in `lib/holdout_eval.holdout_combinations()`
   and every configuration has a planned row.

**The opening is recorded.** `results/run_status_holdout.csv` is appended to, never overwritten:
one row per opening, with the date, the commit, the digests of the set and of the sealed file,
and how many rows ran. Plan §3 asks that a second opening be recorded if it happens, and this is
where it would appear -- as a second row, not as a silently replaced first one. A working-tree
marker (`.holdout_opened`, gitignored) says whether *this* tree has opened the year; it is not
versioned, because a versioned seal would seal every clone and stop `analysis/run.sh` from
reproducing phase E from nothing.

Nothing here decides anything. The rows are frozen, the reporting rule is frozen, and the
scripts that collect and report read files this one writes.

Seeds: the gradient-boosted rows seed `random_state` from the project seed inside
`lib.stage2_perturb.make_model`, unchanged from development.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/06_stability
ANALYSIS = NODE.parents[0]
ROOT = ANALYSIS.parent
sys.path.insert(0, str(ANALYSIS / "scripts"))
from lib.holdout_eval import holdout_combinations, run_row  # noqa: E402

RESULTS = NODE / "results"
MANIFEST = RESULTS / "manifest_holdout.csv"
FREEZE = RESULTS / "holdout_freeze.json"
VERIFICATION = RESULTS / "holdout_runner_verification.json"
STATUS = RESULTS / "run_status_holdout.csv"
MARKER = NODE / ".holdout_opened"
PREPARE = ANALYSIS / "01_data" / "01_prepare" / "results"
DEV_CSV = PREPARE / "development.csv"
HOLDOUT_CSV = PREPARE / "holdout.csv"

TWO_STAGE_FIELDS = ["province", "split", "month", "h", "actual", "stage1_mean", "stage1_se",
                    "stage2_correction", "final_mean", "final_se", "crps_stage1", "crps",
                    "fit_failed", "error"]
BASELINE_FIELDS = ["province", "split", "month", "actual", "forecast_mean", "forecast_se",
                   "crps", "fit_failed", "error"]
STATUS_FIELDS = ["opened_on", "opened_at_commit", "manifest_sha256", "holdout_csv_sha256",
                 "n_rows_planned", "n_rows_run", "wall_seconds", "opening_number", "note"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight() -> tuple[dict, list[str]]:
    """The four refusals, all of them before a single holdout byte is parsed."""
    freeze = json.loads(FREEZE.read_text())
    frozen = freeze["frozen_inputs"]

    if digest(MANIFEST) != frozen["results/manifest_holdout.csv"]:
        raise RuntimeError("manifest_holdout.csv does not hash to the frozen digest -- the "
                           "phase-E set has moved since it was frozen; refusing to open the year")
    if digest(VERIFICATION) != frozen["results/holdout_runner_verification.json"]:
        raise RuntimeError("holdout_runner_verification.json does not hash to the digest the "
                           "freeze recorded -- the gate is not the gate that was passed")
    verification = json.loads(VERIFICATION.read_text())
    if not verification["all_reproductions_identical"]:
        raise RuntimeError("the gate does not record three identical reproductions of the stored "
                           "development results; refusing to open the year")
    if digest(HOLDOUT_CSV) != frozen["analysis/01_data/01_prepare/results/holdout.csv"]:
        raise RuntimeError("holdout.csv does not hash to the digest recorded at the freeze -- the "
                           "file being opened is not the file that was sealed")

    with MANIFEST.open(newline="") as f:
        manifest = list(csv.DictReader(f))
    planned = [r["combination"] for r in manifest if r["status"] == "planned"]
    combos = holdout_combinations()
    missing = [c for c in planned if c not in combos]
    extra = [c for c in combos if c not in planned]
    if missing or extra:
        raise RuntimeError(f"manifest/runner disagree: rows without a configuration {missing}; "
                           f"configurations without a planned row {extra}")
    return freeze, planned


def write_combination(name: str, per_cell: list[dict], conclusion: dict, baseline: bool) -> None:
    out = RESULTS / name
    out.mkdir(parents=True, exist_ok=True)
    fields = BASELINE_FIELDS if baseline else TWO_STAGE_FIELDS
    with (out / "per_cell_scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(per_cell)
    (out / "conclusion.json").write_text(json.dumps({"combination": name, **conclusion}, indent=2) + "\n")


def record_opening(freeze: dict, n_planned: int, n_run: int, wall: float) -> int:
    """Append one row per opening. A second opening is a second row, never a replacement."""
    existing = []
    if STATUS.exists():
        with STATUS.open(newline="") as f:
            existing = list(csv.DictReader(f))
    n = len(existing) + 1
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    note = ("the single opening the plan allows" if n == 1 else
            "a SECOND opening of the held-out year -- plan §3 requires this be visible; "
            "the reason belongs in the plan's §4b")
    existing.append({"opened_on": time.strftime("%Y-%m-%d %H:%M:%S"), "opened_at_commit": head,
                     "manifest_sha256": freeze["sha256"],
                     "holdout_csv_sha256": freeze["frozen_inputs"]["analysis/01_data/01_prepare/results/holdout.csv"],
                     "n_rows_planned": n_planned, "n_rows_run": n_run,
                     "wall_seconds": round(wall, 1), "opening_number": n, "note": note})
    with STATUS.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=STATUS_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(existing)
    MARKER.write_text(f"opened {time.strftime('%Y-%m-%d %H:%M:%S')} at {head}, opening {n}\n")
    return n


def main() -> None:
    freeze, planned = preflight()
    combos = holdout_combinations()

    # Everything above this line ran without reading a case value from 2010.
    with DEV_CSV.open(newline="") as f:
        dev_rows = list(csv.DictReader(f))
    with HOLDOUT_CSV.open(newline="") as f:
        holdout_rows = list(csv.DictReader(f))
    all_rows = dev_rows + holdout_rows

    log, t_all = [], time.perf_counter()
    for name in planned:
        t0 = time.perf_counter()
        per_cell, conclusion = run_row(name, all_rows, dev_rows)
        baseline = combos[name][0] == "baseline"
        write_combination(name, per_cell, conclusion, baseline)
        entry = {"combination": name, "status": "run", "wall_seconds": round(time.perf_counter() - t0, 1),
                 "mean_crps": conclusion["mean_crps"] if baseline else conclusion["two_stage"]["mean_crps"],
                 "n_cells_scored": conclusion["n_cells_scored"]}
        log.append(entry)
        if baseline:
            print(f"{name:48s} {entry['wall_seconds']:7.1f}s  mean CRPS {entry['mean_crps']:.3f}  "
                  f"cov {conclusion['coverage_90']:.3f}  ({entry['n_cells_scored']} cells)", flush=True)
        else:
            print(f"{name:48s} {entry['wall_seconds']:7.1f}s  stage1 {conclusion['stage1_alone']['mean_crps']:.3f}  "
                  f"two-stage {conclusion['two_stage']['mean_crps']:.3f}  ({conclusion['pct_change_vs_stage1']:+.2f}%)  "
                  f"cov {conclusion['stage1_alone']['coverage_90']:.3f}->{conclusion['two_stage']['coverage_90']:.3f}",
                  flush=True)
    wall = time.perf_counter() - t_all

    with (RESULTS / "run_log_holdout.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["combination", "status", "wall_seconds", "mean_crps",
                                          "n_cells_scored"], lineterminator="\n")
        w.writeheader()
        w.writerows(log)
    opening = record_opening(freeze, len(planned), len(log), wall)
    summary = {"phase": "E", "opening_number": opening, "main_path": freeze["main_path"],
               "manifest_sha256": freeze["sha256"], "frozen_at_commit": freeze["frozen_at_commit"],
               "n_planned": len(planned), "n_run": len(log),
               "total_wall_seconds": round(wall, 1),
               "estimated_wall_seconds": json.loads((RESULTS / "manifest_holdout_summary.json").read_text())["planned_cost_s"],
               "preflight": {"manifest_matches_freeze": True, "gate_matches_freeze": True,
                             "holdout_file_matches_seal": True, "rows_all_executable": True}}
    (RESULTS / "run_summary_holdout.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
