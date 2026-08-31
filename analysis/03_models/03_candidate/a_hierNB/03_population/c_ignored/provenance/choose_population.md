# Provenance — how population enters the model — not at all

```
result:              results/population_ignored/model_option_spec.json
script:              scripts/choose_population.py
                     sha256:64457fed9c9531a32784a02bbea8fd3e8194e420f907b57138bc1cf7a30faa6f
invocation:          "$PYTHON" scripts/choose_population.py
                     (from the node directory, via run.sh, driven by
                     AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=population_ignored and COMBO_BASE=main. PYTHON is
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
node:                analysis/03_models/03_candidate/a_hierNB/03_population/c_ignored
produced:            2026-08-27
```

**What it establishes.** The population column is constant within every province
(`population_is_constant_within_province: true`, 18 distinct values over 2 592 rows),
which is what makes a pooled province intercept able to stand in for it exactly rather
than approximately. Batch 3 established that the column is a single 2020 snapshot
applied to thirteen years, so what the offset projects onto 1998 is one year's
demography.

**What the run of it established.** **23.723** mean CRPS against the main path's
23.698 — a difference of 0.025, two orders of magnitude inside the resolvable floor.
Dropping the population column changes nothing this backtest can measure. The pooled
province effect widens to sigma **1.87** from 1.27, which is the intercept absorbing
exactly what the offset had been supplying.

**What is given up** matters outside this backtest and not inside it: the model can no
longer be read as forecasting a rate, and it has nothing to say about a province it
has never seen. Every evaluated province here is in the training period, so neither
cost is paid.

alternatives-considered: `b_covariate`, which estimates the coefficient instead and scores slightly worse.
    A population series back-cast per year rather than a constant, which is the
    `02_setup/01_population` fork one level up — a different question, moving every model
    including the reference, and not this node's to answer.

agency: agent-autonomous

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/model_option_spec.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `population_ignored__holdout`
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
