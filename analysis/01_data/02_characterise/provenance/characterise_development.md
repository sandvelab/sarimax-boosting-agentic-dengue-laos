# Provenance — the description of the development period

```
result:              results/dev_overview.json
                     results/covariate_units_check.json
                     results/completeness_by_province_year.csv
                     results/target_missing_cells.csv
                     results/cases_by_province.csv
                     results/cases_by_year.csv
                     results/cases_national_monthly.csv
                     results/seasonality_by_month.csv
                     results/zero_structure.csv
                     results/covariate_summary.csv
                     results/population_static_check.csv
                     results/lag_correlation.csv
script:              scripts/characterise_development.py
                     sha256:a94fe9c009085ef6d8f38c87a2472162035cad09655d6e6cb80c7cc7b75e8ca8
invocation:          "$PYTHON" scripts/characterise_development.py
                     (from the node directory, via run.sh)
inputs:              ../01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     Archive/lao-dataset/chap_LAO_admin1_monthly_schema.json
                     sha256:ff750db4202c32fc187b26bb3566b4f981b94467664502e76cbd09977dd06210
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every table is a deterministic summary — counts, quantiles and
                     rank correlations — with no resampling anywhere; project seed 20260822
                     has no surface. Verified by running the tree twice: byte-identical.
commit:              1ae2649
instructions-commit: 15b4ba9
node:                analysis/01_data/02_characterise
produced:            2026-08-23
```

**What it establishes.** 2 592 rows, 18 provinces, 144 months, a complete grid. 209 of the
target cells are missing (8.1%) and 1 341 of the 2 383 observed are zero (56.3%); 77 031 cases
in total. One province, Vientiane (LA-VI), never reports at all; Xaisomboun (LA-XN) reports
through 2005-12 and then stops; Phongsaly (LA-PH) has four cases in twelve years. Population is
static across the whole period for every province, confirming the schema's own note. Dengue
peaks in July–September; rainfall leads it by about a month, temperature by two to three,
humidity by nought to one. The schema's `rainfall` unit is wrong: read as the declared monthly
total it puts a province's year at 50–78 mm, read as a mean daily rate at 1 518–2 383 mm.

**On the negative correlations at lags five and six.** They are the far side of a twelve-month
cycle, not a mechanism, and are stored rather than interpreted.

alternatives-considered: the lag correlations could have been pooled across provinces in one
regression, which is more powerful and would have let the between-province differences in
level enter as if they were a climate signal; they are computed within province and then
summarised instead, and the min–max band over provinces is kept so the spread is visible.
Pearson on log1p counts was the other reasonable choice and would be defensible; Spearman was
taken because more than half the observed months are zero and a rank statistic does not depend
on how the ties are transformed. Both are cheap, and the choice is a candidate perturbation
for phase D rather than a settled question. Completeness could have been reported only as a
total; it is broken down by province and year because which provinces reach the metric turns
out to depend on it.

agency: agent-autonomous. What to characterise is the plan's (§7, batch 3); every statistic,
cut and transformation here is the agent's.
information: human-pointed — the static-population problem and the expectation of zero-heavy
early years come from `Archive/case-source-material/chapOrientation.md` §4.
