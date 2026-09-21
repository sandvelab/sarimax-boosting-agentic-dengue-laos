# Claim collection

Everything the analysis supports, each statement bound to the result grounding it. The
manuscript is written from this file; nothing enters the manuscript that is not here.

Format — one block per claim, appended by `/claims add`:

```
## C1
The statement, in one or two sentences.
grounds: analysis/02_measure/a_jaccard/results/summary.tsv
node: analysis/02_measure/a_jaccard
scope: holds for the strict filtering convention only
alternatives: the base-pair measure gives a weaker effect (see C9)
by: agent-autonomous
```

`by:` is the agency field — `human-set`, `agent-on-human-assessment` or `agent-autonomous`.
Claims about **stability** are claims like any other and belong here too: what the
perturbation set showed, and which choices the conclusion turned out to be sensitive to.

No claims yet — the tree has not produced a result.

## C1
On the development backtest, the two-stage ensemble with the main-path stage 2 (gradient-boosted trees on stage 1's in-window h-step out-of-sample error, pooled across provinces on the standardised-error scale) beats stage 1 alone on mean CRPS, 25.16 against 26.05 (-3.41%), with 90% interval coverage improved from 82.7% to 85.7%.
grounds: analysis/04_stage2/g_oosErrorBoosting/results/comparison.json · analysis/04_stage2/g_oosErrorBoosting/results/all_candidates_comparison.json
node: analysis/04_stage2/g_oosErrorBoosting
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened
alternatives: the five candidates trained on stage 1's in-sample one-step residual (a-e) do not clear both criteria; f_oosErrorRidge, the linear sibling on the same target, does, by -1.64%
by: agent-autonomous

## C2
The sign of the central comparison is stable: in all 29 planned perturbations of stage 1's specification, the training window, the backtest scheme, the modelability threshold and every constant of the main-path stage 2, the two-stage ensemble beats stage 1 alone on mean CRPS with 90% coverage not worse; the margin ranges from -0.70% to -10.64% (median -3.32%), and no perturbation flips it.
grounds: analysis/06_stability/results/distribution.json · analysis/06_stability/results/conclusions.csv
node: analysis/06_stability
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened; the set is the frozen development manifest (29 tier-2 rows), and five tier-3 alternatives were not run
alternatives: none of the run perturbations supports the opposite statement; the alternatives that could (a count or heavier-tailed predictive family at stage 1) were not run
by: agent-autonomous

## C3
The size of the margin depends on how the training errors are made and on stage 1's specification, not on the stage-2 family's hyperparameters or seed: nine perturbations move it by more than two percentage points from the main path's -3.41% -- larger under the airline or stationarity-enforced stage 1, Chap's default scheme, the level-only feature set, the bounded correction, dropping the cross-province term or adding climate anomalies; smaller under a 2002 training-window start (-0.92%) or a true rolling refit of the in-window errors (-0.70%) -- while all seven hyperparameter and seed perturbations stay within two points (-1.63% to -4.19%).
grounds: analysis/06_stability/results/perturbation_effects.csv · analysis/06_stability/results/distribution.json
node: analysis/06_stability
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened
alternatives: the rolling-refit row is the honest version of the main path's fixed-parameter shortcut and gives the smallest margin; a reader who weights it most should read the margin as under one percent
by: agent-autonomous

## C4
The gain is concentrated: Khammouane, Salavan, Bokeo and Xiangkhouang improve in every one of the 30 combinations run (main and 29 perturbations), while Savannakhet, Vientiane Capital, Luang Prabang, Xayaboury and Oudomxay improve in at most 20% of them; the two largest losses (Savannakhet, Vientiane Capital) persist under every perturbation of the stage-2 configuration.
grounds: analysis/06_stability/results/province_stability.csv
node: analysis/06_stability
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened
alternatives: a per-province or partially pooled stage 2, not built, is the natural alternative this pattern suggests
by: agent-autonomous

## C5
The correction helps at two and three months ahead in every combination run and at one month ahead in fewer than half (47%): the multi-step error is what a stage 2 trained on multi-step errors corrects.
grounds: analysis/06_stability/results/horizon_stability.csv
node: analysis/06_stability
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened
by: agent-autonomous

## C6
The only configurations in which the two-stage ensemble loses to stage 1 alone are the four candidates trained on stage 1's in-sample one-step residual (a_linearLags, b_gradientBoosting, c_bayesianRidge, d_linearClimate), a residual that is essentially white; the fifth such candidate, e_pooledRandomForest, wins on mean CRPS but with coverage collapsed to 64.4%.
grounds: analysis/06_stability/results/conclusions.csv · analysis/05_residualStructure/results/error_structure.json
node: analysis/06_stability
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened
by: agent-autonomous

## C7
Five reasonable alternatives were not run and the stability statement does not cover them: a log1p stage 1; a negative-binomial or zero-truncated predictive family at stage 1 (the one change that could repair the interval coverage deficit, which is a heavy tail of reporting-regime cells a Gaussian cannot carry); a multiplicative combination rule; an ENSO covariate; Chap-native evaluation.
grounds: analysis/06_stability/results/manifest.csv · analysis/05_residualStructure/results/error_structure.json
node: analysis/06_stability
scope: these are absences recorded with reasons, not findings
by: agent-autonomous

## C8
With h_levelOnlyBoosting as the main path, the sign of the central comparison is stable: in all 26 planned perturbations of the v2 development manifest (stage 1's specification, the training window, the backtest scheme, the modelability threshold and every constant of the main-path stage 2) the two-stage ensemble beats stage 1 alone on mean CRPS with 90% coverage not worse; the margin ranges from -1.06% to -10.41% (median -5.91%) against the main path's -6.53%, no perturbation flips it, and every row improves at least 4 of 8 splits.
grounds: analysis/06_stability/results/distribution_v2.json · analysis/06_stability/results/conclusions_v2.csv
node: analysis/06_stability
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened; the set is the frozen v2 development manifest (26 tier-2 rows), and five tier-3 alternatives were not run
alternatives: none of the run perturbations supports the opposite statement; the alternatives that could (a count or heavier-tailed predictive family at stage 1) were not run; the v1 set around g_oosErrorBoosting (C2) reached the same sign conclusion
by: agent-autonomous

## C9
Around h_levelOnlyBoosting the size of the margin depends on stage 1's specification and on what the correction is trained on, not on the stage-2 family's hyperparameters or seed: eight perturbations move it by more than two percentage points from the main path's -6.53% -- larger under the airline (-10.41%) or stationarity-enforced (-10.16%) stage 1; smaller under one model per horizon (-3.47%), a rolling 72-month window (-3.40%), adding the recent-residual and cross-province features back to the minimal input (-3.32%), a true rolling refit of the in-window errors (-2.99%), a 2002 window start (-1.06%) or a no-differencing stage 1 (-1.06%) -- while the five hyperparameter and seed perturbations stay within two points (-4.76% to -6.45%), as do winsorisation, the bound without floor, clipping, standardisation and warm-up.
grounds: analysis/06_stability/results/perturbation_effects_v2.csv · analysis/06_stability/results/distribution_v2.json
node: analysis/06_stability
scope: holds on the development backtest (1998-2009, 8 splits, 3-month horizon) only; the sealed 2010 holdout has not been opened
alternatives: the rolling-refit row is the honest version of the main path's fixed-parameter shortcut; a reader who weights it most should read the margin as about three percent
by: agent-autonomous

## C10
A no-differencing stage 1, SARIMAX(1,0,1)x(1,0,0,12), alone scores mean CRPS 24.93 on the development backtest -- better than the main path's stage 1 (26.05) and within 0.6 CRPS of the two-stage main path (24.35) -- and under it the residual correction is worth only -1.06%; part of the second stage's development margin is a repair of stage 1's differencing choice.
grounds: analysis/06_stability/results/stage1=nodiff_101x100@h/conclusion.json · analysis/06_stability/results/perturbation_effects_v2.csv · analysis/05_residualStructure/results/stage1_weaknesses.json
node: analysis/06_stability
scope: holds on the development backtest only; stage 1 is fixed as SARIMAX(1,1,1)x(1,0,0,12) by a human-set decision (plan section 4b, 2026-09-21) and is not repaired, so this is a documented weakness bearing on the central comparison, not a change of main path
alternatives: under g_oosErrorBoosting the same stage 1 left a margin of -3.36% (v1); a stage 1 chosen by a unit-root test or by development CRPS would be the alternative not taken
by: agent-autonomous

## C11
Changing the main path from g_oosErrorBoosting to h_levelOnlyBoosting moves the development margin from -3.41% to -6.53%, and 20 of the 22 perturbations shared by name between the v1 and v2 manifests move with it (median shift -2.3 points; the conservative rolling-refit reading from -0.70% to -2.99%); the two exceptions are stage-1 changes (airline -10.64% to -10.41%; no differencing -3.36% to -1.06%). Four v2 rows whose configuration is by construction identical to a v1 row reproduce its two-stage mean CRPS exactly.
grounds: analysis/06_stability/results/version_comparison_v2.csv · analysis/06_stability/results/distribution_v2.json
node: analysis/06_stability
scope: holds on the development backtest only; both versions are development-set measurements around main paths selected on the same cells
alternatives: Chap's default scheme moved the size in v1 and not in v2; the per-horizon fit, the rolling window and the no-differencing stage 1 move it in v2 and not in v1
by: agent-autonomous

## C12
Around h_levelOnlyBoosting the gain is concentrated: Khammouane, Salavan, Bokeo, Xiangkhouang and Xekong improve in every one of the 27 combinations run (main and 26 perturbations) and Champasak in 25, while Oudomxay never improves and Phongsaly, Luang Prabang and Vientiane Capital improve in at most 10%; Savannakhet improves in 4 of 27 (the airline stage 1, the rolling window, the bound without floor, the tighter winsorisation), and the Vientiane Capital and Luang Prabang losses turn around only under the airline stage 1 or, for Vientiane Capital, the full feature set with climate anomalies.
grounds: analysis/06_stability/results/province_stability_v2.csv
node: analysis/06_stability
scope: holds on the development backtest only; province names from analysis/01_data/02_characterise/results/province_summary.csv
alternatives: a per-province or partially pooled stage 2, not built, is the natural alternative this pattern suggests (as in C4)
by: agent-autonomous

## C13
Around h_levelOnlyBoosting the correction helps three months ahead in every one of the 27 combinations, two months ahead in 26, and one month ahead in 23 (85%, against 47% around g_oosErrorBoosting); the four combinations that lose at one month ahead are the per-horizon fit, the rolling 72-month window, the minimal input with recent-residual and cross-province features added back, and the no-differencing stage 1.
grounds: analysis/06_stability/results/horizon_stability_v2.csv · analysis/06_stability/results/horizon_stability.csv
node: analysis/06_stability
scope: holds on the development backtest (3-month horizon) only
by: agent-autonomous
