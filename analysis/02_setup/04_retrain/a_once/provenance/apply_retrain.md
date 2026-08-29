# Provenance — the retrain policy, at the platform's default

```
result:              results/main/analysis_dataset.csv
                     results/main/setup_spec.json
script:              scripts/apply_retrain.py
                     sha256:fcf062fdf92ecebec845d38281505cd0933b650fb8e7a303d3ec3ae08b5e63fa
invocation:          "$PYTHON" scripts/apply_retrain.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/02_setup/03_provinces/a_chapFilter/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage sets a flag and passes the dataset through.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/02_setup/04_retrain/a_once
produced:            2026-08-26
```

**What it establishes.** `n_retrain = 1` reaches `chap eval` from a file. That is the whole
point of the stage: before it, the flag was a constant inside whichever script happened to
call the platform, and two model scripts could have disagreed about it without anything
noticing. Now every model reads it from the assembled setup, and a combination that changes
it changes it for all of them at once.

**What the flag does not guarantee.** `n_retrain` governs how often chap-core calls `train`.
A model that does its fitting inside `predict` refits at every split regardless — which is
what the reference model does, since its `train.R` is a placeholder and the INLA fit runs in
`predict.R` (batch 4). So this stage fixes the platform's behaviour and not the models', and
whether our own candidates refit at predict time is a separate, candidate-internal fork.
Recording that distinction here is the point: it would otherwise look as though one flag had
made all the models comparable in this respect, and it has not.

alternatives-considered: refitting at every split (`b_everySplit`) is the sibling, built in
phase D. It is the more expensive side — it multiplies every model's cost by the number of
splits — which is a reason to have measured it rather than to have assumed which side is
right. Making `n_retrain` part of batch 3's fixed triple was rejected in batch 5: the triple
fixes what is evaluated and this does not.

agency: agent-autonomous. That `n_retrain` was left at the default and flagged as a fork is
batch 3's; building it as a node so the flag travels in a file is the agent's.

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
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
node:                analysis/02_setup/04_retrain/a_once
produced:            2026-08-29
```

**What it establishes.** Ran under the rows that did not move this fork.

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
