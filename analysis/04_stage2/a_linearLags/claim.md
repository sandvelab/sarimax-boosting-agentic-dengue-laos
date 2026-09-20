# Claim

Does a linear regression on stage 1's lag-12 in-sample residual and calendar month, added additively to stage 1's forecast, improve mean CRPS over stage 1 alone on the development backtest?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

No: added to stage 1's forecast mean, a linear regression on stage 1's lag-12 in-sample
residual and cyclical calendar month scores **mean CRPS 26.26** over the identical 371 cells
stage 1 alone scores — **0.78% worse** than stage 1's 26.05, not better. Interval coverage
(nominal 90%) is essentially unchanged: 82.7% for stage 1 alone vs. 83.3% for the two-stage
ensemble — both already under-covering the nominal level regardless of stage 2, a property of
stage 1's raw-scale Gaussian CRPS on zero-heavy series (02_stage1's own known weakness), not
something this candidate introduces or fixes. 40 of 408 cells (9.8%) had stage 2 abstain
(correction = 0) for lack of a usable lag-12 residual or too few valid training rows, recorded
per-cell rather than absorbed into the score. `results/conclusion.json`,
`results/comparison.json`.

This is one candidate, not the answer to whether stage 2 earns its place at all — a linear
correction on a minimal residual-lag input failing does not rule out a family with more
capacity (tree-based) or a different structural assumption (Bayesian/linear-with-structure),
which batches 5–7 add as siblings.
