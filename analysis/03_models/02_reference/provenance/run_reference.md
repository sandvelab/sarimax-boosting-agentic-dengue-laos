# Provenance — the reference model, evaluated from inside the tree

```
result:              results/main/eval_repeat_1.nc  results/main/eval_repeat_1.log
                     results/main/eval_repeat_2.nc  results/main/eval_repeat_2.log
                     results/main/eval_repeat_3.nc  results/main/eval_repeat_3.log
                     results/main/eval_repeat_4.nc  results/main/eval_repeat_4.log
                     results/main/model_spec.json
                     results/main/run_cost.json
                     results/main/service_info.json
                     results/main/config_schema.json
script:              scripts/run_reference.py
                     sha256:7cf99ccde40c1344dbc7da2da3eb93c1fcc618af188e6cd6afca2450606e1357
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:f8ed323be836f65a6fccc9b5a74d2f2008ad13ccf0ccd6d79c9ea209d03a8dc7
invocation:          "$PYTHON" scripts/run_reference.py
                     which starts the pinned container, waits for /health, and then
                     issues four times
                     environment/chapenv/bin/chap eval
                       --model-name http://localhost:8010 --run-config.is-chapkit-model
                       --dataset-csv analysis/02_setup/results/main/analysis_dataset.csv
                       --output-file results/main/eval_repeat_<k>.nc
                       --backtest-params.n-periods 3 --backtest-params.n-splits 8
                       --backtest-params.stride 3 --backtest-params.n-retrain 1
                     with every flag read from the assembled setup. The exact command
                     line is the first line of each results/main/eval_repeat_<k>.log.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     the reference model, pinned by image digest:
                     ghcr.io/chap-models/chapkit_ewars_model@sha256:abd8098f2b828d3ef98
                     99ed136d20a4f5387f8c3abe901f386905cec166d823a
                     whose org.opencontainers.image.revision label is the source commit
                     it was built from; the label is read back out of the image at every
                     run and stored in results/main/model_spec.json rather than trusted.
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0, for
                     the platform. The *model's* environment is the pinned amd64 R-INLA
                     image, which on this arm64 machine runs under emulation. Docker must
                     be running for this node to execute, which is a dependency of
                     analysis/run.sh and is recorded in readme-at-start.md.
seeds:               **none, and none is available.** scripts/predict.R in the reference
                     calls inla.posterior.sample and rnbinom and never calls set.seed,
                     and the chapkit service exposes no seed parameter. Rule 6 cannot be
                     satisfied for this model. It is quantified instead: the evaluation
                     is repeated four times and every repeat is kept, so the spread is a
                     stored result rather than a caveat.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/03_models/02_reference
produced:            2026-08-26
```

**What it establishes.** The model the project's success criterion names, scored on the same
dataset, at the same scheme, through the same `chap eval` path as our own models — from
inside the tree. Batch 4 ran the same model as reconnaissance and said plainly that the
number was not a reported result because a result produced outside the tree does not exist.
This is the node that makes it one.

**Why four repeats.** The conclusion the root computes is a ratio whose denominator is this
model's CRPS. Batch 4 measured the reference's re-run spread at sd 0.196 CRPS over four
identical runs, about 2 % of its mean — the same order as the fork effects the stability run
exists to detect. An unaveraged denominator would put that wobble on every combination's
conclusion and it would be indistinguishable from a real effect of one of our own choices.
Four repeats put the term at roughly half the standard deviation, and they cost about ten
minutes per combination, which batch 5's budget carries.

**Why the pin is an image digest.** `chap eval --model-name <URL>` fetches at run time,
which would make the headline comparison depend on another repository's current state — the
objection the plan's §3 makes against running Chap as a hosted service, applied to the
reference model. The digest pins bytes; the image's revision label carries the source commit
those bytes were built from, so one pin fixes both, and the script reads the label back out
of the image rather than restating it.

**What is deliberately not done.** The reference is not tuned, not reconfigured, and not
perturbed. It runs at its own default configuration, which is what the plan's §2 defines
success against; a reference we had adjusted would be a model of ours wearing the field's
name. `results/main/config_schema.json` records what could have been configured and was not.

