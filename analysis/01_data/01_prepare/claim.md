# Claim

Partition the archived Laos dataset into the development file (1998-01 to 2009-12) and the sealed holdout file (2010), verifying the archived checksums first, and confirm the holdout's completeness (row counts, provinces present, months present) without reading its case values.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

The archived source checksum verifies. The file is a complete 18×156 grid (1998-01 to
2010-12); the partition yields 2,592 development rows (1998-01 to 2009-12) and 216 holdout
rows (2010, all 12 months, all 18 provinces present — `results/holdout_completeness.json`).
No holdout case value was read to produce this answer.
