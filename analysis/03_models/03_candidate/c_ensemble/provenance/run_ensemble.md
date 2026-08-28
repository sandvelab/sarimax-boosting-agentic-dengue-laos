# Provenance — candidate 3's evaluation

```
result:              main/eval.nc
                     main/eval.log
                     main/model_spec.json
                     main/run_cost.json
                     main/fitted_model.json
                     family_ensemble/eval.nc
                     family_ensemble/eval.log
                     family_ensemble/model_spec.json
                     family_ensemble/run_cost.json
                     family_ensemble/fitted_model.json
                     weighting_crpsWeighted/eval.nc
                     weighting_crpsWeighted/eval.log
                     weighting_crpsWeighted/model_spec.json
                     weighting_crpsWeighted/run_cost.json
                     weighting_crpsWeighted/fitted_model.json
script:              scripts/run_ensemble.py
                     sha256:9b5fd0e989d3590add5f22aee409c06e0be941c6fb6ba3d92379dd8f621fc5f1
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:b05916bff2567b79571ba2ce27dbf26ce5cf5e6540c278ba5b570df1907688f5
model:               scripts/ensemble_model/ — the Chap model contract directory
                     MLproject       sha256:a57e3ebb170013448f53c50a059026862e7501ab9fa0378a451e396315fda55f
                     ensemble.py     sha256:7cb23102a9b842af7292ef3d2668b7fa6c92f62e4a61ed3a5360c85c373b593f
                     train.py        sha256:5940a548ecbb47ecdcb7e2b55a0557b4b7adb665d9f64be47c61edfa144c74da
                     predict.py      sha256:a85b011a07646c41677f3d148154904db78b22fd0f5ccc0ad5fc7a5d98a55f5b
                     pyproject.toml  sha256:fc412bb99299ade094058c4ed9b16aede511f287b6f6a152d2f8e7fbbc08992b
                     uv.lock         sha256:119926445193585c77bc6b26bc3c0dd2be9f302d0958fa5cee4b9ea2c6dda053
                     (the same six hashes are in each model_spec.json, written before the
                     run, and chap-core reports that the lockfile it built from is the one
                     shipped here)
members:             the four models the pool contains are not part of this directory. They
                     are run through their own entry points, from their own nodes, and the
                     sha256 of every file in each of their contract directories is in
                     results/<combo>/members.json, whose own sha256 is in the
                     configuration this run was given.
invocation:          "$PYTHON" scripts/run_ensemble.py
                     which calls environment/chapenv/bin/chap eval
                       --model-name scripts/ensemble_model
                       --dataset-csv analysis/02_setup/results/main/analysis_dataset.csv
                       --backtest-params.n-periods 3 --n-splits 8 --stride 3 --n-retrain 1
                       --model-configuration-yaml results/<combo>/model_configuration.yaml
                     with the flags read from 02_setup rather than named here.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     results/<combo>/model_configuration.yaml
                     results/<combo>/members.json
environment:         environment/ (project main) for the driver; the model's own
                     environment is built by chap-core from scripts/ensemble_model/uv.lock
                     — CPython 3.13.0 with numpy 2.5.2, pandas 3.0.5, pyyaml 6.0.3 and
                     scikit-learn 1.7.2. It is the **union of its members'** environments,
                     because the pool runs its members in its own interpreter;
                     prepare_members.py compares every member's pins against this file and
                     fails the run if one asks for a version it does not carry.
seeds:               component seed 1648567750, derived as above and carried in the
                     configuration file. It seeds the pool's own draw: which of each
                     member's thousand samples the pool takes, and in what order they are
                     written. How many each member contributes is not drawn at all — it is
                     the largest-remainder allocation of the weights. The members' draws
                     come from the members' own seeds through their own entry points.
                     Verified by AI-internal/useful-scripts/verify_model_determinism.sh,
                     which names this candidate by its own node path and reports
                     `identical` on metrics_cell.csv, models.csv and fitted_model.json.
commit:              5e1de04
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-28
```

**What it establishes.** The project's reported model and its reported conclusion. Mean CRPS
**18.817** over the 371 evaluated cells against the reference model's 22.098 — skill
**+0.1485**, the first positive figure this project has produced — and ahead of both required
baselines. The paired difference is **−3.282** with a split-clustered standard error of
**1.726**, which is 1.90 standard errors and nearly six times the 0.565 CRPS floor the
reference's own unseeded re-runs occupy. It does not separate the two models and is not
reported as doing so.

**What the fitted object contains, and why it is large.** The pool's fitted model embeds each
member's fitted object whole, so `predict` needs nothing but the file chap-core hands it.
Every model in this project writes its fitted object as JSON — Rule 5 — which is what makes
embedding possible at all; a member that pickled would have made the pool's own object a
pickle.

**Under `min_crps` the fit contains an estimate, and where it came from is in the file.** The
weights are fitted on the last four forecast blocks of whatever training frame chap-core
hands `train`, with every member refitted on the frame with those blocks removed. Nothing
from the evaluated period is used. The validation periods, the members' scores on them, the
pairwise terms of the pooled-CRPS quadratic and the solve's objective at every vertex are all
in `fitted_model.json`.

alternatives-considered: pooling the members' stored evaluation samples post hoc instead of
building a Chap model (rejected — phase C requires every candidate to be scored through the
same `chap eval` path, and a post-hoc pool is scored by a different path however similar the
metric; the post-hoc pool was built anyway, as a *check* on this one, in check_pool.py);
averaging the members' quantiles rather than their distributions (rejected — it is a
different model, and it narrows where the members disagree where a linear pool widens; the
widening is the property this node is testing); drawing a member per sample rather than
allocating exactly (rejected — allocation is an exact sample of the mixture with one fewer
source of Monte Carlo noise, and a small-weight member then contributes its share in every
cell instead of by luck); giving the pool a fit-time fork as candidate 1 has (rejected — the
pool does not fit anything of its own beyond the weights, and where the members fit is the
members' fork).
agency: agent-autonomous
