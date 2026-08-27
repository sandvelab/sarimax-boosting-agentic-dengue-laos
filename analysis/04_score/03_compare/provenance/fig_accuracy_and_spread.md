# Provenance — point accuracy against distributional accuracy

```
result:              results/main/fig_accuracy_and_spread.png
                     results/main/fig_accuracy_and_spread.csv
                     results/main/fig_accuracy_and_spread_preaggregation.csv
script:              scripts/fig_accuracy_and_spread.py
                     sha256:5690ff8cf2db1756275f933d15fe8e6995085bf7a55f7a65d4c8313b1d013e49
invocation:          "$PYTHON" scripts/fig_accuracy_and_spread.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so the combination is
                     `main` and results go to results/main/.)
inputs:              analysis/04_score/02_aggregate/a_unweighted/results/main/metrics_summary.csv
                     analysis/04_score/01_collect/results/main/metrics_cell.csv
                     (the aggregate is found by searching 02_aggregate for the one child
                     with results under this combination, never by naming a child)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     matplotlib from the same environment
seeds:               none; a deterministic summary of stored scores. Project seed
                     20260822 has no surface here.
commit:              4563baf
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-27
```

**What it establishes.** The batch's central finding in one image: the candidate is the most
accurate model in the project on the point forecast (MAE 27.11, against the reference's
28.90) and the least accurate on the metric the project is scored by (CRPS 26.10, against
22.10). The two panels rule out the easy explanation. It is not that the candidate is badly
calibrated on average — it is the closest of our models to both nominal interval levels. The
problem is that coverage averaged over provinces cannot see an interval that is far too wide
in one province and far too narrow in another, which is what `fig_crps_by_location`'s second
panel shows and what the candidate's provenance record quantifies.

**Why the third figure at this node rather than a panel added to an existing one.** The two
figures already here answer "where does each model's score come from" and "can the paired
comparison separate two models". This one answers a third question that only became askable
when a model arrived whose two metrics disagreed. Adding it as a panel would have made a
figure about the comparison also be a figure about one model.

**The dashed lines are not measurements.** 0.50 and 0.80 are properties of the intervals'
definitions — a 10–90 interval covers 80 % of a calibrated forecast's outcomes because that
is what 10 to 90 means — and they are the only constants in the script.

alternatives-considered: plotting CRPS against sharpness (mean interval width) instead of
against MAE, which would name the mechanism more directly. Rejected because interval width
is not in the stored per-cell file — it would need the forecast quantiles out of the NetCDF,
and a figure that reaches past `01_collect` into the evaluations is a figure that stops being
an aggregation of the one scored file everything else reports from. Also considered: a PIT
histogram per model, which is the standard calibration diagnostic. Deferred to batch 9, where
it is diagnostic for a repair rather than description of a result.

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
