# Claim

Does the conclusion that the two-stage ensemble earns its place against stage 1 alone survive reasonable alternative ways of building either stage — stage 1's specification, stage 2's family, target, inputs and combination rule, the training window and the backtest scheme — and which of those choices does it turn on? The perturbation set is planned and frozen here before it is run; the report is the distribution of conclusions across it, not the best one.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Batch 11 — planned and frozen, not yet run.** The perturbation set is
`results/manifest.csv` (40 rows; frozen in `results/manifest_freeze.json`), costed from
`results/run_costs.csv`.

- **Cost.** Re-running every existing model node (`02_stage1` and all seven `04_stage2`
  candidates) takes 87 seconds in total and reproduces every committed output byte for byte
  (`results/run_costs_summary.json`): stage 1 7.7 s, the per-province candidates 7–10 s each,
  `f_oosErrorRidge` 16 s, `g_oosErrorBoosting` 22 s. Compute is not the binding constraint on
  stability work here; development effort per perturbation is. The compute budget is set
  provisionally at one hour of wall-clock (agent-autonomous, for the human to revise); the
  29 planned tier-2 rows are estimated at 24 minutes, so the line falls below every planned
  row and nothing is excluded for budget.
- **Tier 1 (6 rows, derived from the tree):** the six not-taken `04_stage2` siblings, already
  run; their results are their own.
- **Tier 2 (29 rows, ranked by expected informativeness):** at the top, the refinement the
  Savannakhet loss motivates (a correction bounded relative to the forecast level), the
  airline specification for stage 1, standardising the stage-2 target by the province's
  residual scale instead of stage 1's se, and a rolling 72-month training window that forgets
  the pre-2008 reporting regime; then the level-only feature set, the no-differencing stage 1,
  a true rolling refit for the in-window errors, the per-horizon fit, Chap's default scheme
  (7 splits, stride 1), the winsorisation bound (2, 5, none), the seed, the climate anomalies,
  the 2002 window start, the boosting hyperparameters, the ridge penalty, clipping, feature
  ablations, warm-up and thresholds. Each row names the node, the parameter, the main and
  alternative values and the basis for calling the alternative reasonable.
- **Tier 3 (5 rows, not run, with the reason):** a log1p stage 1 and a negative-binomial or
  truncated-normal predictive family (both need a verified metric extension; the second is
  the most consequential fork not run, since the coverage deficit is a heavy tail a Gaussian
  cannot carry), a multiplicative combination rule (undefined near zero; needs a design), an
  ENSO covariate (new data acquisition; a governance call), and Chap-native evaluation
  (decided against in plan §4).
- **Run design for batch 12** (`results/manifest_summary.json`): tier 1 by calling each
  sibling's `run.sh`; tier 2 by a combination runner in this node that recomputes stage 1 and
  the main-path stage 2 under the combination's settings and writes `results/<combination>/`,
  trusted only once its `main` combination reproduces `g_oosErrorBoosting`'s stored per-cell
  scores byte for byte. Batch 13 reports the distribution.

No conclusion about stability is drawn here; the claim is answered by batch 13.

**Batch 12 — run.** Every planned row ran (`results/run_log.csv`, `results/run_summary.json`:
29 combinations, 1,937 s of the 3,600 s ceiling; the rolling refit alone 990 s). The runner
(`scripts/03_run_combinations.py`, on `lib/stage2_perturb.py`) was gated: its `main`
combination reproduced `04_stage2/g_oosErrorBoosting`'s 408 per-cell rows value for value
(`results/main/conclusion.json`, `verification_vs_main_path`: 0 mismatches) before any
perturbation ran, and it refuses a manifest that does not hash to the frozen digest. Each
combination's per-cell scores and conclusion are under `results/<combination>/`;
`results/conclusions.csv` gathers one row per manifest row (tier 1 from the siblings' own
comparison files, tier 3 as not run).

Headline counts from `conclusions.csv`, ahead of batch 13's report: of the 36 rows that ran
(main, 6 siblings, 29 perturbations), the two-stage ensemble beats stage 1 alone on mean CRPS
in 32 and does so with coverage not worse in 31. **All 29 tier-2 perturbations keep the
two-stage ensemble ahead of stage 1 alone with coverage not worse**, from −0.70% (true rolling
refit of the in-window errors) to −10.64% (the airline stage 1, whose stage 1 alone is much
worse at 29.15 and is largely rescued by the correction). The four rows where the ensemble
loses are the four batch 4–8 siblings trained on the in-sample residual (a–d); the one row
that wins on CRPS with worse coverage is `e_pooledRandomForest`. One caveat recorded rather
than hidden: in the rolling-refit combination, 3 origins per split whose refit returned
non-finite predictions contributed no training row (visible as the per-split row counts, 3
below `main`'s); the runner's non-finite-feature counter does not cover that case.
Batch 13 reports the distribution and which choices the margin turns on.
