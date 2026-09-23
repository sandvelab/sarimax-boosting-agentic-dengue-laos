Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 20)

# Does a residual-correction stage earn its place? A pre-registered, held-out evaluation of a two-stage SARIMAX ensemble for monthly dengue forecasting in Laos, with its complete provenance record

## Abstract

**Background.** Two-stage forecasting designs fit a base model, then fit a second model to the
base model's residuals and add its prediction back as a correction. Such hybrids are common and
their gains are disputed: a second stage can only help if the errors it is trained on carry
structure, and the residuals a fitted time-series model leaves in-sample often do not.

**Methods.** We built a two-stage ensemble for monthly reported dengue cases in the provinces of
Laos, 1998–2010. Stage 1 is a per-province SARIMAX on raw counts; stage 2 predicts stage 1's
forecast error and corrects the forecast mean. Ten stage-2 candidates were built, differing in
family, input and, decisively, in the error they were trained on. Development used 1998–2009
under a fixed rolling-origin backtest scored by the continuous ranked probability score (CRPS)
and 90% interval coverage, beside persistence and seasonal-climatology baselines. The reported
configuration was chosen by a rule written before the last candidate's result was seen. The
year 2010 was sealed throughout, and opened once across a perturbation set of 33 rows frozen in
advance, with the reporting rule frozen with it. Every judgment call is an alternatives node in
the analysis tree or a logged decision, every reported figure is read from a stored file, and
the whole analysis reproduces byte for byte from a fresh clone.

**Results.** On development data stage 1 alone (mean CRPS 26.05) beats both baselines, and
the five candidates trained on stage 1's in-sample one-step residual all fail to improve on it:
that residual is essentially white. Candidates trained on stage 1's multi-step out-of-sample
error, computed inside each training window and pooled across provinces on a standardised
scale, succeed. The pre-registered configuration reads only the horizon, the target month and
the forecast level, and scores 24.35 (−6.53%) with coverage improved from 82.7% to 85.2%; the
sign of its margin survives all 26 development perturbations. On the held-out year it scores
99.20 against stage 1's 128.51 (−22.81%), improves all four splits and 75% of cells, and the sign
survives all 26 frozen perturbations. On the same cells, seasonal climatology scores 77.29.
2010 was an epidemic year with 22,903 reported cases against 12,291 in the two development test
years, and no model in the frozen set covers more than 61.5% of outcomes at a nominal 90%.

**Conclusions.** A residual-correction stage trained on multi-step out-of-sample error, reading
almost nothing, reliably improves a SARIMAX first stage on held-out data. The model it improves
is beaten on that data by a seasonal mean, and the improvement is largest exactly where the base
model is most wrong. Ablation against one's own first stage is necessary and not sufficient; the
naive baselines and the pre-registration are what kept the positive answer honest.

## 1. Introduction

Dengue surveillance produces monthly case counts by province, and health systems want
forecasts of them one to three months ahead. A natural design for such forecasts is a
seasonal autoregressive model, which captures the annual cycle and the local trend, and a
natural way to try to improve it is to add a second model that learns whatever the first one
misses. The second model is trained on the first model's residuals and its prediction is added
to the first model's forecast. This is boosting in the general statistical sense of the word:
fit, take residuals, fit again on the residuals.

The design has a long record and a mixed one. Zhang (2003) is the template: an ARIMA model,
then a neural network on its lagged residuals, added back. Taşkaya-Temizel and Casey (2005)
showed on nine datasets that such hybrids do not necessarily outperform their constituents and
can underperform them, because a well-specified linear model leaves residuals with little
structure to learn. Firmino et al. (2014) made the condition explicit: correcting a forecaster's
errors helps only when those errors are not white noise. The stacking literature says the same
thing from the other side. Wolpert (1992) and Breiman (1996) argued that a second-level model
must be trained on held-out first-level predictions rather than in-sample fits, and Ben Taieb
and Hyndman (2014) applied exactly this to time series, keeping a recursive linear base forecast
and correcting its *h*-step errors directly with a boosted model at each horizon. For count data
at low levels, the calibration of the predictive distribution is a separate problem from the
accuracy of its mean: Sesay et al. (2026) found, for monthly dengue at one- to three-month
horizons, that a negative-binomial integer autoregression kept good interval calibration where a
negative-binomial regression substantially under-covered, and that lag-1 climate covariates added
no statistically significant skill.

The question this study asks is therefore narrow and internal: **on the same data, the same
splits and the same scoring, does a residual-correction stage improve on the SARIMAX it is
built on, by how much, and does the answer survive reasonable alternative ways of building
either stage?** We do not compare against an external reference model. We do compare against
the two baselines any forecast should beat, persistence and seasonal climatology, because a
positive answer to the internal question means little if both stages lose to a seasonal mean.

