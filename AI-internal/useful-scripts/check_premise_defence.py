#!/usr/bin/env python3
"""Situations put to batch 32's defence of the registered pool membership, on the live tree.

The weighting child of candidate 3 registers, before the pool runs, how many members the
pool will have and what share of its mass sits on the plan's two required baselines. With
equal weights that statement is the model: the count is the weight. Batch 22 gave the
persistence and climatology baselines a second published construction each, and from that
day the child counted contract directories while the pool resolved each fork to one child.
Forty combinations recorded **six members at 1/6 with two-thirds of the mass on required
baselines**; **four at 1/4** ran.

Batch 32 gave both one rule. That is a claim about what happens under conditions this
repository is no longer in, so it is tested by putting the repository back into them, one
file at a time, and restoring afterwards.

Six situations, each restored before the next:

1. **the clean-room's own two lines**: batch 19's run from a cold checkout printed
   `6 members at 0.167 each, 4 of them required baselines` and, three lines later,
   `ensemble members[main]: 4 — persistence, climatology, hier_nb, boosted; ... not on
   this combination's path: [b_negBinomialFloor, b_frozenWindow]`. The fixed child, run
   here under `main`, must print the first line as the second one already said it: four
   members, two required baselines, and the same two contracts left out. This is the only
   situation whose evidence was produced by a machine that had never run this repository;
2. **the record batch 22 left**: `covariates_rich`'s specification as it stood before this
   batch. `/validate invariants` must fail on it, and on all three of its clauses -- two
   constructions of one baseline in one pool, once for each of the two baseline forks; a
   membership the pool's own record contradicts; and a copy in `candidate_spec.json`
   saying the same wrong thing. Four findings, because the fork clause is about a fork;
3. **the structural clause alone**: the same document with every record of the run that
   produced it out of reach. The fork clause must still fire on both forks, because a
   combination that has never been run has no record to be checked against;
4. **a stale embedded copy**: the child's specification corrected and the family
   assembler not re-run. Only the third clause may fire -- this is the cascade that made
   one defect into ninety-four documents;
5. **the runtime guard**: with the old specification restored, `prepare_members.py` must
   refuse to build the pool rather than build one its own specification contradicts, and
   must refuse before writing anything. It is staged on `covariates_rich` and not on
   `main`, because `main` is one of the seven combinations whose specification was written
   before batch 22 and named the right four members all along -- the guard has nothing to
   catch there, which is a property of when that file was last written and not of the
   defence;
6. **the tree as it stands**: no finding at all.

Every situation ends with the file back to its committed content, checked by digest, and
`analysis/` left clean by git's own account. Exits non-zero if any situation fails or if
anything under `analysis/` is left changed.

Writes AI-generated/validation/<date>_premiseDefence.json
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENSEMBLE = ROOT / "analysis/03_models/03_candidate/c_ensemble"
EQUAL = ENSEMBLE / "01_weighting/a_equal"
CHECK = ROOT / "AI-internal/useful-scripts/check_invariants.py"
PYTHON = ROOT / "environment/chapenv/bin/python"
VENV = ROOT / ".venv/bin/python"
#: The commit before this batch rewrote the premises -- where the old specifications are.
BEFORE = "a4ce730"
#: The clean-room run of 2026-09-05, from a checkout that had never seen this machine.
CLEANROOM = ROOT / "AI-generated/validation/26-09-05_cleanroom-artefacts/run.log"
#: The combination the situations are staged on: a candidate-internal row, so its pool is
#: the four the main path pools and its record is one batch 14 wrote.
STAGED = "covariates_rich"


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def git_show(rev: str, path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{rel}"],
                         capture_output=True, text=True, check=True)
    return out.stdout


def invariant_findings() -> list[str]:
    out = subprocess.run([str(VENV), str(CHECK), "--only", "pool", "--quiet"],
                         capture_output=True, text=True, cwd=ROOT)
    return [line.strip() for line in out.stdout.splitlines()
            if line.strip() and not line.startswith(("FAIL", "ok", "All"))
            and "invariant failure" not in line]


def analysis_is_clean() -> bool:
    out = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "analysis"],
                         capture_output=True, text=True, check=True)
    return not out.stdout.strip()


def situation_one() -> dict:
    """The clean-room's own two lines, and what the fixed child says now."""
    log = CLEANROOM.read_text().splitlines()
    child = next(l for l in log if l.startswith("weighting/a_equal[main]:"))
    pool = next(l for l in log if l.startswith("ensemble members[main]:"))
    cold_child_count = int(re.search(r"(\d+) members at", child).group(1))
    cold_pool_count = int(re.search(r"members\[main\]: (\d+)", pool).group(1))
    cold_excluded = sorted(re.findall(r"01_baselines/\d\d_\w+/(\w+)/scripts", pool))

    run = subprocess.run([str(PYTHON), str(EQUAL / "scripts" / "choose_weighting.py")],
                         capture_output=True, text=True, cwd=ROOT,
                         env={**os.environ, "COMBO": "main", "COMBO_BASE": ""})
    now = run.stdout.strip().splitlines()[-1]
    now_count = int(re.search(r"(\d+) members at", now).group(1))
    now_excluded = sorted(re.findall(r"01_baselines/\d\d_\w+/(\w+)/scripts", now))

    return {
        "situation": "the clean-room's own two lines",
        "cold_checkout_log": str(CLEANROOM.relative_to(ROOT)),
        "cold_child_said": cold_child_count,
        "cold_pool_ran": cold_pool_count,
        "cold_pool_left_out": cold_excluded,
        "child_says_now": now_count,
        "child_leaves_out_now": now_excluded,
        "passed": (cold_child_count != cold_pool_count
                   and now_count == cold_pool_count
                   and now_excluded == cold_excluded),
    }


