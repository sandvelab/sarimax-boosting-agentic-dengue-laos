# Batch 2 — reconnaissance: Chap

Generated from [[26-08-22_dengueForecastingCase]] — iteration 2

**Phase A · Status: done — produced · Executed 2026-08-23**

---

The batch that everything else waited on. `chap-core` installs, `chap eval` runs end to end
on this machine, and the five questions [[chapOrientation]] §5 left open are answered from
the running tool rather than from prose. Every quoted figure below comes from a file in
`AI-generated/chap-reconnaissance/`, which carries its own `provenance.md`.

## 1. The install recipe

```bash
bash environment/install-chap.sh          # from the repository root
environment/chapenv/bin/chap --version    # 2.1.0
```

The script creates a project-local virtual environment on **CPython 3.13.0** and installs
**`chap-core==2.1.0`**, then writes the resolved 174-package set to `environment/lock.txt`.
Nothing went wrong — no build failures, no compilation, no manual intervention — which is
worth saying plainly, because the batch was written on the assumption that this was the
risky step and it was not.

**`chap-core` needs no Docker and no R.** It is a pure-Python distribution with 53 declared
dependencies, resolving to 174 packages, all available as wheels on macOS arm64. Docker enters later and for a
different reason (§2).

Three details are load-bearing, and each is a decision rather than a detail:

- **Python 3.13, and pinned to the patch.** `chap-core` 2.1.0 declares
  `requires-python >=3.13,<3.14`, so the major and minor are forced. The patch is pinned
  because `uv venv --python 3.13` silently resolves to whichever 3.13 the building machine
  holds — here `3.13.0` from uv's own store, while the repository's `.venv` runs 3.13.7.
  A version that depends on what the machine happens to have is not a specification.
- **A project-local environment, not the documented tool install.** The documentation says
  `uv tool install chap-core --python 3.13`, which puts the executable in the operator's
  `~/.local/share/uv/tools` — outside the repository and outside anything `analysis/run.sh`
  can rebuild. The pinned version is identical either way; the location is what makes it
  reproducible from the repository alone. It is invoked as `environment/chapenv/bin/chap`,
  the same convention `AGENTS.md` §8 sets for `.venv`.
- **`CHAP_RUNS_DIR` must be set explicitly.** `chap-core` writes per-run working directories
  to `runs/` *relative to the current working directory* unless the environment variable
  says otherwise. Left implicit, where you were standing becomes part of the recipe.

The environment was rebuilt from scratch — `chapenv/` deleted, script re-run — and resolved
the identical 174 packages. `environment/environment.yml` and `environment/Dockerfile` were
rewritten to describe this build path; the conda framing they carried was repository
template text and never described anything that had been built. **The Docker layer has not
been verified**: no Docker daemon is running on this machine, so the third layer of Rule 3
is a specification and not an artifact. `environment/README.md` says so under *What cannot
be pinned*, alongside the two other things pinning `chap-core` does not cover.

## 2. The model contract

A Chap model is a **directory with an `MLproject` file** — YAML despite the name — declaring
what the model needs, what runtime it wants, and two commands. `chap-core` parses it into
`ModelTemplateConfigV2`, which forbids unknown fields, so the schema below is exhaustive
rather than illustrative.

```yaml
name: ewars_template                    # required; the only required field

target: disease_cases                   # what the model predicts
required_covariates: [population]       # must be present in the data
supported_period_type: any              # month | week | any
allow_free_additional_continuous_covariates: true
requires_geo: false                     # true if the model needs the GeoJSON polygons
min_prediction_length: null             # eval refuses a shorter horizon than this
max_prediction_length: null             # a longer one is wrapped and applied iteratively
user_options:                           # JSON-schema-shaped; the configurable surface
  precision: {type: number, default: 0.01, description: Prior on fixed-effect precision}
hpo_search_space: null
meta_data: {display_name: ..., author: ..., author_assessed_status: gray, ...}
adapters: {Cases: disease_cases, E: population}   # rename columns on the way in

docker_env: {image: ghcr.io/dhis2-chap/docker_r_inla:master}   # or uv_env / renv_env /
                                                               # conda_env / python_env

entry_points:
  train:
    parameters: {train_data: path, model: str, model_config: path}
    command: "Rscript train.R {train_data} {model} {model_config}"
  predict:
    parameters: {historic_data: path, future_data: path, model: str, out_file: path, model_config: path}
    command: "Rscript predict.R {model} {historic_data} {future_data} {out_file} {model_config}"
```

