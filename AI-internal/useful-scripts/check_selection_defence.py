"""Put batch 25's failure back to the fixed `plan_manifest.py` and see what it does now.

Batch 25's clean-room run of `analysis/run.sh` exited 1 at the freeze check. Two things the
development manifest *derives* had moved, both from numbers that do not reproduce: the
tier-1 order, which breaks ties on measured wall-clock cost, and the tier-2 pairing, which
ranks on a skill score that divides by the unseeded reference model. Six of the eight pairs
were re-selected and three tier-1 ranks moved.

Batch 26 makes both a recorded decision. This checks that the record actually holds, using
**the clean-room's own conclusions.csv** as the drifted input rather than a synthetic one --
the defence is tested against the data that broke it.

## How it runs, and why it touches the live tree

`plan_manifest.py` reads the whole tree: every fork, every model's `run_cost.json`, the
phase-C sweeps. There is no honest way to sandbox that into a throwaway copy the way batch
24 sandboxed the frozen manifest, which is four files. So each scenario swaps one *tracked*
input, invokes the node script, records what happened, and restores from git -- and the
restore is unconditional, so an exception still leaves the tree as it was found. Nothing
here writes to `manifest_selection.json`, which is the artefact under test.

The node script is invoked under `environment/chapenv`, because a node's scripts are part of
the pinned analysis whatever they import (AGENTS.md §8). This harness runs under `.venv`.

Usage:
  .venv/bin/python AI-internal/useful-scripts/check_selection_defence.py --root .
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

RESULTS = "analysis/05_stability/results"
SCRIPT = "analysis/05_stability/scripts/plan_manifest.py"
PYTHON = "environment/chapenv/bin/python"
CLEANROOM = "AI-generated/validation/26-09-02_cleanroom-artefacts"
# Tracked files the node script rewrites, restored after every scenario.
TOUCHED = ["manifest.csv", "manifest_notes.json", "forks.csv", "tier2_rule.md",
           "conclusions.csv"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def restore(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "checkout", "--",
                    *[f"{RESULTS}/{f}" for f in TOUCHED]],
                   capture_output=True)


def run_plan(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([str(root / PYTHON), str(root / SCRIPT)],
                          cwd=root, capture_output=True, text=True)


def scenario_drifted_conclusions(root: Path) -> dict:
    """The one that broke batch 25: a re-drawn reference moves every skill score.

    The rule, applied to these conclusions, chooses six different pairs. The record must
    win, `manifest.csv` must come back byte-identical, and the disagreement must be
    reported rather than absorbed.
    """
    before = sha(root / RESULTS / "manifest.csv")
    shutil.copy(root / CLEANROOM / "conclusions.csv", root / RESULTS / "conclusions.csv")
    proc = run_plan(root)
    check = json.loads((root / RESULTS / "manifest_selection_check.json").read_text())
    after = sha(root / RESULTS / "manifest.csv")
    return {
        "what_it_does": "swaps in the clean-room run's conclusions.csv, which the tier-2 "
                        "rule ranks on, and re-plans",
        "exit_code": proc.returncode,
        "manifest_unchanged": before == after,
        "recorded_pairs_kept": check["tier2_recorded"],
        "pairs_the_rule_would_choose_now": check["tier2_the_rule_would_choose_now"],
        "n_pairs_that_would_differ": len(check["tier2_pairs_that_would_differ"]),
        "verdict": check["verdict"],
        "passes": (proc.returncode == 0 and before == after
                   and len(check["tier2_pairs_that_would_differ"]) > 0),
        "why_this_is_the_test": "batch 25 re-selected six of eight pairs from exactly "
                                "these numbers and the freeze check then stopped the run",
    }


def scenario_dropped_from_the_tree(root: Path) -> dict:
    """A recorded combination the tree no longer carries is fatal, not quietly dropped."""
    record = json.loads((root / RESULTS / "manifest_selection.json").read_text())
    hacked = dict(record)
    hacked["tier1_order"] = [*record["tier1_order"], "a_row_the_tree_does_not_have"]
    path = root / RESULTS / "manifest_selection.json"
    original = path.read_text()
    path.write_text(json.dumps(hacked, indent=1, sort_keys=True) + "\n")
    proc = run_plan(root)
    path.write_text(original)
    return {
        "what_it_does": "adds a combination to the recorded order that the tree cannot "
                        "produce, and re-plans",
        "exit_code": proc.returncode,
        "said": next((l for l in (proc.stdout + proc.stderr).splitlines()
                      if "FATAL" in l), ""),
        "passes": proc.returncode != 0,
        "why": "the recorded order would describe a manifest this repository can no "
               "longer produce, so it stops rather than silently shrinking",
    }


def scenario_pair_component_missing(root: Path) -> dict:
    """A recorded pair whose halves are gone is fatal for the same reason."""
    path = root / RESULTS / "manifest_selection.json"
    original = path.read_text()
    record = json.loads(original)
    hacked = dict(record)
    hacked["tier2_pairs"] = [{"a": "gone", "b": "alsoGone"}, *record["tier2_pairs"][1:]]
    path.write_text(json.dumps(hacked, indent=1, sort_keys=True) + "\n")
    proc = run_plan(root)
    path.write_text(original)
    return {
        "what_it_does": "names a tier-2 pair whose two halves are not tier-1 rows",
        "exit_code": proc.returncode,
        "said": next((l for l in (proc.stdout + proc.stderr).splitlines()
                      if "FATAL" in l), ""),
        "passes": proc.returncode != 0,
        "why": "these eight pairs are what phase D ran and phase E was frozen against",
    }


def scenario_record_is_never_rewritten(root: Path) -> dict:
    """The artefact under test is written once. Two runs must not touch it."""
    path = root / RESULTS / "manifest_selection.json"
    before = sha(path)
    proc = run_plan(root)
    return {
        "what_it_does": "re-plans with the record present and hashes it before and after",
        "exit_code": proc.returncode,
        "sha256_before": before, "sha256_after": sha(path),
        "passes": before == sha(path) and proc.returncode == 0,
        "why": "batch 16 fixed one recomputed field and left the recomputation; batch 24 "
               "had to come back for the file. A record of a decision is written once",
    }


def scenario_refreeze_from_cold(root: Path) -> dict:
    """Delete the record and let the freeze path run: it must return what is recorded.

    A regression test rather than a defence. The script was restructured, and a refactor
    that changed the recorded order or pairing would have changed what phase E was frozen
    against.
    """
    path = root / RESULTS / "manifest_selection.json"
    original = path.read_text()
    record = json.loads(original)
    path.unlink()
    proc = run_plan(root)
    refrozen = json.loads(path.read_text())
    path.write_text(original)
    same = (refrozen["tier1_order"] == record["tier1_order"]
            and refrozen["tier2_pairs"] == record["tier2_pairs"])
    return {
        "what_it_does": "removes the record and runs the freeze path from cold",
        "exit_code": proc.returncode,
        "tier1_order_identical": refrozen["tier1_order"] == record["tier1_order"],
        "tier2_pairs_identical": refrozen["tier2_pairs"] == record["tier2_pairs"],
        "passes": same and proc.returncode == 0,
        "why": "the freeze path is kept for a reader implementing this method, and it "
               "must still produce the decision this project actually took",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path,
                    default=Path("AI-generated/validation/26-09-02_selectionDefence.json"))
    a = ap.parse_args()
    root = a.root.resolve()

    if subprocess.run(["git", "-C", str(root), "status", "--porcelain", RESULTS],
                      capture_output=True, text=True).stdout.strip():
        print("refusing to run: results/ has uncommitted changes, and every scenario "
              "restores by checking out from git. Commit or stash first.")
        return 2

    scenarios = {
        "drifted_conclusions": scenario_drifted_conclusions,
        "dropped_from_the_tree": scenario_dropped_from_the_tree,
        "pair_component_missing": scenario_pair_component_missing,
        "record_is_never_rewritten": scenario_record_is_never_rewritten,
        "refreeze_from_cold": scenario_refreeze_from_cold,
    }
    results = {}
    try:
        for name, fn in scenarios.items():
            try:
                results[name] = fn(root)
            finally:
                restore(root)
            print(f"  {'pass' if results[name]['passes'] else 'FAIL'}  {name}")
    finally:
        restore(root)

    out = {
        "what_this_is": "Five situations put to the recorded tier-1 order and tier-2 "
                        "pairing that batch 26 introduced, one of them driven by the "
                        "clean-room run's own conclusions.csv -- the data that broke "
                        "batch 25.",
        "script": "AI-internal/useful-scripts/check_selection_defence.py",
        "under_test": SCRIPT,
        "all_passed": all(r["passes"] for r in results.values()),
        "scenarios": results,
    }
    (root / a.out).write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nall passed: {out['all_passed']}  -> {a.out}")
    return 0 if out["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
