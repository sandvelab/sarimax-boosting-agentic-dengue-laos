Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 10)

# Batch 10 — a systematic second iteration on stage 2

## 1. The question this batch answered

After batch 9 the human asked for a systematic second iteration rather than a sixth candidate
picked ad hoc: a literature search on how a first-stage model's residuals can be predicted
better than chance and when residual-correction hybrids help or fail; an analysis of what stage
1's residuals actually are and what could predict them; and a couple of models built on both.
The premise stated in the request — that improving on stage 1 requires predicting its
residuals better than chance — is exactly right, and this batch made "chance" concrete rather
than assumed.

Three things were produced: a literature summary (§2 below, sources retrieved by web search
during the batch, not recalled), a diagnostic node `analysis/05_residualStructure` (§3), and two
new `04_stage2` alternatives, `f_oosErrorRidge` and `g_oosErrorBoosting` (§4). Both new
candidates beat stage 1 alone on mean CRPS with *improved* interval coverage — the first to
clear both of plan §2's bars — and `g_oosErrorBoosting` was promoted to `04_stage2`'s main path.

## 2. What the literature says, and what it implied here

Every reference below was found in a search result or fetched page during this batch; where
only an abstract or a secondary summary could be read, that is marked. Two searches were run in
parallel by delegated agents (one on residual-stage hybrids and calibration, one on dengue
predictors in Laos and mainland Southeast Asia); their reports were read in full and are
condensed here.

**Why residual bolt-ons fail.** Zhang (2003, *Neurocomputing* 50:159–175) is the template this
project's stage 2 follows: ARIMA, then a second model on lagged ARIMA residuals, added back.
Taşkaya-Temizel & Casey (2005, *Neural Networks* 18:781–789) showed on nine datasets that such
hybrids "do not necessarily outperform individual forecasts" and can underperform their
constituents, because a well-specified linear model leaves residuals with little exploitable
structure. Firmino et al. (2014, *Neural Networks* 50:1–11) make the condition explicit:
correcting a forecaster's errors only helps when those errors are not white noise. Successful
follow-ups changed the design rather than the learner: Khashei & Bijari (2011, *Applied Soft
Computing*; design from secondary summaries) give the second model the raw series as well as
the residuals; Wang et al. (2013, *Systems Research and Behavioral Science* 30:244–259) find a
multiplicative combination beats an additive one.

**Train the second level on out-of-sample errors, per horizon.** Wolpert (1992, *Neural
Networks* 5:241–259) and Breiman (1996, *Machine Learning* 24:49–64): a second-level model must
be trained on held-out first-level predictions, not in-sample fits. Chatfield (1993, *JBES*
11:121–135) and Hyndman's published notes document that in-sample one-step residuals understate
future errors. Most directly: Ben Taieb & Hyndman (2014, ICML, PMLR 32:109–117) keep a
recursive linear base forecast and correct its *h-step* errors directly with a boosted model at
each horizon, "consistently" improving out-of-sample forecasts. A counter-finding, flagged:
Zaborowski et al. (2026, arXiv:2608.10620, preprint) find that for *spread* post-processing on
M4 monthly series, in-sample residuals beat rolling one-step out-of-sample errors — so the
out-of-sample principle is established for the mean correction, less so for the variance.

**Calibration and count data.** Gneiting et al. (2005, *Monthly Weather Review* 133:1098–1118)
and Gneiting, Balabdaoui & Raftery (2007, *JRSS B* 69:243–268): CRPS rewards sharpness subject
to calibration, and a second stage can correct location and spread jointly (EMOS), with a
zero-truncated normal for non-negative quantities (Thorarinsdottir & Gneiting 2010, *JRSS A*
173:371–388). Kolassa (2016, *IJF* 32:788–803) and Czado, Gneiting & Held (2009, *Biometrics*
65:1254–1261): low-count series need count distributions and PIT-based checks. Sesay et al.
(2026, *PLOS Global Public Health*): for monthly dengue at 1–3 months, a negative-binomial
autoregressive model reached near-nominal coverage where a GLM did not, and lag-1 climate gave
no significant gain.

**Pooling across series.** Montero-Manso & Hyndman (2021, *IJF* 37:1632–1653): global models
fit across heterogeneous series are not more restrictive than local ones and should be given
more capacity; Januschowski et al. (2022, *IJF* 38:1473–1481) and Salinas et al. (2020, *IJF*
36:1181–1191): per-series scale normalisation is essential and must not leak the future.

