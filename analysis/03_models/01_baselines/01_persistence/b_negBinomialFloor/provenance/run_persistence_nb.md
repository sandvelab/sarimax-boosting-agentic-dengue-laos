# Provenance — the parametric persistence baseline, on its own combination

```
result:              results/$COMBO/eval.nc
                     results/$COMBO/eval.log
                     results/$COMBO/fitted_model.json
                     results/$COMBO/model_spec.json
                     results/$COMBO/run_cost.json
combinations:        persistence_negBinomialFloor
script:              scripts/run_persistence_nb.py
                     sha256:6b0b4482d702c65332e3a1b6f3b1b3c073fd081781540bc058ae3f449515e820
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:b05916bff2567b79571ba2ce27dbf26ce5cf5e6540c278ba5b570df1907688f5
                     the model itself, scripts/persistence_model/:
                     MLproject       sha256:d629e5c92e033a85…
                     negbinom.py     sha256:3eeaeddc9c4dde2a…
                     train.py        sha256:8cb8222f9cbb4c50…
                     predict.py      sha256:121de7f5cfda0d4f…
                     pyproject.toml  sha256:b468929b6e64b7d7…
                     uv.lock         sha256:5cb8569317a55511…
                     (the full digests are in results/$COMBO/model_spec.json, written by
                     the run before it started)
invocation:          "$PYTHON" scripts/run_persistence_nb.py
                     with COMBO=persistence_negBinomialFloor and COMBO_BASE=main, set by
                     environment/chapenv/bin/python \
                       analysis/05_stability/scripts/run_manifest.py --batch 22
                     which issues
                     environment/chapenv/bin/chap eval
                       --model-name <node>/scripts/persistence_model
                       --dataset-csv analysis/02_setup/results/main/analysis_dataset.csv
                       --output-file results/$COMBO/eval.nc
                       --backtest-params.n-periods 3 --backtest-params.n-splits 8
                       --backtest-params.stride 3 --backtest-params.n-retrain 1
                     with every flag read from the assembled setup, not from this script.
                     The exact command line is the first line of results/$COMBO/eval.log.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     resolved through COMBO_BASE, because a fork on how a baseline wraps
                     its uncertainty changes no dataset; which combination answered the
                     lookup is recorded as `setup_from_combo` in model_spec.json
                     analysis/02_setup/results/main/setup_spec.json (the flags)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     for the platform. The *model* runs in its own environment, which
                     chap-core builds from the model's pyproject.toml and uv.lock; the
                     runner verifies after the run that the lockfile chap-core built
                     from is byte-identical to the tracked one, and records the result
                     as `shipped_lockfile_is_the_one_built_from`.
seeds:               none. The dispersion is fitted by a deterministic search on a fixed
                     grid, and the 1 000 draws per cell are the fitted negative
                     binomial's quantile function evaluated at the fixed levels
                     (i + 0.5)/1000, not sampled from it. Project seed 20260822 has no
                     surface here. Verified rather than asserted:
                     AI-generated/determinism-checks/model_determinism.json, which names
                     this node from batch 22 onward.
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/03_models/01_baselines/01_persistence/b_negBinomialFloor
produced:            2026-08-29
```

**What it establishes.** The second of the two published constructions for a probabilistic
persistence baseline, scored on the identical path as the first. It scores **20.698 mean
CRPS** over the same 371 cells against the main path's **24.879**
(`analysis/04_score/03_compare/results/persistence_negBinomialFloor/leaderboard.csv`), so the
construction the main path rejected is **4.181 CRPS better** — more than seven times the
0.565 CRPS floor below which nothing on this dataset can be attributed to a model. It is
also better calibrated on both intervals: 10–90 coverage 0.720 against 0.666, 25–75
coverage 0.550 against 0.491.

**It beats the reference model.** 20.698 against the reference's 22.098, a paired per-cell
difference of −1.400 with a split-clustered standard error of 1.424 — 0.98 standard errors,
which does not separate them, and is not reported as though it did. A model the plan's §4
requires as a *baseline* is nonetheless ahead of the field's own model on the point estimate.

**The constants are the source's.** Floor 0.2, window five observations, dispersion by
maximum likelihood: all from the KIT baseline for the German COVID-19 Forecast Hub
(<https://github.com/KITmetricslab/KIT-baseline>), which batch 6 read and recorded in
`AI-generated/vertical-slice/provenance.md` as the construction not taken. Choosing any of
them here would have let the path not taken be tuned against the path taken.

**Two arbitrary constants, not one.** Batch 6 rejected this construction because the floor
would be doing visible work in the majority of months that report zero. That criticism holds
and it understates the problem: on this dataset the maximum-likelihood dispersion often does
not exist — an all-zero window drives the likelihood monotonically toward a point mass at
zero — so the estimator needs bounds, and on the development training frame those bounds bind
for **six of the seventeen provinces that report at all**, five at the lower bound and one at
the upper (`results/$COMBO/fitted_model.json`, `provinces_at_a_dispersion_bound`). The
second constant is doing its work in exactly the provinces where the first one is. The
construction is better anyway, which is the finding.

**A gap in the record, stated rather than closed.** The dispersion this model *forecast*
with was re-estimated inside `predict` from the expanding historic frame at each split, and
chap-core does not surface a model's stdout, so those per-split estimates are not in any
file — `fitted_model.json` holds the training-frame fit, which is what the model knew at
fitting time and the fallback, not the parameters behind the forecasts. This is the third
time in this project that moving fitting into `predict` has cost the record rather than the
score (batch 4 on the reference, batch 21 on `04_fitTime/b_refitAtPredict`). Closing it
means a place for a model to write per-split diagnostics that outlives chap-core's run
directory, which is a change to the shared `chap_eval.py`; it is left to batch 14, which
touches that file and re-runs every combination configured by it.

alternatives-considered: **fitting the dispersion in `train` and freezing it**, so that this
child would differ from its sibling in the parametric form alone. Rejected: the source
re-estimates from the last five observations available at forecast time, and the sibling
already takes its anchor from the historic frame, so a frozen dispersion beside a moving mean
is a hybrid neither published construction describes. The consequence is recorded rather
than hidden — this fork moves where the spread is estimated as well as its form, and that is
a property of the two constructions rather than a confound introduced here; the fork next
door, `02_climatology`, isolates the window question on its own. Also considered and
rejected: **one contract directory with a `construction` switch**, which would have made the
fork a configuration option rather than a path in the tree, and would have re-hashed a model
that produced six committed combinations' results.

agency: agent-autonomous. The requirement for a persistence baseline is the plan's
(`human-set`, §4); that its construction is a fork was settled in batch 6; building and
running this child is the manifest's row 10.
information: agent-retrieved — the construction's constants were re-read from the KIT
repository on 2026-08-29; every number quoted above is read from the files this run produced.
