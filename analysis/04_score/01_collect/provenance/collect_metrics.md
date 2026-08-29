# Provenance — per-cell scores for every model that ran

```
result:              results/main/metrics_cell.csv
                     results/main/models.csv
script:              scripts/collect_metrics.py
                     sha256:1b9e3e5028e142ed03d27a2624b6c74a79c2cf5a933394ecd96cb562e21b6422
invocation:          "$PYTHON" scripts/collect_metrics.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              every model node's evaluation for this combination, discovered by
                     globbing analysis/03_models/**/results/main/model_spec.json rather
                     than by being listed:
                       01_baselines/01_persistence/a_empiricalChange/results/main/eval.nc
                       01_baselines/02_climatology/a_expandingWindow/results/main/eval.nc
                       02_reference/results/main/eval_repeat_{1,2,3,4}.nc
                     with the per-model input hashes in each node's own model_spec.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0.
                     The metrics are chap-core's own registered metrics, asked for by
                     id; pinning chap-core pins them.
seeds:               none. Every value is read out of a stored evaluation file; the
                     script computes no statistic of its own beyond a mean over the
                     reference's repeats. Project seed 20260822 unused.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/04_score/01_collect
produced:            2026-08-26
```

**What it establishes.** One file at the platform's finest resolution — one row per model,
province, target month and lead time, carrying CRPS, absolute error, both interval
indicators and the observed value — from which every reported figure in the project is an
aggregation. Nothing downstream re-derives a score, so no two reported numbers can disagree
about what a model scored.

**This node implements no metric.** Every value comes from chap-core's own registered metric
class, asked for by id (`crps`, `mae`, `coverage_10_90`, `coverage_25_75`) at its detailed
resolution. The only things the script chooses are the level of aggregation — the finest one
available — and the split label, recovered by the arithmetic batch 2 established,
`split = time_period − (horizon_distance − 1)`. A metric of our own would be the one we
could most easily bend without it being visible, which is why §4b rules it out for this
project.

**Models are discovered, not listed.** A model reaches this file by having run, and by no
other route. That is what makes the node indifferent to which child of a fork produced a
model — exactly one child has results under any one combination — and it is what will let
phase C add a candidate without editing the scoring node.

**The unseeded reference is carried twice over.** Each of its four repeats becomes its own
row (`reference_r1` … `reference_r4`), and a further row (`reference`) holds the per-cell
mean over them. Every repeat scored the identical cells, so the mean is an average over
draws of the same quantity rather than over different evaluations. Downstream, the mean is
the denominator of the skill score, which stops a 2 % wobble in an external model's sampler
being read as an effect of one of our own choices; the individual repeats are what say how
large that wobble was here.

alternatives-considered: the reference's repeats could have been reduced to a mean here and
the repeats discarded, which would have halved this file. Rejected — the repeat-to-repeat
spread is the noise floor of the entire comparison and it has to be recomputable from stored
scores rather than quoted from batch 4. Aggregating to province level in this node was also
rejected: the paired comparison needs per-cell rows, and an aggregation that cannot be
undone is a decision taken at the wrong time. Accumulating rows into an existing file, which
is what the vertical slice's version did, was replaced by rebuilding from the discovered
specs, because an accumulating file can hold a row from a model that no longer exists.

agency: agent-autonomous. That the metric is always chap-core's is §4b's decision from batch
2; the discovery mechanism and the treatment of the reference's repeats are this batch's,
implementing batch 5's design.
information: agent-retrieved — chap-core's metric API surface was established in batch 2.

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

```
result:              results/main/metrics_cell.csv · models.csv
                     autoregressive_lag3/metrics_cell.csv
                     autoregressive_lag3/models.csv
                     covariates_lagged/metrics_cell.csv
                     covariates_lagged/models.csv
                     covariates_rich/metrics_cell.csv
                     covariates_rich/models.csv
                     fitTime_refitAtPredict/metrics_cell.csv
                     fitTime_refitAtPredict/models.csv
                     observation_negBinomial/metrics_cell.csv
                     observation_negBinomial/models.csv
                     observation_zeroInflated/metrics_cell.csv
                     observation_zeroInflated/models.csv
                     population_covariate/metrics_cell.csv
                     population_covariate/models.csv
                     population_ignored/metrics_cell.csv
                     population_ignored/models.csv
                     yearVariance_shared/metrics_cell.csv
                     yearVariance_shared/models.csv
script:              scripts/collect_metrics.py
                     sha256:6b70fd8074a9b326efdfc2cb88d1fb50c180843a7b5906c01340395b715f7ff6
```

