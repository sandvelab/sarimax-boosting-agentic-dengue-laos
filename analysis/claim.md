# Claim

Develop, as autonomously as the setup allows, a two-stage forecasting ensemble for monthly
dengue case counts across the provinces of Laos — a SARIMAX-family model (stage 1) whose
residuals are corrected by a second model (stage 2, family open) — and establish whether the
second stage earns its place against stage 1 alone, the required baselines, and the prior
project's externally reported reference, on Chap's dataset for Laos.

Full aim, success criteria and non-negotiables:
`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`.

## Children

kind: sub-analyses
main-path: (none yet)

## Environment

inherits: the project main environment (`environment/`) — not yet pinned; see
`environment/README.md`.

## Answers

Batch 2: the data partitions and characterises cleanly (`01_data`), the project's own CRPS
implementation is verified (`00_metric`), and stage 1 alone — a per-province SARIMAX(1,1,1)×
(1,0,0,12) on raw counts, refit every split — scores **mean CRPS 26.05** over 371 cells on
the development backtest, with no fit failures. The plan's actual question (§2: does stage 2
improve on this?) is not yet answered — stage 2 has not been built.

Batch 3: both required baselines are built (`03_baselines`) and stage 1 beats each of them on
the identical 371-cell set — **7.99% lower mean CRPS than persistence (28.32), 3.20% lower
than seasonal climatology (26.91)**. This backtest resolves enough to separate stage 1 from
naive forecasting, with a modest margin over climatology whose stability across reasonable
alternative choices is deferred to the stability phase (plan §4). Stage 2 has still not been
built.

Batch 4: the residual-correction contract and first stage-2 candidate are built
(`04_stage2/a_linearLags`) — a linear regression on stage 1's lag-12 residual and calendar
month, added to stage 1's forecast mean. It does **not** earn its place: mean CRPS 26.26
against stage 1 alone's 26.05, **0.78% worse**, with essentially unchanged interval coverage.
The plan's central question (§1–§2: does *some* stage-2 family beat stage 1 alone?) is not yet
answered — one candidate failing does not settle it; batches 5–7 add a tree-based candidate
and a non-tree structural candidate as further alternatives before any conclusion is drawn.
