# Provenance — the reporting grid

```
result:              results/fig_completeness.png
                     results/fig_completeness.csv                (the plotted values)
                     results/fig_completeness_preaggregation.csv  (every absent
                     province-month individually)
script:              scripts/fig_completeness.py
                     sha256:9f4c1eb914ed2fe3cbe368f2b2336424e21f2738b007e212ebac53797019b4c7
invocation:          "$PYTHON" scripts/fig_completeness.py
                     (from the node directory, via run.sh)
inputs:              results/completeness_by_province_year.csv
                     results/target_missing_cells.csv
environment:         environment/ (project main) — CPython 3.13.0, matplotlib 3.11.1
seeds:               none. The figure is a deterministic redraw of a stored table;
                     project seed 20260822 has no surface. Verified by running the
                     tree twice: the PNG came back byte-identical.
commit:              1ae2649
instructions-commit: 15b4ba9
node:                analysis/01_data/02_characterise
produced:            2026-08-23
```

**What it shows.** The figure that decides what the headline metric is a mean over.
Vientiane is empty for all twelve years; Xaisomboun is complete through 2005 and empty from
2006; Phongsaly loses 2008 and one month of 2009; Xekong loses four months of 2007.
Everything else is complete.

alternatives-considered: a province × month grid at full resolution would show exactly which
months are absent rather than how many per year, and was rejected as illegible at 18 × 144;
the per-cell detail is in the pre-aggregation file instead. Showing the missing count rather
than the observed count inverts the colour scale to no benefit.

agency: agent-autonomous.
