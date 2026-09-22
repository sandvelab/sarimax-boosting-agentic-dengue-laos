# Provenance sidecar — `26-09-22_twoStageDengueLaos.md`

Each statement in the draft, mapped to the claim it rests on (`../claims/claims.md`) or, where
it describes the method rather than a result, to the stored file that fixes it. Keyed by section
and by the opening words of the sentence, so the mapping survives reformatting.

**Method statements are marked `method:`.** They are design facts read from a result file, not
findings; `/claims check-text` flags them because no claim asserts them, which is correct.

## Summary

| Statement | Rests on |
|---|---|
| "We develop a two-stage forecasting ensemble…" | method: `analysis/claim.md`; plan §1 |
| "on a sealed held-out year, opened once… lowers mean CRPS by 22.8%… with improved interval coverage" | **C14** |
| "the sign of that improvement survives all 26 pre-registered perturbations" | **C16** |
| "a seasonal climatology baseline beats the two-stage ensemble by 22%" | **C17** |
| "no configuration in the frozen set is adequately calibrated" | **C18** |
| "Both results are reported, because a correction that reliably improves a poor forecast is a real finding and a weak one" | interpretation; the two results are **C14** and **C17**. Plan §2 requires a badly-calibrated or baseline-beaten winner to be reported as not having won |

## 1. Data and design

| Statement | Rests on |
|---|---|
| "Monthly reported dengue cases for 18 Lao provinces, 1998-01 to 2010-12" | method: `analysis/01_data/01_prepare/results/partition_summary.json` |
| "2010 was sealed before any work began and opened once… across a manifest frozen in advance" | method: `analysis/06_stability/results/holdout_freeze.json` · `results/run_status_holdout.csv`; plan §3 |
| "Seventeen provinces meet the modelability threshold… fixed from development months alone" | method: `analysis/01_data/02_characterise/results/modelability_summary.json` · `analysis/06_stability/results/holdout_runner_verification.json` |
| "Stage 1 is a per-province SARIMAX(1,1,1)×(1,0,0,12) on raw counts, refit each split" | method: `analysis/02_stage1/claim.md` · `results/conclusion.json` |
| "Stage 2 never sees the target: it is trained on stage 1's *h*-step out-of-sample error…" | method: `analysis/04_stage2/h_levelOnlyBoosting/claim.md`; described as a finding in **C1** |
| "from a CRPS implementation verified against a reference before use" | method: `analysis/00_metric/claim.md` |
| "Development: 8 rolling-origin splits, 3-month horizon, 371 scored cells" | method: `analysis/01_data/03_backtest_scheme/results/schedule_summary.json` |
| "Held out: 4 splits covering 2010 exactly once… 192 scored cells" | method: `analysis/06_stability/results/holdout_runner_verification.json` · **C14** (the cell count) |
| "Every judgment call… is either an alternatives node… or a logged decision" | method: `analysis/06_stability/results/manifest.csv`; plan §3 |
| "The stability set perturbs each of them and reports the distribution of conclusions rather than the best one" | method: `analysis/06_stability/claim.md` · `results/distribution_v2.json` · `results/distribution_holdout.json`; AGENTS.md §4 |

## 2. Development results

| Statement | Rests on |
|---|---|
| "The first five, trained on stage 1's in-sample one-step residual, all fail… coverage collapsed to 64.4%" | **C6** |
| "that residual is essentially white, while the multi-step out-of-sample error… carries a level-dependent over-prediction, a calendar bias and a horizon effect" | **C6**, **C7** (grounds: `05_residualStructure/results/error_structure.json`) |
| "the best of them uses the most minimal input tried: horizon, target month, and the forecast level…" | **C20**; method: `analysis/04_stage2/h_levelOnlyBoosting/claim.md` |
| Table row: persistence 28.32, seasonal climatology 26.91, stage 1 26.05 | **C17** (which states the development ranking); `analysis/03_baselines/results/comparison.json` |
| Table rows: stage 1 26.05 / 82.7%, two-stage 24.35 / 85.2%, −6.53% | **C8** (margin, coverage-not-worse), **C10** (24.35), **C18** (82.7% and 85.2%) |
| "in all 26 (−1.06% to −10.41%, median −5.91%); no perturbation flips the sign" | **C8** |
| "The size turns on stage 1 and on how the training errors are constructed… smaller under a true rolling refit (−2.99%)… within two points" | **C9** |
| "a no-differencing stage 1 scores 24.93 alone, within 0.6 CRPS of the two-stage ensemble" | **C10** |

