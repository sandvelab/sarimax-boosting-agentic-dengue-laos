# Provenance — whether the recent case history enters — it does not (main path)

```
result:              results/main/model_option_spec.json
script:              scripts/choose_autoregressive.py
                     sha256:89a2f5068038495ff4fb8109a4273ed06dd3a7d64c9bf5ed3b69db656165a58a
invocation:          "$PYTHON" scripts/choose_autoregressive.py
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
node:                analysis/03_models/03_candidate/a_hierNB/05_autoregressive/a_none
produced:            2026-08-27
```

**What it establishes.** The information the main path declines to use, measured
rather than argued: within a province, log1p case counts correlate **0.701** at three
months' lag and **0.758** at twelve. Twelve months is the seasonal cycle the harmonics
already carry, so the lagged count is not obviously carrying anything the calendar
does not — which is the premise on which this child rests.

**Why this node exists at all.** Batch 8 declined to add an autoregressive term inside
the four forks it had, on the grounds that a structural term added outside the forks
would be exactly the silent judgment call this project exists to make visible. This
node is that call made visible: the term batch 8 declined is `b_lag3`, and declining
it is now a child with a claim, a premise and a score rather than a paragraph in a
report.

alternatives-considered: `b_lag3`, the term itself, built and run in this batch. A lag of one or two months,
    which correlate more strongly (0.882 and 0.791) and are not available at the third of
    Chap's three forecast months; not a fork, because a model that cannot forecast the
    third month is not a model this evaluation can score.

agency: agent-autonomous

---

## Batch 11 — the same choice under three further combinations

```
result:              family_hierNB/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_autoregressive.py
                     sha256:89a2f5068038495ff4fb8109a4273ed06dd3a7d64c9bf5ed3b69db656165a58a
invocation:          bash analysis/03_models/03_candidate/a_hierNB/05_autoregressive/a_none/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/05_autoregressive/a_none
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
