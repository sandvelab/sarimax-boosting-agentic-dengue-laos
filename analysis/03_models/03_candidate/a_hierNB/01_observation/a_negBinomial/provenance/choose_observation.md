# Provenance — the observation model for the counts

```
result:              results/main/model_option_spec.json
script:              scripts/choose_observation.py
                     sha256:37b58d80427f9c198d82a194e7cf76c2d09c35a4a2bc26a34f0d9c87eb72c090
invocation:          "$PYTHON" scripts/choose_observation.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so the combination is
                     `main` and results go to results/main/.)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and computes two summary statistics
                     of a stored column; project seed 20260822 has no surface here.
commit:              4563baf
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/01_observation/a_negBinomial
produced:            2026-08-27
```

**What it establishes.** The premise the choice rests on, computed rather than asserted:
over the 2 383 observed cells of the development file the pooled variance-to-mean ratio is
**434**, against 1 for a Poisson, and **56 %** of cells are zero. A single negative binomial
is a defensible carrier for both facts; so is a mixture, and that is the fork.

**What the choice is not.** It is not a claim that no zero-generating process exists. A zero
month in a province that reported four cases in twelve years and a zero month in the capital
are the same value with different meanings, and no column in this dataset separates them.
The choice is that the model does not posit the distinction it cannot observe, and the
siblings are where positing it gets tried and scored.

alternatives-considered: `b_zeroInflated` (a mixture of a point mass at zero with a negative
binomial) and `c_hurdle` (a binary reporting model and a truncated count model fitted
separately), both retained as unbuilt siblings of this node until batch 9 builds them. Also
considered and rejected as a fork of its own: a Poisson observation model, which the ratio
above rules out on the data rather than on taste — a fork whose answer is already known is
not a fork.

agency: agent-autonomous. The plan requires a candidate from batch 4's shortlist and batch 5
placed the fork; which child is the main path at its defaults is this batch's.
