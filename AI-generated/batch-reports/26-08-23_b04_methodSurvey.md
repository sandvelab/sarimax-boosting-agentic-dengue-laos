# Batch 4 — reconnaissance: methods

Generated from [[26-08-22_dengueForecastingCase]] — iteration 4

**Phase A · Status: done — produced · Executed 2026-08-23**

---

The batch that gives the project a criterion. `chapkit_ewars_model` runs on the development
dataset, on this machine, at the scheme batch 3 fixed, and its score exists. With that
number in hand the model families of [[trustAgenticSupplementary]] §S2 can be ranked against
something rather than against an intuition.

Every figure quoted below comes from a file in `AI-generated/method-reconnaissance/`, which
carries its own `README.md` and `provenance.md`. The literature is cited to sources that were
read; where only an abstract was reachable, the text says so.

## 1. The reference runs

```bash
docker run -d --platform linux/amd64 -p 8000:8000 \
  ghcr.io/chap-models/chapkit_ewars_model@sha256:abd8098f2b828d3ef9899ed136d20a4f5387f8c3abe901f386905cec166d823a
environment/chapenv/bin/chap eval \
  --model-name http://localhost:8000 --run-config.is-chapkit-model \
  --dataset-csv analysis/01_data/01_partition/results/development_1998-01_2009-12.csv \
  --backtest-params.n-periods 3 --backtest-params.n-splits 8 \
  --backtest-params.stride 3 --backtest-params.n-retrain 1 --output-file <out>.nc
```

Both open questions batches 2 and 3 carried forward are closed. **Docker was the whole
obstacle**: with the daemon up, the amd64 R-INLA image runs under emulation on this arm64
machine without a fallback, without a rebuild, and without the prohibitive slowness that was
the risk. The image is 4.7 GB and took about six minutes to pull once; after that an
eight-split backtest of the reference costs **149 seconds, 18.6 per split**
(`ewars_run_cost.json`).

**The reference is pinned by image digest**, and the image's
`org.opencontainers.image.revision` label is `a4c2fa423d7030e6eb7c1031b066e147bbc5aaa5`,
which is the head commit of the model repository. The digest therefore pins the bytes and the
source commit together, which is stronger than the `@<commit>` URL form the plan's §4b
anticipated, and the vendoring fallback it allowed for is not needed. Building locally from
that commit would have been *weaker*: the repository's `Dockerfile` builds
`FROM ghcr.io/dhis2-chap/chapkit-r-inla:latest`, so a local build pins our layer and leaves
the INLA runtime floating.

### What it scores

| Metric | Value | Nominal | Reading |
|---|---|---|---|
| **Mean CRPS** | **21.891** | — | The number to beat |
| MAE | 28.504 | — | |
| Coverage 10–90 | 0.817 | 0.80 | Very slightly wide |
| Coverage 25–75 | 0.617 | 0.50 | **Substantially too wide** |

Over **16 provinces and 371 cells**, with **1 000 posterior draws per cell**
(`ewars_development_metrics_global.csv`, `ewars_development_evaluable_cells.csv`,
`ewars_development_samples_per_cell.csv`). The run's own log names one rejected region,
`LA-VI`, and the per-province cell counts show 24 for every province except Phongsaly at 11 —
which is batch 3's prediction, arrived at there from chap-core's splitter and confirmed here
by a model actually being scored.

**The calibration line is the most useful thing in that table for phase C.** The reference is
close to nominal in the tails and materially over-dispersed in the middle: it spends
probability mass on a central interval half again as wide as it needs. CRPS rewards sharpness
subject to calibration, so a candidate that tightens the core of its predictive distribution
without losing the tails has a route to a better score that does not require better point
predictions. That is a more specific target than "try to be more accurate".

### What it does not use

The reference's default configuration takes **`rainfall` and `mean_temperature` only**
(`ewars_service_info.json`, `ewars_config_schema.json`). `mean_relative_humidity` is in the
file and is not used by it — while batch 3 found humidity correlating with cases at ρ ≈ 0.31
at lags 0–1, positive in 17 of 17 provinces. A covariate the reference ignores and the data
supports is an opening, and it costs nothing to take.

