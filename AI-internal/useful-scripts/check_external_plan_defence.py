"""Put four situations to `plan_external.py` and see which it reports and which it refuses.

Batch 20's external plan carries an estimate built from a **measured wall-clock duration** —
the seconds the held-out `main` row took, read from
`05_stability/results/run_status_holdout.csv`. That file is rewritten by every run of
`05_stability/run.sh`, which on `analysis/run.sh` is the step immediately before this node.
So a planning script that recomputed itself would come back from a clean checkout with a
different estimate, and the claim that the plan was committed before the rows ran would be a
claim about a file that had since been rewritten. It is the fourth time this project has had
to separate a recorded decision from a derivation over values that do not reproduce: batch
24's frozen manifest, batch 26's tier-1 order and tier-2 selection, batch 30's frozen
development figure, and this.

The split is the one those three arrived at, and this checks that it holds:

| situation | expected |
|---|---|
| the record as committed | exit 0, rows verified, nothing rewritten |
| the cost unit has drifted — the holdout row's duration changed | exit 0, the drift **reported**, the manifest byte-identical |
| a row's structural field has moved — the cell count changed | **exit non-zero**, nothing written |
| the record is absent | exit 0, the plan **written** from today's inputs |

The drifted unit is not synthetic where it need not be: batch 31's clean-room run recorded
its own duration for `main__holdout` (7 394 s over the 32 holdout rows, against the archive's
run), and the scenario uses a duration of that kind rather than an invented one.

## How it runs, and why it touches the live tree

Each scenario swaps one *tracked* input or moves the record aside, invokes the node script,
records what happened, and restores from git — and the restore is unconditional, so an
exception still leaves the tree as it was found. The node script is invoked under
`environment/chapenv`, because a node's scripts are part of the pinned analysis whatever they
import (AGENTS.md §8); this harness runs under `.venv`.

Usage:
  .venv/bin/python AI-internal/useful-scripts/check_external_plan_defence.py --root .
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

NODE = "analysis/06_external"
SCRIPT = f"{NODE}/scripts/plan_external.py"
MANIFEST = f"{NODE}/results/manifest_external.csv"
PLAN = f"{NODE}/results/external_plan.json"
CHECK = f"{NODE}/results/external_plan_check.json"
STATUS = "analysis/05_stability/results/run_status_holdout.csv"

TRACKED = [MANIFEST, PLAN, STATUS]


def sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def restore(root: Path) -> None:
    """Put every tracked file this harness may touch back to HEAD, unconditionally."""
    subprocess.run(["git", "-C", str(root), "checkout", "--", *TRACKED, CHECK],
                   capture_output=True)


def run_script(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(root / "environment/chapenv/bin/python"), "scripts/plan_external.py"],
        cwd=root / NODE, capture_output=True, text=True)


def scenario_unchanged(root: Path) -> dict:
    """The record as committed. Nothing should be rewritten."""
    before = sha256(root / MANIFEST)
    proc = run_script(root)
    after = sha256(root / MANIFEST)
    check = json.loads((root / CHECK).read_text()) if (root / CHECK).exists() else {}
    return {
        "expected": "exit 0, rows verified, manifest byte-identical",
        "returncode": proc.returncode,
        "manifest_unchanged": before == after,
        "rows_agree": check.get("rows_agree"),
        "estimates_that_drifted": check.get("estimates_that_drifted"),
        "passes": (proc.returncode == 0 and before == after
                   and check.get("rows_agree") is True
                   and check.get("estimates_that_drifted") == 0),
        "stdout_tail": proc.stdout.strip().split("\n")[0] if proc.stdout else "",
    }


def scenario_unit_drifted(root: Path) -> dict:
    """The holdout `main` row took a different number of seconds, as a re-run makes it.

    The estimate the plan carries is that duration divided by 192 cells and multiplied by
    each row's cells. Changing it is exactly what `05_stability/run.sh` does one step
    earlier on every run, so this is the ordinary case and not the exotic one.
    """
    path = root / STATUS
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    original = None
    for row in rows:
        if row["combination"] == "main__holdout":
            original = row["seconds"]
            # Batch 31's clean-room run took a different duration for the same row; this
            # is a change of that size and direction rather than an invented one.
            row["seconds"] = f"{float(row['seconds']) * 1.32:.1f}"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    before = sha256(root / MANIFEST)
    proc = run_script(root)
    after = sha256(root / MANIFEST)
    check = json.loads((root / CHECK).read_text()) if (root / CHECK).exists() else {}
    return {
        "expected": "exit 0, the drift reported, manifest byte-identical",
        "holdout_main_seconds": {"recorded": original,
                                 "made_to_read": f"{float(original) * 1.32:.1f}"},
        "returncode": proc.returncode,
        "manifest_unchanged": before == after,
        "rows_agree": check.get("rows_agree"),
        "estimates_that_drifted": check.get("estimates_that_drifted"),
        "passes": (proc.returncode == 0 and before == after
                   and check.get("rows_agree") is True
                   and check.get("estimates_that_drifted") == 4),
    }


def scenario_row_moved(root: Path) -> dict:
    """A structural field has moved: the recorded plan names a cell count this tree denies.

    This is the case that must be fatal. A plan whose rows no longer describe what the tree
    would run is not a plan that was committed before the run; it is a different plan
    wearing that claim.
    """
    path = root / MANIFEST
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    for row in rows:
        if row["combination"] == "main__tha":
            row["cells"] = str(int(row["cells"]) + 1)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    before = sha256(path)
    proc = run_script(root)
    after = sha256(path)
    return {
        "expected": "exit non-zero, nothing written",
        "returncode": proc.returncode,
        "manifest_unchanged": before == after,
        "message_names_the_field": "main__tha.cells" in (proc.stdout + proc.stderr),
        "passes": (proc.returncode != 0 and before == after
                   and "main__tha.cells" in (proc.stdout + proc.stderr)),
    }


def scenario_from_cold(root: Path) -> dict:
    """No record at all — a first run. The plan is written, and it is the same plan."""
    recorded = (root / MANIFEST).read_bytes()
    (root / MANIFEST).unlink()
    (root / PLAN).unlink()
    proc = run_script(root)
    written = (root / MANIFEST).read_bytes() if (root / MANIFEST).exists() else b""
    return {
        "expected": "exit 0, the plan written",
        "returncode": proc.returncode,
        "manifest_written": bool(written),
        # The estimate is a measured duration and `run_status_holdout.csv` is at HEAD here,
        # so a first run from this tree reproduces the recorded plan exactly. From a tree
        # whose stability half had re-run, it would not, and that is the whole reason the
        # record exists.
        "identical_to_the_record": written == recorded,
        "passes": proc.returncode == 0 and written == recorded,
    }


SCENARIOS = {
    "the_record_as_committed": scenario_unchanged,
    "the_cost_unit_drifted": scenario_unit_drifted,
    "a_structural_row_moved": scenario_row_moved,
    "no_record_at_all": scenario_from_cold,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--out",
                        default="AI-generated/validation/26-09-04_externalPlanDefence.json")
    a = parser.parse_args()
    root = Path(a.root).resolve()

    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--",
                            *TRACKED], capture_output=True, text=True).stdout.strip()
    if dirty:
        print("refusing to run: the files every scenario restores from git have "
              f"uncommitted changes:\n{dirty}")
        return 2

    results = {}
    try:
        for name, scenario in SCENARIOS.items():
            try:
                results[name] = scenario(root)
            finally:
                restore(root)
            print(f"  {'pass' if results[name]['passes'] else 'FAIL'}  {name}")
    finally:
        restore(root)

    out = {
        "what_this_is": (
            "four situations put to analysis/06_external/scripts/plan_external.py, which "
            "records its plan once and verifies it thereafter. The rows are structural and "
            "a change to them is fatal; the estimate is a measured wall-clock duration and "
            "a change to it is reported"),
        "script": SCRIPT,
        "scenarios": results,
        "all_passed": all(r["passes"] for r in results.values()),
    }
    (root / a.out).write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nall passed: {out['all_passed']}  -> {a.out}")
    return 0 if out["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
