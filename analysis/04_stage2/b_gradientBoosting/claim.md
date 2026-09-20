# Claim

Does a gradient-boosted tree trained on stage 1's lag-12 in-sample residual and calendar month
(the same inputs as `a_linearLags`, to isolate the model-family comparison), added additively
to stage 1's forecast, improve mean CRPS over stage 1 alone on the development backtest?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

No: a gradient-boosted regression tree on stage 1's lag-12 in-sample residual and cyclical
calendar month, added to stage 1's forecast mean, scores **mean CRPS 27.68** over the
identical 371 cells stage 1 alone scores — **6.25% worse** than stage 1's 26.05, and worse
than `a_linearLags`'s 26.26 as well. Interval coverage (nominal 90%) does not improve either:
82.7% for stage 1 alone vs. 82.2% for this candidate — essentially unchanged, not
overconfident, but not better calibrated. 40 of 408 cells (9.8%) abstained under the same
`MIN_TRAIN_ROWS` threshold as `a_linearLags`, recorded per-cell. `results/conclusion.json`,
`results/comparison.json`.

Given the same minimal input as `a_linearLags` (isolating the family comparison), more model
capacity made the correction worse, not better — consistent with a genuinely small, noisy
residual signal at this input specification rather than a linear-vs-nonlinear structure the
tree could exploit and the linear model could not. This is a second negative result, not a
settled answer to whether stage 2 earns its place at all: a richer input set or a
non-tree, non-linear family (Bayesian/linear-with-structure, batches 6-7) may yet find signal
this candidate's minimal inputs did not expose.