Chap logs `Column 'rainfall' is present in the dataset but not used by the model` for all
three climate columns (`ewars_dataset_warnings.txt`). **The warning is cosmetic**: it is
emitted against the service's declared `required_covariates`, which is `["population"]`
alone, while `allow_free_additional_continuous_covariates` is true and the container's own
log records the training frame arriving as `2397 rows x 9 columns` including all three. The
model gets what it asks for. Worth recording because a reader who saw only the warning would
conclude the reference had been run without climate data.

### Where the work happens is not where the contract says

`scripts/train.R` in the reference is a placeholder that writes an empty `model.rds`; the
INLA fit runs in `scripts/predict.R`, which row-binds the historic and future frames and
fits on the combination. So although `n_retrain 1` means chap-core calls `train` once, the
reference in fact **re-fits at every split**, on the expanding window.

This matters for phase C in two ways. It is the practical answer to batch 2's observation
that `n_retrain 1` leaves a single fit stale across two years of prediction — a model that
does its work in `predict` is not stale. And it means a candidate of ours that fits only in
`train` would be compared against a reference that refits eight times, which is a difference
in what is being compared rather than in model quality. Whichever convention our candidates
take must be stated, and it is a fork worth having.

## 2. The reference is not reproducible, and that bounds the whole comparison

`scripts/predict.R` calls `inla.posterior.sample` and `rnbinom` and **never calls
`set.seed`**; the chapkit service exposes no seed in its configuration schema. The reference
is therefore a draw, not a number. Four identical invocations gave:

| Run | CRPS | MAE | Coverage 10–90 | Coverage 25–75 |
|---|---|---|---|---|
| 1 | 21.891 | 28.504 | 0.817 | 0.617 |
| 2 | 22.166 | 28.617 | 0.806 | 0.606 |
| 3 | 21.805 | 28.309 | 0.814 | 0.609 |
| 4 | 21.712 | 28.373 | 0.803 | 0.623 |

sd 0.196, range 2.07 % of the mean (`ewars_repeatability_runs.csv`,
`ewars_repeatability_summary.csv`). This is the first thing in this project that is not
bit-reproducible, and **the cause is in the reference rather than in anything here** — Rule 6
can be satisfied for our own models and cannot be satisfied for the model they are measured
against. It is recorded rather than worked around, and one consequence is concrete: the
evaluation file `ewars_development_eval.nc` is kept, because it is the only record of the
draw the reported per-region and per-split tables were computed from.

### What the comparison can distinguish

The plan's §2 asks for a plain statement of this, and it can be given before any candidate
exists — which is the only time it can be given with nothing to gain from the answer.
Three spreads, from `ewars_reference_spread.json`:

| Source of spread | sd | Range |
|---|---|---|
| Monte Carlo, over identical re-runs | 0.196 | 21.71 – 22.17 |
| Across the 8 splits | 15.98 | 4.96 – 56.41 |
| Across the 16 provinces | 26.25 | 0.06 – 95.24 |

The per-split figure is the one that binds. Treating the eight splits as the unit, the
standard error of the mean CRPS is **5.65 — 26 % of the mean itself**, so an *unpaired*
comparison of two models' headline numbers cannot resolve a difference smaller than roughly
half the reference's entire score. Nothing about this design is going to produce a
significant result, and the plan said so before the numbers arrived.

**But the comparison phase C actually runs is paired**, on the same 371 cells, and a paired
comparison is far tighter than that figure suggests, because the split-to-split variation
that dominates it is common to both models. The 5.65 is the right number for "how variable is
dengue forecasting difficulty across these two years" and the wrong number for "how small a
model difference can we detect". Phase C should compute the paired per-cell difference and
its spread directly, and report that; this figure is recorded so that it is not later mistaken
for the sensitivity of the comparison.

