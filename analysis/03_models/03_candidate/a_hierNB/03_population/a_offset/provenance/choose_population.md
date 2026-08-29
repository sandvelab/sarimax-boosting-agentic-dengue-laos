# Provenance — how population enters the model

```
result:              results/main/model_option_spec.json
script:              scripts/choose_population.py
                     sha256:9236fb5674bde13400f7db71f005a42a05b69d1bf2f2dd6e2194daf006d3a31e
invocation:          "$PYTHON" scripts/choose_population.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so the combination is
                     `main` and results go to results/main/.)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and checks a column is positive;
                     project seed 20260822 has no surface here.
commit:              4563baf
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/03_population/a_offset
produced:            2026-08-27
```

**What it establishes.** `log(population)` is defined for every province — the largest is
**23.8 times** the smallest — so the offset can be taken, which is the premise the choice
rests on and the one thing about it that could have failed silently.

**What an offset assumes.** It is a coefficient fixed at one rather than estimated: reported
cases scale proportionally with population. That is not obviously true of a reported count,
where surveillance intensity also varies with province size, and it is exactly what the
siblings relax.

**Why this is a different node from `02_setup/01_population`.** That fork decides what the
column *contains* — the archive's constant, or a per-year back-cast — and moves every model
including the reference. This one decides what *our* model does with whatever it was handed,
and moves only ours. Batch 3's problem list had one entry; conflating them would have put a
candidate-internal choice into the subtree that re-scores the reference.

alternatives-considered: `b_covariate` (an estimated coefficient on standardised log
population) and `c_ignored` (population does not enter, so a province's level is carried
only by its own pooled intercept), retained as unbuilt siblings until batch 9. The offset is
the main path because the reference model uses one, and a candidate that differs from the
reference in both its structure and its treatment of exposure is a candidate whose gap
cannot be attributed.

agency: agent-autonomous. Batch 5 placed the fork; which child is the main path at its
defaults is this batch's.

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

This fork did not move in batch 9: its best sibling stayed inside the 0.57 CRPS floor, so
this child is still the main path. `results/main/model_option_spec.json` was regenerated
anyway, because every combination re-runs the whole candidate and because the
specification gained an `input_from_combo` field -- which records, for a combination that
inherits the common ground it did not move, where that ground came from. On `main` it
reads `main`, because `analysis/run.sh` sets no base and can inherit nothing.

The siblings built and run in batch 9 are named in their own records. Their scores from
the promoted main path: `b_covariate` −0.178 and `c_ignored` −0.025
(`AI-generated/candidate-forks/round2_promoted/fork_interaction.csv`).

script sha256: 7c509e917ddb0535ad68ee30bbcab7ed20db9b89053137329adb03ed00b16bec

agency: agent-autonomous.

---

## Batch 11 — the same choice under three further combinations

```
result:              family_hierNB/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_population.py
                     sha256:7c509e917ddb0535ad68ee30bbcab7ed20db9b89053137329adb03ed00b16bec
invocation:          bash analysis/03_models/03_candidate/a_hierNB/03_population/a_offset/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/03_population/a_offset
produced:            2026-08-28
```

**Why these combinations exist.** `family_hierNB` is candidate 1's own combination: batch 11
promoted the family fork to `c_ensemble`, so candidate 1 no longer runs under `main` and its
results live under a combination of its own, exactly as candidate 2's have since batch 10.
`family_ensemble` and `weighting_crpsWeighted` are the ensemble's two combinations, and this
step ran under them because **the pool configures its candidate-1 member from these same fork
nodes**: `c_ensemble/scripts/prepare_members.py` runs each family's fork main-path children
and that family's assembler under the running combination, rather than pointing the pool at a
configuration assembled somewhere else. That is what makes a perturbation of this fork move
the pool's member with it in phase D.

**Nothing here chose anything new.** The child that ran is the one this fork already declared
as its main path, and the specification it wrote under each of the three combinations differs
from the one it wrote under `main` in exactly one line — the `combo` field naming the
combination — because the step reads the dataset and nothing else. Verified by diff.

alternatives-considered: pointing the pool at the configuration stored under `main` instead of
assembling one under the running combination (rejected — the pool would then be configured
from a combination it is not running under, and a perturbation that moved this fork would
leave the pool's member behind).
agency: agent-autonomous

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/model_option_spec.json
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
node:                analysis/03_models/03_candidate/a_hierNB/03_population/a_offset
produced:            2026-08-29
```

**What it establishes.** The family's main-path child, re-run under each row.

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
