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
