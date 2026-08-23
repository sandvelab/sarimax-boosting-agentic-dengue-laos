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
- **Status**: analysis (phase A — orientation and bootstrap).
- **Manuscript**: `Human-AI-collaboration/manuscript/`
- **The plan being executed**:
  `Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`. It carries the
  batch ledger; `/do` runs the next open batch and stops.

## Settings this project has fixed

| Setting | Value |
|---|---|
| Project random seed | `20260822`. Every component seed derives from it. |
| Main environment | `environment/environment.yml` (the analysis). Not the same as `.venv`, which runs the repository's own machinery. |
| Repository machinery interpreter | `.venv/bin/python` — CPython 3.13.7, created 2026-08-23 with `python3 -m venv .venv` on macOS 26.6.2 (arm64). |
| Tracking level | **full** (`AGENTS.md` §6). This project is *about* tracking, so the usual argument for a lighter touch does not apply. Raise it with me rather than drifting. |
| Compute budget for stability work | Phase D gets roughly 4–6 batches. `/perturb` estimates the cost of each perturbation, ranks by expected informativeness, cuts at that line and **records where the line fell and what was below it**. If the overall budget binds, cut phase D before phase E. |
| Data governance | Public and redistributable. The Lao files are pinned by repository commit hash, copied into `Archive/` unmodified, marked `(IS_SHADOW)`, with `provenance.md`. Nothing here is access-restricted, so the release scan is about secrets, not permissions. |
| Target | `disease_cases` (reported dengue), monthly, admin-1, Laos. |
| Metric | Mean CRPS across regions × splits, produced by Chap's own evaluation. Secondary: interval coverage, MAE. |
| Required baselines | Persistence and seasonal climatology, implemented as Chap-compatible models so they traverse the identical evaluation path. |
| Development data | 1998-01 to 2009-12. The only file development ever sees. |
| Held-out data | 2010-01 to 2010-12. Sealed until the final validation. |
| Backtest scheme (`n-periods`, `n-splits`, `stride`) | *Fixed in batch 3.* It does not move after that, because a horizon changed midway makes every earlier number incomparable. |
| Git remote | None, and none is to be created. `/release` prepares the repository and stops. |

## What must not happen

These override everything else here.

1. **The final year is removed from the data before any work begins, and touched once.**
   2010 is cut off into a separate holdout file; development, tuning, selection and the whole
   backtest happen on 1998-01 to 2009-12 and nothing is ever pointed at anything else. The
   holdout's case values are not read, plotted, characterised or reasoned about during
   development. If the holdout is opened a second time, that it happened and why is recorded.
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
above.

## Where things are

- The analysis is a tree of questions under `analysis/`. Start at
  `AI-generated/hierarchical-report/index.html`, or `/node tree`.
- Batch reports, one per executed batch, are in `AI-generated/batch-reports/`.
- Source material — the manuscript, the 2013 rules, the proposal and its supplement, and the
  Chap orientation note — is in `Archive/case-source-material/`.
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
