# Task history

One line per completed task. Written by `/log-tasks`; expanded entries in
`ai_task_details.md`.

This log is **part of the published record** of how the work came about. Write entries a
reader who was not present can follow, and keep them honest about what did not work.

- T1 (2026-09-20): Reset the repository from its prior, completed project (EWARS-comparison
  dengue forecasting, released at `github.com/sandvelab/veridical-agentic-dengue-laos`) to a
  blank scaffold, keeping only the reused archived raw data and the generic framework
  machinery, and ran batch 1 of a new plan — a two-stage SARIMAX/residual-correction ensemble
  for the same dataset. Wrote the new plan, `readme-at-start.md` and `README.md`; verified the
  reused dataset's checksums; created `.venv`; wrote the root `analysis/claim.md`. One
  methodological change under Rule 4: `node.py`'s generated `run.sh` template had a
  project-specific path (`environment/chapenv/`) leaked into generic machinery, fixed to
  `environment/env/`. `/validate invariants` passes except `git` (resolved by this batch's
  commit). Report: `26-09-20_b01_orientAndSetUp.md`. Three open questions raised for the
  human: the backtest scheme, whether to keep citing the prior project's EWARS score, and
  environment scoping (deferred to batch 2). **Same day, in dialogue**: the human settled the
  first two — reuse the prior project's backtest scheme (`3/8/3`) as the default, and drop the
  EWARS citation entirely rather than keep it as context. Recorded in the plan's §4b and
  propagated to §1, §2, §4 and `readme-at-start.md`; pushed to the remote.
