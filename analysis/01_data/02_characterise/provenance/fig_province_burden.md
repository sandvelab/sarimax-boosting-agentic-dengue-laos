# Provenance — the burden distribution across provinces

```
result:              results/fig_province_burden.png
                     results/fig_province_burden.csv                (the plotted values)
                     results/fig_province_burden_preaggregation.csv  (the province-month
                     counts the totals sum over)
script:              scripts/fig_province_burden.py
                     sha256:94a8206919059030a56fa447cb547508e16a78d6aabe48a35b18449a32e9c51f
invocation:          "$PYTHON" scripts/fig_province_burden.py
                     (from the node directory, via run.sh)
inputs:              results/cases_by_province.csv
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

**What it shows.** Four orders of magnitude between Vientiane Capital's 28 768 cases and
Phongsaly's four, and six provinces reporting zero in more than 85% of their observed
months. This is the figure behind the warning about the metric: CRPS is averaged unweighted
over provinces, so six provinces where predicting zero is almost always right carry the same
weight as the capital, and a model can improve the headline number by getting the easy
provinces slightly more confidently right.

alternatives-considered: a linear axis was tried first and collapses fifteen provinces onto
the baseline; the log axis is honest here because the question is the order of magnitude,
and the zero-burden province is drawn at a floor value rather than dropped so that its
absence from the metric stays visible. Cases per 100 000 is in the plotted-values file and
was not drawn, because it inherits the static-population problem.

agency: agent-autonomous.
