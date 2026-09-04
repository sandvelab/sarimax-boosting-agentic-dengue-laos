# Provenance — reproducibility report

One section per document. Append; never overwrite an existing section.

---

## `26-09-05_reproducibilityReport.md` and `repro_inventory.json` — 2026-09-05, batch 19

```
result:              AI-generated/repro-report/26-09-05_reproducibilityReport.md
                     AI-generated/repro-report/repro_inventory.json
script:              AI-internal/useful-scripts/repro_inventory.py
                     sha256:97051632b77c7bf8c310ebb39832fa435079bfb46db84918b2b24f544e38855a
                     (the inventory; the narrative is written by hand from it)
invocation:          .venv/bin/python AI-internal/useful-scripts/repro_inventory.py --root .
inputs:              the analysis tree at commit 922506bb8 — every claim.md, every
                     results/ directory, every provenance record
                     Human-AI-collaboration/claims/claims.md
                     environment/lock.txt
                     the repository's git history
                     AI-generated/plan-drift/plan_drift.json  (the agency figures in §4)
                     AI-generated/hierarchical-report/README.md  (the page and combination
                     counts in §1)
environment:         .venv (repository machinery) — CPython 3.13.7
seeds:               none. The inventory is a walk and a set of counts.
commit:              922506bb8 (`counted_at_commit` in repro_inventory.json)
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                not a node — a report about the project rather than a result of it
produced:            2026-09-05
alternatives-considered: writing the report's counts from the batch reports, which hold most
                     of them already. Rejected: those figures were correct when written and
                     several have since moved, and a closing report that quotes a stale
                     count is the failure the report's own §5 is about. Everything countable
                     is counted at the commit the report is written at.
agency:              agent-autonomous. That the report exists is Rule 10's; its content, the
                     inventory script and the judgments in §5 are the agent's.
```

**What the inventory script found that the report would otherwise have got wrong.** Walking
`AI-internal/useful-scripts/` for script files counted **15 078 files and 6 094 813 lines**,
because `/validate cleanroom` clones the whole repository into a subdirectory of it and
builds environments there. The count now comes from `git ls-files`, which knows what belongs
to the project where the filesystem does not. The same walk also counted the claim
collection's own fenced *example* block as a claim, putting the collection at 48 and
reporting one broken grounding pointer that is documentation rather than a claim.

**Why §5 is longer than §1.** `/repro-report` says section 5 is not optional and is the
section a critical reader will value most. Ten things are listed there, of which four were
found while writing this report rather than before it.