Two features of how the study was carried out bear on how its results should be read, and are
part of what it reports. First, the held-out year was sealed before any modelling began and
opened once, across a perturbation set and a reporting rule frozen beforehand, with the
configuration to be evaluated pre-registered by a rule written before the last candidate's
result was known. Second, the analysis was developed largely autonomously by an agentic AI
system under a fixed set of written instructions, with every judgment call recorded as either
an alternatives node in an analysis tree or a logged decision carrying who made it. The paths
not taken are kept runnable and were run. Section 3.9 describes this method of work, because
two runs of the same code under different instructions are two different methods.

## 2. Data

The data are monthly reported dengue case counts for the eighteen admin-1 provinces of the Lao
People's Democratic Republic from January 1998 to December 2010, as harmonised and published by
the DHIS2 Chap project (repository `dhis2/climate-health-data`, pinned by commit), whose schema
attributes the case counts to OpenDengue (LSHTM, CC BY 4.0). The file is a complete 18 × 156
grid of province-months with missing observations recorded as empty. It also carries monthly
rainfall, mean temperature, mean relative humidity and a static population figure per province;
the climate fields are read only by two not-taken stage-2 candidates, by the diagnostic analysis
of stage 1's errors, and by one row in each stability set.

The file was partitioned once into a development set of 2,592 rows (1998-01 to 2009-12) and a
held-out set of 216 rows (the twelve months of 2010). The held-out set's completeness was
confirmed by counting rows, provinces and months without reading a case value, and its digest
was recorded so that the file eventually opened could be shown to be the file that was sealed.

On development data, 17 of the 18 provinces have at least 24 present months and are modelled.
Vientiane province (LA-VI) reports nothing in the development period and is excluded.
Xaisomboun (LA-XN) has 96 of 144 development months present but stops reporting before the
evaluated span, so it contributes no scored cell to the development backtest, and it reports no
cases in any month of 2010, so it contributes none to the held-out evaluation either. The set of
modelled provinces was fixed from the development months alone and was deliberately not
re-derived when the held-out year opened.

Lao national dengue surveillance began in 1998 and was paper-based until an electronic system
was introduced in 2008 (Khampapongpane et al., 2014). The consequences of that transition are
visible in the data and turn out to matter for the results (Sections 4.3 and 4.6).

## 3. Methods

### 3.1 Evaluation

All models are scored by the continuous ranked probability score (CRPS) of a Gaussian
predictive distribution against the observed count, averaged over the scored province-months
("cells"), with the empirical coverage of the central 90% interval reported beside it. Lower
CRPS is better; coverage should be near 90%. The CRPS implementation is the project's own
closed form. Before it was used on real data it was verified against an independent library
implementation, matching `properscoring.crps_gaussian` to within 1.11 × 10⁻¹⁶ over a 45-case
grid and matching a Monte-Carlo ensemble estimator within tolerance at three sample sizes.

The development backtest is a rolling-origin scheme with an expanding training window,
three-month test windows, eight splits and a stride of three months, so the evaluated span is
January 2008 to December 2009, with the first split trained on 120 months and the last on 141.
Each split scores forecasts at horizons of one, two and three months. Over the 17 modelled
provinces this yields 408 cell slots, of which 371 carry an observation and are scored. The
scheme was fixed in advance and reused from an earlier project on the same data for
comparability; its consequences for stage 2 are discussed in Section 3.4.

A two-stage configuration "earns its place" if it has lower mean CRPS than stage 1 alone on the
same cells **and** 90% coverage not worse than stage 1's. A model that wins on CRPS while being
badly calibrated has not won. Both criteria are evaluated on development data and again on the
held-out year.

### 3.2 Stage 1

Stage 1 is a per-province SARIMAX(1,1,1)×(1,0,0)₁₂ fitted by maximum likelihood to the raw case
counts, refit at every split, forecasting the mean and standard error at horizons one to three.
The order was a first, defensible default rather than a selected one: an integrated
non-seasonal term for the local trend and a seasonal autoregressive term at lag twelve for the
annual cycle. It was fixed as the study's premise. Its specification was perturbed in the
stability set, and its weaknesses were documented rather than repaired, a decision the human
investigator made and reaffirmed (Section 8). Fitting is deterministic; no stage-1 fit failed
in any of the 136 development fits.

### 3.3 Baselines

Two naive forecasts are scored through the identical pipeline on the identical cells.
Persistence holds the last observed value flat across the test window, with the standard
deviation of the training window's one-step differences as its spread. Seasonal climatology
forecasts the mean of the same calendar month in the training window, with that month's
training-window standard deviation as its spread. Both are Gaussian forecasts scored by the
same CRPS code as everything else.

### 3.4 Stage 2: the contract and the candidates

