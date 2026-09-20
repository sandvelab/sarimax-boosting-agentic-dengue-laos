# Claim

Is the project's own closed-form Gaussian CRPS implementation correct? Verify against an independent library implementation and against Monte-Carlo convergence, since every reported score in this project depends on it (plan §4, Rule 1).

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

The project's closed-form Gaussian CRPS matches `properscoring.crps_gaussian` to within
1.11e-16 over a 45-case grid, and matches `properscoring.crps_ensemble`'s Monte-Carlo estimate
(a general empirical estimator, not tied to the Gaussian formula) within relative tolerance at
three sample sizes. It is trusted for scoring from here on. `results/verification.json`.
