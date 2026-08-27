# Provenance — the climate covariates and their lag

```
result:              results/main/model_option_spec.json
script:              scripts/choose_covariates.py
                     sha256:7de1f60262a97d3b153130aa145fb1d9fc8e31019dad15d8246deab61fbf5fc5
invocation:          "$PYTHON" scripts/choose_covariates.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so the combination is
                     `main` and results go to results/main/.)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     chap-models/ewars_plus_template, laos_eval_config.yaml — the
                     reference family's own published configuration for this country,
                     read at https://github.com/chap-models/ewars_plus_template
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and counts missing values; project
                     seed 20260822 has no surface here.
commit:              4563baf
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/02_covariates/a_lagged
produced:            2026-08-27
```

**What it establishes.** Rainfall and mean temperature at a two-month lag, with neither
column missing a single value across the 2 592 rows of the development file. Humidity is
present in the file and left out.

**Where the choice comes from, since it is not ours.** `chap-models/ewars_plus_template` —
the clean re-implementation of the reference family that batch 4 flagged and batch 5 left
unread — ships `laos_eval_config.yaml`, a configuration for *this country* naming exactly
these two covariates at `n_lags: 2`. Taking the same pair at the same lag makes our
candidate's first configuration a comparable one rather than a differently-tuned one. Two
months is also what `01_data/02_characterise` found the data supports: the lagged rank
correlation between climate and counts is broad enough that a lag chosen to the month would
be fitting noise.

alternatives-considered: `b_rich` (all three covariates at several lags each) and
`c_climateFree` (no climate at all, the seasonal term carrying the annual cycle), retained as
unbuilt siblings until batch 9. The third is the one worth stating plainly — if a
climate-free model scores the same, the covariates are decoration, and that is a finding
about the dataset rather than about the model. Also considered: selecting the lag per
province by cross-validation, as `ewars_plus_template` does by default. Rejected for the
defaults because a selection procedure inside the model is a second thing to hold constant
when comparing forks, and because the reference's own Lao configuration bypasses it.

agency: agent-on-human-assessment for the covariate pair and lag — the choice follows the
reference model the human fixed as the comparison target, read from that model's published
configuration (`agent-retrieved`). agent-autonomous for leaving humidity out at the defaults.