The Monte Carlo term sets a floor of a different kind: **any advantage under about 0.4 CRPS
(2 sd) is inside the reference's own re-run noise**, and re-running the reference is the only
way to know which side of that line a small margin falls.

## 3. The cost of an evaluation run, in the unit batch 5 needs

| Model | Route | Wall clock, 8 splits | Per split |
|---|---|---|---|
| `chapkit_ewars_model` | chapkit REST, amd64 image, emulated | 149 s | 18.6 s |
| `minimalist_example_uv` | `MLproject` + `uv_env`, native arm64 | 56 s | 7.0 s |

(`ewars_run_cost.json`, `native_run_cost.json`.) **Evaluation is not the binding cost of this
project.** A full backtest of a native Python model on the real dataset costs about a minute,
so a phase-D manifest of fifty analyses is under an hour of compute, and the budget of the
plan's §9 should be expressed in *implementation* effort rather than in evaluation runs.
That is a substantial revision to what batch 5 was expected to find.

The native run's own score is reported here only because a cost figure whose numbers nobody
examined is a cost figure nobody checked: CRPS 44.055, exactly equal to its MAE, with both
coverage metrics at zero. The model emits one draw per cell, so the equality is the
definition rather than a coincidence — batch 2 established this on the example dataset and it
reproduces here. **It is not a candidate score.** It is worth one observation all the same:
an untuned linear regression scores about twice the reference's CRPS, which is the width of
the corridor phase C is working in.

## 4. What else is in the model library

`github.com/chap-models` holds **39 repositories**; the last published sweep of
`chap-models-checker` (pinned at commit `5f21853e`, swept 2026-05-18) covers **28** of them
and reports **27 pass, 1 fail** (`chap_models_library_summary.json`,
`chap_models_inventory.csv`). Eleven repositories have no sweep row because they are newer
than the sweep, not because they failed — among them `ewars_plus_template`, `mstl_arima`,
`auto_regressive_monthly_v2` and `minimalist_configurable_model`, several of which are
directly relevant.

**The sweep publishes no scores.** Its records carry status, duration, spec and log path and
no metric field of any kind, which answers [[chapOrientation]] §5's last question: there is no
existing leaderboard, on Lao data or any other. Nineteen of the swept monthly-or-any models
did run against a curated dataset which, for that covariate combination, is a **Lao subset**
— so much of the library has been *pointed at* Lao data, as a smoke test, with no number
retained.

**Twenty-three of the 28 could be run on our file as it stands** — right period type, no
geometry required, and no covariate we do not have (`runnable_on_our_data` in
`chap_models_library_summary.json`). Four are blocked by covariates we do not hold, and the
list matters:

- **`Vietnam-dengue-superensemble`** needs `nino34_anomaly`, wind speed, specific humidity,
  and urban and peri-urban land cover, and is the single failing model in the sweep. The
  superensemble family of §S2 therefore has no runnable integrated exemplar here.
- `Madagascar_ARIMA` and `epidemiar_example_model` want `precipitation`/`temperature` and
  could be reached with `--data-source-mapping`; `chapkit_rwanda_malaria_bym_model` needs
  the polygons, and `chap eval` has no flag for handing a model geometry.

Sixteen of the 28 run only because the sweep host forced `--platform=linux/amd64`, which is
now known to be workable on this machine but doubles their wall clock.

## 5. The §S2 families, against this dataset

The constraints are not negotiable and several families do not survive them: **144 monthly
periods, 16 evaluated provinces, about 2 040 training rows before the first split, three
climate covariates, a static population figure, 56 % zeros among observed months, and a
requirement for calibrated probabilistic output at a three-month horizon.**

**Bayesian hierarchical spatio-temporal (INLA and similar) — viable, and it is the
incumbent.** This is what the reference is, and the operational systems it derives from are
built the same way: EWARS-csd combines a distributed-lag non-linear model with INLA, and the
INLA family is the standard tool for exactly this shape of problem (16 units, monthly, over-
dispersed counts, partial pooling across provinces doing the work that per-province data
cannot). Its weakness on this dataset is visible in §1: over-dispersed in the middle of the
predictive distribution.

