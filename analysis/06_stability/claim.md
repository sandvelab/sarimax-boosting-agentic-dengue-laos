# Claim

Does the conclusion that the two-stage ensemble earns its place against stage 1 alone survive reasonable alternative ways of building either stage — stage 1's specification, stage 2's family, target, inputs and combination rule, the training window and the backtest scheme — and which of those choices does it turn on? The perturbation set is planned and frozen here before it is run; the report is the distribution of conclusions across it, not the best one.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Batch 11 — planned and frozen, not yet run.** The perturbation set is
`results/manifest.csv` (40 rows; frozen in `results/manifest_freeze.json`), costed from
`results/run_costs.csv`.

- **Cost.** Re-running every existing model node (`02_stage1` and all seven `04_stage2`
  candidates) takes 87 seconds in total and reproduces every committed output byte for byte
  (`results/run_costs_summary.json`): stage 1 7.7 s, the per-province candidates 7–10 s each,
  `f_oosErrorRidge` 16 s, `g_oosErrorBoosting` 22 s. Compute is not the binding constraint on
  stability work here; development effort per perturbation is. The compute budget is set
  provisionally at one hour of wall-clock (agent-autonomous, for the human to revise); the
  29 planned tier-2 rows are estimated at 24 minutes, so the line falls below every planned
  row and nothing is excluded for budget.
- **Tier 1 (6 rows, derived from the tree):** the six not-taken `04_stage2` siblings, already
  run; their results are their own.
- **Tier 2 (29 rows, ranked by expected informativeness):** at the top, the refinement the
  Savannakhet loss motivates (a correction bounded relative to the forecast level), the
  airline specification for stage 1, standardising the stage-2 target by the province's
  residual scale instead of stage 1's se, and a rolling 72-month training window that forgets
  the pre-2008 reporting regime; then the level-only feature set, the no-differencing stage 1,
  a true rolling refit for the in-window errors, the per-horizon fit, Chap's default scheme
  (7 splits, stride 1), the winsorisation bound (2, 5, none), the seed, the climate anomalies,
  the 2002 window start, the boosting hyperparameters, the ridge penalty, clipping, feature
  ablations, warm-up and thresholds. Each row names the node, the parameter, the main and
  alternative values and the basis for calling the alternative reasonable.
- **Tier 3 (5 rows, not run, with the reason):** a log1p stage 1 and a negative-binomial or
  truncated-normal predictive family (both need a verified metric extension; the second is
  the most consequential fork not run, since the coverage deficit is a heavy tail a Gaussian
  cannot carry), a multiplicative combination rule (undefined near zero; needs a design), an
  ENSO covariate (new data acquisition; a governance call), and Chap-native evaluation
  (decided against in plan §4).
- **Run design for batch 12** (`results/manifest_summary.json`): tier 1 by calling each
  sibling's `run.sh`; tier 2 by a combination runner in this node that recomputes stage 1 and
  the main-path stage 2 under the combination's settings and writes `results/<combination>/`,
  trusted only once its `main` combination reproduces `g_oosErrorBoosting`'s stored per-cell
  scores byte for byte. Batch 13 reports the distribution.

No conclusion about stability is drawn here; the claim is answered by batch 13.

**Batch 12 — run.** Every planned row ran (`results/run_log.csv`, `results/run_summary.json`:
29 combinations, 1,937 s of the 3,600 s ceiling; the rolling refit alone 990 s). The runner
(`scripts/03_run_combinations.py`, on `lib/stage2_perturb.py`) was gated: its `main`
combination reproduced `04_stage2/g_oosErrorBoosting`'s 408 per-cell rows value for value
(`results/main/conclusion.json`, `verification_vs_main_path`: 0 mismatches) before any
perturbation ran, and it refuses a manifest that does not hash to the frozen digest. Each
combination's per-cell scores and conclusion are under `results/<combination>/`;
`results/conclusions.csv` gathers one row per manifest row (tier 1 from the siblings' own
comparison files, tier 3 as not run).

