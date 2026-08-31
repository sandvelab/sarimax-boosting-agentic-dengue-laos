# Provenance — how population enters the model — an estimated coefficient

```
result:              results/population_covariate/model_option_spec.json
script:              scripts/choose_population.py
                     sha256:7c1476d01deaa95e600f3937d755ba5c22038fd9bd5f683b7802026b8548de05
invocation:          "$PYTHON" scripts/choose_population.py
                     (from the node directory, via run.sh, driven by
                     AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=population_covariate and COMBO_BASE=main. PYTHON is
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
node:                analysis/03_models/03_candidate/a_hierNB/03_population/b_covariate
produced:            2026-08-27
```

**What it establishes.** The check a fixed offset never makes. Across the 17 provinces
with a record, log mean reported cases rises by **1.74** per unit of log population
(`results/population_covariate/model_option_spec.json`), where an offset is the
assertion that the number is exactly 1. So reported cases rise faster than population
across provinces and an offset is not describing this data; what the offset's fixed
coefficient of 1 costs is then an empirical question rather than an assumption, which
is the shape of a fork worth having rather than a decision.

**What the run of it established.** It scores **23.876** against the main path's
23.698, so estimating the coefficient is slightly worse than fixing it. The fitted
coefficient on standardised log population in the presence block is **1.725**, and the
province spread it leaves over is much smaller than the offset model's — sigma
**0.94** against 1.27 — which says the estimated coefficient and the pooled province
intercept are explaining the same thing.

alternatives-considered: `c_ignored`, the third child, which drops population entirely and scores between
    the two. Standardising log population on the training period rather than on the whole
    frame, which is what the model does for every other continuous column and is therefore
    not a choice this node makes.

agency: agent-autonomous

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/model_option_spec.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `population_covariate__holdout`
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
