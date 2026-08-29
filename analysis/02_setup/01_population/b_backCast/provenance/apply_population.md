# Provenance — the population column, back-cast to a per-year series

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
                     results/$COMBO/population_series.csv
script:              scripts/apply_population.py
                     sha256:5ceba1b88fc757d5ddaecf58bf2544524be76e6f9b267cf7e8e0f87c567c7143
invocation:          "$PYTHON" scripts/apply_population.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=popColumn_backCast, which is the only combination that takes
                     this child.)
inputs:              analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     Archive/lao-population/worldbank_SP.POP.TOTL_LAO_1990-2021.json
                     sha256:b86c1fa0da08ce671c42ff0353f53432e5fb447b0f001333b77894046cbe85b1
                     Archive/lao-dataset/chap_LAO_admin1_monthly_schema.json
                     sha256:ff750db4202c32fc187b26bb3566b4f981b94467664502e76cbd09977dd06210
                     (read for one field: the snapshot's reference year)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The transformation is a deterministic multiplication of one
                     column by a table of ratios; project seed 20260822 has no surface here.
commit:              40b6936
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/01_population/b_backCast
produced:            2026-08-29
```

**What it establishes.** The archived population column is a single figure per province held
constant for thirteen years. This child replaces it with `snapshot × N(year)/N(2020)`, where
`N` is the World Bank's annual national total for Lao PDR. The scale runs from 0.7144 in 1998
to 0.8496 in 2009 (`results/$COMBO/setup_spec.json`), so the denominator a model divides by
now grows across the record instead of standing still.

**And it establishes something about the archive that nothing had checked.** The snapshot
sums to **4 961 076** across the eighteen provinces. The national total at the schema's
declared reference year, 2020, is **7 346 533**; the year whose national total is nearest the
snapshot's is **1995**. Either the column is not a 2020 level, or it is a WorldPop total that
does not reconcile with the UN's — the file cannot say which. Both figures and the nearest
year are computed by this script and written into the specification. This is the third
statement in that schema found not to describe the file; the row count and the rainfall unit
were the first two, and both are recorded in `Archive/lao-dataset/provenance.md`.

**Why the anchor is used anyway.** Changing the reference year multiplies every population in
the file by one constant. For any model that takes population as a log offset that constant
is absorbed by the intercept, so what survives the choice is the *shape* of the trend, which
is the thing this fork exists to perturb. The stage takes the schema at its word and records
the discrepancy rather than silently correcting a level it cannot verify.

alternatives-considered: **a provincial series** rather than a national one — rejected because
the only provincial measurements of Lao population in this period are the 1995, 2005 and 2015
censuses, which have no machine-readable, pinnable release, and an input transcribed by hand
from a PDF is the manual data manipulation step Rule 2 exists to keep out. The cost is that
every province is scaled by the same factor, so the fork probes a trend and not a differential,
and the script says so where it bites. **Anchoring the series to 1995**, the year whose national
total matches the snapshot's, rather than to the schema's 2020 — rejected because it would
substitute our inference about the column for the archive's statement about it, and because
under a log offset the two anchors are the same analysis. **Interpolating monthly rather than
annually** — rejected as false precision: the source is an annual estimate and a monthly
interpolation would invent within-year structure the series does not carry.

agency: agent-autonomous. That the static column is a problem was established from the data by
batch 3; that the alternative to it is a back-cast was fixed by batch 5's fork design. The
choice of the World Bank national series, the multiplicative construction, the anchor and the
decision not to chase the censuses are the agent's.
information: agent-retrieved — the series is fetched from the World Bank API by
`AI-internal/data-acquisition/fetch_lao_population.sh` and archived under
`Archive/lao-population/`, whose `provenance.md` carries the vintage and the licence; the
snapshot's reference year is read from the dataset's own schema file.
