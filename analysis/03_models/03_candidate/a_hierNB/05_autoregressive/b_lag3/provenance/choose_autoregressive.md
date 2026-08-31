# Provenance — whether the recent case history enters — the count three months back

```
result:              results/autoregressive_lag3/model_option_spec.json
script:              scripts/choose_autoregressive.py
                     sha256:7ef7586d955b56f0c2b12be3e35f6f31e6d8f429d06fdeb4556f30863dbb4191
invocation:          "$PYTHON" scripts/choose_autoregressive.py
                     (from the node directory, via run.sh, driven by
                     AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=autoregressive_lag3 and COMBO_BASE=main. PYTHON is
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
node:                analysis/03_models/03_candidate/a_hierNB/05_autoregressive/b_lag3
produced:            2026-08-27
```

**What it establishes.** The lagged count is available for **2 324** of the 2 383
observed cells at lag 3, and it costs the first three months of each province's record
at fit time: 1 959 usable rows against the main path's 2 012.

**What the run of it established.** **23.345** mean CRPS against the main path's
23.698 — a gain of 0.353, inside the 0.57 floor and therefore not attributable. Around
the batch-8 configuration the same child was worth **−0.075**, so it moved from
marginally harmful to marginally helpful without either number meaning anything.

The premise predicted this. A lag-3 correlation of 0.701 against a lag-12 correlation
of 0.758 says the recent count is telling the model roughly what month of the year it
is, and the seasonal harmonics say that already. Batch 7's observation that a
persistence baseline is level with the reference at one month's lead does not carry to
three months, which is the only lead a single model can serve here.

alternatives-considered: A separate model per horizon, each using the freshest lag available to it, which
    would let the one-month forecast use a one-month lag; rejected because Chap fits one
    model and asks it for three months, so three models would be three entries on the
    leaderboard evaluated on overlapping cells — a different comparison from the one this
    project defines. Recorded because it is the version of this idea that might work.

agency: agent-autonomous

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/model_option_spec.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `autoregressive_lag3__holdout`
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
