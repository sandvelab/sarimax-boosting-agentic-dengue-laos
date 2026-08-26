# Provenance — the vertical slice

One section per group of outputs in this folder, per `AGENTS.md` §8. Append; never
overwrite an existing section.

Everything here was produced on 2026-08-26 from commit `ced3e1a`, which is the
commit-before-the-run of Rule 4 and contains the model and the scripts exactly as they
were executed. The instruction set in force was `15b4ba9`; the tree machinery in
`AI-internal/useful-scripts/` was at `1ae2649`.

---

## `persistence_development_eval.nc`, `persistence_development_eval.log`, `persistence_fitted_model.json`

```
result:              persistence_development_eval.nc
                     persistence_development_eval.log
                     persistence_fitted_model.json
                     slice_run_cost.json
                     slice_inputs.sha256
script:              AI-internal/vertical-slice/run_vertical_slice.sh
model:               AI-internal/vertical-slice/persistence_model/
                     MLproject     sha256:cbd3158db12438ac9dc2ce94d4397b9cce2e02170c76f3715004a83221d7f0d6
                     pyproject.toml sha256:d9bea910f823bf3b61d4b70192ca4f330a7fc2ad2d026e97dce4e44d636357f7
                     uv.lock       sha256:b02aa38515b1a2112f949bdfe9eee55ba9c7a7baf3163f3b97630c5991c28311
                     train.py      sha256:00d202385453b55fce6d675a48cc515daf87f062e66061e9433892f650e5c908
                     predict.py    sha256:e9e96b8fb0290b70fc6db7ca0d865b940a2987cce563d68172d49df77db5ab7e
invocation:          bash AI-internal/vertical-slice/run_vertical_slice.sh
                     (from the repository root; the eval command it issues is
                      chap eval --model-name <model dir>
                        --dataset-csv analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                        --backtest-params.n-periods 3 --backtest-params.n-splits 8
                        --backtest-params.stride 3 --backtest-params.n-retrain 1)
inputs:              analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0.
                     The model brings its own: chap-core's uv_env runner built it from
                     the model's pinned pyproject.toml and uv.lock — CPython 3.13.0,
                     numpy 2.5.2, pandas 3.0.5, python-dateutil 2.9.0.post0, six 1.17.0,
                     tzdata 2026.3. **The lockfile shipped with the model is the one the
                     run used**: the copy chap-core left in its run directory is
                     byte-identical to the tracked one, so the model's environment is
                     pinned by a file under version control rather than re-resolved at
                     run time.
seeds:               none. The model contains no randomness — its predictive
                     distribution is the empirical quantile function evaluated at the
                     1 000 fixed levels (i + 0.5)/1000, not sampled from. Project seed
                     20260822 has no surface here. Verified, not asserted: see
                     determinism_check.json.
commit:              ced3e1a
instructions-commit: 15b4ba9
node:                none — the claim tree is erected in batch 7. This is the vertical
                     slice, and its numbers are not reported results of the project.
produced:            2026-08-26
```

**What it establishes.** The chain runs, on the real data, at the fixed scheme, with a
file at every join. The evaluation covers **371 cells over 16 provinces and 8 splits** —
independently reproducing what batch 3 derived from chap-core's splitter and batch 4
observed on the reference. The run's own log carries `Rejected regions: ['LA-VI'] due to
missing target values for the whole training period`, and Phongsaly contributes 11 cells
where every other province contributes 24, which is the second half of batch 3's
prediction.

**The four `Column '<name>' is present in the dataset but not used by the model`
warnings are correct here**, unlike the cosmetic ones batch 4 recorded for the
reference. This model genuinely uses no covariate: a persistence forecast reads only
past values of the target. It is recorded so that the same warning text is not read the
same way in both places.

**`Model has not specified minimum and maximum predicted length`** is expected. The
`MLproject` leaves `min_prediction_length` and `max_prediction_length` unset because the
model is defined at any horizon; the change distribution is fitted for `h` up to 3 and
the evaluation never asks for more.

alternatives-considered: the model could have been run from a node in the claim tree
straight away, which would have avoided running it twice. It was not, because batch 7
builds the tree and routing a model through a tree that does not exist is how the tree
ends up shaped by one model. The evaluation costs 16 seconds, so the duplicated compute
is not worth pre-empting a design decision for. The point forecast could also have been
carried forward from a *smoothed* recent window rather than the single last observation;
that is a different baseline, not this one, and the plan names this one.

agency: agent-autonomous. The requirement for a persistence baseline and the backtest
scheme are the plan's and batch 3's; the model's construction, its environment pinning
and the decision to run it outside the tree are the agent's.
information: agent-retrieved — the two published constructions for a probabilistic
persistence baseline, see the next section.

---

## `results/main/` — the contract files

```
result:              results/main/metrics_cell.csv
                     results/main/metrics_summary.csv
                     results/main/crps_by_location.csv
                     results/main/crps_by_split.csv
                     results/main/crps_by_region_split.csv
                     results/main/crps_by_horizon.csv
