# Read this first

The first thing to read in a new session, human or agent. It says what *this particular*
project is. When it stops matching reality it is worse than nothing.

Then read `AGENTS.md` — the standing instructions, and the single source of truth for how
work is done here.

---

## The project

**Develop, as autonomously as the setup allows, a two-stage forecasting ensemble for monthly
dengue case counts across the provinces of Laos: a SARIMAX-family model (stage 1) whose
residuals are corrected by a second model (stage 2), whose family is itself an open judgment
call — and establish whether the second stage earns its place**, together with the complete
veridical record of how it came about. Full aim, success criteria and non-negotiables:
`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`.

The dataset is `chap_LAO_admin1_monthly.csv`, already archived at `Archive/lao-dataset/`
from the prior project this repository carried (below).

**This repository previously carried a different, completed project** — comparing candidate
forecasting models against the WHO EWARS-csd reference on the same dataset, developed to
batch 33 and released publicly at `github.com/sandvelab/veridical-agentic-dengue-laos`. That
project's analysis tree, claims, manuscript and generated documents have been removed from
this repository so it holds one project at a time (`AGENTS.md` §1, §9); the raw archived Lao,
population and sibling-country data were kept, since they are re-usable resources and not that
project's output. Nothing in this file describes that project; its own record is at the URL
above.

## The article

- **Target venue**: not yet decided.
- **Status**: batches 1–10 complete (phases A–C). Stage 1 (per-province SARIMAX,
  mean CRPS 26.05 over 371 cells, 90% coverage 82.7%) beats both required baselines
  (persistence 28.32, seasonal climatology 26.91). Seven stage-2 residual-correction
  candidates exist under `04_stage2`. Five (batches 4–9) were trained on stage 1's
  **in-sample one-step residual** and failed: four lose to stage 1 alone (26.26–28.07); the
  fifth, `e_pooledRandomForest` (25.89), wins on CRPS but collapses coverage to 64.4%.
  Batch 10's diagnostic node `05_residualStructure` showed why — that residual is essentially
  white, while the **h-step out-of-sample error** a stage 2 must correct carries a
  level-dependent over-prediction, a calendar bias and a horizon effect (and unpredictable
  2008–09 reporting-regime breaks that make up the whole coverage deficit). Two candidates
  trained on that error inside each training window, pooled across provinces on the
  standardised-error scale, **both beat stage 1 alone with improved coverage**:
  `f_oosErrorRidge` 25.63 (−1.64%, coverage 84.6%) and `g_oosErrorBoosting` 25.16 (−3.41%,
  coverage 85.7%) — the first candidates to clear both of plan §2's bars.
  **`g_oosErrorBoosting` is `04_stage2`'s main path** (promoted batch 10, agent-autonomous).
  The margin is modest, sits in four provinces and the later splits, and loses ground in
  Savannakhet and Vientiane Capital; whether it survives reasonable alternative choices is
  phase D's question. Logged, untried forks: a correction bounded relative to the forecast
  level; a heavier-tailed or count predictive family at stage 1; per-horizon models; a true
  rolling refit for in-window errors; ENSO indices as an external covariate. Phase D has
  started: batch 11 built `06_stability`, measured that the whole model tree re-runs in 87 s
  with byte-identical outputs, and froze the development perturbation manifest (40 rows: 6
  siblings, 29 planned parametric perturbations, 5 not run with reasons). Batch 12 ran it in
  full (1,937 s; runner verified against the main path first): all 29 perturbations keep the
  two-stage ensemble ahead of stage 1 alone with coverage not worse (−0.70% to −10.64%).
  Batch 13 reports the distribution and what the margin turns on.
- **Manuscript**: `Human-AI-collaboration/manuscript/` (empty).
- **The plan being executed**:
  `Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`. It carries
  the batch ledger (§6); `/do` runs the next open batch and stops.

## Settings this project has fixed

| Setting | Value |
|---|---|
| Project random seed | `20260920`. Every component seed derives from it. |
| Main environment | Pinned, batch 2: CPython 3.13.0, `pandas`/`numpy`/`scipy`/`statsmodels`/`properscoring`. `scikit-learn` added batch 5 (tree-based and Bayesian-ridge stage-2 candidates). Installed from `environment/lock.txt` by `environment/install-env.sh`. Invoked as `environment/env/bin/python`. No Docker. |
| Repository machinery interpreter | `.venv`, created batch 1 (CPython 3.13.7), per `setup-guide.md` §3. |
| Tracking level | **Full** (`AGENTS.md` §6), carried over from the prior project's settled position. Raise it with the human rather than drifting. |
| Compute budget for stability work | One hour of wall-clock, provisional (agent-autonomous, batch 11; plan §4b). Measured: the whole model tree re-runs in 87 s and the planned perturbations are estimated at 24 min, so the budget excludes nothing planned. |
| Storage budget | Not a constraint by default, matching the prior project's settled position; raised with the human if this project's outputs turn out to be unusually large. |
| Data governance | Public and redistributable — the Lao, population and sibling-country data are unchanged from the prior project's archived, checksummed, `(IS_SHADOW)`-marked copies. |
| Target | `disease_cases` (reported dengue), monthly, admin-1, Laos. |
| Development data | 1998-01 to 2009-12. The only file development ever sees. |
| Held-out data | 2010-01 to 2010-12. Sealed until the final validation (plan §3). |
| Backtest scheme | `n_periods 3 / n_splits 8 / stride 3`, reused from the prior project as the default (human-set, 2026-09-20, plan §4b), for comparability between the two projects. |
| Evaluation harness | Native Python, not Chap — plan §4 records why. The CRPS implementation must be verified against a known-correct reference before it is trusted on real data. |
| Metric | Mean CRPS across regions and splits, from our own verified implementation. Secondary: interval coverage, MAE. |
| Primary comparison | The two-stage ensemble vs. stage 1 alone, on the same splits — the question this project exists to answer (plan §2). |
| Required baselines | Persistence and seasonal climatology, scored through the same pipeline as every model. |
| External reference | None (human-set, 2026-09-20, plan §4b) — the prior project's EWARS-csd score is not cited. |
| Git remote | `github.com/sandvelab/sarimax-boosting-agentic-dengue-laos`, public, already connected. Pushed through batch 10 on 2026-09-21 at the human's instruction, after a lightweight secrets scan (plan §4b); the release batch still runs the full secrets/data-permission scan. |
| Open reproducibility item | Result CSVs are written with Windows line endings but stored by git with Unix endings, so a fresh clone's CSVs hash differently from the working-copy digests in provenance records. To be settled tree-wide before the clean-room check (plan §6 row 17, §4b 2026-09-21). |

## What must not happen

These override everything else here; the plan's §3 states them in full.

1. **The final year (2010) is sealed before any work begins and opened once**, at the final
   validation, across a perturbation manifest frozen beforehand. Nothing is added, dropped,
   re-tuned or re-run on the holdout after a number from it has been seen.
2. **No number reaches a claim except through a file.** Whatever computes CRPS here writes its
   output to a file; every reported figure is read from that file by a script.
3. **Every judgment call — stage 1's specification, stage 2's family and inputs, the
   combination rule, the training window, zero-handling — is a node or a logged decision,
   never silent.**
4. **Agency is recorded on every decision.**
5. **Failures are kept**: a stage-2 family that does not fit, a specification that does not
   converge, an ablation showing no benefit — all stay in the record.
