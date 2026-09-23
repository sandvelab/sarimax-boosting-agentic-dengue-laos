# Provenance sidecar — `26-09-23_twoStageDengueLaosManuscript.md`

Each statement in the manuscript, mapped to the claim it rests on (`../claims/claims.md`) or,
where it describes the method rather than a result, to the stored file that fixes it. Keyed by
section and by the opening words of the sentence, so the mapping survives reformatting. Where a
paragraph's statements all rest on the same claims, the paragraph is one row.

**Method statements are marked `method:`.** They are design facts read from a result file, a
node's `claim.md` or the plan, not findings; `/claims check-text` flags them because no claim
asserts them, which is correct. **Literature statements are marked `literature:`** and rest on
the batch-10 literature record (`AI-generated/batch-reports/26-09-20_b10_stage2SystematicSecondIteration.md`
§2), where every reference was retrieved and read during that batch. When this manuscript was
written the bibliographic details of all eight references were re-verified by web search, and the
characterisation of Sesay et al. (2026) was checked against the article's own abstract and
corrected to it (`journals.plos.org/globalpublichealth/article?id=10.1371/journal.pgph.0005404`).

## Abstract

| Statement | Rests on |
|---|---|
| "Two-stage forecasting designs fit a base model…" | literature: Zhang (2003); Taşkaya-Temizel & Casey (2005); Firmino et al. (2014) as recorded in the batch-10 record |
| "Stage 1 is a per-province SARIMAX on raw counts; stage 2 predicts stage 1's forecast error…" | method: `analysis/02_stage1/claim.md` · `analysis/04_stage2/claim.md` |
| "Ten stage-2 candidates were built…" | **C32** |
| "Development used 1998–2009 under a fixed rolling-origin backtest… beside persistence and seasonal-climatology baselines" | method: `analysis/01_data/03_backtest_scheme/results/schedule_summary.json`; **C24**, **C27** |
| "The reported configuration was chosen by a rule written before the last candidate's result was seen" | **C31** (scope), **C32**; method: plan §4b (2026-09-21) |
| "The year 2010 was sealed throughout, and opened once across a perturbation set of 33 rows frozen in advance, with the reporting rule frozen with it" | method: `analysis/06_stability/results/holdout_freeze.json` · `results/run_status_holdout.csv`; **C14**, **C16** |
| "Every judgment call is an alternatives node… every reported figure is read from a stored file, and the whole analysis reproduces byte for byte from a fresh clone" | method: `AGENTS.md` §1–§4; `AI-generated/validation/2026-09-22_cleanroom-artefacts/summary.json` and the release-time clean-room run recorded in the batch-20 report |
| "stage 1 alone (mean CRPS 26.05) beats both baselines" | **C25**, **C27** |
| "the five candidates trained on stage 1's in-sample one-step residual all fail… that residual is essentially white" | **C6**, **C28**, **C32** |
| "Candidates trained on stage 1's multi-step out-of-sample error… succeed" | **C1**, **C31**, **C32** |
| "reads only the horizon, the target month and the forecast level, and scores 24.35 (−6.53%) with coverage improved from 82.7% to 85.2%" | **C31** |
| "the sign of its margin survives all 26 development perturbations" | **C8** |
| "On the held-out year it scores 99.20 against stage 1's 128.51 (−22.81%), improves all four splits and 75% of cells, and the sign survives all 26 frozen perturbations" | **C14**, **C16** |
| "On the same cells, seasonal climatology scores 77.29" | **C17** |
| "2010 was an epidemic year with 22,903 reported cases against 12,291 in the two development test years" | **C19** |
| "no model in the frozen set covers more than 61.5% of outcomes at a nominal 90%" | **C18** |
| Conclusions paragraph | interpretation of **C14**, **C17**, **C18**, **C20**; plan §2 |

## 1. Introduction

