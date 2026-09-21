# Claim

Does a per-province SARIMAX model, backtested on the development data under this project's fixed scheme, produce a well-formed, file-grounded CRPS score?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

Yes: a per-province SARIMAX(1,1,1)×(1,0,0,12), fitted on raw `disease_cases` and refit at
every split, produces a well-formed backtest: **mean CRPS 26.05** over 371 scored cells (16
of 17 modelable provinces contribute a scored cell in the evaluated span; LA-XN stops
reporting before 2008 and contributes none — consistent with the prior project's independent
finding of 371 evaluable cells on the same scheme). No fit failed (0/136). This is stage 1
*alone*; whether stage 2's residual correction improves on it is the plan's actual question
(§2) and is not yet answered. `results/conclusion.json`, `results/per_cell_scores.csv`.

**Known weaknesses, documented and deliberately not repaired (batch 14; human-set, plan §4b
2026-09-21: stage 1 stays SARIMAX as specified).** The file-grounded list is
`analysis/05_residualStructure/results/stage1_weaknesses.json`; each entry carries its
evidence, its effect, whether a stage 2 can address it, and the stage-1 fork not taken.

1. **Coverage below nominal because the standardised error is heavy-tailed** (87.1 / 82.1 /
   79.0% by horizon against 90%; median |z| 0.3, 1% of cells beyond |z| 23). Scaling sigma to
   reach nominal coverage raises mean CRPS from 26.05 to 35.65. A Gaussian on counts cannot
   carry this tail; no stage 2 that adds to the mean can change it.
2. **Negative forecast means** in 4.0% of cells, concentrated in Savannakhet after its 2008
   collapse; clipping alone is worth −0.56% CRPS. Every stage-2 candidate from batch 10 clips.
3. **The standard error does not grow with the level** (Spearman 0.65 between |z| and the
   forecast level): a province whose level collapsed keeps an se tens of times its current
   level (Savannakhet se 200–414, mean actual 8), one whose level rose has an se far too small.
   A standardised correction inherits this; `i_boundedBoosting` limits the damage.
4. **Systematic multi-step bias**: over-prediction in two thirds of cells, more at high
   forecast levels and in November–April; under-prediction in the June–July onset. This is the
   structure the batch-10 stage-2 candidates learn, and why they earn their place at 2–3
   months ahead.
5. **Reporting-regime breaks in 2008–09** (Savannakhet 166 → 8 cases a month; Bokeo 0.7 → 39;
   Salavan 4 → 61), consistent with Laos's 2008 move to electronic reporting. No province's own
   history predicts them; they are the coverage deficit and much of the CRPS.
6. **The specification is a first default, not a selected one.** It beats both baselines; its
   own score moves from 23.99 to 29.15 under the alternative orders and windows the stability
   node ran, and the stage-2 margin survives every one of them.
