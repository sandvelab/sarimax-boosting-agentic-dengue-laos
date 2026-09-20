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
- T2 (2026-09-20): Resumed after a machine crash mid-close-out of batch 2, then ran batches
  3–7. Closing batch 2: fixed a relative-path bug in three provenance records (one `../` too
  many, pointing outside `analysis/scripts/lib/`), re-verified every affected sha256 against
  the actual files, filled in `02_stage1`'s deferred commit hash, and wrote its batch report.
  Batch 3 built the required baselines (`03_baselines/`: persistence 28.32, seasonal
  climatology 26.91 mean CRPS) — stage 1 (26.05) beats both. Batch 4 built the stage-2
  residual-correction contract and its first candidate (`04_stage2/a_linearLags`, OLS on
  stage-1's lag-12 residual + calendar month): 26.26, 0.78% worse than stage 1 alone — the
  first honest negative result on the project's central question. Batch 5 added a tree-based
  candidate (`b_gradientBoosting`, pinning `scikit-learn`): 27.68, 6.25% worse. Batch 6 added
  a Bayesian candidate (`c_bayesianRidge`, using its own posterior predictive variance rather
  than borrowing stage 1's): 28.07 CRPS but the best-calibrated of the three (86.8% vs.
  nominal 90% coverage). Batch 7 formalised `a_linearLags` as `04_stage2`'s main path (the
  least-bad candidate, not an endorsement), updated the root `analysis/claim.md` to state
  plainly that no stage-2 family tried beats stage 1 alone, and logged climate covariates and
  population — both already present in the development data, neither yet used by any stage-2
  candidate — as an explicit, unexplored input-space fork rather than a silent default.
  `readme-at-start.md`'s status and environment rows, stale since batch 2, brought current.
  `/validate invariants` passes clean after every batch's close-out commit. Reports:
  `26-09-20_b02_dataAndStage1.md` through `26-09-20_b07_stage2MainPathAndInputForks.md`.
  Nothing pushed to the remote this session.
- T3 (2026-09-20): Ran batch 8, after asking the human to settle the open question batch 7
  left (move to phase D now, or try richer stage-2 inputs first) — the human chose to explore
  inputs. Inserted a new ledger row 8 into the plan (backed up first), renumbering the
  stability phase and everything after it from rows 8–15 to 9–16, and logged the choice in the
  plan's §4b as human-set. Built a fourth stage-2 alternative, `04_stage2/d_linearClimate`:
  `a_linearLags`'s exact OLS family with lag-12 rainfall, mean temperature and mean relative
  humidity added — lag-12 rather than contemporaneous, for the same forecast-time-leakage
  reason `a_linearLags` used lag-12 for the residual, and the same family as `a_linearLags` on
  purpose, to isolate the input question from the model-family question batches 5–6 already
  answered. Result: mean CRPS 26.85, worse than stage 1 alone (26.05, +3.05%) and worse than
  `a_linearLags` on the minimal input (26.26, +2.25%) — the most plausible untried fork named
  in batch 7 did not change the central finding. `a_linearLags` remains `04_stage2`'s main
  path; all four stage-2 candidates built so far lose to stage 1 alone. Updated
  `04_stage2/claim.md` and the root `analysis/claim.md` with the result and what remains
  untried (a non-linear family given climate, a genuinely forward climate signal, population,
  cross-province pooling). Brought `AI-generated/batch-reports/README.md` current — it had
  gone stale after batch 1, never updated for batches 2–7. `/validate invariants` passes
  except `git`, which fails only on the pre-existing, out-of-scope untracked `.idea/`. Report:
  `26-09-20_b08_stage2LinearClimate.md`. Nothing pushed to the remote this session.
