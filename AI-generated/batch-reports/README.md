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
