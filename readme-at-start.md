# Read this first

The first thing to read in a new session, human or agent. It says what *this particular*
project is. When it stops matching reality it is worse than nothing.

Then read `AGENTS.md` — the standing instructions, and the single source of truth for how
work is done here.

---

## The project

**Develop, as autonomously as the setup allows, a spatio-temporal model that forecasts
monthly dengue case counts across the provinces of Laos, and make it perform decently under
Chap's own standard evaluation — while producing the complete veridical record of how it
came about.** The data is `chap_LAO_admin1_monthly.csv` from
`github.com/dhis2/climate-health-data`: monthly reported dengue counts for the admin-1
provinces of Laos, 1998–2010, with rainfall, mean temperature, mean relative humidity and a
static population figure. The evaluation is Chap's own cross-validated backtest (`chap
eval`), run against a locally installed, version-pinned `chap-core`; the headline number is
**mean CRPS across regions and across test splits**, reported with calibration beside it.

Two things are produced at once and neither is subordinate to the other: a forecasting
model with a defensible score, and the record of every execution, environment, judgment call
and rejected alternative behind it, together with how far the conclusion survives them. The
second is the reason the first is being done — **a model that scores well but whose
development cannot be reconstructed is a failed run of this project.**

The article this record feeds is the worked case for
`Archive/case-source-material/reproAgenticAiManuscript.md`, whose *An illustrating case*
section is currently unwritten. The project also belongs to the TrustAgentic proposal
(`trustAgenticProposal.md`), which asks how far an agentic system gets on a real,
representative research problem, and where it fails.

## The article

- **Target venue**: not fixed in the source material. The manuscript this case serves updates
  Sandve et al., *PLoS Comput Biol* 9(10): e1003285 (2013), which is the obvious precedent.
- **Status**: analysis (phase A complete, batches 1–5; phase B complete, batches 6–7; phase C complete, batches 8–11; **phase D under way — batches 12, 13 and 22 done, batch 14 next**). Twenty batches in the ledger, plus one optional, plus **batch 21 on the branch `greedy`** — a counterfactual that iterates batch 9's promotion rule to a fixpoint, is never merged, and produces no reported result. What it settled is in the plan's §4b. **The ledger is executed top to bottom and a batch's number is an identifier, not a position**: batch 22 was added between 13 and 14.
- **Manuscript**: `Human-AI-collaboration/manuscript/`
- **The plan being executed**:
  `Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`. It carries the
  batch ledger; `/do` runs the next open batch and stops.

## Settings this project has fixed

| Setting | Value |
|---|---|
| Project random seed | `20260822`. Every component seed derives from it. |
| Main environment | `environment/` — CPython 3.13.0 and `chap-core==2.1.0`, **installed from** `environment/lock.txt` by `environment/install-chap.sh`, which reports any difference between what it built and that file. Invoked as `environment/chapenv/bin/chap`. Not the same as `.venv`, which runs the repository's own machinery. The Docker layer builds (verified batch 7). |
| Repository machinery interpreter | `.venv/bin/python` — CPython 3.13.7, created 2026-08-23 with `python3 -m venv .venv` on macOS 26.6.2 (arm64). |
| Tracking level | **full** (`AGENTS.md` §6). This project is *about* tracking, so the usual argument for a lighter touch does not apply. Raise it with me rather than drifting. |
| Compute budget for stability work | Phase D is batches 12, 13, 22, 14, 15. The perturbation manifest is two tiers — every fork taken alone, then eight pairs selected by a rule fixed in advance — over **seventeen** forks, run on development and again on the holdout. Batch 12 wrote it: **24 tier-1 combinations, 8 tier-2 slots**, in `analysis/05_stability/results/manifest.csv`, committed before any of it ran. It costs **124 minutes on development and 75 on the holdout**, against a **12-hour budget** the agent set so the cut order has something to be a cut against; nothing is cut and the cut order is recorded. Compute is not what binds and it is not close — **89 of the 124 minutes are re-running the reference model**, four unseeded repeats on each of five setup rows, for the one model the plan forbids perturbing. |
| Stability, so far | **10 of the 24 tier-1 rows have conclusions** (batches 13 and 22). The five `02_setup` forks span skill **+0.1266 to +0.1861** around the main path's +0.1485 — every gap smaller than the reference's own 0.57 CRPS re-run spread. The single `04_score` weighting fork moves it four times as much: **+0.2288** population-weighted, **+0.2320** case-weighted, from re-weighting a stored file and re-running no model. **Under case weighting persistence beats the reported pool**, 86.598 to 88.484, and the pool's 10–90 coverage falls from 0.863 to 0.701. The two **baseline** forks are the extremes: freezing the climatology's estimation window moves the conclusion by 0.0025 of skill, and the persistence construction by **−0.0279**, the largest move of any row. |
| Data governance | Public and redistributable. The Lao files are pinned by repository commit hash, copied into `Archive/` unmodified, marked `(IS_SHADOW)`, with `provenance.md`. Nothing here is access-restricted, so the release scan is about secrets, not permissions. |
| Target | `disease_cases` (reported dengue), monthly, admin-1, Laos. |
| What the metric is a mean over | **16 provinces, 371 cells** on development — not the 18 provinces in the file. Vientiane (LA-VI) reports nothing and is dropped by Chap's region filter; Xaisomboun (LA-XN) stops reporting after 2005 and contributes no evaluable cell. Established in batch 3. |
| Metric | Mean CRPS across regions × splits, produced by Chap's own evaluation. Secondary: interval coverage, MAE. |
| Reported conclusion | A skill score against the reference model, `1 − CRPS_ours / CRPS_ewars`, computed per analysis by a script, with raw CRPS and coverage beside it. Relative rather than absolute, so that the development and held-out spreads can be read on one axis instead of confounding inflated performance with a harder year. **Currently +0.148** (`analysis/results/main/conclusion.json`): mean CRPS **18.817** against the reference's 22.098, ahead of both required baselines, ahead of each of the reference's four repeats individually, and better in six of the eight splits. The reported model is **candidate 3, the linear opinion pool**, promoted onto the main path in batch 11. It is also the most over-dispersed model in the project — 10–90 coverage 0.863 against nominal 0.80, 25–75 coverage 0.749 against 0.50 — and §2's rule that a badly calibrated CRPS winner has not won is why that is reported beside the score rather than under it. |
| Required baselines | Persistence and seasonal climatology, implemented as Chap-compatible models so they traverse the identical evaluation path. Each has a fork on how it is constructed, and batch 22 ran both: the persistence fork is worth **4.181 CRPS** — the second published construction scores 20.698 and **beats the reference model** — and the climatology window fork 0.532, inside the noise floor. The reported analysis takes the worse persistence construction, and the pool is better off for it. |
| Reference model to beat | `https://github.com/chap-models/chapkit_ewars_model` (WHO EWARS-csd), at its own default configuration — on the cross-validated development backtest **and** on the held-out year. Not tuned by us. Pinned by image digest `sha256:abd8098f…` (= source commit `a4c2fa42`); runs as an amd64 chapkit service under emulation, so **Docker must be running**. Its development mean CRPS is **22.098**, the per-cell mean of four repeats scored from inside the tree in batch 7 (batch 4's reconnaissance figure was 21.9). It is **unseeded**: the four repeats span 21.820 to 22.385, so a margin under **~0.57 CRPS** against it means nothing. |
| Project seed, derived | Every component seed is `int(blake2b("<project seed>:<component>", digest_size=8), 16) % 2**32`, computed by `analysis/scripts/lib/project_seed.py`, which reads the project seed from the table above rather than carrying a copy. Fixed in batch 8, the first batch with anything to seed. |
| What counts as success | Beating both baselines and EWARS. Nothing here can reach statistical significance and no attempt is made to suggest it does: the comparison is reported with its per-region and per-split spread and a plain statement of what that spread can distinguish. "We cannot separate these two" is a conclusion. **The backtest's resolution is a property of the pair being compared, not of the dataset** — batch 7 measured about 4 CRPS using the baselines; batch 8's candidate cleared two standard errors; batch 9's candidate is **1.03 standard errors** from the reference, which is the "cannot separate" case arriving in practice; batch 10's candidate 2 is **1.20 standard errors on the other side** of it, which is the same case with the sign reversed; batch 11's pool is **1.90 standard errors** on that side, which is the largest margin the project has and still short of separating the two. Nothing below **0.57 CRPS** can be attributed to a model at all, which is the reference's own re-run spread. |
| Shape of the reported result | A **spread, not a point**, on both datasets. The phase-D perturbation set is frozen before the holdout is opened and re-run on it, so development and holdout are both reported as distributions over the analyses that all looked reasonable. |
| Model service framework | `chapkit` may be used to build our own models against the Chap contract. Permitted, not mandated. |
| Development data | 1998-01 to 2009-12. The only file development ever sees. |
| Held-out data | 2010-01 to 2010-12. Sealed until the final validation. |
| Backtest scheme (`n-periods`, `n-splits`, `stride`) | **Development: 3, 8, 3** (`n-retrain` 1) — evaluates 2008-01 to 2009-12 from a training set ending 2007-12. **Phase E: 3, 4, 3** on the full file — evaluates exactly 2010. Fixed in batch 3; it does not move, because a horizon changed midway makes every earlier number incomparable. Verified against chap-core's own splitter in `analysis/01_data/02_characterise/results/split_schedule.csv`. |
| Git remote | None, and none is to be created. `/release` prepares the repository and stops. |

