# Batch 6 — the vertical slice

Generated from [[26-08-22_dengueForecastingCase]] — iteration 6

**Phase B · Status: done — produced · Executed 2026-08-26**

---

The batch that makes the modelling real. A Chap-compatible model of our own — the
persistence baseline the plan's §4 requires — runs through `chap eval` on the
development dataset, at the scheme batch 3 fixed, and produces a mean CRPS with the
per-region and per-split values behind it. Every link in the chain has now been
exercised once, with a file at every join.

Every figure below comes from a file in `AI-generated/vertical-slice/`, which carries
its own `README.md`, `provenance.md` and `criticality.md`. **None of them is a reported
result of the project**: the claim tree is erected in batch 7, and a result produced
outside the tree does not exist — the same rule batch 4 applied to the reference score.

## 1. The chain, and the file at every join

```bash
bash AI-internal/vertical-slice/run_vertical_slice.sh
```

which issues

```bash
environment/chapenv/bin/chap eval \
  --model-name AI-internal/vertical-slice/persistence_model \
  --dataset-csv analysis/01_data/01_partition/results/development_1998-01_2009-12.csv \
  --backtest-params.n-periods 3 --backtest-params.n-splits 8 \
  --backtest-params.stride 3 --backtest-params.n-retrain 1 \
  --output-file <out>.nc
```

| Link | What crosses it | The file |
|---|---|---|
| archive → development file | the 2 592 rows development may see | `development_1998-01_2009-12.csv`, hashed into `slice_inputs.sha256` |
| development file → model | the training frame and, per split, the expanding historic frame | chap-core's run directory |
| model fit → forecast | the fitted change distributions | `persistence_fitted_model.json` |
| model → platform | 371 cells × 1 000 draws | `persistence_development_eval.nc` |
| platform → metric | chap-core's own `CRPSMetric` and three secondaries | — |
| metric → the tree's contract | one row per cell, every metric, the observed value beside it | `results/main/metrics_cell.csv` |
| contract → reported figures | four aggregations, all `groupby` on that one file | `metrics_summary.csv`, `crps_by_location.csv`, `crps_by_split.csv`, `crps_by_horizon.csv` |

**Nothing crosses a join except through a file**, which is `AGENTS.md` §1 and the whole
reason the slice is worth running before anything clever is attempted. The run costs
**16 seconds, 2.0 per split** (`slice_run_cost.json`), against the 56 seconds batch 4
measured for chap-core's own example model and the 149 the emulated reference takes.

## 2. What it scored

| Metric | Persistence | Nominal | Reference, for context |
|---|---|---|---|
| **Mean CRPS** | **24.879** | — | 21.891 |
| MAE | 29.073 | — | 28.504 |
| Coverage 10–90 | 0.666 | 0.80 | 0.817 |
| Coverage 25–75 | 0.491 | 0.50 | 0.617 |

Over **371 cells, 16 provinces, 8 splits, 1 000 draws per cell**
(`results/main/metrics_summary.csv`). The reference column is batch 4's reconnaissance
figure (`ewars_development_metrics_global.csv`), and the two sit side by side here only
so the corridor is visible. **Neither number is a reported result, and the gap
between them is not this batch's finding.** What determines whether a gap of that size means
anything is the *paired* per-cell comparison, and that needs both models scored from
inside the tree, which is batch 7 (§7).

The corridor is now bounded on both sides. An untuned linear regression scores 44.055
(batch 4); a baseline that reads nothing but past values of the target scores 24.879;
the reference scores 21.891. **A candidate has to beat 24.879 to be worth implementing
and 21.891 to succeed**, and the room between them is about 3 CRPS.

### The calibration is the interesting half

The two models are miscalibrated in **opposite directions**, and that is more useful
than either number alone.

The reference is close to nominal in the tails (0.817 against 0.80) and materially too
wide in the middle (0.617 against 0.50): it spends probability mass on a central
interval half again as wide as it needs. Persistence is the reverse — its central
interval is almost exactly right (0.491 against 0.50) and its tails are much too thin
(0.666 against 0.80). It gets the ordinary month right and is caught out by the unusual
one, which is precisely what a random walk does to an epidemic series.

