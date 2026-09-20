result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/01_stage2_linear_lags.py
        sha256:35b6fe13d5b64f8f115a2fbbc19252e8e27ed1cfe9ab9c50ec9809500ea5f38d
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/stage1_model.py
        sha256:8372f58c394ac348fbf04d18c32818e5efd55ca9e557cfa45a8a45d831b78b98
invocation: ../../../environment/env/bin/python scripts/01_stage2_linear_lags.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (02_stage1's stored forecast is a verification reference, not a value the score is
         carried from -- this script re-derives stage 1's forecast independently via
         lib/stage1_model.py and refuses to proceed if the two disagree beyond 1e-6; see
         "verification" below.)
environment: environment/ (project main)
         lock.txt sha256:1d10c3af0cce41440634defbe5b77b0fa30243333df2fd9493015ba2e197278a
seeds: none — the re-derived SARIMAX fit is the same deterministic L-BFGS as 02_stage1
        (verified bit-for-bit against it, not merely spot-checked, since this script compares
        every one of the 408 cells as a side effect of its own correctness check — see
        verification below); the stage-2 OLS step is a closed-form least-squares solve
        (`numpy.linalg.lstsq`), also fully deterministic.
verification: this script re-derives stage 1's forecast (`lib/stage1_model.py`) rather than
        reading 02_stage1's stored file, so that it also gets stage 1's in-sample residuals,
        which 02_stage1 never persisted. Before trusting those residuals it compares its own
        re-derived (mean, se) against 02_stage1's stored per_cell_scores.csv cell for cell:
        408/408 cells verified, max|Δmean|=0.0, max|Δse|=0.0 (bit-identical), recorded in
        results/conclusion.json under "verification_vs_stage1_stored_forecast". The script
        raises rather than proceeds if this check fails.
commit: (see this batch's commit for a_linearLags)
instructions-commit: 595c32d
node: analysis/04_stage2/a_linearLags
produced: 2026-09-20
alternatives-considered: (1) Stage 2's input is lag-12 in-sample residual + cyclical calendar
  month only, not lag-1: lag-1 residual is available at forecast time for the first of the
  3-month test window but not for the second or third (it would depend on an actual not yet
  observed at forecast time in a real deployment), so it was rejected as a leakage risk
  rather than included and quietly biasing the later test months of each split. Lag-12 always
  falls inside the training window regardless of which test month is being predicted. (2)
  Sigma is left unchanged from stage 1's forecast standard error — stage 2 corrects the mean
  only. Recalibrating sigma from stage 2's own correction error would need a further nested
  split within an already-small per-province-per-split training window (as few as ~24
  present months for some provinces) and was judged not worth the added complexity for a
  first candidate; interval coverage is reported beside CRPS (see
  `results/comparison.json`) precisely so an overconfidence problem from this choice would
  show up rather than be assumed away. (3) A province/split abstains (correction = 0) rather
  than fit an OLS on fewer than 12 valid rows (3x the 4 regression parameters), or apply a
  correction whose lag-12 input is itself missing for a specific test month: 40 of 408 cells
  abstained this way, recorded per-cell in `results/per_cell_scores.csv` under
  `stage2_abstained`, not silently absorbed into the score.
agency: agent-autonomous
