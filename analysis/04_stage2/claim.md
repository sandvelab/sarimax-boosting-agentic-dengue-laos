# Claim

Which stage-2 model family, trained to predict stage 1's residuals and added back as a correction, earns its place against stage 1 alone on the development backtest?

## Children

kind: alternatives
main-path: g_oosErrorBoosting

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

**Batch 10 — a systematic second iteration (human-set: literature, diagnostics, then
candidates; plan §4b).** Two things changed the picture. First, `05_residualStructure` showed
*why* candidates a–e found nothing: they were trained on stage 1's in-sample one-step
residual, which is essentially white (mean autocorrelation within ±0.06 at every lag), whereas
the quantity a stage 2 must correct — the 1-, 2- and 3-step out-of-sample error — is not:
stage 1 over-predicts in two thirds of cells, more at high forecast levels and in November–
April, and under-predicts in June–July; the dominant errors, and the whole coverage deficit,
are reporting-regime breaks in 2008–09 (Bokeo, Salavan, Savannakhet) that no province's own
history predicts. Climate anomalies at lags 1–3 carry no usable signal (|ρ| ≤ 0.05), and the
coverage gap cannot be fixed by scaling sigma without losing CRPS (an oracle factor takes
26.05 to 35.65). Second, the literature retrieved this batch (stacking: Wolpert 1992, Breiman
1996; horizon-specific correction of a recursive base forecast: Ben Taieb & Hyndman 2014;
the hybrid-ARIMA critique: Taşkaya-Temizel & Casey 2005; global models with per-series
scaling: Montero-Manso & Hyndman 2021) says the same thing from theory.

Two candidates were built on that basis, differing only in family: both train on stage 1's
h-step error computed inside each split's training window from every origin with parameters
fixed (~5,000 rows per split, pooled across provinces), standardised by stage 1's own se and
winsorised at ±3, from forecast-time features (horizon, target month, forecast level relative
to the province's residual scale, recent residuals and their cross-province mean, trailing
incidence, trailing zero fraction); the correction z-hat × se is added to stage 1's mean and
the result clipped at zero; sigma unchanged.

- **`f_oosErrorRidge`** (ridge): mean CRPS **25.63**, −1.64% vs stage 1, coverage 84.6%
  (stage 1: 82.7%). Improves 4 of 8 splits and 56.6% of cells.
- **`g_oosErrorBoosting`** (shallow gradient-boosted trees): mean CRPS **25.16**, −3.41%,
  coverage 85.7%. Improves 5 of 8 splits and 56.6% of cells.

**Both clear plan §2's two bars — lower mean CRPS than stage 1 alone, with calibration not
worse (here: better) — the first candidates to do so.** Clipping stage 1's mean at zero alone
accounts for −0.56% of either gain; the correction accounts for the rest (−1.09% and −2.87%
against the clipped stage 1). Gains sit in Khammouane, Salavan, Bokeo and Champasak and grow
with horizon; both lose in Savannakhet, where stage 1's se is tens of times the 2008–09 case
level and a small standardised correction becomes a large absolute one — a refinement (bound
the correction relative to the forecast level) logged as untried. The updated ranking, best to
worst, among candidates clearing both bars: **g_oosErrorBoosting (25.16) < f_oosErrorRidge
(25.63) < stage 1 alone (26.05) < a_linearLags (26.26) < d_linearClimate (26.85) < seasonal
climatology (26.91) < b_gradientBoosting (27.68) < c_bayesianRidge (28.07) < persistence
(28.32)**, with `e_pooledRandomForest` (25.89, coverage 64.4%) still reported alongside.
`g_oosErrorBoosting/results/all_candidates_comparison.json` holds all seven side by side.

**Main-path decision (batch 10, agent-autonomous, reversible with `/node promote`):
`g_oosErrorBoosting` becomes `04_stage2`'s main path**, replacing `a_linearLags`, which was
only ever the least-bad losing candidate. This is the first time the main path is a candidate
that earns its place on development evidence rather than a placeholder. The margin is modest,
concentrated in a few provinces and the later splits, was reached after diagnostics that
looked at the same development test cells, and rests on fixed rather than searched
hyperparameters — so it is exactly what the stability phase (rows 11–13) exists to test, with
`f_oosErrorRidge` the linear not-taken sibling it runs. Forks logged as untried after this
batch: a correction bounded relative to the forecast level; a heavier-tailed or count
predictive family at stage 1 (the honest fix for coverage); per-horizon separate models; a
true rolling refit for the in-window errors; ENSO indices as an external forecast-time
covariate (the literature's one climate signal with multi-month lead, not in this dataset).
**Ledger row 10 closes here.**