Stage 2 never sees the target. It is trained to predict a quantity derived from stage 1's error
and its prediction is added to stage 1's forecast mean; the final forecast is stage 1's mean plus
the correction, with stage 1's standard error unchanged, and the mean clipped at zero because a
case count cannot be negative. Stage 2 is trained on every horizon the evaluation scores,
h = 1..3, with the horizon set read from the backtest scheme rather than fixed in code.

Ten candidates were built as alternatives in the analysis tree and all ten remain there. They
fall into two groups by what the second stage is trained on.

**In-sample one-step residual (candidates a–e).** The first five predict the residual stage 1
leaves on its own training data at one step ahead, from that residual at lag twelve and the
calendar month (a: ordinary least squares; b: gradient-boosted trees; c: Bayesian ridge
regression combining its own predictive variance into the interval), with lag-12 rainfall,
temperature and humidity added (d: linear), and with all provinces pooled into one random forest
per split on the same input (e), adapted from a community model in the Chap ecosystem.

**Multi-step out-of-sample error, in-window (candidates f–j).** The remaining five predict
stage 1's *h*-step forecast error as it would have been observed at every forecast origin inside
the current training window, with stage 1's parameters held at the values fitted on that window.
The error is standardised by stage 1's own forecast standard error, winsorised at ±3, and
pooled across all provinces into one model per split, which gives between roughly 4,700 and
5,700 training rows per split. The correction is the predicted standardised error multiplied
back by the standard error. Within this group the candidates differ by family (f: ridge
regression; g–j: gradient-boosted trees with 150 trees of depth 3, learning rate 0.05,
subsampling 0.8 and a minimum of 20 rows per leaf), by input (the full set for f, g and i:
horizon, target month, forecast level relative to the province's residual scale, recent
residuals and their cross-province mean, trailing incidence and trailing zero fraction; the
minimal level-only set for h and j: horizon, target month and forecast level only), and by
whether the correction is bounded relative to the forecast level (i and j).

### 3.5 Diagnostics of stage 1's errors

Between the two groups of candidates, a diagnostic analysis characterised stage 1's development
errors: the autocorrelation of the in-sample residual, and the structure of the out-of-sample
error by horizon, calendar month, province and forecast level, together with a leave-one-split-
out estimate of how much of that error is predictable at all from information available at
forecast time, against a permutation null. This analysis reads the same development test cells
the candidates are scored on, so the candidates built on it are development-set selection and
their development scores are read as such; the held-out year is the guard.

### 3.6 Selection and pre-registration

The reported stage-2 configuration was chosen among candidates g, h, i and j by a rule written
down before the last of them had been run: the lowest development mean CRPS with coverage not
worse than stage 1's, a tie within 0.1 CRPS broken by more splits improved, then by the simpler
configuration. This was the third round of selection on the same 371 development cells. The
chosen configuration was frozen into the held-out manifest before the year was opened, and two
better-scoring development perturbations of it were explicitly not promoted at the freeze.

### 3.7 The stability set

The judgment calls made in building either stage were enumerated as a perturbation manifest
and run by a stability node that reports the distribution of the central comparison across them
rather than the best row. Each row changes one thing: stage 1's order (an "airline"
(0,1,1)×(0,1,1)₁₂ specification, no differencing, enforced stationarity), the training window
(a 2002 start; a rolling 72-month window), the backtest scheme (Chap's default of seven splits
at stride one), the modelability threshold, and every constant of the stage-2 configuration (the
winsorisation bound, standardisation, warm-up, clipping, the bound and its floor, one model per
horizon, the feature set, a true rolling refit of stage 1 when constructing the in-window errors,
the boosting hyperparameters and the seed). Twenty-six such rows surround the reported
configuration. A perturbation is said to "move the size" of the margin when it changes the
percentage improvement over stage 1 by more than two percentage points; this is a reporting
threshold, not a test. Five further alternatives were listed and not run, each with its reason:
a log-transformed stage 1, a negative-binomial or zero-truncated predictive family at stage 1, a
multiplicative combination rule, an ENSO covariate, and evaluation through the Chap platform's
own harness.

### 3.8 The held-out evaluation

The held-out manifest was frozen with 43 rows, of which 33 were run: the pre-registered
configuration and both baselines; four of the nine not-taken stage-2 siblings (f, g, i, j); and
the 26 development perturbations under held-out names, so that every judgment call measured on
development is measured again on 2010 and the two pair row by row. The five in-sample-residual
candidates and the five unrun alternatives were recorded as not run, with reasons. The year is
scored as four successive three-month blocks covering 2010 exactly once, under the same
horizons, with the training window expanding to include the held-out months already forecast,
exactly as a forecaster operating through 2010 would have had them; the four splits train on
144 to 153 months. The province set is development's seventeen. The reporting rule was frozen
with the set: the pre-registered configuration against stage 1 alone on both criteria as the
primary answer; both baselines beside it; the perturbation spread as a distribution and never
as a best row; and, afterwards, nothing added, dropped, re-tuned, re-run or promoted on
held-out evidence, with a result contradicting development to be reported as the finding.

