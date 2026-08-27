# Provenance — candidate-forks

One section per file, appended and never overwritten (`AGENTS.md` §8).

## round1_batch8Defaults/ — the sweep around the batch-8 configuration

```
produced:            2026-08-27, batch 9
script:              AI-internal/useful-scripts/candidate_fork_sweep.py run
                     (at the time it ran, the driver had no --label and wrote to this
                     folder's root; the files were moved into round1_batch8Defaults/
                     unchanged when the driver gained --label, in commit 15b8516)
invocation:          .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py run
inputs:              analysis/04_score/02_aggregate/a_unweighted/results/<combo>/metrics_summary.csv
                     analysis/03_models/03_candidate/a_hierNB/results/<combo>/run_cost.json
                     analysis/03_models/03_candidate/a_hierNB/results/<combo>/candidate_spec.json
                     for <combo> in main and the nine non-main children of the six forks
environment:         .venv (the repository's own machinery) drives; every step it runs
                     executes under environment/ (project main)
commit:              49825b5
instructions-commit: cf97b81
```

The base is the batch-8 configuration: `a_negBinomial`, `a_lagged`, `a_offset`,
`a_trainOnly`, `a_none`, `a_shared`, mean CRPS **26.100**. Nine combinations, each moving one
fork and inheriting the rest from `main`. **Not regenerable**: the tree's per-combination
results behind this table were replaced by round 2, and rebuilding them would require
checking out commit `49825b5`. This is the table the promotion was decided from and it is
kept for that reason.

## promotion_rule.md — the rule the promotion was made by

```
produced:            2026-08-27, batch 9, by hand
commit:              b987640
```

Written after `round1_batch8Defaults/fork_leaderboard.csv` existed and **before** the
promoted combination was run, and committed in that state, so that what it decides cannot
have been fitted to what it decided. It is a decision record, not a derived document.

## round2_promoted/ — the sweep around the promoted main path

```
produced:            2026-08-27, batch 9
script:              AI-internal/useful-scripts/candidate_fork_sweep.py
invocation:          .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py \
                       run --label round2_promoted
                     .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py \
                       compare-rounds --before round1_batch8Defaults --after round2_promoted
inputs:              the same per-combination files as round 1, plus
                     round1_batch8Defaults/fork_leaderboard.csv for the comparison
environment:         as above
commit:              15b8516
instructions-commit: cf97b81
```

The base is the promoted main path — `c_hurdle`, `c_climateFree`, `a_offset`, `a_trainOnly`,
`a_none`, `b_provinceScaled`, configuration `28c7c617d5c2…`, mean CRPS **23.698**. The nine
combinations are the non-main children *of that main path*, so three of them
(`observation_negBinomial`, `covariates_lagged`, `yearVariance_shared`) are the children the
promotion demoted. Regenerable from the tree as it now stands, in about nine minutes.

`fork_interaction.csv` and `fork_interaction.json` compare the two rounds: what each child
was worth around the earlier base against what it is worth around the later one. Their
headline is that three forks worth **4.632** CRPS one at a time delivered **2.402** together,
and that two of the nine children measured in both rounds reversed sign.