**Gradient-boosted trees on engineered climate-lag features — viable, with a caveat that is
the whole difficulty.** Trees give no predictive distribution for free, and CRPS is not
forgiving of a point forecast dressed as one — the native run above scores 44 with perfect
point-forecast machinery and zero coverage. A boosted model must be paired with an
observation model (negative binomial or Poisson–gamma with a fitted dispersion) or a quantile
ensemble. `XGBoost_for_Malawi` is a worked Chap integration of this family and can be read.

**Spatio-temporal GNNs — ruled out.** Sixteen nodes and 144 timesteps is not a graph learning
problem; the parameter count of any reasonable architecture exceeds the number of
observations by an order of magnitude, and the adjacency structure of 16 provinces carries
little information that a province-level random effect does not already carry more cheaply.
This is a genuine finding about the family rather than a budget cut, and it is recorded as
such.

**Probabilistic superensembles — viable as a *combination of our own candidates*, not as an
integration.** The one integrated exemplar cannot be run on this data (§4). But the family's
central claim is well supported: in the 2024 Infodengue-Mosqlimate Dengue Challenge, six
teams forecast five Brazilian states with machine-learning and classical statistical models,
and — in the preprint's own words — *"Model performance varied between years and locations,
and no single model consistently excelled"*, with the resulting ensembles adopted by
Brazilian public health authorities. (Abstract only; the PNAS and medRxiv full texts returned
403.) An ensemble over our own candidates costs almost nothing once the candidates exist.

**Fine-tuned time-series foundation models — low priority, and the evidence points the wrong
way for this dataset.** Recent evaluations across epidemic series report foundation models
performing strongly on influenza-like illness and similar dense series, while noting that
their *"advantage becomes less consistent in small, highly zero-inflated time series, where
conventional machine learning models can occasionally outperform more complex frameworks"*.
That is a precise description of six of our sixteen provinces. There is also no Chap
integration of one, and 2 040 rows is not a fine-tuning set — any use would be zero-shot,
with covariates handled poorly or not at all.

**Knowledge-informed thermal priors — ruled out as a backbone, retained as a covariate
transform.** The mechanistic result is that transmission suitability for *Aedes aegypti* is
**unimodal in temperature with an optimum near 29 °C**. The Lao development data spans
10.4–29.7 °C with a mean of 22.4 and a 95th percentile of 26.4 (`covariate_summary.csv`),
so essentially the whole dataset sits on the **rising limb** of that curve. A suitability
transform would there be very nearly a monotone function of temperature, and would add little
that a smooth term on temperature does not already provide. Its value on this dataset is as
one candidate transform among several in a phase-D fork, not as a mechanistic backbone. Note
also batch 3's warning that the archived schema's rainfall unit is wrong by a factor of about
thirty, which is exactly the trap an externally-sourced mechanistic threshold would fall into.

**One more finding from the comparative literature, which cuts against reading any of the
above too confidently.** The most directly comparable published comparison — AR, MA, ARIMA,
ETS, VAR, SARIMAX, SVM, random forest, XGBoost, LSTM and Prophet on weekly Rio de Janeiro
dengue, 2016–2023 — concludes that SARIMAX was the best statistical model with covariates,
LSTM with climate covariates the best machine-learning model, and combinations better than
either. But it scored on MAE, MAPE, RMSE and 95 % coverage, and it had eight years of
*weekly* data for a single city with six-year training windows. Its ranking is not
transferable to 16 provinces of monthly counts scored on CRPS, and the fact that the two
models Chap integrates from that paper (`Xiang_LSTM`, `Xiang_SVM`) declare no covariates at
all is a further reason to treat the transfer with care.

## 6. The ranked shortlist

Cost is given as implementation effort, since §3 established that evaluation is cheap. "Runs"
counts full eight-split backtests, at about one minute each for a native model.