The machinery that opens the year was written and verified before the freeze against stored
development results, reproducing the pre-registered configuration's and both baselines'
per-cell scores with zero mismatches over 408 cells each, so that no code was written or
corrected with a held-out number on screen. The opening itself is recorded in a tracked file
with the commit, the manifest's digest and the held-out file's digest, so that a second opening
would be visible.

### 3.9 The method of work

The analysis is a tree of claims under version control. Each node is an analytical question
with its scripts, results and a provenance record for every result, binding it to the script,
its invocation, its inputs and their digests, the environment, the seed, the commit the code was
at and the commit the instructions were at. Children of a node are either sub-analyses, all of
which run, or alternatives, of which exactly one is annotated as the main path and runs; the
root's run script therefore reproduces exactly the reported analysis, while the paths not taken
stay in the tree, complete, and are executed by the stability node. No number reaches a claim
except through a file: whatever computes a score writes it to disk, and every figure in this
article is read from a stored result by a script, through a claim collection that binds each
statement to the file grounding it. A provenance sidecar beside this article maps each of its
statements to its claim.

The work was carried out by an agentic AI system executing a written plan in batches, under a
standing instruction file that is itself version-controlled as part of the method. Every
decision carries an agency label: set by the human investigator, made by the agent on the
human's assessment, or made by the agent autonomously. The default was autonomous, and the
exceptions are listed in Section 8. Three checks were run rather than trusted: a deterministic
invariant checker at every commit; a clean-room reproduction that clones the repository, builds
the environment from its lockfile, runs the whole analysis and compares every stored result byte
for byte; and an "outsider test" in which a fresh agent with no context is asked to follow the
instructions and report every point at which it guessed or found a false statement. The
environment is CPython 3.13 with 18 locked packages, among them statsmodels 0.15.0 for stage 1
and scikit-learn 1.9.1 for the tree-based candidates; the project seed is 20260920 and every
component seed derives from it.

## 4. Results

### 4.1 Stage 1 against the baselines

On the 371 scored development cells stage 1 alone scores mean CRPS 26.05 with 90% coverage
82.7%. Persistence scores 28.32 and seasonal climatology 26.91, so stage 1 beats both, by 7.99%
and 3.20%. The backtest resolves enough to separate a SARIMAX from naive forecasting, though the
margin over climatology is modest.

### 4.2 Candidates trained on the in-sample residual fail

All five candidates trained on stage 1's in-sample one-step residual fail the criteria of
Section 3.1. Four lose to stage 1 alone on CRPS: the linear correction scores 26.26, the linear
correction with climate covariates 26.85, the gradient-boosted trees 27.68 and the Bayesian ridge
28.07. The pooled random forest scores 25.89, better than stage 1, but its 90% interval covers
64.4% of outcomes: the pooled correction, shaped by provinces spanning under one to over 150
mean monthly cases, overshoots on the scales it was not fit to and drives many forecasts below
zero. Adding climate covariates to the linear correction made it worse, not better.

### 4.3 Why they fail, and what a second stage could learn

The in-sample one-step residual is essentially white. On the final split's training window its
mean autocorrelation across provinces is within ±0.06 at every lag from 1 to 12 (0.004 at lag
12), with at most 3 of the 17 provinces beyond two standard errors at any lag. There was nothing
in it for a second stage to learn.

The multi-step out-of-sample error is not white, but its structure is skewed and concentrated.
Stage 1 over-predicts in about two thirds of cells while its mean error is positive (+2.6 cases
at two months ahead, +7.3 at three), because it under-predicts by large amounts in a few. The
sign is seasonal: 55% of June and July errors are positive, against 13–23% in January to April.
Five provinces carry three quarters of the CRPS, and three of them are reporting-regime breaks
in the test years that no province's own history predicts: Savannakhet fell from 166 cases a
month in its training window to 8, Bokeo rose from 0.7 to 39, Salavan from 4 to 61. Those cells
give standardised errors up to 164 and account for the whole coverage deficit. Stage 1's
standard error does not grow with its forecast level as a count's variance would, and the
resulting heavy tail cannot be repaired by rescaling: an oracle multiplier on the standard error
that reaches nominal coverage raises mean CRPS from 26.05 to 35.65. Negative forecast means
occur in 4.0% of cells.

Only a small part of the out-of-sample error is predictable from information available at
forecast time. Across 56 feature-set and family configurations under leave-one-split-out
cross-validation, 10 beat a permutation null on skill and only 2 lowered CRPS against stage 1,
the best by 0.84% with a mean absolute correction of 0.32 standardised units. A second stage can
earn its place here, but the ceiling suggested by this exploratory estimate is low.

