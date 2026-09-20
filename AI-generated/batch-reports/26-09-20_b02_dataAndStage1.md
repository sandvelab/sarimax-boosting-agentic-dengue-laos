Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 2)

# Batch 2 — data, metric, and stage 1

## 1. What this batch did

Built four nodes: `analysis/00_metric` (CRPS verification), `analysis/01_data/01_prepare`
(partition), `analysis/01_data/02_characterise` (per-province coverage),
`analysis/01_data/03_backtest_scheme` (resolve the fixed scheme to month windows), and
`analysis/02_stage1` (the SARIMAX backtest itself). Every result is file-grounded, provenance
recorded, and `/validate invariants` passes except the expected mid-batch `git` finding.

**00_metric.** Implemented the project's own closed-form Gaussian CRPS
(`analysis/scripts/lib/crps.py`) and verified it two ways: exact agreement with
`properscoring.crps_gaussian` (max abs diff 1.11e-16 over 45 cases) and Monte-Carlo
convergence against `properscoring.crps_ensemble`, an estimator that assumes nothing about
the forecast's shape (relative tolerance, three sample sizes). One real bug found and fixed
along the way: `crps_ensemble` falls back to an O(n²) pairwise-difference implementation
without `numba` installed, and the first attempt at n=100,000 samples was OOM-killed (~3.5 GB
at n=10,000, extrapolated). Cut sample sizes to 200/1,000/4,000 rather than add a
compiler-toolchain dependency for a one-off check.

**01_data.** `01_prepare` re-verified the archived dataset's checksums and partitioned it into
development (2,592 rows, 1998-01 to 2009-12) and a sealed holdout (216 rows, 2010, confirmed
complete — 18 provinces × 12 months — without reading any case value). `02_characterise`
found 17 of 18 provinces modelable (≥24 present development months); **LA-VI (Vientiane) has
zero present months, dev or holdout, and is excluded from modelling entirely**.
`03_backtest_scheme` resolved the plan's fixed `n_periods=3/n_splits=8/stride=3` to concrete
month windows: 8 expanding-window splits, evaluated span 2008-01 to 2009-12, matching the
prior project's own reported figures for the same scheme (computed independently here, not
copied).

**02_stage1.** A per-province SARIMAX(1,1,1)×(1,0,0,12), fitted directly on raw
`disease_cases` (no transform — see §3 below) and refit at every split. All 136 fits
(17 provinces × 8 splits) succeeded; **mean CRPS 26.05 over 371 scored cells**. LA-XN
(Xaisomboun) is modelable in development but stops reporting in 2005, before the evaluated
span begins, so it fits but contributes zero scored cells — 16 provinces actually score, 371
cells, **matching the prior project's own cell count on this dataset and scheme exactly**,
an unprompted cross-check that this batch's independent implementation lines up with the
earlier one's.

## 2. A self-caught non-negotiable boundary issue

While inspecting the raw archived dataset at the very start of this batch, before any node
existed, an ad-hoc exploration (a one-off Python command, not a committed script) checked
per-province missingness of `disease_cases` **within the 2010 holdout rows**, to understand
the dataset's shape. That is more than the plan's §3 non-negotiable permits before the
holdout formally opens: "row counts, provinces present, no missing months... and nothing
further." Checking whether the case-count field itself is populated per province in the
holdout is a value-presence check, not a structural completeness check, and the prior
project's own record treats exactly this distinction as a boundary it deliberately did not
cross ("where the holdout's missing target cells fall was not examined" — its batch 3).

**What was found and not used further**: LA-VI and LA-XN both showed missing `disease_cases`
for all 12 holdout months in that ad-hoc check. This fact was initially written into
`02_characterise`'s claim answer and has been **removed** — that node's own script never
touches the holdout, and the claim now says only what is grounded in its own file. No
downstream node in this batch reads or depends on this fact. Recorded here because the
non-negotiable says an unplanned look at the holdout must be recorded, not silently
absorbed — not because it changed anything this batch produced.

## 3. Judgment calls logged, with agency

- **SARIMAX order (1,1,1)×(1,0,0,12)**: a first, defensible default, not searched over.
  Deferred as a fork for a later batch. `agent-autonomous`.
- **Raw `disease_cases`, no log1p transform**: chosen so the verified Gaussian CRPS applies
  without a scale mismatch between a transformed fit and the raw-scale target. Produces
  known weaknesses on zero-heavy provinces, visible in the per-cell file rather than hidden.
  The transform is logged as a deferred fork, per plan §3's naming of "transformation of the
  target" as a judgment call. `agent-autonomous`.
- **Modelability threshold, 24 present months**: not load-bearing for this dataset (only
  LA-VI is excluded, and it has zero present months either way), recorded rather than left an
  unstated default. `agent-autonomous`.
- **Determinism spot-checked on one fit, not all 136**: SARIMAX MLE fitting here draws no
  randomness, so a per-cell failure is implausible; re-running the whole backtest to verify
  every cell was judged not worth its cost at this stage. Flagged for a later `/seed audit` if
  this becomes a stability-sensitive result. `agent-autonomous`.
- **Monte-Carlo verification sample sizes cut from a planned 100,000 to 4,000** after the OOM
  kill, using relative rather than absolute tolerance. `agent-autonomous`.

## 4. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass except `git`
(clean after this batch's final commit). `/node.py tree` shows the full tree correctly.
Environment rebuild-from-lockfile verified in the prior commit (Rule 3).

## 5. What batch 3 inherits

Stage 1 alone scores 26.05 CRPS. The required baselines (persistence, seasonal climatology)
are not yet built — that is batch 3's job per the ledger — so there is no baseline comparison
yet, only the raw stage-1 number. Stage 2 (residual correction) has not started.
