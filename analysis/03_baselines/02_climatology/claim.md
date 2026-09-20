# Claim

Scored through the same native CRPS pipeline as stage 1: does a seasonal-climatology forecast (next month = mean of that calendar month in the training window) produce a well-formed, file-grounded CRPS score on the same cells?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

Yes: a seasonal-climatology forecast (mean of that calendar month's training-window values,
sigma the same calendar month's training-window standard deviation) scores **mean CRPS
26.91** over the same 371 cells stage 1 and persistence score, with no fit failures (0/408).
`results/conclusion.json`, `results/per_cell_scores.csv`.