### 4.4 Candidates trained on the out-of-sample error succeed

All five candidates trained on the in-window multi-step out-of-sample error clear both
criteria on development data (Table 1). The ridge regression on the full feature set scores
25.63 (−1.64%), the gradient-boosted trees on the same input 25.16 (−3.41%, coverage 85.7%),
the bounded correction 24.53, the level-only input 24.35 and the level-only bounded correction
24.29. By the pre-registered rule the level-only configuration (h) is the reported one: it and
the level-only bounded configuration tie within 0.1 CRPS and on splits improved (6 of 8), and h
is the simpler. It scores mean CRPS 24.35 against stage 1's 26.05 (−6.53%), with coverage
improved from 82.7% to 85.2%.

**Table 1. Development backtest, 371 cells.** Mean CRPS and 90% interval coverage. Candidates
are ordered by mean CRPS; the two criteria are lower CRPS than stage 1 alone and coverage not
worse than stage 1's.

| Model | Trained on | Mean CRPS | vs stage 1 | 90% coverage | Earns its place |
|---|---|---|---|---|---|
| j — level-only, bounded, boosting | out-of-sample error | 24.29 | −6.78% | 85.2% | yes |
| **h — level-only boosting (reported)** | out-of-sample error | **24.35** | **−6.53%** | **85.2%** | **yes** |
| i — bounded boosting, full features | out-of-sample error | 24.53 | −5.85% | 85.7% | yes |
| g — boosting, full features | out-of-sample error | 25.16 | −3.41% | 85.7% | yes |
| f — ridge, full features | out-of-sample error | 25.63 | −1.64% | 84.6% | yes |
| e — pooled random forest, climate | in-sample residual | 25.89 | −0.63% | 64.4% | no (coverage) |
| **Stage 1 alone (SARIMAX)** | — | **26.05** | — | **82.7%** | — |
| a — linear, lag-12 residual | in-sample residual | 26.26 | +0.78% | — | no |
| d — linear, climate covariates | in-sample residual | 26.85 | +3.05% | — | no |
| Seasonal climatology | — | 26.91 | +3.20% | — | — |
| b — boosting, lag-12 residual | in-sample residual | 27.68 | +6.25% | — | no |
| c — Bayesian ridge, lag-12 residual | in-sample residual | 28.07 | +7.73% | 86.8% | no |
| Persistence | — | 28.32 | +7.99% | — | — |

### 4.5 Stability on development data

Around the reported configuration, the sign of the central comparison is stable: in all 26
perturbations of stage 1's specification, the training window, the backtest scheme, the
modelability threshold and every constant of stage 2, the ensemble beats stage 1 alone with
coverage not worse. The margin ranges from −1.06% to −10.41% with a median of −5.91%, no
perturbation flips it, and every row improves at least 4 of the 8 splits.

The size of the margin turns on stage 1 and on what the correction is trained on, not on the
stage-2 family's tuning. Eight perturbations move it by more than two percentage points. It is
larger under a weaker stage 1: the airline specification (−10.41%) and enforced stationarity
(−10.16%). It is smaller under one model per horizon (−3.47%), a rolling 72-month window
(−3.40%), adding the recent-residual and cross-province features back to the minimal input
(−3.32%), a true rolling refit of stage 1 when constructing the in-window errors (−2.99%), a
2002 start to the training window (−1.06%) and a no-differencing stage 1 (−1.06%). The five
hyperparameter and seed perturbations stay within two points (−4.76% to −6.45%), as do the
winsorisation bound, the bound without its floor, clipping, standardisation and warm-up.

Two of these rows qualify the development margin directly. The rolling refit is the honest
version of the main configuration's fixed-parameter shortcut, and a reader who weights it most
should read the development margin as about three percent. And a no-differencing stage 1,
SARIMAX(1,0,1)×(1,0,0)₁₂, alone scores 24.93, better than the fixed stage 1's 26.05 and within
0.6 CRPS of the two-stage configuration's 24.35; under it the correction is worth only −1.06%.
Part of the second stage's development margin is a repair of stage 1's differencing choice.

The same set was first run around the full-feature boosting candidate (g) before the
pre-registered configuration was chosen, with the same qualitative result: all 29 perturbations
kept the ensemble ahead with coverage not worse (−0.70% to −10.64%, median −3.32%), nine moved
the size, and the rolling refit gave the smallest margin (−0.70%); Khammouane, Salavan, Bokeo and
Xiangkhouang improved in every one of those 30 combinations while Savannakhet and Vientiane
Capital improved in at most 20%. Changing the reported
configuration from g to h moved the margin from −3.41% to −6.53%, and 20 of the 22 perturbations
shared by name between the two runs moved with it, by a median of 2.3 points; the two exceptions
are stage-1 changes.