| Statement | Rests on |
|---|---|
| "Dengue surveillance produces monthly case counts by province…" through "fit, take residuals, fit again on the residuals" | method: plan §1 (the architecture and its rationale) |
| "The design has a long record and a mixed one." through "near-nominal coverage for monthly dengue where a Gaussian model did not" | literature: Zhang (2003); Taşkaya-Temizel & Casey (2005); Firmino et al. (2014); Wolpert (1992); Breiman (1996); Ben Taieb & Hyndman (2014); Sesay et al. (2026), each as characterised in the batch-10 record §2 |
| "The question this study asks is therefore narrow and internal…" | method: plan §1–§2; `analysis/claim.md` |
| "We do not compare against an external reference model. We do compare against the two baselines…" | method: plan §2, §4b (2026-09-20, human-set) |
| "the held-out year was sealed before any modelling began and opened once… pre-registered by a rule written before the last candidate's result was known" | method: plan §3; `analysis/06_stability/results/holdout_freeze.json`; **C31** (scope) |
| "the analysis was developed largely autonomously by an agentic AI system under a fixed set of written instructions… The paths not taken are kept runnable and were run" | method: `AGENTS.md` §2–§4; `analysis/06_stability/claim.md`; plan §4b |

## 2. Data

| Statement | Rests on |
|---|---|
| "monthly reported dengue case counts for the eighteen admin-1 provinces… January 1998 to December 2010… harmonised and published by the DHIS2 Chap project… whose schema attributes the case counts to OpenDengue (LSHTM, CC BY 4.0)" | method: `Archive/lao-dataset/provenance.md` (2026-08-23 and 2026-09-23 sections) · `Archive/lao-dataset/chap_LAO_admin1_monthly_schema.json` |
| "The file is a complete 18 × 156 grid…" | **C22** |
| "It also carries monthly rainfall, mean temperature, mean relative humidity and a static population figure… read only by two not-taken stage-2 candidates, by the diagnostic analysis of stage 1's errors, and by one row in each stability set" | method: `Archive/lao-dataset/README.md` · `analysis/04_stage2/claim.md` (candidates d, e) · `analysis/05_residualStructure/claim.md` (answer 4) · `analysis/06_stability/results/manifest.csv` (the climate-anomaly rows of v1 and v2) |
| "partitioned once into a development set of 2,592 rows… and a held-out set of 216 rows" | **C22** |
| "The held-out set's completeness was confirmed by counting rows, provinces and months without reading a case value, and its digest was recorded" | **C22**; method: `analysis/06_stability/results/holdout_freeze.json` (`frozen_inputs`) |
| "17 of the 18 provinces have at least 24 present months… Vientiane province (LA-VI) reports nothing… Xaisomboun (LA-XN) has 96 of 144… stops reporting before the evaluated span" | **C23** |
| "it reports no cases in any month of 2010, so it contributes none to the held-out evaluation" | method: `analysis/06_stability/results/holdout_year_context.json` (`note_on_cells`); **C14** (192 cells, 16 provinces) |
| "The set of modelled provinces was fixed from the development months alone and was deliberately not re-derived" | **C23** (scope); method: plan §4b (2026-09-22) |
| "Lao national dengue surveillance began in 1998 and was paper-based until an electronic system was introduced in 2008" | literature: Khampapongpane et al. (2014), as characterised in the batch-10 record §2 |

## 3. Methods