**What predicts dengue at 1–3 months in this region.** Lao-specific: national surveillance began
in 1998, was paper-based until the electronic EWARN system in 2008, and not all provinces
reported until 2010; 2008 peaked unusually early, in June (Khampapongpane et al. 2014, *WPSAR*
5(1)). Temperature acts at lags of roughly 1–4 months and rainfall at 0–3 months with a hump
shape (Sugeno et al. 2023, *BMC Public Health*; Soukavong et al. 2024, *Scientific Reports*;
both 2015–2020 data). Cross-province synchrony and travelling waves are documented for the
region (van Panhuis et al. 2015, *PNAS* 112:13069–13074; Cummings et al. 2004, *Nature*
427:344–347), and cases from connected provinces improved Thai SARIMA forecasts by 5–10% at 1–3
months (Kiang et al. 2021, *Scientific Reports*). Early-season incidence predicts the season's
magnitude (Cousien et al. 2019, *EID* 25(12); Cuong et al. 2013, *EID* 19(6); Lauer et al.
2018, *PNAS* 115:E2175, abstract-level). Comparative studies repeatedly find climate adds little
beyond lagged incidence at short horizons and can hurt (Johansson et al. 2016, *Scientific
Reports* 6:33707; Johansson et al. 2019, *PNAS* 116:24268, via secondary sources; Benedum et
al. 2020, *PLOS NTD*), while pooled models beat per-location ones (Zhao et al. 2020, *PLOS NTD*).

**Implications taken into this batch.** (1) Check whether the residual stage 2 has been
training on is white; if it is, no learner will beat chance. (2) Change the target to the
h-step out-of-sample error, computed leakage-safely inside each training window. (3) Pool
across provinces on a standardised scale and back-scale per province. (4) Try
incidence-derived and cross-province features; expect little from short-lag climate. (5) Test
whether the coverage deficit is a spread-scale problem before building a spread correction.
Not taken up, logged: ENSO indices as an external forecast-time covariate (not in the
dataset); a negative-binomial or truncated-normal predictive family (a stage-1 specification
fork).

## 3. What stage 1's residuals are (`analysis/05_residualStructure`)

All numbers from `results/error_structure.json`, `results/test_cells.csv`,
`results/insample_residual_acf.csv` and `results/predictability.{csv,json}`.

- **The in-sample one-step residual is white.** Mean autocorrelation across provinces within
  ±0.06 at every lag 1–12 (lag 12: 0.004). Candidates a–e trained on noise.
- **The out-of-sample error is not, but it is skewed and concentrated.** Stage 1 over-predicts
  in two thirds of cells (median error near zero, mean positive); 55% of June–July errors are
  positive against 13–23% in January–April. Five provinces carry three quarters of the CRPS,
  and three of them are reporting-regime breaks in the test years (Savannakhet 166 → 8
  cases/month between the training window and 2008–09; Bokeo 0.7 → 39; Salavan 4.0 → 61). The
  Lao surveillance history above (paper to electronic reporting in 2008; provinces coming
  online through 2010) is the plausible cause. Those cells give |z| up to 164 and are the whole
  coverage deficit (87.1/82.1/79.0% by horizon).
- **Scaling sigma cannot fix coverage without losing CRPS.** The per-horizon factor that
  would reach nominal coverage (1.22/1.91/2.44) is an oracle, and even so it takes mean CRPS
  from 26.05 to 35.65: median |z| is 0.3, so most cells are already over-covered and pay for
  the tail. The in-window errors a leakage-safe stage 2 could estimate from are *over*-covered
  (factor 0.62–0.75), so an honest spread correction would shrink intervals. This is a
  predictive-family problem, not a spread-scale one. Clipping the mean at zero needs nothing
  estimated and lowers CRPS to 25.91.
- **What co-varies with the error at forecast time**: stage 1's own forecast level relative
  to the province's residual scale (Spearman −0.27; a high forecast is usually too high), the
  calendar (−0.21), the last residual at the origin (+0.20 by rank), the horizon, trailing
  incidence (−0.12), the cross-province mean (−0.09). Climate anomalies at lags 1–3: |ρ| ≤ 0.05.
- **Better than chance, cross-validated on the test cells**: of 56 feature-set × family
  configurations (leave-one-split-out, permutation-based chance threshold), 10 beat chance on
  skill and only 2 lower CRPS — both the forecast-level features with a ridge (−0.8%). The
  earlier candidates' input never beats chance in any family. Rich feature sets fit with trees
  lose in CRPS even with positive skill on the standardised scale, because a gain in many small
  cells is paid for in a few large-se cells.

## 4. The two candidates

Both train on stage 1's h-step error computed inside each split's training window from every
origin after the 24-month warm-up, with parameters fixed at the window's estimates
(`lib.residual_features.pseudo_oos_errors`, verified equal to a truncated-data forecast) —
roughly 4,700–5,700 rows per split, pooled across the 17 provinces — as z = error / se
winsorised at ±3, from forecast-time features only (`lib.stage2_oos.FEATURES`: horizon and
target-month indicators; forecast level relative to the province's residual scale; recent
standardised residuals and their cross-province mean at the origin; trailing-12-month incidence
anomaly; trailing-24-month zero fraction; no climate). The correction z-hat × se is added to
stage 1's mean, clipped at zero; sigma is unchanged. Stage 1 is re-derived and verified
bit-for-bit against `02_stage1`'s stored forecast before any residual is used (408/408 cells).

| Model | Mean CRPS | vs. stage 1 | 90% coverage | Splits improved | Cells improved |
|---|---|---|---|---|---|
| Stage 1 alone | 26.05 | — | 82.7% | — | — |
| Stage 1, mean clipped at zero | 25.91 | −0.56% | 82.7% | — | — |
| `f_oosErrorRidge` (ridge, α=10) | **25.63** | **−1.64%** | **84.6%** | 4 of 8 | 56.6% |
| `g_oosErrorBoosting` (GBM, depth 3, 150 trees) | **25.16** | **−3.41%** | **85.7%** | 5 of 8 | 56.6% |

