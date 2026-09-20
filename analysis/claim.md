# Claim

Develop, as autonomously as the setup allows, a two-stage forecasting ensemble for monthly
dengue case counts across the provinces of Laos — a SARIMAX-family model (stage 1) whose
residuals are corrected by a second model (stage 2, family open) — and establish whether the
second stage earns its place against stage 1 alone and the required baselines, on the same
Laos dataset. No external reference model is used or cited (plan §1, §2, §4b, human-set
2026-09-20) — the comparison is entirely internal to this project's own models and data.

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

Batch 5: a second stage-2 candidate, gradient-boosted regression trees
(`04_stage2/b_gradientBoosting`) on the identical minimal input as `a_linearLags` (lag-12
residual, calendar month), also does **not** earn its place: mean CRPS 27.68, **6.25% worse**
than stage 1 alone, and worse than the linear candidate too. Two candidates have now failed
on the same minimal input — batches 6–7 still owe a non-tree, non-linear candidate and a
richer input set before the plan's central question can be answered either way.

Batch 6: a third stage-2 candidate, Bayesian ridge regression (`04_stage2/c_bayesianRidge`) on
the identical minimal input, combining its own posterior predictive variance with stage 1's
into the final interval, is the worst of the three on CRPS — **28.07, 7.73% worse** than stage
1 alone — despite being the best-calibrated (86.8% empirical coverage against a nominal 90%,
vs. 82.7% for stage 1 alone): the wider interval its genuine calibration attempt buys costs
more CRPS than the mean correction recovers. All three stage-2 candidates built so far lose to
stage 1 alone on this minimal input
(`04_stage2/c_bayesianRidge/results/all_candidates_comparison.json`). This does not settle the
plan's central question on a richer input — batch 7 is reserved for the formal main-path
decision among the three and for exploring what stage 2 is allowed to see (more lags,
covariates, population) as its own fork.
