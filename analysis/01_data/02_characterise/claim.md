# Claim

On the development file only: per-province series length, missingness and zero-rate, and which provinces are modelable at all.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

17 of 18 provinces are modelable (≥24 present months in development). **LA-VI (Vientiane)
has 0/144 development months present** and is excluded from modelling entirely. LA-XN
(Xaisomboun) is modelable in development (96/144 present) but stops reporting partway through
the development period. Whether it reports anything in the holdout is not examined here — see
the flagged note in the batch report on a boundary overstep during this batch's earlier,
informal data exploration, which looked at that and should not have. Full table:
`results/province_summary.csv`.
