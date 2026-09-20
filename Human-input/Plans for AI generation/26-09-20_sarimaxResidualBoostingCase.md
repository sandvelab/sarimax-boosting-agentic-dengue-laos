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
| 8 | C (cont.) — richer stage-2 input | Build a fourth stage-2 alternative, `04_stage2/d_linearClimate`: same family as the main path (`a_linearLags`) with lag-12 climate covariates (rainfall, mean temperature, mean relative humidity) added to its input, isolating the input-richness question from the model-family one. Score it through the same pipeline; decide whether it changes the main-path pick. *(Inserted 2026-09-20, human-set — batch 7 left phase-C-continuation vs. phase-D as an open choice and the human chose to explore richer inputs first; renumbers what were rows 8–15 to 9–16.)* | open |
| 9–11 | D — Stability | Enumerate the judgment calls made so far as a perturbation manifest (stage 1 order/spec, stage 2 family and its inputs, combination rule, training window, zero-handling, anything else that accrued); cost it; freeze the development manifest; run it; report the distribution rather than the single number. | open |
| 12 | D (cont.) / freeze | Freeze the phase-E (holdout) manifest before the holdout opens, per §3. | open |
| 13 | E — Final validation | Open the 2010 holdout once; run exactly the frozen manifest; report the held-out distribution beside the development one. | open |
| 14 | F — Claims & report | Build the claim collection from the tree; generate the hierarchical report. | open |
| 15 | F (cont.) | `/validate cleanroom` and `/validate outsider`; fix what they find. | open |
| 16 | F — Release | Write the manuscript section(s) this project supports; run the release scan; push. | open |

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
