"""Count what this repository actually contains, so the reproducibility report cites files.

`/repro-report` asks for a document stating what was produced, what is tracked and how, the
veridical section, the agency record and what does not hold. Every count in that document
has to come from somewhere, and `AGENTS.md` §1 does not allow it to come from counting by
eye — the report is the last document this project writes, and a figure in it that nobody
can recompute would be the exact failure the project exists to argue against.

So this walks the repository and writes the inventory. The report quotes it and computes
nothing of its own.

**What it deliberately does not do.** It makes no judgment. Whether a chain is *good* is the
report's business; this says how many links there are and how many of them resolve. And it
does not re-run the invariant checker: that has its own entry point and its own exit code,
and a second implementation of it here would be a second thing to keep in step.

Usage:
  .venv/bin/python AI-internal/useful-scripts/repro_inventory.py --root .
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

SCRIPT_SUFFIXES = {".py", ".sh", ".R", ".r"}
GENERATED = {"__pycache__", ".venv", "work", "node_modules"}


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True).stdout.strip()


def field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    v = m.group(1).strip() if m else ""
    return None if v in ("", "-", "none", "n/a") else v


def tree_inventory(root: Path) -> dict:
    nodes = sorted(p.parent for p in (root / "analysis").rglob("claim.md"))
    kinds, forks, alternatives_children = {}, [], 0
    for node in nodes:
        text = (node / "claim.md").read_text()
        kind = field(text, "kind")
        kids = [p for p in node.iterdir() if p.is_dir() and (p / "claim.md").exists()]
        if not kids:
            continue
        kinds[kind] = kinds.get(kind, 0) + 1
        if kind == "alternatives":
            main = field(text, "main-path")
            forks.append({
                "fork": str(node.relative_to(root)),
                "children": sorted(k.name for k in kids),
                "main_path": main,
                "not_taken": sorted(k.name for k in kids if k.name != main),
            })
            alternatives_children += len(kids)
    return {
        "nodes": len(nodes),
        "node_paths": [str(n.relative_to(root)) for n in nodes],
        "nodes_with_children_by_kind": kinds,
        "forks": len(forks),
        "fork_detail": forks,
        "alternatives_children": alternatives_children,
        "paths_not_taken": sum(len(f["not_taken"]) for f in forks),
    }


def results_inventory(root: Path) -> dict:
    files, total, by_combination = [], 0, {}
    for node in sorted(p.parent for p in (root / "analysis").rglob("claim.md")):
        results = node / "results"
        if not results.is_dir():
            continue
        for f in results.rglob("*"):
            if not f.is_file() or f.name == ".gitkeep":
                continue
            if any(part in GENERATED for part in f.relative_to(results).parts):
                continue
            files.append(f)
            total += f.stat().st_size
            parts = f.relative_to(results).parts
            # `logs/` at the stability and external nodes is a directory of run logs, not
            # a combination. The nodes that hold a manifest are the two whose results are
            # not combination-scoped, which is the same exemption `/validate invariants`
            # derives from where the manifests are.
            if len(parts) > 1 and parts[0] != "logs":
                by_combination[parts[0]] = by_combination.get(parts[0], 0) + 1
    suffixes: dict[str, int] = {}
    for f in files:
        suffixes[f.suffix or "(none)"] = suffixes.get(f.suffix or "(none)", 0) + 1
    return {
        "result_files": len(files),
        "bytes": total,
        "gigabytes": round(total / 1e9, 2),
        "by_suffix": dict(sorted(suffixes.items(), key=lambda kv: -kv[1])),
        "combination_directories": len(by_combination),
        "files_per_combination_min": min(by_combination.values()) if by_combination else 0,
        "files_per_combination_max": max(by_combination.values()) if by_combination else 0,
    }


def provenance_inventory(root: Path) -> dict:
    records, sections, hashed, scripts_named = 0, 0, 0, set()
    agency: dict[str, int] = {}
    for node in sorted(p.parent for p in (root / "analysis").rglob("claim.md")):
        prov = node / "provenance"
        if not prov.is_dir():
            continue
        for rec in sorted(prov.glob("*.md")):
            records += 1
            text = rec.read_text()
            sections += max(1, text.count("\n```\n") // 2)
            hashed += len(re.findall(r"sha256:[0-9a-f]{64}", text))
            for m in re.finditer(r"^script:\s*(\S+)", text, re.M):
                scripts_named.add(m.group(1))
            for m in re.finditer(r"^agency:\s*(.*)$", text, re.M):
                key = m.group(1).strip().split(".")[0].split(",")[0].strip()
                agency[key] = agency.get(key, 0) + 1
    return {
        "records": records,
        "recorded_runs": sections,
        "sha256_digests_named": hashed,
        "distinct_scripts_named": len(scripts_named),
        "agency_on_records": dict(sorted(agency.items(), key=lambda kv: -kv[1])),
    }


def scripts_inventory(root: Path) -> dict:
    """Script files and their lines, per half of the repository.

    Counted from `git ls-files` rather than from the filesystem. `/validate cleanroom`
    clones the whole repository into `AI-internal/useful-scripts/repo` and builds its
    environments there, so a walk of that directory while a clean-room run is in flight
    counts fifteen thousand files and six million lines of somebody else's code as this
    project's machinery. Git knows what belongs to the project and the filesystem does not.
    """
    tracked = [root / p for p in git(root, "ls-files").split("\n") if p]
    out = {}
    for label, base in (("analysis", root / "analysis"),
                        ("machinery", root / "AI-internal" / "useful-scripts")):
        files = [p for p in tracked
                 if p.is_file() and p.suffix in SCRIPT_SUFFIXES
                 and p.is_relative_to(base)
                 and not any(part.startswith(".") or part in GENERATED
                             for part in p.relative_to(base).parts)]
        out[label] = {
            "files": len(files),
            "lines": sum(len(p.read_text(errors="ignore").splitlines()) for p in files),
        }
    return out


def claims_inventory(root: Path) -> dict:
    path = root / "Human-AI-collaboration/claims/claims.md"
    text = path.read_text()
    # The file opens with a fenced example of the block format, and that example is a
    # complete block carrying a `grounds:` path that does not exist. Counting it would put
    # the collection one claim over and report a broken pointer that is documentation.
    # Fenced regions are dropped before parsing rather than the example being named.
    text = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    blocks = re.findall(r"^## (C\d+)\n(.*?)(?=\n## C|\Z)", text, re.S | re.M)
    grounds, agency, nodes = [], {}, {}
    for _, body in blocks:
        for line in body.splitlines():
            if line.startswith("grounds:"):
                grounds += [g.strip() for g in line[8:].split("·")]
            if line.startswith("by:"):
                key = line[3:].strip()
                agency[key] = agency.get(key, 0) + 1
            if line.startswith("node:"):
                key = line[5:].strip()
                nodes[key] = nodes.get(key, 0) + 1
    missing = [g for g in grounds if g and not (root / g).exists()]
    return {
        "claims": len(blocks),
        "grounding_paths": len(grounds),
        "grounding_paths_that_resolve": len(grounds) - len(missing),
        "grounding_paths_missing": missing,
        "by_agency": dict(sorted(agency.items(), key=lambda kv: -kv[1])),
        "claims_per_node": dict(sorted(nodes.items(), key=lambda kv: -kv[1])),
    }


def git_inventory(root: Path) -> dict:
    def count(*paths: str) -> int:
        out = git(root, "rev-list", "--count", "HEAD", "--", *paths)
        return int(out) if out else 0
    first = git(root, "log", "--reverse", "--format=%ad", "--date=short").split("\n")[0]
    return {
        "commits": count(),
        "commits_touching_analysis": count("analysis"),
        "commits_touching_the_instructions": count("AGENTS.md", "CLAUDE.md", ".claude"),
        "first_commit_date": first,
        "last_commit_date": git(root, "log", "-1", "--format=%ad", "--date=short"),
        "head": git(root, "rev-parse", "--short=9", "HEAD"),
        "tracked_files": len(git(root, "ls-files").split("\n")),
        "working_tree_clean": git(root, "status", "--porcelain") == "",
    }


def environment_inventory(root: Path) -> dict:
    lock = root / "environment" / "lock.txt"
    packages = [l for l in lock.read_text().splitlines()
                if l.strip() and not l.startswith("#")] if lock.exists() else []
    return {
        "lockfile": str(lock.relative_to(root)) if lock.exists() else None,
        "pinned_packages": len(packages),
        "node_level_overrides": sorted(
            str(p.parent.relative_to(root))
            for p in (root / "analysis").rglob("env") if p.is_dir()),
    }


def plots_inventory(root: Path) -> dict:
    figures, with_data = [], 0
    for png in sorted((root / "analysis").rglob("results/**/*.png")):
        if any(part in GENERATED for part in png.parts):
            continue
        figures.append(png)
        if (png.with_suffix(".csv")).exists() or (png.with_suffix(".json")).exists():
            with_data += 1
    return {"figures": len(figures), "with_plotted_values_beside_them": with_data}


def manifests_inventory(root: Path) -> dict:
    out = {}
    for label, rel in (
            ("development", "analysis/05_stability/results/manifest.csv"),
            ("holdout", "analysis/05_stability/results/manifest_holdout.csv"),
            ("external", "analysis/06_external/results/manifest_external.csv")):
        path = root / rel
        if not path.exists():
            continue
        rows = list(csv.DictReader(path.open()))
        out[label] = {"file": rel, "rows": len(rows),
                      "named_combinations": len({r["combination"] for r in rows
                                                 if r.get("combination")})}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="AI-generated/repro-report/repro_inventory.json")
    a = parser.parse_args()
    root = Path(a.root).resolve()

    inventory = {
        "what_this_is": (
            "what the repository contains, counted by walking it. The reproducibility "
            "report quotes these figures and computes none of its own"),
        "counted_at_commit": git(root, "rev-parse", "--short=9", "HEAD"),
        "tree": tree_inventory(root),
        "results": results_inventory(root),
        "provenance": provenance_inventory(root),
        "scripts": scripts_inventory(root),
        "claims": claims_inventory(root),
        "git": git_inventory(root),
        "environment": environment_inventory(root),
        "plots": plots_inventory(root),
        "manifests": manifests_inventory(root),
    }
    out = root / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inventory, indent=2) + "\n")

    t, r, p, c = (inventory["tree"], inventory["results"],
                  inventory["provenance"], inventory["claims"])
    print(f"tree:       {t['nodes']} nodes, {t['forks']} forks, "
          f"{t['paths_not_taken']} paths not taken")
    print(f"results:    {r['result_files']} files, {r['gigabytes']} GB, "
          f"{r['combination_directories']} combination directories")
    print(f"provenance: {p['records']} records over {p['recorded_runs']} recorded runs, "
          f"{p['sha256_digests_named']} digests")
    print(f"claims:     {c['claims']}, {c['grounding_paths_that_resolve']} of "
          f"{c['grounding_paths']} grounding paths resolve")
    print(f"-> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
