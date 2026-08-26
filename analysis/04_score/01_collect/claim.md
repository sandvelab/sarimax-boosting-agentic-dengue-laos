# Claim

What did each model score on every evaluable cell? One row per model, province, target month and lead time, with CRPS, absolute error, both interval indicators and the observed value beside them, taken from chap-core's own registered metrics.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

2 597 rows: 371 evaluable cells for each of seven model rows — two baselines, the
reference's four repeats, and the reference's per-cell mean. Each row carries CRPS, absolute
error, both interval indicators, the observed value, the split it belongs to and the number
of draws behind it. Every reported figure in the project is an aggregation of this one file.

All three models were scored on the identical 371 cells, which is what makes the paired
comparison at `03_compare` possible at all.
