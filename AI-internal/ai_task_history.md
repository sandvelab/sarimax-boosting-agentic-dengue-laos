# Task history

One line per completed task. Written by `/log-tasks`; expanded entries in
`ai_task_details.md`.

This log is **part of the published record** of how the work came about. Write entries a
reader who was not present can follow, and keep them honest about what did not work.

- T1 (2026-08-23): Batch 1 of the dengue-forecasting plan — read the five source documents, initialised git and `.venv` (CPython 3.13.7), filled in `readme-at-start.md` and the root `analysis/claim.md`, created `AI-generated/batch-reports/`, and wrote the batch-1 report with ten inconsistencies found in the instructions and source material. No analysis, no data, no Chap. `/validate invariants` passes. **Extended same day**: the two questions the report raised were settled in dialogue — the reference model is `chapkit_ewars_model` and the stability spread is carried forward to the held-out year — and the plan was revised accordingly, the plan as delivered archived, and a §4b decision log opened with the agency recorded on each decision.
- T2 (2026-08-23): Batch 2 of the dengue-forecasting plan — installed and pinned `chap-core==2.1.0` on CPython 3.13.0 as a project-local environment, verified the pin by rebuilding it to an identical 174-package set, and ran one `chap eval` end to end on a pinned five-region example dataset. Established the model contract, the backtest arithmetic and the exact form of Chap's CRPS, and answered all five questions `chapOrientation.md` §5 left open. Report: `26-08-23_b02_chapSetup.md`. `/validate invariants` passes.
