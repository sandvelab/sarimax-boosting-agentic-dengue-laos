result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/01_stage2_linear_climate.py
        sha256:a595fa71ea0ce53ae62360d3ac309d99831c6d05cdfde2d5df43c73235ca6169
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/stage1_model.py
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
invocation: ../../../environment/env/bin/python scripts/01_stage2_linear_climate.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (02_stage1's stored forecast is a verification reference, not a value the score is
         carried from -- this script re-derives stage 1's forecast independently via
         lib/stage1_model.py, exactly as a_linearLags does, and refuses to proceed if the two
         disagree beyond 1e-6; see "verification" below. The climate columns read from
         development.csv -- rainfall, mean_temperature, mean_relative_humidity -- are the
         same file a_linearLags already reads for disease_cases, no new acquisition.)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none -- the re-derived SARIMAX fit is the same deterministic L-BFGS as 02_stage1 and
        a_linearLags (verified bit-for-bit against 02_stage1's stored forecast, all 408 cells,
        as a side effect of this script's own correctness check -- see verification below);
        the stage-2 OLS step is a closed-form least-squares solve (numpy.linalg.lstsq), also
        fully deterministic.
verification: this script re-derives stage 1's forecast (lib/stage1_model.py) rather than
        reading 02_stage1's stored file, so that it also gets stage 1's in-sample residuals.
        Before trusting those residuals it compares its own re-derived (mean, se) against
        02_stage1's stored per_cell_scores.csv cell for cell: 408/408 cells verified,
        max|Δmean|=0.0, max|Δse|=0.0 (bit-identical), recorded in
        results/conclusion.json under "verification_vs_stage1_stored_forecast". The script
        raises rather than proceeds if this check fails.
commit: 8c414b7
instructions-commit: 595c32d
node: analysis/04_stage2/d_linearClimate
produced: 2026-09-20
alternatives-considered: (1) Contemporaneous (test-month) climate values instead of lag-12:
  rejected as leakage for this project's question -- development.csv holds already-observed
  historical climate for every month including the test months, but a real 1-3-month-ahead
  deployment would not know next quarter's rainfall with the certainty the file implies; lag-12
  falls inside the training window regardless of which of the 3 test months is being
  predicted, exactly the same leakage-safety argument a_linearLags already made for the
  residual lag. This is conservative -- it forgoes the current season's anomaly and stands in
  a same-season climatological proxy instead -- and that gap is logged as an untried
  refinement (a genuine short-range meteorological forecast is not in this dataset), not a
  rejected option. (2) Population as a fourth covariate: not added here, per 04_stage2/claim.md's
  batch-7 reasoning that it is near-constant within a province over this backtest's span
  relative to month-to-month case variation -- deprioritised, not run, kept as its own logged
  fork rather than silently folded into this candidate. (3) Same family (linear OLS) as
  a_linearLags, not a new family: deliberate, to isolate the input-richness question from the
  model-family question already explored by b_gradientBoosting and c_bayesianRidge on the
  minimal input -- trying climate on a new family simultaneously would confound the two axes.
agency: agent-autonomous
