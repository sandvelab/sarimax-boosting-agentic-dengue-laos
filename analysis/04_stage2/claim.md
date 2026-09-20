# Claim

Which stage-2 model family, trained to predict stage 1's residuals and added back as a correction, earns its place against stage 1 alone on the development backtest?

## Children

kind: alternatives
main-path: a_linearLags

## Environment

inherits: the project main environment (`environment/`)

## Answers

Not yet settled — one candidate so far. `a_linearLags` (main path by default, being the only
child) does not beat stage 1 alone: mean CRPS 26.26 vs. 26.05, 0.78% worse
(`a_linearLags/claim.md`). This does not close the question the plan asks (§1: is there *a*
stage-2 family that earns its place) — batches 5–7 add a tree-based candidate and a
Bayesian/linear-with-structure candidate as further alternatives, and the main-path
designation is revisited once they exist.
