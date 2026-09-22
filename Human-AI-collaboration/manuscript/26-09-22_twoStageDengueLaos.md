Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1

# Does a residual-correction stage earn its place? A two-stage SARIMAX ensemble for monthly dengue forecasting in Laos

## Summary

We develop a two-stage forecasting ensemble for monthly dengue case counts across the
provinces of Laos — a per-province SARIMAX (stage 1) whose forecast errors are predicted and
corrected by a second model (stage 2) — and ask whether the second stage earns its place. It
does: on a sealed held-out year, opened once across a perturbation set frozen beforehand, the
ensemble lowers mean CRPS by 22.8% against stage 1 alone with improved interval coverage, and
the sign of that improvement survives all 26 pre-registered perturbations. The same run shows
that the model it improves is the wrong model for that year: a seasonal climatology baseline
beats the two-stage ensemble by 22%, and no configuration in the frozen set is adequately
calibrated. Both results are reported, because a correction that reliably improves a poor
forecast is a real finding and a weak one.

## 1. Data and design

Monthly reported dengue cases for 18 Lao provinces, 1998-01 to 2010-12. Development uses
1998-01 to 2009-12 only; **2010 was sealed before any work began and opened once**, at the end,
across a manifest frozen in advance. Seventeen provinces meet the modelability threshold on
development data and that set is fixed from development months alone, so the evaluated cells
cannot shift when the year opens.

Stage 1 is a per-province SARIMAX(1,1,1)×(1,0,0,12) on raw counts, refit each split. Stage 2
never sees the target: it is trained on stage 1's *h*-step out-of-sample error, computed inside
each split's own training window, pooled across provinces on the standardised-error scale, and
its prediction is added back to stage 1's mean. Scoring is mean CRPS with 90% interval coverage
beside it, from a CRPS implementation verified against a reference before use. Development:
8 rolling-origin splits, 3-month horizon, 371 scored cells. Held out: 4 splits covering 2010
exactly once at the same horizon, 192 scored cells.

Every judgment call — stage 1's order, stage 2's family and inputs, the combination rule, the
training window, the zero-handling threshold — is either an alternatives node in the analysis
tree or a logged decision. The stability set perturbs each of them and reports the distribution
of conclusions rather than the best one.

## 2. Development results

Ten stage-2 candidates were built. The first five, trained on stage 1's **in-sample one-step
residual**, all fail: four lose to stage 1 alone, and the fifth wins on CRPS with coverage
collapsed to 64.4%. Diagnostics explain why — that residual is essentially white, while the
multi-step out-of-sample error a stage 2 must actually correct carries a level-dependent
over-prediction, a calendar bias and a horizon effect. Candidates trained on *that* quantity
succeed, and the best of them uses the most minimal input tried: horizon, target month, and the
forecast level relative to the province's own residual scale.

| Development backtest (371 cells) | Mean CRPS | 90% coverage |
|---|---|---|
| Persistence | 28.32 | — |
| Seasonal climatology | 26.91 | — |
| Stage 1 alone (SARIMAX) | 26.05 | 82.7% |
| **Two-stage ensemble** | **24.35** | **85.2%** |
| Margin vs. stage 1 | **−6.53%** | +2.5 pts |

Across 26 perturbations of stage 1's specification, the training window, the backtest scheme
and every constant of stage 2, the ensemble beats stage 1 alone with coverage not worse in all
26 (−1.06% to −10.41%, median −5.91%); **no perturbation flips the sign**. The *size* turns on
stage 1 and on how the training errors are constructed — larger under a weaker stage 1, smaller
under a true rolling refit of those errors (−2.99%) — and is insensitive to the stage-2 family's
hyperparameters and seed (all within two points). One result qualifies the development margin
directly: a no-differencing stage 1 scores 24.93 alone, within 0.6 CRPS of the two-stage
ensemble, so part of the gain is a repair of stage 1's differencing choice.

## 3. Held-out results

The configuration evaluated on 2010 was pre-registered before the year opened, by a rule written
down before its result was seen. The set ran once, in full; nothing was added, dropped, re-tuned
or promoted afterwards.

