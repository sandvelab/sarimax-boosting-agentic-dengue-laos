# Claim

Does adding lag-12 climate covariates (rainfall, mean temperature, mean relative humidity) to the a_linearLags stage-2 input improve mean CRPS over stage 1 alone, and over a_linearLags itself, on the development backtest?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

No, on both counts. Adding lag-12 rainfall, mean temperature and mean relative humidity to
`a_linearLags`'s exact OLS family (same lag-12 residual + calendar-month input, plus the three
climate columns, same additive-correction-to-the-mean contract) scores **mean CRPS 26.85**
over the same 371 cells: **worse than stage 1 alone** (26.05, +3.05%) and **worse than
`a_linearLags` on the minimal input** (26.26, +2.25%). Coverage is essentially unchanged from
`a_linearLags` (83.0% vs. 83.3% empirical, nominal 90%) — climate does not buy calibration
either. 40 of 408 cells abstained, the same count as `a_linearLags`, for the same reasons
(insufficient training rows or an unavailable lag-12 value — here, either the residual or one
of the three climate columns). `results/conclusion.json`, `results/comparison.json`,
`results/all_candidates_comparison.json`.

This does not settle whether climate covariates could help stage 2 under a different
treatment — only that the specific, leakage-safe lag-12 proxy tried here does not, on the
family it was tried with. Two things this candidate's design deliberately leaves open,
logged rather than silently closed: **contemporaneous or forecast climate** (this dataset has
no genuine forward climate signal to try; using the test month's own observed value would be
leakage for a real deployment, argued in the provenance record) and **a non-linear family**
given the same climate input (tree-based or Bayesian, as `b_gradientBoosting` and
`c_bayesianRidge` tried on the minimal input but not on this one — confounding family and
input together was avoided here on purpose, so a future candidate crossing the two remains a
clean, single-variable addition to the tree rather than a repeat of this one).