## 3. Held-out results

| Statement | Rests on |
|---|---|
| "pre-registered before the year opened, by a rule written down before its result was seen" | method: plan §4b (2026-09-21, human-set) · `analysis/04_stage2/claim.md` |
| "The set ran once, in full; nothing was added, dropped, re-tuned or promoted afterwards" | method: `analysis/06_stability/results/run_summary_holdout.json` · `run_status_holdout.csv`; plan §4b (2026-09-22) |
| Table rows: stage 1 128.51 / 57.3%, two-stage 99.20 / 61.5%, −22.81% | **C14**, **C18** |
| Table rows: persistence 127.58 / 56.2%, climatology 77.29 / 54.7% | **C17**, **C18** |
| "It improves all 4 splits, 75% of cells and every horizon" | **C14** |
| "the sign holds in all 26 frozen perturbations (−29.25% to −4.18%, median −20.89%)" | **C16** |
| "16.3 points larger than on development, and 29 of 31 rows paired by name… gain more" | **C15** |
| "beaten there by a naive seasonal mean, reversing the development ranking" | **C17** |
| "every model's 90% interval covers barely half its outcomes" | **C18** |
| "22,903 cases in twelve months against 12,291 in twenty-four, peaking at 5,649… against a prior maximum of 1,410" | **C19** |

## 4. What the conclusion turns on

| Statement | Rests on |
|---|---|
| "The two level-only configurations gain about 23%; every configuration carrying recent-residual and cross-province features gains 4% or less" | **C20** |
| "On development that gap was about 3 percentage points; on the held-out year it is about 19" | **C20** |
| "the held-out margin would have been −2.25% rather than −22.81%" | **C20**, **C14** |

## 5. Implications

Interpretive paragraphs. Each conclusion is drawn from the claims named; the inference is the
authors', the numbers are not.

| Statement | Rests on |
|---|---|
| "The correction that worked is trained on multi-step out-of-sample error, not in-sample residuals, and reads almost nothing" | **C6**, **C20** |
| "Hybrid designs that train on the wrong residual, or that give the second stage rich province-specific features, did worse here and generalised worse" | **C6**, **C20** |
| "The ensemble's best result… was obtained on the year in which its base model was most badly wrong, and it still lost to a naive seasonal baseline" | **C14**, **C17**, **C19** |
| "Ablation against one's own first stage is necessary and nowhere near sufficient" | inference from **C14** + **C17** |
| "Coverage was acceptable on ordinary years and collapsed on the epidemic year, for every model tried" | **C18** |
| "The single change our diagnostics identified as capable of repairing it… was deliberately not built" | **C7**; plan §4b (2026-09-21, human-set) |
| "Development performance understated, not overstated, the held-out margin" | **C15** |

## 6. Limitations

| Statement | Rests on |
|---|---|
| "One held-out year of roughly 200 province-months… and that year is atypical" | **C14** (cell count), **C19**; plan §2 |
| "One province reports no cases for any month of 2010 and is therefore unscored, leaving 16 provinces" | method: `analysis/06_stability/results/holdout_year_context.json` (`note_on_cells`) |
| "five reasonable alternatives… were not run, each recorded with its reason" | **C7**; `analysis/06_stability/results/manifest_holdout.csv` |
| "Three perturbations beat the reported configuration on held-out data and none was promoted" | `analysis/06_stability/results/perturbation_effects_holdout.csv`; plan §4b (2026-09-22) |

## 7. Reproducibility

All method statements: `AGENTS.md` §2–§3, `analysis/run.sh`, the per-node `provenance/`
records, `analysis/06_stability/results/holdout_freeze.json` and `run_status_holdout.csv`.
