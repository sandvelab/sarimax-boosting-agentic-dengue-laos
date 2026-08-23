# Provenance — the backtest scheme

```
result:              results/backtest_scheme_chosen.json
                     results/backtest_scheme_candidates.csv
                     results/split_schedule.csv
                     results/evaluable_cells_by_province.csv
script:              scripts/check_backtest_scheme.py
                     sha256:e44094ffd1391e1155984ad7811a63e439a348c35dde505444071f4421ad4dc2
invocation:          "$PYTHON" scripts/check_backtest_scheme.py
                     (from the node directory, via run.sh)
inputs:              ../01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0.
                     The split schedule and the region filter are chap-core's own
                     `train_test_generator` and `validate_and_filter_dataset_for_evaluation`,
                     called directly; the schedule is read off what they return rather than
                     recomputed from the formula in their docstrings.
seeds:               none. The splitter is an index calculation over the period range;
                     project seed 20260822 has no surface.
commit:              1ae2649
instructions-commit: 15b4ba9
node:                analysis/01_data/02_characterise
produced:            2026-08-23
```

**The scheme, fixed here and not moved again.** Development: `n_periods 3`, `n_splits 8`,
`stride 3`, `n_retrain 1` — evaluating 2008-01 to 2009-12 from a training set ending 2007-12.
Phase E: `n_periods 3`, `n_splits 4`, `stride 3` on the full file — evaluating exactly
2010-01 to 2010-12 from a training set ending 2009-12, verified on a synthetic calendar
rather than on the archived original, because a split schedule depends only on the period
range and answering it does not require opening the holdout.

**What the metric is a mean over, which is not what it looks like.** The region filter drops
Vientiane, leaving 17 provinces and a nominal 17 × 8 × 3 = 408 cells. Missing observations
are dropped before the metric is computed, so Xaisomboun — kept by the filter because its
*training* period has data — contributes nothing to the evaluated span, and Phongsaly
contributes 11 of 24. The headline mean is over **16 provinces and 371 cells**.

alternatives-considered: seven candidate schemes were run and are stored in
`backtest_scheme_candidates.csv`. `stride 1` was rejected for every `n_splits`: successive
splits then overlap in the months they predict, so the splits are strongly correlated, the
design is unbalanced, and batch 2's identity between the platform's mean over cells and a
mean over regions × splits no longer holds. Among the `stride 3` options, `n_splits 4`
evaluates only 2009 and makes the development estimate a statement about one dengue season;
`n_splits 12` evaluates three years but, with `n_retrain 1`, leaves the single fit made on
data ending 2006-12 while predicting through 2009. `n_splits 8` is the middle: ten years of
training before the first split and two complete seasonal cycles evaluated. `n_retrain` is
itself a judgment call and is left at chap-core's default of 1 here, flagged as a phase-D
perturbation rather than tuned. `n_periods` was not chosen freely — batch 2 found chap-core
forcing `n_periods=3` for the EWARS model and the chapkit EWARS service declaring
`prediction_periods: 3`, so a different horizon would mean the plan's central comparison
never happens.

**A consequence worth stating.** Development and holdout differ in `n_splits` (8 against 4)
because the evaluated windows differ in length by design — two years against one. `n_periods`
and `stride` are identical, and the per-cell CRPS is identical, so the two are comparable
through the skill score the plan's §4b fixes at the root, which is a ratio within each
dataset. Raw CRPS levels are not comparable between them and are not treated as though they
were.

agency: agent-autonomous. That the scheme must be fixed in this batch and never moved is the
plan's (§7, batch 3); the values, the candidate set and the reasoning are the agent's.
The `n_periods = 3` constraint is `agent-on-human-assessment` in origin — it follows from the
human's choice of `chapkit_ewars_model` as the reference (§4b, 2026-08-23).
