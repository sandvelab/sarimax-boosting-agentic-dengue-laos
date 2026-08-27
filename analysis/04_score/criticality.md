# Criticality — what `04_score` stores, and what it would cost to lose

Written by `/annotate-criticality`. **This file proposes nothing and deletes nothing.**

Everything here is regenerable by `bash analysis/04_score/run.sh` in **about twenty seconds**
— *provided the model nodes' evaluation files still exist*. That proviso is the whole
storage question for this project and it is settled at `03_models`, not here: three of the
six evaluations upstream cannot be reproduced at all.

Total: **1.3 MB per combination.**

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `01_collect/results/$COMBO/metrics_cell.csv` | 183 KB | **main result** | yes, ~15 s, **only while the `.nc` files survive** | **highest** | Every reported figure in the project is an aggregation of this file. Two orders of magnitude smaller than the 56 MB of NetCDF it is derived from, and it carries everything the project reports. **If storage ever forces a choice between this file and the evaluations behind it, this is what to keep for our own models** — they can be re-run; the reference's cannot. |
| `01_collect/results/$COMBO/models.csv` | 1 KB | main result | yes, ~15 s | high | What each scored row is: origin, node, seeded or not, which repeat. Tiny and load-bearing. |
| `02_aggregate/*/results/$COMBO/metrics_summary.csv` | 1 KB | **main result** | yes, ~1 s | **highest** | The headline figures. |
| `02_aggregate/*/results/$COMBO/crps_by_location.csv` | 5 KB | **main result** | yes, ~1 s | **highest** | Where the aggregate hides the most; the per-province spread is one of the batch's two substantive findings. |
| `02_aggregate/*/results/$COMBO/crps_by_split.csv`, `crps_by_region_split.csv`, `crps_by_horizon.csv` | 1–20 KB | main result | yes, ~1 s | high | The resolutions the plan requires beside the mean. |
| `03_compare/results/$COMBO/leaderboard.csv` | 2 KB | **main result** | yes, ~5 s | **highest** | The file phase C adds candidates to, and the one the plan requires never to be typed. |
| `03_compare/results/$COMBO/paired_summary.csv` | 3 KB | **main result** | yes, ~5 s | **highest** | The answer to what the comparison can resolve. |
| `03_compare/results/$COMBO/reference_repeat_noise.csv` | 2 KB | **main result** | **no** — it is a statistic of four unseeded runs that cannot be repeated | **highest** | The noise floor, computed from the reference against itself. Re-running would produce a different floor from different draws. Small, and irreplaceable in the same sense as the evaluations it comes from. |
| `03_compare/results/$COMBO/paired_vs_reference.csv` | 328 KB | side result | yes, ~5 s | medium | Every per-cell paired difference, per reference variant. The largest file at this node and the most prunable: it is a join of two columns of `metrics_cell.csv`, and it is kept because it is what the figure's pre-aggregation file points at. |
| `03_compare/results/$COMBO/paired_by_split.csv`, `comparison_notes.json` | 1–7 KB | main result | yes, ~5 s | high | The split-level comparison and the machine-readable summary of what it resolves. |
| `03_compare/results/$COMBO/fig_*.png` + `.csv` + `_preaggregation.csv` | 60–150 KB each | main result | yes, ~5 s | high | Rule 7: the figures with their plotted values and their pre-aggregation values. The pre-aggregation files duplicate columns of `metrics_cell.csv` and are the second candidate for pruning after `paired_vs_reference.csv`. |

**At the scale of the manifest.** About 1.3 MB per combination over 28 combinations is
**37 MB**, and the figures are drawn only for the combinations that get reported. Nothing
here binds.

## Added in batch 8

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `03_compare/results/$COMBO/fig_accuracy_and_spread.png` + `.csv` | 132 KB + 1 KB | **main result** | yes, ~2 s | **highest** | The figure that shows CRPS and MAE ranking the models in opposite orders. Its plotted-values file is eight rows and is the cheapest way to read the batch's central finding. |
| `03_compare/results/$COMBO/fig_accuracy_and_spread_preaggregation.csv` | 132 KB | side result | yes, ~2 s | medium | The per-cell scores the eight summary rows average — a subset of `metrics_cell.csv`'s columns. Prunable in the same breath as the other two pre-aggregation files, and after them, since it is the smallest. |
