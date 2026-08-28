# Provenance — the observation model for the counts — a two-part hurdle (main path from batch 9)

```
result:              results/main/model_option_spec.json
script:              scripts/choose_observation.py
                     sha256:29497b824dee908cedd5948227d05a7313812613e6e6634f0eb75070d4a44a5f
invocation:          "$PYTHON" scripts/choose_observation.py
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
node:                analysis/03_models/03_candidate/a_hierNB/01_observation/c_hurdle
produced:            2026-08-27
```

**What it establishes.** The two regimes the hurdle separates are far apart on this
dataset: the mean over all observed months is **32.3** cases and the mean over the
months that reported anything is **73.9**, with 56 % of months at zero. A single mean
function has to sit between those, which is the case for splitting them.

**What the run of it established.** This is the largest single improvement any fork
of this node produced. Around the batch-8 configuration it took the candidate from
**26.100** to **23.985** mean CRPS
(`AI-generated/candidate-forks/round1_batch8Defaults/fork_leaderboard.csv`), past both
required baselines, and it is on that evidence that it was promoted. Measured again
from the promoted main path it is worth **0.601** rather than 2.115
(`round2_promoted/fork_interaction.csv`): most of what it bought around the old
configuration overlapped with what the other two promoted forks bought.

**What the construction gives up**, stated where it is implemented: the positive part
is a negative binomial on `y - 1`, a shifted count distribution rather than a
zero-truncated one. It is the cheaper of the two standard hurdles and it reuses the
module's existing fit unchanged. The cost is that the positive part's coefficients are
not comparable with the other two observation models', which is a cost this fork never
had to pay — the children are compared on what they forecast.

alternatives-considered: A zero-truncated negative binomial for the positive part instead of the shifted
    one, which is the textbook hurdle and needs a score function this module does not
    have; rejected for cost, and recorded because it is the obvious next version of this
    child rather than a discarded idea. The mixture `b_zeroInflated`, which was run and
    scored worse. The plain `a_negBinomial`, which was the main path until this batch and
    is now a sibling with its own combination.

agency: agent-autonomous

---

## Batch 11 — the same choice under three further combinations

```
result:              family_hierNB/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_observation.py
                     sha256:29497b824dee908cedd5948227d05a7313812613e6e6634f0eb75070d4a44a5f
invocation:          bash analysis/03_models/03_candidate/a_hierNB/01_observation/c_hurdle/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/01_observation/c_hurdle
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
