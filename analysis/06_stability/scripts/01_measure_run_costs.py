#!/usr/bin/env python3
"""Measure what one run of each existing model node costs, by running it.

`/perturb plan` asks for the compute cost of every perturbation. Rather than guess, this
script re-runs the main script of stage 1 and of every stage-2 candidate under the pinned
environment, times each, and records the wall-clock seconds to `results/run_costs.csv`. The
manifest planner (`02_plan_manifest.py`) reads that file to cost each planned combination --
no number is carried from a terminal.

A second thing falls out for free and is recorded too: every node's `results/` is hashed
before and after its re-run. Every one of these scripts is deterministic or seeded (Rule 6),
so a re-run must reproduce the committed outputs byte for byte; whether it does is written
per node (`all_outputs_identical`). A mismatch would be a finding, not something to fix here.

Run order matters for the stage-2 siblings whose compare scripts read each other's
`comparison.json` (c reads a-b; d reads a-c; e reads a-d; g reads a-f): stage 1 first, then
the alternatives in letter order. Nothing here reads the holdout.

Seeds: none drawn by this script; the seeded scripts it calls pin their own.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import time
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]  # analysis/06_stability
ANALYSIS = NODE.parents[0]
RESULTS = NODE / "results"

TARGETS = ["02_stage1"] + [f"04_stage2/{p.name}" for p in sorted((ANALYSIS / "04_stage2").iterdir())
                          if p.is_dir() and (p / "claim.md").exists()]


def digest_dir(d: Path) -> dict[str, str]:
    out = {}
    for f in sorted(d.rglob("*")):
        if f.is_file() and f.name != ".gitkeep":
            out[str(f.relative_to(d))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def main() -> None:
    rows = []
    for rel in TARGETS:
        node = ANALYSIS / rel
        before = digest_dir(node / "results")
        t0 = time.perf_counter()
        proc = subprocess.run(["bash", "run.sh"], cwd=node, capture_output=True, text=True)
        wall = time.perf_counter() - t0
        after = digest_dir(node / "results")
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        rows.append({
            "node": f"analysis/{rel}", "wall_seconds": round(wall, 2), "exit_code": proc.returncode,
            "n_result_files": len(after), "all_outputs_identical": bool(not changed),
            "changed_files": ";".join(changed),
        })
        if proc.returncode != 0:
            rows[-1]["stderr_tail"] = proc.stderr[-500:]

    RESULTS.mkdir(exist_ok=True)
    fieldnames = ["node", "wall_seconds", "exit_code", "n_result_files", "all_outputs_identical", "changed_files"]
    with (RESULTS / "run_costs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    summary = {
        "n_nodes_timed": len(rows),
        "total_wall_seconds": round(sum(r["wall_seconds"] for r in rows), 2),
        "all_exit_zero": all(r["exit_code"] == 0 for r in rows),
        "all_outputs_identical_on_rerun": all(r["all_outputs_identical"] for r in rows),
        "nodes_with_changed_outputs": [r["node"] for r in rows if not r["all_outputs_identical"]],
        "per_node": rows,
    }
    (RESULTS / "run_costs_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
