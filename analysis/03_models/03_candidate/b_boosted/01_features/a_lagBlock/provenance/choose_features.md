# Provenance — a_lagBlock's option specification

```
result:              family_boosted/model_option_spec.json
                     head_quantileEnsemble/model_option_spec.json
script:              scripts/choose_features.py
                     sha256:8e8f4bac751b78c71634890481584d772d88d611b5d1d40e53fa7773fe0a3d2c
invocation:          "$PYTHON" scripts/choose_features.py
                     (from the node directory, via run.sh; COMBO=family_boosted, COMBO_BASE=main)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     (inherited from combination `main`, recorded as `input_from_combo`)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; this node makes a choice and measures the premise for it.
commit:              6cb1163
instructions-commit: cf97b81
node:                01_features/a_lagBlock
produced:            2026-08-28
```

**What it establishes.** The main path's feature set: eighteen columns, and the count of rows whose lags fall before the record begins — 209 of the 2 012 fitted rows, which the boosters carry as a learned missing-value direction rather than dropping. The asymmetry between the climate lags, which start at zero, and the count lags, which start at three, is recorded with its reason: `chap eval` hands the model the covariates of the months it forecasts, so only the target is unknown.

alternatives-considered: dropping the twelve-month count lag, which would have left `b_richCalendar` to win on having a season at all rather than on how the season is described (rejected — a fork whose non-main child was built to lose says nothing); standardising the columns as candidate 1 does (rejected — a tree splits on order, so it would change nothing and would imply it did); dropping rows with a missing lag, as candidate 1's fit does (rejected — the boosters learn a direction at each split, so the rows are usable, and this is a real difference between the two families rather than a setting).
agency: agent-autonomous

---

## Batch 11 — the same choice under the ensemble's three combinations

```
result:              main/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_features.py
                     sha256:8e8f4bac751b78c71634890481584d772d88d611b5d1d40e53fa7773fe0a3d2c
invocation:          bash analysis/03_models/03_candidate/b_boosted/01_features/a_lagBlock/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              PENDING
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/b_boosted/01_features/a_lagBlock
produced:            2026-08-28
```

**Why these combinations exist.** All three are combinations of the ensemble, and this step
ran under them because **the pool configures its candidate-2 member from these same fork
nodes**. `main` is among them for the first time: batch 11 promoted `c_ensemble` to the main
path, so `analysis/run.sh` now reaches candidate 2 — as a member of the pool, through
`c_ensemble/scripts/prepare_members.py`, and not as a model on `main`'s leaderboard. There is
no `model_spec.json` under `main` at this node and there should not be: candidate 2 is a
sibling alternative and is evaluated on its own under `family_boosted`.

**Nothing here chose anything new.** The child that ran is the one this fork already declared
as its main path, and its specification under each combination differs from the one it wrote
under `family_boosted` in exactly one line — the `combo` field naming the combination.
Verified by diff.

alternatives-considered: as in the parallel record at candidate 1's forks.
agency: agent-autonomous