The gain is concentrated and its concentration is stable. Khammouane, Salavan, Bokeo,
Xiangkhouang and Xekong improve in every one of the 27 combinations run around h, and Champasak
in 25; Oudomxay never improves, and Phongsaly, Luang Prabang and Vientiane Capital improve in at
most 10%. By horizon, the correction helps three months ahead in all 27 combinations, two months
ahead in 26 and one month ahead in 23; around g it helped one month ahead in fewer than half.

### 4.6 The held-out year

The frozen set was run once, in full: 33 of 33 planned rows. Nothing was added, dropped,
re-tuned, re-run or promoted afterwards. One province reports no cases for any month of 2010,
so 192 of the 204 frozen cell slots are scored, over 16 provinces.

**The second stage earns its place on data never used in development.** On the 192 cells the
ensemble scores mean CRPS 99.20 against stage 1 alone's 128.51 (−22.81%), with 90% coverage
61.5% against 57.3%. It improves all four splits, 75% of cells and every horizon. The sign
survives every one of the 26 frozen perturbations, from −29.25% to −4.18% with a median of
−20.89% and quartiles at −22.81% and −17.82%, with no row improving fewer than half its splits.
The held-out margin is 16.3 percentage points *larger* than the development margin, and across
the 31 rows paired by name between the two datasets, 29 have a larger margin on the held-out
year than on development (median shift −15.6 points). Development understated the second
stage's value on this year rather than overstating it.

**And the two-stage model is beaten on that year by a required baseline** (Table 2). Seasonal
climatology scores 77.29 on the same cells, against the ensemble's 99.20 and stage 1's 128.51,
while persistence (127.58) is level with stage 1. This reverses the development ranking, where
stage 1 beat climatology by 3.2%. The two-stage architecture improves on its own first stage and
is still 28% worse than taking the mean of the same calendar month.

**Table 2. Held-out year 2010, 192 cells, 16 provinces.** Every row was frozen before the year
was opened. Development figures from Table 1 for comparison.

| Model | Mean CRPS, 2010 | 90% coverage, 2010 | Mean CRPS, development | 90% coverage, development |
|---|---|---|---|---|
| Seasonal climatology | **77.29** | 54.7% | 26.91 | — |
| Two-stage ensemble (h, pre-registered) | 99.20 | 61.5% | 24.35 | 85.2% |
| Persistence | 127.58 | 56.2% | 28.32 | — |
| Stage 1 alone (SARIMAX) | 128.51 | 57.3% | 26.05 | 82.7% |
| Ensemble vs stage 1 | **−22.81%** | +4.2 points | −6.53% | +2.5 points |

Every model is calibrated far worse on the held-out year than on development. The 90% interval
of stage 1 alone covers 57.3% of outcomes and the ensemble's 61.5%, against 82.7% and 85.2% on
development, and the baselines are worse still. The correction improves coverage as it did on
development, by 4.2 percentage points, but from a level at which no configuration in the frozen
set is adequately calibrated.

The reason the numbers are several times larger is the year. 2010 was an epidemic year unlike
anything in the development test span: the 192 scored cells carry 22,903 reported cases in
twelve months against 12,291 in the twenty-four development test months, 3.6 times the mean
cases per cell, peaking at 5,649 cases in September 2010 against a development-span maximum of
1,410. A SARIMAX on raw counts with a Gaussian predictive interval does not follow that. The
correction recovers much of the level error, and a model with no trend at all does better than
either.

The held-out result turns on the second stage's input far more sharply than development
showed. The two level-only configurations gain about 23% (h −22.81%, j −22.70%), while every
configuration carrying the recent-residual and cross-province features gains 4% or less (f
−3.89%, i −2.27%, g −2.25%, and the perturbation that adds those features back to the reported
configuration −4.18%). On development the gap between the two groups was about 3 percentage
points; on the held-out year it is about 19. Had the full-feature boosting candidate remained the
reported configuration, as it was before the pre-registration, the held-out margin reported here
would have been −2.25%. Sixteen of the 26 perturbations move the size of the held-out margin by
more than two points, against eight of 26 on development, so the size is less stable on the
held-out year, not more.

Three frozen perturbations beat the pre-registered configuration on the held-out year and none
is promoted, because the year measures a pre-registered choice and selecting on it would spend
the only unused data this study has.

## 5. Discussion

**A residual-correction stage can add real, reproducible value, provided it is trained on the
right error.** Every candidate trained on stage 1's in-sample one-step residual failed and every
candidate trained on its multi-step out-of-sample error succeeded, on development data and, for
those run, on the held-out year. This is the condition Firmino et al. (2014) stated and the
prescription of Wolpert (1992), Breiman (1996) and Ben Taieb and Hyndman (2014), confirmed on a
small, noisy, real surveillance dataset: the in-sample residual of a fitted SARIMAX is white and
carries nothing, while the multi-step forecast error carries a level-dependent over-prediction, a
calendar bias and a horizon effect that a simple model recovers.

