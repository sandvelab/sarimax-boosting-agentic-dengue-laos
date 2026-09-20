# Claim

Which stage-2 model family, trained to predict stage 1's residuals and added back as a correction, earns its place against stage 1 alone on the development backtest?

## Children

kind: alternatives
main-path: a_linearLags

## Environment

inherits: the project main environment (`environment/`)

## Answers

Not yet settled — three candidates now, all negative, all on the identical minimal input
(stage 1's lag-12 in-sample residual, cyclical calendar month). `a_linearLags` (plain OLS):
mean CRPS 26.26 vs. stage 1 alone's 26.05, 0.78% worse. `b_gradientBoosting` (regularised
gradient-boosted trees, same inputs): 27.68, 6.25% worse. `c_bayesianRidge` (Bayesian ridge,
its own posterior predictive variance combined into the final interval): 28.07, 7.73% worse —
the best-calibrated of the three (86.8% empirical coverage vs. nominal 90%, against 82.7% for
stage 1 alone) but the worst CRPS, since the wider interval that calibration buys costs more
than the mean correction gains. `a_linearLags` remains the (still-losing) main path by
default — it is the least-bad of the three, not a candidate that earns its place.
`analysis/04_stage2/c_bayesianRidge/results/all_candidates_comparison.json` holds all three
side by side. This does not close the question the plan asks (§1: is there *a* stage-2 family
that earns its place) on a richer input — batch 7 is reserved for the formal main-path
decision among the three and for exploring what stage 2 is allowed to see (more lags,
covariates, population) as its own fork.

**Batch 7 — main-path decision.** `a_linearLags` is the main path (least-bad of the three,
still losing to stage 1 alone; `run.sh` and `main-path:` above already reflected this since
batch 6). The formal decision, made explicit here: none of the three earns its place, so
"main path" records which of the three the stability phase (rows 8–10) treats as the default
stage-2 configuration when it perturbs stage 1's spec, the training window, and zero-handling
— not a claim that stage 2 should be adopted.

**Batch 7 — what stage 2 is allowed to see, logged as an explicit fork (plan §3: "each is
either an alternatives node with its rejected siblings intact, or an explicitly logged
decision with its basis").** All three candidates built (`a_linearLags`, `b_gradientBoosting`,
`c_bayesianRidge`) share one input set — stage 1's lag-12 in-sample residual plus cyclical
calendar month — fixed once in batch 4's leakage analysis (lag-1 is unsafe for the 2nd/3rd
test month of a 3-month split; lag-12 is always inside the training window) and reused
unexamined by batches 5 and 6. This batch surveyed what else is actually available rather than
guessing, and **did not build any of it** — recorded here as a visible absence, not a silent
one (AGENTS.md §5/§6):

- **Additional lags** (lag-2 through lag-11, or lag-1 restricted to only the first test month
  of each split, where it is genuinely available): not tried. Cheap to add, plausible effect
  unknown; deferred to the stability phase or a future alternatives child, whichever is
  reached first.
- **Climate covariates**: `analysis/01_data/01_prepare/results/development.csv` already
  carries `rainfall`, `mean_temperature` and `mean_relative_humidity` per province-month —
  reused directly from the archived dataset, no new acquisition needed. Not tried by any
  candidate. This is the most informative untried fork: dengue transmission has a known
  climate dependence, so a stage-2 model given these columns (rather than stage 1, which sees
  none of them) is the most plausible way for the two-stage architecture to actually earn its
  place, and its absence should not be read as "climate covariates were considered and
  rejected" — they were not tried at all.
- **Population**: `development.csv` also carries a per-province `population` column
  (`Archive/lao-population/` separately holds only a country-level World Bank total, coarser
  than what is already in the working dataset and not needed). Not tried. Population is
  near-constant within a province across this backtest's span relative to its month-to-month
  case variation, so it was judged the least informative of the untried covariates — a
  reasoned deprioritisation, not an oversight, but still not run.
- **Province identity, used structurally**: `c_bayesianRidge` fits independently per
  province, like its siblings — none of the three pools information across provinces (e.g. a
  shared/partial-pooled coefficient on the lag-12 term). Not tried. This is a different kind of
  fork from a raw input feature (it changes what the model borrows strength from, not what it
  literally reads), named separately per plan §3's own distinction between "covariates" and
  "population" as separate items.