**The contract is language-agnostic.** `train` and `predict` are shell commands and the
exchange is CSV files on disk, so anything that reads a CSV and writes a CSV qualifies. The
worked examples are Python (`minimalist_example_uv`) and R (`minimalist_example_r`,
`ewars_template`), and nothing in the mechanism prefers either.

**`predict` writes the forecast as samples.** Its output CSV carries `time_period`,
`location`, and one column per draw — `sample_0`, `sample_1`, … The trivial example model
emits a single `sample_0`, which is the whole reason its CRPS came out numerically equal to
its MAE (§3). A real submission emits many, and the number of draws is the model's choice.

**The model brings its own environment, and Chap builds it.** Whichever `*_env` key the
`MLproject` declares selects a runner — `uv_env`, `renv_env`, `conda_env`, `python_env`, or
`docker_env` for an image. So pinning `chap-core` pins the platform and the metric, not the
models. **This is where Docker enters**: a model declaring `docker_env` cannot run without a
daemon.

**There is a second, newer route: a chapkit REST service**, run with
`--run-config.is-chapkit-model` and pointed at a URL. There is no `MLproject`; the model is
a FastAPI service built with `chapkit`, declaring its configuration as a pydantic model and
shelling out to train and predict scripts. This matters immediately, because the reference
model §2 of the plan names is one of these — see §5.

**Model URLs can carry a ref.** `--model-name https://github.com/org/repo@<commit>` clones
that commit specifically; without one, `chap-core` shallow-clones the default branch. The
plan's §4b decision to pin the reference model by commit is therefore satisfiable directly,
and the vendoring fallback it allowed for is not needed.

## 3. What `chap eval` actually computes

### The backtest is anchored to the end of the file

`chap eval` runs an **expanding-window rolling-origin backtest**, and the splits are laid
out backwards from the last period in the dataset:

```
split_idx      = -(n_periods + (n_splits - 1) * stride + 1)
split i:  train on  [ .. period[split_idx + i*stride] ]
          predict   [ period[split_idx + i*stride + 1] .. + n_periods ]
```

Two consequences the plan depends on. **The evaluated span is
`n_periods + (n_splits - 1) * stride` periods long and always ends at the final period of
the file** — which is what makes phase E's preferred route work (§5). And **the model is
trained once by default**: `n_retrain` defaults to 1, so the estimator is fitted on the data
up to the first split point and every later split re-uses that fit, with the expanding
window passed as context at predict time rather than as training data. `n_retrain` is
configurable and is a judgment call — a candidate alternatives node for phase D.

The smoke run confirms the arithmetic exactly. Five regions, monthly data ending 2019-12,
`n_periods 3`, `n_splits 4`, `stride 1` gives an evaluated span of `3 + 3 = 6` periods,
and `smoke_eval.nc` carries `time_period` 201907 … 201912.

**Regions can be dropped before the backtest.** `validate_and_filter_dataset_for_evaluation`
removes any location whose target is entirely missing over the training period, logging
`Rejected regions:`. On the Lao data, where early years are zero-heavy and some provinces
report almost nothing, this could silently change *which* provinces the headline mean is a
mean over. Batch 3 should check the log line, not assume it is empty.

### The output

`smoke_eval.nc` is an xarray dataset with dimensions
**`(location, time_period, horizon_distance, sample)`**, plus `historical_time_period` for
plotting context. Variables: `forecast`, `observed`, `historical_observed`. Global
attributes carry `model_name`, `model_version`, `model_configuration`, `chap_version`,
`split_periods` and `org_units`.