Headline counts from `conclusions.csv`, ahead of batch 13's report: of the 36 rows that ran
(main, 6 siblings, 29 perturbations), the two-stage ensemble beats stage 1 alone on mean CRPS
in 32 and does so with coverage not worse in 31. **All 29 tier-2 perturbations keep the
two-stage ensemble ahead of stage 1 alone with coverage not worse**, from −0.70% (true rolling
refit of the in-window errors) to −10.64% (the airline stage 1, whose stage 1 alone is much
worse at 29.15 and is largely rescued by the correction). The four rows where the ensemble
loses are the four batch 4–8 siblings trained on the in-sample residual (a–d); the one row
that wins on CRPS with worse coverage is `e_pooledRandomForest`. One caveat recorded rather
than hidden: in the rolling-refit combination, 3 origins per split whose refit returned
non-finite predictions contributed no training row (visible as the per-split row counts, 3
below `main`'s); the runner's non-finite-feature counter does not cover that case.
Batch 13 reports the distribution and which choices the margin turns on.

**Batch 13 — the answer** (`results/distribution.json`, `results/perturbation_effects.csv`,
`results/province_stability.csv`, `results/horizon_stability.csv`; claims C1–C7 in the
collection).

*The sign survives.* In all 29 planned perturbations the two-stage ensemble beats stage 1
alone on mean CRPS with 90% coverage not worse: margin −0.70% to −10.64%, quartiles −4.19% to
−2.41%, median −3.32% against the main path's −3.41%. No perturbation flips it. The only
configurations that lose are the four early siblings trained on the in-sample one-step
residual, which is white.

*The size turns on how the training errors are made and on stage 1, not on the stage-2
family's tuning.* Nine rows move the margin by more than two points. It is larger when stage
1 is weaker (airline specification: stage 1 alone 29.15, corrected 26.05, −10.6%; enforced
stationarity −8.4%; Chap's default scheme −7.2%) and under four stage-2 simplifications that
were not selected (level-only features −6.5%, bounded correction −5.8%, no cross-province
term −5.8%, climate anomalies added −5.8%). It is smaller under a 2002 training-window start
(−0.9%) and, most importantly, under a true rolling refit of the in-window errors (−0.7%) —
the honest version of the main path's fixed-parameter shortcut. A reader who weights that row
most should read the development margin as under one percent. All seven hyperparameter and
seed perturbations stay within two points (−1.6% to −4.2%). Split-level agreement is 5 or
more of 8 splits in 22 rows, 4 in 6 rows, and 3 in one (the rolling 72-month window).

*The gain is concentrated, and the concentration is stable.* Khammouane, Salavan, Bokeo and
Xiangkhouang improve in every one of the 30 combinations; Savannakhet, Vientiane Capital,
Luang Prabang, Xayaboury and Oudomxay improve in at most 20%. Two and three months ahead
improve in every combination; one month ahead in 47%.

*What the statement does not cover*: the five tier-3 alternatives, above all a count or
heavier-tailed predictive family at stage 1, the one change that could repair the coverage
deficit. Everything here is development data; the sealed 2010 holdout is opened once, in
batch 15, across a manifest frozen in batch 14.

**Batch 15 — the v2 run and report, around `h_levelOnlyBoosting`** (`results/run_summary_v2.json`,
`results/conclusions_v2.csv`, `results/distribution_v2.json`, `results/perturbation_effects_v2.csv`,
`results/province_stability_v2.csv`, `results/horizon_stability_v2.csv`,
`results/version_comparison_v2.csv`; claims C8–C13). Batch 14 annotated `h` as `04_stage2`'s
main path and re-planned the manifest around it (v2: 26 tier-2 rows suffixed `@h`, nine tier-1
siblings, five tier-3 not run; v1's 29 rows kept as superseded). The runner's `main@h` gate
reproduced `h`'s 408 per-cell rows with 0 mismatches; all 26 rows ran in 1,537 s of the 3,600 s
ceiling. v1's files are untouched: v2 writes `_v2` files beside them.

*The sign survives, again.* In all 26 perturbations the two-stage ensemble beats stage 1 alone
on mean CRPS with 90% coverage not worse: −10.41% to −1.06%, quartiles −6.53% to −4.90%, median
−5.91% against the main path's −6.53%. No row improves fewer than half the splits (21 rows 6 of
8, 5 rows 4 of 8).

*The size turns on stage 1 and on what the correction is trained on, not on the family's
tuning.* Eight rows move the margin by more than two points. Larger: the airline stage 1
(29.15 → 26.11, −10.4%) and stationarity enforced (26.80 → 24.08, −10.2%). Smaller: one model
per horizon (−3.5%), the rolling 72-month window (−3.4%), adding the recent-residual and
cross-province features back to the minimal input (−3.3%), the true rolling refit of the
in-window errors (−3.0%), the 2002 window start (−1.1%) and — the new finding — the
no-differencing stage 1 (−1.1%): SARIMAX(1,0,1)×(1,0,0,12) alone scores 24.93, better than the
main path's stage 1 (26.05) and within 0.6 CRPS of the two-stage main path (24.35), so part of
the second stage's margin is a repair of stage 1's differencing choice. Stage 1 stays as
specified (human-set, batch 14); this is recorded as its documented weakness bearing on the
central comparison. The five hyperparameter and seed rows stay within two points (−4.8% to
−6.5%), as do winsorisation, the bound without its floor, clipping, standardisation and
warm-up.

*Beside v1.* Changing the main path from `g` to `h` moves the margin from −3.41% to −6.53%,
and 20 of the 22 perturbations shared by name move with it (median shift −2.3 points); the
two exceptions are stage-1 changes (airline −10.64% → −10.41%; no differencing −3.36% →
−1.06%). The conservative rolling-refit reading moves from −0.70% to −2.99%. Chap's default
scheme moved the size in v1 and not in v2; the per-horizon fit, the rolling window and the
no-differencing stage 1 move it in v2 and not in v1. Four v2 rows are, by construction, the
same configuration as a v1 row and reproduce its two-stage mean CRPS to the last digit.

*The gain is concentrated, as before, and reaches one month ahead now.* Khammouane, Salavan,
Bokeo, Xiangkhouang and Xekong improve in every one of the 27 combinations and Champasak in
25; Oudomxay never improves, and Phongsaly, Luang Prabang and Vientiane Capital improve in at
most 10% (Savannakhet in 4 of 27: the airline stage 1, the rolling window, the bound without
floor, the tighter winsorisation). Three months ahead improves in every combination, two in
26 of 27, one month ahead in 23 of 27 (v1: 47%).

*Not promoted, and not covered.* Three v2 rows score better on development data than `h`
(winsorisation at 5: −6.92%; the bound without floor: −6.78%; no winsorisation: −6.57%) —
within the seed row's own distance from the main path — and none is promoted: the main path
is the pre-registered choice the holdout will evaluate. The five tier-3 alternatives are
unchanged and uncovered. Batch 16 freezes the holdout manifest from v2.

**Batch 16 — the phase-E set, frozen** (`results/manifest_holdout.csv`,
`results/holdout_freeze.json`, `results/manifest_holdout_summary.json`,
`results/holdout_runner_verification.json`). Nothing here is a result about dengue: this batch
fixes what the held-out year will be evaluated across, and proves that every row of it can be
run, before the year is opened.

*The evaluation design.* The project's fixed scheme — `n_periods 3`, `stride 3`, expanding
window ending at the file's last period — resolves over the combined 1998-01 to 2010-12 span to
**four successive three-month blocks covering 2010 exactly once**, trained on 144, 147, 150 and
153 months. Each block after the first trains on the holdout months already forecast, which is
what a forecaster operating through 2010 would have had, and it keeps the horizons h = 1..3 that
stage 2 is trained on. **The province set is development's seventeen**, derived from the
development months alone, so the cell set cannot move when the year opens; the base set is
17 × 12 = 204 cells per row. The alternative — one origin at 2009-12 forecasting twelve months
— was rejected: it scores the year at horizons no model here is built or evaluated for.

*The machinery is gated before it is frozen.* `lib/holdout_eval.py` runs in development mode and
reproduces three stored results value for value: the main path's 408 per-cell scores (0
mismatches) and both required baselines' 408 each (0, 0). The baselines matter most —
`03_baselines`' scripts cannot read another file, so these are a second implementation, and
nothing but the comparison says the two agree. The planner refuses to freeze a set the gate has
not passed, refuses a manifest and a configuration set that disagree in either direction, and
on every later run verifies the frozen file rather than rewriting it.

*The set.* 43 rows, 33 planned, an estimated 940 s against the 3,600 s ceiling carried over from
phase D — the line falls below every planned row and nothing is excluded for budget. Tier 0 (3):
the pre-registered main path `h_levelOnlyBoosting` and the two required baselines; stage 1 alone
needs no row, since every two-stage row scores it on the same cells. Tier 1 (9): the four
not-taken siblings the parametrised pipeline expresses (`f`, `g`, `i`, `j`) planned; `a`–`e` not
run, because each would need a holdout-capable rewrite of its own script, all five lose to stage
1 alone on development, and batch 10's diagnostics explain why. Tier 2 (26): the development v2
perturbations under holdout names, so every judgment call measured on development is measured
again on the held-out year and the two pair by row name. Tier 3 (5): carried forward unchanged.

*What binds.* `holdout_freeze.json` records the manifest's sha256, 43 rows, the commit it was
frozen at (67f998c — which carries every script the set will be run by and no holdout result),
and the sealed holdout file's own digest, so the file phase E opens is the file that was sealed.
The reporting rule is frozen with the set: plan §2's two bars on the main path as the primary
answer, both baselines beside it, the tier-2 spread reported as a distribution and never as a
best row, every row paired with its development counterpart — and, afterwards, nothing added,
dropped, re-tuned or re-run once a holdout number has been seen, nothing promoted on held-out
evidence, and a result contradicting development reported as the finding. Two decisions were the
human's at the freeze (plan §4b, 2026-09-22): the main path stays `h_levelOnlyBoosting`, and
stage 1 is not reopened after the no-differencing finding.

*A defect found on the way, in this node's own development freeze.* `02_plan_manifest.py`
rewrote `results/manifest.csv` on every run, with `est_cost_s` taken from wall-clock that
`01_measure_run_costs.py` re-measures each time — so every full run of `analysis/run.sh` moved
the file away from the digest recorded in `manifest_freeze.json`, and nothing noticed, because
the `freeze` invariant covered only the phase-E set. The cost columns change nothing the
manifest plans, which is exactly why it was invisible; the frozen digest is what the batch-13
and batch-15 reports rest on. The script now re-plans in memory, compares, writes
`results/manifest_freeze_check.json` and leaves the file alone, failing if the manifest no
longer hashes to its freeze or if a re-plan would change anything beyond the cost columns; a
change of main path still plans a new version, as batch 14 did. **`manifest.csv` is unchanged**
— still `d2c5e813…`, the v2 digest frozen at `cef9a18`. Both refusals were exercised rather
than assumed.

**Batch 17 — the held-out year, opened once** (`results/run_status_holdout.csv`,
`results/run_summary_holdout.json`, `results/conclusions_holdout.csv`,
`results/distribution_holdout.json`, `results/perturbation_effects_holdout.csv`,
`results/province_stability_holdout.csv`, `results/horizon_stability_holdout.csv`,
`results/development_comparison_holdout.csv`, `results/holdout_year_context.json`; claims
C14–C20). Opening number 1, at commit `8eda4fd`; the four preflight refusals all passed, all 33
planned rows ran in 623 s, and nothing was added, dropped, re-tuned or re-run.

*The primary answer, by the frozen rule: the second stage earns its place.* On the 192 scored
cells the two-stage ensemble scores mean CRPS **99.20 against stage 1 alone's 128.51, −22.81%**,
with 90% coverage **61.5% against 57.3%** — both of plan §2's bars cleared, all 4 splits and 75%
of cells improved, every horizon improved. The margin is **larger** than development's −6.53%,
by 16.3 points, and 29 of the 31 rows paired by name have a larger margin on the held-out year
than on development. The sign survives every frozen perturbation: 26 of 26, −29.25% to −4.18%,
median −20.89%, no flips, coverage never worse.

*And the two-stage model still loses to a naive baseline.* On the same cells **seasonal
climatology scores 77.29** — 22% better than the two-stage ensemble and 40% better than stage 1
alone — while persistence (127.58) is level with stage 1. This reverses the development ranking,
where stage 1 beat climatology by 3.2%. Coverage collapses for everything: 57.3%, 61.5%, 56.2%
and 54.7% against a nominal 90%, where development gave 82.7% and 85.2%. **The correction
improves a first stage that is itself badly beaten on this year**, and no configuration in the
frozen set is adequately calibrated on it.

*Why the numbers are so much larger.* 2010 is an epidemic year unlike the development test span:
22,903 cases in twelve months against 12,291 in twenty-four, 3.6× the mean cases per cell, with a
September peak of 5,649 against a development-span maximum of 1,410
(`results/holdout_year_context.json`, written after the opening and not part of the frozen set).

*What the held-out year turns on.* The input, far more sharply than development showed. The two
level-only configurations gain about 23% (`h` −22.81%, `j` −22.70%); every configuration carrying
the recent-residual and cross-province features gains 4% or less (`f` −3.89%, `i` −2.27%, `g`
−2.25%, and adding those features back to the main path −4.18%). On development that gap was
about 3 points; here it is about 19. Had `g_oosErrorBoosting` remained the main path, as it was
until batch 14, the held-out margin reported here would have been −2.25%.

*Not promoted, and not covered.* Three tier-2 rows beat the main path on the held-out year (no
winsorisation −29.25%, the looser bound −28.72%, a higher learning rate −25.77%); none is
promoted, because the holdout measures a pre-registered configuration and selecting on it would
spend the only unused data this project has. The five tier-3 alternatives and the five
in-sample-residual siblings were not run, with their reasons. **Sixteen of 26 rows move the
margin beyond the two-point threshold, against eight of 26 on development**, so the size is less
stable here, not more. One province, LA-XN, reports no cases for any month of 2010 and so
contributes no scored cell: the held-out evaluation is 16 provinces, not 17.