**And the aggregate hides how uneven this is.** Per province
(`results/main/crps_by_location.csv`), 10–90 coverage runs from **0.042 in Salavan to
1.000 in four provinces**. Salavan is a real failure — 24 cells, mean CRPS 58.6, and the
observation outside the 10–90 interval 23 times out of 24 — while Savannakhet and
Bolikhamxai are covered every time and are therefore too wide rather than well
calibrated. A single coverage figure over 16 provinces whose burdens differ by four
orders of magnitude is an average of two opposite failures. This is the same warning
batch 3 gave about the mean CRPS, now visible in a second metric and in data rather
than in prospect.

### CRPS by lead time and by split

| Horizon | Cells | Mean CRPS |
|---|---|---|
| 1 month | 124 | 16.426 |
| 2 months | 123 | 24.763 |
| 3 months | 124 | 33.447 |

The degradation with lead time is what a persistence forecast must do, and it is worth
having measured: a candidate that beats persistence at one month and not at three has
not beaten it at the horizon the evaluation actually scores.

Per split, CRPS runs **6.612 to 45.429** (`crps_by_split.csv`), against the reference's
4.957 to 56.405. The two models find the same splits hard — 2009-07 is the worst for
both — which is the observation that makes batch 4's argument for a paired comparison
concrete rather than theoretical: most of that variation is the difficulty of the
period, common to both models, and it cancels when the comparison is made cell by cell.

## 3. The model, and the judgment call inside a "trivial" baseline

The plan defines persistence as *next month = last observed month*. That is a point
forecast, and CRPS scores a distribution: batch 4 measured a single-draw model at CRPS
44.055 with both coverage metrics at zero. **How to put a predictive distribution around
a point baseline is a judgment call, and it is not a small one** — it sets the entire
calibration of one of the two numbers the project's success criterion is defined
against.

There are two published constructions and they disagree, so the choice is logged rather
than assumed:

- **Non-parametric — taken.** The last observed value plus the empirical distribution of
  past *h*-step changes, each change entered together with its negation so the
  predictive median stays exactly on the last observation, truncated at zero. This is
  the form the US COVID-19 Forecast Hub's baseline takes. It estimates nothing.
- **Parametric — not taken.** A negative binomial with mean equal to the last
  observation and dispersion fitted by maximum likelihood from recent observations, with
  the mean floored at a small constant *"to avoid zero variance in parametric predictive
  distribution"* when nothing was observed. This is the KIT baseline for the German
  COVID-19 Forecast Hub.

**The floor is what decides it on this dataset.** 56 % of observed months are zero and
six of sixteen evaluated provinces are above 85 % zeros, so the parametric form's
arbitrary constant would be setting the width of the predictive distribution in a
majority of cells — doing its most visible work exactly where the baseline matters most.
The non-parametric form needs no floor and has no tuning surface at all, which is what a
baseline should have: a baseline that can be tuned is a competitor wearing a baseline's
name.

Sources are recorded in `provenance.md` with what was read in full and what was not.

**Two implementation details that are decisions, not details.** Changes are pooled
*within* a province and never across provinces — with burdens spanning four orders of
magnitude, a pooled distribution of absolute changes would be set by Vientiane Capital
and would be absurd for Phongsaly. And the point forecast is anchored in the *historic*
frame while the spread comes from the *training* frame: under `n_retrain 1` chap-core
fits once but hands `predict` an expanding window at every split, so the anchor always
moves and the spread does not, which is the honest reading of a persistence forecast
under this backtest.

**This adds a fork to batch 5's inventory** — how uncertainty is wrapped around a point
baseline — which sits under the baseline node and moves only that leaderboard row. It is
the first fork this project found by building something rather than by reading the data.

## 4. The model's environment is pinned by a file that travels with it

Batch 2 established that `chap-core`'s `uv_env` runner builds each model's environment
itself, and drew the consequence that **pinning `chap-core` pins the platform and the
metric, not the models**. That gap is closed here for models of our own.

`persistence_model/` ships a `pyproject.toml` with exact dependency pins and
`requires-python = "==3.13.0"`, beside a `uv.lock` resolving six packages. The
interpreter is pinned to the patch for the reason batch 2 pinned the analysis
environment to the patch: a version that depends on what the building machine happens to
hold is not a specification.

**And the shipped lockfile is the one the run used** — the copy chap-core left in its
run directory is byte-identical to the tracked one. The model's environment is therefore
pinned by a file under version control rather than re-resolved at run time, which is
what Rule 3 asks for and what a model fetched from a URL at evaluation time cannot
offer.

## 5. Rule 6, satisfied by there being nothing to seed

