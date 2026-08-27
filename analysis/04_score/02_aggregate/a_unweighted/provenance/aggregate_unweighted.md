# Provenance — the headline mean, unweighted over cells

```
result:              results/main/metrics_summary.csv
                     results/main/crps_by_location.csv
                     results/main/crps_by_split.csv
                     results/main/crps_by_region_split.csv
                     results/main/crps_by_horizon.csv
script:              scripts/aggregate_unweighted.py
                     sha256:cc1df71851d253c94bbfce7c9a1aecb7b3ef5bc7c0046aa707da0b08f880af93
invocation:          "$PYTHON" scripts/aggregate_unweighted.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/04_score/01_collect/results/main/metrics_cell.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Five `groupby` aggregations of one stored file.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/04_score/02_aggregate/a_unweighted
produced:            2026-08-26
```

**What it establishes.** The headline figures per model, and the four resolutions the plan
requires beside the mean — by province, by split, by province and split, and by lead time.
All five are `groupby` operations on one file, so a reader can check any reported figure by
re-running one line against `metrics_cell.csv`.

**Why the unweighted mean is the main path and why that is not an endorsement.** It is what
Chap's own evaluation reports and what the project's success criterion is defined against,
so it is the summary the comparison must be made in. It is also, on this dataset, a poor
summary: an unweighted mean over cells is dominated by the arithmetic of the large-count
provinces, where absolute errors are large, and says almost nothing about how well the
sixteen provinces are served individually. Batch 3 predicted this from the burden
distribution; the per-province file beside this one is where it becomes visible.

**The cheapest fork in the project.** Re-weighting is a re-aggregation of `metrics_cell.csv`
and re-runs no model at all, so both siblings cost seconds. That is why batch 5 records the
scoring fork as a third kind beside the plan's two: it re-scores every model, like a setup
fork, and costs nothing, unlike one.

alternatives-considered: population weighting and case weighting are the siblings
(`b_populationWeighted`, `c_caseWeighted`), built when the stability manifest needs them.
Reporting a median rather than a mean over cells was considered and rejected: CRPS is
defined as an expectation and the reference implementations, including Chap's own, report
the mean, so a median would make our headline number incomparable with everyone else's. A
per-province mean-of-means — giving each province equal weight regardless of how many cells
it contributes — is a fourth weighting and is *not* one of the planned siblings; it is noted
here as a candidate the manifest could add.

agency: agent-autonomous. That the criterion is defined on the unweighted mean is the plan's
(`human-set`, §4); the placement of the weighting question as a fork is batch 5's.

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

```
result:              results/main/metrics_summary.csv · crps_by_location.csv ·
                     crps_by_split.csv · crps_by_region_split.csv · crps_by_horizon.csv
                     autoregressive_lag3/metrics_summary.csv
                     autoregressive_lag3/crps_by_location.csv
                     autoregressive_lag3/crps_by_split.csv
                     autoregressive_lag3/crps_by_region_split.csv
                     autoregressive_lag3/crps_by_horizon.csv
                     covariates_lagged/metrics_summary.csv
                     covariates_lagged/crps_by_location.csv
                     covariates_lagged/crps_by_split.csv
                     covariates_lagged/crps_by_region_split.csv
                     covariates_lagged/crps_by_horizon.csv
                     covariates_rich/metrics_summary.csv
                     covariates_rich/crps_by_location.csv
                     covariates_rich/crps_by_split.csv
                     covariates_rich/crps_by_region_split.csv
                     covariates_rich/crps_by_horizon.csv
                     fitTime_refitAtPredict/metrics_summary.csv
                     fitTime_refitAtPredict/crps_by_location.csv
                     fitTime_refitAtPredict/crps_by_split.csv
                     fitTime_refitAtPredict/crps_by_region_split.csv
                     fitTime_refitAtPredict/crps_by_horizon.csv
                     observation_negBinomial/metrics_summary.csv
                     observation_negBinomial/crps_by_location.csv
                     observation_negBinomial/crps_by_split.csv
                     observation_negBinomial/crps_by_region_split.csv
                     observation_negBinomial/crps_by_horizon.csv
                     observation_zeroInflated/metrics_summary.csv
                     observation_zeroInflated/crps_by_location.csv
                     observation_zeroInflated/crps_by_split.csv
                     observation_zeroInflated/crps_by_region_split.csv
                     observation_zeroInflated/crps_by_horizon.csv
                     population_covariate/metrics_summary.csv
                     population_covariate/crps_by_location.csv
                     population_covariate/crps_by_split.csv
                     population_covariate/crps_by_region_split.csv
                     population_covariate/crps_by_horizon.csv
                     population_ignored/metrics_summary.csv
                     population_ignored/crps_by_location.csv
                     population_ignored/crps_by_split.csv
                     population_ignored/crps_by_region_split.csv
                     population_ignored/crps_by_horizon.csv
                     yearVariance_shared/metrics_summary.csv
                     yearVariance_shared/crps_by_location.csv
                     yearVariance_shared/crps_by_split.csv
                     yearVariance_shared/crps_by_region_split.csv
                     yearVariance_shared/crps_by_horizon.csv
script:              scripts/aggregate_unweighted.py   (unchanged)
```

Run once per combination by the sweep driver, on that combination's own
`01_collect/results/<combo>/metrics_cell.csv`. Nothing about the script changed; it is the
node that answers "what did this combination score", and `metrics_summary.csv` is what the
fork leaderboard is copied from.

**Where the promoted main path's CRPS goes**, from `results/main/crps_by_location.csv`: it
now beats the reference in Vientiane Capital (78.0 against 92.8, coverage 0.88 against
0.78) and in Luang Prabang, and loses badly in Salavan (55.1 against 38.4, coverage
**0.12**), Bokeo and Attapeu -- the provinces whose intervals are far too narrow. By lead
time it is 20.4 / 23.2 / **27.5** against the reference's 16.5 / 22.0 / 27.8, so at three
months' lead our candidate is now level with the field's own model, and at one month it is
not close.

alternatives-considered: none new. The weighting fork's two unbuilt siblings
(`b_populationWeighted`, `c_caseWeighted`) remain batch 12's, and batch 7's note that the
weighting fork is not to be cut from the manifest stands -- with more force now, since the
candidate's worst province is one of the two carrying the most cases.

agency: agent-autonomous.
