# method-reconnaissance

What batch 4 established about the *methods* available to this project, captured to files so
that `26-08-23_b04_methodSurvey.md` quotes stored output rather than terminal scrollback.
Three questions, one folder: does the reference model of the plan's §2 run on this project's
development dataset, what does it cost, and what else is in Chap's model library.

Everything here is regenerable — `bash AI-internal/reconnaissance/run_ewars_reference.sh`,
`ewars_reproducibility.sh` and `capture_model_library.sh` — with one caveat that is itself a
finding: **the reference model is unseeded**, so a re-run reproduces the recipe but not the
numbers. `provenance.md` records the pins, the invocations and the commit behind each file.

| File | What it holds |
|---|---|
| `ewars_image_pin.txt`, `ewars_image_labels.json` | The reference pinned by image digest, and the source commit the image was built from |
| `ewars_service_info.json`, `ewars_config_schema.json` | What the running chapkit service declares about itself and its configurable surface |
| `ewars_development_eval.nc`, `ewars_development_eval.log` | One backtest of the reference on the development dataset at the scheme batch 3 fixed: 16 provinces, 3 periods × 8 splits |
| `ewars_dataset_warnings.txt` | The regions Chap dropped and the columns it reported unused, from the run's own log |
| `ewars_metrics_aggregate.csv` | What `chap export-metrics` gives: every registered metric, no breakdown |
| `ewars_development_metrics_global.csv` | CRPS, MAE and the two interval-coverage metrics, at global aggregation |
| `ewars_development_crps_by_location.csv`, `_by_split.csv`, `_by_region_split.csv`, `_detailed.csv` | The same CRPS at four resolutions, from chap-core's own metric classes |
| `ewars_development_mae_by_location.csv`, `_coverage_10_90_by_location.csv`, `_coverage_25_75_by_location.csv` | The secondary metrics per province |
| `ewars_development_evaluable_cells.csv`, `_samples_per_cell.csv` | What the headline mean is a mean over, and how many draws stand behind each cell |
| `ewars_run_cost.json` | Wall clock and seconds per split, for batch 5's budget |
| `ewars_repeatability_runs.csv`, `ewars_repeatability_summary.csv` | Four identical invocations of the reference, and how far their scores move |
| `ewars_reference_spread.json` | The three spreads that bound any comparison against the reference: Monte Carlo, across splits, across regions |
| `chap_models_inventory.csv` | Every repository in `github.com/chap-models`, joined to the last published sweep of which ones still run |
| `chap_models_checker_report.json` | That sweep, as published, pinned by commit |
| `chap_models_library_summary.json`, `model_library_sources.txt` | The counts the survey quotes, and where the two sources came from |
| `native_run_cost.json`, `native_development_metrics_global.csv`, `native_development_eval.log` | What an evaluation run costs for a *native* Python model on this data — the unit batch 5's budget needs for our own candidates |
| `ewars-work/`, `library-work/`, `native-work/` | Untracked. Run directories, per-repeat evaluation files, and a clone of the sweep. |

**The reference score here is not yet a result of this project.** It establishes that the
criterion of the plan's §2 is attainable and what it costs. The *reported* reference score is
produced inside the claim tree, from a node, once the tree exists — because a result produced
outside the tree does not exist (`AGENTS.md` §2, and the plan's phase B).
