result: results/per_cell_scores.csv · results/conclusion.json · results/feature_importances.csv
script: scripts/01_stage2_oos_error_boosting.py
        sha256:d4613712ec92ed73735dc6e44c96a14c4c944c4725a39b61c0480968a012581c
        ../../scripts/lib/stage2_oos.py
        sha256:04dbf43aa5b4b4d7868859f7be35f15a6a4060a9f728b3a89a5fd7511cafcb41
        ../../scripts/lib/residual_features.py
        sha256:c6339fc4b5bc37e4c9102e64e76f56a5d57ea3de7ab9fe0aa1e20b6d66dbc513
        ../../scripts/lib/stage1_model.py  (specification constants only)
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/project_seed.py
        sha256:8cf8c777a92e0d43663854423c4a6854675ea150613d42b5d08f69de14b18a5b
invocation: ../../../environment/env/bin/python scripts/01_stage2_oos_error_boosting.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (verification reference only)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: project 20260920; component seed 3256270425 = component_seed("04_stage2/g_oosErrorBoosting"),
        pinned as GradientBoostingRegressor's random_state; row subsampling (subsample=0.8) is
        real randomness. Verified per /seed: the script was run twice end to end at commit
        90add4c and results/per_cell_scores.csv and results/conclusion.json compared byte for
        byte -- identical.
verification: re-derived stage-1 forecast vs 02_stage1's stored per_cell_scores.csv: 408/408
        cells, max|Δmean| = 0.0, max|Δse| = 0.0 (results/conclusion.json).
commit: 90add4c
instructions-commit: 595c32d
node: analysis/04_stage2/g_oosErrorBoosting
produced: 2026-09-20
design: identical to f_oosErrorRidge in target, training rows, features, combination rule and
        verification (that node's provenance/stage2_oos_error_ridge.md holds the argument for
        each); the one axis changed is the family -- GradientBoostingRegressor with
        n_estimators=150, max_depth=3, learning_rate=0.05, subsample=0.8, min_samples_leaf=20
        (GBM_PARAMS), a fixed modest configuration, not a search.
alternatives-considered:
  - A hyperparameter search per split: rejected, as b_gradientBoosting and
    e_pooledRandomForest rejected it, because searching against the one backtest is the
    silent-tuning failure MOTIVATION.md names, and because the run would need its own seeding
    and cost argument. The configuration is a perturbation for the stability phase.
  - A random forest (e_pooledRandomForest's family) on these rows: not built; boosting with
    shallow trees was preferred as the non-linear sibling because its output is an additive
    correction to a fitted mean, the same role the ridge plays, so the family comparison is as
    clean as it can be. A forest on the same rows is a one-script addition if wanted.
  - Everything f_oosErrorRidge considered and rejected applies here unchanged.
agency: agent-autonomous
information: agent-retrieved (as for f_oosErrorRidge; additionally Januschowski et al. 2022
        on gradient-boosted trees as global models, cited in the batch report).

---
section appended at commit d9d1fba (comment-only change in a library after the run; nothing
re-run):
        ../../scripts/lib/residual_features.py
        sha256:cbe025691c5e58b415720849ca3e30964f24c96f921764d638a9ccd8149bec2c
        (was c6339fc4…: the comment on WARMUP_MONTHS reworded, see
        05_residualStructure/provenance/error_structure.md). This node's own script is
        unchanged. The committed results are those of the 90add4c run.

---
section appended at commit e590d27 (run at 926cd1a; human-set follow-up, plan §4b 2026-09-21):
the horizon set stage 2 trains on is now read from the evaluation scheme, not fixed.
script: scripts/01_stage2_oos_error_boosting.py
        sha256:2168ed84b9ba1b2dbde0950655352f81b961b23e7a12dfa24dac89e20472840b
        (was d4613712…: same change as f_oosErrorRidge's script -- reads n_periods via
        check_horizons, passes it to every row builder, records horizon_months)
        ../../scripts/lib/stage2_oos.py
        sha256:d6f12d8cf9643eab708ed9fc175b372f562dcd9578da4efd19ec7ccf603e0074
        (was 04dbf43a…; see f_oosErrorRidge/provenance/stage2_oos_error_ridge.md)
inputs (added): ../../01_data/03_backtest_scheme/results/schedule_summary.json
        sha256:dc56ddb766c0e73e253236485169d2e97ab8e8aaa648e2319d4587cd603e9ccc
outcome: results/per_cell_scores.csv and results/feature_importances.csv byte-identical to the
        90add4c run (same seed, same rows); results/conclusion.json differs only by the two
        added horizon fields. The scores above stand.
