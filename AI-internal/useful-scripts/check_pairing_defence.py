"""Put batch 27's failure back to the fixed `pair_holdout_development.py` and see what it does now.

Batch 27's clean-room run of `analysis/run.sh` reached phase E, scored all 32 held-out
analyses, and exited 1 at the last script in the tree. `pair_holdout_development.py`
required every frozen `development_skill_score` in `manifest_holdout.csv` to still equal
what `conclusions.csv` said today, to 1e-9. The development skill score divides by the
reference model, which is unseeded, so that assertion can hold only on a tree whose
development half has not been re-run -- it passes exactly where it is not needed.

What the run actually had was **32 drifted figures and zero moved pairings**, with
`manifest_holdout.csv` byte-identical to the archive's and every drift inside the noise band
the same run measured for itself. `holdout_freeze_check.json`, written minutes earlier by
batch 24's machinery, reported the same drift on the same 32 rows and concluded that the
frozen set was intact.

Batch 30 separates the two. A drifted figure is reported; a moved pairing is fatal. This
checks that the separation holds, using **the clean-room's own `conclusions.csv`** as the
drifted input rather than a synthetic one -- the defence is tested against the data that
stopped the run, exactly as batch 26 tested its own against batch 25's.

## How it runs, and why it touches the live tree

Each scenario swaps one *tracked* input, invokes the node script, records what happened, and
restores from git -- and the restore is unconditional, so an exception still leaves the tree
as it was found. Nothing here writes to `manifest_holdout.csv`, which is the frozen artefact
the comparison reads and which no scenario may touch.

The node script is invoked under `environment/chapenv`, because a node's scripts are part of
the pinned analysis whatever they import (AGENTS.md §8). This harness runs under `.venv`.

Usage:
  .venv/bin/python AI-internal/useful-scripts/check_pairing_defence.py --root .
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

RESULTS = "analysis/05_stability/results"
SCRIPT = "analysis/05_stability/scripts/pair_holdout_development.py"
PYTHON = "environment/chapenv/bin/python"
CLEANROOM = "AI-generated/validation/26-09-03_cleanroom-artefacts"
# Tracked files a scenario mutates or the node script rewrites, restored after each one.
TOUCHED = ["conclusions.csv", "distribution.json", "holdout_vs_development.csv",
           "holdout_vs_development.json", "fork_sensitivity_both.csv"]
ANSWER = "holdout_vs_development.json"
# What the node script writes, as opposed to the inputs a scenario swaps in.
WRITTEN = ["holdout_vs_development.csv", ANSWER, "fork_sensitivity_both.csv"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def restore(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "checkout", "--",
                    *[f"{RESULTS}/{f}" for f in TOUCHED]], capture_output=True)


def run_pair(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([str(root / PYTHON), str(root / SCRIPT)],
                          cwd=root, capture_output=True, text=True)


def rows_of(path: Path) -> list[dict]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def frozen_column(root: Path) -> list[tuple[str, str]]:
    """The development figures the comparison reports, as written to the output table."""
    return [(r["combination"], r["development_skill_score"])
            for r in rows_of(root / RESULTS / "holdout_vs_development.csv")]


def scenario_drifted_frozen_figures(root: Path) -> dict:
    """The one that stopped batch 27: a re-drawn reference moves every development figure.

    The run must finish, report the drift, and compare on the frozen figures regardless.
    """
    before = frozen_column(root)
    # Both files come from the same run. The band the drift is measured against is the
    # one that run drew for itself (0.034944), not batch 15's (0.021778) -- mixing them
    # would compare batch 27's drift against a band measured from a different draw of the
    # same unseeded model, and the comparison would mean nothing.
    shutil.copy(root / CLEANROOM / "conclusions.csv", root / RESULTS / "conclusions.csv")
    shutil.copy(root / CLEANROOM / "distribution.json",
                root / RESULTS / "distribution.json")
    proc = run_pair(root)
    answer = json.loads((root / RESULTS / ANSWER).read_text())
    verified = answer["frozen_pairing_verified"]
    drift = verified["frozen_figures_that_drifted"]
    return {
        "what_it_does": "swaps in the clean-room run's conclusions.csv and its own "
                        "distribution.json -- the numbers the old version died on, with "
                        "the band that run measured -- and re-runs the comparison",
        "exit_code": proc.returncode,
        "verdict": verified["verdict"],
        "pairings_that_moved": len(verified["pairings_that_moved"]["rows"]),
        "frozen_figures_that_drifted": drift["rows"],
        "largest_absolute_move": drift["largest_absolute_move"],
        "development_noise_band": drift["development_noise_band"],
        "largest_move_is_inside_the_band": drift["largest_move_is_inside_the_band"],
        "compared_on_the_frozen_figures": before == frozen_column(root),
        "development_beats_reference_count": answer[
            "does_the_conclusion_hold_on_2010"]["on_development_it_was"][
            "beats_the_reference"],
        "passes": (proc.returncode == 0
                   and len(verified["pairings_that_moved"]["rows"]) == 0
                   and drift["rows"] == 32
                   and before == frozen_column(root)
                   and drift["largest_move_is_inside_the_band"]
                   and answer["does_the_conclusion_hold_on_2010"][
                       "on_development_it_was"]["beats_the_reference"] == 27),
        "why_this_is_the_test": "batch 27 had exactly these 32 drifted figures and zero "
                                "moved pairings, and exited 1 at the last script in the "
                                "tree with every held-out analysis already scored",
    }


def scenario_pairing_moved(root: Path) -> dict:
    """A frozen row whose development twin the table no longer concludes is fatal.

    This is the case the old message claimed and the data never showed. Nothing may be
    written: the comparison would be against an analysis this tree cannot produce.
    """
    manifest = rows_of(root / RESULTS / "manifest_holdout.csv")
    twin = next(r["development_combination"] for r in manifest
                if r["development_skill_score"] not in ("", None))
    path = root / RESULTS / "conclusions.csv"
    kept = [r for r in rows_of(path) if r["combination"] != twin]
    write_rows(path, kept)
    before = sha(root / RESULTS / ANSWER)
    proc = run_pair(root)
    return {
        "what_it_does": f"removes {twin} from the development table, so a frozen row is "
                        f"paired with an analysis the tree no longer concludes",
        "exit_code": proc.returncode,
        "said": next((l for l in (proc.stdout + proc.stderr).splitlines()
                      if "no longer carries" in l), ""),
        "answer_file_untouched": before == sha(root / RESULTS / ANSWER),
        "passes": proc.returncode != 0 and before == sha(root / RESULTS / ANSWER),
        "why": "a moved pairing is the comparison being about something other than what "
               "it says, which is the only difference that can make the reported answer "
               "wrong. It stops before anything is written",
    }


def scenario_twin_without_a_conclusion(root: Path) -> dict:
    """A twin still in the table but with no skill score is reported, not fatal."""
    manifest = rows_of(root / RESULTS / "manifest_holdout.csv")
    twin = next(r["development_combination"] for r in manifest
                if r["development_skill_score"] not in ("", None))
    path = root / RESULTS / "conclusions.csv"
    rows = rows_of(path)
    for r in rows:
        if r["combination"] == twin:
            r["skill_score"] = ""
            r["why_not"] = "blanked by check_pairing_defence.py"
    write_rows(path, rows)
    proc = run_pair(root)
    answer = json.loads((root / RESULTS / ANSWER).read_text())
    reported = answer["frozen_pairing_verified"][
        "development_twins_without_a_conclusion_today"]["rows"]
    return {
        "what_it_does": f"blanks {twin}'s skill score, keeping the row",
        "exit_code": proc.returncode,
        "reported_rows": len(reported),
        "passes": proc.returncode == 0 and len(reported) == 1,
        "why": "the frozen figure is a record of what was paired and stands on its own; "
               "the twin's absence from today's table is worth reporting and is not a "
               "reason to refuse to report the comparison",
    }


def scenario_beats_reference_comes_from_the_freeze(root: Path) -> dict:
    """The development boolean must not follow today's table.

    `conclude.py` defines it as `ours.mean_crps < reference.mean_crps` and both sides are
    frozen beside the row, so it is derived from the freeze. On batch 27's clean-room
    conclusions one row flips and the reported count would read 28 rather than 27.
    """
    path = root / RESULTS / "conclusions.csv"
    rows = rows_of(path)
    flipped = 0
    for r in rows:
        if r["beats_reference"] in ("True", "False"):
            r["beats_reference"] = "False" if r["beats_reference"] == "True" else "True"
            flipped += 1
    write_rows(path, rows)
    before = sha(root / RESULTS / "holdout_vs_development.csv")
    proc = run_pair(root)
    answer = json.loads((root / RESULTS / ANSWER).read_text())
    return {
        "what_it_does": f"inverts beats_reference on all {flipped} development rows and "
                        f"re-runs",
        "exit_code": proc.returncode,
        "table_unchanged": before == sha(root / RESULTS / "holdout_vs_development.csv"),
        "development_beats_reference_count": answer[
            "does_the_conclusion_hold_on_2010"]["on_development_it_was"][
            "beats_the_reference"],
        "passes": (proc.returncode == 0
                   and before == sha(root / RESULTS / "holdout_vs_development.csv")
                   and answer["does_the_conclusion_hold_on_2010"][
                       "on_development_it_was"]["beats_the_reference"] == 27),
        "why": "a reported phase-E count that follows a re-derived table is the same "
               "defect as a frozen figure re-asserted against one, three lines away",
    }


def scenario_the_output_is_stable(root: Path) -> dict:
    """Two runs on an untouched tree produce byte-identical outputs."""
    before = {f: sha(root / RESULTS / f) for f in WRITTEN}
    proc = run_pair(root)
    after = {f: sha(root / RESULTS / f) for f in WRITTEN}
    return {
        "what_it_does": "re-runs the comparison on the archived tree and hashes the three "
                        "files it writes, before and after",
        "exit_code": proc.returncode,
        "files": {f: before[f] == after[f] for f in before},
        "passes": proc.returncode == 0 and before == after,
        "why": "the comparison is arithmetic over stored scores and reads no clock, so a "
               "re-run of it must reproduce the archive exactly",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path,
                    default=Path("AI-generated/validation/26-09-03_pairingDefence.json"))
    a = ap.parse_args()
    root = a.root.resolve()

    if subprocess.run(["git", "-C", str(root), "status", "--porcelain", RESULTS],
                      capture_output=True, text=True).stdout.strip():
        print("refusing to run: results/ has uncommitted changes, and every scenario "
              "restores by checking out from git. Commit or stash first.")
        return 2

    scenarios = {
        "drifted_frozen_figures": scenario_drifted_frozen_figures,
        "pairing_moved": scenario_pairing_moved,
        "twin_without_a_conclusion": scenario_twin_without_a_conclusion,
        "beats_reference_comes_from_the_freeze":
            scenario_beats_reference_comes_from_the_freeze,
        "the_output_is_stable": scenario_the_output_is_stable,
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
        "what_this_is": "Five situations put to the frozen-pairing check that batch 30 "
                        "rebuilt, one of them driven by the clean-room run's own "
                        "conclusions.csv -- the data that stopped batch 27 at the last "
                        "script in the tree.",
        "script": "AI-internal/useful-scripts/check_pairing_defence.py",
        "under_test": SCRIPT,
        "the_drifted_input": f"{CLEANROOM}/conclusions.csv",
        "all_passed": all(r["passes"] for r in results.values()),
        "scenarios": results,
    }
    (root / a.out).write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nall passed: {out['all_passed']}  -> {a.out}")
    return 0 if out["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