The correction alone, against the clipped stage 1, is −1.09% (ridge) and −2.87% (boosting).
Gains grow with horizon (ridge: h=1 −0.7%, h=3 −2.4%; boosting: h=1 +0.8%, h=2 −5.6%, h=3
−4.2%). By province the gains sit in Khammouane, Salavan, Bokeo and Champasak; both lose in
Savannakhet (+232 and +211 CRPS-units summed), where stage 1's se of 200–414 is tens of times
the 2008–09 case level, so a standardised correction of +0.4–0.6 becomes 130–190 cases — the
correction inherits stage 1's spread miscalibration. Vientiane Capital also loses (+79, +127):
the level shrinkage was wrong in the genuine late-2009 surge. The ridge's coefficients are
stable across all eight splits (`f_oosErrorRidge/results/ridge_coefficients.csv`): forecast
level −0.19 to −0.22, July +0.09 to +0.12, January −0.07, last residual +0.06 to +0.07,
trailing zero fraction −0.09 to −0.14. The boosting model's importances rank the same
features first (`g_oosErrorBoosting/results/feature_importances.csv`).

Updated ranking among candidates clearing both bars: **g_oosErrorBoosting (25.16) <
f_oosErrorRidge (25.63) < stage 1 alone (26.05) < a_linearLags (26.26) < d_linearClimate
(26.85) < seasonal climatology (26.91) < b_gradientBoosting (27.68) < c_bayesianRidge (28.07)
< persistence (28.32)**, with `e_pooledRandomForest` (25.89, coverage 64.4%) alongside.
`g_oosErrorBoosting/results/all_candidates_comparison.json` holds all seven.

## 5. Judgment calls logged, with agency

- **A diagnostic node in the tree rather than a scratch investigation** (`agent-autonomous`):
  its numbers shaped the candidates, so they had to be file-grounded (AGENTS.md §1). It is
  numbered `05` because it reads stage 1's stored backtest; no candidate reads its output, so
  the run order carries no data dependency. The stability node takes the next free number; the
  invariant checker's manifest paths (`05_stability`, inherited from the prior project) will
  need revising when phase D starts.
- **Characterising the development backtest's own test cells and designing candidates on
  them** (`agent-autonomous`, plan §4b): development-set model selection, which is what the
  development data is for; the sealed 2010 holdout guards against the optimism. The development
  scores above are read accordingly.
- **The target** (h-step in-window out-of-sample error, standardised by stage 1's se,
  winsorised at ±3), **the features** (no climate), **the family pair** (ridge and shallow
  boosting, fixed hyperparameters, no search), **and the combination rule** (clip at zero,
  sigma unchanged): each `agent-autonomous`, each argued in the node's provenance with the
  alternatives considered, and each a perturbation for phase D.
- **No spread correction** (`agent-autonomous`): on the diagnostic evidence it would lose CRPS
  and an honest in-window estimate would shrink the intervals; the fix belongs to stage 1's
  predictive family and is logged as a fork.
- **Promoting `g_oosErrorBoosting` to the main path** (`agent-autonomous`, its own commit,
  reversible with `/node promote`): the first main path that earns its place on development
  evidence. The margin is modest, uneven across provinces and splits, and unsearched
  hyperparameters make the ridge–boosting gap itself a stability question.
- **Two comment-only source edits after the runs** to satisfy the invariant checker's
  heuristics honestly (naming the absence of a seed; rewording a warm-up comment the
  cross-step heuristic flagged): no logic changed, nothing re-run, and each affected
  provenance record carries a section naming the old and new digests.

## 6. Checks run

`/validate invariants`: all checks pass except `git`, which failed only mid-batch on expected
uncommitted edits and on the pre-existing untracked `.idea/`. Stage-1 re-derivation verified
bit-for-bit in all three new nodes (408/408 cells). Determinism verified per `/seed` by full
second runs diffed byte for byte: `g_oosErrorBoosting`'s scoring script and
`05_residualStructure`'s predictability script (both draw real randomness), identical. The
statsmodels mechanism the in-window errors rely on (`get_prediction(dynamic=True)`) was checked
against `apply(refit=False)` on a truncated series before use.

## 7. What batch 11 inherits

A stage 2 that earns its place on development data, and an understanding of why the first five
did not. Phase D (ledger rows 11–13) now has a real margin to test: the perturbation manifest
should include stage 1's specification (a count or heavier-tailed family is the one change that
could fix coverage), the stage-2 target's winsorisation bound and standardisation, the ridge
penalty and boosting configuration, the feature set with and without the cross-province and
incidence terms, clipping, per-horizon versus pooled fitting, and the training-window warm-up.
Two refinements are logged as untried and directly motivated: bounding the correction relative
to the forecast level (the Savannakhet failure), and a true rolling refit for the in-window
errors. The literature's one climate signal with multi-month lead, ENSO, is not in the dataset
and would be a new acquisition.
