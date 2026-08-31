# Provenance — whether fitting happens in train or predict — refit at predict

```
result:              results/fitTime_refitAtPredict/model_option_spec.json
script:              scripts/choose_fit_time.py
                     sha256:4b0939310512e8e6376c51c4e16cdb12a6601488fcac3530968ac6f9412b4195
invocation:          "$PYTHON" scripts/choose_fit_time.py
                     (from the node directory, via run.sh, driven by
                     AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=fitTime_refitAtPredict and COMBO_BASE=main. PYTHON is
                     environment/chapenv/bin/python.)
inputs:              analysis/02_setup/results/main/setup_spec.json (the evaluation flags)
                     sha256:part of the setup this combination inherits; the file is hashed into
                     the setup's own record
                     resolved from combination `main`, because this combination moved
                     only this fork and inherits the common ground it did not move.
                     Recorded in the specification as `input_from_combo`.
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and computes summary statistics of
                     stored columns; project seed 20260822 has no surface here.
commit:              15b8516
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/04_fitTime/b_refitAtPredict
produced:            2026-08-27
```

**What it establishes.** Under the fixed backtest scheme (`n_periods` 3, `n_splits` 8,
`stride` 3, `n_retrain` 1) a train-time fit never sees the **21 months** of history
that accumulate by the last split. This child uses them, at eight fits per backtest
instead of one. It is also what the reference model does: `chapkit_ewars_model` fits
inside its predict endpoint, so under the main path the comparison carries an
unmeasured asymmetry, and measuring it is this fork's whole purpose.

**What the run of it established.** **22.825** mean CRPS against the main path's
23.698 — the best combination in the second sweep, clearing the 0.57 floor, and the
closest any model of ours has come to the reference's 22.098. It costs **108 seconds**
against the main path's 36, which is the eight fits.

**A gap in the record this child creates**, stated rather than left to be noticed:
with the fit inside predict, `train` writes a stub and the fitted objects live only in
chap-core's per-split run directories, which are working space and not tracked. So
`results/fitTime_refitAtPredict/fitted_model.json` records the configuration and the
training period and no fitted parameters. Rule 5 is satisfied for what this
configuration *has* — there is no single fitted object — but a reader looking for one
should know why it is not there.

**It was not promoted.** Batch 9 applies its promotion rule once, from the sweep taken
around the batch-8 configuration, where this child was worth 0.408 and inside the
floor. From where the model now stands it is worth 0.873 and would qualify.

alternatives-considered: `n_retrain` greater than 1, which would make chap-core itself refit between splits
    rather than the model refitting inside predict; it is the `02_setup/04_retrain` fork,
    one level up, and it moves every model including the reference — a different question
    that this child deliberately does not answer. Refitting on a rolling rather than an
    expanding window; not built, and it is the natural sibling if this child is ever
    promoted.

agency: agent-autonomous

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/model_option_spec.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `fitTime_refitAtPredict__holdout`
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
