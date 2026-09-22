# Develop a two-stage SARIMAX/residual-correction ensemble for dengue forecasting in Laos, veridically

The plan this repository now exists to execute. It is written to be run by an agent that has
none of the conversation behind it in context: everything needed to start is either here or
in `Archive/`.

**This repository previously carried a different, completed project** (comparing candidate
models against the WHO EWARS-csd reference on the same dataset), released at
`github.com/sandvelab/veridical-agentic-dengue-laos`. That project's own analysis tree,
claims and manuscript have been removed from this repository so it holds one project at a
time (`AGENTS.md` §1, §9); its raw archived data was kept, because raw data is a re-usable
resource and not the prior project's output (§4 below).

---

## 1. The aim

**Develop, as autonomously as the setup allows, a two-stage forecasting ensemble for monthly
dengue case counts across the provinces of Laos, and establish whether the second stage earns
its place.** The architecture is fixed; the rest is not:

1. **Stage 1** is a SARIMAX-family model (or a close structural relative — the exact order and
   specification are judgment calls, not fixed here) fitted per province, producing a baseline
   forecast and a residual series (observed minus stage-1 fitted/forecast) on the training data.
2. **Stage 2** is a *second* model, trained to predict stage 1's residuals from covariates
   and/or lagged structure, whose prediction is added back to stage 1's forecast to produce the
   final one. **Stage 2's model family is itself an open judgment call** — gradient boosting,
   random forest, a Bayesian model, or something else — and is explored as an alternatives node,
   not decided here. What is fixed is the *role*: stage 2 never sees the raw target, only stage
   1's residuals, and the combination is additive correction, not a second independent forecast
   averaged with the first. This is what makes it a two-stage *boosting-style* ensemble in the
   general statistical sense (fit, take residuals, fit again on the residuals) rather than an
   ensemble of independently-boosted trees.

Two things are produced at once, and neither is subordinate to the other, matching this
repository's standing purpose (`AGENTS.md` §1):

1. **A forecasting model, with a defensible score** — specifically, evidence on whether the
   residual-correction stage actually improves on stage 1 alone, by how much, and how reliably
   across reasonable alternative ways of building it.
2. **The complete veridical record of how it came about.**

**The central comparison this project is built to answer is internal, not external**: stage 1
alone vs. the two-stage ensemble, on the same data, same splits, same everything else. A
project that only reports the two-stage ensemble's absolute score without the ablation against
stage 1 alone has not answered its own question. Comparison against the required baselines
(persistence, seasonal climatology) is still owed. **The prior project's EWARS-csd score is
not cited here** — settled 2026-09-20, human-set (§4b): this project stands on its own
comparison, stage 1 alone vs. the two-stage ensemble vs. the required baselines, without
reaching for the prior project's external reference at all.

## 2. What "earns its place" means

There is no absolute scale for CRPS, so the criterion is the same kind of comparison the prior
project used, narrowed to what this project is actually asking:

- **Primary**: mean CRPS of the two-stage ensemble vs. stage 1 alone, across regions and test
  splits, on the development backtest. The two-stage model earns its place if it beats stage 1
  alone; the margin, its spread across provinces and splits, and whether it survives reasonable
  alternative ways of building either stage, are the real content of the answer.
- **Secondary**: both required baselines (persistence, seasonal climatology), implemented the
  same way for comparability.

No external reference model is used or cited (§4b, 2026-09-20, human-set) — the comparison
this project answers is entirely internal to the two datasets and models named above.

**The aim is to conclude, and the conclusion will be an uncertain call**, for the same
statistical reason the prior project reported: one held-out year is roughly 216 province-months
and twelve years of development data give a handful of meaningful splits. An honest "the
residual stage doesn't reliably help" is a conclusion, not a failure. If it doesn't help on the
main configuration, that is reported plainly, together with which alternative configurations
were tried and what they cost — the negative-space discipline `AGENTS.md` §4 and the prior
project's plan both hold to.

**A model that wins on mean CRPS while being badly calibrated has not won.** Report interval
coverage beside CRPS, for both stages, on both datasets.

## 3. Non-negotiables

These override anything else in this plan.

- **The final year stays sealed until the final validation, exactly as the prior project sealed
  it.** The same 1998-01 to 2009-12 / 2010-01 to 2010-12 split is reused (§4): development,
  tuning and selection happen only on the first file; the holdout is opened once, at the end, in
  a single batch, and the perturbation set evaluated on it is frozen beforehand. The three
  consequences the prior project's §3 recorded — the holdout is not characterised beyond row
  counts and completeness before it opens; a second opening is recorded if it happens; the
  frozen manifest binds and nothing else does — apply here unchanged.
- **No number reaches a claim except through a file** (`AGENTS.md` §1). Whatever computes CRPS
  here — this project is not required to route through Chap's own evaluation harness (§4) — it
  writes its output to a file, and every reported figure is read from that file by a script, not
  carried by hand from terminal output.
- **Every judgment call is a node or a logged decision, never silent.** Stage 1's order and
  specification, stage 2's model family, what stage 2 sees as input (lagged residuals, climate
  covariates, calendar effects, population), how the correction is combined with stage 1's
  forecast, how the zero-heavy early years are handled, the training window — each is either an
  alternatives node with its rejected siblings intact, or an explicitly logged decision with its
  basis.
- **Agency is recorded on every decision**: `human-set`, `agent-on-human-assessment`, or
  `agent-autonomous`; and for information gathering, `agent-retrieved` or `human-pointed`. The
  default here is `agent-autonomous`, so the entries that matter are the exceptions.
- **Failures are kept.** A stage-2 family that does not fit, a specification that does not
  converge, an ablation that shows no benefit: all stay in the record with what happened.