def situation_two() -> dict:
    """The record batch 22 left. All three clauses must fire."""
    spec = EQUAL / "results" / STAGED / "model_option_spec.json"
    keep = spec.read_bytes()
    spec.write_text(git_show(BEFORE, spec))
    findings = invariant_findings()
    spec.write_bytes(keep)
    mine = [f for f in findings if STAGED in f]
    return {
        "situation": "the record batch 22 left",
        "combination": STAGED,
        "findings": mine,
        "fork_clause": any("under the alternatives fork" in f for f in mine),
        "record_clause": any("member_selection.json records" in f for f in mine),
        "embedded_clause": any("embeds a different membership" in f for f in mine),
        "restored": digest(spec) == hashlib.sha256(keep).hexdigest(),
        "passed": (len(mine) == 4
                   and sum("under the alternatives fork" in f for f in mine) == 2
                   and sum("member_selection.json records" in f for f in mine) == 1
                   and sum("embeds a different membership" in f for f in mine) == 1),
    }


def situation_three() -> dict:
    """A combination with no record of its own: the structural clause has to stand alone."""
    spec = EQUAL / "results" / STAGED / "model_option_spec.json"
    keep = spec.read_bytes()
    recorded = ENSEMBLE / "results" / STAGED / "member_selection.json"
    membership = ENSEMBLE / "results" / STAGED / "members.json"
    assembled = ENSEMBLE / "results" / STAGED / "candidate_spec.json"
    hidden = [(p, p.read_bytes()) for p in (recorded, membership, assembled)]
    spec.write_text(git_show(BEFORE, spec))
    for path, _ in hidden:
        path.unlink()
    findings = invariant_findings()
    spec.write_bytes(keep)
    for path, content in hidden:
        path.write_bytes(content)
    mine = [f for f in findings if STAGED in f]
    return {
        "situation": "the structural clause alone",
        "records_removed": [str(p.relative_to(ROOT)) for p, _ in hidden],
        "findings": mine,
        "restored": all(digest(p) == hashlib.sha256(c).hexdigest() for p, c in hidden),
        "passed": len(mine) == 2 and all("under the alternatives fork" in f for f in mine),
    }


def situation_four() -> dict:
    """The child corrected, the family assembler not re-run."""
    assembled = ENSEMBLE / "results" / STAGED / "candidate_spec.json"
    keep = assembled.read_bytes()
    assembled.write_text(git_show(BEFORE, assembled))
    findings = invariant_findings()
    assembled.write_bytes(keep)
    mine = [f for f in findings if STAGED in f]
    return {
        "situation": "a stale embedded copy",
        "findings": mine,
        "restored": digest(assembled) == hashlib.sha256(keep).hexdigest(),
        "passed": len(mine) == 1 and "embeds a different membership" in mine[0],
    }


def situation_five() -> dict:
    """The runtime guard: the pool refuses to be built against a premise it contradicts."""
    spec = EQUAL / "results" / STAGED / "model_option_spec.json"
    members = ENSEMBLE / "results" / STAGED / "members.json"
    selection = ENSEMBLE / "results" / STAGED / "member_selection.json"
    keep = spec.read_bytes()
    before = {p: digest(p) for p in (members, selection)}
    spec.write_text(git_show(BEFORE, spec))
    run = subprocess.run([str(PYTHON), str(ENSEMBLE / "scripts" / "prepare_members.py")],
                         capture_output=True, text=True, cwd=ROOT,
                         env={**os.environ, "COMBO": STAGED, "COMBO_BASE": ""})
    spec.write_bytes(keep)
    untouched = all(digest(p) == d for p, d in before.items())
    return {
        "situation": "the runtime guard",
        "exit_code": run.returncode,
        "message": (run.stderr or run.stdout).strip().splitlines()[:3],
        "wrote_nothing": untouched,
        "restored": digest(spec) == hashlib.sha256(keep).hexdigest(),
        "passed": run.returncode != 0 and untouched
                  and "contradicts" in (run.stderr + run.stdout),
    }


def situation_six() -> dict:
    findings = invariant_findings()
    return {"situation": "the tree as it stands", "findings": findings,
            "passed": not findings}


def main() -> int:
    situations = [situation_one(), situation_two(), situation_three(),
                  situation_four(), situation_five(), situation_six()]
    clean = analysis_is_clean()
    document = {
        "what_this_is": ("batch 32's defence of the registered pool membership, put to "
                         "six situations on the live tree and restored after each"),
        "commit_the_old_specifications_come_from": BEFORE,
        "situations": situations,
        "all_passed": all(s["passed"] for s in situations),
        "analysis_left_clean": clean,
    }
    out = (ROOT / "AI-generated" / "validation"
           / f"{date.today():%y-%m-%d}_premiseDefence.json")
    out.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    for s in situations:
        print(f"  {'pass' if s['passed'] else 'FAIL'}  {s['situation']}")
    print(f"premise defence: {sum(s['passed'] for s in situations)} of "
          f"{len(situations)} situations pass; analysis/ "
          f"{'clean' if clean else 'LEFT CHANGED'} -> {out}")
    return 0 if document["all_passed"] and clean else 1


if __name__ == "__main__":
    sys.exit(main())
