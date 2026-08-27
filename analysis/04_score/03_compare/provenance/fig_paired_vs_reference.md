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

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

Regenerated on `main` after the promotion, from the promoted candidate's scores. The sweep
combinations do not reach this node: batch 9 stops at `02_aggregate`, because a conclusion
per sibling is the phase-D deliverable and producing nine of them here would report the
stability answer before the manifest that makes it honest has been frozen.

**What moved.** The candidate's paired difference against the reference fell from **4.002**
CRPS to **1.599**, and its split-clustered standard error is **1.551**, so the difference
is **1.03 standard errors** -- against 3.62 for the batch-8 configuration. The comparison
that batch 8 could resolve, this one cannot: on the development backtest our candidate and
the field's own model are not distinguishable. It wins 41 % of cells and 2 of 8 splits.

alternatives-considered: none new; the node's own choices are batch 7's.

agency: agent-autonomous.
