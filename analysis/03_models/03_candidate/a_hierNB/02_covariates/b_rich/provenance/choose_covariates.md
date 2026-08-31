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

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/model_option_spec.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `covariates_rich__holdout`
script:              unchanged; the same script, the same sha256, the same invocation
inputs:              unchanged, except that the setup chain reaches this node from
                     `01_data/01_partition/results/phase_e_1998-01_2010-12.csv` and under
                     the phase-E backtest scheme (3 periods, 4 splits, stride 3). Which of
                     the two a combination faces is decided by
                     `analysis/scripts/lib/combos.py` from the `__holdout` suffix.
environment:         unchanged
seeds:               unchanged. A component seed is derived from the project seed and the
                     component's name, and no part of that derivation is the dataset.
commit:              609e1be
instructions-commit: cf97b81
produced:            2026-08-31
alternatives-considered: none new. The holdout row runs the same alternative at the same
                     fork; what differs is the year it is scored on, which is the whole
                     design of phase E.
agency:              agent-autonomous for running it; human-set for the constraint that the
                     set was frozen before the year was opened (plan §3).
```

The artefact is named by its combination-invariant path above, which is the form
`check_invariants` reads as covering every combination the manifests name. Nothing about
what this step does changed; the record is extended because the set of combinations it runs
under grew.
