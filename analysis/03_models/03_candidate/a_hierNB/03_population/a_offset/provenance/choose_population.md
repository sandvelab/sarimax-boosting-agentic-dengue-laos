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