| Held-out year 2010 (192 cells) | Mean CRPS | 90% coverage |
|---|---|---|
| Stage 1 alone (SARIMAX) | 128.51 | 57.3% |
| Persistence | 127.58 | 56.2% |
| **Two-stage ensemble** | **99.20** | **61.5%** |
| Seasonal climatology | **77.29** | 54.7% |
| Ensemble margin vs. stage 1 | **−22.81%** | +4.2 pts |

**The second stage earns its place.** It improves all 4 splits, 75% of cells and every horizon,
and the sign holds in all 26 frozen perturbations (−29.25% to −4.18%, median −20.89%). The
margin is 16.3 points *larger* than on development, and 29 of 31 rows paired by name across the
two datasets gain more on the held-out year.

**And the two-stage model is beaten there by a naive seasonal mean**, reversing the development
ranking, while every model's 90% interval covers barely half its outcomes. 2010 is an epidemic
year unlike the development span — 22,903 cases in twelve months against 12,291 in twenty-four,
peaking at 5,649 in September against a prior maximum of 1,410. A SARIMAX on raw counts with a
Gaussian predictive interval does not follow that; the correction recovers much of the level
error, and a model with no trend at all does better than either.

## 4. What the conclusion turns on

The held-out result depends sharply on what stage 2 is allowed to see. The two level-only
configurations gain about 23%; every configuration carrying recent-residual and cross-province
features gains 4% or less. On development that gap was about 3 percentage points; on the
held-out year it is about 19. Had the earlier, richer-input candidate remained the reported
configuration — as it was until the pre-registration — the held-out margin would have been
−2.25% rather than −22.81%. The minimal input generalised; the richer ones did not.

## 5. Implications

**A residual-correction stage can add real, reproducible value — and mostly by fixing level
error.** The correction that worked is trained on multi-step out-of-sample error, not in-sample
residuals, and reads almost nothing: horizon, month, forecast level. Hybrid designs that train
on the wrong residual, or that give the second stage rich province-specific features, did worse
here and generalised worse.

**A large relative improvement over a weak base model is not evidence of a good forecaster.**
The ensemble's best result, −22.8% on held-out data, was obtained on the year in which its base
model was most badly wrong, and it still lost to a naive seasonal baseline. Ablation
against one's own first stage is necessary and nowhere near sufficient; the naive baselines are
what caught this.

**Calibration failed where it mattered most.** Coverage was acceptable on ordinary years and
collapsed on the epidemic year, for every model tried. The single change our diagnostics
identified as capable of repairing it — a count or heavier-tailed predictive family at stage 1
in place of the Gaussian — was deliberately not built, and remains the most consequential gap.

**Development performance understated, not overstated, the held-out margin.** The usual worry
about selection on development data did not materialise here; the year's character mattered far
more than any optimism from repeated model selection on the same cells.

## 6. Limitations

One held-out year of roughly 200 province-months supports a direction, not a precise effect
size, and that year is atypical. One province reports no cases for any month of 2010 and is
therefore unscored, leaving 16 provinces. Stage 1 was fixed by decision and not repaired, so
five reasonable alternatives — a log1p transform, a count or heavier-tailed predictive family, a
multiplicative combination rule, an ENSO covariate, and an alternative evaluation harness — were
not run, each recorded with its reason. Three perturbations beat the reported configuration on
held-out data and none was promoted, so the reported margin is a pre-registered measurement
rather than the best available number.

## 7. Reproducibility

The analysis is a tree of claims under `analysis/`, reproduced end to end by `analysis/run.sh`
at a pinned environment; paths not taken remain in the tree and are executed by the stability
node. Every reported figure is read from a stored result by a script, each result carries a
provenance record binding it to script, inputs, environment, seed and commit, and every sentence
above traces to an entry in the claim collection through the sidecar beside this file. The
held-out manifest, its sha256 and the commit it was frozen at are recorded before the year was
opened, and the opening itself is recorded, so a second opening would be visible.
