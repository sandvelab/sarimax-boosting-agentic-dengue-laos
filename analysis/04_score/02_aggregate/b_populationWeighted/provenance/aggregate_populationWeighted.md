# Provenance — the headline mean weighted by population

```
result:              results/$COMBO/metrics_summary.csv
                     results/$COMBO/crps_by_location.csv
                     results/$COMBO/crps_by_split.csv
                     results/$COMBO/crps_by_region_split.csv
                     results/$COMBO/crps_by_horizon.csv
                     results/$COMBO/weights.csv
                     results/$COMBO/weighting_notes.json
script:              scripts/aggregate_populationWeighted.py
                     sha256:0a58a5a82577c90e492a534d6b931caea8202ec9f6ad02fcbe9509ce6b06a71c
                     analysis/04_score/scripts/lib/aggregate.py
                     sha256:93dfb354e605db7bd7f281de89e66b06a8bc3201e4454f34aa4c2d45e502cef0
invocation:          "$PYTHON" scripts/aggregate_populationWeighted.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=aggregate_populationWeighted and COMBO_BASE=main.)
inputs:              analysis/04_score/01_collect/results/$COMBO/metrics_cell.csv
                     analysis/02_setup/results/<COMBO or its base>/analysis_dataset.csv
                     — the combination that answered is recorded in
                     results/$COMBO/weighting_notes.json as `weight_basis`
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every figure is a weighted groupby of a stored file.
commit:              ce0eb34
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/04_score/02_aggregate/b_populationWeighted
produced:            2026-08-29
```

**What it establishes.** Under population weighting the pool scores **28.577** against the
reference's **37.055** — a skill score of **+0.2288**, against the main path's +0.1485
(`analysis/results/aggregate_populationWeighted/conclusion.json`). Re-weighting the same
per-cell file, with no model re-run, moves the headline conclusion by **+0.080 of skill**,
which is more than any of the five setup forks moved it. The cheapest fork in the project is
the one the conclusion is most sensitive to.

**What the weighting does to the sample.** All 371 cells carry positive weight, the total is
108 901 072 person-months, and the Kish effective sample size is **215** of 371
(`results/$COMBO/weighting_notes.json`). The top decile of cells carries 29.8 % of the weight
and Vientiane Capital alone carries 21.2 %. So the concentration the unweighted mean was
already suspected of is made explicit and measurable here rather than argued about.

**The weight is per cell, not per province.** It is taken from the assembled dataset's
`population` column at each province-month, so under the population fork's back-cast child —
where the column is a per-year series — this weighting follows it with no code change. That
is what makes the two forks composable in tier 2.

alternatives-considered: **a constant weight per province**, taken once — rejected because it
would silently disagree with `popColumn_backCast` and make the tier-2 pair of those two forks
mean something neither of them means alone. **Weighting the paired comparison as well** —
**not done, and this is a known gap**: `03_compare` computes the paired difference, the
clustered standard errors and the split-level comparison from the unweighted per-cell file, so
under this row `conclusion.json` carries a re-weighted `skill_score` beside paired statistics
that are still unweighted. The row's headline is weighted and its spread is not. Fixing that
means teaching `compare_models.py` to read `weights.csv`, including a weighted clustered
standard error, which is a change to shared code that every combination runs; it is recorded
here, in `04_score/02_aggregate/claim.md` and in batch 13's report, and it belongs to the batch
that is already fixing shared scoring code.

agency: agent-autonomous. The fork and its claim are batch 5's and batch 12's; the per-cell
weight, the concentration diagnostics and the decision to leave the paired statistics
unweighted for now are the agent's.
information: agent-retrieved — the weights come from the assembled dataset and the scores from
`01_collect`, both read at run time.
