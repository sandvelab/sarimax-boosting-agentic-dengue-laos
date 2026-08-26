# Provenance — figure: per-province score and calibration

```
result:              results/main/fig_crps_by_location.png
                     results/main/fig_crps_by_location.csv
                     results/main/fig_crps_by_location_preaggregation.csv
script:              scripts/fig_crps_by_location.py
                     sha256:a2076299572146b7ff0fcaf6bf18c94f4596047475e61caf656dc50d4143d90f
invocation:          "$PYTHON" scripts/fig_crps_by_location.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/04_score/02_aggregate/a_unweighted/results/main/crps_by_location.csv
                     (resolved by searching for the one child of 02_aggregate with
                     results under this combination)
                     analysis/04_score/01_collect/results/main/metrics_cell.csv
environment:         environment/ (project main) — matplotlib 3.11.1, pandas 2.3.3
seeds:               none.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-26
```

**What it shows.** Every model's mean CRPS per province on a log scale, provinces ordered by
the dengue burden that produced it, with 10–90 interval coverage beside it. This is the
figure batch 6 said batch 7 would draw once two models were in the tree, and it exists
because the headline number is an unweighted mean over provinces whose burdens differ by
four orders of magnitude: an aggregate coverage close to nominal can be an average of a
province covered every time and a province covered almost never, and batch 6 measured
exactly that on one model.

The reference's four repeats are not drawn individually; the row drawn for it is the
per-cell mean over them, which is what the conclusion divides by. The repeats are in the
pre-aggregation file.

**Plotted values** are in `fig_crps_by_location.csv`. **Pre-aggregation values** are in
`fig_crps_by_location_preaggregation.csv` — the per-cell scores the province means average.

**One thing the axis label had to be corrected about.** The count beside each province is the
cases in the **evaluated** cells, 2008-01 to 2009-12, not over the whole record — it is what
the score is averaged against, and the two orderings are not the same province ordering. The
first version said only "cases", which would have invited a reader to compare it with batch
3's per-province totals over twelve years.

alternatives-considered: a linear CRPS axis was rejected because Vientiane Capital's mean
is two orders of magnitude above Phongsaly's and everything but the capital would sit on the
axis. Ordering provinces alphabetically rather than by burden was rejected: the ordering is
what makes the relationship between burden and score legible, and it is the relationship the
figure exists to show.

agency: agent-autonomous.
