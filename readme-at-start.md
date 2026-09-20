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
- **Status**: batches 1–7 complete (phases A–C). Stage 1 (per-province SARIMAX,
  mean CRPS 26.05 over 371 cells) beats both required baselines (persistence 28.32,
  seasonal climatology 26.91). Three stage-2 residual-correction families were built and
  scored on the same minimal input (stage-1 lag-12 residual + calendar month) — linear
  (26.26), gradient boosting (27.68), Bayesian ridge (28.07, best-calibrated) — and **all
  three lose to stage 1 alone**; the central comparison (plan §2) currently reads "the
  residual stage does not earn its place under any family tried." `a_linearLags` is
  `04_stage2`'s main path as the least-bad candidate, not an endorsement. Climate covariates
  and population, already present in the development data, are logged as an unexplored
  stage-2 input fork rather than silently skipped. Phase D (stability/perturbation, ledger
  rows 8–10) has not started.
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
| Compute budget for stability work | Not yet set — phase D (plan §6) sets it once stage 1 and stage 2 are running and their per-run cost is known. |
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
| Git remote | `github.com/sandvelab/sarimax-boosting-agentic-dengue-laos`, public, already connected. The release batch runs the secrets/data-permission scan before pushing anything beyond this reset. |

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