| Statement | Rests on |
|---|---|
| 3.1 "All models are scored by the continuous ranked probability score… 90% interval… Lower CRPS is better" | method: `analysis/00_metric/claim.md`; plan §4 |
| 3.1 "verified against an independent library implementation, matching `properscoring.crps_gaussian` to within 1.11 × 10⁻¹⁶ over a 45-case grid and matching a Monte-Carlo ensemble estimator…" | **C21** |
| 3.1 "rolling-origin scheme… eight splits… stride of three months… January 2008 to December 2009, with the first split trained on 120 months and the last on 141" | **C24** |
| 3.1 "408 cell slots, of which 371 carry an observation and are scored" | **C25**; method: `analysis/02_stage1/results/conclusion.json` (`n_cells_total`, `n_cells_scored`) |
| 3.1 "The scheme was fixed in advance and reused from an earlier project… for comparability" | **C24** (scope); method: plan §4b (2026-09-20, human-set) |
| 3.1 "A two-stage configuration 'earns its place' if…" | method: plan §2 |
| 3.2 "per-province SARIMAX(1,1,1)×(1,0,0)₁₂… refit at every split… horizons one to three" | **C25**; method: `analysis/02_stage1/results/conclusion.json` (`model`) |
| 3.2 "The order was a first, defensible default rather than a selected one" | **C26** (sixth weakness); method: `analysis/02_stage1/provenance/sarimax_backtest.md` (`alternatives-considered`) |
| 3.2 "its weaknesses were documented rather than repaired, a decision the human investigator made and reaffirmed" | **C26** (`by: human-set`); method: plan §4b (2026-09-21, 2026-09-22) |
| 3.2 "Fitting is deterministic; no stage-1 fit failed in any of the 136 development fits" | **C25**; method: `analysis/02_stage1/provenance/sarimax_backtest.md` (`seeds`) |
| 3.3 Persistence and seasonal climatology definitions | method: `analysis/03_baselines/01_persistence/claim.md` · `analysis/03_baselines/02_climatology/claim.md`; **C27** (alternatives) |
| 3.4 "Stage 2 never sees the target… stage 1's standard error unchanged, and the mean clipped at zero" | method: plan §1; `analysis/04_stage2/h_levelOnlyBoosting/results/conclusion.json` (`model`, `stage2_config`) |
| 3.4 "trained on every horizon the evaluation scores, h = 1..3, with the horizon set read from the backtest scheme" | method: `analysis/04_stage2/h_levelOnlyBoosting/results/conclusion.json` (`horizon_months`); plan §4b (2026-09-21, human-set) |
| 3.4 "Ten candidates were built as alternatives in the analysis tree and all ten remain there" | **C32** |
| 3.4 In-sample-residual candidates a–e: their inputs and families | method: `analysis/04_stage2/claim.md` (batches 4–9 answers) |
| 3.4 Out-of-sample-error candidates f–j: target construction, standardisation, winsorisation at ±3, pooling, "roughly 4,700 and 5,700 training rows per split", hyperparameters, feature sets, bound | method: `analysis/04_stage2/claim.md` (batch-10 and batch-14 answers) · `analysis/04_stage2/h_levelOnlyBoosting/results/conclusion.json` (`stage2_config`, `n_training_rows_by_split`) |
| 3.5 The diagnostic analysis and what it measured | method: `analysis/05_residualStructure/claim.md` |
| 3.5 "This analysis reads the same development test cells… development-set selection… the held-out year is the guard" | **C29**, **C30** (scope); method: plan §4b (2026-09-20) |
| 3.6 The selection rule and "the third round of selection on the same 371 development cells" | **C31**, **C32**; method: plan §4b (2026-09-21, human-set) · `analysis/04_stage2/claim.md` (batch 14) |
| 3.6 "frozen into the held-out manifest before the year was opened, and two better-scoring development perturbations… not promoted at the freeze" | method: plan §4b (2026-09-22, human-set) · `analysis/06_stability/results/holdout_freeze.json` |
| 3.7 The perturbation manifest and what each row changes; "Twenty-six such rows" | **C8** (scope); method: `analysis/06_stability/results/manifest.csv` · `analysis/06_stability/claim.md` (batch 11, 14) |
| 3.7 "'move the size'… more than two percentage points; this is a reporting threshold, not a test" | method: `analysis/06_stability/results/distribution_v2.json` (`sensitivity_points`); plan §4b (2026-09-21) |
| 3.7 "Five further alternatives were listed and not run, each with its reason…" | **C7** |
| 3.8 "frozen with 43 rows, of which 33 were run… four of the nine not-taken siblings… the 26 development perturbations under held-out names" | method: `analysis/06_stability/results/holdout_freeze.json` · `results/manifest_holdout.csv` · `results/run_status_holdout.csv`; **C16** (scope) |
| 3.8 "The five in-sample-residual candidates and the five unrun alternatives were recorded as not run, with reasons" | **C16** (alternatives); method: `results/manifest_holdout.csv` (`reason_if_not_run`) |
| 3.8 "four successive three-month blocks covering 2010 exactly once… the four splits train on 144 to 153 months… The province set is development's seventeen" | **C24**; method: `analysis/06_stability/results/holdout_runner_verification.json`; plan §4b (2026-09-22) |
| 3.8 "The reporting rule was frozen with the set…" | method: `analysis/06_stability/results/holdout_freeze.json` (`reporting_rule`) |
| 3.8 "The machinery… verified before the freeze… zero mismatches over 408 cells each" | method: `analysis/06_stability/results/holdout_runner_verification.json`; plan §4b (2026-09-22) |
| 3.8 "The opening itself is recorded in a tracked file with the commit, the manifest's digest and the held-out file's digest" | method: `analysis/06_stability/results/run_status_holdout.csv` |
| 3.9 The tree, provenance records, sub-analyses and alternatives, "No number reaches a claim except through a file", the sidecar | method: `AGENTS.md` §1–§3; `AI-internal/skill-references/provenance-record.md`; this file |
| 3.9 "carried out by an agentic AI system executing a written plan in batches… Every decision carries an agency label" | method: `AGENTS.md` §4; plan §3, §4b |
| 3.9 "Three checks were run rather than trusted…" | method: `AGENTS.md` §5; `AI-internal/useful-scripts/check_invariants.py` · `cleanroom.sh`; `AI-generated/validation/` |
| 3.9 "CPython 3.13 with 18 locked packages, among them statsmodels 0.15.0… scikit-learn 1.9.1; the project seed is 20260920" | method: `environment/environment.yml` · `environment/lock.txt`; plan §4 |

