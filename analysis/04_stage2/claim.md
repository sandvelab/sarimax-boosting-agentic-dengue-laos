# Claim

Which stage-2 model family, trained to predict stage 1's residuals and added back as a correction, earns its place against stage 1 alone on the development backtest?

## Children

kind: alternatives
main-path: a_linearLags

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
