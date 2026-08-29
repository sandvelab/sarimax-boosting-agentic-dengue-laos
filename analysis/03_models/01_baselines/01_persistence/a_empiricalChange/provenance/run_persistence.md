# Provenance — the persistence baseline, evaluated from inside the tree

```
result:              results/main/eval.nc
                     results/main/eval.log
                     results/main/model_spec.json
                     results/main/run_cost.json
                     results/main/fitted_model.json
script:              scripts/run_persistence.py
                     sha256:e91e4f3fd8f24b50c5ea509550a173e9e4765e307482785d53070f534e0a8c0f
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:f8ed323be836f65a6fccc9b5a74d2f2008ad13ccf0ccd6d79c9ea209d03a8dc7
                     the model itself, scripts/persistence_model/:
                     MLproject       sha256:cbd3158db12438ac…
                     train.py        sha256:8ddad23fbbced15a…
                     predict.py      sha256:e9e96b8fb0290b70…
                     pyproject.toml  sha256:d9bea910f823bf3b…
                     uv.lock         sha256:b02aa38515b1a211…
                     (the full digests are in results/main/model_spec.json, written by
                     the run before it started)
invocation:          "$PYTHON" scripts/run_persistence.py
                     which issues
                     environment/chapenv/bin/chap eval
                       --model-name <node>/scripts/persistence_model
                       --dataset-csv analysis/02_setup/results/main/analysis_dataset.csv
                       --output-file results/main/eval.nc
                       --backtest-params.n-periods 3 --backtest-params.n-splits 8
                       --backtest-params.stride 3 --backtest-params.n-retrain 1
                     with every flag read from the assembled setup, not from this script.
                     The exact command line is the first line of results/main/eval.log.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     analysis/02_setup/results/main/setup_spec.json (the flags)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     for the platform. The *model* runs in its own environment, which
                     chap-core builds from the model's pyproject.toml and uv.lock; the
                     runner verifies after the run that the lockfile chap-core built
                     from is byte-identical to the tracked one, and records the result
                     as `shipped_lockfile_is_the_one_built_from`.
seeds:               none, and this is verified rather than asserted. The 1 000 draws per
                     cell are the empirical quantile function evaluated at the fixed
                     levels (i + 0.5)/1000, not sampled from it, so the model contains no
                     randomness. Batch 6 checked byte-identity across two runs
                     (AI-generated/vertical-slice/determinism_check.json). Project seed
                     20260822 has no surface here.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis/03_models/01_baselines/01_persistence/a_empiricalChange
produced:            2026-08-26
```

**What it establishes.** The persistence baseline runs from a node, on the dataset the
setup chain assembled, at the scheme the stored scheme file fixes — and reproduces batch 6's
mean CRPS **to the last digit** (24.879338288409706 both times, over the same 371 cells).
That is the check the plan's batch 7 asks for: the vertical slice is routed through the tree
and `analysis/run.sh` reproduces its result end to end. It is also evidence that the tree
added no arithmetic of its own between the platform and the number.

**What moved and what did not.** The model directory moved from
`AI-internal/vertical-slice/persistence_model/` into this node with its git history and
without a single byte changing. What is new is everything around it: the dataset arrives
from `02_setup` instead of from the partition node directly, the backtest flags arrive from
a file instead of from constants in the runner, and the call to `chap eval` is the shared
one every model of ours goes through.

**Cost.** 28 seconds for the full eight-split backtest, 3.5 per split
(`results/main/run_cost.json`). Batch 6 measured 16 seconds for the same work; the
difference is machine load on the day and not a change in what is computed — the output is
identical.

alternatives-considered: the runner could have lived at the node in full rather than calling
a shared library. Rejected: two model nodes with their own copies of the evaluation call are
two models that can drift into being evaluated differently, and "no candidate is compared on
a metric computed a different way" is a constraint the plan states for phase C and is
cheapest to enforce structurally now. The model's own alternatives — the parametric
negative-binomial construction of the predictive distribution — are batch 6's decision,
recorded there and held as this node's unbuilt sibling.

agency: agent-autonomous. The requirement for a persistence baseline is the plan's
(`human-set`, §4); the construction of its predictive distribution was decided in batch 6;
routing it through the tree is this batch's mechanical work.

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
node:                analysis/03_models/01_baselines/01_persistence/a_empiricalChange
produced:            2026-08-29
```

**What it establishes.** Re-run on each of the five setup rows. **Its mean CRPS is 24.879 on every one of them, identical to the main path's** — the model uses neither population nor covariates, and merging a province that never reports cannot change the series it does read. An unseeded model reproducing exactly across five datasets is a determinism signal worth having.

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
