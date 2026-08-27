# Provenance — the observation model for the counts — a zero-inflated mixture

```
result:              results/observation_zeroInflated/model_option_spec.json
script:              scripts/choose_observation.py
                     sha256:7a9ef24c915a54b1f45cacd540774ce9c06c2bc127a6b6bc64a7353a72d3b350
invocation:          "$PYTHON" scripts/choose_observation.py
                     (from the node directory, via run.sh, driven by
                     AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=observation_zeroInflated and COMBO_BASE=main. PYTHON is
                     environment/chapenv/bin/python.)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     resolved from combination `main`, because this combination moved
                     only this fork and inherits the common ground it did not move.
                     Recorded in the specification as `input_from_combo`.
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and computes summary statistics of
                     stored columns; project seed 20260822 has no surface here.
commit:              15b8516
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/01_observation/b_zeroInflated
produced:            2026-08-27
```

**What it establishes.** The premise the choice rests on, computed rather than
asserted: of the **199** province-years in the development file, **41** reported nothing
at all, and of the 1 341 zero months **491** fall inside those years while **850** fall
inside years that did report. Neither count settles the question — no
column here distinguishes a true zero from an unreturned form, which is why the
observation model is a fork.

**What the run of it established.** The mixture fitted a mixing weight of **0.035**:
three and a half per cent of months attributed to a process that reports nothing
whatever transmission did. That is small, and it is the fork answering itself — the
negative binomial was already absorbing almost all of the zeros through its variance
function. The combination scored **24.129** mean CRPS against the main path's 23.698
(`AI-generated/candidate-forks/round2_promoted/fork_leaderboard.csv`), so the mixture
is worse than the two-part hurdle the main path takes, and worse than doing nothing.

alternatives-considered: `c_hurdle`, which is now the main path and takes the opposite position — that
    reporting and magnitude are two processes with their own regressions, rather than one
    process with a mixing weight. Also considered: a zero-inflation probability that
    varies with the province or the season rather than one constant. Not built, because
    the constant mixture is already the weaker of the two mixture-style answers here, and
    a richer version of a losing structure is a poor use of the batch. Recorded as not
    run rather than left absent.

agency: agent-autonomous