**Models may now be inherited, and every row says whether it was.** When `COMBO_BASE` is
set, a model node with no results under this combination is taken from the base
combination, and `models.csv` carries a `scored_under_combo` column. That is what makes a
candidate-internal fork cheap: it changed nothing the reference or the baselines face, and
the reference is unseeded, so re-running it would replace its four repeats with a different
draw and move the denominator of every comparison for reasons unrelated to the fork. On
`main` nothing is inherited, because `analysis/run.sh` sets no base.

In every one of the nine sweep combinations, `hier_nb` was scored under the combination and
the reference, persistence and climatology under `main`.

alternatives-considered: re-running the reference in each combination, which is what the
phase-D manifest does for a fork that moves the data or the evaluation; not done here,
because a candidate-internal fork moves neither, and batch 4 measured the reference's
re-run spread at sd 0.196 CRPS -- comparable to several of the fork effects being measured.
Merging a combination's own models with the base's for the same node; refused in
`combos.resolve_glob`, because a merged answer would describe an analysis that never ran.

agency: agent-autonomous.

## Batch 10 — candidate 2's three combinations

```
result:              family_boosted/metrics_cell.csv
                     family_boosted/models.csv
                     features_richCalendar/metrics_cell.csv
                     features_richCalendar/models.csv
                     head_quantileEnsemble/metrics_cell.csv
                     head_quantileEnsemble/models.csv
script:              scripts/collect_metrics.py
                     sha256:6b70fd8074a9b326efdfc2cb88d1fb50c180843a7b5906c01340395b715f7ff6
invocation:          bash analysis/04_score/01_collect/run.sh
                     with COMBO=<combination> and COMBO_BASE=main
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              6cb1163
instructions-commit: cf97b81
produced:            2026-08-28
```

In every one of the three, `boosted` was scored under the combination and the reference,
persistence, climatology and `hier_nb` under `main` — nine model rows against `main`'s
eight. Candidate 2 is a sibling family under an alternatives node, so it never appears
under `main` at all, and candidate 1 never appears under these three except as an
inherited row.

---

## Batch 11 — three further combinations, and `main` re-collected after the promotion

```
result:              family_hierNB/metrics_cell.csv
                     family_hierNB/models.csv
                     family_ensemble/metrics_cell.csv
                     family_ensemble/models.csv
                     weighting_crpsWeighted/metrics_cell.csv
                     weighting_crpsWeighted/models.csv
script:              scripts/collect_metrics.py
                     sha256:6b70fd8074a9b326efdfc2cb88d1fb50c180843a7b5906c01340395b715f7ff6
invocation:          bash analysis/04_score/01_collect/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/04_score/01_collect
produced:            2026-08-28
```

**What it establishes.** The per-cell scores of every model under the ensemble's two
combinations and under candidate 1's own. `family_ensemble` and `weighting_crpsWeighted` carry
nine model rows — the pool scored under the combination, and the reference's five rows,
persistence, climatology and `hier_nb` inherited from `main` as it stood before the promotion;
`family_hierNB` carries eight, candidate 1 under the combination and the rest inherited.
Candidate 2 appears in none of them, because it has never run under `main` or under anything
these inherit from.

**`main` was re-collected, and what it contains changed.** The promotion moved
`03_candidate`'s main path from `a_hierNB` to `c_ensemble` and candidate 1's `results/main/`
were removed with it, so `main` now holds eight model rows rather than nine: the ensemble, the
two required baselines and the reference's five. That is exactly the set `analysis/run.sh`
produces, which is the property this node's discovery-by-glob exists to give — a model is
scored by the fact of having run, and after the promotion candidate 1 does not run on the main
path.

alternatives-considered: keeping candidate 1's `main` rows on the reported leaderboard for
context (rejected — the leaderboard would then carry a row produced by a version of the tree
that no longer exists; the cross-family comparison lives in
`AI-generated/candidate-forks/families/family_leaderboard.csv`, which says under which
combination each family ran).
agency: agent-autonomous

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/metrics_cell.csv
                     results/$COMBO/models.csv
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
node:                analysis/04_score/01_collect
produced:            2026-08-29
```

**What it establishes.** Collected under all seven rows. On the five setup rows every model was re-run and `scored_under_combo` names the row itself; on the two scoring rows every model was inherited from `main`, which is what makes a re-weighting cost thirteen seconds.

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
