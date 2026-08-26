# Provenance — figure: what the paired comparison can separate

```
result:              results/main/fig_paired_vs_reference.png
                     results/main/fig_paired_vs_reference.csv
                     results/main/fig_paired_vs_reference_preaggregation.csv
script:              scripts/fig_paired_vs_reference.py
                     sha256:0e6530003a76e38db7d3c9275d185ac8f94af6c7cd644ad53a92c7a3d1b06a68
invocation:          "$PYTHON" scripts/fig_paired_vs_reference.py
                     (from the node directory, via run.sh, after compare_models.py;
                     PYTHON is environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              results/main/paired_vs_reference.csv
                     results/main/paired_summary.csv
                     results/main/paired_by_split.csv
                     results/main/reference_repeat_noise.csv
environment:         environment/ (project main) — matplotlib 3.11.1, pandas 2.3.3
seeds:               none. Every panel is a deterministic summary of stored scores.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-26
```

**What it shows.** Three readings of the same comparison, getting stricter left to right: the
per-cell paired differences as a distribution; the same differences aggregated to the eight
backtest splits; and the mean paired difference per model with the naive error bar beside
the clustered one, against a shaded band showing where the reference's own unseeded re-runs
put it. **A model whose interval overlaps that band has not been distinguished from the
reference by this evaluation**, however large its aggregate margin looks — which is the
figure's whole point and the reason the band is drawn rather than described.

**Plotted values** are in `fig_paired_vs_reference.csv` (the per-model summary rows).
**Pre-aggregation values** are in `fig_paired_vs_reference_preaggregation.csv` — every
per-cell paired difference the panels summarise, so the histogram can be rebuilt at any
binning and the error bars recomputed under any other assumption.

The left panel uses a symmetric log scale because the differences span four orders of
magnitude in the tails and a linear axis shows one spike and nothing else. That is a
presentation choice and it is stated here because it is the kind of choice that changes what
a reader sees without changing a number.

alternatives-considered: a cumulative distribution rather than a histogram would avoid the
binning choice entirely and was not taken because the two-sided asymmetry of the differences
is what the panel is for and reads worse as a CDF. Plotting per-province rather than
per-split differences in the middle panel was rejected — the split panel is the one that
corresponds to a comparison needing no independence assumption, and the province view is the
other figure at this node.

agency: agent-autonomous.
