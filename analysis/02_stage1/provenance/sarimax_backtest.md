result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/sarimax_backtest.py
        sha256:82690b24ae6ee3023278264e6d4e39d11e62f6f043204d5110c75bd39f46adb7
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../environment/env/bin/python scripts/sarimax_backtest.py
inputs: ../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../01_data/02_characterise/results/modelability_summary.json  sha256:869509cfbe44b8c03844d7760cfed4ad199d4cebda3598dd849a179d203371a2
         ../01_data/03_backtest_scheme/results/split_schedule.csv  sha256:4645c239d5bbff181e31382113660d4a2048a39489d20d5deefde86f6275c5dc
environment: environment/ (project main)
         lock.txt sha256:1d10c3af0cce41440634defbe5b77b0fa30243333df2fd9493015ba2e197278a
seeds: none — SARIMAX MLE fitting here draws no randomness (deterministic L-BFGS from fixed
        starting values). Verified by fitting one province/split twice outside the tree and
        comparing forecast mean and se bit-for-bit (identical to full float64 precision);
        not re-verified for all 136 fits, a scope decision recorded below.
commit: (see this batch's commit for 02_stage1)
instructions-commit: 595c32d
node: analysis/02_stage1
produced: 2026-09-20
alternatives-considered: (1) SARIMAX order (1,1,1)x(1,0,0,12) is a first, defensible default
  -- integrated non-seasonal term for the local trend, seasonal AR(1) at lag 12 for the
  annual dengue cycle -- not a searched-over optimum; order selection is deferred to a later
  perturbation fork rather than explored here, per the plan's own stated batch-2 scope. (2)
  Fitting on raw `disease_cases` rather than log1p(cases) was chosen so the Gaussian CRPS
  this batch verified applies without a distributional mismatch between the transformed fit
  and the raw-scale target; log1p is deferred as an explicit transformation-choice fork
  (plan §3 names "transformation of the target" as a judgment call requiring one). This
  produces predictable weaknesses on zero-heavy provinces (over-dispersion, occasional
  negative forecast means scored at face value) which are visible in the per-cell file
  rather than smoothed over. (3) Determinism was spot-checked on one case rather than all
  136 fits, on the reasoning that the fitting method (L-BFGS, no stochastic component) makes
  a fit-specific failure implausible and re-running the whole backtest to verify each cell
  costs more than the check is worth at this stage; flagged for `/seed audit` to revisit if
  this becomes a stability-sensitive result.
agency: agent-autonomous
