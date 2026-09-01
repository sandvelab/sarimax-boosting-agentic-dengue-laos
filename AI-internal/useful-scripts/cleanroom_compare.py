"""Classify what the clean-room run changed, against the archived results.

The comparison is git's: the clone's index is the archive, so after the run every
difference is a modified tracked file. This sorts them into the three kinds that mean
different things.

  identical    the file came back byte for byte -- the reproduction
  path-only    the only lines that differ contain the repository's absolute path, which
               is the run directory and not a result
  numeric      something the analysis computed came out different

Run from the clean-room directory after the run finishes.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CR = Path(__file__).resolve().parent
REPO = CR / "repo"
LIVE = Path("/Users/geirksa_1_2_3/ai/special-purpose vaults/ReprodicbleAgenticAiCase")


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True).stdout


def classify() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {"path-only": [], "numeric": [], "untracked": []}
    for line in git("status", "--porcelain").splitlines():
        status, path = line[:2].strip(), line[3:].strip().strip('"')
        if status == "??":
            out["untracked"].append(path)
            continue
        diff = git("diff", "--unified=0", "--", path)
        body = [l for l in diff.splitlines()
                if (l.startswith("+") or l.startswith("-"))
                and not l.startswith(("+++", "---"))]
        if body and all(str(REPO) in l or str(LIVE) in l for l in body):
            out["path-only"].append(path)
        else:
            out["numeric"].append(path)
    return out


def conclusion(where: Path, combo: str) -> dict:
    p = where / "analysis/results" / combo / "conclusion.json"
    return json.loads(p.read_text()) if p.exists() else {}


def main() -> int:
    tracked = len(git("ls-files").splitlines())
    kinds = classify()
    changed = len(kinds["path-only"]) + len(kinds["numeric"])
    print(f"tracked files: {tracked}")
    print(f"  identical : {tracked - changed}")
    print(f"  path-only : {len(kinds['path-only'])}")
    print(f"  numeric   : {len(kinds['numeric'])}")
    print(f"  untracked : {len(kinds['untracked'])}\n")

    for kind in ("numeric", "untracked"):
        if kinds[kind]:
            print(f"--- {kind} ({len(kinds[kind])}) ---")
            for p in sorted(kinds[kind]):
                print(f"    {p}")
            print()

    # The headline, side by side. The reference model is unseeded, so this is expected to
    # move; the question is whether it moves by less than the reference's own measured
    # re-run spread, which is the only yardstick this project has for it.
    for combo in ("main", "main__holdout"):
        a, b = conclusion(LIVE, combo), conclusion(REPO, combo)
        if not a or not b:
            continue
        print(f"--- conclusion.json [{combo}] ---")
        for k in sorted(set(a) | set(b)):
            va, vb = a.get(k), b.get(k)
            if va == vb:
                continue
            delta = ""
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                delta = f"   Δ {vb - va:+.6f}"
            print(f"    {k}\n        archived  {va}\n        cleanroom {vb}{delta}")
        print()

    # The comparison is itself a reported result, so it lands in a file rather than being
    # read out of this script's output (AGENTS.md §1).
    conclusions = {}
    for combo in ("main", "main__holdout"):
        a, b = conclusion(LIVE, combo), conclusion(REPO, combo)
        if not a or not b:
            continue
        moved = {}
        for k in sorted(set(a) | set(b)):
            va, vb = a.get(k), b.get(k)
            if va == vb:
                continue
            entry = {"archived": va, "cleanroom": vb}
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                entry["delta"] = vb - va
            moved[k] = entry
        conclusions[combo] = {
            "fields_identical": sorted(k for k in set(a) & set(b) if a[k] == b[k]),
            "fields_moved": moved}

    Path(CR / "comparison.json").write_text(json.dumps(
        {"tracked": tracked, "identical": tracked - changed,
         "cleanroom_head": (CR / "cleanroom_head.txt").read_text().strip()
         if (CR / "cleanroom_head.txt").exists() else None,
         "rows_of_the_stability_manifest_reached": sorted(
             p.stem for p in (REPO / "analysis/05_stability/results/logs").glob("*.log")
             if p.stat().st_mtime > (CR / "install_env.log").stat().st_mtime),
         "conclusions": conclusions,
         "file_classes": kinds}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
