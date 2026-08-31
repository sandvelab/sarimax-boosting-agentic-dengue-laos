"""Measure how far the live plan has drifted from the plan as it was delivered.

Phase E asks for the plan's own drift as a reported result: how much of the original
design survived, what had to change, and how much of the change was the human's and how
much the agent's. That is evidence about how far an agentic system can be handed a research
plan and left to run it, which no other part of this project measures.

`AGENTS.md` §1 is why this is a script rather than a reading. Every figure in
`AI-generated/plan-drift/26-08-31_planDrift.md` is read from what this writes; none of them
is counted by eye and carried into prose.

What it measures, and the choices behind each:

**Survival is measured on the delivered text, not on the live text.** The question is how
much of the original design is still standing, so the denominator is the delivered file. A
live file that tripled in size would otherwise report a collapse in survival while having
deleted nothing.

**Lines and words are both reported**, because they answer different questions. A line
survives only if it is byte-identical, so line survival is the fraction of the plan nobody
touched. Word survival is coarser and higher, and the gap between them is the reworded-but-
not-rewritten part.

**Sections are matched by their heading text**, so a renamed section counts as the delivered
one being gone and a new one arriving. That is the honest reading: §4b did not exist when the
plan was delivered, and calling it a rename of something would hide that.

**Every §4b decision is counted once, with its agency as written.** The vocabulary is
`AGENTS.md` §4's: `human-set`, `agent-on-human-assessment`, `agent-autonomous`. Rows whose
agency cell says something else are reported separately rather than dropped, because a
silent drop is how a tally starts to flatter.

Usage, from the repository root:
  .venv/bin/python AI-internal/useful-scripts/plan_drift.py
"""

from __future__ import annotations

import csv
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIVERED = ROOT / "Archive/plan-as-delivered/26-08-22_dengueForecastingCase_asDelivered.md"
LIVE = ROOT / "Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md"
OUT = ROOT / "AI-generated/plan-drift"

AGENCIES = ("human-set", "agent-on-human-assessment", "agent-autonomous")


def delivered_text() -> str:
    """The delivered plan with the archive marker removed.

    `AGENTS.md` §8 puts `(IS_SHADOW)` on line 2 of everything under `Archive/`, and the
    file's own provenance record says that is the only change made to it. Leaving it in
    would report one deleted line that the project never wrote.
    """
    lines = DELIVERED.read_text().splitlines(keepends=True)
    if lines[1].strip() != "(IS_SHADOW)":
        raise SystemExit(f"line 2 of {DELIVERED.name} is not the archive marker; "
                         "the provenance record says it should be")
    return "".join(lines[:1] + lines[2:])


def survival(old: list[str], new: list[str]) -> dict:
    """How much of `old` is still present in `new`, by difflib's matching blocks."""
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    kept = sum(block.size for block in matcher.get_matching_blocks())
    return {"delivered": len(old), "live": len(new), "survived": kept,
            "deleted": len(old) - kept, "added": len(new) - kept,
            "survival_fraction": round(kept / len(old), 4) if old else None}


def sections(text: str) -> dict[str, list[str]]:
    """Top-level `## ` sections, heading text -> body lines (heading included)."""
    out: dict[str, list[str]] = {}
    current = "(preamble)"
    out[current] = []
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            current = line[3:].strip()
            out.setdefault(current, [])
        out[current].append(line)
    return out


LEDGER_ROW = re.compile(r"^\|\s*(\d+|—)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|"
                        r"\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$")


def ledger(text: str) -> dict[str, dict]:
    """The batch ledger, keyed by the `#` column.

    Read from the `## 6. Batch ledger` section only. The document has a second table of
    the same shape further down -- `## Batch ledger — reports` -- and counting both would
    double every batch.
    """
    body = sections(text).get("6. Batch ledger", [])
    rows: dict[str, dict] = {}
    for line in body:
        m = LEDGER_ROW.match(line)
        if not m or m.group(1) == "#":
            continue
        num, phase, aim, status, report = (g.strip() for g in m.groups())
        # The delivered ledger carries three placeholder rows -- phases C, D and E, whose
        # batches batch 5 was to write -- and all three have `—` in the `#` column. Keying
        # on that column alone collapsed them into one, and undercounted by two the part
        # of the plan that was deliberately left blank. Distinguished by phase, which is
        # what actually tells them apart.
        key = num if num != "—" else f"—{phase}"
        rows[key] = {"phase": phase, "aim": aim, "status": status, "report": report}
    return rows