script:              AI-internal/vertical-slice/collect_metrics.py
invocation:          environment/chapenv/bin/python AI-internal/vertical-slice/collect_metrics.py
                       --evaluation AI-generated/vertical-slice/persistence_development_eval.nc
                       --model persistence
                       --out-dir AI-generated/vertical-slice/results
                       --combo main
                     (issued by run_vertical_slice.sh)
inputs:              persistence_development_eval.nc, produced by the section above
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; the script is a set of aggregations
commit:              ced3e1a
instructions-commit: 15b4ba9
node:                none — batch 7 moves this routine to analysis/04_score/01_collect
produced:            2026-08-26
```

**No metric is implemented here, and that is the point.** Every value in every file
comes from chap-core's own registered metric, asked for by id — `crps`, `mae`,
`coverage_10_90`, `coverage_25_75` — at the platform's finest resolution, which is the
cell `(location, time_period, horizon_distance)`. The only things this script chooses
are the level of aggregation and the split label, and the split label is recovered by
the arithmetic batch 2 established, `split = time_period − (horizon_distance − 1)`.
Batch 2's rule stands: a metric we computed ourselves is precisely the metric we could
bend without it being visible, and the defence is not to write one.

**Every reported figure is an aggregation of `metrics_cell.csv`, and nothing is typed.**
The summary, the per-province table, the per-split table and the per-horizon table are
all `groupby` operations on that one file, so a reader can recompute any of them from
it, and no value crosses between steps except through a file (`AGENTS.md` §1).

alternatives-considered: the per-split values could have been taken from chap-core's
`split_periods` attribute on the `.nc` rather than recovered arithmetically. Batch 2
established that the two agree exactly on the smoke run, and the arithmetic form works
on a frame that has already been flattened, which is where the aggregation happens. The
coverage metrics could have been reported only at the aggregate level, which is what
`chap export-metrics` offers; they are carried per cell because a per-province
calibration figure turned out to be the most informative thing in this batch.

agency: agent-autonomous.

---

## `determinism_check.json`

```
result:              determinism_check.json
script:              AI-internal/vertical-slice/verify_determinism.sh
invocation:          bash AI-internal/vertical-slice/verify_determinism.sh
inputs:              two independent runs of run_vertical_slice.sh into temporary directories
environment:         environment/ (project main)
seeds:               none — the claim under test is that there is nothing to seed
commit:              ced3e1a
instructions-commit: 15b4ba9
node:                none
produced:            2026-08-26
```

**Result: identical.** Six contract files and the fitted model came back byte for byte
the same across two independent runs.

The evaluation `.nc` is excluded from the comparison, and that exclusion is inherited
rather than invented: batch 2 established that chap-core stamps `created_date` into the
file and serialises `split_periods` and `org_units` from unordered sets, so two
identical runs differ in those bytes while nothing numeric moves. Everything the project
reports from is computed *out of* the `.nc` and is compared.

agency: agent-autonomous. Rule 6 requires verification rather than assertion; how to
verify is the agent's.

---

## Sources for the baseline's construction

Read rather than recalled, per `AGENTS.md` §7. Two published constructions exist for
putting a predictive distribution around a persistence forecast, and they disagree —
which is why the choice is a logged decision here and a fork in phase D rather than a
detail.

- **Non-parametric, and the one taken.** The US COVID-19 Forecast Hub's baseline is a
  random walk whose predictive quantiles are the quantiles of the collection of observed
  differences *and their negations*, with quantiles below zero truncated to zero; the
  negations are what make the distribution symmetric and the predictive median equal to
  the most recent observation. Retrieved 2026-08-26 via search; the description above is
  from the search result summarising the Hub's baseline specification, and the
  peer-reviewed statement of the same baseline's behaviour — *"the baseline model assumes
  case or death counts stay the same as the latest data point over all future horizons,
  with expanding uncertainty"* — was read in full at
  Sherratt, K. et al., *Predictive performance of multi-model ensemble forecasts of
  COVID-19 across European nations*, **eLife** 12:e81916 (2023),
  doi:10.7554/eLife.81916, <https://elifesciences.org/articles/81916>.
  That paper does not reproduce the technical specification, and says so; it refers to
  Cramer et al. for it. **This is recorded honestly**: the field's use of the baseline is
  read from a peer-reviewed source, the exact construction from a secondary description
  of the Hub's implementation, and the implementation here is the project's own.
- **Parametric, and the one not taken.** The KIT baseline for the German COVID-19
  Forecast Hub sets the predictive mean for the next period to the previous observation
  and takes quantiles from a negative binomial with a dispersion estimated by maximum
  likelihood from the last five observations, with the mean floored at 0.2 *"to avoid
  zero variance in parametric predictive distribution"* when nothing was observed. Read
  at <https://github.com/KITmetricslab/KIT-baseline>, 2026-08-26.

**Why the non-parametric one is the main path.** 56 % of observed months in this dataset
are zero and six of sixteen evaluated provinces are above 85 % zeros, so the parametric
form's floor would be doing visible work in a majority of cells — an arbitrary constant
setting the width of the predictive distribution wherever the baseline matters most. The
non-parametric form estimates nothing and needs no floor. The parametric form is
retained as the sibling of the phase-D fork on how uncertainty is wrapped around a point
baseline, which is a fork this batch adds to batch 5's inventory.

agency: agent-autonomous, on `agent-retrieved` information.
