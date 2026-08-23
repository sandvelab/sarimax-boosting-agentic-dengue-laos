# Provenance — the national dengue series

```
result:              results/fig_cases_timeline.png
                     results/fig_cases_timeline.csv                (the plotted values)
                     results/fig_cases_timeline_preaggregation.csv  (the province-month
                     observations the national line sums over)
script:              scripts/fig_cases_timeline.py
                     sha256:47f1e7a2155d00fe8770035e5f26fa824af60aeb6a6135a106dee633293e89ff
invocation:          "$PYTHON" scripts/fig_cases_timeline.py
                     (from the node directory, via run.sh)
inputs:              results/cases_national_monthly.csv
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

**What it shows.** Sharp annual epidemics with a large 2003 peak and a smaller 1998 one, on
a strong and stable annual cycle. The lower panel is the count of provinces reporting in
each month, which falls from 17 to 15–16 after 2005 and is drawn beneath the series
deliberately: a national total over a varying number of reporting provinces is not
comparable across months, and the figure would be misleading without it. The per-province
mean is stored in the plotted-values file for the same reason.

alternatives-considered: plotting the national total alone is cleaner and was rejected
because it hides the reporting change. A per-capita rate was the other option and was
rejected because the population figure is a single 2020 snapshot applied to all thirteen
years, so a rate would carry that error into the picture; how population should enter is a
phase-D fork, not something to settle in a figure.

agency: agent-autonomous.
