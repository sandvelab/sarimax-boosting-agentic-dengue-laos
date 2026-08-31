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

- **Target venue**: ***PLoS Computational Biology*** (human-set, 2026-08-31). The manuscript
  this case serves updates Sandve et al., *PLoS Comput Biol* 9(10): e1003285 (2013), which
  is both the precedent and now the target.
- **Status**: analysis (phase A complete, batches 1–5; phase B complete, batches 6–7; phase C complete, batches 8–11; **phase D complete — batches 12, 13, 22, 14 and 15; phase E under way — batch 16 opened the holdout and ran the frozen set on it, batch 17 completed the claim collection and built the hierarchical report, and batch 18 is next**). Twenty batches in the ledger, plus **batch 20, which was optional and is confirmed — it runs before batch 19, so the remaining order is 18, 20, 19** — plus **batch 21 on the branch `greedy`** — a counterfactual that iterates batch 9's promotion rule to a fixpoint, is never merged, and produces no reported result. What it settled is in the plan's §4b. **The ledger is executed top to bottom and a batch's number is an identifier, not a position**: batch 22 was added between 13 and 14.
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
| Compute budget for stability work | Phase D is batches 12, 13, 22, 14, 15. The perturbation manifest is two tiers — every fork taken alone, then eight pairs selected by a rule fixed in advance — over **seventeen** forks, run on development and again on the holdout. Batch 12 wrote it: **24 tier-1 combinations, 8 tier-2 slots**, in `analysis/05_stability/results/manifest.csv`, committed before any of it ran. It was planned at 124 minutes on development and 75 on the holdout, against a **12-hour budget** the agent set so the cut order has something to be a cut against; nothing is cut and the cut order is recorded. **The whole development manifest has run and took 3.66 hours**, summed from `run_status.csv` over all 32 rows. Over the rows the manifest costed, planned and actual agree at 7 469 s — a ratio of **1.00** — with per-row ratios from 0.52 to 1.91, which is batch 13's finding confirmed a second time: the total is right and no individual row is, so the cut order those estimates rank carries no information. Compute is not what binds and it is not close — most of it is re-running the reference model, four unseeded repeats through an amd64 image under emulation, for the one model the plan forbids perturbing. **The phase-E half was frozen at an estimated 2.07 hours** (`analysis/05_stability/results/manifest_holdout.csv`) **and ran in 2.39, a ratio of 1.15** — the first estimates in this project that were predictions rather than measurements of runs that had already happened, and the worst row is again `retrain_everySplit` at 1.97 (`results/holdout_cost_planned_vs_actual.json`). |
| Stability, reported | **Phase D is done. The development set is 32 analyses and the result is a distribution, not a number** (`analysis/05_stability/results/distribution.json`). Reported skill spans **−0.0724 to +0.2320** around the main path's +0.1485, **which sits thirteenth of thirty-two**; our model beats the reference on **27 of 32** and both required baselines on 27, and the failures are structured — the five rows the reference wins are the five that replace our model or refit its weights, the five a baseline wins are the five that weight the mean by cases. 10–90 coverage runs **0.458 to 0.920** against a nominal 0.80. **Six of the seventeen forks move the conclusion further than the reference model moves on its own and eleven do not** (`results/sensitivity_by_fork.csv`), the yardstick being the **0.0218** spread of our skill score against the reference's four unseeded repeats — measured, not chosen. Above it: family 0.2209, pool weighting 0.1820, headline-mean weighting 0.0835, province filter 0.0376, persistence construction 0.0279, training window 0.0219. Below it: nine of the eleven candidate-internal forks phase C spent three batches on. **The model family is what the conclusion is sensitive to and the choices inside a family are not** — swapping the pool for candidate 1 costs 0.2209 of skill, while the eleven forks inside the two member families span 18.638 to 18.933 CRPS, about half the reference's own 0.57 re-run spread. The exception is the pool's own weighting fork, worth 0.1820 and the second-largest move. The scoring fork is worth 0.0835, the five `02_setup` forks at most 0.0376, the two baseline forks at most 0.0279. **Under case weighting a required baseline beats the reported model in every combination it appears in**, five rows of the 32. **And the forks do not compose**: tier 2's largest interaction, −0.1033, is bigger than either main effect behind it — the province filter and case weighting each improve the reported skill alone and almost exactly cancel together. **Phase E ran the same 32 on 2010** (`holdout_distribution.json`, `holdout_vs_development.json`): skill **−0.5038 to +0.2026** around +0.0868, which sits **eighteenth of thirty-two**; our model beats the reference on 26 and both baselines on 27; **28 of the 32 scored worse than on development**, median −0.056. **The ranking of the analyses barely transfers** — rank correlation **+0.396** — while the ranking of the forks transfers better at **+0.679**, with **14 of 17 agreeing** on whether they matter. But the order changes at the top: the **province filter goes from 0.0376 to 0.2696**, the largest fork effect in the project, the family halves to 0.0949, and the pool's weighting collapses to 0.0121 and falls below the band. **The row development ranked fourth (+0.1861), highest of every analysis that does not re-weight the mean, is twenty-ninth on 2010 (−0.1828), with its case-weighted pair worst of all at −0.5038**, and it is a fork that moves the *reference* — our pool goes 76.73 → 76.56 while the reference goes 84.03 → 64.72. |
| Storage budget | **Not a constraint.** A few gigabytes for the whole repository is fine (human-set, 2026-08-29, on batch 22's question). Nothing is pruned and no batch plans around disk; `/annotate-criticality` keeps annotating so that a future decision would be targeted. Measured now that both manifests have run: `analysis/` holds **18 GB**, of which **16 GB is `analysis/**/work/`** — chap-core's per-split run directories, gitignored since batch 7 and read by nothing after a run. What the repository tracks under `analysis/` is **1.6 GB** of `results/`. Still inside what the human called fine, and the holdout's rows are about half the size of their development twins because the backtest is four splits rather than eight. |
| Data governance | Public and redistributable. The Lao files are pinned by repository commit hash, copied into `Archive/` unmodified, marked `(IS_SHADOW)`, with `provenance.md`. Nothing here is access-restricted, so the release scan is about secrets, not permissions. |
| Target | `disease_cases` (reported dengue), monthly, admin-1, Laos. |
| What the metric is a mean over | **16 provinces, 371 cells** on development — not the 18 provinces in the file. Vientiane (LA-VI) reports nothing and is dropped by Chap's region filter; Xaisomboun (LA-XN) stops reporting after 2005 and contributes no evaluable cell. Established in batch 3. |
| Metric | Mean CRPS across regions × splits, produced by Chap's own evaluation. Secondary: interval coverage, MAE. |
| Reported conclusion | A skill score against the reference model, `1 − CRPS_ours / CRPS_ewars`, computed per analysis by a script, with raw CRPS and coverage beside it. Relative rather than absolute, so that the development and held-out spreads can be read on one axis instead of confounding inflated performance with a harder year. **+0.1485 on development and +0.0868 on the held-out year** (`analysis/results/main/conclusion.json`, `analysis/results/main__holdout/conclusion.json`): mean CRPS **18.817** against the reference's 22.098, ahead of both required baselines, ahead of each of the reference's four repeats individually, and better in six of the eight splits. The reported model is **candidate 3, the linear opinion pool**, promoted onto the main path in batch 11. It is also the most over-dispersed model in the project — 10–90 coverage 0.863 against nominal 0.80, 25–75 coverage 0.749 against 0.50 — and §2's rule that a badly calibrated CRPS winner has not won is why that is reported beside the score rather than under it. On 2010 that over-dispersion does not survive: 10–90 coverage is **0.755**. Beside the ratio, the raw figures on the holdout are **76.731 against the reference's 84.026** over 192 cells — 2010 is about four times the CRPS of the development period for every model in the comparison, which is what the ratio exists to control for. |
| Required baselines | Persistence and seasonal climatology, implemented as Chap-compatible models so they traverse the identical evaluation path. Each has a fork on how it is constructed, and batch 22 ran both: the persistence fork is worth **4.181 CRPS** — the second published construction scores 20.698 and **beats the reference model** — and the climatology window fork 0.532, inside the noise floor. The reported analysis takes the worse persistence construction, and the pool is better off for it. |
| Reference model to beat | `https://github.com/chap-models/chapkit_ewars_model` (WHO EWARS-csd), at its own default configuration — on the cross-validated development backtest **and** on the held-out year. Not tuned by us. Pinned by image digest `sha256:abd8098f…` (= source commit `a4c2fa42`); runs as an amd64 chapkit service under emulation, so **Docker must be running**. Its development mean CRPS is **22.098**, the per-cell mean of four repeats scored from inside the tree in batch 7 (batch 4's reconnaissance figure was 21.9). It is **unseeded**: the four repeats span 21.820 to 22.385, so a margin under **~0.57 CRPS** against it means nothing. |
| Project seed, derived | Every component seed is `int(blake2b("<project seed>:<component>", digest_size=8), 16) % 2**32`, computed by `analysis/scripts/lib/project_seed.py`, which reads the project seed from the table above rather than carrying a copy. Fixed in batch 8, the first batch with anything to seed. |
| What counts as success | Beating both baselines and EWARS. Nothing here can reach statistical significance and no attempt is made to suggest it does: the comparison is reported with its per-region and per-split spread and a plain statement of what that spread can distinguish. "We cannot separate these two" is a conclusion. **The backtest's resolution is a property of the pair being compared, not of the dataset** — batch 7 measured about 4 CRPS using the baselines; batch 8's candidate cleared two standard errors; batch 9's candidate is **1.03 standard errors** from the reference, which is the "cannot separate" case arriving in practice; batch 10's candidate 2 is **1.20 standard errors on the other side** of it, which is the same case with the sign reversed; batch 11's pool is **1.90 standard errors** on that side, which is the largest margin the project has and still short of separating the two. Nothing below **0.57 CRPS** can be attributed to a model at all, which is the reference's own re-run spread. |
| Shape of the reported result | A **spread, not a point**, on both datasets, and both are now reported. Development runs **−0.0724 to +0.2320**; the holdout runs **−0.5038 to +0.2026**, a range of 0.706 against 0.304 — **more than twice as wide**. The set was frozen before the year was opened, so the second spread is a measurement rather than a selection. |
| Model service framework | `chapkit` may be used to build our own models against the Chap contract. Permitted, not mandated. |
| Development data | 1998-01 to 2009-12. The only file development ever sees. |
| Held-out data | 2010-01 to 2010-12. **Opened once, in batch 16**, and evaluated across the manifest frozen in batch 15. The file phase E reads is `analysis/01_data/01_partition/results/phase_e_1998-01_2010-12.csv`, written by `open_holdout.py` from the two parts beside it and byte-identical to the archived source; which of the two files a combination reads is decided by the `__holdout` suffix, in `analysis/scripts/lib/combos.py` and nowhere else. |
| Backtest scheme (`n-periods`, `n-splits`, `stride`) | **Development: 3, 8, 3** (`n-retrain` 1) — evaluates 2008-01 to 2009-12 from a training set ending 2007-12. **Phase E: 3, 4, 3** on the full file — evaluates exactly 2010. Fixed in batch 3; it does not move, because a horizon changed midway makes every earlier number incomparable. Verified against chap-core's own splitter in `analysis/01_data/02_characterise/results/split_schedule.csv`. |
| Git remote | **`github.com/sandvelab/veridical-agentic-dengue-laos`** (human-set, 2026-08-31, reversing the earlier position that none was to be created). Created and pushed as the **last** step of batch 19's `/release`, after the secrets and data-permission scan, `/validate cleanroom`, `/validate outsider` and both generated reports — a release that pushes before its own scan has not run its scan. The agent asks before the push. Feasible as measured: `.git` is **131 MB** packed and no tracked file exceeds 50 MB, though the working tree is 1.6 GB. |

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
   **This has happened: batch 16 opened it, on 2026-08-31, and ran exactly the set frozen in
   batch 15.** The driver enforces the second half, on **two conditions and needing both**:
   the row is recorded as `ran` in `05_stability/results/run_status_holdout.csv`, which is
   versioned, so re-running one means deleting its row and that shows in git; and
   `05_stability/results/.holdout_opened`, which is gitignored, says that *this working
   tree* is the one that opened the year. **Batch 18's clean-room check found that the
   versioned condition alone sealed every clone of the repository too**, so all thirty-two
   rows were skipped in a fresh checkout and the phase-E half of `analysis/run.sh`
   reproduced its outputs without running the analysis behind them.
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

Anything that spends real money; abandoning the local Chap install for a hosted service; any
change to the success criterion or to the five points above. **Creating the remote is no
longer open** — it was settled on 2026-08-31, owner and name both, and the agent still asks
before the push itself. The success criterion was settled on 2026-08-23 and is now fixed — including what to
do if EWARS cannot be run on this dataset, which the plan's §2 answers.

Two things that were open and are not: **the case write-up's judgment about where this
setup was more trouble than it was worth is the agent's**, offered back for comment
afterwards, and batch 19 labels it `agent-autonomous` rather than jointly held; and
**`analysis/run.sh` is not split**, so it reproduces both distributions and the clean-room
check in batch 18 is a six-hour run. Both human-set, 2026-08-31, on batch 16's questions.

## Where things are

- The analysis is a tree of questions under `analysis/`. Start at
  `AI-generated/hierarchical-report/index.html`, or `/node tree`. **Batch 17 built that
  report**: 1 175 pages, the tree above and four levels below it — the national mean each
  model was scored at, that mean by province, each province month by month, and the
  per-cell scores everything above is an average of, for each of the 65 combinations that
  were scored. Every number on it is displayed from the file the analysis wrote. It is
  gitignored and rebuilt in about two seconds by `/hierarchical-report`; only its
  `provenance.md` is versioned. Its full design — every node,
  every fork, the file contract between them, and the `COMBO` mechanism that lets one code path
  serve both the main analysis and the stability run — is in
  `AI-generated/batch-reports/26-08-26_b05_bootstrapPlan.md`. **Batch 7 built it**, and
  `bash analysis/run.sh` reproduces the whole reported analysis **and the distribution around
  it**: batch 15 put the perturbation driver into `05_stability/run.sh` and batch 16 the
  phase-E half after it, so the run is about six hours rather than the twenty minutes it was
  through batch 14. Most of the difference is the reference model's four unseeded repeats
  through an amd64 image under emulation, now on two datasets.
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
  and deliberately **not** in `run.sh` until batch 15; the two defects that held fourteen
  built rows are fixed and those rows have run.
  **Batch 16 opened the holdout and ran the frozen set on it.** `01_data/01_partition`
  gained `open_holdout.py`, which reassembles the archived file from the two parts beside it
  and verifies the result byte for byte, so the node that was the only one licensed to read
  the whole record is still the only one that does. Which of the two files a combination
  reads, which backtest scheme it runs under and which span its province and training-window
  forks call "evaluated" are all decided by the `__holdout` suffix, in
  `analysis/scripts/lib/combos.py` and nowhere else — six setup scripts and `conclude.py`
  read it rather than carrying a copy. `run_manifest.py --dataset holdout` runs the set; its
  one different row is the main path, which on development runs `conclude.py` alone and here
  runs the whole pipeline. The phase-E half of `05_stability/run.sh` follows it, so
  `analysis/run.sh` is now about six hours and reproduces both distributions.
  **Batch 15 reported the distribution and froze the phase-E set**: `distribution.json`,
  `distribution_rows.csv`, `sensitivity_by_fork.csv` and three figures at `05_stability`,
  the driver added to `run.sh` after checking that re-planning returns the frozen manifest
  byte-identical, `manifest_holdout.csv` with each row's development conclusion frozen
  beside it, and the `combos` invariant extended to read both manifests. The first twelve
  claims are in `Human-AI-collaboration/claims/claims.md`.
  **Batch 14 ran them and tier 2, and fixed four things**: `prepare_members.py` ran every
  member fork's main-path child where the combination had already moved one; `conclude.py`
  read our reported model off `claim.md` rather than off the results, so every family row
  would have said `candidate_exists: false`; `03_compare` computed its paired spread
  unweighted beside a leaderboard that followed the weighting fork, so the two weighting rows
  had been carrying the main path's own spread under a re-weighted mean; and the driver
  called a family's `run.sh` after the moved child, which re-runs that fork's sibling when
  the fork belongs to the family that is running. **All four are the same fork-blindness** —
  a step that discovers something from the tree, written when every fork had one child that
  did anything — and this is the fourth, third and last count of it. The batch also carried
  out the **assembler lift** batches 10 and 11 both logged and deferred to whichever batch
  re-ran the combinations those scripts configured: `03_models/scripts/lib/assemble_config.py`
  is now the one way a candidate family's configuration is assembled, and the three families
  are one-screen runners.
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
- Everything the analysis supports is in `Human-AI-collaboration/claims/claims.md` — **39 claims**. Batch 15 wrote the first twelve, all of them phase D's; batch 16 added nine, all of them phase E's; and **batch 17 added eighteen**, which are the phase-A, -B and -C half the file had been missing — the development headline and what its margin cannot separate, the reference model's own re-run floor, what pooling bought and what fitting its weights cost, the family that never beat the reference, three statements in the dataset's schema that do not describe the file, and the determinism of every model we wrote. **A claim may state what follows trivially from the figures it cites — a ratio, a ranking — and may not state anything that needed a step nobody ran** (human-set, 2026-08-31, settling batch 17's question). So the paired margin is reported as 3.282 CRPS against a split-clustered standard error of 1.726 *and* as the 1.90 standard errors that quotient makes it.
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

1. `analysis/run.sh` reproduces the reported analysis from a clean environment — and, since
   batch 15, the whole perturbation set with it, and since batch 16 the same set on the
   held-out year.
2. Every reported result traces to a file that was executed.
3. Every sentence in the manuscript traces to a claim, to a result, to a command.
4. The alternatives not taken are still in the tree, runnable.
5. `/validate invariants` passes, because it was satisfied rather than weakened.
6. This file describes the project as it actually is.
