result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/climatology_backtest.py
        sha256:44bf14ce7e11b167303681e06feb6d4da6ffed7582a6cfcb10fba916e94619e0
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/climatology_backtest.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
environment: environment/ (project main)
         lock.txt sha256:1d10c3af0cce41440634defbe5b77b0fa30243333df2fd9493015ba2e197278a
seeds: none — climatology is a deterministic mean/std of training-window values grouped by
        calendar month; no fitting, no randomness anywhere in the computation.
commit: (see this batch's After commit for 02_climatology)
instructions-commit: 595c32d
node: analysis/03_baselines/02_climatology
produced: 2026-09-20
alternatives-considered: same distributional-forecast gap as 01_persistence (plan requires
  every model scored the same Gaussian way). Considered: (1) a single project-wide sigma —
  rejected, discards seasonal spread differences the climatology mean itself is built from;
  (2) sigma from the province's full non-seasonal history — rejected, mixes months with
  different means and overstates spread for low-variance months; (3) sigma as the standard
  deviation of the same calendar month's own training-window values, matching the quantity
  the mean is computed from — this is what the script does. A calendar month with fewer than
  two training-window observations (std undefined) falls back to the 1e-6 floor, same as
  01_persistence.
agency: agent-autonomous
