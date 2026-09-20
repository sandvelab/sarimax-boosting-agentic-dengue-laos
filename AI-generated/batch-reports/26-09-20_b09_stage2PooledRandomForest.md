Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 9)

# Batch 9 — pooled random forest, adapted from chap-models

## 1. What this batch did

Mid-batch-8-close-out, the human said to keep exploring stage-2 candidates rather than move to
phase D, and to try an existing model from `github.com/chap-models` for stage 2. That org holds
dozens of forecasting models built to run inside the Chap platform; none is a residual-correction
model in this project's sense, so this batch adapted one rather than importing it wholesale.

**Selection** (`gh api` against the org, read directly rather than from memory): inspected
`XGBoost_for_Malawi`, `ewars_plus_template`, `Vietnam-dengue-superensemble` (all R) and
`rwanda_random_forest` (Python). Picked `rwanda_random_forest` — it needs no new environment
dependency (this project already pins `scikit-learn`), and its central structural idea, a
**random forest pooled across every location** rather than fit per location, is exactly the
cross-province-pooling fork `04_stage2/claim.md` logged as untried since batch 7.

**What was adapted, and what was not** (all logged in the node's own provenance and module
docstring): the pooling idea and the algorithm family (random forest, bagging — distinct from
`b_gradientBoosting`'s boosting) were kept. The original repo's own feature set (lag-1..3
climate and lag-1..3 target) was **not** reused — leakage-unsafe for this project's 3-month test
window, the same reasoning `a_linearLags` established in batch 4 — and replaced with
`d_linearClimate`'s exact input, so pooling is the one axis this candidate changes. The original
repo's population/log1p incidence transform was dropped (this project's stage 2 predicts a
residual, not a raw count). The original repo's `RandomizedSearchCV` hyperparameter search was
replaced with a fixed, modest configuration (`n_estimators=200, max_depth=5,
min_samples_leaf=5, max_features="sqrt"`), in the same spirit `b_gradientBoosting` chose shallow
trees over a search.

**Result: the first candidate to beat stage 1 alone on mean CRPS — and the first to fail
calibration this badly.** Mean CRPS **25.89** against stage 1 alone's 26.05 (**-0.63%**) and
against `d_linearClimate`'s 26.85 on the identical input (**-3.57%**). But empirical interval
coverage **collapses to 64.4%** against a nominal 90% (every prior candidate stayed near stage
1's own 82.7-86.8%). Per plan §2 ("a model that wins on mean CRPS while being badly calibrated
has not won"), this candidate does not earn its place either.

A third script, `03_diagnose_coverage_collapse.py`, was written specifically to ground the
"why" in a file rather than leave it as a terminal observation (Rule 1). It found: 27.5% of this
candidate's corrected forecasts are negative (impossible for a case count) — 2.4-2.5x every
per-province sibling's rate (10.8% for `a_linearLags`, 11.6% for `d_linearClimate`) and 6.8x
stage 1 alone's own rate (4.0%) — concentrated in the lowest-case-count provinces (Pearson
r=-0.53 between a province's mean case count and its negative-forecast rate; two provinces
averaging under 1 case/month have 18/24 cells corrected into negative territory, while every
province averaging over 55 cases/month has zero). The pooled correction function is shaped by
the mixed-scale training pool and overshoots on the scales it was not specifically fit to.

**The pooling idea itself is not ruled out — only this implementation of it.** A version that
preserves each province's own scale under pooling (a per-province offset or standardisation
before pooling, neither tried) is logged as an untried refinement in `04_stage2/claim.md` and
this node's own `claim.md`, not a rejected option.

Updated ranking among candidates clearing both the CRPS and calibration bars (unchanged from
batch 8): stage 1 alone (26.05) < `a_linearLags` (26.26) < `d_linearClimate` (26.85) < seasonal
climatology (26.91) < `b_gradientBoosting` (27.68) < `c_bayesianRidge` (28.07) < persistence
(28.32), with `e_pooledRandomForest` (25.89) reported alongside as CRPS-best-but-miscalibrated
rather than folded into that ranking.

**Plan updated** before any modelling (backed up first): inserted as ledger row 9 with the
human's instruction and the model-selection reasoning recorded in the plan's own §4b; the
stability phase and everything after it renumbered from rows 9–16 to 10–17.

## 2. Judgment calls logged, with agency

- **Which chap-models repo to adapt**: `agent-autonomous`, argued on environment fit (Python,
  no new dependency) and structural relevance (pooling directly addresses a named fork) over
  the R-based alternatives inspected.
- **Reusing the pooling idea but not the original repo's feature set, target transform, or
  hyperparameter search**: `agent-autonomous`, each with its own reason (leakage safety,
  contract mismatch, reproducibility/compute cost respectively), logged in the script's module
  docstring and this node's provenance rather than silently deviating from the source repo.
- **Not slotting `e_pooledRandomForest` into the single best-to-worst ranking**: `a_linearLags`
  is not moved off the main path by a candidate that fails the calibration bar — recorded
  explicitly rather than letting the lowest CRPS number quietly become the headline.
- **Seeding real randomness**: unlike `b_gradientBoosting`'s no-real-randomness configuration,
  the random forest's bootstrap resampling is genuine randomness, pinned via `random_state` and
  verified (per `/seed`) by running the script twice end to end and diffing
  `per_cell_scores.csv` and `conclusion.json` byte for byte — identical both times.

## 3. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass except `git`,
which failed only mid-batch on expected uncommitted edits and, at the end, only on the
pre-existing, out-of-scope untracked `.idea/`. Stage-1 re-derivation verified bit-for-bit
against `02_stage1`'s stored forecast (408/408 cells, max|Δ|=0.0). Determinism verified by a
full second run of `01_stage2_pooled_random_forest.py`, diffed byte for byte against the
first.

## 4. What batch 10 inherits

Five stage-2 candidates now exist. Four lose outright; the fifth (`e_pooledRandomForest`) wins
on mean CRPS but fails calibration badly, and the mechanism is understood and file-grounded.
Two forks are now explicitly logged as untried refinements rather than closed questions:
climate given a non-linear family (from batch 8), and scale-preserving pooling (from this
batch). Population and a genuinely forward climate signal remain untried from batch 7.

Nothing in this batch's own record decides whether to build the scale-preserving pooling
refinement, try population, move to phase D, or stop exploring stage-2 candidates — that
remains the human's call, as it has been since batch 7. If the human wants to keep exploring,
the scale-preserving pooling fix is the most directly motivated next step, since it targets the
specific, understood failure of the one candidate that has actually beaten stage 1 alone so
far, rather than opening a new, less-motivated axis.
