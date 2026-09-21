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
main-path: -

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

Batch 7: `04_stage2`'s main path is `a_linearLags` — the least-bad of the three candidates
built (mean CRPS 26.26 vs. stage 1's 26.05), not an endorsement that it earns its place. **The
plan's central comparison (§1–§2), answered as of this batch: no stage-2 family tried so far
beats stage 1 alone.** All three families explored — a plain linear correction, gradient-
boosted trees, and a Bayesian ridge regression — lose to stage 1, by 0.78%, 6.25% and 7.73%
mean CRPS respectively, all on the identical minimal input (stage 1's lag-12 in-sample
residual and cyclical calendar month). That input set was fixed once in batch 4 and reused
unexamined by batches 5–6; this batch logs it as an explicit, unexplored fork rather than a
silent default (`04_stage2/claim.md`) — richer inputs (additional lags, the rainfall/
temperature/humidity/population columns already present in the archived dataset, province
identity used structurally) remain untried, so "no stage-2 family earns its place" is a
finding about this minimal input, not a closed question about stage 2 in general. Persistence
(28.32) and seasonal climatology (26.91) remain worse than stage 1 alone (batch 3), so the
honest ranking on development data, best to worst, is: **stage 1 alone (26.05) < a_linearLags
(26.26) < seasonal climatology (26.91) < b_gradientBoosting (27.68) < c_bayesianRidge (28.07) <
persistence (28.32)**. This closes phase C; phase D (stability, ledger rows 8–10) is next.

Batch 8: the human chose to try the most plausible untried fork named by batch 7 — climate
covariates — before moving to phase D. A fourth candidate, `04_stage2/d_linearClimate`, adds
lag-12 rainfall, mean temperature and mean relative humidity to `a_linearLags`'s exact input
and family (isolating the input question from the family question already explored by
`b_gradientBoosting` and `c_bayesianRidge`). **It does not earn its place either: mean CRPS
26.85, 3.05% worse than stage 1 alone and 2.25% worse than `a_linearLags` on the minimal
input.** `a_linearLags` remains `04_stage2`'s main path. The updated ranking, best to worst:
**stage 1 alone (26.05) < a_linearLags (26.26) < d_linearClimate (26.85) < seasonal
climatology (26.91) < b_gradientBoosting (27.68) < c_bayesianRidge (28.07) < persistence
(28.32)**. This narrows but
does not close the climate question: a non-linear family given the same climate input, and a
genuinely forward (rather than lag-12 proxy) climate signal, remain untried
(`04_stage2/claim.md`).

Batch 9: at the human's direction to keep exploring and to try an existing model from
`github.com/chap-models`, a fifth candidate, `04_stage2/e_pooledRandomForest`, adapts
`chap-models/rwanda_random_forest` — a random forest pooled across all 17 provinces in one
shared fit per split, rather than every prior candidate's independent per-province fits, on
`d_linearClimate`'s exact input. **This is the first stage-2 candidate to beat stage 1 alone
on mean CRPS: 25.89 against 26.05 (-0.63%), and -3.57% against `d_linearClimate` on the
identical input it isolates pooling from.** But it does not earn its place either: empirical
interval coverage collapses to **64.4%** against a nominal 90% (every prior candidate stayed
near stage 1's own 82.7-86.8%), which plan §2 explicitly disqualifies ("a model that wins on
mean CRPS while being badly calibrated has not won"). The mechanism, traced in
`04_stage2/e_pooledRandomForest/results/coverage_collapse_diagnosis.json`: 27.5% of its
corrected forecasts are negative (impossible for a case count), concentrated in the
lowest-case-count provinces (Pearson r=-0.53 between a province's mean case count and its
negative-forecast rate) — the pooled correction, shaped by provinces spanning under 1 to over
150 mean monthly cases, overshoots on scales it was not specifically fit to. The pooling
*idea* is not ruled out by this, only this implementation of it; a scale-preserving version
(a per-province offset or standardisation before pooling) is logged as untried. The ranking
among candidates that clear both the CRPS and calibration bars is unchanged from batch 8:
**stage 1 alone (26.05) < a_linearLags (26.26) < d_linearClimate (26.85) < seasonal
climatology (26.91) < b_gradientBoosting (27.68) < c_bayesianRidge (28.07) < persistence
(28.32)**, with `e_pooledRandomForest` reported alongside as CRPS-best-but-miscalibrated
rather than folded into it. Phase D (stability) is next, renumbered to ledger rows 10–12
unless the human chooses to keep exploring further.

Batch 10: at the human's direction, a systematic second iteration rather than a sixth ad-hoc
candidate — a literature search, a diagnostic node (`05_residualStructure`) on what stage 1's
out-of-sample errors are and what predicts them, then candidates built on both. The
diagnostics explain the five failures: candidates a–e trained on stage 1's in-sample one-step
residual, which is essentially white, while the h-step out-of-sample error a stage 2 must
correct carries a level-dependent over-prediction, a calendar bias and a horizon effect —
modest, predictable structure — alongside unpredictable reporting-regime breaks in 2008–09
that make up the entire coverage deficit. Two candidates trained on that error inside each
training window, pooled across provinces on the standardised scale, **both beat stage 1 alone
on mean CRPS with improved coverage: `04_stage2/f_oosErrorRidge` 25.63 (−1.64%, coverage
84.6%) and `04_stage2/g_oosErrorBoosting` 25.16 (−3.41%, coverage 85.7%), against 26.05 and
82.7%** — the first candidates to clear both of plan §2's bars. **The plan's central
comparison, as of this batch: a residual-correction stage can earn its place, when it is
trained on the right target.** The margin is modest, sits in four provinces and the later
splits, and loses ground in Savannakhet and Vientiane Capital; `g_oosErrorBoosting` is
promoted to `04_stage2`'s main path on this development evidence, and whether the margin
survives reasonable alternative choices is now the stability phase's question (ledger rows
11–13). Ranking among candidates clearing both bars: **g_oosErrorBoosting (25.16) <
f_oosErrorRidge (25.63) < stage 1 alone (26.05) < a_linearLags (26.26) < d_linearClimate
(26.85) < seasonal climatology (26.91) < b_gradientBoosting (27.68) < c_bayesianRidge (28.07)
< persistence (28.32)**.

Batch 11: phase D opens with `06_stability`. The development perturbation set is planned,
costed and frozen (`06_stability/results/manifest.csv`, 40 rows: 6 tier-1 siblings already in
the tree, 29 tier-2 parametric perturbations of stage 1's specification, the training window
and scheme, and every constant in the main-path stage 2, all planned; 5 tier-3 alternatives
not run, each with its reason). Re-running the whole existing tree costs 87 seconds and
reproduces every output byte for byte, so the compute budget is set provisionally at one hour
and excludes nothing planned. **Nothing about the central comparison changes in this batch**;
batch 12 runs the set and batch 13 reports the distribution of conclusions across it.

Batch 12: the frozen set ran in full (29 perturbations, 1,937 s of a 3,600 s ceiling; the
runner first reproduced the main path's per-cell scores value for value). Every one of the 29
tier-2 perturbations — stage 1's specification, the training window, Chap's default scheme,
the modelability threshold, and every constant of the main-path stage 2 — keeps the two-stage
ensemble ahead of stage 1 alone on mean CRPS with coverage not worse, from −0.70% to −10.64%
(`06_stability/results/conclusions.csv`). The only rows where it loses are the four early
siblings trained on the in-sample residual. The distribution, and which choices the margin
turns on, are batch 13's report.
