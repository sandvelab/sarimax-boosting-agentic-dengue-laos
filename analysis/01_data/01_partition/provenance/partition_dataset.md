# Provenance — the partition of the archived dataset

```
result:              results/development_1998-01_2009-12.csv
                     results/holdout_2010_SEALED.csv
                     results/partition_check.json
                     results/part_structure.csv
                     results/rowcount_reconciliation.json
                     results/partition_outputs.sha256
script:              scripts/partition_dataset.py
                     sha256:84a9dd25a703dc4d7e0a6ba808a064b47a3142558a845a1f7138e77138f69566
invocation:          "$PYTHON" scripts/partition_dataset.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              Archive/lao-dataset/chap_LAO_admin1_monthly.csv
                     sha256:19488aa1fc4d961ae1a6aeb75b874789576877664fce47713628f497a06fff56
                     Archive/lao-dataset/chap_LAO_admin1_monthly_schema.json
                     sha256:ff750db4202c32fc187b26bb3566b4f981b94467664502e76cbd09977dd06210
                     Archive/lao-dataset/sha256sums.txt (re-verified at run time)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The partition is a deterministic filter on time_period and the
                     structural summaries are counts; project seed 20260822 has no surface.
commit:              1ae2649
instructions-commit: 15b4ba9 (AGENTS.md, CLAUDE.md, .claude/); the tree machinery
                     AI-internal/useful-scripts/node.py was at 1ae2649, which changed how
                     every node's run.sh is generated and is recorded as methodological
node:                analysis/01_data/01_partition
produced:            2026-08-23
```

**What it establishes.** The source partitions exactly: 2 808 data rows to 2 592 development
and 216 holdout, no line in both, the sorted union byte-identical to the sorted source, and
each part an order-preserving subsequence of it. The source is a complete rectangular panel
of 18 provinces × 156 months with no duplicate primary keys and no missing months. The
schema's `row_count: 2575` counts rows with a non-missing `disease_cases`, not rows in the
file — 233 rows carry a missing target, 209 of them in the development period.

**Why the exactness check is not a concatenation.** The file is ordered by province and then
by month, so a cut on time is not a prefix and a suffix; concatenating the two parts does not
rebuild the file even when nothing has been lost. Content equality and within-part ordering
are therefore checked separately, and the reported hash is of the sorted lines.

**What was deliberately not done to the holdout.** Its case values were not read, summarised
or plotted. Row count, provinces present, months present and the *number* of missing target
cells are recorded, which is the completeness check the plan's §3 permits; **where** those 24
missing cells fall was not examined, though phase E will need it to know what the final
validation can measure.

alternatives-considered: the partition could have been done with pandas and written back
through a CSV writer, which is shorter. It was done on the text lines because a parser
round trip re-formats floats, and "the two parts contain exactly the source" would then be a
claim about a formatter rather than about the file. The holdout could also have been left
unwritten and recreated in phase E by filtering the archived original — that would remove one
file that has to stay sealed, but it would also mean the partition was never verified, and
the verification is the point. A third option was to place the holdout outside `analysis/`
entirely; it is here because it is an output of a node like any other, and its filename
carries the seal instead.

agency: agent-autonomous. The split point, the sealing rule and the requirement to verify
the partition are the plan's (`human-set`, §3); how to verify it is the agent's.
information: human-pointed — the dataset, its repository and the row-count discrepancy come
from `Archive/case-source-material/chapOrientation.md` §4.
