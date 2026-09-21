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

---
section appended at commit cef9a18 (batch 14): script changed, **not yet run under this
version** -- the v2 run is batch 15's.
script: scripts/03_run_combinations.py
        sha256:f923da2f9531d01fb0cd9a019b5b68e8ce1d15580f6a0a4fd4ee594476ce332f
        (was e353726e…: the main path is read from 04_stage2/claim.md and must match the one
        the manifest was frozen for; configurations are held per main path (g: the v1 rows;
        h: the v2 `@h` rows) with the main path's Stage2Config as the base each row varies; the
        gate row is `main<tag>` and compares with that main path's stored per-cell file; rows
        marked superseded are not re-run). The committed results under results/<v1 name>/
        remain those of the edc5158 run described above.

---
section appended at commit ba79a02 (batch 15): **the v2 run, around h_levelOnlyBoosting**.
script: scripts/03_run_combinations.py
        sha256:1a12e18cbca89d778be8e40174be18a51d976b5b2b4fcca61da8ed176762c637
change: (was f923da2f…) the run log and summary of a version after the first are written as
        run_log_v<N>.csv and run_summary_v<N>.json, so v1's run_log.csv and run_summary.json
        stay the record of the batch-12 run. The library files are unchanged from the section
        above (stage2_perturb b5371bb8…, stage2_oos d6f12d8c…, residual_features cbe02569…,
        backtest bb036170…, crps 90f29c83…, project_seed 8cf8c777…).
result: results/$COMBO/per_cell_scores.csv · results/$COMBO/conclusion.json for main@h and
        every planned tier-2 row of manifest v2 (the 26 rows suffixed `@h`) ·
        results/run_log_v2.csv  sha256:5ff022a2aa40ed861bfe3ece742eaeb85c97a499b41bf65b42ad17973c3701c9 ·
        results/run_summary_v2.json  sha256:3f5ab45a7756f402518ca8af7ffda20749a6bdf2054f5f4b48e975eee9833ecb
invocation: ../../environment/env/bin/python scripts/03_run_combinations.py
inputs: results/manifest.csv  sha256:d2c5e813e7215eb908787049546e0e8346c3311ea7b6d6b3ca6fd43c53834ac0
         (v2, frozen at cef9a18; the run refuses to start unless it hashes to the frozen digest
         and unless 04_stage2/claim.md's main path is the one it was frozen for)
         results/manifest_freeze.json  sha256:a6e1efa271432a42694d4c106aa366a6641a5c52d3ac41d345c3101aeff15d95
         ../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../04_stage2/h_levelOnlyBoosting/results/per_cell_scores.csv  sha256:52d9f2457dfa1d9a675d2978479621df195eccb315aa0ada95a66cb70c8f3b41
         (the gate: main@h reproduced it on all 408 rows with 0 mismatched values,
         results/main@h/conclusion.json "verification_vs_main_path", before any row ran)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: project 20260920. h_levelOnlyBoosting's Stage2Config keeps seed_component
        "04_stage2/g_oosErrorBoosting" (random_state 3256270425) -- the node was built from this
        pipeline with that seed, which is what lets the gate reproduce it -- so every gradient-
        boosted v2 row uses it and differs from main@h by its perturbation alone; the
        `stage2=alt_seed@h` row uses component_seed("04_stage2/g_oosErrorBoosting/alt").
        Determinism shown by the gate and by `stage2=min_train_rows1000@h` and
        `modelable=36_months@h`, which change nothing binding and reproduce main@h's 24.3508
        exactly; and by four rows whose configuration is, by construction, identical to a v1
        row (main@h = stage2=g_level_month_horizon_only; plus_recent_and_incidence@h =
        g_no_cross_province; plus_recent_and_cross@h = g_no_incidence_terms; full_plus_climate@h
        = g_with_climate_anomalies), all four reproducing the v1 two-stage mean CRPS to the last
        digit (results/version_comparison_v2.csv, written by 05_report_distribution.py).
commit: ba79a02
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-22
where the budget line fell: nowhere. All 26 planned rows ran; total wall 1,536.6 s of the
        3,600 s ceiling (results/run_summary_v2.json); the rolling refit alone 773.6 s
        (results/run_log_v2.csv). The gate took 28.7 s.
caveat carried from v1: in `stage2=rolling_refit_oos@h`, 3 origins per split whose refit
        returned non-finite predictions contributed no training row (per-split counts 4707 …
        5676 against main@h's 4710 … 5679; n_training_rows_dropped_nonfinite is 0 because the
        counter does not cover origins skipped inside in_window_errors).
alternatives-considered (this section):
  - Overwriting run_log.csv and run_summary.json with the v2 run's: rejected -- v1's files are
    the record of the batch-12 run that the batch-13 report and claims C2-C7 cite.
  - Dropping the four rows whose configuration coincides with a v1 row as redundant: rejected
    -- they are what the manifest planned around h, and their exact reproduction of v1's
    values is a free determinism check that is recorded rather than discarded.
agency: agent-autonomous (the run and its output naming); the main path it runs around is
        the batch-14 pre-registered choice (rule agent-autonomous, annotating now human-set).