The model contains **no randomness**. Its 1 000 draws are the empirical quantile function
evaluated at the fixed levels `(i + 0.5)/1000`, not sampled from it — a construction
chosen partly for this reason. Nearest-rank quantiles are used, so every draw is an
integer change that actually occurred in the training data.

The claim is checked rather than asserted (`verify_determinism.sh`,
`determinism_check.json`): two independent runs produced **byte-identical** contract
files and fitted model. The evaluation `.nc` is excluded from that comparison, and the
exclusion is inherited from batch 2 rather than invented for the occasion — chap-core
stamps `created_date` into the file and serialises two set-valued attributes in
run-dependent order, so identical runs differ in those bytes while nothing numeric
moves. Everything the project reports from is computed out of the `.nc` and is compared.

This is worth stating beside batch 4's finding. **The model the success criterion names
is unseeded and moves by about 2 % between identical runs; the baseline it is measured
against is bit-reproducible.** Rule 6 can be satisfied for what this project builds and
cannot be satisfied for what it is measured against, and the asymmetry is now
demonstrated at both ends rather than argued at one.

## 6. Batch 5's file contract, exercised

`results/main/` is literal. `main` is the combination id batch 5's design gives the main
analysis path, every node in the tree reads and writes under `results/$COMBO/`, and the
layout is exercised here with one child per fork — before it has to carry alternatives.

`collect_metrics.py` is the routine `analysis/04_score/01_collect` will run. It
implements no metric: every value comes from chap-core's own registered metric asked for
by id, at the platform's finest resolution, and the only things the script chooses are
the aggregation level and the split label, which is recovered by batch 2's arithmetic.
It accumulates rows per model, replacing a model's rows and keeping every other model's,
so the same call adds each later model to a shared leaderboard **without any value being
retyped between steps**. That is what the plan's phase C means by a leaderboard
maintained by a script and never typed, and it works before there is a leaderboard to
maintain.

One thing the contract gained from contact with a real evaluation: **the per-cell
coverage indicators are worth carrying**, which the design listed but did not argue for.
The per-province calibration in §2 is the most informative thing in this batch and it is
not recoverable from an aggregate.

## 7. What was deliberately not done

**The paired per-cell comparison against the reference.** Batch 4 left it as the
project's first open question and batch 5 assigned it to batch 7. Both per-cell files
now exist and the join is a few seconds of work, so this is a decision rather than an
obstacle: the comparison is between two models' scores, batch 4's reference figure was
explicitly reconnaissance, and a comparison assembled from one number produced inside
the tree and one produced outside it is not the comparison the project reports. Batch 7
scores both from nodes and computes it there. Recording the temptation is part of the
record — it was cheap, it was informative, and it was still the next batch's.

**Anything to do with the second baseline or the holdout.** Seasonal climatology is
batch 7's; the holdout stays sealed.

## 8. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The persistence baseline's predictive distribution is the **non-parametric** empirical-change construction, not the parametric negative-binomial one | Both are published and they disagree. The parametric form needs a floor on the mean to avoid a degenerate distribution at zero counts, and 56 % of observed months here are zero, so the floor would set the width of the predictive distribution in a majority of cells. The non-parametric form estimates nothing, which is what a baseline should do. | agent-autonomous, on agent-retrieved information |
| Which construction is used becomes a **fork** under the baseline node, added to batch 5's inventory | It sets the calibration of one of the two numbers the success criterion is defined against. A choice that consequential is not a preprocessing detail. It moves only that leaderboard row. | agent-autonomous |
| Changes are pooled **within** a province, with a pooled fallback below ten observed pairs | Burdens differ by four orders of magnitude; a pooled absolute-change distribution would be set by the capital. On the development data no province needed the fallback, and the fitted model records that rather than leaving it silent. | agent-autonomous |
| The draws are the empirical **quantile function at fixed levels**, not samples from it | Removes randomness from the model entirely, so Rule 6 is satisfied by there being nothing to seed and the check is byte-identity. A sampled version would have been equally valid and strictly worse to reproduce. | agent-autonomous |
| **1 000 draws per cell**, matching the reference | CRPS in the sample-based energy form is estimated from the draws, so two models compared at different draw counts are compared at different Monte Carlo resolutions. | agent-autonomous |
| The model ships a **`uv.lock` and a patch-pinned interpreter** | Batch 2 established that pinning `chap-core` does not pin the models. Verified rather than assumed: the lockfile in chap-core's run directory is byte-identical to the tracked one. | agent-autonomous |
| The slice runs **outside the claim tree**, and batch 7 moves the model into it and re-runs | The tree is erected in batch 7, and routing a model through a tree that does not exist is how the tree ends up shaped by one model. At 16 seconds the duplicated compute is not worth pre-empting a design decision for. Same reasoning batch 4 used for the reference. | agent-autonomous |
| The paired comparison against the reference is **not** computed here | It is a comparison between two models' scores, and one of the two numbers available is reconnaissance. Batch 7 produces both from nodes. | agent-autonomous |
| The evaluation `.nc` is **kept**, and flagged as the first candidate for pruning | Unlike the reference's, it is fully regenerable in 16 seconds from a deterministic model with a locked environment. Kept while the tree is being built; `criticality.md` says why and what it would cost to lose. | agent-autonomous |

