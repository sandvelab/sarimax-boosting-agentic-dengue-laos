# Provenance — candidate 2's evaluation

```
result:              family_boosted/eval.nc
                     family_boosted/eval.log
                     family_boosted/model_spec.json
                     family_boosted/run_cost.json
                     family_boosted/fitted_model.json
                     features_richCalendar/eval.nc
                     features_richCalendar/eval.log
                     features_richCalendar/model_spec.json
                     features_richCalendar/run_cost.json
                     features_richCalendar/fitted_model.json
                     head_quantileEnsemble/eval.nc
                     head_quantileEnsemble/eval.log
                     head_quantileEnsemble/model_spec.json
                     head_quantileEnsemble/run_cost.json
                     head_quantileEnsemble/fitted_model.json
script:              scripts/run_boosted.py
                     sha256:b3a708e4b8457cdadcdf44345c701cd5aa21ad4644ab52a3d71979fd5b70f916
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:b05916bff2567b79571ba2ce27dbf26ce5cf5e6540c278ba5b570df1907688f5
model:               scripts/boosted_model/ — the Chap model contract directory
                     MLproject       sha256:8be1d6513c59c4bf966587a6a02da7b28f32e6ddbbb0ec14b2ddba65194593c2
                     boosted.py      sha256:fc2f86efbde8dbad1c697ca71969f36e4a1c9d5d3c8f824fa9f47dc451d7303b
                     train.py        sha256:1c787a11fd59938042235a6c50412f544640a97fc447309d16c5953fa1774aff
                     predict.py      sha256:44e65d9b4ec69d4f89f0d6da87f8f34aedf1e5259548042b1108f6d5ba8cfa3d
                     pyproject.toml  sha256:d2f5a08403481c6921069341c628cf39297c97351ad916fb86ad7b9bd948f5d1
                     uv.lock         sha256:794f21a324e02564a6768c66b2fadef613f78bc136a41420d1f483965e83393c
                     (the same six hashes are in each model_spec.json, written before the
                     run, and chap-core reports that the lockfile it built from is the one
                     shipped here)
invocation:          "$PYTHON" scripts/run_boosted.py
                     which calls environment/chapenv/bin/chap eval
                       --model-name scripts/boosted_model
                       --dataset-csv analysis/02_setup/results/main/analysis_dataset.csv
                       --backtest-params.n-periods 3 --n-splits 8 --stride 3 --n-retrain 1
                       --model-configuration-yaml results/<combo>/model_configuration.yaml
                     with the flags read from 02_setup rather than named here.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     (inherited from combination `main` through COMBO_BASE, and recorded
                     as inherited in each model_spec.json)
                     results/<combo>/model_configuration.yaml
environment:         environment/ (project main) for the driver; the model's own
                     environment is built by chap-core from scripts/boosted_model/uv.lock
                     — CPython 3.13.0 with numpy 2.5.2, pandas 3.0.5, pyyaml 6.0.3 and
                     scikit-learn 1.7.2. **This is the first model in the project to need
                     a dependency beyond the three the others share**; the pin is exact and
                     travels with the model.
seeds:               component seed 1877199108, derived as above and carried in the
                     configuration file. It seeds the NumPy generator every forecast draw
                     comes from, and the boosters' random_state. The fit draws nothing:
                     early stopping is disabled and the round count is fixed before the
                     final fit, so two fits on one frame are identical. Verified by
                     AI-internal/useful-scripts/verify_model_determinism.sh, which reports
                     `identical` for this model on metrics_cell.csv, models.csv and
                     fitted_model.json.
commit:              6cb1163
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/b_boosted
produced:            2026-08-28
```

**What it establishes.** The project's best development score: mean CRPS **20.771** over the
371 evaluated cells, against the reference model's 22.098 and candidate 1's 23.698. The
paired difference against the reference is −1.327 with a split-clustered standard error of
1.110, and it clears the 0.565 CRPS floor the reference's own unseeded re-runs occupy.

**Why the fitted model is JSON and not a pickle.** Rule 5 forbids a language-specific pickle
for anything outliving the session, and this object outlives it — chap-core writes it
between `train` and `predict` and `chap_eval.py` copies it into `results/`. So the
boosted ensembles are stored as trees with their split features, thresholds, missing-value
directions and leaf values, and `boosted.py` walks that structure itself. Because that is a
second prediction path, and a second path can disagree, the fit checks it: each booster's
stored form is evaluated on the training rows and compared with scikit-learn's own
prediction, and the run fails if they differ. The largest difference recorded on any of the
three combinations is **0.0**. The stored model was also read back with scikit-learn blocked
from importing, which is the property the storage format exists to give.

**What was inherited rather than recomputed.** These combinations moved a model of ours and
nothing the reference or the baselines face, so the dataset, the setup choices and the other
four models' scores are taken from combination `main` and every one of those inheritances is
named in the file that reports it. The reference in particular is not re-run: it is unseeded,
and re-running it would replace its four repeats with a different draw and move the
denominator of every comparison for reasons unrelated to this candidate.

alternatives-considered: writing our own gradient-boosting implementation, as candidate 1's
GLM fitter is written (rejected — boosting is binning, split finding, shrinkage and a
stopping rule, each with choices in it, and a hand-written version would be both unreadable
and incomparable with anything published; scikit-learn's is the standard one, pinned exactly,
and documented where a reader can check it); pickling the fitted boosters (rejected under
Rule 5); refitting inside `predict` as candidate 1's `04_fitTime` fork allows (rejected —
with the ladder head the fit is fifteen boosters and two passes, so refitting per split
multiplies the backtest by the number of splits to answer a question the cheaper family has
already answered, and batch 21 found refit-at-predict is the configuration under which a
model has no stored fitted object at all); making the boosting hyper-parameters forks
(rejected — that enumerates a tuning grid whose siblings all have to be re-run in phase D and
on the holdout, to answer a question about tuning rather than about a judgment call an
analyst would plausibly make differently; logged here and in the node's claim instead, as
`AGENTS.md` §3 permits).
agency: agent-autonomous

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/eval.nc
                     results/$COMBO/eval.log
                     results/$COMBO/model_spec.json
                     results/$COMBO/run_cost.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that reaches this node -- here `family_boosted__holdout`
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
