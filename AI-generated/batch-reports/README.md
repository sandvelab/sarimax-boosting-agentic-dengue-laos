# batch-reports

One report per executed batch of the live plan
(`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`). Not
regenerable — each is an account of what happened during one batch, and a re-run produces a
different report, not the same one.

## Currently here

- `26-09-20_b01_orientAndSetUp.md` — batch 1: reset the repository from the prior, completed
  project to a blank project scaffold; wrote the new plan and `readme-at-start.md`; verified
  the reused archived data's checksums; created `.venv` and the root `analysis/claim.md`. No
  modelling.
- `26-09-20_b02_dataAndStage1.md` — batch 2: characterised the reused dataset, implemented and
  verified the CRPS metric, built the backtest scheme, and built stage 1 (per-province
  SARIMAX) end to end.
- `26-09-20_b03_baselines.md` — batch 3: built the persistence and seasonal-climatology
  baselines through the same pipeline; both lose to stage 1 alone.
- `26-09-20_b04_stage2LinearLags.md` — batch 4: built the residual-correction contract and the
  first stage-2 candidate, `a_linearLags`; it does not beat stage 1 alone.
- `26-09-20_b05_stage2GradientBoosting.md` — batch 5: second stage-2 candidate,
  `b_gradientBoosting`, on the identical minimal input; also loses.
- `26-09-20_b06_stage2BayesianRidge.md` — batch 6: third stage-2 candidate, `c_bayesianRidge`;
  best-calibrated of the three but the worst CRPS.
- `26-09-20_b07_stage2MainPathAndInputForks.md` — batch 7: `a_linearLags` set as `04_stage2`'s
  main path (least-bad, not an endorsement); climate covariates, extra lags, population and
  cross-province pooling logged as explicit, unexplored input-space forks.
- `26-09-20_b08_stage2LinearClimate.md` — batch 8: fourth stage-2 candidate, `d_linearClimate`
  (the climate-covariate fork tried, at the human's direction); also loses to stage 1 alone
  and to `a_linearLags`.
- `26-09-20_b09_stage2PooledRandomForest.md` — batch 9: fifth stage-2 candidate,
  `e_pooledRandomForest`, adapted from `chap-models/rwanda_random_forest` at the human's
  direction; the first to beat stage 1 alone on mean CRPS, but disqualified by a collapse in
  interval coverage traced to negative forecasts concentrated in low-case-count provinces.
- `26-09-20_b10_stage2SystematicSecondIteration.md` — batch 10: literature search, a
  diagnostic node on stage 1's out-of-sample errors (`05_residualStructure`), and two
  candidates trained on those errors rather than on in-sample residuals (`f_oosErrorRidge`,
  `g_oosErrorBoosting`); both beat stage 1 alone with improved coverage, and
  `g_oosErrorBoosting` becomes `04_stage2`'s main path.
- `26-09-21_b11_stabilityPlan.md` — batch 11: phase D opens with `06_stability`; per-run
  costs measured by re-running the whole tree (87 s, byte-identical), the development
  perturbation manifest planned, ranked and frozen (40 rows), the run design fixed for batch 12.
- `26-09-21_b12_stabilityRun.md` — batch 12: the combination runner built and verified against
  the main path; all 29 planned perturbations run (1,937 s); every one keeps the two-stage
  ensemble ahead of stage 1 alone with coverage not worse.
- `26-09-21_b13_stabilityReport.md` — batch 13: the distribution of the central conclusion
  across the set — sign stable, size not; the gain concentrated in four provinces and at 2–3
  months ahead; seven claims into the collection. Phase D closes.
- `26-09-21_b14_stage2ThirdIterationAndMainPath.md` — batch 14: stage 1 fixed and its six
  weaknesses documented (human-set); three more stage-2 candidates (`h`, `i`, `j`) built
  through the verified pipeline; `h_levelOnlyBoosting` annotated as main path by a
  pre-registered rule; the stability manifest re-planned around it (v2).