## 9. Compliance for this batch

- **Rule 1** — every figure above comes from a file in `AI-generated/vertical-slice/`,
  with `provenance.md` binding each group to its script, invocation, input hashes, model
  hashes, environment, commit, instruction-set commit and agency. Three records. The
  wall-clock figure was written to JSON by the script that held the clock, not read off
  a terminal. The reference figures quoted for context in §2 come from batch 4's stored
  files and are labelled as reconnaissance where they appear.
- **Rule 2** — nothing produced was edited. The runner's first version used a `find`
  predicate BSD `find` does not accept; it was corrected at the source and the pipeline
  re-run, and no output file was patched.
- **Rule 3** — the analysis environment did not change. The *model's* environment is new
  and is pinned three ways: exact dependency versions, an interpreter pinned to the
  patch, and a lockfile verified to be the one the run used.
- **Rule 4** — committed before the run (`ced3e1a`, the commit recorded in every
  provenance record) and after it, with the run named.
- **Rule 5** — the evaluation `.nc`, the fitted model, the log, the contract file and
  four reporting resolutions are stored, in NetCDF, JSON and CSV. No pickle: the fitted
  model outlives the session, so it is JSON. 10.2 MB tracked, annotated in
  `criticality.md`; the 77 MB working directory is not.
- **Rule 6** — no randomness, and that is verified rather than asserted: two independent
  runs, byte-identical, recorded in `determinism_check.json` with the one exclusion
  named and justified.
- **Rule 7** — no plot in this batch. The per-province and per-split tables are what a
  plot would be drawn from, and batch 7 draws them once both models are in the tree.
- Rules 8, 9 and 10 have no surface here: no report generation, no claim entered,
  nothing released.
- **`/validate invariants`** — run at the end of the batch; outcome in the ledger entry.

## 10. What is still unknown

1. **Whether a paired per-cell comparison on 371 cells can separate two models.**
   Unchanged, deliberately (§7), and now one batch from being answered with both models
   in the tree. §2's observation that the two models find the same splits hard is
   encouraging for it and is not a substitute for it.
2. **How model configuration reaches an `MLproject` model.** Still unexercised — this
   model has no configuration, and chap-core wrote it an empty
   `model_configuration_for_run.yaml`. Batch 8's candidate needs it.
3. **Whether the Docker layer of `environment/` builds.** Open since batch 2; batch 7's
   scope.
4. **What `ewars_plus_template` is.** To be read before batch 8 implements candidate 1.

## 11. For the human

- **The chain works and it is fast.** 16 seconds for a full eight-split backtest of a
  native model on the real data. Batch 4's conclusion that implementation, not
  evaluation, is what binds this project is confirmed at the low end.
- **The baseline is not a straw man.** It scores 24.879 against the reference's 21.891
  and an untuned regression's 44.055, so a candidate has about 3 CRPS of room and has to
  earn it. That is a narrower corridor than the plan assumed when it called for a model
  "within reach" of the field's own.
- **A "trivial" baseline turned out to contain a real judgment call**, with two
  published answers that disagree, and the answer sets the calibration of one of the two
  numbers success is defined against. It is now a fork rather than a detail. This is the
  kind of thing the manuscript is about: the choice would have been invisible in an
  ordinary repository, made once in an afternoon and never written down.
- **Coverage varies from 0.042 to 1.000 across provinces** on a model whose aggregate
  coverage looks respectable. Batch 3 predicted that the unweighted mean over sixteen
  very unequal provinces would hide things; this is the first measurement of it hiding
  something.