- **If reusing the archived dataset or its prior-project provenance turns out to be wrong**
  (e.g. a defect the prior project's record did not catch), **stop and report it** rather than
  silently patching around it — the same instruction the prior plan gave for its reference
  model, applied to inherited data instead of an inherited model.

## 4. Decisions already made

Settled here so that execution does not reopen them.

| | Decision |
|---|---|
| **Project seed** | `20260920`. Every component seed derives from it, by the same BLAKE2b construction the prior project used (`AI-internal/skill-references/provenance-record.md` if it needs restating). |
| **Target** | `disease_cases` (reported dengue), monthly, admin-1, Laos — same as the prior project. |
| **Data** | Reused from `Archive/lao-dataset/`, already pinned by commit, checksummed, and `(IS_SHADOW)`-marked; batch 1 re-verifies the checksums rather than re-fetching. `Archive/lao-population/` likewise, if population is used at either stage. `Archive/sibling-datasets/` (Thailand, Vietnam) is available as an optional external check, not required. |
| **Development data** | 1998-01 to 2009-12, same as the prior project — the only file development ever sees. |
| **Held-out data** | 2010-01 to 2010-12, sealed until the final validation (§3), same as the prior project. |
| **Backtest scheme** | `n_periods 3 / n_splits 8 / stride 3` on development, reused from the prior project as the default, for direct comparability of the two projects' numbers even though the constraint that produced it (Chap forcing `n_periods=3` for EWARS) does not itself apply here. *(human-set, 2026-09-20.)* Batch 2 may still deviate with a concrete, recorded reason — this fixes the default, not a ban on reconsidering it. |
| **Evaluation harness** | **Not Chap.** The prior project routed every score through a locally installed, version-pinned `chap-core` because the point was platform-compatible comparison against a Chap-native reference model. This project's question is about the two-stage architecture, not platform integration, so the default is a native Python pipeline: the model code, the backtest splitter and the CRPS computation are ours, each written once, tested, and used identically for every candidate — matching the discipline `AGENTS.md` §1 asks for by a different route than Chap's harness supplied it. *(agent-autonomous, reconsider in batch 1 if the native CRPS implementation cannot be verified against a known-correct reference.)* |
| **Metric** | Mean CRPS across regions and splits from our own verified implementation (verify against a reference implementation such as `scoringrules`, `properscoring`, or a Chap re-derivation on a toy case, before trusting it on real data — Rule 1 makes an unverified metric implementation the single most likely way this project ends up dishonest). Secondary: interval coverage, MAE. |
| **Required baselines** | Persistence (next month = last observed) and seasonal climatology (next month = mean of that calendar month in the training window), scored through the same native pipeline as every other model. |
| **External reference** | None. The prior project's EWARS-csd score is not cited, even as context. *(human-set, 2026-09-20 — settling what batch 1 had left open.)* |
| **Environment** | One native Python environment, pinned per `AGENTS.md` §3 / Rule 3 once batch 1 or 2 knows what it needs (a SARIMAX implementation — e.g. `statsmodels` or `pmdarima` — and a stage-2 library, chosen per family explored). No Docker requirement unless a stage-2 family turns out to need one. |
| **Tracking level** | Full (`AGENTS.md` §6), same as the prior project — this repository is about tracking, and reusing its own dataset and disciplines is not a reason to relax that. |
| **Storage budget** | Not a constraint by default, matching the prior project's own settled position; raised with the human if this project's model outputs turn out to be unusually large. |
| **Scope of the tree** | The whole analysis, stage 1, stage 2 and their combination, is in `analysis/`. Nothing important happens outside it. |
| **Git remote** | Already created and connected: `github.com/sandvelab/sarimax-boosting-agentic-dengue-laos`, public. The release batch (§9, phase F) runs the secrets/data-permission scan before anything beyond the reset performed to start this project is pushed. |

## 4b. Decisions settled during execution

Accumulates as `AGENTS.md` §4 and the prior project's own plan §4b did: each entry with its
basis and its agency (`human-set`, `agent-on-human-assessment`, `agent-autonomous`),
append-only, oldest first.

### 2026-09-20 — settling batch 1's open questions, in dialogue

| Decision | Basis | Agency |
|---|---|---|
| The backtest scheme reuses the prior project's `n_periods 3 / n_splits 8 / stride 3` as the default | The human's choice, from batch 1's question of whether to re-derive one from scratch or anchor to the prior project's — direct comparability between the two projects' numbers was preferred over a scheme derived in isolation. | human-set |
| The prior project's EWARS-csd score is not cited anywhere in this project, not even as context | The human's choice, from batch 1's question of whether to keep it as optional context or drop it — this project stands entirely on its own internal comparison (stage 1 alone vs. the two-stage ensemble vs. the required baselines). §1, §2 and §4's "External reference" row updated accordingly. | human-set |

### 2026-09-20 — settling batch 7's open question

| Decision | Basis | Agency |
|---|---|---|
| Explore a richer stage-2 input (climate covariates) before moving to phase D, rather than freezing `a_linearLags` on the minimal input and starting stability work immediately | The human's choice, from batch 7's question of whether the central finding ("no stage-2 family earns its place") might change on a richer input before perturbing it. Inserted as ledger row 8; rows formerly 8–15 renumbered 9–16 (§6). | human-set |

### 2026-09-20 — continuing to explore, with an externally sourced model

| Decision | Basis | Agency |
|---|---|---|
| Keep exploring stage-2 candidates rather than move to phase D after batch 8's negative climate result, and try a model adapted from `github.com/chap-models` | The human's explicit instruction, mid-batch-9, after batch 8 reported no gain from climate covariates on the linear family. Inserted as ledger row 9; rows formerly 9–16 renumbered 10–17 (§6). | human-set |
| Which `chap-models` repo to adapt (`rwanda_random_forest`), and that it is adapted rather than run through Chap itself | The human named the org, not a specific repo or integration mode. `rwanda_random_forest` was picked over R-based alternatives (`XGBoost_for_Malawi`, `ewars_plus_template`, `Vietnam-dengue-superensemble`) because it needs no new environment dependency and its pooling idea directly addresses `04_stage2/claim.md`'s logged-but-untried cross-province-pooling fork; its algorithm and structural idea are reused inside this project's own native pipeline (plan §4's "not Chap" evaluation-harness decision is unchanged — the candidate still predicts stage 1's residual, not the raw target, and is scored by this project's own CRPS implementation, never by chap-core). | agent-autonomous (repo selection and integration mode); information: agent-retrieved (org listing and repo contents fetched via `gh api`, not recalled from memory) |

### 2026-09-20 — a systematic second iteration on stage 2

| Decision | Basis | Agency |
|---|---|---|
| Continue phase C with a *systematic* second iteration — literature search, a diagnostic analysis of what stage 1's residuals actually are and what could predict them, then new candidates — rather than a sixth candidate picked ad hoc or a move to phase D | The human's explicit instruction after batch 9: the pooled random forest improved CRPS but was miscalibrated, and the question posed was how to predict the residuals "better than chance", since that is what improving on stage 1 requires. Inserted as ledger row 10; rows formerly 10–17 renumbered 11–18 (§6). | human-set |
| The diagnostic analysis is a node in the tree (`analysis/05_residualStructure`), not a scratch investigation | Its numbers inform how the new candidates are built, so they must be file-grounded (AGENTS.md §1). It is a sub-analysis of the root, numbered after `04_stage2` because it reads stage 1's stored backtest output; it does not feed data to any candidate — the candidates estimate whatever they need inside each split's own training window, so run order between `04_stage2` and `05_residualStructure` carries no data dependency. The stability node, when it is built, takes the next free number. | agent-autonomous |
| The diagnostics characterise the *test-cell* errors of the development backtest, and candidate design is informed by them | This is development-set model selection, which is what the development data is for (§3); the sealed 2010 holdout is the guard against the mild optimism it introduces. Recorded so that the development-backtest score of any candidate built on these diagnostics is read as a development score, not an independent one. | agent-autonomous |

### 2026-09-21 — an open reproducibility item, noted for phase F

| Decision | Basis | Agency |
|---|---|---|
| **Line endings of result CSVs are inconsistent between the working copy and the repository, and this is to be settled before the clean-room check (row 17), not now.** Every node's CSV outputs are written with `\r\n` (Python's `csv` module default; confirmed with `file` on `02_stage1` and `04_stage2` outputs) while git normalises them to `\n` on commit (`core.autocrlf = input`; no `.gitattributes`). Consequence: the sha256 digests of CSV *inputs* recorded in provenance records are those of the working copy, and a fresh clone's copies hash differently; `/validate invariants`' `hashes` check is unaffected (it hashes scripts, which are `\n` already), but `/validate cleanroom`'s byte comparison against archived results will flag every CSV unless it is line-ending-aware or the convention is fixed first. | Observed during batch 10's follow-up when `cmp` reported re-run outputs as differing while git reported them unchanged. Noted rather than fixed because fixing it means either re-running every node and re-hashing every record, or adding a `.gitattributes` and a line-ending-aware comparison — a tree-wide decision that belongs to the clean-room batch, where its cost is paid once. The human asked for it to be carried in the plan. | human-set (carry it forward in the plan); agent-retrieved (the observation) |
| **The repository is pushed to the public remote now, at the human's instruction, ahead of the release batch's full scan** | The human asked to commit and push after batch 10. §4's git-remote row reserves the secrets/data-permission scan for the release batch; a lightweight scan (tracked files grepped for key/token/password patterns; `.env` and credentials confirmed untracked) was run before this push and found nothing, and the data is already settled as public and redistributable (§4). The full release scan still runs in row 18. | human-set |

### 2026-09-21 — batch 11: the stability plan

| Decision | Basis | Agency |
|---|---|---|
| The stability node is `analysis/06_stability`, and the invariant checker's manifest paths were moved from the prior project's `05_stability` to it | `05` went to the residual diagnostics in batch 10; a sub-analysis's number is its run order. Changing `check_invariants.py` is a methodological change and was committed on its own with that stated. | agent-autonomous |
| Compute budget for stability work: one hour of wall-clock, provisional | Measured, not guessed: re-running every existing model node takes 87 s in total (`06_stability/results/run_costs.csv`); the 29 planned tier-2 perturbations are estimated at 24 minutes. Compute is not the binding constraint here, development effort per perturbation is, so the budget excludes nothing planned. Set by the agent because §4 left it to phase D; the human may revise it. | agent-autonomous |
| Row "11–13" split into three rows with distinct aims (plan / run / report) | The three steps have different deliverables and the run cannot start before the manifest is frozen and the runner verified. | agent-autonomous |
| Five alternatives are listed as tier 3 and not run: log1p stage 1; a negative-binomial or truncated-normal predictive family; a multiplicative combination rule; an ENSO covariate; Chap-native evaluation | Each needs machinery this project has not built (a verified metric extension, a combination design, a data acquisition) or reopens a §4 decision; they are recorded with the reason so the line is visible. The predictive-family fork is flagged as the most consequential one not run: batch 10's diagnostics show the coverage deficit is a heavy tail a Gaussian cannot carry. Whether to build it is a human call. | agent-autonomous (the listing); the decision to build any of them is left open |

### 2026-09-21 — batch 12: the stability run

| Decision | Basis | Agency |
|---|---|---|
| Tier-2 perturbations run through a separate parametrised pipeline (`lib/stage2_perturb.py`, `06_stability/scripts/03_run_combinations.py`) rather than by editing the candidates' scripts | The candidates' scripts fix their constants and refuse a stage-1 forecast that differs from `02_stage1`'s stored one, so they cannot run a stage-1 perturbation; the runner is trusted only because its `main` combination reproduced `g_oosErrorBoosting`'s 408 per-cell rows value for value (0 mismatches) before any perturbation ran, and it refuses a manifest that no longer hashes to its frozen digest. | agent-autonomous |
| In the rolling-refit combination, an origin whose fresh SARIMAX fit returns a non-finite prediction contributes no training row | The first full run stopped there with NaN features. Skipping is recorded, not hidden: the per-split row counts in that combination's `conclusion.json` are 3 below `main`'s in every split (3 skipped origins per split, out of ~4,700 rows), and the runner's non-finite-feature counter is documented as not covering this case. No other combination was affected; all 29 rows were re-run from scratch after the fix. | agent-autonomous |
| Where the budget line fell: nowhere — all 29 planned rows ran, 1,937 s of the 3,600 s ceiling (the rolling refit alone 990 s) | Recorded in `06_stability/results/run_summary.json` and `run_log.csv`. | agent-autonomous |

### 2026-09-21 — batch 13: the stability report

| Decision | Basis | Agency |
|---|---|---|
| The report is written from `conclusions.csv` and the per-combination files by a script (`05_report_distribution.py`) into `distribution.json` and three tables, and the prose in the node's `claim.md`, the batch report and the claims cites those files | Rule 1: no number reaches a claim except through a file; the distribution is a result like any other. | agent-autonomous |
| "Moves the size" is defined as a margin more than two percentage points from the main path's | A reporting threshold, not a test; chosen so that hyperparameter and seed noise (all within two points) is separated from the choices that change the finding's magnitude. Recorded in the script and in `distribution.json` (`sensitivity_points`). | agent-autonomous |
| Seven claims (C1–C7) enter the claim collection now, scoped to the development backtest | The perturb skill asks that each stability conclusion be a claim; phase F builds the rest of the collection from the tree. Each carries grounds, scope and the alternatives that would support a different statement. | agent-autonomous |
| No perturbation that beat the main path on development data is promoted | The main path was frozen before the run so the report is a measurement, not a selection (plan §3); the better-scoring simplifications (level-only features, bounded correction) are recorded as such and are candidates for a *pre-registered* change before the holdout manifest is frozen in batch 14, if the human wants one — a decision this batch does not make. | agent-autonomous |

### 2026-09-21 — after phase D: stage 1 fixed, stage 2 explored further, the main path annotated now

| Decision | Basis | Agency |
|---|---|---|
| **Stage 1 is not repaired.** It stays the per-province SARIMAX(1,1,1)×(1,0,0,12) on raw counts; the predictive-family fork (negative binomial / zero-truncated normal), the log1p transform and every other stage-1 change stay unbuilt. Its weaknesses — the heavy-tailed standardised error that no rescaling of a Gaussian repairs, negative forecast means, a standard error that does not grow with the level, systematic seasonal and level-dependent bias, and the 2008–09 reporting-regime breaks — are documented in one file-grounded place instead. | The human's instruction after batch 13: "do not repair anything in stage 1 — that should be sarimax. Just document well the weaknesses." The project's question is whether a second stage earns its place on top of a SARIMAX, so the first stage is a fixed premise, not a design variable. | human-set |
| **Stage 2 is explored further**, with the configurations the stability run scored better than the frozen main path built as alternatives nodes (`h_levelOnlyBoosting`, `i_boundedBoosting`, `j_levelOnlyBoundedBoosting`) | The human's instruction: "explore several stage-2 solutions further". The three are the two stage-2 simplifications that moved the development margin most (level-only input −6.5%; bounded correction −5.8%) and their untried combination; each is one clean axis away from `g_oosErrorBoosting` or from each other. | human-set (explore further); agent-autonomous (which three) |
| **One stage-2 configuration is annotated as the main path now**, before the holdout manifest is frozen, by a rule written before the combination's result is seen: among `g`, `h`, `i`, `j`, the lowest development mean CRPS with 90% coverage not worse than stage 1's; tie within 0.1 CRPS broken by more splits improved, then by the simpler configuration. | The human's instruction: "annotate one of them as the main already now". This is development-set selection — the third round of it on the same 371 cells — and the holdout is the guard; recording the rule first is what makes the holdout evaluate a pre-registered choice rather than a post-hoc one. | human-set (annotate now); agent-autonomous (the rule) |
| **The v1 development stability manifest is superseded, not edited**: a v2 is planned around the annotated main path, with the new siblings as tier-1 rows and the tier-2 perturbations re-specified around the new main's constants; v1's rows and results stay in the tree under their names, marked superseded | Exploring stage 2 after phase D changes the main path the stability run was built around; v1's report (batch 13) remains a true record of `g_oosErrorBoosting`'s stability and is not rewritten. | agent-autonomous |

### 2026-09-21 — stage 2's horizon set is the evaluation scheme's

| Decision | Basis | Agency |
|---|---|---|
| Stage 2 is trained on every horizon the evaluation scores, h = 1..`n_periods`, with `n_periods` read from the backtest schedule (`01_data/03_backtest_scheme/results/schedule_summary.json`) rather than fixed in code; a test window of a different length is refused | The human's instruction, after batch 10, that the second-stage model must relate to the full horizon the evaluation uses — the scheme's default horizon, which is Chap's. Verified against chap-core itself (`chap_core/cli_endpoints/evaluate.py`, fetched via the GitHub API, `agent-retrieved`): Chap's evaluate default is `BacktestParams(n_periods=3, n_splits=7, stride=1)`, so this project's `n_periods = 3` is Chap's default horizon (its `n_splits 8 / stride 3` differ, by the batch-1 decision above). `f_oosErrorRidge` and `g_oosErrorBoosting` already trained on h = 1..3, so no score changed (per-cell outputs byte-identical); what changed is that the coupling is now read from the scheme and checked, not assumed, and `conclusion.json` records `horizon_months` and its source. Candidates a–e, which trained on the one-step in-sample residual, are unchanged: their mismatch with the evaluation horizon is part of the record of why they failed. | human-set (the requirement); agent-autonomous (the implementation) |

### 2026-09-22 — batch 15: the stability v2 run and report

| Decision | Basis | Agency |
|---|---|---|
| The v2 run, conclusions and report are written as `_v2` files beside v1's (`run_log_v2.csv`, `run_summary_v2.json`, `conclusions_v2.csv`, `distribution_v2.json`, `perturbation_effects_v2.csv`, `province_stability_v2.csv`, `horizon_stability_v2.csv`, `version_comparison_v2.csv`); v1's files are not overwritten | v1's files are the grounds of the batch-13 report and claims C2–C7; the runner, collector and reporter now read the version and main path from the freeze rather than naming a candidate in code, and a later version gets `_v3` files the same way. | agent-autonomous |
| The four v2 rows whose configuration is by construction identical to a v1 row (the main path itself and the three "add features back" rows) were run, not dropped, and their exact reproduction of v1's values is recorded as a determinism check | They are what the manifest planned around `h`; a free check is recorded rather than discarded. All four reproduced v1 to the last digit. | agent-autonomous |
| No better-scoring v2 row is promoted (winsorisation at 5, −6.92%; the bound without floor, −6.78%; no winsorisation, −6.57%, against `h`'s −6.53%) | The main path is the pre-registered choice (batch 14) and the report is a measurement of it; the three lie within the seed row's own distance from the main path. If a change is wanted it belongs before the holdout freeze in batch 16, as a recorded decision, and this batch does not make it. | agent-autonomous |
| **The no-differencing stage 1 finding is recorded against stage 1's documented weaknesses, and stage 1 is not reopened.** SARIMAX(1,0,1)×(1,0,0,12) alone scores 24.93 on development data, better than the fixed stage 1 (26.05) and within 0.6 CRPS of the two-stage main path (24.35); under it the correction is worth −1.06%. | The decision not to repair stage 1 is the human's (2026-09-21); the finding bears on how the central comparison is read — part of the second stage's margin repairs a differencing choice — so it is a claim (C10) and is flagged here for the human. | human-set (stage 1 fixed); agent-autonomous (the recording); the decision whether this changes anything is open |
| "Moves the size" stays at two percentage points for v2 | Comparability with v1; the threshold is a column in the output. | agent-autonomous |

### 2026-09-22 — batch 16: the two questions batch 15 left open, settled at the freeze

| Decision | Basis | Agency |
|---|---|---|
| **The holdout manifest pre-registers `h_levelOnlyBoosting` as the main path.** The three v2 rows that scored better on development data (winsorisation at 5, −6.92%; the bound without its floor, −6.78%; no winsorisation, −6.57%, against `h`'s −6.53%) are not promoted. | The human's choice, from batch 15's question of whether to change the pre-registered configuration before the freeze. The three lie within the alternative-seed row's own distance from `h`, so they separate it by less than the seed does; and a change now would make the held-out year evaluate a fourth round of selection on the same 371 development cells rather than a choice made before the results were seen. | human-set |
| **Stage 1 is not reopened after the no-differencing finding.** SARIMAX(1,1,1)×(1,0,0,12) stays; the finding that SARIMAX(1,0,1)×(1,0,0,12) alone scores 24.93, within 0.6 CRPS of the two-stage main path, stays documented as a stage-1 weakness and as claim C10. | The human's choice, reaffirming the 2026-09-21 decision at the last moment it could be revised. `stage1=nodiff_101x100@h__holdout` is in the frozen set either way, so the held-out year still measures how much of the margin survives a better stage 1 — it is a perturbation, not the main path. | human-set |

### 2026-09-22 — batch 16: how the held-out year is evaluated, fixed before it opens

| Decision | Basis | Agency |
|---|---|---|
| **The holdout is scored as four successive three-month blocks covering 2010 exactly once**, with the project's fixed `n_periods 3` / `stride 3` and an expanding training window, so `n_splits = 4` is read off the length of the held-out file rather than chosen. Each block after the first trains on the holdout months already forecast. | The scheme is the project's (plan §4) and the horizon set is the one stage 2 is trained on (§4b, 2026-09-21); this is the only resolution of that scheme that scores every held-out month once. The alternative — one origin at 2009-12 forecasting h = 1..12 — was rejected: it evaluates the year at horizons no model here is built or scored for. Training on already-forecast holdout months is what a forecaster operating through 2010 would have had, and the year is still opened once, by one script. Recorded in `06_stability/results/holdout_runner_verification.json`. | agent-autonomous |
| **The province set evaluated on the holdout is development's seventeen**, derived from the development months alone (`min_modelable_months` applied to 1998-01–2009-12), not re-derived from the combined file. | A cell set that can move when the year opens is a set chosen after the fact. LA-VI is excluded on development data and carries 2010 rows, so re-deriving would change the denominator of every reported mean. | agent-autonomous |
| **Phase E's machinery is written and gated in batch 16, not in batch 17** — `lib/holdout_eval.py`, verified against this repository's stored development results before the manifest is frozen. | Plan §3 allows one opening. If the code that opens the year is also the code being debugged, the first failure is repaired with a held-out number already on screen and the second run is not the first opening. The gate is the same one the development combination runner had to pass: three reproductions of stored per-cell scores, 408 rows each, 0 mismatched values. The two required baselines are a second implementation (`03_baselines`' scripts are closed records and cannot read another file), and the comparison is the only thing that says the two agree. | agent-autonomous |
| **The five in-sample-residual siblings (`a`–`e`) are not run on the holdout**, recorded as a visible absence rather than dropped | Each needs a holdout-capable rewrite of its own node script; all five lose to stage 1 alone on development (+0.78% to +7.73%, with `e`'s −0.63% failing plan §2's calibration bar); and batch 10's diagnostics explain the failure mechanically. The held-out year is spent on the configurations whose margin is in question. | agent-autonomous |
| **The reporting rule is frozen with the set**, in `holdout_freeze.json`: plan §2's two bars on the main path as the primary answer, both baselines beside it, the tier-2 spread as a distribution and never as a best row, every row paired with its development counterpart — and afterwards nothing added, dropped, re-tuned or re-run once a holdout number has been seen, nothing promoted on held-out evidence, and a result contradicting development reported as the finding. | A frozen set without a frozen rule leaves the choice of what to emphasise to be made after the numbers are seen, which is the same failure one row later. | agent-autonomous |
| **`check_invariants.py`'s `freeze` check was looking in an empty place, and was fixed before the freeze it protects** | Its leak detection named `analysis/results/*__holdout/`, the prior project's layout; this project's stability node writes to `analysis/06_stability/results/`, so the check passed by matching nothing — a check that reads as evidence and is not. It now matches any tracked path under `analysis/` carrying the `__holdout` suffix. A methodological change (AGENTS.md §3, Rule 4), committed with the batch's "Before" commit and stated in those terms. | agent-autonomous |
| **The frozen *development* set was not staying frozen, and now does.** `02_plan_manifest.py` rewrote `manifest.csv` on every run, with `est_cost_s` taken from wall-clock that `01_measure_run_costs.py` re-measures each time, so every full run of `analysis/run.sh` moved the file away from the digest in `manifest_freeze.json` — and nothing checked it, because the `freeze` invariant covered only the phase-E set. The script now verifies instead of rewriting (`manifest_freeze_check.json`), refuses a file that no longer hashes to the freeze, refuses a re-plan that would change anything beyond the cost columns, and still plans a new version when the main path changes, which is the path batch 14 took. The `freeze` invariant now asserts the development freeze as well. `manifest.csv` is unchanged: still `d2c5e813…`, the v2 digest frozen at `cef9a18`. | agent-autonomous |

### 2026-09-22 — batch 17: the held-out year, opened once

| Decision | Basis | Agency |
|---|---|---|
| **The frozen set was run exactly as frozen, and nothing was added, dropped, re-tuned, re-run or promoted afterwards.** Three tier-2 rows beat the main path on the held-out year (no winsorisation −29.25%, the looser winsorisation bound −28.72%, a higher learning rate −25.77% against the main path's −22.81%) and none is promoted. | The holdout measures a pre-registered configuration; selecting on it would spend the only unused data this project has and would make the reported margin a maximum rather than a measurement. | agent-autonomous |
| **The runner's gate precondition was corrected before the year was opened, not after.** Its first version required `holdout_runner_verification.json` to hash to the digest the freeze recorded; that file carries the wall-clock of its own checks, so its digest moved inside batch 16 itself, and from a clean clone the precondition could never have been satisfied. It now asserts the gate's verdict (three reproductions, zero mismatches) and its scope, checked against the frozen manifest's own `n_expected_cells`. | `holdout_freeze.json` states what binds: the manifest is the frozen artefact and the other `frozen_inputs` digests are context recorded at the freeze. The runner had promoted a context digest to a precondition. The year stayed shut throughout, and the correction is in the record as its own commit. | agent-autonomous |
| **`11_characterise_holdout_year.py` describes the opened year, and is recorded as not being a row of the frozen set** | Every model scores several times worse on 2010 than on development, and a report giving the margin without saying why would be true and useless — a reader could not tell whether the second stage helped because it is good or because there was an unusual amount left to correct. Describing the data after the year is opened is what the opening is for; it adds no row, re-tunes nothing and re-runs nothing. | agent-autonomous |
| **The held-out evaluation is 16 provinces, not 17.** LA-XN reports no cases for any month of 2010, so its 12 cells carry no actual to score against, and 192 of the 204 frozen cell slots are scored. | An outcome, reported, not a reason to re-plan after opening. Batch 1's holdout completeness check recorded rows and months present — which they are — and did not record whether `disease_cases` was populated; that is a gap in the check, noted for row 19. | agent-autonomous |
| **The comparison against the required baselines is reported as the finding it is**, not as a footnote: seasonal climatology (77.29) beats both the two-stage ensemble (99.20) and stage 1 alone (128.51) on the held-out year, reversing the development ranking. | Plan §2 makes both baselines part of the reported comparison on both datasets, and §2 also says an honest negative is a conclusion. The two-stage architecture improving on its own first stage, while that first stage is beaten by a naive seasonal mean, is the single most important thing the held-out year says. | agent-autonomous |
| **Open for the human, and not decided here**: whether the project now builds the stage-1 predictive-family fork (tier 3, recorded as not run by the human-set decision of 2026-09-21) in the light of the held-out calibration collapse, and whether anything further may be evaluated on 2010 at all given that it has been opened. | Plan §3 allows one opening and the manuscript can be written from what is now in hand. Re-opening is a decision with a cost that only the human should pay. | (open) |

### 2026-09-22 — row 17b: an overview article, requested outside the batch sequence

| Decision | Basis | Agency |
|---|---|---|
| **A short overview article is written now, from the claim collection**, rather than waiting for phase F's row 20. It is `Human-AI-collaboration/manuscript/26-09-22_twoStageDengueLaos.md`, with a provenance sidecar beside it. | The human's request, once the held-out result was in: a 1–2 page overview a reader can take in quickly. Given a ledger row of its own (row 17b) because nothing is done here that the ledger does not name (AGENTS.md §8); row 20's full manuscript is unaffected. | human-set (that it is written now); agent-autonomous (what it contains) |
| **The article reports the held-out baseline result as a headline, beside the positive answer to the project's own question** | Plan §2: a model that wins on mean CRPS while being badly calibrated has not won, and an honest negative is a conclusion. The second stage earning its place (C14) and the two-stage model losing to seasonal climatology (C17) are both results, and neither is a footnote to the other. | agent-autonomous |
| **`/claims check-text` found one factual error, corrected before the draft was committed** | The draft called climatology "the simplest baseline in the study"; the simplest is persistence, which the ensemble beats. The check flags sentences with no matching claim and is deliberately crude; reading each flag is what caught this, which is the point of running it. | agent-autonomous |

### 2026-09-22 — batch 18: the claim collection completed from the tree, and the report's drill-down rebuilt

| Decision | Basis | Agency |
|---|---|---|
| **Twelve claims added (C21–C32) so that every node in the tree is represented in the collection**, not only the stability node. Before this batch 20 of 21 claims sat on `06_stability` and the metric, data, stage-1, baseline, diagnostic and stage-2 nodes had none. | Rule 9 makes the collection the bridge from results to text, and phase F's job is to build it *from the tree*. A node whose answer is in its `claim.md` and nowhere in the collection cannot be written from. | agent-autonomous |
| **C26, on stage 1's six documented weaknesses, is recorded as `human-set`** rather than agent-autonomous | The statement exists because the human decided stage 1 would be documented instead of repaired (2026-09-21, reaffirmed 2026-09-22); the agency field records who made the call the claim reports, not who typed it. | human-set |
| **The hierarchical report's drill-down below the tree was rebuilt for this project's layout.** It addressed the prior project's paths (`04_score/01_collect/results/<combo>/metrics_cell.csv`, `crps_by_location.csv`, `leaderboard.csv`), none of which exist here, so the root page reported "0 combination(s) scored" and Rule 8's requirement that summaries link down to the values they aggregate was not met. It now discovers every directory holding a `per_cell_scores.csv` — 103 of them — and gives each a page with the stored conclusion, the stored per-split and per-horizon blocks, the same cells grouped by province and by month, and a link to the per-cell file. | The tree rendered and the level below it was empty, which reads as "there is nothing here" rather than "this was never wired up" — the same failure as a check that passes by looking in an empty place (batch 16). A generated report that silently omits a rule's deliverable is worse than one that fails. | agent-autonomous |
| **The by-province and by-month tables are computed by the report for display and say so on the page**; they are not stored results | Storing an aggregate beside each of the 103 results would mean re-running the analysis inside a reporting batch. The boundary is recorded in `AI-generated/hierarchical-report/provenance.md` and on every page that shows such a table. | agent-autonomous |

### 2026-09-23 — batch 19: the clean-room and outsider checks

| Decision | Basis | Agency |
|---|---|---|
| **The line-ending item is settled by `.gitattributes` (`*.csv -text`) plus `git add --renormalize`, not by fixing the writers and re-running.** All 133 CSVs now hash identically in the working copy, the repository and a clone. | It was not cosmetic. A fresh clone's `holdout.csv` hashed to `e6d57643…` against the frozen `389e4f49…`, so `08_run_holdout.py` would have refused to open it and **phase E was not reproducible from a clone at all**. The rejected alternative — `lineterminator="\n"` in the fifteen writers, then re-run — would change `holdout.csv`'s bytes, and re-freezing the phase-E seal after the year has been opened is what the seal exists to prevent. The cost accepted: the writers stay non-uniform, and a future contributor must not "fix" one without re-hashing every record that names its output. | agent-autonomous |
| **`cleanroom.sh` is written and is the implementation of `/validate cleanroom`**, which until now described a check that nothing performed. It compares the checked-out inputs before running anything, and declares the files whose content measures the machine rather than the analysis. | A check described in prose and absent in code is the failure mode this batch found eleven other instances of. Declaring the varying files keeps a real difference visible instead of drowned in wall-clock noise. | agent-autonomous |
| **The result: the analysis reproduces from nothing** — 288 of 289 byte-identical on the first run, and 289 of 289 after one fix. The single difference was `distribution_holdout.json`, which embedded `run_summary_holdout.json` whole and so carried a stopwatch inside a result file; it now embeds the opening's identity and not its timings. | Verified rather than argued: the corrected reporter was run in this tree and in the clone, both reading only stored files so neither reopens the year, and the two outputs are byte-identical. | agent-autonomous |
| **Ten of the outsider test's twelve findings are fixed**, most seriously `AGENTS.md` §8 naming an interpreter that does not exist (`environment/chapenv/bin/python`) and the deadlock that made adding a new alternatives child impossible without hand-editing a frozen artefact. | Eleven of the twelve are stale text inherited from the prior project; one (the deadlock) is a regression this project introduced in batch 18 when the planner was made to verify rather than rewrite — the guard was right and its error message left a contributor no legal move. | agent-autonomous |
| **`.claude/settings.json`'s `<PARENT_DIR>` / `<HOME>` placeholders were NOT substituted, and the matter is raised with the human.** The safeguard they exist for has failed: the parent directory's `CLAUDE.md` is loaded into every session here, so by Rule 4 every session has run under an instruction set nobody intended. | Changing what instructions govern the repository is not a change to make on an agent's report, and it bears on the published record of the method. What it needs: the two real paths substituted, and a §4b entry recording that sessions to this point ran with the parent file in context. | (open — human) |
| **A lesson recorded for row 20**: a project that inherits a repository inherits its prose, and prose does not fail. A grep for `chapenv`, `06_external`, `data-acquisition`, `$COMBO`, `05_stability` and `batch [23][0-9]` finds nearly all of it mechanically and is worth running before the release scan. | Three instances of the same class had already been found by hand (batches 16, 18, and this one); the outsider found seven more in a single pass. | agent-autonomous |

## 5. How this plan is used

Unlike a plan written once and left alone, this one is edited as it runs, the same way the
prior project's was: §6 below is the live batch ledger, and sketched phases become concrete
batches as they are reached. The plan as it stands after batch 1 is archived to
`Archive/plan-as-delivered/` (recreated for this project) so later drift is measurable, the
same discipline the prior project applied to itself.

## 6. Batch ledger

One row per `/do` invocation. Status: `open`, `done`, or `blocked` with why.

| Batch | Phase | Aim | Status |
|---|---|---|---|
| 1 | A — Orient & set up | Read `readme-at-start.md`, `AGENTS.md`, `MOTIVATION.md`; re-verify the archived Laos dataset's checksums and re-read its `provenance.md`; stand up the repository's own `.venv`; write the root `analysis/claim.md`; raise any open questions this plan leaves the human (backtest scheme, whether to keep the EWARS citation, anything else). No modelling. | done |
| 2 | B — Data & stage 1 | Characterise the reused dataset for this project's purposes (it does not need re-discovery, but per-province handling does); implement the fixed backtest scheme (§4) and verify the CRPS computation against a known-correct reference; build stage 1 (SARIMAX family) as a runnable node with a first, defensible default specification; get an end-to-end backtest running and producing a file-grounded score. | done |
| 3 | B (cont.) | Implement the required baselines through the same pipeline; establish the first honest number for "how much does the backtest resolve" (the prior project's equivalent finding, re-derived for this project's own scheme and models). | done |
| 4 | C — Stage 2, first candidate | Build the residual-correction contract (stage 2 reads stage 1's residuals and whatever covariates its first configuration uses) and one concrete stage-2 family as the first alternatives child; get the two-stage ensemble scoring end to end. | done |
| 5 | C (cont.) | Add a tree-based stage-2 family alternative (`04_stage2/b_gradientBoosting`), same minimal input as batch 4's candidate to isolate the model-family comparison. | done |
| 6 | C (cont.) | Add a non-tree, non-linear stage-2 family alternative (e.g. a Bayesian or linear-with-structure model). | done |
| 7 | C (cont.) | Decide which stage-2 family sits on the main path, on development evidence, with the rejected families kept runnable; log what stage 2 is allowed to see (lags, covariates, population) as forks. | done |
| 8 | C (cont.) — richer stage-2 input | Build a fourth stage-2 alternative, `04_stage2/d_linearClimate`: same family as the main path (`a_linearLags`) with lag-12 climate covariates (rainfall, mean temperature, mean relative humidity) added to its input, isolating the input-richness question from the model-family one. Score it through the same pipeline; decide whether it changes the main-path pick. *(Inserted 2026-09-20, human-set — batch 7 left phase-C-continuation vs. phase-D as an open choice and the human chose to explore richer inputs first; renumbers what were rows 8–15 to 9–16.)* | done |
| 9 | C (cont.) — pooling fork, external model | Build a fifth stage-2 alternative, `04_stage2/e_pooledRandomForest`, adapting `chap-models/rwanda_random_forest` (a community model from the Chap ecosystem the human pointed at): a random forest pooled across all provinces in one shared fit per split, rather than the per-province independent fits every prior candidate used, on the same input as `d_linearClimate`. Isolates the pooling fork logged as untried at the end of batch 7. *(Inserted 2026-09-20, human-set — "keep exploring", and use an existing chap-models model for stage 2; renumbers what were rows 9–16 to 10–17.)* | done |
| 10 | C (cont.) — second iteration on stage 2, systematic | Rather than a sixth ad-hoc candidate: (i) a literature search on when residual-correction hybrids help or fail and on what predicts dengue at 1–3-month horizons in Laos and mainland Southeast Asia (sources retrieved and read, not recalled); (ii) a diagnostic node, `05_residualStructure`, that characterises stage 1's *out-of-sample* forecast errors on the development backtest — by horizon, calendar month, province scale, spread calibration, cross-province synchrony — and estimates from information available at forecast time how much of them is predictable at all ("better than chance"), which is what a stage 2 has to achieve to earn its place; (iii) new `04_stage2` alternatives built on what (i) and (ii) show, scored through the unchanged pipeline, calibration reported beside CRPS. *(Inserted 2026-09-20, human-set — "do a systematic try for how to improve in a second iteration"; renumbers what were rows 10–17 to 11–18.)* | done |
| 11 | D — Stability: plan | Create the stability node (`06_stability`); enumerate the judgment calls made in batches 1–10 as a perturbation manifest (stage 1 order/spec, stage 2 family, target, inputs and combination rule, training window, zero-handling, backtest scheme, seeds); measure per-run cost by re-running the existing tree; set the compute budget; rank by informativeness; freeze the development manifest. | done |
| 12 | D — Stability: run | Build the combination runner (verified against the main path's stored per-cell scores before anything else is trusted); run every planned row of the frozen manifest; write `results/<combination>/` per row; record where the budget line fell. | done |
| 13 | D — Stability: report | Report the distribution of conclusions across the set — which choices the central comparison is insensitive to and which it turns on; each conclusion and the stability claim itself to the claim collection. | done |
| 14 | C (cont.) — third stage-2 iteration, and the main path annotated | Stage 1 stays SARIMAX as specified and is **not repaired**; its weaknesses are documented, file-grounded, in one place (`05_residualStructure/results/stage1_weaknesses.json`, `02_stage1/claim.md`). Build the stage-2 configurations the stability run found better than the frozen main path as proper alternatives nodes — the minimal (level-only) input, the bounded correction, and their combination — through the unchanged pipeline, each verified against stage 1's stored forecast. Then **annotate one of them as `04_stage2`'s main path now**, by a rule written down before the combination's result is seen, so the holdout evaluates a pre-registered configuration. Re-plan the development stability manifest around the annotated main path (v2; v1 superseded and kept). *(Inserted 2026-09-21, human-set — "do not repair anything in stage 1; document the weaknesses; explore several stage-2 solutions further, but annotate one as the main already now"; renumbers what were rows 14–18 to 16–20.)* | done |
| 15 | D (cont.) — stability v2 | Run the v2 manifest around the annotated main path with the verified runner; report its distribution beside v1's; claims. | done |
| 16 | D (cont.) / freeze | Freeze the phase-E (holdout) manifest before the holdout opens, per §3 — and, with it, the evaluation design (how the twelve held-out months are split, which provinces are scored) and the reporting rule. Build and gate phase E's machinery in this batch rather than in row 17, against this repository's stored development results, so that no code is written or corrected with a held-out number on screen. *(Scope widened 2026-09-22, agent-autonomous; §4b.)* | done |
| 17 | E — Final validation | Open the 2010 holdout once; run exactly the frozen manifest with the gated machinery; report the held-out distribution beside the development one, by the rule frozen in row 16. **Record the opening itself**: a tracked `run_status_holdout.csv` written when the year is read, so that a second opening would be visible (plan §3's third consequence). The prior project's `.gitignore` entry for its working-tree seal marker still names `analysis/05_stability/` and is this row's to settle. | done |
| 17b | F (early) — overview article | A short 1–2 page article covering the whole study, with results from both the development backtest and the held-out year, and the implications; written from the claim collection, with a provenance sidecar. *(Requested by the human outside the batch sequence, 2026-09-22; §4b. Row 20 still owes the full manuscript.)* | done |
| 18 | F — Claims & report | Build the claim collection from the tree; generate the hierarchical report. | done |
| 19 | F (cont.) | `/validate cleanroom` and `/validate outsider`; fix what they find. **Before the clean-room comparison, settle the line-ending mismatch noted in §4b (2026-09-21)**: every node's CSV outputs are written with Windows line endings (Python's `csv` module default) while git stores them with Unix endings (`core.autocrlf = input`, no `.gitattributes`), so a fresh clone's result files hash differently from the working-copy digests recorded in provenance. Either write CSVs with `lineterminator="\n"` and re-run (re-hashing every record), or commit a `.gitattributes` that fixes the convention and make the clean-room comparison line-ending-aware — decide, record which, and apply it once for the whole tree rather than node by node. | done |
| 20 | F — Release | Write the manuscript section(s) this project supports; run the release scan; push. | open |

This ledger will grow rows and renumber batch scope the way the prior project's did — a
batch's number is an identifier assigned when it starts, not a position fixed in advance — but
the phase structure above is meant to hold.

## Batch ledger — reports

*(One link per completed batch, added by `/do`. Never overwritten.)*

### Batch 1 — orient and set up

- [[26-09-20_b01_orientAndSetUp]]

### Batch 2 — data, metric, and stage 1

- [[26-09-20_b02_dataAndStage1]]

### Batch 3 — required baselines

- [[26-09-20_b03_baselines]]

### Batch 4 — stage-2 contract and first candidate

- [[26-09-20_b04_stage2LinearLags]]

### Batch 5 — tree-based stage-2 candidate

- [[26-09-20_b05_stage2GradientBoosting]]

### Batch 6 — Bayesian stage-2 candidate

- [[26-09-20_b06_stage2BayesianRidge]]

### Batch 7 — stage-2 main-path decision and input-space forks

- [[26-09-20_b07_stage2MainPathAndInputForks]]

### Batch 8 — climate-covariate stage-2 candidate

- [[26-09-20_b08_stage2LinearClimate]]

### Batch 9 — pooled random forest, adapted from chap-models

- [[26-09-20_b09_stage2PooledRandomForest]]

### Batch 10 — a systematic second iteration on stage 2

- [[26-09-20_b10_stage2SystematicSecondIteration]]

### Batch 11 — the stability plan

- [[26-09-21_b11_stabilityPlan]]

### Batch 12 — the stability run

- [[26-09-21_b12_stabilityRun]]

### Batch 13 — the stability report

- [[26-09-21_b13_stabilityReport]]

### Batch 14 — stage 1 fixed and documented; third stage-2 iteration; main path annotated

- [[26-09-21_b14_stage2ThirdIterationAndMainPath]]

### Batch 15 — the stability set re-run around the annotated main path (v2)

- [[26-09-22_b15_stabilityRunV2]]

### Batch 16 — the phase-E set frozen, and its machinery gated before the year opens

- [[26-09-22_b16_holdoutFreeze]]

### Batch 17 — the held-out year opened once, and what it said

- [[26-09-22_b17_finalValidation]]

### Row 17b — the overview article

- [[26-09-22_twoStageDengueLaos]]

### Batch 18 — the claim collection and the hierarchical report

- [[26-09-22_b18_claimsAndReport]]

### Batch 19 — the clean-room and outsider checks

- [[26-09-23_b19_cleanroomAndOutsider]]

