# Claim

Does the archived source file partition exactly into a development period (1998-01 to 2009-12) and a held-out year (2010), and is each part well-formed? This is the only node in the project that reads the full file.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The partition is exact.** The archived file's 2 808 data rows go to 2 592 development
(1998-01 to 2009-12) and 216 holdout (2010), with no line in both, the sorted union
byte-identical to the sorted source, and each part an order-preserving subsequence of it.
The file is ordered by province and then by month, so the two parts do not concatenate back
into it; content and ordering are checked separately for that reason.
→ `results/partition_check.json`

**The source is a complete rectangular panel**: 18 provinces × 156 months, no missing
months, no duplicate primary keys. Every column is fully populated except `disease_cases`,
which is absent in 233 cells — 209 in development, 24 in the holdout.
→ `results/part_structure.csv`

**The schema's row count is a label error, not a stale figure.** `row_count: 2575` is the
number of rows carrying a non-missing `disease_cases`; the file has 2 808 rows. Both numbers
are right about different things, and the field counts complete records rather than rows.
→ `results/rowcount_reconciliation.json`

**No conversion is needed for `chap eval`.** The archived CSV is already in the form the
platform reads. chap-core's own loader takes both parts with every row, every province and
every missing target preserved, adding only a `parent` column.
→ `results/chap_ingest_check.json`

**The holdout is well-formed and sealed**: 216 rows, all 18 provinces, all 12 months of
2010, no duplicates, 24 cells without a dengue count. Where those 24 fall was not examined.
