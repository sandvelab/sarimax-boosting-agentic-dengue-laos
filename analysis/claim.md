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

Batch 13: the stability report (`06_stability/results/distribution.json`; claims C1–C7).
**On development data the central conclusion — a stage 2 trained on stage 1's multi-step
out-of-sample error earns its place — is stable in sign across every reasonable alternative
run** (29 of 29, coverage never worse), **and unstable in size**: the margin is −3.41% on the
main path, between −2.41% and −4.19% for half the perturbations, as large as −10.6% when
stage 1 is specified worse, and as small as −0.70% when the in-window training errors come
from a true rolling refit rather than the fixed-parameter shortcut. The gain sits in
Khammouane, Salavan, Bokeo and Xiangkhouang in every combination and never in Savannakhet or
Vientiane Capital; it is a two-and-three-months-ahead gain. The predictive-family fork that
could repair coverage was not run. Phase D closes; batch 14 freezes the holdout manifest.

Batch 14 (human-set: stage 1 is not repaired; stage 2 explored further; one configuration
annotated as main now): stage 1's weaknesses are documented in one file-grounded place
(`05_residualStructure/results/stage1_weaknesses.json`, `02_stage1/claim.md`) — six of them,
each with evidence, effect, whether a stage 2 can address it, and the stage-1 fork not taken.
Three stage-2 configurations were built as nodes: the minimal level-only input
(`h_levelOnlyBoosting`, 24.35, −6.53%, coverage 85.2%), the bounded correction
(`i_boundedBoosting`, 24.53, −5.85%, 85.7%) and both (`j_levelOnlyBoundedBoosting`, 24.29,
−6.78%, 85.2%); all clear both bars. **`h_levelOnlyBoosting` is `04_stage2`'s main path**, by a
rule written before the combination's result was seen (lowest development CRPS with coverage
not worse; tie within 0.1 broken by splits improved, then simplicity). **The central
comparison now stands at −6.53% on development data**, the third selection on the same
cells; the holdout is the guard. Stability around `h` (v2) is planned here and run next.

Batch 15: the development stability set re-run around `h_levelOnlyBoosting`
(`06_stability/results/distribution_v2.json`; claims C8–C13). **The sign holds in all 26
perturbations** (−10.41% to −1.06%, median −5.91%, coverage never worse), **and the size still
turns on stage 1 and on the construction of the training errors, not on the stage-2 family's
tuning.** New in this round: the no-differencing SARIMAX alone scores 24.93, better than the
main path's stage 1 (26.05) and within 0.6 CRPS of the two-stage main path (24.35), so under
that stage 1 the correction is worth only −1.06% — part of the second stage's margin is a
repair of stage 1's differencing choice, recorded against stage 1's documented weaknesses
(stage 1 stays as specified, human-set). The true rolling refit, the conservative reading,
gives −2.99% (v1: −0.70%). The gain is concentrated in the same provinces as before, with
Xekong joining the always-improved set, and now reaches one month ahead in 23 of 27
combinations. Nothing is promoted; batch 16 freezes the holdout manifest from v2.

Batch 16: the phase-E set is frozen before the held-out year is opened
(`06_stability/results/manifest_holdout.csv`, 43 rows, sha256 recorded in
`holdout_freeze.json` at a commit carrying every script the set will be run by and no holdout
result). **No number about dengue changes in this batch.** What it fixes is what the held-out
year will be asked: the twelve months are scored as four expanding-window three-month blocks
covering 2010 exactly once at h = 1..3, on development's seventeen provinces — 204 cells per
row; the set is the pre-registered main path `h_levelOnlyBoosting` with both required baselines,
four of the nine not-taken siblings, the 26 development v2 perturbations under holdout names,
and ten rows not run with their reasons; and the reporting rule is frozen with it, so what
counts as the answer is decided before the numbers exist. Phase E's machinery was built and
gated here rather than in phase E, reproducing the main path's and both baselines' stored
development per-cell scores on 408 rows each with 0 mismatches, so that no code is written or
corrected with a held-out number on screen. At the freeze the human kept `h_levelOnlyBoosting`
and left stage 1 unreopened (plan §4b, 2026-09-22). Batch 17 opens the year once.

Batch 17: **the held-out year was opened once and the frozen set run in full**
(`06_stability/results/run_status_holdout.csv` records the opening; `distribution_holdout.json`
the answer; claims C14–C20). The project's own question is answered in the affirmative, and the
answer arrives with a second finding that qualifies it.

**The second stage earns its place on data never used in development.** On the 192 scored cells
of 2010 the two-stage ensemble scores mean CRPS **99.20 against stage 1 alone's 128.51
(−22.81%)**, with 90% coverage **61.5% against 57.3%** — both of plan §2's bars cleared, all four
splits and 75% of cells improved. The margin is larger than development's −6.53%, not smaller,
and it survives every one of the 26 frozen perturbations (−29.25% to −4.18%, median −20.89%, no
sign flips, coverage never worse).

**And the whole two-stage model is beaten on that year by seasonal climatology**, one of the two
required baselines, scored on the same cells through the same pipeline: **77.29 against the
ensemble's 99.20 and stage 1's 128.51**. On development the ranking was the other way round
(stage 1 26.05 < climatology 26.91). Coverage collapses for every model — 54.7% to 61.5% against
a nominal 90%. 2010 is an epidemic year quite unlike the development test span (22,903 cases in
twelve months against 12,291 in twenty-four; a September peak of 5,649 against a maximum of
1,410), and a SARIMAX on raw counts with a Gaussian predictive interval does not follow it.

So the honest statement of what this project found: **a residual-correction stage trained on
stage 1's multi-step out-of-sample error does earn its place, robustly and by a wide margin on
held-out data — on top of a first stage that is itself the wrong model for the year it was tested
on.** The stage-1 fork that batch 10's diagnostics identified as the one that could repair
calibration, a count or heavier-tailed predictive family, was recorded as not run by a human-set
decision and remains the largest thing this analysis does not cover. Nothing was promoted on
held-out evidence, and three tier-2 rows that beat the main path there are recorded as such and
left alone.