## What must not happen

These override everything else here.

1. **The final year is removed from the data before any work begins, and opened once.**
   2010 is cut off into a separate holdout file; development, tuning, selection and the whole
   backtest happen on 1998-01 to 2009-12 and nothing is pointed at anything else until the
   final validation. The holdout's case values are not read, plotted, characterised or
   reasoned about during development. If the holdout is opened a second time, that it happened
   and why is recorded. It is opened once but *evaluated* many times — across the frozen
   perturbation manifest — and that is only honest because the manifest was fixed beforehand:
   **nothing is added, dropped, re-tuned or re-run after a holdout number has been seen.**
2. **No number reaches a claim except through a file.** `chap eval` writes NetCDF, `chap
   export-metrics` writes CSV; every reported figure is read from one of those by a script,
   never from terminal output. (`AGENTS.md` §1.)
3. **Every judgment call is an alternatives node or a logged decision, never silent** — and
   carries its agency: `human-set`, `agent-on-human-assessment`, `agent-autonomous`; for
   information gathering, `agent-retrieved` or `human-pointed`.
4. **Failures are kept.** Models that did not work, installs that did not build, approaches
   abandoned: they stay in the record with what went wrong.
5. **Chap runs locally, from a pinned version** — not against a hosted service. If a local
   install proves genuinely impossible, stop and report rather than switching.

