result: results/run_log_holdout.csv · results/run_summary_holdout.json ·
        results/run_status_holdout.csv · results/$COMBO/per_cell_scores.csv ·
        results/$COMBO/conclusion.json (for each of the 33 planned rows of the frozen phase-E set)
script: scripts/08_run_holdout.py
        sha256:2acfd8c5964f10a548ff549def19541384e7ceb3c6a0c0ba398e19c13d61cd44
        the machinery it runs, ../scripts/lib/:
        holdout_eval.py sha256:2c7d9990ca2fedd7a651d7a0bc64347e4af25cabd11402f0715169ca6ed87fdf
        stage2_perturb.py sha256:b5371bb823a6e8b9b821db11ee9f6c11d1d2d02b46752619c31b491980b0241a
        backtest.py sha256:bb036170c3e82031614c3fa2e7c9454ee98dad17ff7b3a387397d0addbf5f405
        crps.py sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../environment/env/bin/python scripts/08_run_holdout.py
inputs: analysis/01_data/01_prepare/results/holdout.csv
         sha256:389e4f4975980588c88a8a0f9d44e6ad903644faf096ebb469e62d89122e100d
         -- **the sealed file, opened here for the first and only time**, and the digest is the
         one holdout_freeze.json recorded at the freeze, checked before the file was parsed
        analysis/01_data/01_prepare/results/development.csv
         sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         (the training history, and the source of the frozen province set)
        results/manifest_holdout.csv
         sha256:835bb52cab2e91cc630d420f59b07691cf8a7ddb0990e5079bfbba25d9080ab0
         -- the frozen set, checked byte for byte against holdout_freeze.json before anything ran
        results/holdout_freeze.json (the freeze record: digests, the frozen commit, the rule)
        results/holdout_runner_verification.json (the gate, checked for its verdict and scope)
environment: environment/ (project main)
        lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: project seed 20260920; the gradient-boosted rows derive `random_state` per component
        inside lib/stage2_perturb.make_model, unchanged from development. No seed is drawn here.
commit: 8eda4fd
instructions-commit: 8eda4fd
node: analysis/06_stability
produced: 2026-09-22
the-opening: **opening number 1**, 2026-09-22 19:59:33, at commit 8eda4fd, recorded in
        results/run_status_holdout.csv -- a file this script appends to, never overwrites, so a
        second opening would be a second row (plan §3's third consequence). The working-tree
        marker .holdout_opened is written beside it and is gitignored, because a versioned seal
        would seal every clone and stop analysis/run.sh reproducing phase E from nothing.
preflight: four refusals, all evaluated before a holdout byte was parsed, all passed --
        the manifest hashes to the freeze; holdout.csv hashes to the seal; the gate records
        three reproductions with zero mismatched values over the frozen row set and the frozen
        cell set (17 provinces x 4 splits x 3 horizons = 204, the n_expected_cells the frozen
        manifest records for the main row); every planned row has a configuration and every
        configuration a planned row. Each refusal was exercised against a deliberately broken
        input before the run, and each stopped it.
run: 33 of 33 planned rows, 622.9 s against an estimate of 939.8 s and a ceiling of 3,600 s.
        Nothing was added, dropped or re-run.
scored: 192 of 204 cell slots. **LA-XN reports no cases for any month of 2010**, so its 12 cells
        carry no actual to score against; LA-VI was already outside the modelable set on
        development data. Batch 1's holdout completeness check recorded rows and months present,
        which they are, and did not record whether disease_cases was populated -- so the
        held-out evaluation is 16 provinces, not 17. No fit failed and stage 2 abstained nowhere.
warnings: four `RuntimeWarning: Mean of empty slice` from lib/stage2_oos.py:91 in the rows that
        carry the trailing-incidence features, from LA-XN's all-missing 2010 window. The
        expression is guarded (`if np.isfinite(...) else 0.0`), so the feature degrades to 0 and
        no non-finite value reaches a model; the affected province contributes no scored cell.
        Recorded rather than silenced.
alternatives-considered:
  - Building this script in the same batch that opens the year: rejected in batch 16 and the
    reason held here. The first version of this script refused to open the year on a
    precondition that was wrong (it compared the gate file's bytes, and that file carries its own
    stopwatch); it was corrected with the year still shut, which is the point of writing it first.
  - Blocking a second run once .holdout_opened exists: rejected -- analysis/run.sh must reproduce
    phase E from a clean clone, and a refusal keyed on a working-tree file would stop it. A second
    opening is recorded instead, as a second row with a note saying what it is.
  - Stopping the run when LA-XN turned out to be unscoreable: rejected -- the frozen set says what
    runs, and the cell count is an outcome to report, not a reason to re-plan after opening.
agency: agent-autonomous (the execution). The set, the design and the reporting rule were frozen
        in batch 16; the main path they are built around is human-set (plan §4b, 2026-09-22).
information: none retrieved; every input is a file already in this repository.