**The correction that generalised reads almost nothing.** The reported configuration sees the
horizon, the target month and stage 1's own forecast level relative to the province's residual
scale. The richer input, which adds recent residuals, their cross-province mean and trailing
incidence, scored within three points of it on development and nineteen points behind it on the
held-out year. The features that describe recent history are the ones that describe the
development period's reporting-regime breaks, and they did not transfer to an epidemic year. The
finding of the diagnostic analysis, that the forecast level was the strongest single correlate
of the error, is what the pre-registration rule ended up selecting for.

**A large relative improvement over a weak base model is not evidence of a good forecaster.**
The ensemble's best result, −22.8% on held-out data, was obtained on the year in which its base
model was most badly wrong, and it still lost by 22% to a seasonal mean. The internal ablation
this study was built to answer came out clearly positive, and on its own it would have been
misleading. The naive baselines, scored through the same pipeline on the same cells and frozen
into the held-out set, are what caught this. They were required by the study's plan before any
model existed, and they should be required by any study of a hybrid design.

**Calibration failed where it mattered most, for every model.** Coverage was tolerable on
ordinary years and collapsed on the epidemic year. The diagnostics identified the cause before
the year was opened: the standardised error is heavy-tailed because a Gaussian on raw counts has
a spread that does not grow with the level, and no rescaling of that spread repairs it without
losing CRPS. The one change identified as capable of repairing it, a count or heavier-tailed
predictive family at stage 1, was deliberately not built, because the study's premise was a
SARIMAX first stage and the question was whether a second stage earns its place on top of it.
That premise was a decision, and Section 6 records what it cost. Sesay et al. (2026) report that
a negative-binomial count autoregression kept its interval calibration for monthly dengue at
these horizons where a negative-binomial regression under-covered; a count model of that kind
is the natural next first stage.

**Part of the second stage's development margin repairs a choice made at stage 1.** A
no-differencing SARIMAX alone came within 0.6 CRPS of the two-stage configuration on development
data, and under it the correction was worth one percent. On the held-out year the no-differencing
row remained in the frozen set as a perturbation and the sign held. A reader who wants the
second stage's margin net of what a better-specified first stage would have recovered should read
the development margin as one to three percent, and the held-out margin as what it is: the gain
over the first stage that was actually used.

**Development performance understated, not overstated, the held-out margin.** The usual worry
about repeated selection on the same development cells did not materialise. Three rounds of
selection took place on the same 371 cells and the held-out margin was sixteen points larger
than the development margin, not smaller; the year's character mattered far more than any
optimism introduced by selection. This is one year and one dataset, and it is not a reason to
stop worrying about selection. It is a reason to seal a year and open it once.

**On the method of work.** The study was developed largely autonomously by an agentic system,
and the parts of it that a reader should trust least, the repeated selection on development
data, the choice of what to build next after each negative result, and the framing of the
answer, are exactly the parts a fast, cheap analyst can do more of than a slow one. What kept
them honest was structural rather than attentional: the sealed year and its recorded opening,
the frozen manifest and reporting rule, the requirement that every number reach a claim through
a file, the alternatives kept runnable and run, and checks that verify the record's shape with
code rather than with memory. Those checks verify shape and not content. A record can name the
wrong script; a claim can point at a result that does not support it. Structural checking
narrows where a human must look and does not remove the need to look, and the complete record,
including the paths not taken, is published so that a reader can.

## 6. Limitations

One held-out year of 192 province-months supports a direction, not a precise effect size, and
that year was an epidemic year unlike the development span; the held-out margin should not be
read as the expected margin on an ordinary year, for which the development estimate of one to
six percent is the better guide. Two of eighteen provinces contribute no scored cell, one because
it never reports in the development period and one because it stops reporting before the
evaluated span and reports nothing in 2010.

Stage 1 was fixed by decision and not repaired. Five reasonable alternatives were therefore
listed and not run, each with its reason: a log-transformed target and a count or heavier-tailed
predictive family at stage 1, both of which need a verified extension of the metric; a
multiplicative combination rule, undefined near zero; an ENSO covariate, a new data acquisition;
and evaluation through the Chap platform's harness, decided against at the outset. The
predictive-family fork is the most consequential absence in this study, because it is the one
change identified as able to repair coverage. The five candidates trained on the in-sample
residual were not run on the held-out year; all five lose to stage 1 on development and the
diagnostics explain why, but their held-out behaviour is not measured.