**Why none of these was run in this batch** (AGENTS.md §6, cost vs. informativeness): each
would need its own alternatives or sub-analyses node, a fresh contract check against stage 1's
stored forecast, and its own provenance record — the same scope as batches 4–6 individually,
not a small addition. Given three families have already been tried and lost on the same
minimal input, the more informative next step is deciding *whether* to spend further batches on
richer inputs at all versus moving to the stability phase (rows 8–10) with `a_linearLags` as
the frozen default — left as an open question for the human rather than a call this batch
makes for itself, since it trades further exploration against the plan's own stated tracking
level (AGENTS.md §6) and is exactly the kind of scope decision plan §6 reserves for dialogue.

**Batch 8 — the climate-covariate fork, tried (human-set: explore richer inputs before phase
D, plan §4b).** A fourth candidate, `d_linearClimate`, added lag-12 rainfall, mean temperature
and mean relative humidity to `a_linearLags`'s exact input and family, isolating the
input-richness question from the model-family one flagged above. **Result: worse, not
better** — mean CRPS 26.85 against stage 1 alone's 26.05 (+3.05%) and against `a_linearLags`'s
own 26.26 (+2.25%). The most plausible untried route named in batch 7 did not change the
central finding when tried on the family it was tried with; `a_linearLags` remains the main
path. `analysis/04_stage2/d_linearClimate/results/all_candidates_comparison.json` holds all
four candidates side by side — **no stage-2 family or input tried so far earns its place.**
This narrows, but does not close, the climate-covariate question: it rules out lag-12 climate
added to a linear correction, not climate added to a non-linear one (`b_gradientBoosting` or
`c_bayesianRidge`'s families, given the same input, remain an untried cell of the
family × input grid) nor a genuinely forward climate signal (not available in this dataset).
Population and cross-province pooling remain untried, as recorded above. **Ledger row 8
closes here**; the plan's §6 renumbers the stability phase to rows 9–11 (was 8–10).

**Batch 9 — the cross-province-pooling fork, tried (human-set: keep exploring, and try an
existing `chap-models` model for stage 2).** A fifth candidate, `e_pooledRandomForest`,
adapts `chap-models/rwanda_random_forest`: one random forest fit per split, pooled across all
17 provinces, on `d_linearClimate`'s exact input — isolating pooling as the one axis this
candidate changes. **Result: mixed, and on balance still a no.** Mean CRPS **25.89** — the
first candidate to beat stage 1 alone (26.05, -0.63%) and to beat `d_linearClimate` on the
identical input (26.85, -3.57%) — but empirical interval coverage collapses to **64.4%**
against nominal 90% (every prior candidate stayed near stage 1's own 82.7-86.8%). Per plan §2
("a model that wins on mean CRPS while being badly calibrated has not won"), this candidate
does not earn its place either.
`analysis/04_stage2/e_pooledRandomForest/results/coverage_collapse_diagnosis.json` traces the
break to 27.5% of its corrected forecasts landing below zero (impossible for a case count),
concentrated in the lowest-case-count provinces (r=-0.53 between a province's mean case count
and its negative-forecast rate) — a pooled correction shaped by provinces spanning under 1 to
over 150 mean monthly cases overshoots on the scales it was not specifically fit to. **The
pooling idea itself is not ruled out, only this implementation of it**: a version preserving
each province's own scale under pooling (e.g. a per-province offset or standardisation before
pooling) is logged as an untried refinement, not a rejected one. On mean CRPS alone,
`e_pooledRandomForest` (25.89) ranks best of everything built so far, ahead of stage 1 alone
(26.05); but since it fails the calibration bar plan §2 sets, the ranking among candidates
that meet both criteria is unchanged from batch 8: **stage 1 alone (26.05) < a_linearLags
(26.26) < d_linearClimate (26.85) < seasonal climatology (26.91) < b_gradientBoosting (27.68)
< c_bayesianRidge (28.07) < persistence (28.32)**, with `e_pooledRandomForest` reported
alongside rather than slotted into that ranking, since collapsing it to a single CRPS number
would hide the trade-off that disqualifies it. `results/all_candidates_comparison.json` holds
all five side by side. **Ledger row 9 closes here.**
