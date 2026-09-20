result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/01_stage2_bayesian_ridge.py
        sha256:4cf23ee10fafe750d0b3107ee966bc5094d3456b00b63911f43ea38646285015
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/stage1_model.py
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
invocation: ../../../environment/env/bin/python scripts/01_stage2_bayesian_ridge.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (02_stage1's stored forecast is a verification reference, not a value the score is
         carried from -- this script re-derives stage 1's forecast independently via
         lib/stage1_model.py and refuses to proceed if the two disagree beyond 1e-6; see
         "verification" below.)
environment: environment/ (project main, unchanged this batch -- scikit-learn already pinned
         by batch 5)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none -- BayesianRidge has no `random_state` parameter and uses no random
        initialisation (a deterministic fixed-point iteration from fixed starting
        hyperparameters). Verified, not assumed: the script fits the same training data
        twice from scratch on the first province/split with enough rows and confirms
        bit-identical (mean, std) predictions (`np.array_equal`), recorded in
        results/conclusion.json under "determinism_check", and raises rather than proceeds
        if the two ever disagreed.
verification: this script re-derives stage 1's forecast (`lib/stage1_model.py`), the same
        module `a_linearLags`/`b_gradientBoosting` use, rather than reading 02_stage1's
        stored file directly, so it also gets stage 1's in-sample residuals. Before trusting
        those residuals it compares its own re-derived (mean, se) against 02_stage1's stored
        per_cell_scores.csv cell for cell: 408/408 cells verified, max|Δmean|=0.0,
        max|Δse|=0.0 (bit-identical), recorded in results/conclusion.json under
        "verification_vs_stage1_stored_forecast". The script raises rather than proceeds if
        this check fails.
commit: f2b5636
instructions-commit: 595c32d
node: analysis/04_stage2/c_bayesianRidge
produced: 2026-09-20
alternatives-considered: (1) BayesianRidge (closed-form, evidence-maximised Gaussian prior on
  coefficients) chosen over a hierarchical partial-pooling model (e.g. PyMC) -- it answers the
  calibration question the plan asks without a heavy MCMC dependency for per-province-per-split
  fits on as few as ~24 rows, where MCMC asymptotics are the wrong tool anyway; no new
  dependency needed since scikit-learn is already pinned. (2) Inputs kept identical to
  a_linearLags/b_gradientBoosting (lag-12 in-sample residual, cyclical calendar month) to
  isolate the model-family comparison from the input-set question, deferred to batch 7. (3)
  Features standardised (zero mean / unit variance, training-window statistics only) before
  fitting and un-standardised after -- necessary because BayesianRidge places a single
  shared-precision prior across all coefficients, which implicitly assumes comparable feature
  scales; the raw lag-12 residual (disease-case units) and sin/cos calendar features
  ([-1, 1]) are not comparable without this. (4) Calibration: final variance combines stage
  1's forecast variance and stage 2's own posterior predictive variance as independent sources
  (`final_se = sqrt(stage1_se^2 + stage2_se^2)`), a genuine calibration attempt rather than
  leaving sigma unchanged as the two prior candidates did — enabled by this being the first
  candidate whose model exposes its own predictive uncertainty. (5) A province/split abstains
  (correction = 0, stage2_se = 0) under the same MIN_TRAIN_ROWS=12 threshold as the other two
  candidates: 40 of 408 cells abstained, recorded per-cell in results/per_cell_scores.csv
  under `stage2_abstained`.
agency: agent-autonomous
