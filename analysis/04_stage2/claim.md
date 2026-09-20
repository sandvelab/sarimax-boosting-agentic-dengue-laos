# Claim

Which stage-2 model family, trained to predict stage 1's residuals and added back as a correction, earns its place against stage 1 alone on the development backtest?

## Children

kind: alternatives
main-path: a_linearLags

## Environment

inherits: the project main environment (`environment/`)

## Answers

Not yet settled — two candidates so far, both negative. `a_linearLags` (linear on lag-12
residual + calendar month) does not beat stage 1 alone: mean CRPS 26.26 vs. 26.05, 0.78%
worse. `b_gradientBoosting` (regularised gradient-boosted trees, same inputs) is worse still:
mean CRPS 27.68, 6.25% worse than stage 1 alone. `a_linearLags` remains the (still-losing)
main path by default — it is the less-bad of the two, not a candidate that earns its place.
This does not close the question the plan asks (§1: is there *a* stage-2 family that earns its
place) — batch 6 adds a non-tree, non-linear candidate (Bayesian or linear-with-structure) as
a further alternative, and batch 7 revisits the main-path designation and what stage 2 is
allowed to see once all three exist.
