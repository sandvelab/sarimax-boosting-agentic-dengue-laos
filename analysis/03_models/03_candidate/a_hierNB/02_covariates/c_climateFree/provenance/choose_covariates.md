# Provenance — which climate covariates, at which lags — none (main path from batch 9)

```
result:              results/main/model_option_spec.json
script:              scripts/choose_covariates.py
                     sha256:1d0bd98005db6e884ac0224ee34e90174dd6204ba19f0a5853edce9724e2d614
invocation:          "$PYTHON" scripts/choose_covariates.py
                     (from the node directory, via run.sh, with COMBO unset, so the
                     combination is `main` and results go to results/main/. PYTHON is
                     environment/chapenv/bin/python.)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and computes summary statistics of
                     stored columns; project seed 20260822 has no surface here.
commit:              15b8516
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/02_covariates/c_climateFree
produced:            2026-08-27
```

**What it establishes.** With no lagged column required, no row is dropped for a lag
falling before a province's record begins, so this child fits on **2 012** usable rows
against the lagged child's 1 978 — the 34 rows a two-month lag was discarding at the
start of each province's record.

**What the run of it established.** Around the batch-8 configuration, dropping the
climate covariates entirely *improved* the candidate, from 26.100 to **25.452** mean
CRPS, and that is why it was promoted. Measured again from the promoted main path the
sign reverses: putting the two lagged covariates back is worth **+0.112**
(`round2_promoted/fork_interaction.csv`), so from where the model now stands the
climate-free choice is marginally the worse one. Both numbers are inside or close to
the 0.57 CRPS floor, and the honest reading is that **this fork cannot be settled on
this dataset** — which is itself the finding, and it bears on a reference model whose
premise is that climate drives an early warning.

alternatives-considered: `b_rich`, which takes the opposite position and scores better than either around
    the promoted configuration; retained and re-run rather than adopted, because the
    promotion rule was applied once and this fork's answer moves with the others. Leaving
    the fork at `a_lagged`, which is what batch 8 did and what the reference family's own
    published Lao configuration does.

agency: agent-autonomous

---

## Batch 11 — the same choice under three further combinations

```
result:              family_hierNB/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_covariates.py
                     sha256:1d0bd98005db6e884ac0224ee34e90174dd6204ba19f0a5853edce9724e2d614
invocation:          bash analysis/03_models/03_candidate/a_hierNB/02_covariates/c_climateFree/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/02_covariates/c_climateFree
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
node:                analysis/03_models/03_candidate/a_hierNB/02_covariates/c_climateFree
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
