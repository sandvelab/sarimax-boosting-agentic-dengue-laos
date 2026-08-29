# Provenance — the seasonal climatology baseline

```
result:              results/main/eval.nc
                     results/main/eval.log
                     results/main/model_spec.json
                     results/main/run_cost.json
                     results/main/fitted_model.json
script:              scripts/run_climatology.py
                     sha256:27e18c80c0c2d2455f837d11b0c0c81d24763e6f7e7bb2f10e7f3aca9bf1cb03
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:f8ed323be836f65a6fccc9b5a74d2f2008ad13ccf0ccd6d79c9ea209d03a8dc7
                     the model itself, scripts/climatology_model/:
                     MLproject       sha256:88629436ded4b762…
                     train.py        sha256:aefaaea693b57dfb…
                     predict.py      sha256:bcc27e087e107044…
                     pyproject.toml  sha256:ad4e90168d860af8…
                     uv.lock         sha256:9867dae7038607da…
                     (the full digests are in results/main/model_spec.json)
invocation:          "$PYTHON" scripts/run_climatology.py
                     which issues the same `chap eval` call the persistence baseline
                     goes through, with --model-name <node>/scripts/climatology_model.
                     The exact command line is the first line of results/main/eval.log.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     analysis/02_setup/results/main/setup_spec.json (the flags)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     for the platform. The model's own environment is built by chap-core
                     from its pyproject.toml and uv.lock, and resolves to the identical
                     six packages as the persistence baseline's: the two lockfiles differ
                     only in the project name and version, which is worth knowing because
                     it means the two baselines differ in what they compute and in
                     nothing else.
seeds:               none. The 1 000 draws per cell are the empirical quantile function
                     evaluated at the fixed levels (i + 0.5)/1000, not sampled from it,
                     so the model contains no randomness. Project seed 20260822 unused.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis/03_models/01_baselines/02_climatology/a_expandingWindow
produced:            2026-08-26
```

**What it establishes.** The second baseline the plan's §4 requires, implemented against the
Chap contract and evaluated through the identical path as the first, so the two are
comparable with each other and both are comparable with the reference. Its mean CRPS is in
`04_score`; nothing here quotes it, because the scoring node is where scores are computed.

**The judgment call inside it.** A climatology forecast is a distribution by construction —
a set of past Julys — so unlike the persistence baseline it needs no decision about how to
wrap uncertainty around a point. What it does need is a decision about **which window
estimates that distribution**: the training frame, so that a model fitted once really is
fitted once, or the expanding historic frame chap-core hands to `predict` at every split.
This node takes the expanding window, on the grounds that it is the same treatment the
persistence baseline gets — its anchor is the most recent observation in the historic frame,
not in the training frame — and that a baseline artificially deprived of two years of data
would overstate whatever eventually beats it. `train.py` builds and stores the frozen table
anyway, so what the alternative would have used is in the record.

**A second, smaller choice, recorded rather than buried.** A province-month with fewer than
three observed years falls back to that province's whole observed record rather than to a
pooled cross-province distribution, for the reason batch 6 gave for the other baseline:
burdens differ by four orders of magnitude, so anything pooled across provinces is set by
the capital. How often the fallback fired is printed by the run and is in
`results/main/eval.log`.

alternatives-considered: the frozen-training-window construction is the sibling
(`b_trainOnly`), built when the stability manifest needs it. A smoothed climatology — a
window of three calendar months rather than one, which is common in the seasonal forecasting
literature — was considered and not taken, because it introduces a smoothing width, and a
baseline with a tunable parameter is a competitor wearing a baseline's name. A
negative-binomial fitted to each province-month was rejected for the reason batch 6 rejected
the parametric persistence baseline: on a dataset where 56 % of observed months are zero, a
parametric family needs a floor and the floor would be doing the work.

agency: agent-autonomous. The requirement for a seasonal-climatology baseline is the plan's
(`human-set`, §4); the construction, the window fork and the fallback are the agent's.

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/eval.nc
                     results/$COMBO/eval.log
                     results/$COMBO/fitted_model.json
                     results/$COMBO/model_spec.json
                     results/$COMBO/run_cost.json
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 13, and
                     COMBO_BASE=main
combinations:        aggregate_caseWeighted, aggregate_populationWeighted, popColumn_backCast, provinces_mergeVientiane, provinces_reportingOnly, retrain_everySplit, trainingWindow_from2004
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/03_models/01_baselines/02_climatology/a_expandingWindow
produced:            2026-08-29
```

**What it establishes.** Re-run on each of the five setup rows, and **24.337 on every one**, for the same reason the persistence record gives.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`, because one script produces the same artefact
under every combination from the same invocation — the combination is a parameter, and each
file records its own in a `combo` field. `/validate invariants` accepts that form only for
combinations the stability manifest names, and its `combos` check is what keeps that set
closed, so the two checks close over each other rather than either being weakened.

alternatives-considered: a section per combination, as batches 10 and 11 wrote for the family
rows — rejected here because seven near-identical sections at twenty-odd nodes is 150 sections
that say the same sentence, and the placeholder exists precisely so that a parameterised step
is recorded once. Where a combination made this node do something *different*, that is in the
paragraph above rather than in a section of its own.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.