Note the documentation's `eval-reference` page describes the dimensions as
*"time, location, quantile, split"*. The file has **`sample`, not `quantile`**, and no
`split` dimension at all. Recording the discrepancy per [[chapOrientation]]'s own
instruction that where the note and the documentation disagree the documentation wins — here
it is the documentation and the artifact that disagree, and the artifact wins.

### CRPS, exactly

`chap-core` computes CRPS in the sample-based energy form, over **all** forecast samples:

```
CRPS = E|X − y| − ½ E|X − X′|
```

per **(location, time_period, horizon_distance)** cell, aggregated by **unweighted mean**.
That triple is the platform's finest resolution; `location`, `time_period` and
`horizon_distance` are the only three dimensions a metric can be grouped by. Eighteen
metrics are registered, including `mae`, `rmse`, `crps_log1p`, and the two the plan wants
for calibration, **`coverage_10_90` and `coverage_25_75`** — so the secondary metrics §4 of
the plan asks for all come from the same call.

**Per-region and per-split values are recoverable — but not from `chap export-metrics`.**
The CLI exporter computes every metric at global aggregation only and writes one row per
`.nc` file. The breakdown is in the library: `CRPSMetric.get_metric(..., dimensions=...)`
takes any subset of the three dimensions. `describe_evaluation.py` uses it, so the score
stays chap-core's own at every resolution and only the aggregation level changes. This
mattered enough to be worth stating as a rule for the rest of the project: **we never
implement CRPS.** A metric we computed ourselves is precisely the metric we could bend
without it being visible, and the defence is not to write it.

**The split is recoverable by arithmetic**, since a rolling-origin backtest predicts
`time_period` from an origin `horizon_distance` steps back:

```
split (first predicted period) = time_period − (horizon_distance − 1)
```

`smoke_crps_by_split.csv` is produced that way and recovers exactly the four splits named in
the file's `split_periods` attribute.

**The platform's mean is a mean over cells, and with a constant stride that is the same
thing as a mean over regions and splits.** Each split contributes exactly `n_periods` cells
per region, so with `stride` constant the design is balanced: in the smoke run, 4 splits ×
3 horizons × 5 regions = 60 cells, and the mean of the four per-split means reproduces the
global CRPS to the last digit. Worth having checked, because had the design been unbalanced
the plan's headline — "mean CRPS across regions and across test splits" — would not have
been the number `chap export-metrics` prints. Two things do unbalance it: a stride that is
not constant, and **missing observations, which are dropped before the metric is computed**.
The second is a live risk on the Lao data and a reason batch 3 must characterise
completeness per province and per year.

### Cost

The whole `chap eval` invocation took **42 seconds**, of which 41 were the four splits: five
regions, a trivial model, roughly ten seconds per split. Almost all of that is
process-and-environment overhead per split rather than fitting, so it is close to a floor
rather than a typical figure — a real model adds its own fit time on top. Batch 5's budget
should be expressed in evaluation runs, and the per-run figure it needs is the one batch 4
gets from a real model, not this one.

### Reproducibility of the evaluation itself

The capture script was run twice in succession. Every metric file came back byte-identical.
`smoke_eval.nc` did not: `created_date` is a wall-clock stamp, and `split_periods` and
`org_units` are serialised from unordered sets, so they come out in a different order each
run. Nothing numeric moves — but **a byte-comparison of two `.nc` files from identical runs
reports a difference**, which `/validate cleanroom` has to know before it compares outputs
against archived ones in phase E.

## 4. The five questions batch 1 handed over

