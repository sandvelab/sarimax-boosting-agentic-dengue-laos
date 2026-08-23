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
- **Status**: analysis (phase A — orientation and bootstrap; batches 1–3 done, batch 4 next).
- **Manuscript**: `Human-AI-collaboration/manuscript/`
- **The plan being executed**:
  `Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`. It carries the
  batch ledger; `/do` runs the next open batch and stops.

## Settings this project has fixed

| Setting | Value |
|---|---|
| Project random seed | `20260822`. Every component seed derives from it. |
| Main environment | `environment/` — CPython 3.13.0 and `chap-core==2.1.0`, built by `environment/install-chap.sh`, resolved in `environment/lock.txt`. Invoked as `environment/chapenv/bin/chap`. Not the same as `.venv`, which runs the repository's own machinery. |
| Repository machinery interpreter | `.venv/bin/python` — CPython 3.13.7, created 2026-08-23 with `python3 -m venv .venv` on macOS 26.6.2 (arm64). |
| Tracking level | **full** (`AGENTS.md` §6). This project is *about* tracking, so the usual argument for a lighter touch does not apply. Raise it with me rather than drifting. |
| Compute budget for stability work | Phase D gets roughly 4–6 batches. `/perturb` estimates the cost of each perturbation, ranks by expected informativeness, cuts at that line and **records where the line fell and what was below it**. If the overall budget binds, cut phase D before phase E. |
| Data governance | Public and redistributable. The Lao files are pinned by repository commit hash, copied into `Archive/` unmodified, marked `(IS_SHADOW)`, with `provenance.md`. Nothing here is access-restricted, so the release scan is about secrets, not permissions. |
| Target | `disease_cases` (reported dengue), monthly, admin-1, Laos. |
| What the metric is a mean over | **16 provinces, 371 cells** on development — not the 18 provinces in the file. Vientiane (LA-VI) reports nothing and is dropped by Chap's region filter; Xaisomboun (LA-XN) stops reporting after 2005 and contributes no evaluable cell. Established in batch 3. |
| Metric | Mean CRPS across regions × splits, produced by Chap's own evaluation. Secondary: interval coverage, MAE. |
| Reported conclusion | A skill score against the reference model, `1 − CRPS_ours / CRPS_ewars`, computed per analysis by a script, with raw CRPS and coverage beside it. Relative rather than absolute, so that the development and held-out spreads can be read on one axis instead of confounding inflated performance with a harder year. |
| Required baselines | Persistence and seasonal climatology, implemented as Chap-compatible models so they traverse the identical evaluation path. |
| Reference model to beat | `https://github.com/chap-models/chapkit_ewars_model` (WHO EWARS-csd), at its own default configuration — on the cross-validated development backtest **and** on the held-out year. Not tuned by us. |
| What counts as success | Beating both baselines and EWARS. Nothing here can reach statistical significance and no attempt is made to suggest it does: the comparison is reported with its per-region and per-split spread and a plain statement of what that spread can distinguish. "We cannot separate these two" is a conclusion. |
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
  `AI-generated/hierarchical-report/index.html`, or `/node tree`.
- Batch reports, one per executed batch, are in `AI-generated/batch-reports/`.
- What the Chap platform is and does — the CLI surface, the model contract, and one worked
  `chap eval` on an unrelated example dataset — is captured in
  `AI-generated/chap-reconnaissance/`, rebuilt by `AI-internal/reconnaissance/`. None of
  those numbers is a result of this project.
- Source material — the manuscript, the 2013 rules, the proposal and its supplement, and the
  Chap orientation note — is in `Archive/case-source-material/`.
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