## 4. Results

| Statement | Rests on |
|---|---|
| 4.1 "stage 1 alone scores mean CRPS 26.05 with 90% coverage 82.7%. Persistence scores 28.32 and seasonal climatology 26.91… by 7.99% and 3.20%" | **C25**, **C27** |
| 4.2 "Four lose to stage 1 alone on CRPS: … 26.26 … 26.85 … 27.68 … 28.07. The pooled random forest scores 25.89… covers 64.4%" | **C32**, **C6** |
| 4.2 "the pooled correction, shaped by provinces spanning under one to over 150 mean monthly cases, overshoots… drives many forecasts below zero" | method: `analysis/04_stage2/claim.md` (batch 9) · `analysis/04_stage2/e_pooledRandomForest/results/coverage_collapse_diagnosis.json` |
| 4.2 "Adding climate covariates to the linear correction made it worse, not better" | **C32** (a 26.26 vs d 26.85) |
| 4.3 "The in-sample one-step residual is essentially white… within ±0.06… 0.004 at lag 12… at most 3 of the 17 provinces" | **C28** |
| 4.3 "Stage 1 over-predicts in about two thirds of cells… +2.6… +7.3… 55% of June and July… 13–23%… Five provinces carry three quarters… Savannakhet 166 to 8, Bokeo 0.7 to 39, Salavan 4 to 61… up to 164… the whole coverage deficit" | **C29** |
| 4.3 "standard error does not grow with its forecast level… an oracle multiplier… raises mean CRPS from 26.05 to 35.65. Negative forecast means occur in 4.0% of cells" | **C26** |
| 4.3 "Across 56 feature-set and family configurations… 10 beat a permutation null… only 2 lowered CRPS… 0.84%… 0.32 standardised units" | **C30** |
| 4.4 "All five candidates trained on the in-window multi-step out-of-sample error clear both criteria… 25.63 (−1.64%)… 25.16 (−3.41%, coverage 85.7%)… 24.53… 24.35… 24.29" | **C32**, **C1**, **C31** |
| 4.4 "By the pre-registered rule the level-only configuration (h) is the reported one… tie within 0.1 CRPS and on splits improved (6 of 8)… the simpler" | **C31**, **C32**; method: `analysis/04_stage2/h_levelOnlyBoosting/claim.md` |
| 4.4 "mean CRPS 24.35 against stage 1's 26.05 (−6.53%), with coverage improved from 82.7% to 85.2%" | **C31** |
| Table 1, every row | **C32** (all ten CRPS values), **C25** (stage 1), **C27** (baselines), **C31** (h coverage), **C1** (g coverage), **C6** (e coverage); f and i coverage and c coverage: method: `analysis/04_stage2/claim.md` (batch 10, batch 14 table, batch 6 answer) |
| 4.5 "in all 26 perturbations… −1.06% to −10.41% with a median of −5.91%… at least 4 of the 8 splits" | **C8** |
| 4.5 "Eight perturbations move it by more than two percentage points… (−10.41%)… (−10.16%)… (−3.47%)… (−3.40%)… (−3.32%)… (−2.99%)… (−1.06%)… (−1.06%)… (−4.76% to −6.45%)" | **C9** |
| 4.5 "a reader who weights it most should read the development margin as about three percent" | **C9** (alternatives) |
| 4.5 "a no-differencing stage 1… alone scores 24.93… within 0.6 CRPS… only −1.06%. Part of the second stage's development margin is a repair of stage 1's differencing choice" | **C10** |
| 4.5 "first run around the full-feature boosting candidate (g)… all 29 perturbations… (−0.70% to −10.64%, median −3.32%), nine moved the size, and the rolling refit gave the smallest margin (−0.70%)" | **C2**, **C3** |
| 4.5 "Khammouane, Salavan, Bokeo and Xiangkhouang improved in every one of those 30 combinations while Savannakhet and Vientiane Capital improved in at most 20%" | **C4** |
| 4.5 "Changing the reported configuration from g to h moved the margin from −3.41% to −6.53%, and 20 of the 22 perturbations… median of 2.3 points; the two exceptions are stage-1 changes" | **C11** |
| 4.5 "Khammouane, Salavan, Bokeo, Xiangkhouang and Xekong improve in every one of the 27 combinations… Champasak in 25; Oudomxay never… at most 10%" | **C12** |
| 4.5 "three months ahead in all 27 combinations, two months ahead in 26 and one month ahead in 23; around g it helped one month ahead in fewer than half" | **C13**, **C5** |
| 4.6 "The frozen set was run once, in full: 33 of 33 planned rows. Nothing was added, dropped, re-tuned, re-run or promoted afterwards" | method: `analysis/06_stability/results/run_status_holdout.csv`; plan §4b (2026-09-22) |
| 4.6 "One province reports no cases for any month of 2010, so 192 of the 204 frozen cell slots are scored, over 16 provinces" | **C14** (scope); method: `analysis/06_stability/results/holdout_year_context.json` |
| 4.6 "99.20 against… 128.51 (−22.81%)… 61.5% against 57.3%… all four splits, 75% of cells and every horizon" | **C14** |
| 4.6 "from −29.25% to −4.18% with a median of −20.89% and quartiles at −22.81% and −17.82%, with no row improving fewer than half its splits" | **C16** |
| 4.6 "16.3 percentage points larger… 29 have a larger margin… (median shift −15.6 points). Development understated…" | **C15** |
| 4.6 "Seasonal climatology scores 77.29… persistence (127.58)… stage 1 beat climatology by 3.2%… 28% worse" | **C17** |
| Table 2, every row | **C14**, **C17**, **C18** (2010 columns); **C25**, **C27**, **C31** (development columns) |
| 4.6 "57.3%… 61.5%, against 82.7% and 85.2%… baselines are worse still… by 4.2 percentage points… no configuration in the frozen set is adequately calibrated" | **C18** |
| 4.6 "22,903 reported cases… 12,291… 3.6 times… 5,649 cases in September 2010… 1,410" | **C19** |
| 4.6 "A SARIMAX on raw counts with a Gaussian predictive interval does not follow that… a model with no trend at all does better than either" | interpretation of **C17**, **C18**, **C19**, **C26** |
| 4.6 "The two level-only configurations gain about 23% (h −22.81%, j −22.70%)… (f −3.89%, i −2.27%, g −2.25%… −4.18%)… about 3 percentage points… about 19… would have been −2.25%" | **C20** |
| 4.6 "Sixteen of the 26 perturbations move the size… against eight of 26 on development" | **C16** |
| 4.6 "Three frozen perturbations beat the pre-registered configuration on the held-out year and none is promoted" | method: `analysis/06_stability/results/perturbation_effects_holdout.csv`; plan §4b (2026-09-22) |

