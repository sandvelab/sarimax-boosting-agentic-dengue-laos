# Claim

Scored through the same native CRPS pipeline as stage 1: does a persistence forecast (next month = last observed) produce a well-formed, file-grounded CRPS score on the same cells?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

Yes: a persistence forecast (last observed value, held flat across each split's test window,
with sigma taken as the training window's own one-step-difference standard deviation) scores
**mean CRPS 28.32** over the same 371 cells stage 1 scores, with no fit failures (0/408).
`results/conclusion.json`, `results/per_cell_scores.csv`.
