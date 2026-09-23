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
- **Status**: **batches 1–20 complete and the release pushed** (`v1.0-release`, 2026-09-23, at the
  human's instruction; the release scan's findings are in `AI-generated/batch-reports/26-09-23_b20_release.md`
  §2 and §8). What remains is the human's citable deposit — a GitHub release from the tag with a
  Zenodo DOI, to be cited in the manuscript's §7. The analysis reproduces from a fresh clone byte for byte (`/validate cleanroom`, run
  at batch 19 and again at release), its instruction files have been walked twice by fresh agents
  that had never seen them (`/validate outsider`, batches 19 and 20), and every check in
  `/validate invariants` holds at the release commit.

  **What the analysis found.** Stage 1, a per-province SARIMAX(1,1,1)×(1,0,0,12) on raw counts,
  scores mean CRPS 26.05 on the development backtest (371 cells, 90% coverage 82.7%) and beats
  both required baselines (persistence 28.32, seasonal climatology 26.91). Ten stage-2
  candidates were built under `04_stage2` and all are kept. The five trained on stage 1's
  in-sample one-step residual fail, because that residual is white (`05_residualStructure`);
  the five trained on stage 1's in-window multi-step out-of-sample error, pooled across provinces
  on the standardised scale, all clear plan §2's two bars. **`04_stage2`'s main path is
  `h_levelOnlyBoosting`** — gradient-boosted trees reading only the horizon, the target month and
  the forecast level — annotated in batch 14 by a rule written before the last candidate's result
  was seen: 24.35 (−6.53%), coverage 85.2%. Its margin is sign-stable across all 26 development
  perturbations (−1.06% to −10.41%, median −5.91%) and turns in size on stage 1's specification
  and on the construction of the training errors, not on the stage-2 family's tuning; a
  no-differencing stage 1 alone scores 24.93, within 0.6 CRPS of the two-stage main path. **The
  held-out year was opened once, in batch 17**, across a set of 33 rows frozen in batch 16: the
  ensemble scores 99.20 against stage 1 alone's 128.51 (−22.81%, coverage 61.5% vs 57.3%, all 4
  splits and 75% of cells improved, sign-stable across all 26 frozen perturbations) — **and
  seasonal climatology scores 77.29 on the same cells**, reversing the development ranking, while
  every model's coverage collapses on an epidemic year (22,903 cases against 12,291 in the two
  development test years). The held-out result turns on stage 2's input: the two level-only
  configurations gain about 23%, every full-feature configuration 4% or less. Stage 1 was fixed
  by decision and not repaired (human-set, 2026-09-21, reaffirmed at the freeze); its six
  weaknesses are documented in `05_residualStructure/results/stage1_weaknesses.json`. Five
  alternatives were listed and not run, above all a count or heavier-tailed predictive family at
  stage 1, the one change identified as able to repair coverage. Claims C1–C32 are in the
  collection.

  **How it got here**, one line per batch, each with its report in `AI-generated/batch-reports/`:
  1 orient; 2 data, metric, stage 1; 3 baselines; 4–6 stage-2 candidates a–c on the in-sample
  residual, all losing; 7 `a_linearLags` as least-bad main path, input forks logged; 8 climate
  covariates (d), losing; 9 pooled random forest from `chap-models` (e), wins CRPS, fails
  coverage; 10 literature, the diagnostic node, and candidates f–g on the out-of-sample error,
  both earning their place, `g` promoted; 11–13 the development stability set planned, run and
  reported around `g` (sign stable in 29 of 29); 14 stage 1 fixed and documented, candidates h–j
  built, `h` annotated by the pre-registered rule; 15 the stability set re-run around `h` (26 of
  26); 16 the phase-E set, evaluation design and reporting rule frozen and the machinery gated;
  17 the year opened once; 17b the overview article; 18 the claim collection completed from the
  tree and the hierarchical report's drill-down rebuilt; 19 the clean-room check written and
  passed, the outsider test run, line endings settled; 20 the full manuscript, the release scan,
  the reproducibility report, both checks re-run, and the release assembled.
- **Manuscript**: `Human-AI-collaboration/manuscript/26-09-23_twoStageDengueLaosManuscript.md` —
  the full article, written from all 32 claims, with its provenance sidecar; and
  `26-09-22_twoStageDengueLaos.md`, the 1–2 page overview, beside it. The claim collection holds
  32 claims covering every node (`Human-AI-collaboration/claims/claims.md`); the hierarchical
  report is regenerated by `/hierarchical-report` (103 scored results, 127 pages; gitignored,
  with a tracked `provenance.md` recording each build); the reproducibility report is
  `AI-generated/repro-report/26-09-23_reproducibilityReport.md`, written from an inventory of the
  artefacts. **Target venue: not yet decided**, so the manuscript is venue-neutral.
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
| Held-out data | 2010-01 to 2010-12. **Opened, once, in batch 17 on 2026-09-22** — the opening is recorded in `analysis/06_stability/results/run_status_holdout.csv`. It was sealed from the start of the project until then (plan §3). What is permitted now: reading and reporting the stored results. Nothing may be added, dropped, re-tuned, re-run or promoted on held-out evidence, and a further opening would be a second row in that file and a recorded decision in plan §4b. |
| Backtest scheme | `n_periods 3 / n_splits 8 / stride 3`, reused from the prior project as the default (human-set, 2026-09-20, plan §4b), for comparability between the two projects. |
| Evaluation harness | Native Python, not Chap — plan §4 records why. The CRPS implementation must be verified against a known-correct reference before it is trusted on real data. |
| Metric | Mean CRPS across regions and splits, from our own verified implementation. Secondary: interval coverage, MAE. |
| Primary comparison | The two-stage ensemble vs. stage 1 alone, on the same splits — the question this project exists to answer (plan §2). |
| Required baselines | Persistence and seasonal climatology, scored through the same pipeline as every model. |
| External reference | None (human-set, 2026-09-20, plan §4b) — the prior project's EWARS-csd score is not cited. |
| Git remote | `github.com/sandvelab/sarimax-boosting-agentic-dengue-laos`, public. Pushed through batch 10 on 2026-09-21 after a lightweight scan, and **through batch 20 on 2026-09-23 with the tag `v1.0-release`**, after the full release scan (`AI-generated/validation/2026-09-23_release-scan/`) and at the human's instruction. |
| Line endings, settled | **Settled in batch 19** by `.gitattributes` (`*.csv -text`) plus `git add --renormalize`: git now stores and checks out CSVs exactly as written, so working copy, repository and any clone agree byte for byte. This was not cosmetic — a fresh clone's `holdout.csv` hashed differently from the digest the phase-E freeze recorded, so the holdout runner would have refused to open it and phase E was not reproducible from a clone. Do not "fix" a CSV writer and re-run without re-hashing every provenance record that names its output. |
| Instruction set, settled | **`AGENTS.md` in this folder governs, and nothing outside it** (human-set, 2026-09-23, plan §4b). Batches 1–19 also had the parent vault-collection's `/Users/geirksa_1_2_3/ai/CLAUDE.md` in context, because `.claude/settings.json`'s `claudeMdExcludes` still held the template's literal `<PARENT_DIR>` / `<HOME>` placeholders and matched nothing. That file is cross-vault housekeeping, concerns no part of the analysis and was never acted on, so no stored number is affected; it is recorded because Rule 4 makes the instruction files part of the method. **The real paths belong in `.claude/settings.local.json` (gitignored), never in the tracked `settings.json`**, which is public — absolute paths there would leak a home directory and still not work on any other machine. See `setup-guide.md` §2. |

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
