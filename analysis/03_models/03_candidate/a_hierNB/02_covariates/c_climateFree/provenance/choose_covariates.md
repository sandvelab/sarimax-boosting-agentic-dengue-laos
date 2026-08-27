# Provenance — which climate covariates, at which lags — none (main path from batch 9)

```
result:              results/main/model_option_spec.json
script:              scripts/choose_covariates.py
                     sha256:1d0bd98005db6e884ac0224ee34e90174dd6204ba19f0a5853edce9724e2d614
invocation:          "$PYTHON" scripts/choose_covariates.py
                     (from the node directory, via run.sh, with COMBO unset, so the
                     combination is `main` and results go to results/main/. PYTHON is
                     environment/chapenv/bin/python.)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and computes summary statistics of
                     stored columns; project seed 20260822 has no surface here.
commit:              15b8516
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/02_covariates/c_climateFree
produced:            2026-08-27
```

**What it establishes.** With no lagged column required, no row is dropped for a lag
falling before a province's record begins, so this child fits on **2 012** usable rows
against the lagged child's 1 978 — the 34 rows a two-month lag was discarding at the
start of each province's record.

**What the run of it established.** Around the batch-8 configuration, dropping the
climate covariates entirely *improved* the candidate, from 26.100 to **25.452** mean
CRPS, and that is why it was promoted. Measured again from the promoted main path the
sign reverses: putting the two lagged covariates back is worth **+0.112**
(`round2_promoted/fork_interaction.csv`), so from where the model now stands the
climate-free choice is marginally the worse one. Both numbers are inside or close to
the 0.57 CRPS floor, and the honest reading is that **this fork cannot be settled on
this dataset** — which is itself the finding, and it bears on a reference model whose
premise is that climate drives an early warning.

alternatives-considered: `b_rich`, which takes the opposite position and scores better than either around
    the promoted configuration; retained and re-run rather than adopted, because the
    promotion rule was applied once and this fork's answer moves with the others. Leaving
    the fork at `a_lagged`, which is what batch 8 did and what the reference family's own
    published Lao configuration does.

agency: agent-autonomous
