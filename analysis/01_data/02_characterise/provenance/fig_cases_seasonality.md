# Provenance — the seasonal profile against climate

```
result:              results/fig_cases_seasonality.png
                     results/fig_cases_seasonality.csv                (the plotted values)
                     results/fig_cases_seasonality_preaggregation.csv  (the province-month
                     observations the monthly means are taken over)
script:              scripts/fig_cases_seasonality.py
                     sha256:2eb01a4d8eca72f59b41375f890714d2b59ad99d9d7a8f37f3aaf5bfed5daf70
invocation:          "$PYTHON" scripts/fig_cases_seasonality.py
                     (from the node directory, via run.sh)
inputs:              results/seasonality_by_month.csv
                     ../01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, matplotlib 3.11.1
seeds:               none. The figure is a deterministic redraw of a stored table;
                     project seed 20260822 has no surface. Verified by running the
                     tree twice: the PNG came back byte-identical.
commit:              1ae2649
instructions-commit: 15b4ba9
node:                analysis/01_data/02_characterise
produced:            2026-08-23
```

**What it shows.** Cases peak in July–August at roughly fourteen times the February trough.
Rainfall peaks with them; humidity rises earlier and stays high through the season. The
rainfall axis is labelled mm/day, which is what the column is rather than what the schema
declares — see `covariate_units_check.json`.

alternatives-considered: the mean is shown rather than the median, which is zero in every
month and would draw a flat line — a true statement about a zero-heavy panel and an
uninformative figure. Both are in the plotted-values file. A per-province small-multiple
would show that the peak month differs across the country and is deferred to phase C, where
it would inform a model rather than describe the data.

agency: agent-autonomous.