## 5. Discussion

Interpretive paragraphs. Each conclusion is drawn from the claims named; the inference is the
authors', the numbers are not.

| Statement | Rests on |
|---|---|
| "Every candidate trained on stage 1's in-sample one-step residual failed and every candidate trained on its multi-step out-of-sample error succeeded" | **C6**, **C32**, **C20** (held-out f, g, i, j) |
| "the in-sample residual of a fitted SARIMAX is white… the multi-step forecast error carries a level-dependent over-prediction, a calendar bias and a horizon effect" | **C28**, **C29** |
| "This is the condition Firmino et al. (2014) stated and the prescription of Wolpert (1992), Breiman (1996) and Ben Taieb and Hyndman (2014)" | literature: batch-10 record §2 |
| "The richer input… within three points of it on development and nineteen points behind it on the held-out year" | **C20** |
| "the forecast level was the strongest single correlate of the error" | method: `analysis/05_residualStructure/claim.md` (answer 4) · `results/error_structure.json` |
| "The ensemble's best result, −22.8% on held-out data… still lost by 22% to a seasonal mean" | **C14**, **C17**, **C19** |
| "They were required by the study's plan before any model existed" | method: plan §2, §4 (required baselines) |
| "Coverage was tolerable on ordinary years and collapsed on the epidemic year" | **C18** |
| "the standardised error is heavy-tailed because a Gaussian on raw counts has a spread that does not grow with the level, and no rescaling of that spread repairs it without losing CRPS" | **C26**, **C29** |
| "The one change identified as capable of repairing it… was deliberately not built" | **C7**, **C18** (alternatives); plan §4b (2026-09-21, human-set) |
| "Sesay et al. (2026) report that a negative-binomial autoregression reached near-nominal coverage" | literature: batch-10 record §2 |
| "A no-differencing SARIMAX alone came within 0.6 CRPS… worth one percent. On the held-out year the no-differencing row remained in the frozen set… the sign held" | **C10**, **C16** |
| "read the development margin as one to three percent" | **C9** (alternatives), **C10** |
| "Three rounds of selection took place on the same 371 cells and the held-out margin was sixteen points larger" | **C31** (scope), **C15** |
| "On the method of work" paragraph | method: `AGENTS.md` §1, §4, §5; `.claude/commands/validate.md` ("these checks verify shape and never content") |

