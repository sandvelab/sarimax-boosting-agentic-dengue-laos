# Provenance — the climate–dengue lag structure

```
result:              results/fig_covariate_lag_correlation.png
                     results/fig_covariate_lag_correlation.csv                (the plotted values)
                     (no separate pre-aggregation file: the per-province correlations are
                     summarised in lag_correlation.csv, which carries the min, median, max
                     and the count of provinces on each side of zero — the spread the
                     figure draws)
script:              scripts/fig_covariate_lag_correlation.py
                     sha256:ddc24b26fbbf1cc8ad2b1555fa1e9867055aecb39b80a4737547aa37b6f92e64
invocation:          "$PYTHON" scripts/fig_covariate_lag_correlation.py
                     (from the node directory, via run.sh)
inputs:              results/lag_correlation.csv
environment:         environment/ (project main) — CPython 3.13.0, matplotlib 3.11.1
seeds:               none. The figure is a deterministic redraw of a stored table;
                     project seed 20260822 has no surface. Verified by running the
                     tree twice: the PNG came back byte-identical.
commit:              1ae2649
instructions-commit: 15b4ba9
node:                analysis/01_data/02_characterise
produced:            2026-08-23
```

**What it shows.** Rainfall associates most strongly at a lag of one month (mean Spearman
0.32 over provinces, positive in all 17), temperature at two to three months (0.32, positive
in 16–17), humidity at nought to one (0.31, positive in all 17). The band is the min–max
across provinces and is wide: the association is consistent in sign but not in size. The
turn negative by lag five or six is the far side of the annual cycle, not a mechanism.

alternatives-considered: cross-correlation on detrended or deseasonalised series would
separate the within-season association from the shared annual cycle, and is a better
question than this figure answers. It is deliberately left to phase C: at this stage the
purpose is to know that a lag structure exists and roughly where, which decides whether
lagged covariates are worth a fork at all.

agency: agent-autonomous.
