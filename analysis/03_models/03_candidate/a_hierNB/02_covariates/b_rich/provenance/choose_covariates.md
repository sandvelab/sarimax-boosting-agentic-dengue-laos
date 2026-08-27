# Provenance — which climate covariates, at which lags — all three at lags 1, 2 and 3

```
result:              results/covariates_rich/model_option_spec.json
script:              scripts/choose_covariates.py
                     sha256:6278fbef24e5f000a295213c797816d40a983cd838e9ab3afa1a60fdf2bd0aec
invocation:          "$PYTHON" scripts/choose_covariates.py
                     (from the node directory, via run.sh, driven by
                     AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=covariates_rich and COMBO_BASE=main. PYTHON is
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
node:                analysis/03_models/03_candidate/a_hierNB/02_covariates/b_rich
produced:            2026-08-27
```

**What it establishes.** Nine standardised climate columns instead of two, at the cost
of the first three months of every province's record: 1 961 usable rows against 2 012
for a model with no climate term at all.

**What the run of it established.** It scores **22.877** mean CRPS against the main
path's 23.698, which is the second-best combination in the second sweep and clears the
0.57 CRPS floor. Its fitted coefficients say why the covariate question is not settled:
mean temperature at lag 1 (**+0.653**) and lag 3 (**+0.594**) carry far more than
rainfall at any lag (**−0.084**, **−0.132**, **−0.013**), and the seasonal harmonics
shrink toward zero as the climate columns take over the annual cycle — `sin1` falls
from −1.235 on the main path to **−0.027** here. The two are substituting for each
other rather than adding, which is the same finding the climate-free child gives from
the other side.

**It was not promoted**, and that is a decision rather than an oversight: batch 9
applies its promotion rule once, from the sweep taken around the batch-8
configuration, where this child was worth 0.461 and inside the floor.

alternatives-considered: A per-covariate lag rather than one lag list applied to all three columns, which
    would let temperature enter at lag 1 and rainfall at lag 3; not built, because it is a
    sibling of this fork rather than an option, and because this child's coefficients are
    the evidence that would motivate it. Lag 0, rejected: a covariate contemporaneous with
    the forecast month is not available at forecast time.

agency: agent-autonomous