## Left to the human, not to the agent

Creating a git remote and naming it; anything that spends real money; abandoning the local
Chap install for a hosted service; any change to the success criterion or to the five points
above. The success criterion was settled on 2026-08-23 and is now fixed — including what to
do if EWARS cannot be run on this dataset, which the plan's §2 answers.

## Where things are

- The analysis is a tree of questions under `analysis/`. Start at
  `AI-generated/hierarchical-report/index.html`, or `/node tree`. Its full design — every node,
  every fork, the file contract between them, and the `COMBO` mechanism that lets one code path
  serve both the main analysis and the stability run — is in
  `AI-generated/batch-reports/26-08-26_b05_bootstrapPlan.md`. **Batch 7 built it**, and
  `bash analysis/run.sh` reproduces the whole reported analysis in about twenty minutes.
  `analysis/README.md` is the map. Every node below `01_data` reads and writes under
  `results/$COMBO/`, which defaults to `main`. **Batch 8 added `03_models/03_candidate`**,
  our own model families: `a_hierNB` and the four forks that configure it. Its
  configuration reaches the model as a file assembled from those forks and passed to
  `chap eval --model-configuration-yaml`, which is also where the component seed enters.
  **Batch 9 built every remaining child of those forks and added two more forks** —
  `05_autoregressive` and `06_yearVariance` — ran all nine alternatives on development, and
  promoted three of them onto the main path. The candidate now beats both required baselines
  and is 1.03 standard errors from the reference. A second environment variable,
  `COMBO_BASE`, lets a combination inherit what it did not move; `analysis/run.sh` sets
  none, so the reported analysis inherits nothing.
  **Batch 10 added `03_models/03_candidate/b_boosted`** — candidate 2, gradient-boosted trees
  with a probabilistic head — and its two forks, `01_features` and `02_head`. It scores
  **20.771** on development. The model brings **scikit-learn** into a
  model environment for the first time, pinned by the `uv.lock` beside it, and stores its
  fitted ensembles as JSON the project's own code can walk without scikit-learn installed.
  **Batch 12 added `05_stability`** — the perturbation manifest and the driver — and, with
  it, the **nine fork children the tree had named in prose and never carried**: the second
  child of each `02_setup` fork, both children of the scoring fork, and the second child of
  each baseline fork. They are nodes with claims and no scripts; batches 13 and 22 wrote
  them, and **every child the tree names is now a path the tree carries**. The manifest is computed from the tree by `scripts/lib/inventory.py`, so it counts
  **seventeen forks** where batch 5's hand-written list counted ten, and
  `/validate invariants` gained a **`combos`** check that fails when the manifest and the
  tree disagree, or when a `results/` directory holds a combination nobody planned. **Batch
  11's promotion changed what two of the forks reach**: the pool takes both required
  baselines as members, so a fork on how persistence wraps its uncertainty now moves our
  reported model as well as the persistence row. The driver, `run_manifest.py`, is written
  and deliberately **not** in `run.sh` until batch 15, because fourteen built rows still need
  two defects fixed first — both recorded in `results/manifest_notes.json`.
  **Batch 22 added the two baseline forks' children** — the parametric persistence
  construction and the frozen-window climatology, each its own Chap contract directory. It
  found and fixed two more fork-blind globs, neither reachable until a fork had two built
  children: `prepare_members.py` would have made the reported pool a **six-member pool with
  two persistence baselines and two climatologies**, silently, under `main`; and `01_collect`
  inherited from `COMBO_BASE` per node rather than per fork, which would have put both
  constructions on one leaderboard. Both leave every existing result byte-identical.
  **Batch 11 added `03_models/03_candidate/c_ensemble`** — candidate 3, a linear opinion pool
  over the two candidate families and both required baselines — with one fork, `01_weighting`.
  It scores **18.817** and **the family fork was promoted to it**, so `analysis/run.sh` now
  reproduces the pool and the two demoted families run under `family_hierNB` and
  `family_boosted`. The pool holds no member code: each member runs through **its own Chap
  entry points**, read out of the member's own `MLproject`, and its configuration is assembled
  under the running combination by that family's own scripts — so a phase-D perturbation of a
  member's fork moves the pool's member with it. Its sibling fork child, which fits the weights
  by minimising the pool's CRPS on a year held back inside the training frame, is **4.021 CRPS
  worse**, and that is the batch's most useful result rather than a footnote.
