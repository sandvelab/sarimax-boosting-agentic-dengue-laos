# vertical-slice — batch 6

What the first model produced, end to end, on the real development dataset at the
scheme batch 3 fixed. Built by `AI-internal/vertical-slice/`; every file here has a
section in `provenance.md` beside it.

**None of these numbers is a reported result of the project.** The claim tree is
erected in batch 7, and a result produced outside the tree does not exist — the same
rule batch 4 applied to the reference model's score. What this batch establishes is
that the chain runs and what each link produces; batch 7 re-runs the identical model
from `analysis/03_models/01_baselines/01_persistence/` and that run is the one that is
reported.

## Currently here

| File | What it is |
|---|---|
| `results/main/metrics_cell.csv` | the contract file: one row per evaluable cell, every metric, the observed value beside them |
| `results/main/metrics_summary.csv` | the headline row: mean CRPS, MAE, both coverages |
| `results/main/crps_by_location.csv` | per province, with its coverage and its observed total |
| `results/main/crps_by_split.csv` | per backtest split |
| `results/main/crps_by_region_split.csv` | the two crossed |
| `results/main/crps_by_horizon.csv` | per lead time, 1 to 3 months |
| `persistence_development_eval.nc` | chap-core's own evaluation output, 10 MB |
| `persistence_fitted_model.json` | the fitted change distributions — what the spread comes from |
| `persistence_development_eval.log` | the run's log, including the rejected-region line |
| `slice_run_cost.json` | wall clock, written by the script that held the clock |
| `slice_inputs.sha256` | the bytes that went in |
| `determinism_check.json` | Rule 6: two runs, compared byte for byte |

`results/main/` is literal, not decorative: `main` is the combination id that batch 5's
design gives the main analysis path, and every node in the tree will read and write
under `results/$COMBO/`. The layout is exercised here, with one child per fork, before
it has to carry alternatives.

`slice-work/` is not tracked — chap-core's per-split run directories and the
environment `uv` builds for the model, about 77 MB, rebuilt by the runner from the
pinned lockfile.