DECISION_HEADING = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})\s*—\s*(.+?)\s*$")


def decisions(text: str) -> list[dict]:
    """Every row of every table under `## 4b`, with the heading that settled it."""
    body = sections(text).get("4b. Decisions settled during execution", [])
    out: list[dict] = []
    date = settled_by = ""
    for line in body:
        m = DECISION_HEADING.match(line)
        if m:
            date, settled_by = m.group(1), m.group(2)
            continue
        if not line.startswith("|") or not date:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        if cells[0] == "Decision" or set(cells[0]) <= {"-", ":", " "}:
            continue
        out.append({"date": date, "settled_by": settled_by,
                    "decision": cells[0], "agency": cells[2]})
    return out


def commits() -> list[dict]:
    """Every commit that touched the live plan, oldest first, with its line churn."""
    fmt = "%x01%H%x02%aI%x02%s"
    raw = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--reverse", "--follow", "--numstat",
         f"--format={fmt}", "--", str(LIVE.relative_to(ROOT))],
        capture_output=True, text=True, check=True).stdout
    out: list[dict] = []
    for chunk in raw.split("\x01"):
        if not chunk.strip():
            continue
        head, *rest = chunk.splitlines()
        sha, when, subject = head.split("\x02")
        added = removed = 0
        for line in rest:
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                added += int(parts[0])
                removed += int(parts[1])
        out.append({"commit": sha[:9], "date": when[:10], "subject": subject,
                    "lines_added": added, "lines_removed": removed})
    return out


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old, new = delivered_text(), LIVE.read_text()

    by_line = survival(old.splitlines(), new.splitlines())
    by_word = survival(old.split(), new.split())

    old_sections, new_sections = sections(old), sections(new)
    section_rows = []
    for name, body in old_sections.items():
        live_body = new_sections.get(name)
        s = survival(body, live_body) if live_body is not None else None
        section_rows.append({
            "section": name, "in_live": live_body is not None,
            "delivered_lines": len(body),
            "live_lines": len(live_body) if live_body is not None else 0,
            "survived_lines": s["survived"] if s else 0,
            "survival_fraction": s["survival_fraction"] if s else 0.0})
    for name, body in new_sections.items():
        if name not in old_sections:
            section_rows.append({
                "section": name, "in_live": True, "delivered_lines": 0,
                "live_lines": len(body), "survived_lines": 0, "survival_fraction": ""})
    write_csv(OUT / "sections.csv", section_rows,
              ["section", "in_live", "delivered_lines", "live_lines",
               "survived_lines", "survival_fraction"])

    old_ledger, new_ledger = ledger(old), ledger(new)
    ledger_rows = []
    for num in sorted(set(old_ledger) | set(new_ledger),
                      key=lambda n: (not n.isdigit(), int(n) if n.isdigit() else 0, n)):
        d, l = old_ledger.get(num), new_ledger.get(num)
        ledger_rows.append({
            "batch": num,
            "in_delivered": d is not None,
            "in_live": l is not None,
            "delivered_aim": d["aim"] if d else "",
            "live_aim": l["aim"] if l else "",
            "live_status": l["status"] if l else "",
            "aim_unchanged": bool(d and l and d["aim"] == l["aim"])})
    write_csv(OUT / "ledger.csv", ledger_rows,
              ["batch", "in_delivered", "in_live", "delivered_aim", "live_aim",
               "live_status", "aim_unchanged"])

    decision_rows = decisions(new)
    write_csv(OUT / "decisions.csv", decision_rows,
              ["date", "settled_by", "decision", "agency"])

    tally = {a: sum(1 for r in decision_rows if r["agency"] == a) for a in AGENCIES}
    unrecognised = [r for r in decision_rows if r["agency"] not in AGENCIES]

    commit_rows = commits()
    write_csv(OUT / "commits.csv", commit_rows,
              ["commit", "date", "subject", "lines_added", "lines_removed"])

    # A section the delivered plan named and the live plan still names, with none of its
    # delivered lines left, is a section rewritten rather than kept -- a different finding
    # from one that was deleted, and the two are easy to conflate in prose.
    kept_named = [r for r in section_rows if r["in_live"] and r["delivered_lines"]]
    summary = {
        "delivered_file": str(DELIVERED.relative_to(ROOT)),
        "live_file": str(LIVE.relative_to(ROOT)),
        "measured_at_commit": subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()[:9],
        "by_line": by_line,
        "by_word": by_word,
        "sections": {
            "delivered": sum(1 for r in section_rows if r["delivered_lines"]),
            "live": sum(1 for r in section_rows if r["in_live"]),
            "delivered_and_still_named": len(kept_named),
            "delivered_and_gone": sum(1 for r in section_rows
                                      if r["delivered_lines"] and not r["in_live"]),
            "new_since_delivery": sum(1 for r in section_rows if not r["delivered_lines"]),
            "least_survived": min(kept_named, key=lambda r: r["survival_fraction"])["section"],
            "fully_survived": [r["section"] for r in kept_named
                               if r["survival_fraction"] == 1.0]},
        "ledger": {
            "delivered_named_batches": sum(1 for r in ledger_rows if r["in_delivered"]
                                           and r["batch"].isdigit()),
            "delivered_placeholders": sum(1 for r in ledger_rows if r["in_delivered"]
                                          and not r["batch"].isdigit()),
            "live_batches": sum(1 for r in ledger_rows if r["in_live"] and r["batch"].isdigit()),
            "added_since_delivery": sum(1 for r in ledger_rows
                                        if r["in_live"] and not r["in_delivered"]),
            "aim_unchanged": sum(1 for r in ledger_rows if r["aim_unchanged"]),
            "aim_reworded": sum(1 for r in ledger_rows if r["in_delivered"] and r["in_live"]
                                and not r["aim_unchanged"])},
        "decisions": {
            "total": len(decision_rows),
            "by_agency": tally,
            "unrecognised_agency": [r["agency"] for r in unrecognised],
            "settling_occasions": len({(r["date"], r["settled_by"]) for r in decision_rows}),
            "human_initiated_occasions": len(
                {(r["date"], r["settled_by"]) for r in decision_rows
                 if "the human" in r["settled_by"]}),
            # Who settled the occasion and who made the decision are different questions,
            # and the second is the one that matters. A batch's own table can carry a
            # `human-set` row -- the batch reported, the human ruled, and the ruling was
            # written up where the batch's other decisions are. Counting only the
            # occasions would attribute those to the agent.
            "human_set_at_batch_occasions": sum(
                1 for r in decision_rows if r["agency"] == "human-set"
                and "the human" not in r["settled_by"]),
            "decisions_at_human_occasions": sum(
                1 for r in decision_rows if "the human" in r["settled_by"]),
            "by_agency_fraction": {a: round(tally[a] / len(decision_rows), 4)
                                   for a in AGENCIES} if decision_rows else {}},
        # The first commit is the delivered plan arriving in the repository, not a change
        # to it, so its churn is reported separately. Adding it to the total would count
        # the whole original document as drift.
        "commits": {
            "count": len(commit_rows),
            "first": commit_rows[0]["date"] if commit_rows else None,
            "last": commit_rows[-1]["date"] if commit_rows else None,
            "lines_added": sum(r["lines_added"] for r in commit_rows),
            "lines_removed": sum(r["lines_removed"] for r in commit_rows),
            "revisions_after_the_first": len(commit_rows) - 1,
            "lines_added_after_the_first": sum(r["lines_added"] for r in commit_rows[1:]),
            "lines_removed_after_the_first": sum(r["lines_removed"] for r in commit_rows[1:]),
            "largest_revision": max(commit_rows[1:], key=lambda r: r["lines_added"])
            if len(commit_rows) > 1 else None,
            "three_largest_revisions": sorted(
                commit_rows[1:], key=lambda r: -r["lines_added"])[:3],
            # A revision whose subject opens with a batch number is that batch writing up
            # what it had just done; the rest are the occasions the plan was revised for
            # some other reason. Classified here rather than in prose, because "most of
            # them were routine" is exactly the kind of impression this project asks to
            # have a number attached to.
            "revisions_naming_a_batch": sum(
                1 for r in commit_rows[1:] if r["subject"].lower().startswith("batch")),
            "revisions_not_naming_a_batch": [
                {"date": r["date"], "subject": r["subject"]} for r in commit_rows[1:]
                if not r["subject"].lower().startswith("batch")]},
    }
    (OUT / "plan_drift.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(json.dumps(summary, indent=2))
    print(f"\n-> {OUT.relative_to(ROOT)}/ : plan_drift.json, sections.csv, "
          f"ledger.csv, decisions.csv, commits.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