- Batch reports, one per executed batch, are in `AI-generated/batch-reports/`. Checks on the
  method — clean-room, determinism — are in `AI-generated/validation/` and
  `AI-generated/determinism-checks/`. What every alternative to a candidate's configuration
  scores, and the rules by which forks and families are promoted, are in
  `AI-generated/candidate-forks/` — two rounds for candidate 1, `boosted_round1/` for
  candidate 2 and `ensemble_round1/` for candidate 3, whose forks all stayed put, plus
  `families/` and `family_rule.md`, which are what the family fork was moved on. The numbers there are copied from files
  inside the tree, and it is a phase-C selection aid rather than the phase-D stability
  result.
- The vertical slice that preceded the tree is in `AI-generated/vertical-slice/`. Its numbers
  are **not** reported results; the tree reproduces them exactly, and the persistence model
  itself now lives at `analysis/03_models/01_baselines/01_persistence/a_empiricalChange/`.
- What the reference model and the rest of Chap's model library can do on *this* dataset — the
  reference's score, cost and repeatability, and an inventory of the 39 `chap-models`
  repositories — is in `AI-generated/method-reconnaissance/`, rebuilt by
  `AI-internal/reconnaissance/`. Those numbers establish the criterion; they are not yet
  results of this project.
- What the Chap platform is and does — the CLI surface, the model contract, and one worked
  `chap eval` on an unrelated example dataset — is captured in
  `AI-generated/chap-reconnaissance/`, rebuilt by `AI-internal/reconnaissance/`. None of
  those numbers is a result of this project.
- Source material — the manuscript, the 2013 rules, the proposal and its supplement, and the
  Chap orientation note — is in `Archive/case-source-material/`.
- The annual national population series the population fork back-casts from is in
  `Archive/lao-population/`, fetched from the World Bank by
  `AI-internal/data-acquisition/fetch_lao_population.sh`. Batch 13 established from it that
  **the dataset's population column does not have the level its schema claims**: it sums to
  4.96 M against a stated 2020 reference whose national total was 7.35 M, matching the country
  around 1995. That is the third statement in that schema found not to describe the file.
- The data is in `Archive/lao-dataset/`, at commit `af362d52` of `dhis2/climate-health-data`,
  with a checksum manifest that `analysis/01_data/01_partition` re-verifies on every run. That
  node is the only one licensed to read the full file; everything else reads the development
  file it writes. `AI-internal/data-acquisition/` holds the fetch script.
- The plan **as it was delivered**, before any of it had been run, is in
  `Archive/plan-as-delivered/`. The live plan is edited as the project runs; how far the two
  have drifted, and who drove each change, is a reported result rather than bookkeeping. The
  plan's §4b logs each decision settled during execution, with its agency.
- Everything the analysis supports is in `Human-AI-collaboration/claims/claims.md`.
- Nothing enters the manuscript that is not in that file.

## How to work here

- **Bring source material in**: place it in `Archive/`, marked `(IS_SHADOW)` on line 2,
  with a `provenance.md` beside it. Never edit it in place.
- **Add a question to the analysis**: `/node new <parent> <name> "<claim>"`.
- **After any analysis run**: `/track-result`, `/commit-run after`, `/validate invariants`.
- **When something is worth saying**: `/claims add`.
- **Before release**: `/validate cleanroom`, `/validate outsider`, `/hierarchical-report`,
  `/repro-report`, `/release`.

## What has to stay true

1. `analysis/run.sh` reproduces the reported analysis from a clean environment.
2. Every reported result traces to a file that was executed.
3. Every sentence in the manuscript traces to a claim, to a result, to a command.
4. The alternatives not taken are still in the tree, runnable.
5. `/validate invariants` passes, because it was satisfied rather than weakened.
6. This file describes the project as it actually is.
