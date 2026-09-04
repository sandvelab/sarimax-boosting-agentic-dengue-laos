# Provenance — the plan's own drift

## `plan_drift.json`, `sections.csv`, `ledger.csv`, `decisions.csv`, `commits.csv`

```
result:              plan_drift.json, sections.csv, ledger.csv, decisions.csv, commits.csv
script:              AI-internal/useful-scripts/plan_drift.py
                     sha256:8c9338e201371011d812e876b1f200339952f8acfea0eba0567cbcfbfb149987
invocation:          .venv/bin/python AI-internal/useful-scripts/plan_drift.py
                     (from the repository root)
inputs:              Archive/plan-as-delivered/26-08-22_dengueForecastingCase_asDelivered.md
                     sha256:dd6dc798b2caa7972bb3985fd0c05b915a45828b2bc826ffaadcfa73bc44143d
                     Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md
                     sha256:f532a6bb6228d186c452c3f0e694b04ff393ec8eb38e11845a8954d78f0ad6bd
                     and `git log --follow` over the second of those
environment:         .venv — CPython 3.13.7. Standard library only: difflib, csv, json, re.
                     Not the analysis environment, because this measures the plan and not
                     the data.
seeds:               none — the measurement is deterministic
commit:              ad7e64f
instructions-commit: ad7e64f
node:                not a node — evidence about the method, like the determinism checks
produced:            2026-08-31, batch 18
```

**What it establishes.** How much of the delivered research plan survived execution, section
by section; how the batch ledger grew from seven named batches and three placeholders to
twenty-two; how the 169 decisions in §4b divide by agency; and what the 27 commits that
touched the plan did to it. Read in `26-08-31_planDrift.md`, which quotes these files and
computes nothing of its own.

**Why it re-derives everything on each run rather than accumulating.** Both inputs are files
in the repository at a known commit, so the measurement is a pure function of a commit and
there is nothing to accumulate. Re-running it at a later commit produces that commit's
drift, which is the intended behaviour — the figures quoted in the report are the ones from
the commit named above, and `measured_at_commit` in `plan_drift.json` says which.

**Why the archive marker is stripped from the delivered file before comparing.** `AGENTS.md`
§8 puts `(IS_SHADOW)` on line 2 of everything under `Archive/`, and the delivered plan's own
provenance record says that is the only change made to it. Comparing without stripping it
would report one deleted line that the project never wrote. The script asserts the marker is
there rather than assuming it, and stops if it is not.

---

## `26-09-05_planDrift.md` — the same measurement at the end of the project

```
result:              AI-generated/plan-drift/26-09-05_planDrift.md
                     plan_drift.json, sections.csv, ledger.csv, decisions.csv, commits.csv
                     — **rewritten by this run**; see the note below
script:              AI-internal/useful-scripts/plan_drift.py
                     sha256:8c9338e201371011d812e876b1f200339952f8acfea0eba0567cbcfbfb149987
invocation:          .venv/bin/python AI-internal/useful-scripts/plan_drift.py
inputs:              Archive/plan-as-delivered/26-08-22_dengueForecastingCase_asDelivered.md
                     Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md
                     and that file's git history
environment:         .venv (repository machinery) — CPython 3.13.7
seeds:               none — the measurement is deterministic
commit:              ff29c1c4f (`measured_at_commit` in plan_drift.json)
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                not a node — evidence about the method, like the determinism checks
produced:            2026-09-05, batch 19
```

**What it establishes.** The same four things at the end of the project that batch 18
established in the middle of it: 89.1 % of the delivered plan's lines survive byte for byte
while the document has grown from 468 lines to 1 354; all twelve delivered sections remain
and one is new; the ledger has gone from seven named batches and three placeholders to
thirty-one; and the 247 decisions in §4b divide 85.4 % `agent-autonomous`, 6.9 %
`human-set`, 3.6 % `agent-on-human-assessment`.

**The five data files hold this run and no longer hold batch 18's.** The script writes to
fixed filenames, so re-running it overwrote the figures `26-08-31_planDrift.md` quotes. That
narrative is still an accurate account of what the measurement said at batch 18 — its
numbers are in its own text and in git history at `ad7e64f` — but the files beside it now
answer for 2026-09-05. **This is a real gap in the project's record-keeping**, of exactly the
kind Rule 5 exists to prevent, and it is reported in the reproducibility report's *what does
not hold* section rather than repaired at the end of the project: repairing it means changing
where the script writes, which changes a script whose output is a reported result, on the
last batch, for a file whose earlier values are recoverable from git.

**agency:** agent-autonomous.
