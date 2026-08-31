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

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

```
result:              results/covariates_lagged/model_option_spec.json
script:              scripts/choose_covariates.py
                     sha256:acff2e7d91cf9ed91791fc8d4842b0323b98e5a50c2a9bd9f9aab4e8dc12b656
invocation:          "$PYTHON" scripts/choose_covariates.py
                     driven by AI-internal/useful-scripts/candidate_fork_sweep.py with
                     COMBO=covariates_lagged and COMBO_BASE=main
```

It was the main path until this batch and is now a sibling; `results/main/` was
     removed with the promotion and the step re-run as
     `results/covariates_lagged/model_option_spec.json`. The specification changed shape:
     `covariate_lag_months: 2` became `covariate_lags: [2]`, because the sibling `b_rich`
     needs several lags and one option owned by one fork cannot mean an integer for one
     child and a list for another. The model it configures is identical -- the design
     column is still `rainfall_lag2_z` -- and re-running the batch-8 configuration after
     the change reproduced batch 8's per-cell scores byte for byte. Scored from the
     promoted main path, reverting to it is worth **+0.112** CRPS: from where the model
     now stands, the two lagged covariates are marginally better than none, which is the
     opposite of what the sweep around the batch-8 configuration said.

alternatives-considered: leaving the demoted results under `results/main/` and letting the
assembler pick between two children; refused, because it would make which model ran depend
on a glob's ordering. Renaming the directory rather than re-running the step; refused,
because the file records the combination it was produced under and the name would then
contradict its contents.

agency: agent-autonomous.

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/model_option_spec.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `covariates_lagged__holdout`
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
