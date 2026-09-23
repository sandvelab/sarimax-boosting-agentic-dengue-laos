#!/usr/bin/env python3
"""Inventory of what this repository can establish about its own provenance (`/repro-report`).

The reproducibility report is written from artefacts, not from a checklist of what should
exist, and every count it gives has to come from a file that was executed (AGENTS.md §1). This
script is that file. It walks the claim tree, the provenance records, the claim collection, the
manuscripts' provenance sidecars, the perturbation manifests, the plan's decision log and the
git history, and writes one JSON document the report cites.

It establishes *shape*: how many records exist, which required fields each carries, whether
every claim's grounds resolve. It cannot establish that a record is true. The report's section
on what does not hold is written by reading, and this script only tells the reader where to
look.

Programmatic use:  from repro_inventory import inventory; inventory(root) -> dict
CLI:               .venv/bin/python AI-internal/useful-scripts/repro_inventory.py [--root .]
                       [--out AI-generated/repro-report/inventory.json]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

RECORD_REQUIRED = [
    "result", "script", "invocation", "inputs", "environment", "seeds", "commit",
    "instructions-commit", "node", "produced",
]
RECORD_VERIDICAL = ["alternatives-considered", "agency", "information"]
AGENCY_TERMS = ["human-set", "agent-on-human-assessment", "agent-autonomous"]


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          check=False).stdout.strip()


def _field_lines(text: str) -> dict[str, list[str]]:
    """Lines of the form `field: value` at line start, collected per field (records are
    running accounts, so a field may appear once per appended section)."""
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        m = re.match(r"^([a-z][a-z-]*):\s*(.*)$", line)
        if m:
            out.setdefault(m.group(1), []).append(m.group(2))
    return out


def _agency_of(values: list[str]) -> str:
    joined = " ".join(values).lower()
    found = [t for t in AGENCY_TERMS if t in joined]
    if not found:
        return "unstated"
    return "mixed" if len(found) > 1 else found[0]


# ---------------------------------------------------------------- the tree and its records
def tree_inventory(root: Path) -> dict:
    analysis = root / "analysis"
    nodes = []
    for claim in sorted(analysis.rglob("claim.md")):
        node = claim.parent
        if any(part in ("results", "scripts", "provenance", "env", "work") for part in node.relative_to(root).parts):
            continue
        text = claim.read_text(encoding="utf-8", errors="replace")
        kind = re.search(r"^kind:\s*(.+)$", text, re.M)
        main = re.search(r"^main-path:\s*(.+)$", text, re.M)
        children = sorted(p.name for p in node.iterdir()
                          if p.is_dir() and (p / "claim.md").is_file())
        nodes.append({
            "node": str(node.relative_to(root)),
            "children_kind": (kind.group(1).strip() if kind else "-"),
            "main_path": (main.group(1).strip() if main else "-"),
            "children": children,
            "n_scripts": len(list((node / "scripts").glob("*.py"))) if (node / "scripts").is_dir() else 0,
            "n_results": sum(1 for p in (node / "results").rglob("*") if p.is_file()) if (node / "results").is_dir() else 0,
            "n_provenance_records": len(list((node / "provenance").glob("*.md"))) if (node / "provenance").is_dir() else 0,
            "has_run_sh": (node / "run.sh").is_file(),
            "has_env_override": (node / "env").is_dir(),
        })
    alternatives = [n for n in nodes if n["children_kind"].startswith("alternatives")]
    return {
        "n_nodes": len(nodes),
        "n_alternatives_nodes": len(alternatives),
        "n_alternatives_children_total": sum(len(n["children"]) for n in alternatives),
        "n_paths_not_taken": sum(len(n["children"]) - 1 for n in alternatives),
        "alternatives": [{"node": n["node"], "main_path": n["main_path"], "children": n["children"]}
                         for n in alternatives],
        "n_sub_analyses_nodes": sum(1 for n in nodes if n["children_kind"].startswith("sub-analyses")),
        "n_leaf_nodes": sum(1 for n in nodes if not n["children"]),
        "n_node_scripts": sum(n["n_scripts"] for n in nodes),
        "n_shared_library_scripts": len(list((analysis / "scripts" / "lib").glob("*.py"))),
        "n_run_sh": sum(1 for n in nodes if n["has_run_sh"]),
        "n_env_overrides": sum(1 for n in nodes if n["has_env_override"]),
        "n_result_files": sum(n["n_results"] for n in nodes),
        "n_scored_results": len(list(analysis.rglob("per_cell_scores.csv"))),
        "nodes": nodes,
    }


def records_inventory(root: Path) -> dict:
    recs = sorted((root / "analysis").rglob("provenance/*.md"))
    per_field_present = Counter()
    agency = Counter()
    information = Counter()
    instruction_commits = Counter()
    run_commits = set()
    sections = 0
    per_record = []
    for r in recs:
        text = r.read_text(encoding="utf-8", errors="replace")
        f = _field_lines(text)
        for k in RECORD_REQUIRED + RECORD_VERIDICAL:
            if k in f:
                per_field_present[k] += 1
        agency[_agency_of(f.get("agency", []))] += 1
        info = " ".join(f.get("information", [])).lower()
        if "agent-retrieved" in info and "human-pointed" in info:
            information["both"] += 1
        elif "agent-retrieved" in info:
            information["agent-retrieved"] += 1
        elif "human-pointed" in info:
            information["human-pointed"] += 1
        elif f.get("information"):
            information["stated-other"] += 1
        else:
            information["none"] += 1
        for v in f.get("instructions-commit", []):
            instruction_commits[v.strip()[:7]] += 1
        for v in f.get("commit", []):
            run_commits.add(v.strip()[:7])
        n_sections = len(f.get("result", [])) or 1
        sections += n_sections
        per_record.append({"record": str(r.relative_to(root)), "sections": n_sections,
                           "missing_required": [k for k in RECORD_REQUIRED if k not in f],
                           "missing_veridical": [k for k in RECORD_VERIDICAL if k not in f]})
    return {
        "n_records": len(recs),
        "n_sections_total": sections,
        "field_present_in_n_records": dict(per_field_present),
        "records_missing_any_required_field": [p for p in per_record if p["missing_required"]],
        "records_missing_alternatives_considered": sum(1 for p in per_record if "alternatives-considered" in p["missing_veridical"]),
        "records_missing_information_field": sum(1 for p in per_record if "information" in p["missing_veridical"]),
        "agency": dict(agency),
        "information": dict(information),
        "distinct_instruction_set_commits": sorted(instruction_commits),
        "n_distinct_instruction_set_commits": len(instruction_commits),
        "n_distinct_run_commits": len(run_commits),
    }


# ---------------------------------------------------------------- claims and manuscripts
def claims_inventory(root: Path) -> dict:
    path = root / "Human-AI-collaboration" / "claims" / "claims.md"
    text = path.read_text(encoding="utf-8")
    # The collection's header shows the block format inside a fenced example; it is not a claim.
    text = re.sub(r"^```.*?^```\s*$", "", text, flags=re.M | re.S)
    blocks = re.split(r"^## (C\d+)\s*$", text, flags=re.M)[1:]
    claims = []
    for cid, body in zip(blocks[0::2], blocks[1::2]):
        f = _field_lines(body)
        grounds = [g.strip().strip("`") for g in re.split(r"\s·\s|\s+·\s+", " ".join(f.get("grounds", [])))]
        grounds = [g for g in grounds if g]
        claims.append({
            "id": cid,
            "node": " ".join(f.get("node", [])).strip(),
            "by": _agency_of(f.get("by", [])),
            "grounds": grounds,
            "grounds_resolve": [(root / g).exists() for g in grounds],
            "has_scope": bool(f.get("scope")),
            "has_alternatives": bool(f.get("alternatives")),
            "scope_holdout": "hold" in " ".join(f.get("scope", [])).lower(),
        })
    return {
        "n_claims": len(claims),
        "n_grounds_pointers": sum(len(c["grounds"]) for c in claims),
        "n_grounds_unresolved": sum(1 for c in claims for ok in c["grounds_resolve"] if not ok),
        "by": dict(Counter(c["by"] for c in claims)),
        "n_with_scope": sum(c["has_scope"] for c in claims),
        "n_with_alternatives_field": sum(c["has_alternatives"] for c in claims),
        "n_scoped_to_holdout": sum(c["scope_holdout"] for c in claims),
        "nodes_with_claims": dict(Counter(c["node"] for c in claims)),
        "claims": claims,
    }


def manuscripts_inventory(root: Path, claim_ids: list[str]) -> dict:
    folder = root / "Human-AI-collaboration" / "manuscript"
    out = []
    for sidecar in sorted(folder.glob("*_claims.md")):
        draft = folder / sidecar.name.replace("_claims.md", ".md")
        text = sidecar.read_text(encoding="utf-8")
        rows = [ln for ln in text.splitlines() if ln.startswith("|") and not re.match(r"^\|\s*-", ln)
                and not re.match(r"^\|\s*Statement", ln)]
        cited = Counter(re.findall(r"\*\*(C\d+)\*\*", text))
        # Each row is classified once: resting on a claim first, else a marked method statement.
        claim_rows = sum(1 for ln in rows if re.search(r"\*\*C\d+\*\*", ln))
        method_rows = sum(1 for ln in rows if "method:" in ln and not re.search(r"\*\*C\d+\*\*", ln))
        out.append({
            "draft": str(draft.relative_to(root)) if draft.exists() else None,
            "sidecar": str(sidecar.relative_to(root)),
            "draft_words": len(draft.read_text(encoding="utf-8").split()) if draft.exists() else None,
            "sidecar_statement_rows": len(rows),
            "rows_resting_on_a_claim": claim_rows,
            "rows_marked_method": method_rows,
            "rows_neither": len(rows) - claim_rows - method_rows,
            "distinct_claims_cited": len(cited),
            "claims_cited": sorted(cited, key=lambda c: int(c[1:])),
            "claims_not_cited": sorted([c for c in claim_ids if c not in cited], key=lambda c: int(c[1:])),
        })
    return {"manuscripts": out}


# ---------------------------------------------------------------- manifests and the plan
def manifests_inventory(root: Path) -> dict:
    res = root / "analysis" / "06_stability" / "results"
    out = {}
    for name in ("manifest.csv", "manifest_holdout.csv"):
        p = res / name
        if not p.is_file():
            continue
        rows = list(csv.DictReader(p.open(encoding="utf-8")))
        by = Counter((r.get("tier", "?"), r.get("status", "?")) for r in rows)
        versions = Counter(r.get("version", "") for r in rows) if rows and "version" in rows[0] else {}
        out[name] = {
            "rows": len(rows),
            "by_tier_and_status": {f"tier {t} / {s}": n for (t, s), n in sorted(by.items())},
            "not_run_with_reason": sum(1 for r in rows if (r.get("status") or "").startswith("not_run") and (r.get("reason_if_not_run") or r.get("reason"))),
            "not_run_without_reason": sum(1 for r in rows if (r.get("status") or "").startswith("not_run") and not (r.get("reason_if_not_run") or r.get("reason"))),
            "superseded_kept": sum(1 for r in rows if "superseded" in (r.get("status") or "")),
            "versions": dict(versions),
        }
    for name in ("manifest_freeze.json", "holdout_freeze.json"):
        p = res / name
        if p.is_file():
            d = json.loads(p.read_text())
            out[name] = {k: d.get(k) for k in ("frozen_at_commit", "frozen_on", "rows", "sha256", "main_path", "version") if k in d}
    status = res / "run_status_holdout.csv"
    if status.is_file():
        rows = list(csv.DictReader(status.open(encoding="utf-8")))
        out["holdout_openings"] = [{k: r.get(k) for k in ("opened_on", "opened_at_commit", "opening_number", "n_rows_planned", "n_rows_run")} for r in rows]
    return out


def plan_inventory(root: Path) -> dict:
    plans = sorted((root / "Human-input" / "Plans for AI generation").glob("*.md"))
    plans = [p for p in plans if p.name != "README.md"]
    if not plans:
        return {}
    text = plans[0].read_text(encoding="utf-8")
    sec = re.search(r"^## 4b\..*?(?=^## 5\.)", text, re.M | re.S)
    decisions = []
    if sec:
        for ln in sec.group(0).splitlines():
            if ln.startswith("|") and not re.match(r"^\|\s*-", ln) and not re.match(r"^\|\s*Decision", ln):
                cells = [c.strip() for c in ln.strip("|").split("|")]
                if len(cells) >= 3:
                    decisions.append(_agency_of([cells[-1]]) if "(open" not in cells[-1].lower() else "open")
    ledger = re.search(r"^## 6\..*?(?=^## Batch ledger)", text, re.M | re.S)
    rows = []
    if ledger:
        for ln in ledger.group(0).splitlines():
            if ln.startswith("|") and re.match(r"^\|\s*\d", ln):
                cells = [c.strip() for c in ln.strip("|").split("|")]
                rows.append({"batch": cells[0], "status": cells[-1]})
    return {
        "plan": str(plans[0].relative_to(root)),
        "n_decisions_logged_in_4b": len(decisions),
        "decisions_by_agency": dict(Counter(decisions)),
        "n_ledger_rows": len(rows),
        "ledger_status": dict(Counter(r["status"].split(" ")[0].strip("*").lower() for r in rows)),
    }


# ---------------------------------------------------------------- environment, checks, git
def environment_inventory(root: Path) -> dict:
    env = root / "environment"
    lock = env / "lock.txt"
    return {
        "declarative_spec": (env / "environment.yml").is_file(),
        "lockfile": lock.is_file(),
        "n_locked_packages": sum(1 for ln in lock.read_text().splitlines() if "==" in ln) if lock.is_file() else 0,
        "build_script": (env / "install-env.sh").is_file(),
        "container_image": any(env.glob("Dockerfile*")) or any(root.glob("Dockerfile*")),
        "python_pin": (re.search(r'python:\s*"?([\d.]+)', (env / "environment.yml").read_text()).group(1)
                       if (env / "environment.yml").is_file() else None),
    }


def validation_inventory(root: Path) -> dict:
    out = {"cleanroom_runs": [], "outsider_tests": [], "release_scans": []}
    val = root / "AI-generated" / "validation"
    if val.is_dir():
        for d in sorted(val.glob("*_cleanroom-artefacts")):
            s = d / "summary.json"
            if s.is_file():
                out["cleanroom_runs"].append({"folder": d.name, **json.loads(s.read_text())})
        out["outsider_tests"] = [p.name for p in sorted(val.glob("*outsider-test*.md"))]
        for d in sorted(val.glob("*_release-scan")):
            s = d / "summary.json"
            if s.is_file():
                out["release_scans"].append({"folder": d.name, **json.loads(s.read_text())})
    inv = subprocess.run([str(root / ".venv" / "bin" / "python"),
                          str(root / "AI-internal" / "useful-scripts" / "check_invariants.py")],
                         capture_output=True, text=True, cwd=root, check=False)
    checks = dict(re.findall(r"^(?:ok|FAIL)\s+(\w+)", inv.stdout, re.M) and
                  [(m.group(2), m.group(1)) for m in re.finditer(r"^(ok|FAIL)\s+(\w+)", inv.stdout, re.M)])
    out["invariants"] = {"exit_code": inv.returncode, "checks": checks,
                         "all_hold": inv.returncode == 0 and "All invariants hold" in inv.stdout}
    return out


def git_inventory(root: Path) -> dict:
    first = _git(root, "log", "--reverse", "--format=%h %ad", "--date=short").splitlines()[:1]
    last = _git(root, "log", "-1", "--format=%h %ad", "--date=short")
    n = _git(root, "rev-list", "--count", "HEAD")
    msgs = _git(root, "log", "--format=%s").splitlines()
    return {
        "n_commits": int(n or 0),
        "first_commit": first[0] if first else None,
        "head": last,
        "n_before_commits": sum(1 for m in msgs if m.lower().startswith("before")),
        "n_after_commits": sum(1 for m in msgs if m.lower().startswith("after")),
        "n_methodological_change_commits": sum(1 for m in msgs if "methodological change" in m.lower()),
        "instruction_files_tracked": [p for p in ("AGENTS.md", "CLAUDE.md", ".claude/settings.json")
                                      if _git(root, "ls-files", "--error-unmatch", p)],
        "n_skill_files_tracked": len(_git(root, "ls-files", ".claude/commands").splitlines()),
        "working_tree_clean": _git(root, "status", "--porcelain") == "",
    }


def inventory(root: Path) -> dict:
    claims = claims_inventory(root)
    return {
        "produced": date.today().isoformat(),
        "head": _git(root, "rev-parse", "--short", "HEAD"),
        "tree": tree_inventory(root),
        "provenance_records": records_inventory(root),
        "claims": claims,
        "manuscripts": manuscripts_inventory(root, [c["id"] for c in claims["claims"]]),
        "stability": manifests_inventory(root),
        "plan": plan_inventory(root),
        "environment": environment_inventory(root),
        "validation": validation_inventory(root),
        "git": git_inventory(root),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="AI-generated/repro-report/inventory.json")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    inv = inventory(root)
    out = root / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    t, r, c = inv["tree"], inv["provenance_records"], inv["claims"]
    print(f"nodes {t['n_nodes']} (alternatives nodes {t['n_alternatives_nodes']}, paths not taken "
          f"{t['n_paths_not_taken']}) · scripts {t['n_node_scripts']}+{t['n_shared_library_scripts']} lib · "
          f"results {t['n_result_files']} · records {r['n_records']} · claims {c['n_claims']} "
          f"({c['n_grounds_unresolved']} unresolved grounds) · commits {inv['git']['n_commits']}")
    print(f"written {out.relative_to(root) if out.is_relative_to(root) else out}")


if __name__ == "__main__":
    main()
