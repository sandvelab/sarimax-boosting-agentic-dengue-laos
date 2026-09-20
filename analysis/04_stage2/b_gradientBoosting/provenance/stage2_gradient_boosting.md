result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/01_stage2_gradient_boosting.py
        sha256:575c837eb40f82091ea34075093e10a76d2fd5876aafbcdc9380088408779049
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/stage1_model.py
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
        ../../scripts/lib/project_seed.py
        sha256:8cf8c777a92e0d43663854423c4a6854675ea150613d42b5d08f69de14b18a5b
invocation: ../../../environment/env/bin/python scripts/01_stage2_gradient_boosting.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (02_stage1's stored forecast is a verification reference, not a value the score is
         carried from -- this script re-derives stage 1's forecast independently via
         lib/stage1_model.py and refuses to proceed if the two disagree beyond 1e-6; see
         "verification" below.)
environment: environment/ (project main, re-pinned this batch for scikit-learn)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: component seed `690660778` (`project_seed.component_seed("04_stage2/b_gradientBoosting")`)
        passed as the GradientBoostingRegressor's `random_state`, but the fit configuration
        (`subsample=1.0`, `max_features=None`) draws no real randomness -- verified, not
        assumed: the script fits the same training data twice with two different
        `random_state` values on the first province/split with enough rows and confirms
        bit-identical predictions (`atol=1e-12`), recorded in results/conclusion.json under
        "determinism_check", and raises rather than proceeds if the two ever disagreed. The
        seed is still passed and recorded for defensiveness against a future change to these
        settings that would introduce real randomness.
verification: this script re-derives stage 1's forecast (`lib/stage1_model.py`), the same
        module `a_linearLags` uses, rather than reading 02_stage1's stored file directly, so
        it also gets stage 1's in-sample residuals. Before trusting those residuals it
        compares its own re-derived (mean, se) against 02_stage1's stored
        per_cell_scores.csv cell for cell: 408/408 cells verified, max|Δmean|=0.0,
        max|Δse|=0.0 (bit-identical), recorded in results/conclusion.json under
        "verification_vs_stage1_stored_forecast". The script raises rather than proceeds if
        this check fails.
commit: 66a048e
instructions-commit: 595c32d
node: analysis/04_stage2/b_gradientBoosting
produced: 2026-09-20
alternatives-considered: (1) Inputs kept identical to a_linearLags (lag-12 in-sample residual
  + cyclical calendar month), not extended with lag-1 or anything else, to isolate the
  model-family comparison (linear vs. tree) from the input-set question -- the latter is its
  own deferred fork per the plan's ledger (batches 5-7), and folding both changes into one
  candidate would leave it unclear which one drove any difference in score. (2)
  GradientBoostingRegressor regularised for the very small per-province-per-split training
  windows (`n_estimators=50`, `max_depth=2`, `learning_rate=0.05`) rather than scikit-learn's
  defaults, which have far more capacity than the ~12-40 training rows available here can
  support without memorising them -- a first, defensible default for the tree family, not a
  hyperparameter search. (3) Sigma left unchanged from stage 1, same reasoning and same
  interval-coverage safeguard as a_linearLags, for direct comparability across the two
  candidates. (4) A province/split abstains (correction = 0) under the same
  MIN_TRAIN_ROWS=12 threshold as a_linearLags: 40 of 408 cells abstained, recorded per-cell
  in results/per_cell_scores.csv under `stage2_abstained`.
agency: agent-autonomous
