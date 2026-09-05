"""Check that everything Rule 10 says goes into the release is actually there.

`/release` lists what a release contains. This walks that list and reports, per item,
whether the repository holds it and where — so "the release is assembled" is a file somebody
can re-run rather than a sentence somebody wrote.

It checks presence and not adequacy. Whether the claim collection is *good* is not a question
a script can answer; whether it exists, is tracked, and is where the release says it is, is.

The release here is the repository itself — Rule 10 says the release is the whole tree,
alternatives included — so "assembly" is a verification rather than a copy. Nothing is staged
into a separate directory, because a second copy of a 2.6 GB tree is a second thing to keep
in step with the first.

Usage:
  .venv/bin/python AI-internal/useful-scripts/release_manifest.py --root .
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

#: (what Rule 10 asks for, the paths that answer for it, whether all of them are required)
REQUIRED = [
    ("data, or accessioned references where redistribution is not permitted",
     ["Archive/lao-dataset", "Archive/lao-population", "Archive/sibling-datasets"], True),
    ("all scripts, and analysis/ entire — alternatives included",
     ["analysis", "AI-internal/useful-scripts"], True),
    ("the environment specifications at all three layers",
     ["environment/lock.txt", "environment/install-chap.sh", "environment/Dockerfile"], True),
    ("the claim collection and the manuscript's provenance sidecar",
     ["Human-AI-collaboration/claims/claims.md",
      "Human-AI-collaboration/manuscript/26-09-05_illustratingCase_sidecar.md"], True),
    ("the provenance records",
     ["analysis"], True),
    ("the instruction files and skills — they determine how the analysis was produced",
     ["AGENTS.md", "CLAUDE.md", ".claude/commands"], True),
    ("the hierarchical report and the reproducibility report",
     ["AI-generated/hierarchical-report/provenance.md",
      "AI-generated/repro-report/26-09-05_reproducibilityReport.md"], True),
    ("a root script that rebuilds everything",
     ["analysis/run.sh"], True),
]


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True).stdout


def tracked_under(tracked: set[str], path: str) -> int:
    return sum(1 for p in tracked if p == path or p.startswith(path.rstrip("/") + "/"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="AI-generated/release/release_manifest.json")
    a = parser.parse_args()
    root = Path(a.root).resolve()
    tracked = {p for p in git(root, "ls-files").split("\n") if p}

    items, missing = [], []
    for what, paths, _ in REQUIRED:
        found = {p: tracked_under(tracked, p) for p in paths}
        absent = [p for p, n in found.items() if n == 0]
        missing += absent
        items.append({"rule_10_asks_for": what, "tracked_files_per_path": found,
                      "present": not absent, "absent": absent})

    # The alternatives are the part Rule 10 calls the most valuable thing in the release,
    # so they are counted rather than assumed: a fork child with no scripts would be a path
    # in the tree that nobody can run.
    import re
    forks, not_taken, runnable = 0, 0, 0
    for claim in sorted((root / "analysis").rglob("claim.md")):
        text = claim.read_text()
        kind = re.search(r"^kind:\s*(.*)$", text, re.M)
        if not kind or kind.group(1).strip() != "alternatives":
            continue
        main_path = re.search(r"^main-path:\s*(.*)$", text, re.M)
        main_path = main_path.group(1).strip() if main_path else None
        forks += 1
        for kid in sorted(p for p in claim.parent.iterdir()
                          if p.is_dir() and (p / "claim.md").exists()):
            if kid.name == main_path:
                continue
            not_taken += 1
            if (kid / "run.sh").exists():
                runnable += 1

    report = {
        "what_this_is": (
            "every item Rule 10 says goes into the release, checked against what git tracks. "
            "The release is the repository itself, so this is a verification and not a copy"),
        "checked_at_commit": git(root, "rev-parse", "--short=9", "HEAD").strip(),
        "tracked_files": len(tracked),
        "items": items,
        "everything_rule_10_asks_for_is_present": not missing,
        "absent": sorted(set(missing)),
        "alternatives": {
            "forks": forks,
            "paths_not_taken": not_taken,
            "paths_not_taken_with_a_run_sh": runnable,
            "note": ("Rule 10 calls the paths not taken the most valuable thing in the "
                     "release. Each is counted and each is checked for an entry point, "
                     "because an alternative nobody can run is a directory and not a path"),
        },
        "not_in_the_release_and_why": {
            "AI-generated/hierarchical-report/": (
                "gitignored apart from its provenance record; 1 387 generated pages rebuilt "
                "in three seconds by /hierarchical-report from the tree"),
            "analysis/**/work/": (
                "chap-core's per-split run directories, about 20 GB, read by nothing after "
                "a run and regenerated by the node's own run.sh"),
            "environment/chapenv/": (
                "the built environment; environment/lock.txt and install-chap.sh are what "
                "reproduce it, and the script reports any difference"),
            "analysis/05_stability/.holdout_opened": (
                "the working-tree half of the holdout seal, deliberately unversioned: a "
                "versioned seal seals every clone and turns a reproduction of phase E into "
                "a description of one"),
        },
    }
    out = root / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")

    for item in items:
        print(f"  {'ok ' if item['present'] else 'MISSING'}  {item['rule_10_asks_for']}")
    print(f"\n{len(tracked)} tracked files; {not_taken} paths not taken across {forks} forks, "
          f"{runnable} with an entry point")
    print(f"everything Rule 10 asks for is present: "
          f"{report['everything_rule_10_asks_for_is_present']}\n-> {a.out}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
