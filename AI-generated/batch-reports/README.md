# Batch reports

One report per executed batch of
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`. The plan is run one
batch per invocation of `/do`; each batch writes its report here and links it from the plan's
batch ledger.

Named `YY-MM-DD_bNN_camelCaseName.md`, where `NN` is the batch number. **A report is never
overwritten.** If a batch is redone, the new report is a new file and both stay.

Every batch ends in exactly one of three states, stated at the top of its report:

- **done — produced** — it created or changed something in the analysis, and the report says
  what and where;
- **done — expanded** — it produced no analysis output but replaced itself with more concrete
  batches, and the report says what made those possible;
- **blocked** — it could not proceed, and the report says exactly what is missing and what
  would unblock it.

These reports are the project's own running account of itself, so they are not regenerable
in the way the rest of `AI-generated/` is: they record what happened at a point in time, and
re-running a batch produces a different report rather than the same one.

## Currently here

- `26-08-23_b01_orientAndSetUp.md` — batch 1, phase A: orientation and repository set-up.
