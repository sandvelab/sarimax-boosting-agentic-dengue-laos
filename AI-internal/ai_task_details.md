# Task details

The expanded entry for each task in `ai_task_history.md`: what was produced, the design
decisions, the files affected, and what a future session would need to know. Include
follow-ups, and say plainly where something did not work.

## T1: Reset for a new project, and batch 1 — orient and set up

Full account in `AI-generated/batch-reports/26-09-20_b01_orientAndSetUp.md`; this entry
summarises it.

**Context.** The human asked to start a new, genuinely different project in this repository
(not an extension of the one already here), specified as: a SARIMAX-family model (stage 1)
whose residuals are corrected by a second model of an open family (stage 2), a two-stage
boosting-style ensemble in the general statistical sense — not an ensemble built from
gradient-boosted trees specifically. Since `AGENTS.md` §1/§9 hold this repository to one
project at a time, and the prior project's full record already exists at a separate GitHub
remote, the human confirmed: delete the prior project's own content here rather than
archive-move it.

**What was removed** (git history retains it; the separate remote has the full record too):
`analysis/`, `Human-AI-collaboration/{claims content, manuscript files}`, `AI-generated/`
(all of it), `Archive/case-source-material/`, `Archive/plan-as-delivered/` (the prior plan's
snapshot), the prior project's environment pin (`environment/{environment.yml,Dockerfile,
install-chap.sh,lock.txt}`), `AI-internal/{data-acquisition,reconnaissance,vertical-slice}/`,
the prior plan file, and every `AI-internal/useful-scripts/*.py|*.sh` file not directly
referenced by a generic skill command or `.claude/settings.json` (checked by grep before
deleting — 4 scripts survive: `node.py`, `check_invariants.py`, `claims.py`,
`build_hierarchical_report.py`; everything else, e.g. the clean-room harness and the various
`check_*_defence.py` outsider-critique scripts, was built to defend that specific project's
specific findings and does not generalise).

**What was kept**: `Archive/lao-dataset/`, `Archive/lao-population/`, `Archive/sibling-datasets/`
(raw imports, not that project's output — re-verified by checksum, both pass); `AGENTS.md`,
`CLAUDE.md`, `MOTIVATION.md`, both licences, `folder-structure.md`, `setup-guide.md`,
`.claude/` (all generic method files, unchanged); `AI-internal/skill-references/`.

**What was reset to blank** (folder kept, content cleared, README updated to drop dead
references): `AI-generated/README.md` and its `.gitkeep`; `Human-AI-collaboration/claims/
claims.md` (template only); `Human-AI-collaboration/manuscript/README.md`'s "Currently here";
`Archive/README.md`'s "Currently here"; `Human-input/Plans for AI generation/README.md`'s
"Currently here"; `AI-internal/README.md`'s folder table; `AI-internal/useful-scripts/README.md`'s
script table (4 rows instead of ~20); `AI-internal/ai_task_history.md` and
`ai_task_details.md`; `environment/README.md` and a placeholder `environment/environment.yml`.

**New content written**: the plan
(`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md` — aim, success
criterion centred on the internal stage-1-vs-two-stage comparison rather than an external
platform-comparison exercise, non-negotiables carried over from the prior project's holdout
discipline, decisions already made including *not* routing evaluation through Chap this
time, and a six-phase, fifteen-row batch ledger sketch); `readme-at-start.md`; the top-level
`README.md`; the root `analysis/claim.md` and a childless `analysis/run.sh`;
`Archive/plan-as-delivered/` recreated for this plan (copy, `(IS_SHADOW)`-marked, with
`provenance.md` recording both checksums).

**One methodological change (Rule 4)**: `AI-internal/useful-scripts/node.py`'s
`RUN_HEADER` template hard-coded `environment/chapenv/bin/python`. That is a name specific to
the prior project's Chap-based pinned environment, not a property of the generic node
machinery — found by grepping the whole repository for `chapenv` and finding this one
surviving reference outside deleted files. Changed to `environment/env/bin/python`;
`environment/README.md` updated to state the convention explicitly (build the pinned
environment at `environment/env/`, invoke directly, never activate — matching `.venv`'s own
convention in `AGENTS.md` §8).

**Checks run**: `check_invariants.py` passes except `git` (working tree uncommitted at the
point it was run mid-batch, resolved by this batch's commit); `node.py tree` prints the
single root node; both archived datasets' `sha256sums.txt` verify with `shasum -a 256 -c`.

**Follow-ups / open questions**, raised to the human rather than settled silently: the
backtest scheme (the prior project's was partly shaped by a Chap constraint that does not
apply here); whether the prior project's EWARS score is worth citing at all, given the plan
already makes it optional; and environment scoping, deliberately deferred to batch 2 once
stage 1's actual library needs are known rather than guessed now.

## T2: Recover from a crash mid-batch-2, then run batches 3–7

Full account in each batch's own report,
`AI-generated/batch-reports/26-09-20_b0{2,3,4,5,6,7}_*.md`; this entry summarises the whole
session.

**Context.** A prior session's machine crashed while closing out batch 2 (data, metric,
stage 1) — the "After" commit for `02_stage1` existed, but the wrap-up edits it depends on
(provenance corrections, the root claim answer, the batch report) were still uncommitted in
the working tree. This session began by reconstructing that state rather than redoing it:
diffed every uncommitted change against the actual files, re-verified each provenance
record's sha256 by hand, confirmed the plan-ledger and batch-report edits were internally
consistent, and committed the close-out (`ae2e5f8`) once verified rather than trusting the
uncommitted diff on its own.

**What batch 2's close-out fixed**: three provenance records
(`00_metric/provenance/verify_crps.md`, `01_data/03_backtest_scheme/provenance/
compute_schedule.md`, `02_stage1/provenance/sarimax_backtest.md`) had a relative path one
level too deep, pointing at a nonexistent `scripts/lib/` outside `analysis/scripts/lib/`
rather than inside it — a bug introduced when writing the records, not a computation error;
the recorded sha256 hashes were correct throughout and re-verified against the real files
before the fix was trusted.

**Batches 3–7**, run as five sequential background agents, each verified (`git log`, `git
status`, `check_invariants.py`) before the next was launched:

- **Batch 3 — baselines** (`analysis/03_baselines/`): persistence and seasonal climatology,
  scored through the identical pipeline and cell set as stage 1. Neither baseline's forecast
  is naturally a Gaussian, so each was given a sigma drawn from the historical quantity its
  point forecast is built from (persistence: std of training-window one-step differences;
  climatology: std of the same calendar month's training-window values) rather than an
  invented free parameter — an `agent-autonomous` judgment call, logged in each node's
  provenance. Result: stage 1 (26.05) beats persistence (28.32, −7.99%) and climatology
  (26.91, −3.20%) — the backtest resolves, modestly.
- **Batch 4 — stage-2 contract and first candidate** (`analysis/04_stage2/a_linearLags`):
  established the contract — stage 1's forecast re-derived independently and verified
  bit-identical to `02_stage1`'s stored output (408/408 cells) rather than importing its
  closed script, since a node's own output is never edited or reached into. First candidate:
  OLS on stage 1's lag-12 in-sample residual plus cyclical calendar month (lag-1 excluded as
  leaking within a 3-month test window), sigma left at stage 1's value, interval coverage
  tracked rather than assumed unaffected. Result: 26.26, 0.78% worse than stage 1 alone — the
  project's first negative result on its central question.
- **Batch 5 — tree-based candidate** (`04_stage2/b_gradientBoosting`): a regularised
  gradient-boosting regressor on the same minimal input as batch 4, to isolate the
  model-family comparison from the input-set question. Required pinning `scikit-learn`
  (Rule 3: declarative spec, re-resolved lockfile, verified clean rebuild — `environment/
  README.md` updated in the same batch). Result: 27.68, 6.25% worse than stage 1 alone, and
  worse than the linear candidate. Also fixed, visibly, a stale line in the root
  `analysis/claim.md` still citing the prior project's external reference three batches after
  plan §4b settled that this project cites none.
- **Batch 6 — Bayesian candidate** (`04_stage2/c_bayesianRidge`): the one family genuinely
  different in kind from the other two — a Bayesian ridge regression whose own posterior
  predictive variance is combined with stage 1's forecast variance for the final interval,
  rather than borrowing stage 1's sigma unchanged as the other two candidates did. Result:
  28.07 CRPS, the worst of the three on that metric, but the best-calibrated (86.8% empirical
  coverage against a nominal 90%, vs. 82.7% for stage 1 alone) — the wider, better-calibrated
  interval costs more CRPS than the mean correction recovers.
- **Batch 7 — main-path decision and input-space forks**: with all three stage-2 candidates
  losing to stage 1 alone, formalised `a_linearLags` as `04_stage2`'s main path as the
  least-bad candidate — explicitly not an endorsement that stage 2 earns its place, a
  distinction the root `analysis/claim.md` now states plainly. Logged, as a required explicit
  fork rather than a silent default (plan §3), that every stage-2 candidate so far shares one
  untested input set: climate covariates (`rainfall`, `mean_temperature`,
  `mean_relative_humidity`) and `population` already sit unused in `development.csv`, flagged
  as the most plausible untried route to a stage-2 model that helps, each costing roughly a
  full batch to explore and none run this session.

**Honest development ranking** (mean CRPS, lower is better): stage 1 alone (26.05) <
`a_linearLags` (26.26) < seasonal climatology (26.91) < `b_gradientBoosting` (27.68) <
`c_bayesianRidge` (28.07) < persistence (28.32). The project's central comparison (plan §1,
§2) currently reads: no stage-2 family tried beats stage 1 alone, on the one input set tried
so far.

**Also done**: `readme-at-start.md`'s "Status" and "Main environment" rows, unchanged since
batch 2 and increasingly stale (still said "batch 1 complete", "environment scoping remains
open", "stage-2 libraries not yet added"), brought current.

**Checks run**: `check_invariants.py` clean after every batch's close-out commit (only the
expected mid-batch `git` finding, and the pre-existing, out-of-scope untracked `.idea/`
left alone throughout — a JetBrains project folder, not part of this project's method, never
added to `.gitignore` without being asked).

**Follow-ups**, explicitly not this session's job: phase D (stability/perturbation, ledger
rows 8–10) has not started — the perturbation manifest still needs enumerating (stage 1
order/spec, stage-2 family and its inputs, combination rule, training window, zero-handling),
costing, freezing and running. The climate-covariate and population stage-2 forks are logged
but unbuilt. Nothing from this session has been pushed to the remote.

## T3: Batch 8 — the climate-covariate stage-2 fork

Full account in `AI-generated/batch-reports/26-09-20_b08_stage2LinearClimate.md`.

**Context.** Batch 7 closed with an explicit choice left to the human: move to phase D
(stability) with `a_linearLags` frozen as the stage-2 default, or spend a further batch on
richer stage-2 inputs first (climate covariates named as the most plausible untried route).
Asked via `AskUserQuestion` before doing anything else this batch; the human chose to explore
inputs first. The plan was edited to reflect that choice before any modelling: backed up to
`/tmp/claude_backups/` first, then a new ledger row 8 inserted with the reason and its agency
recorded in the plan's own §4b, renumbering the stability phase and everything after it from
rows 8–15 to 9–16 (§6).

**What was built** (`analysis/04_stage2/d_linearClimate`, via `/node`): a fourth stage-2
alternative that is `a_linearLags`'s exact OLS family — same lag-12 in-sample residual,
same cyclical calendar-month features — with three more regressors: `rainfall`,
`mean_temperature` and `mean_relative_humidity`, all already present in
`development.csv` alongside `disease_cases`, so no new data acquisition was needed. The
climate columns are read at **lag 12**, not contemporaneously: `development.csv` holds
already-observed historical climate for every month including the backtest's test months,
but a real 1–3-month-ahead deployment would not know next quarter's rainfall with the
certainty the file implies, and Laos's climate is strongly seasonal, so the value from 12
months before any test month — always inside the training window regardless of which of the
3 test months is being predicted — stands in as a same-season proxy. This is the identical
leakage argument `a_linearLags` already made for the residual lag, applied to a new input; it
is deliberately conservative (it forgoes the current season's anomaly) and that gap is
recorded as an untried refinement, not a rejected one. Kept the same family as `a_linearLags`
on purpose, rather than also trying a new one, so the result isolates the input-richness
question from the model-family question batches 5–6 already answered; `MIN_TRAIN_ROWS` raised
from 12 to 21 to keep the same "≥3× parameter count" rule at 7 parameters instead of 4.

**Result: negative, like every candidate before it.** Mean CRPS 26.85 over the same 371 cells
— worse than stage 1 alone (26.05, +3.05%) and worse than `a_linearLags` on the minimal input
(26.26, +2.25%); coverage essentially unchanged (83.0% vs. 83.3%, both against nominal 90%).
The most plausible untried fork named in batch 7 did not change the central finding when tried
on the family it was tried with. `a_linearLags` remains `04_stage2`'s main path. Updated
development ranking (mean CRPS): stage 1 alone (26.05) < `a_linearLags` (26.26) <
`d_linearClimate` (26.85) < seasonal climatology (26.91) < `b_gradientBoosting` (27.68) <
`c_bayesianRidge` (28.07) < persistence (28.32). All four stage-2 candidates built so far lose
to stage 1 alone; `04_stage2/claim.md` and the root `analysis/claim.md` both updated, and the
node's own `claim.md` and provenance records (two files, referencing "After" commit `8c414b7`)
name what remains untried: a non-linear family given the same climate input, a genuinely
forward (non-lag-12) climate signal, population, and cross-province pooling.

**Self-caught issue**: the first draft of the root `analysis/claim.md` ranking sentence placed
`d_linearClimate` after seasonal climatology by mistake (26.85 is actually lower than 26.91);
caught on re-reading before committing and corrected.

**Also done**: `AI-generated/batch-reports/README.md` brought current — it had gone stale
after batch 1's entry and never listed batches 2–7's reports, a gap noticed while adding
batch 8's own entry; `readme-at-start.md`'s status line updated for the fourth candidate.

**Checks run**: `check_invariants.py` passes (`tree`, `provenance`, `hashes`, `plots`,
`seeds`, `claims`, `combos`, `freeze`, `crossing`, `pool`) after every commit; `git` fails
only mid-batch on expected uncommitted edits and, at the end, only on the pre-existing,
out-of-scope untracked `.idea/`. Stage-1 forecast re-derivation verified bit-for-bit against
`02_stage1`'s stored `per_cell_scores.csv` (408/408 cells, max|Δ|=0.0) before trusting the
residuals, exactly as `a_linearLags` does.

**Follow-ups**: batch 8's own record does not recommend further input-grid exploration before
phase D — the cost/informativeness trade-off has, if anything, worsened (four families now
tried and lost, not three) — but does not decide that unilaterally either;
`04_stage2/claim.md` remains where a future batch or the human would look to keep exploring
inputs versus moving on. Batch 9 is expected to start phase D (stability, ledger rows 9–11)
unless redirected. Nothing from this session has been pushed to the remote.

## T4: Batch 9 — pooled random forest, adapted from chap-models

Full account in `AI-generated/batch-reports/26-09-20_b09_stage2PooledRandomForest.md`.

**Context.** Mid-turn, before batch 9 was even started, the human instructed: keep exploring
stage-2 candidates (rather than move to phase D as batch 8's report suggested), and use an
existing model from `github.com/chap-models` for stage 2. The plan was updated to record this
before any modelling — inserted as ledger row 9, human-set, renumbering phase D onward from
rows 9–16 to 10–17.

**Model selection.** `github.com/chap-models` holds dozens of forecasting models built for the
Chap platform, none of them a residual-correction model in this project's sense. Rather than
guess, the org's repo listing was fetched via `gh api` and four candidates' contents inspected
directly: `XGBoost_for_Malawi`, `ewars_plus_template`, `Vietnam-dengue-superensemble` (all R,
would need a new environment dependency) and `rwanda_random_forest` (Python,
`sklearn.ensemble.RandomForestRegressor`, no new dependency — `scikit-learn` was already pinned
in batch 5). `rwanda_random_forest` was picked: beyond the environment fit, its central
structural idea — **one model pooled across every location**, rather than fit per location — is
exactly the cross-province-pooling fork `04_stage2/claim.md` logged as untried at the end of
batch 7.

**What was built** (`analysis/04_stage2/e_pooledRandomForest`): for each of the 8 backtest
splits, one `RandomForestRegressor` fit on every modelable province's training rows pooled
together (rather than `a_linearLags`/`b_gradientBoosting`/`c_bayesianRidge`/`d_linearClimate`'s
independent per-province fits), then used to predict every province's test-month corrections
for that split. Three deliberate deviations from the original repo, each logged with its reason
in the script's module docstring and the node's provenance: (1) input set — reused
`d_linearClimate`'s lag-12 residual/calendar/climate features rather than the original repo's
lag-1..3 climate and lag-1..3 target lags, which are leakage-unsafe for this project's 3-month
test window (the same argument `a_linearLags` made in batch 4); (2) no population/log1p
incidence transform — this project's stage-2 contract predicts a residual, not a raw count;
(3) a fixed, modest hyperparameter configuration (`n_estimators=200, max_depth=5,
min_samples_leaf=5, max_features="sqrt"`) instead of the original repo's `RandomizedSearchCV`,
rejected as expensive and a reproducibility risk inside an 8-split backtest — the same
conservative-defaults-over-search choice `b_gradientBoosting` made for its own tree candidate.

**Result: the first candidate to beat stage 1 alone — and the first to fail calibration this
badly.** Mean CRPS 25.89 against stage 1 alone's 26.05 (-0.63%) and against `d_linearClimate`'s
26.85 on the identical input (-3.57%), isolating pooling as a real source of the gain. But
empirical interval coverage collapsed to 64.4% against a nominal 90% (every prior candidate
stayed near stage 1's own 82.7-86.8%). Rather than leave the "why" as a terminal observation, a
third script, `03_diagnose_coverage_collapse.py`, was written to ground it in a file (Rule 1):
27.5% of this candidate's corrected forecasts are negative (impossible for a case count) — 2.4-
2.5x every per-province sibling's rate and 6.8x stage 1 alone's own rate — concentrated in the
lowest-case-count provinces (Pearson r=-0.53 between a province's mean case count and its
negative-forecast rate; provinces averaging under 1 case/month have three-quarters of their
cells corrected negative, while every province averaging over 55 cases/month has none). The
pooled correction function, shaped by a training pool spanning under 1 to over 150 mean monthly
cases, overshoots on the scales it was not specifically fit to.

**Verdict, per plan §2** ("a model that wins on mean CRPS while being badly calibrated has not
won"): this candidate does not earn its place either. The pooling *idea* is not ruled out —
only this scale-blind implementation of it; a version preserving each province's own scale
under pooling (a per-province offset or standardisation before pooling) is logged as an untried
refinement in both `04_stage2/claim.md` and the node's own `claim.md`, not a rejected option.
Updated ranking among candidates clearing both bars (unchanged from batch 8): stage 1 alone
(26.05) < `a_linearLags` (26.26) < `d_linearClimate` (26.85) < seasonal climatology (26.91) <
`b_gradientBoosting` (27.68) < `c_bayesianRidge` (28.07) < persistence (28.32), with
`e_pooledRandomForest` (25.89) reported alongside as CRPS-best-but-miscalibrated rather than
folded into that ranking.

**Seeding (Rule 6).** Unlike `b_gradientBoosting`'s configuration (no real randomness regardless
of seed), a random forest's bootstrap resampling is genuine randomness. Pinned via
`random_state=component_seed("04_stage2/e_pooledRandomForest")` and `n_jobs=1`; verified by
running the whole script twice end to end and diffing `per_cell_scores.csv` and
`conclusion.json` byte for byte (identical both times), recorded in the batch's "After" commit
message and this node's provenance rather than re-run automatically on every future invocation.

**Checks run**: `check_invariants.py` passes throughout except the expected mid-batch `git`
failures and the pre-existing, out-of-scope untracked `.idea/`. Stage-1 re-derivation verified
bit-for-bit against `02_stage1`'s stored forecast (408/408 cells) exactly as every sibling
candidate does.

**Follow-ups**: neither this batch nor batch 8 decides whether to build the scale-preserving
pooling fix, try population, move to phase D, or stop exploring stage-2 candidates — that
remains the human's call. If exploration continues, the scale-preserving pooling refinement is
the most directly motivated next step, since it targets the specific, now-understood failure of
the one candidate that has actually beaten stage 1 alone. Nothing from this session has been
pushed to the remote.

## T5: Batch 10 — a systematic second iteration on stage 2

Full account in `AI-generated/batch-reports/26-09-20_b10_stage2SystematicSecondIteration.md`.

**Context.** After batch 9 (pooled random forest: better CRPS, broken calibration) the human
asked for a systematic try rather than a sixth ad-hoc candidate: literature, an analysis of what
the residuals are and what could predict them, then a couple of models. The request's premise —
that improving on stage 1 means predicting its residuals better than chance — was taken
literally: the diagnostic node makes "chance" a permutation distribution.

**Design decisions.** (1) The diagnostics are a tree node (`05_residualStructure`), numbered
after `04_stage2` because they read stage 1's stored backtest, with no data flowing to any
candidate — every candidate estimates what it needs inside its own training window. (2) The
key finding is a target mismatch: candidates a–e trained on the in-sample one-step residual
(white), while the h-step out-of-sample error is what stage 2 corrects. The new candidates
compute that error inside each training window from every origin with stage 1's parameters
fixed (`get_prediction(dynamic=True)`, verified against `apply(refit=False)`), a cheap and
mildly optimistic stand-in for a rolling refit, logged as such. (3) Target standardised by
stage 1's own se and winsorised at ±3; correction = zhat × se, clipped at zero; sigma unchanged
because the diagnostics show any spread scaling loses CRPS (the coverage deficit is a heavy
tail of regime-break cells, a predictive-family problem for stage 1). (4) No climate features,
on both the diagnostics (|ρ| ≤ 0.05) and the literature. (5) Two families on identical rows —
ridge and shallow boosting — with fixed hyperparameters, no search. (6) `g_oosErrorBoosting`
promoted to main path on development evidence; `f_oosErrorRidge` is the linear not-taken
sibling.

**Files.** New: `analysis/05_residualStructure/` (2 scripts, 5 results, 2 provenance
records), `analysis/04_stage2/f_oosErrorRidge/` and `g_oosErrorBoosting/` (2 scripts, 3–4
results, 2 provenance records each), `analysis/scripts/lib/residual_features.py`,
`analysis/scripts/lib/stage2_oos.py`. Edited: the plan (row 10, §4b, report link),
`analysis/claim.md`, `04_stage2/claim.md` (+ main-path promote via `node.py`),
`readme-at-start.md`, `AI-generated/batch-reports/README.md`. `stage1_model.py` was not
modified (earlier provenance records hash it).

**What did not work or is uneven.** Both candidates lose in Savannakhet (stage 1's se there is
tens of times the 2008–09 level, so a small standardised correction is a large absolute one)
and Vientiane Capital (level shrinkage wrong in a genuine surge). The ridge improves 4 of 8
splits, the boosting 5 of 8, both 56.6% of cells — the mean gain is real on this backtest but
not uniform. The cross-validated predictability test on the test cells themselves was far more
pessimistic (2 of 56 configurations lower CRPS) than the in-window-trained candidates turned
out; the two designs differ in training rows (~325 vs ~5,000) and regime.

**Follow-ups.** Phase D's manifest should perturb: stage 1's predictive family (count or
heavier-tailed — the one change that could fix coverage), the winsorisation bound, the ridge
penalty and boosting configuration, the feature set (with/without cross-province and incidence
terms), clipping, per-horizon vs pooled fitting, the warm-up. Untried refinements: bounding the
correction relative to the forecast level; a true rolling refit for in-window errors; ENSO as
an external covariate (new data). The invariant checker's manifest paths (`05_stability`,
inherited) need revising when the stability node is created at the next free number.

**Follow-up, 2026-09-21 (human-set).** The human asked that the second-stage model relate to
the full horizon the evaluation uses — the scheme's default horizon, which is Chap's.
Verified in chap-core's evaluate endpoint (fetched via the GitHub API): the default is
`BacktestParams(n_periods=3, n_splits=7, stride=1)`, so this project's `n_periods = 3` is Chap's
horizon (its `n_splits`/`stride` differ by the batch-1 decision). `lib/stage2_oos.py` had fixed
the horizons at 1..3 as constants; it now takes `n_ahead` from the caller, and both candidate
scripts read it from the schedule via `check_horizons`, which refuses unequal or mismatched test
windows. Re-run: per-cell scores byte-identical to the committed ones (the working-copy `cmp`
differs only in CRLF line endings, which git normalises); `conclusion.json` records
`horizon_months` and its source. Provenance records for both candidates carry a section with
the new digests and the new input. Candidates a–e are deliberately left unchanged.

**Follow-up 2, 2026-09-21 (human-set).** The CSV line-ending mismatch (every node's CSV is
written `\r\n` by Python's `csv` module; git stores `\n` under `core.autocrlf = input`) is
carried in the plan: §4b entry, an explicit clause in ledger row 17 (settle it tree-wide before
the clean-room byte comparison), and a row in `readme-at-start.md`. At the human's instruction
the repository was pushed to the public remote for the first time since batch 1 (`3c90fe0` to
`c8fd3f5`), after grepping tracked files for key/token/password patterns (prose mentions only)
and confirming no credential-like files are tracked; the decision and the scan are recorded in
the plan's §4b, and the release batch's full scan is unchanged.

## T6: Batch 11 — the stability plan

Full account in `AI-generated/batch-reports/26-09-21_b11_stabilityPlan.md`.

**Design decisions.** The stability node is `06_stability` (05 went to the residual
diagnostics); `check_invariants.py`'s `MANIFEST`/`MANIFEST_HOLDOUT` constants and the two
freeze-file paths were moved accordingly, committed alone as a methodological change. Cost was
measured rather than estimated: `01_measure_run_costs.py` re-runs each node's `run.sh`, times
it, and hashes `results/` before and after — a whole-tree determinism check for free (all
identical). `02_plan_manifest.py` derives tier 1 from the tree (so `combos` cannot disagree),
carries tier 2 and tier 3 as hand-written registries with node, parameter, main and alternative
values, basis and rank, costs tier 2 from the measured times, places the budget line on
cumulative cost, and writes `manifest.csv`, `manifest_summary.json` (including the run design
for batch 12) and `manifest_freeze.json` (sha256 + planning commit). Both scripts write CSVs
with `\n` line endings, unlike earlier nodes (the plan's row-17 item).

**Files.** New: `analysis/06_stability/` (2 scripts, 5 results, 2 provenance records).
Edited: `check_invariants.py`, `analysis/claim.md`, the plan (rows 11–13 split, §4b, report
link), `readme-at-start.md` (compute budget row, status), batch-reports README.

**Follow-ups.** Batch 12: build the combination runner (stage 1 under the combination's
spec/window/scheme plus the main-path stage 2 under its settings; verified byte-for-byte on
the `main` combination against `g_oosErrorBoosting` before anything else runs), then run the
29 planned rows into `06_stability/results/<combination>/`. Note that stage-1 perturbations
cannot reuse the candidates' own scripts, which refuse a stage-1 forecast that differs from
`02_stage1`'s stored one. Batch 13: the distribution report and the stability claims. The
human may revise the provisional budget and decide whether to build the predictive-family fork.

## T7: Batch 12 — running the frozen perturbation set

**What exists so far.** `lib/stage2_perturb.py`: dataclass configs for stage 1
(`order`, `seasonal_order`, `enforce`, `window` expanding/rolling/start), the scheme
(`n_periods`, `n_splits`, `stride`, `min_modelable_months`) and stage 2 (`family`, GBM params,
ridge alpha, seed component, `zclip`, `clip_at_zero`, `standardise` se/resid_rms,
`bounded_correction`, `per_horizon`, `features` full/no_cross_province/no_incidence/
level_only/with_climate, `warmup`, `oos_mode` fixed/rolling_refit, `min_train_rows`), and
`run_combination()` returning per-cell rows and a conclusion (stage-1 and two-stage mean
CRPS and coverage, by horizon and by split). It reuses the shared library functions wherever
the quantity is the same, and re-implements only the feature row, because the feature set is
itself perturbed. `06_stability/scripts/03_run_combinations.py` maps every planned manifest
row to a configuration (`COMBINATIONS`), checks the frozen digest, runs `main` and compares it
value for value with the main path's stored per-cell file (gate passed: 408 rows, 0
mismatches, two-stage 25.164), then runs the planned rows into `results/<combination>/` and
writes `run_log.csv`/`run_summary.json`. `04_collect_conclusions.py` gathers tier 1 (from the
siblings' comparison files), tier 2 and tier 3 into `results/conclusions.csv`.

**What went wrong.** The first run failed on `stage2=g_rolling_refit_oos`: a fresh SARIMAX
fit on a truncated series diverged at some origins and returned non-finite predictions, which
reached the booster as NaN features. Fix: non-finite predictions contribute no training row,
the count is recorded in the conclusion (`n_training_rows_dropped_nonfinite`), and a
non-finite test feature is set to 0 (no information). The collector built the tier-1 path
from `analysis/` twice; fixed. Both fixes committed before the re-run.

**Early results (six rows, before the failure).** All kept the two-stage ensemble ahead of
stage 1 alone with coverage not worse; the bounded correction (−5.85%) and the level-only
feature set (−6.53%) improved on the main path's −3.41%; with the airline stage 1, stage 1
alone is much worse (29.15) and the correction recovers most of it (26.05, −10.6%). These
are not the report — batch 13 reports the full distribution.

**Follow-ups.** When the re-run completes: provenance records for `03`/`04`, the node's
answer, batch report `26-09-21_b12_stabilityRun.md`, ledger row 12 → done, invariants,
commit. Then batch 13.

**Completion.** The re-run finished: 29 combinations, 1,937 s (rolling refit 990 s), gate 0
mismatches, `conclusions.csv` with 41 rows (36 run). All 29 tier-2 rows keep the ensemble
ahead of stage 1 alone with coverage not worse; several beat the main path on development data
(level-only features −6.53%, bounded correction −5.85%, no cross-province term −5.84%, climate
anomalies −5.78%) and none was promoted, since the main path was frozen before the run. The
rolling-refit combination skipped 3 origins per split (non-finite refit predictions), visible
in its per-split row counts; the runner's non-finite counter does not cover that case and the
provenance says so. Files: `06_stability/results/<combination>/` (30 directories incl. main),
`run_log.csv`, `run_summary.json`, `conclusions.csv`; provenance `run_combinations.md`,
`collect_conclusions.md`; report `26-09-21_b12_stabilityRun.md`; plan row 12 done and §4b
entries; `readme-at-start.md` status. Next: batch 13, the distribution report and claims.

## T8: Batch 13 — the stability report

Full account in `AI-generated/batch-reports/26-09-21_b13_stabilityReport.md`.

**Design.** The report is a script's output (Rule 1): `05_report_distribution.py` groups the
29 tier-2 rows by judgment call (stage 1 specification; window/scheme/data; stage-2 target and
combination rule; features; hyperparameters and seed; training-error construction), reports
quantiles of the margin, sign flips, coverage, a "moves the size" flag at two percentage points
from the main path (a reporting threshold, recorded in the output), per-province and
per-horizon stability across main + 29 combinations from the per-cell files, and restates tier
1 and tier 3. Prose in `06_stability/claim.md`, the root `analysis/claim.md`, the batch report
and the claims cites those files.

**What it showed.** Sign stable, size not. The conservative reading is the rolling-refit row
(−0.70%): the main path's fixed-parameter shortcut for the in-window errors flatters the
margin. The gain is concentrated (KH, SL, BK, XI always; SV, VT, LP, XA, OU almost never) and
is a 2–3-month-ahead gain. Four stage-2 simplifications scored better than the frozen main
path (level-only features −6.5%, bounded correction −5.8%, no cross-province term −5.8%,
climate anomalies −5.8%); none promoted, since the main path was frozen before the run.

**Files.** New: `05_report_distribution.py`, four results, provenance `report_distribution.md`;
`Human-AI-collaboration/claims/claims.md` now holds C1–C7 (first claims in this project).
Edited: node and root `claim.md`, plan (row 13 done, §4b, report link), `readme-at-start.md`,
batch-reports README.

**Open for the human before batch 14 (holdout manifest freeze).** (1) Whether to pre-register
a stage-2 simplification that scored better on development data — a recorded decision, or none.
(2) Whether to build the predictive-family fork (negative binomial / zero-truncated normal at
stage 1) before the holdout; it is the only change that could repair coverage and needs a
verified metric extension. (3) The provisional one-hour budget stands unrevised.

## T9: Batch 14 — stage 1 fixed and documented, a third stage-2 iteration, the main path annotated

Full account in `AI-generated/batch-reports/26-09-21_b14_stage2ThirdIterationAndMainPath.md`.

**Design.** The new candidate nodes do not re-implement the pipeline: each runs
`lib.stage2_perturb.run_combination` with its `Stage2Config`, verifies the derived stage-1
forecast against `02_stage1` cell for cell, and writes per-cell and conclusion files in the
perturbation schema (which carries `crps_stage1`; the compare scripts reconstruct the
unclipped mean from `stage1_mean + stage2_correction`). The main-path rule was written into the
plan before `j`'s result existed; `j`'s compare script applies it and records the outcome.
`02_plan_manifest.py` now reads the main path from `04_stage2/claim.md`, tags rows by main
path (`@h`), keeps the previous version's tier-2 rows as superseded, adds a tier-0 gate row,
and records what the freeze supersedes; `03_run_combinations.py` reads the main path, refuses
a manifest frozen for a different one, and holds per-main-path configurations. The weaknesses
script reads only results produced earlier in `analysis/run.sh`'s order.

**Findings.** The level-only input is the larger gain and removes most of the Savannakhet loss
by itself; the bound adds little on top of it; Vientiane Capital's loss persists everywhere.
The development margin now stands at −6.53%, a third selection on the same cells.

**Follow-ups.** Batch 15: re-run `01_measure_run_costs.py` (adds h/i/j), run v2, adapt
`04_collect_conclusions.py` and `05_report_distribution.py` to v2 (main from the tree, `@h`
rows, nine tier-1 siblings), report beside v1, claims. Batch 16: freeze the holdout manifest
from v2. The human's open decision on the provisional budget stands.

## T10: Batch 15 — the stability set re-run around the annotated main path (v2)

Full account in `AI-generated/batch-reports/26-09-22_b15_stabilityRunV2.md`.

**Design.** The three stability scripts became version-aware without touching v1's outputs:
`03_run_combinations.py` writes `run_log_v<N>.csv` / `run_summary_v<N>.json` for a version after
the first; `04_collect_conclusions.py` reads version, main path and tag from
`manifest_freeze.json` / `manifest_summary.json`, copies the main row from the main path's own
`comparison.json`, skips the gate row and superseded rows, and writes `conclusions_v2.csv`;
`05_report_distribution.py` assigns groups by a version-independent base name, writes `_v2`
report files, and adds `versus_v1` (pairing by perturbation name, 22 pairs, and by exact
`config` identity, 4 pairs, with an exact-reproduction check) plus `version_comparison_v2.csv`.
The "Before" commit (ba79a02) carried the script changes; the run and report ran at it.

**Findings.** 26 of 26 keep the ensemble ahead with coverage not worse; eight rows move the
size beyond two points (airline and enforced-stationarity stage 1 larger; per-horizon, rolling
window, added-back recent+cross features, rolling refit, 2002 start and no-differencing stage 1
smaller); hyperparameters and seed within two points. The no-differencing stage 1 alone
(24.93) beats the fixed stage 1 (26.05) and nearly matches the two-stage main path (24.35) —
recorded as claim C10 and flagged in the plan's §4b; stage 1 stays fixed (human-set). Around
`h` the margin is larger and more uniform across stage-2 choices than around `g`, and more
exposed to stage 1's specification. One-month-ahead improvement rose from 47% to 85% of
combinations. Three rows beat `h` on development data; none promoted.

**Follow-ups.** Batch 16: freeze the holdout manifest from v2 (`manifest_holdout.csv` +
`holdout_freeze.json`, as `check_invariants.py`'s `freeze` check expects) before the 2010 file
is opened. Open for the human: whether the no-differencing finding changes the decision not to
repair stage 1; whether a better-scoring stage-2 row should be pre-registered instead of `h`.
The line-ending item (row 19) and the provisional budget stand.

## T11 — batch 16: the phase-E set frozen, and its machinery gated first (2026-09-22)

**What was produced.** `analysis/scripts/lib/holdout_eval.py` (phase E's evaluation design and
the executable definition of every frozen row), `06_stability/scripts/06_verify_holdout_runner.py`
(the development gate) and `07_plan_holdout_manifest.py` (the planner and freezer), wired into
the node's `run.sh`; results `manifest_holdout.csv`, `manifest_holdout_summary.json`,
`holdout_freeze.json`, `holdout_freeze_check.json` and `holdout_runner_verification.json`, with
provenance records for both scripts. Report: `26-09-22_b16_holdoutFreeze.md`.

**The design decisions.** The holdout is scored as four expanding-window three-month blocks
covering 2010 exactly once, which is what the project's fixed `n_periods 3` / `stride 3`
resolves to over the combined span; the alternative (one origin, h = 1..12) is recorded as
rejected because it evaluates horizons no model here is built for. The province set is
development's seventeen, derived from development months alone, so the cell set cannot move
when the year opens. Candidates `a`–`e` are not run on the holdout, with the reason in the
manifest. The reporting rule is frozen with the set, so what counts as the answer does not get
chosen after the numbers exist.

**Why the machinery was built in this batch and not phase E.** Plan §3 allows one opening. If
the code that opens the year were also the code being debugged, the first failure would be
repaired with a held-out number on screen. So `lib/holdout_eval.py` was gated on development
first: three reproductions of stored per-cell scores, 408 rows each, 0 mismatched values. The
two baselines are a second implementation — `03_baselines`' scripts are closed records that
cannot read another file — and that comparison is the only thing saying the two agree.

**Two invariants that were not holding.** `check_invariants.py`'s `freeze` check looked for
holdout results under `analysis/results/*__holdout/`, the prior project's layout, so it passed by
matching nothing. And `02_plan_manifest.py` rewrote the frozen development `manifest.csv` on
every run, with `est_cost_s` taken from wall-clock `01_measure_run_costs.py` re-measures each
time — so every full run of `analysis/run.sh` moved it away from `manifest_freeze.json`'s digest,
and nothing checked, because the invariant covered only phase E's set. The second was found by
starting a full node re-run as a reproduction check and stopping to think about what it would
overwrite. Both are fixed, both refusals were exercised rather than assumed, and `manifest.csv`
is unchanged (`d2c5e813…`).

**Recorded rather than hidden.** While checking the holdout file's column layout, its first data
row was displayed, so one held-out value was seen (Attapeu, 2010-01). No decision in this batch
rests on it, but plan §3 asks that the holdout not be characterised before it opens.

**Follow-ups.** Batch 17 opens 2010 once, runs the 33 planned rows and reports by the frozen
rule; it also owes a record of the opening itself (a tracked `run_status_holdout.csv`, plan §3's
third consequence) and should settle the `.gitignore` entry for the working-tree seal marker,
which still names the prior project's `analysis/05_stability/`. Other prior-project prose
remains in `check_invariants.py` and is row 19's to settle with `/validate outsider`. The
line-ending item (row 19) and the provisional compute budget stand.
