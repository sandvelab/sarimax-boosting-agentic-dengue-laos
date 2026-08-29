# Provenance — refit at every split

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_retrain.py
                     sha256:09459e8d742ae2916e7950d1d2a92c30819463456eb6cfd5139e7318d999998d
invocation:          "$PYTHON" scripts/apply_retrain.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=retrain_everySplit.)
inputs:              the analysis dataset produced by whichever child of 03_provinces ran
                     in this combination — resolved by search, not by name, and its
                     sha256 recorded in results/$COMBO/setup_spec.json as `input_sha256`
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage passes the dataset through and writes one flag.
commit:              40b6936
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/04_retrain/b_everySplit
produced:            2026-08-29
```

**What it establishes.** `n_retrain` is set to **8**, the scheme's `n_splits`, so chap-core
retrains the estimator at every split instead of once
(`results/$COMBO/setup_spec.json`). The dataset is unchanged; the flag reaches `chap eval`
through `02_setup/scripts/assemble_setup.py` and `03_models/scripts/lib/chap_eval.py`, the
same route the main path's `n_retrain = 1` takes, so no model script carries a retrain policy
of its own.

**The value is read, not typed.** chap-core rejects a parameter set with `n_retrain > n_splits`,
so the number has to be the split count of the scheme in force. It is read from
`development_scheme.n_splits` in the stored scheme file — the same key and the same file
`assemble_setup.py` reads `n_periods`, `n_splits` and `stride` from — and the source is
recorded in the specification as `n_retrain_source`. **Phase E moves both lookups together**:
when the holdout scheme replaces the development one in `assemble_setup.py`, this stage has to
follow, or the backtest would run four splits and refit eight times.

**What the fork does and does not reach.** It governs how often chap-core calls `train`. A
model that fits inside its own `predict` refits at every split whatever this flag says, which
is what the reference model does — so this fork moves the platform's behaviour and our models',
and leaves the reference where it was. The candidate-internal fork `04_fitTime` is the one that
moves ours the other way, and the two are separate rows in the manifest for that reason.

alternatives-considered: **an intermediate value**, retraining at two or four evenly spaced
points — rejected because the fork is about whether the backtest measures a model forecasting
or a model going stale, and the two ends of that answer it; intermediate values trace a curve
phase D does not report. **Leaving the flag to each model** — rejected on the grounds
`a_once` already gives: a flag set per model is a flag two models can silently disagree about,
and the comparison would then be between models evaluated differently.

agency: agent-autonomous. That `n_retrain` was an acknowledged fork rather than part of batch 3's
fixed triple is recorded in `a_once`; the value taken here, the decision to read it from the
scheme rather than type it, and the phase-E coupling note are the agent's.
information: agent-retrieved — the split count comes from the stored scheme file, and
`n_retrain`'s semantics from chap-core's own `prediction_evaluator`, which spaces the retrain
points evenly across the splits and rejects `n_retrain > n_splits`.