alternatives-considered: building the image locally from the source commit was rejected in
batch 4 — it would pin our layer and leave the upstream `chapkit-r-inla:latest` base
floating, which is weaker than pinning the published digest. Running the service once and
reusing it across combinations was considered and rejected for the stability run: a service
that has answered other combinations' requests is not obviously stateless, and the cost of
being sure is one container start. Taking fewer repeats was rejected as false economy given
that the denominator's noise is the size of the effects being measured; taking more was
weighed against the emulated cost and left at batch 5's four.

agency: agent-on-human-assessment. That this specific model is the reference, at its own
configuration, on development and on the holdout, is the human's decision (§4b, 2026-08-23).
The digest pin, the repeat count and the decision to quantify rather than work around the
model's unseeded sampler are the agent's.
information: agent-retrieved — the absence of `set.seed` in `predict.R` and the service's
configuration schema were read from the model itself in batch 4.

---

## Batch 13 — a container per repeat, a retry per crash, and a cleared directory

```
result:              results/$COMBO/eval_repeat_1.nc
                     results/$COMBO/eval_repeat_2.nc
                     results/$COMBO/eval_repeat_3.nc
                     results/$COMBO/eval_repeat_4.nc
                     results/$COMBO/eval_repeat_1.log
                     results/$COMBO/eval_repeat_2.log
                     results/$COMBO/eval_repeat_3.log
                     results/$COMBO/eval_repeat_4.log
                     results/$COMBO/model_spec.json
                     results/$COMBO/run_cost.json
                     results/$COMBO/service_info.json
                     results/$COMBO/config_schema.json
script:              scripts/run_reference.py
                     sha256:b0edc4d8a309253b22a689aa3065f67d7f378c436cf5b1e9337225654f0fc426
invocation:          "$PYTHON" scripts/run_reference.py
                     (from the node directory, via run.sh; COMBO set by the driver)
inputs:              analysis/02_setup/results/$COMBO/analysis_dataset.csv
                     ghcr.io/chap-models/chapkit_ewars_model@sha256:abd8098f2b828d3ef98…
environment:         environment/ (project main), plus Docker; the model is served from
                     the pinned amd64 image under emulation
seeds:               none available. The model is unseeded and exposes no seed; that is
                     quantified by four repeats rather than satisfied (Rule 6).
commit:              7035515   (rows provinces_reportingOnly and retrain_everySplit)
                     ce0eb34   (rows popColumn_backCast, provinces_mergeVientiane,
                                trainingWindow_from2004 — before the retry was added)
instructions-commit: 030bee2
node:                analysis/03_models/02_reference
produced:            2026-08-29
```

**What batch 13 measured about this model, by running it 400-odd times.** The reference
crashes intermittently: `Prediction failed: Prediction script did not create output file`,
raised when the R process inside the container exits without writing its predictions. The rate
is of order **one job in a hundred**. A `02_setup` row asks the model for 36 jobs — four
repeats of one train and eight predicts — so about a third of rows failed; `retrain_everySplit`
asks for 64 and failed twice. Four failures were observed today, at repeat 1, 2 and twice at
repeat 4, in rows that succeeded on other attempts. **It is a property of the model, not of any
row.**

**Three changes, in the order they were made.**

*One container per repeat.* The node started a single service and ran all four repeats through
it. Under `n_retrain = 8` that is 64 jobs in one container, and it degraded monotonically —
3.6, 5.6, then 7.5 minutes per repeat — before disconnecting nine jobs into the fourth. The
repeats were always meant to be independent draws; sharing a service was a convenience that
made them share accumulated state.

*Up to three attempts per repeat.* A crashed repeat is retried, and `attempts_per_repeat` in
`model_spec.json` records how many it took. This is a retry and not a selection because the
model is unseeded: every repeat is already a draw, and what is being replaced is a crash, not
an unfavourable number. Both rows re-run under it needed **one attempt for every repeat**, so
no reported figure here rests on a retry.