| # | Candidate | Why | Cost | Verdict |
|---|---|---|---|---|
| 1 | **Hierarchical negative-binomial GLM**: province random effect, harmonic seasonality, distributed climate lags including humidity, log-population offset | The family that demonstrably works at this data size, and the reference's own class — so a win is attributable to the specification rather than to the paradigm. Humidity and the over-wide central interval are both concrete openings (§1). | 1–2 batches to implement; a handful of runs | **Try first** |
| 2 | **Gradient-boosted trees on engineered lag features with a negative-binomial or quantile head** | The strongest genuinely different family that survives the constraints; captures interactions and non-linear lag structure the GLM imposes by hand. The probabilistic head is where the work is, and where it can fail. | 1–2 batches; more runs, tuning is a fork not a search | **Try second** |
| 3 | **Ensemble of 1, 2 and the two required baselines** | Near-free once the components exist, and the family with the best evidence behind it in this exact setting (§5). Weighting is itself a judgment call, so it becomes a fork. | ~½ batch | **Try third** |
| 4 | **Zero-inflated / hurdle observation model** | Six of sixteen provinces are above 85 % zeros. Better framed as an alternatives fork *under* candidate 1 than as a separate family. | Small, given 1 | **Fork, not a family** |
| 5 | **Zero-shot time-series foundation model** | Genuinely different, and the one family that could surprise. But no Chap integration, poor covariate handling, and published weakness in exactly our zero-inflated regime. | 1–2 batches, most of it wrapping | **Only if budget survives** |
| — | **Spatio-temporal GNN** | 16 nodes, 144 periods. | — | **Ruled out** (§5) |
| — | **Superensemble as an integrated model** | Requires covariates we do not have; fails the sweep. | — | **Ruled out** as an integration; survives as #3 |
| — | **Mechanistic thermal backbone** | The data sits on the rising limb of the suitability curve. | — | **Ruled out** as a backbone; survives as a transform fork |

**Implementation route for all of them: an `MLproject` with a `uv_env`, native Python.** It
needs no Docker, chap-core builds the environment itself, batch 2 established the contract and
§3 priced it at 7 seconds a split. `chapkit` remains permitted by the plan's §4 and is the
better choice only for a model that needs a persistent service; nothing on this shortlist
does.

**Also worth running as leaderboard context, at almost no cost**: `chap_pymc`, `chtorch` and
`XGBoost_for_Malawi` are integrated, run on our covariates, and two of the three run natively.
They are not candidates of ours and not the criterion — the criterion is the reference — but
they cheaply establish whether the corridor between 21.9 and 44.1 is where integrated models
generally sit.

## 7. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The reference is pinned by **image digest** `sha256:abd8098f…`, not by a `@<commit>` model URL or a local build | The published image's `revision` label is the source commit, so the digest pins bytes and provenance together; a local build would leave its own `chapkit-r-inla:latest` base floating. | agent-autonomous |
| Batch 4's reference run is **reconnaissance, not the reported reference score** | The tree does not exist until batch 7, and a result produced outside the tree does not exist. What this batch establishes is that the criterion is attainable and what it costs; the score that gets reported is produced from a node. At 149 seconds the duplicated compute is not worth weakening the rule for. | agent-autonomous |
| The reference's **unseeded stochasticity is measured, not worked around** | Four repeats rather than an assertion that it is small. Rule 6 cannot be satisfied for a model whose source has no `set.seed`, and a project about tracking should say which of its numbers is a draw. | agent-autonomous |
| Four repeats, not more | The across-split spread is two orders of magnitude larger, so the Monte Carlo term is not what binds and precision in it buys nothing. | agent-autonomous |
| `ewars_development_eval.nc` is kept (10 MB); the three repeat `.nc` files are not | The reference is unseeded, so neither can be regenerated identically. The kept file is the draw the reported tables were computed from; the repeats' scored summaries preserve everything the repeats are quoted for. | agent-autonomous |
| The model-library sweep is **read at a pinned commit, not re-run** | Re-running pulls an amd64 image per model and would take hours under emulation to answer a question the project does not depend on. What it does depend on — whether the reference runs — was established directly. | agent-autonomous |
| A native-model cost figure is measured with chap-core's own placeholder model, and its score reported with the qualifier attached | The plan asks batch 4 for a per-run cost in the units batch 5 needs, and the emulated reference is the wrong unit. Reporting a cost from a run whose outputs were never examined would be a number with no check behind it. | agent-autonomous |
| The shortlist's implementation route is `MLproject` + `uv_env` rather than `chapkit` | Nothing on the shortlist needs a persistent service, and the `uv_env` route needs no Docker and no image build. `chapkit` stays permitted. | agent-autonomous |

