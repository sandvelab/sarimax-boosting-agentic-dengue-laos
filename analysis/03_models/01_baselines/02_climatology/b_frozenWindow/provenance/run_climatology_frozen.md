# Provenance — the frozen-window climatology baseline, on its own combination

```
result:              results/$COMBO/eval.nc
                     results/$COMBO/eval.log
                     results/$COMBO/fitted_model.json
                     results/$COMBO/model_spec.json
                     results/$COMBO/run_cost.json
combinations:        climatology_frozenWindow
script:              scripts/run_climatology_frozen.py
                     sha256:99747bdd94c6c6b2bdd35fe4a8136e446d3dbd5b5cb114a11937f08e5630dc32
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:b05916bff2567b79571ba2ce27dbf26ce5cf5e6540c278ba5b570df1907688f5
                     the model itself, scripts/climatology_model/:
                     MLproject       sha256:9c9113179e76febd…
                     train.py        sha256:0e338c2fc8d6d41d…
                     predict.py      sha256:d6f029097718dfe4…
                     pyproject.toml  sha256:157da40a6705f29b…
                     uv.lock         sha256:6189ab869f2df637…
                     (the full digests are in results/$COMBO/model_spec.json, written by
                     the run before it started)
invocation:          "$PYTHON" scripts/run_climatology_frozen.py
                     with COMBO=climatology_frozenWindow and COMBO_BASE=main, set by
                     environment/chapenv/bin/python \
                       analysis/05_stability/scripts/run_manifest.py --batch 22
                     which issues
                     environment/chapenv/bin/chap eval
                       --model-name <node>/scripts/climatology_model
                       --dataset-csv analysis/02_setup/results/main/analysis_dataset.csv
                       --output-file results/$COMBO/eval.nc
                       --backtest-params.n-periods 3 --backtest-params.n-splits 8
                       --backtest-params.stride 3 --backtest-params.n-retrain 1
                     with every flag read from the assembled setup, not from this script.
                     The exact command line is the first line of results/$COMBO/eval.log.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     resolved through COMBO_BASE, because a fork on which window estimates
                     a baseline's distribution changes no dataset; which combination
                     answered the lookup is recorded as `setup_from_combo` in
                     model_spec.json
                     analysis/02_setup/results/main/setup_spec.json (the flags)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     for the platform. The *model* runs in its own environment, which
                     chap-core builds from the model's pyproject.toml and uv.lock; the
                     runner verifies after the run that the lockfile chap-core built
                     from is byte-identical to the tracked one, and records the result
                     as `shipped_lockfile_is_the_one_built_from`.
seeds:               none. The 1 000 draws per cell are the frozen table's empirical
                     quantile function evaluated at the fixed levels (i + 0.5)/1000, not
                     sampled from it. Project seed 20260822 has no surface here.
                     Verified rather than asserted:
                     AI-generated/determinism-checks/model_determinism.json, which names
                     this node from batch 22 onward.
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/03_models/01_baselines/02_climatology/b_frozenWindow
produced:            2026-08-29
```

**What it establishes.** The seasonal table estimated once from the training frame and held
fixed scores **24.869 mean CRPS** over the same 371 cells against the expanding window's
**24.337** (`analysis/04_score/03_compare/results/climatology_frozenWindow/leaderboard.csv`).
Freezing costs **0.532 CRPS**, which is *inside* the 0.565 floor below which nothing on this
dataset can be attributed to a model at all.

**Two dengue seasons of data are worth nothing measurable to this baseline.** The training
period ends 2007-12 and the evaluation runs to 2009-12, so the frozen table forecasts two
seasons it has never seen, on a series whose reporting improved throughout — and the
difference does not clear the noise. The model's own node argued before the run that the
choice mattered *because* of that gap; measured, it does not. Calibration moves in the same
small way: 10–90 coverage 0.639 against 0.650, 25–75 coverage 0.520 against 0.542.

**The effect on the model this project reports is smaller still.** The pool takes this
baseline as one of four equally weighted members, and its mean CRPS moves from 18.817 to
18.872 — 0.055 CRPS, a skill score of +0.1460 against the main path's +0.1485. This is the
**smallest move of any tier-1 row run so far**, and the fork's sibling row is the largest.

alternatives-considered: **one contract directory with a `window` switch**, since the fork's
whole content is one branch inside `predict`. Rejected for two reasons that point the same
way: a Chap contract directory is copied whole into chap-core's run directory, so a library
shared between the two children would not travel with either model; and editing the sibling's
files would change the bytes of the model that produced six committed combinations' results,
which is the objection batch 11 raised against the assembler lift. The cost paid instead is
that both children carry the same table build in `train.py`, differing in one recorded field.

agency: agent-autonomous. The requirement for a seasonal climatology baseline is the plan's
(`human-set`, §4); that the estimation window is a fork was settled in batch 6; building and
running this child is the manifest's row 9.
information: agent-retrieved — every number quoted above is read from the files this run
produced.