*The results directory is cleared before writing.* This is the one that mattered most. A failed
re-run had left three repeats from the new run, one `.nc` from the old, and the **previous**
run's `model_spec.json` and `run_cost.json` beside them — a complete-looking set whose
per-cell reference mean spanned two commits and two container lifecycles, with nothing
downstream able to detect it. `provinces_reportingOnly` was in that state, with a
`conclusion.json` describing inputs that had been partly overwritten.

alternatives-considered: **leaving the failures as failures and recording the rows as not run**
— defensible under `AGENTS.md` §4, and rejected because the failure carries no information
about the row and would have put two holes in a frozen manifest that phase E has to re-run.
**Retrying the whole row rather than the repeat** — rejected as strictly worse: it discards up
to three good draws to replace one crash. **Pruning Docker images to free space**, while the
memory hypothesis was still live — rejected, and the reason is worth recording: `image_pin()`
*records* the digest it finds and re-pulls `:latest` when the image is absent, so evicting the
image could substitute a different reference model silently. That the pin is recorded rather
than asserted is a gap this batch did not close.

agency: agent-autonomous. The crash, its rate and the mixed-directory hazard were found by
running; the three changes and the decision to retry rather than to record a hole are the
agent's.
information: agent-retrieved — the failure rate is counted from the run logs under
`results/*/eval_repeat_*.log` and `05_stability/results/logs/`, not estimated.


---

## Batch 23 — the shared evaluation library's digest, two changes late

```
result:              results/$COMBO/eval.nc, results/$COMBO/model_spec.json and the
                     artefacts beside them, as named in the section(s) above
script:              scripts/run_reference.py   (unchanged)
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:b05916bff2567b79571ba2ce27dbf26ce5cf5e6540c278ba5b570df1907688f5
invocation:          unchanged: "$PYTHON" scripts/run_reference.py, from the node
                     directory via run.sh
inputs:              unchanged in kind
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               unchanged from the section(s) above
commit:              4563baf and 49825b5 (the two changes to the library)
instructions-commit: cf97b81
node:                analysis/03_models/02_reference
produced:            2026-08-27; recorded 2026-09-01
```

**What changed in the library, twice.** At `4563baf`, batch 8: a model that takes
configuration is pointed at a **file** for it, passed to chap-core as
`--model-configuration-yaml`, and that file's path, digest and contents are written into the
model specification — so what a run was configured with is a stored artifact rather than a
command line nobody kept. At `49825b5`, batch 9: the assembled common ground is looked up
through `combos.resolve`, so a combination that moved only a candidate-internal fork inherits
`02_setup`'s output from `COMBO_BASE` and the spec records which combination answered, in a
new `setup_from_combo` field. Both are additions. Neither changes what a model computes.

**What the results on disk were produced by.** This node's `results/main/` was written at `a2cdad3`, batch 7, under the first version
of the library. It is the one node where a clean-room re-run cannot be an identity check: the
reference model is unseeded, and batch 18's four repeats moved from {21.917, 22.272, 22.385,
21.820} to {22.436, 22.473, 22.024, 22.145}, a mean of 22.270 against the archived 22.098.
That is 0.171 CRPS, inside the model's own re-run spread and a quarter of the 0.57 floor this
project declines to attribute anything below. What the library changed is how the run is
invoked and recorded, not the container it invokes, which is pinned by image digest — so the
movement is the sampler's and there is nothing here the library could have moved.

**Why four records missed it.** The library is named in the `script:` block below its
node's own runner, with a digest of its own, and nothing checked those digests until this
batch. The four records that name a superseded version are the four written before batch 9 —
this project's whole first tranche of models. The eight written afterwards name the current
one. That is the case that made the `hashes` invariant read the whole `script:` block rather
than its first line: a check on the runner alone would have passed all four while the library
underneath them had moved twice.

alternatives-considered: dropping the library from the `script:` block, so that a record
names only the file it owns and the library is covered wherever it is defined. Rejected — a
run is the runner *and* what it imports, and a record that names only half of that is
describing half a run. The opposite, hashing every module transitively imported, was rejected
as well: it is not what these records do, and adding an obligation retroactively would make
twelve more of them fail for never having promised it.

agency: agent-autonomous.
information: agent-retrieved — the digest is computed from the file, the two changes read
from the diffs, and the reproduction from the clean-room comparison.
