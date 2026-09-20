# Claim

Does a per-province SARIMAX model, backtested on the development data under this project's fixed scheme, produce a well-formed, file-grounded CRPS score?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

Yes: a per-province SARIMAX(1,1,1)×(1,0,0,12), fitted on raw `disease_cases` and refit at
every split, produces a well-formed backtest: **mean CRPS 26.05** over 371 scored cells (16
of 17 modelable provinces contribute a scored cell in the evaluated span; LA-XN stops
reporting before 2008 and contributes none — consistent with the prior project's independent
finding of 371 evaluable cells on the same scheme). No fit failed (0/136). This is stage 1
*alone*; whether stage 2's residual correction improves on it is the plan's actual question
(§2) and is not yet answered. `results/conclusion.json`, `results/per_cell_scores.csv`.
