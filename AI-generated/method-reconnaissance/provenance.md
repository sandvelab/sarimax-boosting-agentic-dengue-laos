# provenance — method-reconnaissance

One section per generated file, per `AGENTS.md` §8. **Append; never overwrite an existing
section.**

These files are not results of the analysis and do not live in a claim tree node, so they
carry no node-level provenance record. The binding of file to script, invocation, pin and
commit is the same either way, and this file is where it is kept. Same split batches 2 and 3
made: how the instrument behaves is provenance, not a finding about dengue in Laos.

---

## `ewars_*` — the reference model on the development dataset — batch 4, 2026-08-23

```
script:              AI-internal/reconnaissance/run_ewars_reference.sh
                     sha256:2a3aa9bf4c00f09396f4aa9e1d2f056c461b0bc9f0719d7b800a5d3e212713a1
                     AI-internal/reconnaissance/score_evaluation.py
                     sha256:0cf4a505fd715bc7270af5cc81fd7150189495d65aba63cbf6d16fcbf148b602
invocation:          bash AI-internal/reconnaissance/run_ewars_reference.sh
                     (run from the repository root; the shell script calls score_evaluation.py)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     built by environment/install-chap.sh, resolved in environment/lock.txt
                     Docker 27.4.0 on aarch64 Darwin; the model image is linux/amd64 and runs
                     under emulation.
model:               ghcr.io/chap-models/chapkit_ewars_model
                     @sha256:abd8098f2b828d3ef9899ed136d20a4f5387f8c3abe901f386905cec166d823a
                     built from chap-models/chapkit_ewars_model commit
                     a4c2fa423d7030e6eb7c1031b066e147bbc5aaa5, at its own default configuration
inputs:              analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
backtest:            n_periods 3, n_splits 8, stride 3, n_retrain 1 — the scheme fixed in batch 3
seeds:               none available. `scripts/predict.R` in the reference calls
                     `inla.posterior.sample` and `rnbinom` and never calls `set.seed`, and the
                     chapkit service exposes no seed in its configuration schema. The project
                     seed 20260822 has no surface here, and this is a Rule 6 gap in the
                     reference rather than in this repository — measured rather than asserted,
                     in `ewars_repeatability_runs.csv`.
commit:              fb100a9
instructions-commit: 15b4ba9
produced:            2026-08-23
```

**What these files are for.** The plan's §2 makes `chapkit_ewars_model` the model to beat, so
until it has been run on this dataset the project has no criterion. This is that run: it
establishes that the reference is runnable on this machine, at what cost, over which
provinces, and with what score and calibration.

**What they are not.** Not the reported reference score. That is produced from a node inside
the claim tree once the tree exists; a result produced outside the tree does not exist. What
is settled here is that the criterion is attainable and what an evaluation run costs.

**alternatives-considered.** Three.

The reference could have been built locally from the repository (`make build`) rather than
pulled from GHCR. Rejected: the local build's own base image, `ghcr.io/dhis2-chap/chapkit-r-inla:latest`,
is unpinned, so building would have pinned our layer and left the INLA runtime floating. The
published image pins both, and its `org.opencontainers.image.revision` label records the
source commit, so the digest pins bytes and provenance at once.

The older `MLproject` route (`ewars_template`, `chap_auto_ewars`) was available and is the
same model family. Rejected: the plan names the chapkit repository specifically, the
`MLproject` one is marked deprecated in favour of it, and both need the same amd64 R-INLA
image anyway.

The repeat evaluations' `.nc` files are not kept, only their scored tables. The reference is
unseeded, so those files cannot be regenerated identically either — but four full sample
archives to document a spread that four numbers document is 40 MB for no additional
recoverable fact. `ewars_development_eval.nc` *is* kept, for exactly the reason the repeats
are not: it is the draw the reported per-region and per-split tables were computed from, and
without it those tables could not be re-derived from anything.

**agency:** agent-autonomous throughout, on aims that are the plan's. The choice of reference
model is human-set (plan §4b, 2026-08-23); the backtest scheme is from batch 3; everything
about how the run was pinned, executed and scored was the agent's.

**information:** agent-retrieved — the model repository, its published image and labels, and
the chapkit service's own `/api/v1/info`. Nothing was taken from memory.

**Reproducibility, checked rather than asserted.** The invocation was repeated four times in
total. The recipe reproduces; the numbers do not. Mean CRPS ranged 21.712–22.166 over the
four runs (sd 0.196, 0.9% of the mean), and MAE and both coverage metrics move similarly.
`ewars_repeatability_runs.csv` holds the four; `ewars_reference_spread.json` puts that
Monte Carlo spread beside the across-split and across-region spreads. This is the first
thing in this project that is *not* bit-reproducible, and the cause is in the reference
model rather than in anything here.

---

## `ewars_repeatability_*`, `ewars_reference_spread.json` — batch 4, 2026-08-23

```
script:              AI-internal/reconnaissance/ewars_reproducibility.sh
                     sha256:957ef5ca51a6027288405eb109fad9a5da5bb01bf673efa50c7bb41a1fa8ccbe
                     AI-internal/reconnaissance/reference_spread.py
                     sha256:4d303932c730d3a8cba67e8a1af6483413a758a68a17f99aec7ab26bf8961b47
invocation:          bash AI-internal/reconnaissance/ewars_reproducibility.sh
                     environment/chapenv/bin/python AI-internal/reconnaissance/reference_spread.py \
                       --detailed AI-generated/method-reconnaissance/ewars_development_crps_detailed.csv \
                       --repeats  AI-generated/method-reconnaissance/ewars_repeatability_runs.csv \
                       --out-file AI-generated/method-reconnaissance/ewars_reference_spread.json
environment:         as above
model, inputs, backtest, seeds: as above
commit:              fb100a9
instructions-commit: 15b4ba9
produced:            2026-08-23
```

