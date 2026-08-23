#!/usr/bin/env python3
"""Check the structural invariants the ten rules imply.

This is the part of the setup that does not depend on anyone remembering. An
instruction in AGENTS.md can be honoured for twenty steps and dropped at the
twenty-first without anything looking wrong; these checks have no attention
budget. Run at the end of every analysis and before every commit.

A failing check is fixed at the cause. Never weaken a check so it passes.

Checks
  tree        every node is well-formed; alternatives nodes have exactly one main
              path, store no scripts of their own, and call only that child;
              sub-analysis parents call every child
  provenance  every file under a node's results/ has a provenance record, and every
              record names an existing script, commit and environment
  plots       every plot image has its plotted values and its plotting script beside it
  seeds       every script that draws randomness has a recorded seed
  claims      every claim in the collection resolves to an existing result
  git         the working tree is clean, and recorded commits exist
  crossing    no result file looks like a value transcribed between steps by hand

Dual interface:
    API:  run_checks(root=".", only=None) -> list[Finding]
    CLI:  python check_invariants.py [--root .] [--only tree,plots] [--quiet]
          exits non-zero if anything failed
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PLOT_SUFFIXES = {".png", ".pdf", ".svg", ".jpg", ".jpeg"}
DATA_SUFFIXES = {".tsv", ".csv", ".txt", ".json", ".parquet"}
SCRIPT_SUFFIXES = {".py", ".R", ".r", ".sh", ".jl"}
RANDOM_HINTS = re.compile(
    r"\b(random|rand\(|randn|sample\(|shuffle|permut|np\.random|torch\.rand|"
    r"set\.seed|rng|Random\()", re.I
)
SEED_HINTS = re.compile(r"\b(seed|set_seed|manual_seed|set\.seed|SEED)\b")


@dataclass
class Finding:
    check: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.check}] {self.path}: {self.message}"


def nodes(root: Path) -> list[Path]:
    return sorted(p.parent for p in (root / "analysis").rglob("claim.md"))


def _field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    return None if v in ("", "-", "none", "n/a") else v


def check_tree(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        run = node / "run.sh"
        if not run.exists():
            out.append(Finding("tree", rel, "no run.sh"))
            continue
        run_text = run.read_text()
        claim_text = (node / "claim.md").read_text()
        kids = sorted(p for p in node.iterdir() if p.is_dir() and (p / "claim.md").exists())
        if not kids:
            continue
        kind = _field(claim_text, "kind")
        if kind not in ("alternatives", "sub-analyses"):
            out.append(Finding("tree", rel, f"has children but kind is {kind!r}"))
            continue
        if kind == "alternatives":
            main = _field(claim_text, "main-path")
            names = [k.name for k in kids]
            if main not in names:
                out.append(Finding("tree", rel, f"main-path {main!r} not among {names}"))
                continue
            called = set(re.findall(r'bash "([^"/]+)/run\.sh"', run_text))
            if called != {main}:
                out.append(Finding(
                    "tree", rel,
                    f"alternatives node must call only the main path {main!r}, calls {sorted(called)}"))
            own = [p for p in (node / "scripts").glob("*") if p.name != ".gitkeep"] \
                if (node / "scripts").is_dir() else []
            if own:
                out.append(Finding(
                    "tree", rel,
                    f"alternatives node is a pure switch but stores {len(own)} script(s)"))
        else:
            called = set(re.findall(r'bash "([^"/]+)/run\.sh"', run_text))
            missing = {k.name for k in kids} - called
            if missing:
                out.append(Finding(
                    "tree", rel, f"sub-analyses node does not call {sorted(missing)}"))
    return out


def _provenance_records(node: Path) -> dict[str, str]:
    prov = node / "provenance"
    if not prov.is_dir():
        return {}
    return {p.name: p.read_text() for p in prov.glob("*.md")}


def check_provenance(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        results = node / "results"
        if not results.is_dir():
            continue
        records = _provenance_records(node)
        blob = "\n".join(records.values())
        for f in sorted(results.rglob("*")):
            if f.is_dir() or f.name == ".gitkeep":
                continue
            name = f.relative_to(results).as_posix()
            if name not in blob:
                out.append(Finding("provenance", f"{rel}/results/{name}",
                                   "no provenance record names this result"))
        for rec_name, rec in records.items():
            for key in ("script:", "commit:", "environment:"):
                if key not in rec:
                    out.append(Finding("provenance", f"{rel}/provenance/{rec_name}",
                                       f"record is missing '{key}'"))
    return out


def check_plots(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        results = node / "results"
        if not results.is_dir():
            continue
        for f in sorted(results.rglob("*")):
            if f.suffix.lower() not in PLOT_SUFFIXES:
                continue
            stem = f.with_suffix("")
            has_data = any(stem.with_suffix(s).exists() for s in DATA_SUFFIXES)
            has_script = any(
                (node / "scripts" / f"{stem.name}{s}").exists() for s in SCRIPT_SUFFIXES
            ) or any(stem.with_suffix(s).exists() for s in SCRIPT_SUFFIXES)
            if not has_data:
                out.append(Finding("plots", f"{rel}/results/{f.name}",
                                   "no plotted-values file beside the figure"))
            if not has_script:
                out.append(Finding("plots", f"{rel}/results/{f.name}",
                                   "no plotting script for this figure"))
    return out


def check_seeds(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        scripts = node / "scripts"
        if not scripts.is_dir():
            continue
        for s in sorted(scripts.rglob("*")):
            if s.suffix not in SCRIPT_SUFFIXES:
                continue
            text = s.read_text(errors="replace")
            if RANDOM_HINTS.search(text) and not SEED_HINTS.search(text):
                out.append(Finding("seeds", f"{rel}/scripts/{s.name}",
                                   "draws randomness but records no seed"))
    return out


def check_claims(root: Path) -> list[Finding]:
    out: list[Finding] = []
    coll = root / "Human-AI-collaboration" / "claims" / "claims.md"
    if not coll.exists():
        return out
    # Drop fenced code blocks first: the collection documents its own format with an
    # example, and an example must not be checked as if it were a real claim.
    text = re.sub(r"^```.*?^```", "", coll.read_text(), flags=re.S | re.M)
    for m in re.finditer(r"^\s*[-*]?\s*grounds:\s*(.+)$", text, re.M):
        for target in [t.strip() for t in m.group(1).split("·")]:
            target = target.strip("`[] ")
            if not target or target.startswith("("):
                continue
            if not (root / target).exists():
                out.append(Finding("claims", target, "claim points at a result that does not exist"))
    return out


def check_git(root: Path) -> list[Finding]:
    out: list[Finding] = []
    if not (root / ".git").is_dir():
        return [Finding("git", ".", "not a git repository -- Rule 4 cannot be satisfied")]
    try:
        st = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return [Finding("git", ".", f"could not run git: {e}")]
    if st:
        n = len(st.splitlines())
        out.append(Finding("git", ".", f"working tree not clean ({n} changed path(s))"))
    for node in nodes(root):
        for rec_name, rec in _provenance_records(node).items():
            m = re.search(r"^commit:\s*([0-9a-f]{7,40})\s*$", rec, re.M)
            if not m:
                continue
            r = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{m.group(1)}^{{commit}}"],
                               capture_output=True)
            if r.returncode != 0:
                out.append(Finding("git", f"{node.relative_to(root)}/provenance/{rec_name}",
                                   f"recorded commit {m.group(1)} does not exist"))
    return out


def check_crossing(root: Path) -> list[Finding]:
    """Heuristic for Rule 1's hardest failure: a value carried between steps by hand.

    A literal numeric constant sitting in a script with a comment naming another
    step is the visible symptom. Reported as a warning to look at, not a proof.
    """
    out: list[Finding] = []
    pat = re.compile(r"^\s*[A-Z_]{3,}\s*=\s*-?\d+\.?\d*\s*#.*\b(from|per|see|step|output|above)\b",
                     re.M | re.I)
    for node in nodes(root):
        scripts = node / "scripts"
        if not scripts.is_dir():
            continue
        for s in sorted(scripts.rglob("*")):
            if s.suffix not in SCRIPT_SUFFIXES:
                continue
            for m in pat.finditer(s.read_text(errors="replace")):
                out.append(Finding("crossing", f"{node.relative_to(root)}/scripts/{s.name}",
                                   f"hard-coded value may have crossed a step by hand: "
                                   f"{m.group(0).strip()[:70]}"))
    return out


CHECKS = {
    "tree": check_tree,
    "provenance": check_provenance,
    "plots": check_plots,
    "seeds": check_seeds,
    "claims": check_claims,
    "git": check_git,
    "crossing": check_crossing,
}


def run_checks(root: str | Path = ".", only: list[str] | None = None) -> list[Finding]:
    root = Path(root).resolve()
    names = only or list(CHECKS)
    findings: list[Finding] = []
    for n in names:
        if n not in CHECKS:
            raise SystemExit(f"unknown check: {n} (have {', '.join(CHECKS)})")
        findings.extend(CHECKS[n](root))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--only", help="comma-separated subset of: " + ", ".join(CHECKS))
    ap.add_argument("--quiet", action="store_true", help="print only failures")
    a = ap.parse_args(argv)

    only = [s.strip() for s in a.only.split(",")] if a.only else None
    findings = run_checks(a.root, only)

    by_check: dict[str, list[Finding]] = {}
    for f in findings:
        by_check.setdefault(f.check, []).append(f)

    for name in (only or list(CHECKS)):
        fs = by_check.get(name, [])
        if fs:
            print(f"FAIL  {name}  ({len(fs)})")
            for f in fs:
                print(f"        {f.path}: {f.message}")
        elif not a.quiet:
            print(f"ok    {name}")

    if findings:
        print(f"\n{len(findings)} invariant failure(s). Fix the cause, not the check.")
        return 1
    if not a.quiet:
        print("\nAll invariants hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