## 6. Limitations

| Statement | Rests on |
|---|---|
| "One held-out year of 192 province-months… an epidemic year… the development estimate of one to six percent" | **C14**, **C19**, **C9**, **C10**, **C31** |
| "Two of eighteen provinces contribute no scored cell…" | **C23**; method: `analysis/06_stability/results/holdout_year_context.json` |
| "Stage 1 was fixed by decision and not repaired. Five reasonable alternatives were therefore listed and not run, each with its reason…" | **C7**; method: `analysis/06_stability/results/manifest.csv` (`reason_if_not_run`); plan §4b (2026-09-21) |
| "The five candidates trained on the in-sample residual were not run on the held-out year" | **C16** (alternatives); method: `analysis/06_stability/results/manifest_holdout.csv` |
| "The diagnostics… read the same development test cells… three rounds of selection" | **C29**, **C30** (scope), **C31** (scope) |
| "Its rows change one thing at a time and do not cover interactions, and the two-point threshold… is a reporting convention. The reported configuration's hyperparameters were fixed rather than searched" | method: `analysis/06_stability/results/manifest.csv`; `distribution_v2.json` (`sensitivity_points`); `analysis/04_stage2/claim.md` (batch 10: "fixed rather than searched hyperparameters") |
| "The evaluation scheme was reused from an earlier project…" | **C24** (scope) |
| "the one respect in which the instruction set in force differed from the one intended is recorded in the project's decision log" | method: plan §4b (2026-09-23) |

## 7. Reproducibility, data and code availability

| Statement | Rests on |
|---|---|
| Repository contents and URL | method: plan §4 (git remote); `README.md`; `AGENTS.md` §3 Rule 10 |
| "At release, a clean-room reproduction… found every comparable stored result byte for byte identical, held-out rows included" | method: `AI-generated/validation/2026-09-22_cleanroom-artefacts/summary.json` (288 + 1 corrected, batch 19) and the release-time run in `AI-generated/validation/2026-09-23_cleanroom-artefacts/summary.json`, as reported in `AI-generated/batch-reports/26-09-23_b20_release.md` |
| "The held-out manifest, its digest and the commit it was frozen at are recorded before the year was opened, and the opening itself is recorded" | method: `analysis/06_stability/results/holdout_freeze.json` · `results/run_status_holdout.csv` |
| Data sources and licences | method: `Archive/lao-dataset/provenance.md` (2026-09-23 section) · `chap_LAO_admin1_monthly_schema.json`; `LICENSE` · `LICENSE-CODE` |

## 8. Agency statement

| Statement | Rests on |
|---|---|
| Every human-set decision listed | method: plan §4 and §4b, the rows marked `human-set` (2026-09-20 through 2026-09-23); **C26** (`by: human-set`) |
| "Every other decision… was the agent's" | method: plan §4b, the rows marked `agent-autonomous`; the `agency:` field of every provenance record under `analysis/` |
