# Provenance — the Chap ingest check

```
result:              results/chap_ingest_check.json
script:              scripts/verify_chap_ingest.py
                     sha256:6238c3bfe03d445b24fe4b845b4064703c303c2d28bd57f80d1adfb9acaf89e7
invocation:          "$PYTHON" scripts/verify_chap_ingest.py
                     (from the node directory, via run.sh)
inputs:              results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     results/holdout_2010_SEALED.csv
                     sha256:e6d576431023b877432ca55e0dc93daeb020fac0fd4aaf71867bbc9f0849f073
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The check is a cell-by-cell equality test; project seed 20260822
                     has no surface.
commit:              1ae2649
instructions-commit: 15b4ba9
node:                analysis/01_data/01_partition
produced:            2026-08-23
```

**What it establishes.** There is no conversion step. `chap eval` reads the CSV directly, and
the archived file already carries `time_period`, `location`, `disease_cases` and the covariate
columns it expects. Both parts load through chap-core's own `DataSet.from_csv` with every row,
every province and every one of the missing target values preserved; the loader adds a
`parent` column and drops nothing. The plan's request for a lossless conversion is answered by
showing that the only transformation in the chain is the partition itself, which the sibling
record verifies.

**Why this matters more than it looks.** A format conversion is where a silent coercion would
live — a missing target becoming a zero would change every count in this project and would not
show up as an error anywhere. The check exists to make that failure visible rather than to
confirm a step that was expected to be trivial.

alternatives-considered: the round trip could have been demonstrated by running `chap eval`
itself, which exercises the loader in situ. That is batch 6's job and needs a model; doing it
here would have made a data check wait on a modelling artefact. Comparing on a written-out
CSV rather than in memory was also possible and was rejected as adding a second formatter to
the comparison.

agency: agent-autonomous.
