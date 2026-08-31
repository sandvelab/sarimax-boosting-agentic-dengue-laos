# Provenance — the province-year effect's variance — one shared by every province

```
result:              results/yearVariance_shared/model_option_spec.json
script:              scripts/choose_year_variance.py
                     sha256:7155560d40e0e59a5926041511dec719ceb41b969a44e69b3de05a827923ef03
invocation:          "$PYTHON" scripts/choose_year_variance.py
                     (from the node directory, via run.sh, driven by
                     AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=yearVariance_shared and COMBO_BASE=main. PYTHON is
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
node:                analysis/03_models/03_candidate/a_hierNB/06_yearVariance/a_shared
produced:            2026-08-27
```

**What it establishes.** The quantity a shared variance is a single number for: across
the 17 provinces with three or more years of record, the spread of log annual totals
around a province's own average runs from **0.49** to **2.73**, a ratio of **5.6**. A
shared variance is the assertion that this ratio is 1.

**What the run of it established.** **23.749** mean CRPS against the main path's
23.698, a difference of **0.051**. Around the batch-8 configuration the same fork was
worth **1.870** CRPS and was the second-largest effect in the sweep; from the promoted
configuration it is worth nothing measurable. The hurdle had already fixed the width
problem the per-province variance was promoted to fix, and the two do not add.

It is also the only combination in the second sweep whose fit **converged** — 48 outer
rounds against the 200-round cap every province-scaled fit hits. The convergence test
is a maximum over the relative movement of every variance, and seventeen variances,
some of them near zero, keep that maximum above tolerance long after the parameters
have stopped moving in any way that matters.

alternatives-considered: `b_provinceScaled`, which is now the main path. A per-province variance shrunk
    toward a common value — a hyperprior over the seventeen variances rather than
    seventeen independent estimates — which is the standard remedy for the thin-record
    provinces this child worries about and the obvious third sibling; not built, and
    recorded as not built rather than left absent.

agency: agent-autonomous

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/model_option_spec.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `yearVariance_shared__holdout`
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
