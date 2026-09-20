# Claim

Does a Bayesian linear regression (sklearn BayesianRidge) on stage 1's lag-12 in-sample residual and calendar month, added additively to stage 1's forecast with its own posterior predictive variance combined into the final interval, improve mean CRPS over stage 1 alone on the development backtest?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

No — worse than either prior candidate. A Bayesian ridge regression on stage 1's lag-12
in-sample residual and cyclical calendar month, added additively to stage 1's forecast with
its own posterior predictive variance folded into the final interval, scores **mean CRPS
28.07** over the identical 371 cells stage 1 alone scores — **7.73% worse** than stage 1's
26.05, worse than `a_linearLags` (26.26, -0.78%) and worse than `b_gradientBoosting` (27.68,
-6.25%). Interval coverage (nominal 90%) is the best of the three candidates — 86.8% vs.
stage 1 alone's 82.7%, `a_linearLags`'s 83.3%, `b_gradientBoosting`'s 82.2% — because
combining stage 2's own posterior variance with stage 1's widens the interval; but the wider,
better-calibrated interval comes at a CRPS cost that dominates any gain from the mean
correction. 40 of 408 cells (9.8%) had stage 2 abstain, same threshold and same rate as both
siblings. `results/conclusion.json`, `results/comparison.json`,
`results/all_candidates_comparison.json` (all three stage-2 candidates side by side).

Three stage-2 candidates have now been built (a linear point-estimator, a tree-based
point-estimator, and this Bayesian one) and all three lose to stage 1 alone on the identical
minimal input. `results/all_candidates_comparison.json`'s `any_candidate_earns_its_place` is
`false`. This does not itself decide whether *any* stage-2 family could earn its place with a
richer input set (more lags, covariates, population) — that is explicitly batch 7's question,
along with the formal main-path decision among the three.