| | Question | Answer |
|---|---|---|
| 1 | Does `chap eval` accept a local model directory? | **Yes.** `--model-name` takes a local path, a GitHub URL optionally suffixed `@<commit>`, or a chapkit service URL. The smoke run used a local directory. Development can happen locally. |
| 2 | The exact form of the reported CRPS, and are per-region and per-split values recoverable? | **Sample-based energy CRPS, unweighted mean over (location, time_period, horizon_distance).** Per-region and per-horizon come from chap-core's own metric API; per-split by arithmetic from the other two. `chap export-metrics` gives the aggregate only. |
| 3 | Can the splits be arranged so every evaluated period falls inside a chosen window? | **Yes, if the window is the end of the file.** The evaluated span is `n_periods + (n_splits−1)·stride` and always ends at the last period. Phase E's preferred route is available (§5). |
| 4 | The install recipe and `chap-core`'s Python requirement | **`>=3.13,<3.14`**; recipe in §1; nothing went wrong. |
| 5 | The model contract, read from worked examples | §2, read from `minimalist_example_uv`, `ewars_template` and the `ModelTemplateConfigV2` schema in the installed source. |

## 5. What this settles for batches 3 and 4

**Phase E can use Chap's own path, and batch 3 should design for it.** Run `chap eval` on
the *full* file with the span arithmetic arranged so the evaluated span is exactly 2010:
`n_periods + (n_splits − 1)·stride = 12`. With `n_periods 3`, `stride 3`, `n_splits 4`, the
first split trains on everything up to 2009-12 and predicts 2010-01…03, and each later split
rolls forward by a quarter. Same command, same CRPS, same isolation as development, and no
script-computed metric anywhere. The fallback batch 3 was told to prepare for is not needed.

This also answers the question batch 1 raised at its §3.3: phase E re-reads the **archived
original**, because the route needs a file that contains both parts. Concatenating the two
split files would work too and would demonstrate the partition was lossless — but the
partition can be verified directly at the point it is made, and reading the archived
original keeps the number of files that must agree at one.

**Batch 3 should fix `n_periods = 3`, unless it finds a reason not to.** `chap-core` carries
an explicit special case forcing `n_periods=3` for the EWARS model, commented in the source
as a hack pending model-specific backtest parameters, and the chapkit EWARS service declares
`prediction_periods: 3` as its default. A horizon the reference model cannot run at would
mean the plan's central comparison never happens. Three is also what the documentation's
own example uses, and it divides 12 exactly, which is what makes the phase-E arrangement
above come out even.

**Batch 4 will need Docker, and Docker on this machine is not running.** The reference model
`chapkit_ewars_model` is a chapkit REST service whose `Dockerfile` builds from
`ghcr.io/dhis2-chap/chapkit-r-inla` and pins `--platform=linux/amd64` with the comment
*"R-INLA is amd64-only"*. On this arm64 Mac that means a Docker daemon plus emulation. The
older `ewars_template` route is no better: it declares `docker_env` with an R-INLA image and
is marked deprecated in favour of the chapkit one. **Neither can run until the Docker daemon
is started**, and how slowly an emulated amd64 INLA fit runs is unknown and could be the
binding cost in this project. This is not a blocker for batch 3, which needs no models at
all, and it is flagged here so it is not discovered inside batch 4.

**`github.com/chap-models` holds 37 repositories**, of which several are directly relevant to
batch 4's shortlist — `ewars_plus_template`, `auto_arima`, `mstl_arima`, `auto_regressive_monthly_v2`,
`Vietnam-dengue-superensemble`, `chap_pymc`, `chtorch`, `XGBoost_for_Malawi` — and one,
`chap-models-checker`, describes itself as running `chap eval` against every repository in
the organisation. If it publishes results, it answers [[chapOrientation]] §5's last question
(has anything been run on Lao data, and with what score) far more cheaply than re-running
them. Batch 4 should look there first.

