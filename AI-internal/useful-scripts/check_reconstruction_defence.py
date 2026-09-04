#!/usr/bin/env python3
"""Situations put to batch 28's reconstruction sweep, on the live tree.

`05_stability/scripts/reconstruct_pools.py` exists so that a `pool_check.json` written
before its members had been evaluated separately does not stay that way. That is a claim
about what happens under conditions this repository is not in — every combination has run
here — so it is tested by putting the repository into them, one file at a time, and
restoring afterwards.

Four situations, each restored before the next:

1. **the record batch 16 left**: `main__holdout/pool_check.json` as it was before this
   batch, saying the reconstruction was impossible. The sweep must rewrite it to the
   complete-tree answer;
2. **a file that is already right**: nothing is re-run and the file is untouched;
3. **a file that is missing entirely**: it is produced;
4. **a row that can never be reconstructed** (`covariates_rich`, which moves a fork inside
   candidate 1): the sweep must leave it saying so rather than reaching for another
   member's directory.

Every situation ends with the file back to its committed content, checked by digest, and
`analysis/` left clean by git's own account. Exits non-zero if any situation fails or if
anything under `analysis/` is left changed.

Writes AI-generated/validation/<date>_reconstructionSweepDefence.json
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENSEMBLE = ROOT / "analysis/03_models/03_candidate/c_ensemble"
SWEEP = ROOT / "analysis/05_stability/scripts/reconstruct_pools.py"
SUMMARY = ROOT / "analysis/05_stability/results/pool_reconstruction.json"
PYTHON = ROOT / "environment/chapenv/bin/python"
#: The commit before batch 28 rewrote the pool checks -- where the early records still are.
BEFORE = "96f1205"


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def git_show(rev: str, path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{rel}"],
                         capture_output=True, text=True, check=True)
    return out.stdout


def run_sweep() -> str:
    out = subprocess.run([str(PYTHON), str(SWEEP)], cwd=SWEEP.parent.parent,
                         capture_output=True, text=True, check=True)
    return out.stdout


def situation(name: str, path: Path, prepare, expect) -> dict:
    """Put the tree into a state, run the sweep, judge it, and restore."""
    committed = digest(path)
    prepare()
    before = digest(path)
    log = run_sweep()
    after = json.loads(path.read_text())
    verdict = expect(after, log, before)
    restored = digest(path)
    return {"situation": name, "file": path.relative_to(ROOT).as_posix(),
            "state_put_to_it": "as it was before batch 28" if before != committed
                               else ("absent" if before is None else "unchanged"),
            "sweep_re_ran_this_row": f"re-running check_pool for {path.parent.name} " in log,
            "restored_to_the_committed_file": restored == committed,
            **verdict}


def main() -> int:
    holdout = ENSEMBLE / "results/main__holdout/pool_check.json"
    already = ENSEMBLE / "results/main/pool_check.json"
    never = ENSEMBLE / "results/covariates_rich/pool_check.json"
    results = []

    results.append(situation(
        "the record batch 16 left, restored", holdout,
        lambda: holdout.write_text(git_show(BEFORE, holdout)),
        lambda after, log, before: {
            "expected": "rebuilt from the members' own evaluations, 76.646",
            "rebuilt": after["reconstruction"]["mean_crps_rebuilt"],
            "passes": (after["reconstruction"]["mean_crps_rebuilt"] is not None
                       and abs(after["reconstruction"]["mean_crps_rebuilt"] - 76.646) < 1e-3
                       and after["reconstruction"]["not_done_because"] is None)}))

    results.append(situation(
        "a file that is already right", already, lambda: None,
        lambda after, log, before: {
            "expected": "not re-run, not touched",
            "rebuilt": after["reconstruction"]["mean_crps_rebuilt"],
            "passes": (digest(already) == before
                       and f"re-running check_pool for main " not in log)}))

    results.append(situation(
        "a file that is missing entirely", already, already.unlink,
        lambda after, log, before: {
            "expected": "produced, with the same reconstruction",
            "rebuilt": after["reconstruction"]["mean_crps_rebuilt"],
            "passes": abs(after["reconstruction"]["mean_crps_rebuilt"] - 18.801) < 1e-3}))

    results.append(situation(
        "a row no order of execution could reconstruct", never,
        lambda: never.write_text(git_show(BEFORE, never)),
        lambda after, log, before: {
            "expected": "still not done, and candidate 1 still the member it lacks",
            "rebuilt": after["reconstruction"]["mean_crps_rebuilt"],
            "passes": (after["reconstruction"]["mean_crps_rebuilt"] is None
                       and after["reconstruction"][
                           "members_without_a_matching_stored_evaluation"] == ["hier_nb"])}))

    # The tree that must be untouched is the analysis: this script and its own output are
    # new files of the batch, and would otherwise report themselves as damage.
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "analysis"],
                           capture_output=True, text=True, check=True).stdout.strip()
    document = {
        "what_this_is": ("four states the reconstruction sweep is supposed to handle, put "
                         "to it on the live tree and restored after each"),
        "commit_the_early_records_come_from": BEFORE,
        "situations": results,
        "all_pass": all(r["passes"] for r in results),
        "all_restored": all(r["restored_to_the_committed_file"] for r in results),
        "analysis_tree_clean_afterwards": not dirty,
        "left_changed": dirty.splitlines(),
    }
    out = (ROOT / "AI-generated" / "validation"
           / f"{date.today():%y-%m-%d}_reconstructionSweepDefence.json")
    out.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    for r in results:
        print(f"  {'pass' if r['passes'] else 'FAIL'}  {r['situation']}"
              f"  (re-run: {r['sweep_re_ran_this_row']}, "
              f"restored: {r['restored_to_the_committed_file']})")
    print(f"reconstruction sweep defence: {sum(r['passes'] for r in results)}/"
          f"{len(results)} pass, analysis tree clean afterwards: "
          f"{document['analysis_tree_clean_afterwards']} -> {out}")
    return 0 if (document["all_pass"] and document["all_restored"]
                 and document["analysis_tree_clean_afterwards"]) else 1


if __name__ == "__main__":
    sys.exit(main())
