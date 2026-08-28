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
commit:              PLACEHOLDER_COMMIT
instructions-commit: cf97b81
node:                01_features/a_lagBlock
produced:            2026-08-28
```

**What it establishes.** The main path's feature set: eighteen columns, and the count of rows whose lags fall before the record begins — 209 of the 2 012 fitted rows, which the boosters carry as a learned missing-value direction rather than dropping. The asymmetry between the climate lags, which start at zero, and the count lags, which start at three, is recorded with its reason: `chap eval` hands the model the covariates of the months it forecasts, so only the target is unknown.

alternatives-considered: dropping the twelve-month count lag, which would have left `b_richCalendar` to win on having a season at all rather than on how the season is described (rejected — a fork whose non-main child was built to lose says nothing); standardising the columns as candidate 1 does (rejected — a tree splits on order, so it would change nothing and would imply it did); dropping rows with a missing lag, as candidate 1's fit does (rejected — the boosters learn a direction at each split, so the rows are usable, and this is a real difference between the two families rather than a setting).
agency: agent-autonomous
