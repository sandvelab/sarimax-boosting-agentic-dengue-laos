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
result:              results/observation_negBinomial/model_option_spec.json
script:              scripts/choose_observation.py
                     sha256:273d690e24446702f63d2bda4457c2bbfccf1344cf6b08c9b35a712c455071fc
invocation:          "$PYTHON" scripts/choose_observation.py
                     driven by AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=observation_negBinomial and COMBO_BASE=main
```

It was the main path until this batch and is now a sibling. `results/main/` was
     removed with the promotion, because a fork with two children holding results under
     one combination is a configuration the assembler refuses -- deliberately -- and
     because those results described a main path that no longer exists. The same step,
     re-run under the combination that names what it now is, produced
     `results/observation_negBinomial/model_option_spec.json`; the premise it computes is
     unchanged, because the dataset is. Scored from the promoted main path, reverting to
     it costs **0.601** CRPS.

alternatives-considered: leaving the demoted results under `results/main/` and letting the
assembler pick between two children; refused, because it would make which model ran depend
on a glob's ordering. Renaming the directory rather than re-running the step; refused,
because the file records the combination it was produced under and the name would then
contradict its contents.

agency: agent-autonomous.
