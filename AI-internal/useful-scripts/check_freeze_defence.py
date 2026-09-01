#!/usr/bin/env python3
"""Check that the frozen phase-E set defends itself, on a copy rather than on the record.

`analysis/05_stability/scripts/freeze_holdout_manifest.py` writes the set phase E runs on
the held-out year and, since batch 24, refuses to rewrite it. That refusal is the whole of
what plan §3 gets from the script, and it is only worth having if it has been made to fail.
So this exercises it against six situations, on a throwaway copy of the node's `results/`,
and writes what happened.

The copy matters. Four of the six scenarios are corruptions of the manifest, and running
them against the live tree would mean writing a broken frozen set into the repository to
find out that the script refuses to. The fixture is built from the live files, mutated, and
deleted.

The scenarios, and what each one is:

  intact                the tree as it stands. The recomputation must agree with the
                        frozen set and nothing may be written to it.
  added                 a fork child discovered after the opening, appearing as a new row
                        in the development manifest. This is the defect batch 18 found:
                        under the old script it produced a 34-row frozen set. It must now
                        be reported as unpaired and the frozen set must stay at 33.
  dropped               a row the frozen set names and the tree no longer carries. Fatal:
                        the frozen set can no longer be reproduced.
  restructured          a frozen row whose fork child was renamed. Fatal for the same
                        reason — the columns that say what analysis runs are the set.
  conclusion_drift      a development conclusion that moved, as the unseeded reference
                        makes it move on any re-run. Reported, not fatal, and the frozen
                        pairing stays as it was frozen.
  missing_after_opening the frozen file deleted while the holdout has been opened. The set
                        is restored from git, never re-derived.

And one more, which is the regression test rather than a defence:

  refreeze_from_cold    the frozen file deleted with no evidence the year was ever opened,
                        which is batch 15's own path. It must come back **byte-identical**
                        to the manifest frozen in batch 15, because batch 24 restructured
                        the script and a refactor that changed the set would have changed
                        the reported result.

The script's refusal is half the fix. The other half is `check_invariants.check_freeze`,
which asserts the same thing about the file rather than about whatever wrote it, and it gets
the same treatment here: four situations, each on a fixture repository, checking that the
invariant fails where it should and not where it should not.

  invariant_intact       this repository. The frozen set is what holdout_freeze.json
                         recorded, and no holdout result exists at the commit that added it.
  invariant_rewritten    a frozen manifest that no longer hashes to the recorded digest.
  invariant_row_count    a frozen manifest with a row count the record disagrees with.
  invariant_late_freeze  a repository in which holdout results already exist at the commit
                         that added the frozen set — the freeze happening after the opening,
                         which is the one thing the record's `commit_note` asserts and
                         nothing checked.

Writes:
  AI-generated/validation/YY-MM-DD_freezeDefence.json

Dual interface:
    API:  run_scenarios(root=".") -> list[dict]
          run_invariant_scenarios(root=".") -> list[dict]
    CLI:  python check_freeze_defence.py [--root .] [--out <path>]
          exits non-zero if any scenario did not behave as specified
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

NODE = Path("analysis/05_stability")
SCHEME = Path("analysis/01_data/02_characterise/results/backtest_scheme_chosen.json")
SCRIPT = "freeze_holdout_manifest.py"
# The node's scripts are part of the pinned analysis, so they are exercised under the
# environment they run under (AGENTS.md §8), not under the repository's own .venv.
PYTHON = Path("environment/chapenv/bin/python")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fixture(root: Path, where: Path) -> Path:
    """A throwaway repository holding just what the script reads and writes."""
    (where / NODE / "scripts").mkdir(parents=True)
    (where / SCHEME.parent).mkdir(parents=True)
    (where / "analysis/results").mkdir(parents=True)
    shutil.copytree(root / NODE / "results", where / NODE / "results")
    shutil.copy(root / NODE / "scripts" / SCRIPT, where / NODE / "scripts" / SCRIPT)
    shutil.copy(root / SCHEME, where / SCHEME)
    # Written by the script itself; a copy of the live one would make the first scenario
    # compare against a file it had not produced.
    (where / NODE / "results" / "holdout_freeze_check.json").unlink(missing_ok=True)
    return where


def invoke(root: Path, where: Path) -> tuple[int, str]:
    done = subprocess.run([str(root / PYTHON), str(where / NODE / "scripts" / SCRIPT)],
                          capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr).strip()


# --- the mutations, each a function of the fixture -------------------------------------

def _manifest(where: Path) -> Path:
    return where / NODE / "results" / "manifest.csv"


def _frozen(where: Path) -> Path:
    return where / NODE / "results" / "manifest_holdout.csv"


def add_a_development_row(where: Path) -> None:
    """A fork child added to the tree after the opening, as `plan_manifest.py` would."""
    path = _manifest(where)
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    new = dict(rows[0])
    new.update({"rank": str(len(rows) + 1), "tier": "1", "combination": "window_from1999",
                "kind": "setup", "fork": "analysis/02_setup/03_window", "child": "c_from1999",
                "status": "planned"})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows + [new])


def drop_a_development_row(where: Path) -> None:
    path = _manifest(where)
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows[:-1])


def restructure_a_row(where: Path) -> None:
    path = _manifest(where)
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    for row in rows:
        if row["child"] and row["child"] != "-":
            row["child"] += "Renamed"
            break
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def move_a_conclusion(where: Path) -> None:
    """What the unseeded reference does to the development half on any re-run."""
    path = where / NODE / "results" / "conclusions.csv"
    rows = list(csv.DictReader(path.open()))
    fields = list(rows[0])
    for row in rows:
        if row["combination"] == "main" and row["skill_score"]:
            row["skill_score"] = str(float(row["skill_score"]) + 0.0065)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def delete_the_frozen_file(where: Path) -> None:
    _frozen(where).unlink()


def delete_the_frozen_file_and_every_trace_of_the_opening(where: Path) -> None:
    _frozen(where).unlink()
    (where / NODE / "results" / "run_status_holdout.csv").unlink(missing_ok=True)
    for child in (where / "analysis/results").iterdir():
        if child.is_dir() and child.name.endswith("__holdout"):
            shutil.rmtree(child)


SCENARIOS = [
    ("intact", None, "the frozen set is verified and not rewritten", 0),
    ("added", add_a_development_row,
     "a development row with no twin is reported as unpaired, never added", 0),
    ("dropped", drop_a_development_row,
     "a frozen row the tree no longer carries is fatal", 1),
    ("restructured", restructure_a_row,
     "a frozen row whose fork child moved is fatal", 1),
    ("conclusion_drift", move_a_conclusion,
     "a development conclusion that moved is reported, not fatal", 0),
    ("missing_after_opening", delete_the_frozen_file,
     "the set is not re-derived after a holdout number has been seen", 1),
    ("refreeze_from_cold", delete_the_frozen_file_and_every_trace_of_the_opening,
     "batch 15's freeze path still returns the manifest frozen in batch 15", 0),
]


def run_scenarios(root: str | Path = ".") -> list[dict]:
    root = Path(root).resolve()
    live_frozen = sha256(root / NODE / "results" / "manifest_holdout.csv")
    live_freeze_json = sha256(root / NODE / "results" / "holdout_freeze.json")
    out: list[dict] = []

    for name, mutate, expectation, expected_exit in SCENARIOS:
        with tempfile.TemporaryDirectory() as tmp:
            where = build_fixture(root, Path(tmp) / "repo")
            if mutate:
                mutate(where)
            code, said = invoke(root, where)

            frozen = _frozen(where)
            freeze_json = where / NODE / "results" / "holdout_freeze.json"
            check_path = where / NODE / "results" / "holdout_freeze_check.json"
            check = json.loads(check_path.read_text()) if check_path.exists() else {}
            rows = (sum(1 for _ in csv.DictReader(frozen.open()))
                    if frozen.exists() else None)

            entry = {
                "scenario": name,
                "expectation": expectation,
                "exit_code": code,
                "exit_code_expected": expected_exit,
                "frozen_rows": rows,
                "frozen_manifest_sha256_unchanged": (
                    frozen.exists() and sha256(frozen) == live_frozen),
                "holdout_freeze_json_sha256_unchanged": (
                    freeze_json.exists() and sha256(freeze_json) == live_freeze_json),
                "unpaired": check.get("unpaired_development_rows", {}).get("rows", []),
                "fatal_missing": check.get("fatal", {}).get(
                    "frozen_rows_the_tree_no_longer_carries", []),
                "fatal_restructured": [
                    r["combination"] for r in
                    check.get("fatal", {}).get("frozen_rows_whose_structure_moved", [])],
                "drifted": [r["combination"] for r in check.get(
                    "drift_under_an_unchanged_set", {}).get("rows", [])],
                "said": said,
            }
            # What "behaved as specified" means, scenario by scenario. Written out rather
            # than reduced to the exit code, because the two failures this exists to catch
            # -- a frozen set that grew, and a re-freeze after the opening -- both exit 0
            # in the version of the script that had them.
            held = entry["exit_code"] == expected_exit
            if name == "intact":
                held &= (rows == 33 and entry["frozen_manifest_sha256_unchanged"]
                         and entry["holdout_freeze_json_sha256_unchanged"]
                         and not entry["unpaired"] and not entry["drifted"])
            elif name == "added":
                held &= (rows == 33 and entry["frozen_manifest_sha256_unchanged"]
                         and entry["unpaired"] == ["window_from1999__holdout"])
            elif name == "dropped":
                held &= bool(entry["fatal_missing"]) and entry[
                    "frozen_manifest_sha256_unchanged"]
            elif name == "restructured":
                held &= bool(entry["fatal_restructured"]) and entry[
                    "frozen_manifest_sha256_unchanged"]
            elif name == "conclusion_drift":
                held &= (entry["drifted"] == ["main__holdout"]
                         and entry["frozen_manifest_sha256_unchanged"])
            elif name == "missing_after_opening":
                held &= (rows is None and "not re-derived" in said)
            elif name == "refreeze_from_cold":
                held &= entry["frozen_manifest_sha256_unchanged"]
            entry["as_specified"] = held
            out.append(entry)
    return out


# --- the other half: the invariant, on fixture repositories ----------------------------

def _invariant_fixture(root: Path, where: Path, with_git: bool) -> Path:
    """Just enough repository for `check_freeze` to have an opinion about."""
    (where / NODE / "results").mkdir(parents=True)
    for name in ("manifest_holdout.csv", "holdout_freeze.json"):
        shutil.copy(root / NODE / "results" / name, where / NODE / "results" / name)
    if with_git:
        subprocess.run(["git", "-C", str(where), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(where), "config", "user.email", "t@example"],
                       check=True)
        subprocess.run(["git", "-C", str(where), "config", "user.name", "t"], check=True)
    return where


def _freeze_findings(where: Path) -> list[str]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_invariants  # noqa: E402  -- the module under test, imported as a library
    return [f.message for f in check_invariants.run_checks(where, ["freeze"])]


def _fixture_rewritten(root: Path, where: Path) -> None:
    path = where / NODE / "results" / "manifest_holdout.csv"
    path.write_text(path.read_text() + "34,1,invented,invented,setup,-,-,-,-,,,True,1.0,"
                                       ",,,,,frozen\n")


def _fixture_row_count(root: Path, where: Path) -> None:
    record = json.loads((where / NODE / "results" / "holdout_freeze.json").read_text())
    record["rows"] = record["rows"] + 1
    (where / NODE / "results" / "holdout_freeze.json").write_text(
        json.dumps(record, indent=1) + "\n")
    # The digest is of the manifest, which has not moved, so only the count disagrees.


def _fixture_late_freeze(root: Path, where: Path) -> None:
    """A repository where the frozen set was added *after* holdout results existed."""
    (where / "analysis/results/main__holdout").mkdir(parents=True)
    (where / "analysis/results/main__holdout/conclusion.json").write_text("{}\n")
    subprocess.run(["git", "-C", str(where), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(where), "commit", "-qm", "everything at once"],
                   check=True)
    head = subprocess.run(["git", "-C", str(where), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    path = where / NODE / "results" / "holdout_freeze.json"
    record = json.loads(path.read_text())
    record["frozen_at_commit"] = head
    path.write_text(json.dumps(record, indent=1) + "\n")


INVARIANT_SCENARIOS = [
    ("invariant_intact", None, False,
     "this repository: the frozen set is what was frozen, and it predates the opening",
     False),
    ("invariant_rewritten", _fixture_rewritten, False,
     "a frozen manifest that no longer hashes to the recorded digest is caught", True),
    ("invariant_row_count", _fixture_row_count, False,
     "a row count the record disagrees with is caught", True),
    ("invariant_late_freeze", _fixture_late_freeze, True,
     "holdout results existing at the commit that added the frozen set is caught", True),
]


def run_invariant_scenarios(root: str | Path = ".") -> list[dict]:
    root = Path(root).resolve()
    out: list[dict] = []
    for name, mutate, with_git, expectation, should_fail in INVARIANT_SCENARIOS:
        if mutate is None:
            found = _freeze_findings(root)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                where = _invariant_fixture(root, Path(tmp) / "repo", with_git)
                mutate(root, where)
                found = _freeze_findings(where)
        out.append({
            "scenario": name,
            "expectation": expectation,
            "findings": found,
            "as_specified": bool(found) == should_fail,
        })
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None,
                    help="where to write the record (default: "
                         "AI-generated/validation/<today>_freezeDefence.json)")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve()
    results = run_scenarios(root)
    invariants = run_invariant_scenarios(root)
    held = all(r["as_specified"] for r in results + invariants)
    out = Path(a.out) if a.out else (
        root / "AI-generated/validation" / f"{date.today():%y-%m-%d}_freezeDefence.json")
    out.write_text(json.dumps({
        "what_this_is": (
            "Seven situations put to analysis/05_stability/scripts/freeze_holdout_manifest.py "
            "on a throwaway copy of the node's results/, and four put to "
            "check_invariants.check_freeze on fixture repositories: the frozen phase-E set "
            "defends itself rather than being rewritten, and the file is checked as well as "
            "the script that writes it (batch 24)."),
        "checked_on": date.today().isoformat(),
        "script": "AI-internal/useful-scripts/check_freeze_defence.py",
        "under_test": [str(NODE / "scripts" / SCRIPT),
                       "AI-internal/useful-scripts/check_invariants.py::check_freeze"],
        "under_test_sha256": sha256(root / NODE / "scripts" / SCRIPT),
        "invariant_sha256": sha256(
            root / "AI-internal/useful-scripts/check_invariants.py"),
        "frozen_manifest_sha256": sha256(root / NODE / "results" / "manifest_holdout.csv"),
        "all_as_specified": held,
        "scenarios": results,
        "invariant_scenarios": invariants,
    }, indent=1) + "\n")

    for r in results:
        print(f"{'ok  ' if r['as_specified'] else 'FAIL'}  {r['scenario']:<22} "
              f"exit {r['exit_code']}  {r['expectation']}")
    for r in invariants:
        print(f"{'ok  ' if r['as_specified'] else 'FAIL'}  {r['scenario']:<22} "
              f"{len(r['findings'])} finding(s)  {r['expectation']}")
    print(f"\n-> {out}")
    return 0 if held else 1


if __name__ == "__main__":
    sys.exit(main())