## 6. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The analysis environment is a project-local venv at `environment/chapenv`, built by a tracked script, not the documented `uv tool install` | A tool install lands outside the repository, so nothing in the repository can rebuild it. The pinned version is the same either way. | agent-autonomous |
| CPython pinned to `3.13.0`, not `3.13` | `uv venv --python 3.13` resolved to whichever 3.13 the machine held. A version that depends on the machine is not a pin. | agent-autonomous |
| `environment.yml` and `Dockerfile` rewritten away from conda | Both were repository template text describing an environment that had never been built. A declarative layer that does not describe the resolved layer is worse than none. | agent-autonomous |
| Reconnaissance scripts live in `AI-internal/reconnaissance/`, outputs in `AI-generated/chap-reconnaissance/`, and neither is a node in the claim tree | The tree holds the analysis of dengue in Laos. "What does `chap eval` compute" is a question about the instrument; giving it a node would put a fact about the platform on the same footing as a finding about the data. The binding to script, pin and commit is kept in a `provenance.md` beside the outputs, per `AGENTS.md` §8. | agent-autonomous |
| The smoke test uses `hydromet_5_filtered.csv` and the `uv` example model, rather than the single-region dataset the documentation walks through | The question that most needed answering was whether *per-region* values are recoverable, which a single-region example cannot answer. The chosen file is five regions, monthly, with a `population` column — the shape of the Lao data. | agent-autonomous |
| **This project never implements CRPS.** Aggregation level is ours; the score is always chap-core's `CRPSMetric` | A metric we computed ourselves is the metric we could most easily bend without it being visible. The plan says as much about a hand-computed CRPS; since the library exposes the breakdown, there is no case in which we need one. | agent-autonomous |
| `smoke-work/` is not tracked | A fetched dataset, a cloned model and the ~200 MB environment chap-core builds for it, all rebuilt from pinned refs by the script. | agent-autonomous |

## 7. What is still unknown

Ordered by what it would cost to discover late.

1. **Whether `chapkit_ewars_model` runs at all on this machine**, and how long an emulated
   amd64 R-INLA fit takes per split. It is batch 4's single most important task and §2 of the
   plan has no criterion until it is answered. The Docker daemon is the first obstacle.
2. **What the Lao data does to the region filter.** Provinces whose target is entirely
   missing across the training window are dropped silently but for a log line, which would
   change what the headline mean is a mean over.
3. **What a real model costs per evaluation run.** The 42 seconds here is process overhead
   with a linear regression attached, and is a floor, not an estimate. Batch 5's budget needs
   the real figure.
4. **Whether `chap-models-checker` publishes scores**, and whether any of them are on Lao
   data.
5. **Whether the Docker layer of `environment/` builds.** Unverifiable while the daemon is
   down, and cheap to check once it is up.
6. **How model configuration reaches a model in practice.** `--model-configuration-yaml`
   and `user_options` are documented and the schema is clear, but nothing here has exercised
   them; the first configurable model in phase C will.

## 8. Compliance for this batch

- **Rule 3** — `chap-core` pinned by version, resolved into `environment/lock.txt`, and
  verified by deleting the environment and rebuilding it to an identical package set. The
  image layer is written but unbuilt, and `environment/README.md` says so rather than
  implying otherwise.
- **Rule 4** — committed before the reconnaissance run and after it, with the run named.
  The before-commit is recorded in `provenance.md`.
- **Rule 1** — every figure in this report comes from a file in
  `AI-generated/chap-reconnaissance/`. Nothing was carried from terminal output. The one
  place that discipline actually bit was the CRPS breakdown: reading a number off the screen
  and grouping it by hand would have been faster and would have produced a metric of our own.
- **Rule 5** — the `.nc`, the exported CSV and the four CRPS resolutions are all stored;
  they are small.
- **Rule 6** — no randomness. The smoke model is an ordinary least-squares fit; the project
  seed has no surface in this batch, and the two runs agreeing to the byte is the evidence.
- Rules 2, 7, 8, 9 and 10 have no surface here: nothing produced was edited, no plot, no
  report generation, no claim, no release.
- **`/validate invariants`** — run at the end of the batch; outcome in the ledger entry.

## 9. For the human

- **Docker Desktop needs to be running before batch 4.** The reference model has no
  non-Docker route, and its image is amd64-only on an arm64 machine. If emulation turns out
  to be prohibitively slow, that is exactly the *practical obstacle* the plan's §2 says to
  bring back rather than work around.
- Batch 1's §3.2 question is now moot: §2 was settled on 2026-08-23 and names
  `chapkit_ewars_model` explicitly. Its §3.3 question is answered in §5 above — phase E
  re-reads the archived original, and the route is Chap's own.
