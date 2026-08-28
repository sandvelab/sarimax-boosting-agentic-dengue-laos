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

## boosted_round1 — candidate 2's forks (batch 10)

```
result:              boosted_round1/fork_leaderboard.csv
                     boosted_round1/fork_sweep.json
                     boosted_round1/sweep_runs.json
                     boosted_round1/sweep_<combination>.log
script:              AI-internal/useful-scripts/candidate_fork_sweep.py
invocation:          .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py \
                       --candidate b_boosted --base family_boosted --inherit-from main \
                       run --label boosted_round1
inputs:              analysis/04_score/02_aggregate/a_unweighted/results/<combo>/
                       metrics_summary.csv
                     analysis/03_models/03_candidate/b_boosted/results/<combo>/
                       run_cost.json, candidate_spec.json
                     for <combo> in family_boosted, features_richCalendar,
                     head_quantileEnsemble
environment:         .venv (repository machinery) for the driver; every step it runs is
                     the tree's own, under environment/chapenv
commit:              6cb1163
instructions-commit: cf97b81
```

The base is candidate 2's own main path — `a_lagBlock`, `a_negBinomial`, mean CRPS
**20.771** — and not `main`, because candidate 2 is a sibling family under an alternatives
node and never runs on the main path at all. That is the distinction batch 10 added to the
driver: a row is **measured against** `family_boosted` and **inherits** the dataset and the
other four models from `main`, and collapsing the two would have made one of them wrong.

Two combinations, one per fork, each taking that fork's non-main child with the other fork
left where it is. **Neither moved the model**: `features_richCalendar` is worth 0.396 CRPS
and `head_quantileEnsemble` costs 0.189, against the 0.565 floor the reference's own re-runs
occupy, so batch 9's promotion rule leaves both forks at their defaults.

Regenerable from the tree as it stands, in about three minutes: no fork was promoted, so all
three combinations are still where the table was copied from.

alternatives-considered: a second copy of the driver with two names changed, which is what
`chap_eval.py` argues against and what a copy per model becomes (rejected — the driver was
generalised instead, with defaults that leave every invocation recorded before batch 10
meaning what it meant); running the two siblings under `COMBO_BASE=family_boosted` so the
chain of inheritance were one deep (rejected — `combos.py` resolves one level of base by
design, and `family_boosted` holds neither the dataset nor the other models, so the lookup
would have failed rather than inherited).
agency: agent-autonomous

## ensemble_round1/ — the sweep around candidate 3's main path

```
produced:            2026-08-28, batch 11
script:              AI-internal/useful-scripts/candidate_fork_sweep.py run
invocation:          .venv/bin/python AI-internal/useful-scripts/candidate_fork_sweep.py \
                       --candidate c_ensemble --base family_ensemble --inherit-from main \
                       run --label ensemble_round1
inputs:              analysis/04_score/02_aggregate/a_unweighted/results/<combo>/metrics_summary.csv
                     analysis/03_models/03_candidate/c_ensemble/results/<combo>/run_cost.json
                     analysis/03_models/03_candidate/c_ensemble/results/<combo>/candidate_spec.json
                     for <combo> in family_ensemble and weighting_crpsWeighted
environment:         .venv (the repository's own machinery) drives; every step it runs
                     executes under environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
```

The base is candidate 3's own main path, `family_ensemble`, mean CRPS **18.817**. One fork
with one non-main child, so the table has two rows. `weighting_crpsWeighted` scores **22.838**
— the fork's alternative is worth **−4.021** CRPS, seven times the resolvable floor and in the
wrong direction, so `a_equal` stays on the main path. **Regenerable**: both combinations are
still in the tree.

The table was rebuilt with `summarise` after `ensemble_model/train.py` changed to record the
pool's component seed in the fitted object, and both combinations were re-run first; every
figure in it came back identical.

## families/ — what each candidate family scores at its own main path

```
produced:            2026-08-28, batch 11
script:              AI-internal/useful-scripts/family_leaderboard.py
                     — new in this batch, and a different question from the fork sweep:
                     across the three families rather than within one candidate
invocation:          .venv/bin/python AI-internal/useful-scripts/family_leaderboard.py \
                       --label families
inputs:              analysis/04_score/02_aggregate/a_unweighted/results/<combo>/metrics_summary.csv
                     and each family's run_cost.json and candidate_spec.json under the
                     combination it ran at its own main path — main for c_ensemble,
                     family_boosted for b_boosted, family_hierNB for a_hierNB
environment:         .venv (the repository's own machinery)
commit:              2799be5
instructions-commit: cf97b81
```

**The table the family fork was promoted from**, and `../family_rule.md` beside it is the rule,
committed before the promoted family was run under `main`. Each family is read from the
combination in which it ran with every one of its internal forks at the child that fork
declares — found by matching the stored specification's chosen child nodes against the forks'
current main paths, never by naming a combination, so a family whose forks moved since it last
ran has no row rather than a stale one. **Regenerable.**

alternatives-considered: extending `candidate_fork_sweep.py` with a subcommand instead of
adding a script (rejected — it would change that file's sha256, which is named in the
provenance of the two sweeps it has already produced, to add a function that shares almost
nothing with it); reading the families from one combination's leaderboard (impossible — an
alternatives node runs one child, so no combination contains all three).
agency: agent-autonomous
