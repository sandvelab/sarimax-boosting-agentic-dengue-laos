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
