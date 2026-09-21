Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 12)

# Batch 12 — the stability run

## 1. What this batch did

Batch 11 froze a development perturbation manifest of 29 planned parametric perturbations,
6 siblings already in the tree and 5 alternatives not run. This batch ran it. All figures
below are read from `analysis/06_stability/results/` — `conclusions.csv`, `run_log.csv`,
`run_summary.json` and each combination's `conclusion.json`.

**The runner.** The candidates' own scripts fix their constants and refuse a stage-1
forecast that differs from `02_stage1`'s stored one, so they cannot run a perturbation of
stage 1. A separate parametrised pipeline, `lib/stage2_perturb.py`, exposes every judgment
call the manifest names: stage 1's order, seasonal order, stationarity enforcement and
training window; the scheme's split count, stride and modelability threshold; and the
main-path stage 2's target winsorisation, standardisation, clipping, correction bound,
per-horizon versus pooled fitting, feature set, family and hyperparameters, seed, warm-up,
in-window error construction and abstention threshold. It reuses the shared library wherever
the quantity is the same and re-implements only the feature row, because the feature set is
itself one of the perturbed choices.

**The gate.** Before any perturbation ran, the runner's `main` combination — every parameter
at its main-path value — was compared with `04_stage2/g_oosErrorBoosting`'s stored per-cell
scores on every shared column: 408 rows, 0 mismatched values, two-stage mean CRPS 25.164
reproduced exactly. The runner also refuses a manifest that no longer hashes to its frozen
digest, and a manifest row without a configuration or a configuration without a row. Two
perturbations that change nothing binding (a higher abstention threshold; a modelability
threshold of 36 months, which every included province clears) reproduced the main path's
25.164 exactly, a second check of the same kind.

**The run.** All 29 planned rows ran: 1,937 s of wall-clock against the 3,600 s ceiling, the
true rolling refit of the in-window errors accounting for 990 s of it. The budget line fell
below every row. The first attempt stopped at that rolling-refit row: a fresh SARIMAX fit on a
truncated series diverged at three origins per split and returned non-finite predictions.
Those origins now contribute no training row, the six rows that had completed were re-run
from scratch with the rest, and their conclusions did not change to any printed digit.

## 2. What the run found — headline counts only

Batch 13 owes the distribution report. What `conclusions.csv` already shows, as counts:

- **All 29 tier-2 perturbations keep the two-stage ensemble ahead of stage 1 alone on mean
  CRPS with coverage not worse.** The change against stage 1 alone ranges from −0.70% (true
  rolling refit of the in-window errors) to −10.64% (the airline stage 1), median −3.32%
  against the main path's −3.41%.
- Of the 36 rows that ran (main, 6 siblings, 29 perturbations), the ensemble beats stage 1 in
  32; the four losses are the batch 4–8 siblings trained on the in-sample one-step residual.
  The one CRPS win with worse coverage is `e_pooledRandomForest`.
- Where stage 1 itself changes, the comparison is internal to the combination: with the
  airline specification stage 1 alone scores 29.15 and the corrected forecast 26.05; with
  stationarity enforced 26.81 and 24.55; with no differencing 24.93 and 24.09; with a rolling
  72-month window 23.99 and 23.50; on Chap's default scheme (7 splits, stride 1; 333 cells)
  35.00 and 32.50, the ensemble improving 6 of 7 splits.
- Several perturbations beat the main path on the development data: the level-only feature
  set (−6.53%), the bounded correction (−5.85%), dropping the cross-province term (−5.84%),
  adding climate anomalies (−5.78%), depth-2 trees (−4.19%). None of these was selected; the
  main path stays as frozen, and these are batch 13's material for saying what the margin
  turns on.
- The rows with the smallest margins are the ones that change how the training errors are
  made or how much data they use: the true rolling refit (−0.70%), a 2002 window start
  (−0.92%), no winsorisation (−1.62%); and split-level agreement is weakest for the rolling
  72-month window (3 of 8 splits improved) and 4 of 8 for six other rows.

## 3. Judgment calls logged, with agency

- **A separate parametrised pipeline with a reproduction gate**, rather than editing the
  candidates' scripts: `agent-autonomous`; the gate is what makes a perturbation's difference
  attributable to the perturbation.
- **Skipping origins whose refit diverges**, recorded via per-split row counts (3 per split
  below `main`'s) and a documented limitation of the non-finite counter: `agent-autonomous`.
- **Re-running all rows after the library fix** rather than resuming: `agent-autonomous`, so
  every result sits under one digest.
- **Not promoting any better-scoring perturbation**: the main path was frozen before the run
  so that what is reported is a measurement, not a selection (plan §3); `agent-autonomous`.

## 4. Checks run

`/validate invariants`: `tree`, `provenance`, `hashes`, `plots`, `seeds`, `claims`, `combos`
(every `results/<combination>/` directory is named by the frozen manifest or is `main`),
`freeze`, `crossing`, `pool` pass; `git` fails only on the pre-existing untracked `.idea/`.
Gate: 408 rows, 0 mismatches. Manifest digest unchanged since the freeze.

## 5. What batch 13 inherits

`conclusions.csv` with one row per manifest row, and per-combination per-cell files for
anything finer (by province, by horizon). Batch 13 writes the distribution report: which
choices the central comparison is insensitive to, which move its size, whether any move its
sign (none did on development data), the tier-3 absences restated, and each conclusion into
the claim collection. Then batch 14 freezes the holdout manifest.