## 8. Compliance for this batch

- **Rule 1** — every figure above comes from a file in `AI-generated/method-reconnaissance/`,
  with `provenance.md` binding each group to its script, invocation, pins, inputs, commit and
  agency. Nothing was carried from terminal output; the run cost was written to JSON by the
  script that ran the clock rather than read off one.
- **Rule 3** — the reference is pinned by digest and its source commit recorded; the analysis
  environment did not change. Docker 27.4.0 on aarch64 is now a recorded part of what the
  reference run requires, and the emulation is named rather than implied.
- **Rule 4** — committed before the run (`fb100a9`, the commit recorded in every provenance
  section) and after it, with the run named.
- **Rule 5** — the evaluation `.nc`, the platform's aggregate export, four CRPS resolutions,
  three secondary metrics per province, the cell counts, the repeatability table and the
  library inventory are all stored, in NetCDF, CSV and JSON. About 11 MB tracked; the 4.7 GB
  image, the run directories and the repeat evaluations are not.
- **Rule 6** — no randomness in anything this repository ran. The reference's randomness is
  not ours to seed, is documented in `provenance.md` as a gap in the reference, and is
  quantified in §2 rather than asserted to be small.
- **Rule 2** — nothing produced was edited. The two scripts whose first version was wrong
  were corrected at the source and the pipeline re-run; no output file was patched.
- Rules 7, 8, 9 and 10 have no surface here: no plot, no report generation, no claim entered,
  nothing released.
- **`/validate invariants`** — run at the end of the batch; outcome in the ledger entry.

## 9. What is still unknown

1. **Whether a paired per-cell comparison is tight enough to distinguish anything.** §2 gives
   the unpaired bound and argues the paired one is much better, but does not compute it — it
   cannot, with one model. The first candidate that runs settles it, and batch 5 should make
   it an explicit early check rather than a phase-D discovery.
2. **Whether our candidates should refit at predict time**, as the reference does (§1). It
   changes what is being compared and it is a fork.
3. **How model configuration reaches an `MLproject` model in practice.** Still unexercised;
   `--model-configuration-yaml` and `user_options` are documented and the chapkit route's
   config schema has now been seen, but the `MLproject` route's has not.
4. **Whether the Docker layer of `environment/` builds.** The daemon is up now and the check
   is cheap; it was not in this batch's scope.
5. **What `ewars_plus_template` is.** Newer than the sweep, describes itself as a Bayesian
   hierarchical NB+INLA model with per-district adaptive lag selection, and is therefore the
   closest published thing to shortlist candidate 1. Worth reading before implementing.

## 10. For the human

- **The project has a criterion: mean CRPS 21.891, with 10–90 coverage 0.817.** Nothing about
  the plan's §2 needs reconsidering — the reference ran at its own default configuration,
  first attempt, and the fallback route §2 provided for is not needed.
- **The reference is unseeded, and its own score moves by about 2 % between identical runs.**
  A margin under roughly 0.4 CRPS against it means nothing. This is a property of the model
  the success criterion names, discovered by measuring rather than by reading, and it is the
  kind of thing the manuscript is about.
- **Evaluation is cheap and implementation is not.** A full backtest costs about a minute for
  a native model. The plan's §9 budget was written in batches of unknown content; batch 5 can
  now write it in the unit that actually binds, which is implementation effort, and phase D's
  perturbation manifest is much less constrained than the plan assumed.
- **Docker needs to be running for any batch that touches the reference**, including phase E.
  Starting it is the only manual step in the whole recipe so far.
