# Claim

How is the Laos dengue dataset partitioned into development and sealed holdout, and characterised (per-province coverage, missingness, modelability) for this project's own backtest scheme?

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

The archived Laos file (18 provinces × 156 months, 1998-01 to 2010-12) partitions cleanly
into a 2,592-row development file (1998-01 to 2009-12) and a 216-row, complete holdout file
(2010), sealed per plan §3. Of the 18 provinces, 17 are modelable on development data; LA-VI
(Vientiane) reports nothing at all and is excluded. The fixed backtest scheme (plan §4b)
resolves to 8 expanding-window splits over the development file, evaluated span 2008-01 to
2009-12. See `01_prepare/claim.md`, `02_characterise/claim.md` and
`03_backtest_scheme/claim.md` for the grounding results.