**What these files are for.** The plan's §2 asks the comparison to be reported with a plain
statement of what its spread can distinguish. The reference alone answers most of that, and
answering it before any candidate of ours exists is the only time it can be answered with
nothing to gain from the answer.

**alternatives-considered.** More repeats would tighten the Monte Carlo estimate; four was
chosen because the across-split spread turned out to be an order of magnitude larger, so the
Monte Carlo term is not what binds and precision in it buys nothing. That the across-split
figure is *unpaired* — and that a paired per-cell comparison between two models will be much
tighter — is recorded in the script and in the batch report, so that the crude number is not
mistaken later for the sensitivity of the comparison phase C will actually run.

**agency:** agent-autonomous. Neither the repeatability check nor the spread decomposition
was asked for by the plan; both follow from Rule 6 and from §2's demand for an honest
statement of what the comparison can resolve.

**information:** agent-retrieved — the reference model's R source, read to establish that no
`set.seed` call exists.

---

## `chap_models_*`, `model_library_sources.txt` — the model library — batch 4, 2026-08-23

```
script:              AI-internal/reconnaissance/capture_model_library.sh
                     sha256:1174df4e5aa5277a83d16d391f804ee84fac36aa7d479e3ae52b5b3089e04079
invocation:          bash AI-internal/reconnaissance/capture_model_library.sh
environment:         environment/ (project main); `gh` and `git` from the host for retrieval
inputs:              GitHub API orgs/chap-models/repos, fetched 2026-08-23T21:42:07Z
                     chap-models/chap-models-checker at commit
                     5f21853e5f3ebd010700b9b1755250d6c69bbbb3, whose last_report.json records a
                     sweep started 2026-05-18T12:36:54Z
seeds:               none. No randomness.
commit:              fb100a9
instructions-commit: 15b4ba9
produced:            2026-08-23
```

**What these files are for.** The plan's batch 4 asks what other integrated models could be
run and whether any has been run on Lao data. Both are answered from two retrieved sources
joined into one table, rather than from prose.

**A caveat that belongs with the numbers.** The organisation listing is live and the sweep is
five months old, so eleven repositories in the organisation have no sweep row — they are
newer than the sweep, not failures. The join keeps them, with empty sweep columns, rather
than dropping them.

**alternatives-considered.** The sweep could have been re-run here rather than read. Rejected
for cost: it pulls an amd64 image per model and would take hours under emulation to answer a
question — which models still run — that this project does not depend on. What the project
does depend on is whether *the reference* runs, and that was established directly.

**agency:** agent-autonomous.

**information:** agent-retrieved. `Archive/case-source-material/trustAgenticSupplementary.md`
§S2, which names the model families to consider, is human-pointed.

---

## `native_*` — what an evaluation run costs for a model of our own kind — batch 4, 2026-08-23

```
script:              AI-internal/reconnaissance/measure_native_cost.sh
                     sha256:4574cfe4d510c1453bfb234b8994474fef6347dc7853adfd9b9c84cff03dc8e9
                     AI-internal/reconnaissance/score_evaluation.py
                     sha256:0cf4a505fd715bc7270af5cc81fd7150189495d65aba63cbf6d16fcbf148b602
invocation:          bash AI-internal/reconnaissance/measure_native_cost.sh
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0. The model
                     brings its own `uv_env`, which chap-core builds; no Docker, native arm64.
model:               dhis2-chap/minimalist_example_uv at commit
                     a67d427bfde1341be6618e64c9a4a9a2c79cec2a — the pin batch 2 used
inputs:              analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
backtest:            n_periods 3, n_splits 8, stride 3, n_retrain 1
seeds:               none. Ordinary least squares; no random draws. The project seed 20260822
                     has no surface here.
commit:              fb100a9
instructions-commit: 15b4ba9
produced:            2026-08-23
```

**What this file is for.** The reference's 149 seconds is an emulated amd64 R-INLA fit, which
is not the unit batch 5's budget needs. Our own candidates will be native Python behind an
`MLproject` with a `uv_env`, and this prices one: 56 seconds for the whole eight-split
backtest, 7 seconds per split.

**What it is not.** Not a candidate score, and it must not become one by being quoted without
its qualifier. The model is chap-core's own placeholder linear regression, which emits a
single draw per cell — which is why its CRPS (44.055) equals its MAE to the last digit and
both coverage metrics are exactly zero. It is retained because a cost figure whose run
produced numbers nobody looked at is a cost figure nobody checked.

**alternatives-considered.** A chapkit Python service (`chapkit_minimalist_example_py`) would
have priced the other route our candidates could take. Rejected for this batch: it needs a
Docker image built locally, which prices the build rather than the evaluation, and the
`MLproject`+`uv_env` route is the one the shortlist recommends.

**agency:** agent-autonomous. The plan asks batch 4 for a per-run cost figure; which model to
price with was not specified.

**information:** agent-retrieved.