The diagnostics that informed the successful candidates read the same development test cells
those candidates were scored on. The reported configuration is the outcome of three rounds of
selection on those cells, and its development score carries the optimism that implies. The
held-out year is the guard against it, and on this year the guard turned out to be needed for
the opposite reason; on another year it might not.

The stability set covers the judgment calls its authors could enumerate. Its rows change one
thing at a time and do not cover interactions, and the two-point threshold that separates
perturbations that "move the size" from those that do not is a reporting convention. The
reported configuration's hyperparameters were fixed rather than searched.

The evaluation scheme was reused from an earlier project on the same data for comparability
rather than derived for this one. Its three-month test windows fix the horizon set stage 2 is
trained on, and a scheme with longer horizons would ask a different question.

Finally, the analysis was developed by an agentic system under written instructions, and those
instructions are part of the method. A change to them during the project would have been a
change of method; the instruction files are versioned and published with the code, and the one
respect in which the instruction set in force differed from the one intended is recorded in the
project's decision log.

## 7. Reproducibility, data and code availability

The complete analysis, with every alternative candidate, every stability row, every provenance
record, the claim collection, this article and its provenance sidecar, the instruction files
under which the work was done, and the plan and decision log that governed it, is public at
`github.com/sandvelab/sarimax-boosting-agentic-dengue-laos`. The root script reproduces the
reported analysis from a fresh clone at the pinned environment; the stability node reproduces
the paths not taken. At release, a clean-room reproduction that built the environment from
nothing in a fresh clone and ran the whole analysis found every comparable stored result byte
for byte identical, held-out rows included. The held-out manifest, its digest and the commit it
was frozen at are recorded before the year was opened, and the opening itself is recorded, so a
second opening would be visible.

The dengue case data are those published by the DHIS2 Chap project at a pinned commit of
`dhis2/climate-health-data`, whose schema attributes the case counts to OpenDengue (The Dengue
Mapping and Modelling Group, LSHTM; CC BY 4.0), with climate fields from ERA5-Land, boundaries
from OCHA COD-AB and population from WorldPop. The archived copy in the repository is
checksummed and re-verified on every run. The derived results and prose are released under
CC BY 4.0 and the code under the MIT licence.

## 8. Agency statement

The analysis was carried out by an agentic AI system (Claude, Anthropic) executing a plan
written by the human investigator, in batches, under a standing instruction file. The default
agency for every decision was the agent's, and the following were the human investigator's:
the architecture (a SARIMAX first stage with an additive residual-correction second stage), the
target, the data and the sealed year; the reuse of the evaluation scheme from an earlier project
for comparability; that no external reference model is cited; that the second stage's horizon
set is the evaluation scheme's; the decisions, after each negative result, to keep exploring
stage 2 rather than proceed to the stability phase, including trying climate covariates and
adapting a community model, and to conduct the diagnostic analysis; that stage 1 stays SARIMAX
as specified and is documented rather than repaired; that stage 2 is explored further after the
first stability run and one configuration annotated as the main path before the held-out freeze;
and, at the freeze, that the pre-registered configuration is kept and stage 1 is not reopened.
Every other decision, including stage 1's order, the design of every stage-2 candidate, the
selection rule, the perturbation manifests and their budgets, the held-out evaluation design and
the reporting rule, was the agent's, and is recorded with its basis in the repository's decision
log and provenance records. The human investigator directed the work between batches through
the plan and its decision log. This article was drafted by the agent from the claim collection.

## References

Ben Taieb, S. and Hyndman, R. J. (2014). Boosting multi-step autoregressive forecasts.
*Proceedings of the 31st International Conference on Machine Learning*, PMLR 32:109–117.

Breiman, L. (1996). Stacked regressions. *Machine Learning* 24:49–64.

Firmino, P. R. A., de Mattos Neto, P. S. G. and Ferreira, T. A. E. (2014). Correcting and
combining time series forecasters. *Neural Networks* 50:1–11.

Khampapongpane, B. et al. (2014). National dengue surveillance in the Lao People's Democratic
Republic, 2006–2012: epidemiological and laboratory findings. *Western Pacific Surveillance and
Response Journal* 5(1).

Sesay, M. M., Ngunyi, A. and Imboga, H. (2026). Probabilistic forecasting of monthly dengue
cases using epidemiological and climate signals: a BiLSTM-negative binomial model versus
mechanistic and count-model baselines. *PLOS Global Public Health*, e0005404.

Taşkaya-Temizel, T. and Casey, M. C. (2005). A comparative study of autoregressive neural
network hybrids. *Neural Networks* 18:781–789.

Wolpert, D. H. (1992). Stacked generalization. *Neural Networks* 5:241–259.

Zhang, G. P. (2003). Time series forecasting using a hybrid ARIMA and neural network model.
*Neurocomputing* 50:159–175.
