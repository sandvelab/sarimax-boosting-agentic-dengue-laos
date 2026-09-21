result: results/$COMBO/per_cell_scores.csv · results/$COMBO/conclusion.json (for `main` and every planned tier-2 combination named in results/manifest.csv) · results/run_log.csv · results/run_summary.json
script: scripts/03_run_combinations.py
        sha256:e353726ed5e445a7b42c0f578074104a03fc2f2666cc7d2acaa01bcda6fd751f
        ../scripts/lib/stage2_perturb.py
        sha256:b5371bb823a6e8b9b821db11ee9f6c11d1d2d02b46752619c31b491980b0241a
        ../scripts/lib/stage2_oos.py  (incidence_state, national_index, wins, ZCLIP)
        sha256:d6f12d8cf9643eab708ed9fc175b372f562dcd9578da4efd19ec7ccf603e0074
        ../scripts/lib/residual_features.py  (climatology and anomaly helpers, recent_residuals)
        sha256:cbe025691c5e58b415720849ca3e30964f24c96f921764d638a9ccd8149bec2c
        ../scripts/lib/backtest.py  (rolling_splits, so the scheme perturbation uses the project's own splitter)
        sha256:bb036170c3e82031614c3fa2e7c9454ee98dad17ff7b3a387397d0addbf5f405
        ../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../scripts/lib/project_seed.py
        sha256:8cf8c777a92e0d43663854423c4a6854675ea150613d42b5d08f69de14b18a5b
invocation: ../../environment/env/bin/python scripts/03_run_combinations.py
inputs: results/manifest.csv  sha256:ba01a061bfbe0a4f3e636d4a747b2a3bffe8d2cd1f673342af790fb2bdc9340b
         results/manifest_freeze.json  sha256:25c81689add00a50a164c99e0b0c1a767e8e7385d6e94c1d45cb76f4bc30795d
         (the run refuses to start unless manifest.csv hashes to the frozen digest)
         ../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../04_stage2/g_oosErrorBoosting/results/per_cell_scores.csv  sha256:d03eaf3c6ca59b7a0b951cb3dd4c38fdbc1eea3dabe894c5e3d0d7198012732c
         (the gate: the `main` combination is compared with it value for value on the shared
         columns before any perturbation runs; a value the score is not carried from)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: project 20260920. Gradient-boosted combinations: random_state = component_seed("04_stage2/g_oosErrorBoosting")
        = 3256270425, the main path's own seed, so a perturbation differs from the main path
        by the perturbation alone; the `stage2=g_alt_seed` row uses
        component_seed("04_stage2/g_oosErrorBoosting/alt") instead. Ridge rows and every
        stage-1 step are deterministic. Determinism of the runner is demonstrated by the
        gate itself: `main` reproduces g_oosErrorBoosting's 408 rows with 0 mismatched values
        (results/main/conclusion.json, "verification_vs_main_path"), and
        `stage2=g_min_train_rows1000` and `modelable=36_months` -- perturbations that change
        nothing binding -- reproduce the main path's 25.164 exactly.
commit: edc5158  (the script and library as they ran for the committed results; see history)
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-21
history: 2b5256c was the first version. Its full run stopped at the seventh combination,
        `stage2=g_rolling_refit_oos`: a fresh SARIMAX fit on a truncated series diverged at
        some origins and returned non-finite predictions, which reached the booster as NaN
        features. edc5158 (lib/stage2_perturb.py) skips an origin whose refit prediction is
        non-finite, drops any training row with a non-finite feature or target (counted as
        n_training_rows_dropped_nonfinite) and sets a non-finite test feature to 0; the six
        combinations that had completed under 2b5256c were re-run from scratch with the rest,
        and their conclusions are unchanged to every printed digit. Limitation, recorded: the
        counter covers non-finite feature rows, not the origins skipped inside
        in_window_errors; those are visible as the rolling-refit combination's per-split
        training-row counts, 3 below `main`'s in every split (4707 vs 4710 in split 0, …).
where the budget line fell: nowhere. All 29 planned rows ran; total wall 1,937 s of the
        3,600 s ceiling (results/run_summary.json); the rolling refit alone 990 s
        (results/run_log.csv).
alternatives-considered:
  - Editing the candidates' own scripts to take parameters: rejected -- they are closed
    records whose provenance hashes them, and they refuse a stage-1 forecast that differs from
    02_stage1's stored one, so no stage-1 perturbation could run through them. A separate
    pipeline with a reproduction gate keeps them intact and makes the runner's fidelity a
    checked fact rather than an assumption.
  - Comparing the gate byte for byte rather than value for value: the candidates write CSVs
    with \r\n and this node writes \n (plan §6 row 17), so bytes cannot match; every shared
    column is compared as the string the CSV carries, which is the same comparison modulo
    line endings.
  - Running only the top-ranked rows first and stopping at the budget: the whole set fit
    inside the ceiling with room to spare, so the ranked order was run to the end; the rank
    still records what would have been cut had the budget bound.
  - Resuming the failed run from the seventh row instead of re-running all: rejected -- a
    library change after six rows had run would have left them under a different digest from
    the rest.
agency: agent-autonomous
