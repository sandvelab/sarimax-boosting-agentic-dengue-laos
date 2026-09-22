result: results/holdout_runner_verification.json
script: scripts/06_verify_holdout_runner.py
        sha256:154bd6b98101bd78081795fe07c081c6357d0c7a19a6d76a49b4dc4a5985f9f5
        the machinery it gates, ../scripts/lib/:
        holdout_eval.py sha256:2c7d9990ca2fedd7a651d7a0bc64347e4af25cabd11402f0715169ca6ed87fdf
        stage2_perturb.py sha256:b5371bb823a6e8b9b821db11ee9f6c11d1d2d02b46752619c31b491980b0241a
        backtest.py sha256:bb036170c3e82031614c3fa2e7c9454ee98dad17ff7b3a387397d0addbf5f405
        crps.py sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../environment/env/bin/python scripts/06_verify_holdout_runner.py
inputs: analysis/01_data/01_prepare/results/development.csv
         sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
        analysis/04_stage2/h_levelOnlyBoosting/results/per_cell_scores.csv (the main path's
         stored 408 cells, the first comparison target)
        analysis/03_baselines/01_persistence/results/per_cell_scores.csv
        analysis/03_baselines/02_climatology/results/per_cell_scores.csv
        analysis/01_data/01_prepare/results/holdout.csv
         sha256:389e4f4975980588c88a8a0f9d44e6ad903644faf096ebb469e62d89122e100d
         -- **the `time_period` column only**, to resolve the frozen scheme over the combined
         span, the same way 01_data/03_backtest_scheme reads development's month labels. No
         case value from the holdout is read by this script.
environment: environment/ (project main)
        lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn by this script. The two-stage comparison seeds `random_state` from the
        project seed inside lib/stage2_perturb.make_model, exactly as the stored result did --
        which is part of what reproducing it value for value demonstrates.
commit: 67f998c
instructions-commit: 67f998c
node: analysis/06_stability
produced: 2026-09-22
gate: three reproductions of stored development results, on the development scheme
        (n_splits 8, stride 3), compared value for value on the columns both sides carry:
        the two-stage pipeline at the main path's configuration, 408 of 408 rows, 0 mismatched
        values; persistence, 408 of 408, 0; seasonal climatology, 408 of 408, 0. 17.4 s.
        The baselines are the ones that matter: `03_baselines`' scripts read the development
        file and the stored split schedule and cannot take another file, so
        lib/holdout_eval.py is a second implementation of both forecasts, and nothing but this
        comparison says the two agree. `07_plan_holdout_manifest.py` refuses to freeze a
        manifest unless this file records `all_reproductions_identical: true`.
also-verified: every row lib/holdout_eval.holdout_combinations() names is constructible
        (33 rows, 0 malformed); the frozen province set is development's seventeen; and the
        holdout scheme resolves over the combined 1998-01..2010-12 span to four expanding
        three-month blocks (training 144, 147, 150, 153 months) covering 2010-01..2010-12
        exactly once.
alternatives-considered:
  - Building the holdout runner in batch 17, alongside the opening: rejected, and this is the
    reason the script exists. Plan §3 allows one opening. If the code that opens the year is
    also the code being debugged, the first failure is repaired with a held-out number already
    on screen and the second run is not the first opening. Everything phase E executes is
    written and checked here instead, against results this repository already has.
  - Reusing 03_baselines' scripts by parameterising them: rejected -- they are closed records
    of a produced result (AGENTS.md §1), and editing them to take another file would rewrite
    the provenance of the development baseline scores. A second implementation gated on
    reproducing the first is the cost of not touching them.
  - Adding a `provinces` parameter to lib/stage2_perturb.py: rejected -- it would change
    Stage2Config/SchemeConfig and so the `config` block every stored conclusion.json carries.
    Restricting the rows handed to the existing pipeline achieves the same thing and leaves
    the development results' provenance untouched.
  - Scoring the holdout from one origin at 2009-12 with h = 1..12: rejected -- it evaluates the
    year at horizons no model here is built or scored for, and the project's horizon coupling
    is to the scheme's n_periods (plan §4b, 2026-09-21), not to the length of the held-out file.
agency: agent-autonomous (the evaluation design, the second baseline implementation, and the
        decision to gate the machinery in this batch rather than in phase E). The main path the
        design is built around is human-set (plan §4b, 2026-09-22).
information: none retrieved; every input is a file already in this repository.
