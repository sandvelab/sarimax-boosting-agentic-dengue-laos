# plan-drift

How far the live research plan has moved from the plan as it was delivered, measured rather
than described.

Phase E asks for this as a reported result, not as bookkeeping: it is the project's only
direct evidence on how far an agentic system can be handed a research plan and left to run
it, which is a question the TrustAgentic proposal asks and which nothing else here answers.

The measurement is a script, because `AGENTS.md` §1 does not allow a figure in prose to have
been counted by eye. `AI-internal/useful-scripts/plan_drift.py` diffs
`Archive/plan-as-delivered/` against `Human-input/Plans for AI generation/`, parses §4b's
agency column and the batch ledger, and reads the plan's commit history.

## Currently

- `26-08-31_planDrift.md` — batch 18. The plan did not drift, it grew: 89.1% of the
  delivered lines survive byte-for-byte while the document is five times its delivered
  length. The aim and the pre-fixed decisions survive intact; the budget and the ledger,
  both labelled provisional at delivery, are what moved. 85.8% of the 169 recorded decisions
  were the agent's alone, and the human's 14.2% are on the criterion and the constraints.
- `plan_drift.json`, `sections.csv`, `ledger.csv`, `decisions.csv`, `commits.csv` — what the
  script wrote, and where every figure in the report is read from.
- `provenance.md` — the record for all five.

Re-run it with `.venv/bin/python AI-internal/useful-scripts/plan_drift.py`. The figures are a
function of the commit it is run at, and `measured_at_commit` in `plan_drift.json` says which.
