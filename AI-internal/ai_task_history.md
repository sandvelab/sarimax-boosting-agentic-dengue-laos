# Task history

One line per completed task. Written by `/log-tasks`; expanded entries in
`ai_task_details.md`.

This log is **part of the published record** of how the work came about. Write entries a
reader who was not present can follow, and keep them honest about what did not work.

- T1 (2026-09-20): Reset the repository from its prior, completed project (EWARS-comparison
  dengue forecasting, released at `github.com/sandvelab/veridical-agentic-dengue-laos`) to a
  blank scaffold, keeping only the reused archived raw data and the generic framework
  machinery, and ran batch 1 of a new plan — a two-stage SARIMAX/residual-correction ensemble
  for the same dataset. Wrote the new plan, `readme-at-start.md` and `README.md`; verified the
  reused dataset's checksums; created `.venv`; wrote the root `analysis/claim.md`. One
  methodological change under Rule 4: `node.py`'s generated `run.sh` template had a
  project-specific path (`environment/chapenv/`) leaked into generic machinery, fixed to
  `environment/env/`. `/validate invariants` passes except `git` (resolved by this batch's
  commit). Report: `26-09-20_b01_orientAndSetUp.md`. Three open questions raised for the
  human: the backtest scheme, whether to keep citing the prior project's EWARS score, and
  environment scoping (deferred to batch 2). **Same day, in dialogue**: the human settled the
  first two — reuse the prior project's backtest scheme (`3/8/3`) as the default, and drop the
  EWARS citation entirely rather than keep it as context. Recorded in the plan's §4b and
  propagated to §1, §2, §4 and `readme-at-start.md`; pushed to the remote.
- T2 (2026-09-20): Resumed after a machine crash mid-close-out of batch 2, then ran batches
  3–7. Closing batch 2: fixed a relative-path bug in three provenance records (one `../` too
  many, pointing outside `analysis/scripts/lib/`), re-verified every affected sha256 against
  the actual files, filled in `02_stage1`'s deferred commit hash, and wrote its batch report.
  Batch 3 built the required baselines (`03_baselines/`: persistence 28.32, seasonal
  climatology 26.91 mean CRPS) — stage 1 (26.05) beats both. Batch 4 built the stage-2
  residual-correction contract and its first candidate (`04_stage2/a_linearLags`, OLS on
  stage-1's lag-12 residual + calendar month): 26.26, 0.78% worse than stage 1 alone — the
  first honest negative result on the project's central question. Batch 5 added a tree-based
  candidate (`b_gradientBoosting`, pinning `scikit-learn`): 27.68, 6.25% worse. Batch 6 added
  a Bayesian candidate (`c_bayesianRidge`, using its own posterior predictive variance rather
  than borrowing stage 1's): 28.07 CRPS but the best-calibrated of the three (86.8% vs.
  nominal 90% coverage). Batch 7 formalised `a_linearLags` as `04_stage2`'s main path (the
  least-bad candidate, not an endorsement), updated the root `analysis/claim.md` to state
  plainly that no stage-2 family tried beats stage 1 alone, and logged climate covariates and
  population — both already present in the development data, neither yet used by any stage-2
  candidate — as an explicit, unexplored input-space fork rather than a silent default.
  `readme-at-start.md`'s status and environment rows, stale since batch 2, brought current.
  `/validate invariants` passes clean after every batch's close-out commit. Reports:
  `26-09-20_b02_dataAndStage1.md` through `26-09-20_b07_stage2MainPathAndInputForks.md`.
  Nothing pushed to the remote this session.
- T3 (2026-09-20): Ran batch 8, after asking the human to settle the open question batch 7
  left (move to phase D now, or try richer stage-2 inputs first) — the human chose to explore
  inputs. Inserted a new ledger row 8 into the plan (backed up first), renumbering the
  stability phase and everything after it from rows 8–15 to 9–16, and logged the choice in the
  plan's §4b as human-set. Built a fourth stage-2 alternative, `04_stage2/d_linearClimate`:
  `a_linearLags`'s exact OLS family with lag-12 rainfall, mean temperature and mean relative
  humidity added — lag-12 rather than contemporaneous, for the same forecast-time-leakage
  reason `a_linearLags` used lag-12 for the residual, and the same family as `a_linearLags` on
  purpose, to isolate the input question from the model-family question batches 5–6 already
  answered. Result: mean CRPS 26.85, worse than stage 1 alone (26.05, +3.05%) and worse than
  `a_linearLags` on the minimal input (26.26, +2.25%) — the most plausible untried fork named
  in batch 7 did not change the central finding. `a_linearLags` remains `04_stage2`'s main
  path; all four stage-2 candidates built so far lose to stage 1 alone. Updated
  `04_stage2/claim.md` and the root `analysis/claim.md` with the result and what remains
  untried (a non-linear family given climate, a genuinely forward climate signal, population,
  cross-province pooling). Brought `AI-generated/batch-reports/README.md` current — it had
  gone stale after batch 1, never updated for batches 2–7. `/validate invariants` passes
  except `git`, which fails only on the pre-existing, out-of-scope untracked `.idea/`. Report:
  `26-09-20_b08_stage2LinearClimate.md`. Nothing pushed to the remote this session.
- T4 (2026-09-20): Ran batch 9, mid-turn, after the human said to keep exploring stage-2
  candidates and to try an existing model from `github.com/chap-models`. Inspected the org via
  `gh api` (not from memory) and picked `chap-models/rwanda_random_forest` (Python, no new
  environment dependency) over three R-based alternatives, because its pooled-across-locations
  design directly addresses the cross-province-pooling fork `04_stage2/claim.md` logged as
  untried since batch 7. Built `04_stage2/e_pooledRandomForest`: a random forest fit once per
  split on every province's training rows pooled together, on `d_linearClimate`'s exact input
  (the original repo's own feature set, target transform and hyperparameter search were each
  deliberately not reused, and why is logged in the node's provenance). Result: mean CRPS
  25.89 — the first stage-2 candidate to beat stage 1 alone (26.05) — but empirical interval
  coverage collapses to 64.4% against nominal 90%. Wrote a third script,
  `03_diagnose_coverage_collapse.py`, to ground the mechanism in a file rather than a terminal
  observation: 27.5% of corrected forecasts are negative (impossible for a case count),
  concentrated in the lowest-case-count provinces (Pearson r=-0.53 between a province's mean
  case count and its negative-forecast rate). Per plan §2, this candidate does not earn its
  place either — the pooling idea is not ruled out, only this scale-blind implementation of
  it. Verified determinism by running the script twice and diffing outputs byte for byte.
  Inserted ledger row 9 (human-set) into the plan before any modelling, renumbering phase D
  onward from rows 9-16 to 10-17. Report: `26-09-20_b09_stage2PooledRandomForest.md`. Nothing
  pushed to the remote this session.
- T5 (2026-09-20): Ran batch 10, a systematic second iteration on stage 2 at the human's
  request (literature search, residual diagnostics, then candidates). Inserted ledger row 10
  (human-set), renumbering phase D onward from rows 10-17 to 11-18. Two delegated web searches
  (residual-stage hybrids and calibration; dengue predictors in Laos and Southeast Asia) were
  read in full and condensed into the batch report with verification flags. Built
  `analysis/05_residualStructure`: stage 1's in-sample one-step residual — what candidates a-e
  trained on — is essentially white; the h-step out-of-sample error a stage 2 must correct
  carries a level-dependent over-prediction, a calendar bias and a horizon effect, plus
  unpredictable 2008-09 reporting-regime breaks (Bokeo, Salavan, Savannakhet) that make up the
  whole coverage deficit; scaling sigma cannot fix coverage without losing CRPS (oracle factor:
  26.05 -> 35.65); climate anomalies at lags 1-3 carry no signal; a leave-one-split-out,
  permutation-referenced predictability test found 2 of 56 configurations lower CRPS. Built
  `04_stage2/f_oosErrorRidge` (25.63, -1.64%, coverage 84.6%) and `04_stage2/g_oosErrorBoosting`
  (25.16, -3.41%, coverage 85.7%), both trained on the in-window h-step error pooled across
  provinces on the standardised scale — the first candidates to beat stage 1 alone (26.05,
  82.7%) on both of plan §2's criteria. Promoted `g_oosErrorBoosting` to `04_stage2`'s main path
  (own commit, reversible). New shared libraries `lib/residual_features.py` and
  `lib/stage2_oos.py`; `stage1_model.py` untouched. Determinism verified for both scripts that
  draw randomness. Report: `26-09-20_b10_stage2SystematicSecondIteration.md`. Follow-up (2026-09-21,
  human-set): stage 2's horizon set bound to the evaluation scheme's `n_periods` (3 months,
  verified as Chap's evaluate default in chap-core) instead of a constant; scores unchanged.
  Noted the CSV line-ending mismatch (working copy CRLF, repository LF) in the plan for the
  clean-room batch. Pushed main to the public remote (3c90fe0..c8fd3f5) at the human's
  instruction after a lightweight secrets scan; the release batch's full scan still runs.
- T6 (2026-09-21): Ran batch 11, the `/perturb plan` step that opens phase D. Created
  `analysis/06_stability` and moved the invariant checker's manifest paths from the prior
  project's `05_stability` to it (own commit). Measured per-run cost by re-running stage 1 and
  all seven stage-2 candidates: 87 s in total, every output byte-identical to the committed
  one. Enumerated the judgment calls of batches 1-10 as a 40-row manifest — 6 tier-1 siblings
  derived from the tree, 29 tier-2 parametric perturbations (stage 1 spec, window, scheme,
  every main-path stage-2 constant) ranked by informativeness with a basis per row, 5 tier-3
  alternatives not run with reasons (the negative-binomial/truncated predictive family flagged
  as the most consequential absence) — set a provisional one-hour compute budget that excludes
  nothing, and froze the manifest. Split ledger row 11-13 into plan/run/report. Report:
  `26-09-21_b11_stabilityPlan.md`. Nothing pushed.
- T7 (2026-09-21): Batch 12, the `/perturb run` step. Built the perturbable
  two-stage pipeline `analysis/scripts/lib/stage2_perturb.py` (stage 1 spec and window,
  scheme and modelability, and every main-path stage-2 constant as parameters) and the
  stability node's runner `03_run_combinations.py`, which refuses a manifest that no longer
  hashes to its frozen digest, refuses a manifest/runner mismatch, and runs the `main`
  combination first as a gate: it reproduced `g_oosErrorBoosting`'s 408 per-cell rows value
  for value (0 mismatches) before any perturbation ran. The first full run stopped at the
  rolling-refit combination (diverged SARIMAX refits at some origins gave non-finite
  features); fixed by skipping and counting such origins, plus a path bug in the collector,
  and re-run. Six combinations completed before the failure, all keeping the two-stage model
  ahead of stage 1 alone. The re-run completed: all 29 planned rows in 1,937 s of the 3,600 s
  ceiling; every one keeps the two-stage ensemble ahead of stage 1 alone with coverage not
  worse (−0.70% to −10.64%, median −3.32%); the only losing rows are the four early siblings
  trained on the in-sample residual. Provenance, node answers and report
  `26-09-21_b12_stabilityRun.md` written; ledger row 12 done. Nothing pushed.
- T8 (2026-09-21): Ran batch 13, the `/perturb report` step; phase D closes. Wrote
  `06_stability/scripts/05_report_distribution.py`, which reads the collected conclusions and
  every combination's per-cell file and writes `distribution.json`, `perturbation_effects.csv`,
  `province_stability.csv` and `horizon_stability.csv`. Finding: the sign of the central
  comparison is stable (29 of 29 perturbations, coverage never worse, margin −0.70% to
  −10.64%, median −3.32%) and its size is not — insensitive to the stage-2 family's tuning
  and seed (all within two points), larger under a weaker stage 1, smallest under a true
  rolling refit of the training errors (−0.70%); four provinces improve in every combination,
  five in at most 20%; 2–3 months ahead improve always, 1 month ahead in 47%. Four
  better-scoring stage-2 simplifications were not promoted (main path frozen before the run).
  Seven claims (C1–C7) added to the collection via `claims.py`, audit clean. Report:
  `26-09-21_b13_stabilityReport.md`. Nothing pushed.
- T9 (2026-09-21): Ran batch 14 at the human's direction (stage 1 not repaired, weaknesses
  documented; stage 2 explored further; a main path annotated now). Inserted ledger row 14
  (human-set), renumbering rows 14-18 to 16-20 and adding row 15 (stability v2). Wrote
  `05_residualStructure/03_stage1_weaknesses.py` -> `stage1_weaknesses.json` (six weaknesses,
  each with evidence, effect, whether stage 2 can address it, and the stage-1 fork not taken)
  and the matching section in `02_stage1/claim.md`. Built `04_stage2/h_levelOnlyBoosting`
  (24.35, -6.53%, cov 85.2%), `i_boundedBoosting` (24.53, -5.85%, 85.7%) and
  `j_levelOnlyBoundedBoosting` (24.29, -6.78%, 85.2%) as thin nodes on the verified
  parametrised pipeline, each verified 408/408 against stage 1's stored forecast. Promoted
  `h_levelOnlyBoosting` to main path by the rule pre-registered in plan section 4b (tie with j
  within 0.1 CRPS and on splits improved; h simpler). Re-planned the stability manifest around
  h (v2, `@h` rows; v1 rows kept as superseded) and adapted the runner to read the main path
  from the tree. Report: `26-09-21_b14_stage2ThirdIterationAndMainPath.md`. Nothing pushed.
- T10 (2026-09-22): Batch 15 — ran the v2 development stability manifest around
  `h_levelOnlyBoosting` (gate 408/408, 0 mismatches; 26 rows, 1,537 s of 3,600 s) and reported
  its distribution beside v1's: sign stable in all 26 (−10.41% to −1.06%, median −5.91%,
  coverage never worse); size turns on stage 1 and the training-error construction; the
  no-differencing SARIMAX alone (24.93) comes within 0.6 CRPS of the two-stage main path
  (24.35). Runner, collector and reporter write `_v2` files beside v1's and read the main path
  from the freeze; the reporter compares v2 with v1 by file (`version_comparison_v2.csv`, four
  configuration-identical rows reproduce v1 exactly). Claims C8–C13. Report:
  `26-09-22_b15_stabilityRunV2.md`. Nothing pushed.
- T11 (2026-09-22): Batch 16 — froze the phase-E set before the held-out year opens, and built
  and gated the machinery that will run it. `06_stability/results/manifest_holdout.csv` (43
  rows, 33 planned, ~940 s of the 3,600 s ceiling; sha256 `835bb52c…` recorded in
  `holdout_freeze.json` at commit `67f998c`), with the evaluation design (four expanding
  three-month blocks covering 2010 exactly once at h = 1..3, on development's seventeen
  provinces — 204 cells per row) and the reporting rule frozen alongside. New
  `analysis/scripts/lib/holdout_eval.py` reproduces `h_levelOnlyBoosting`'s and both required
  baselines' stored development per-cell scores, 408 rows each, 0 mismatches. Fixed two
  invariants that were not holding: the `freeze` check's leak detection named the prior
  project's results layout, and the frozen *development* manifest was rewritten from
  re-measured wall-clock on every run. Human-set at the freeze: the main path stays `h` and
  stage 1 is not reopened. Report: `26-09-22_b16_holdoutFreeze.md`. Nothing pushed; no dengue
  result changed.
- T12 (2026-09-22): Batch 17 — opened the sealed 2010 holdout, once, and ran the frozen phase-E
  set in full (33 of 33 rows, 623 s; opening 1 recorded in
  `06_stability/results/run_status_holdout.csv`; four preflight refusals passed before a
  held-out byte was parsed; nothing added, dropped, re-tuned, re-run or promoted afterwards).
  **The project's own question is answered yes**: the two-stage ensemble scores mean CRPS 99.20
  against stage 1 alone's 128.51 on the 192 scored cells (−22.81%), coverage 61.5% against
  57.3%, sign-stable across all 26 frozen perturbations. **And seasonal climatology (77.29)
  beats the whole two-stage model there**, reversing the development ranking, on an epidemic
  year for which no configuration in the set is adequately calibrated. The held-out margin turns
  sharply on stage 2's input (level-only ~23%, richer inputs ≤4%). Claims C14–C20. Report:
  `26-09-22_b17_finalValidation.md`. Nothing pushed.
- T13 (2026-09-22): Row 17b — wrote the overview article
  `Human-AI-collaboration/manuscript/26-09-22_twoStageDengueLaos.md` (1–2 pages: design,
  development results, held-out results, what the conclusion turns on, implications,
  limitations), from claims C1–C20, with the provenance sidecar
  `26-09-22_twoStageDengueLaos_claims.md` and a `provenance.md` section beside it.
  `/claims check-text` flagged 12 sentences; ten are method or interpretation mapped in the
  sidecar, two were missing from it and were added, and one factual error was caught and fixed
  (climatology called "the simplest baseline"; persistence is simpler and the ensemble beats
  it). Ledger row 17b added because work outside the batch sequence still needs a row.
- T14 (2026-09-22): Batch 18 — completed the claim collection from the tree and rebuilt the
  hierarchical report's drill-down. Twelve claims added (C21–C32), one or two for each node that
  had none: the metric, the three data nodes, stage 1 (including its six documented weaknesses,
  recorded `human-set`), the baselines, the three residual-structure findings, the reported
  stage-2 configuration and the ten-candidate ranking; 32 claims now, all resolving. The
  report's `_detail_pages` addressed the prior project's `04_score/...` layout, so the root page
  reported "0 combination(s) scored" and Rule 8's link down to raw values was not met; it now
  discovers every directory holding a `per_cell_scores.csv` (103) and gives each the stored
  conclusion, the stored per-split and per-horizon blocks, province and month groupings, and a
  link to the per-cell file. 127 pages, 1.8 MB. Report: `26-09-22_b18_claimsAndReport.md`.
  Nothing pushed; no dengue result changed.
- T15 (2026-09-23): Batch 19 — `/validate cleanroom` and `/validate outsider`. The line-ending
  item turned out not to be cosmetic: a fresh clone's `holdout.csv` hashed differently from the
  frozen digest, so the holdout runner would have refused it and **phase E was not reproducible
  from a clone at all**. Settled with `.gitattributes` (`*.csv -text`) plus
  `git add --renormalize`; re-running the writers was rejected because it would change the
  sealed file's bytes. Wrote `cleanroom.sh`, which this repository lacked, and ran it: 88 min,
  exit 0, 288 of 289 results byte-identical, the one difference being a stopwatch the holdout
  report had embedded in itself — fixed, and 289 of 289 after. The outsider test found twelve
  defects; ten fixed (most seriously `AGENTS.md` naming an interpreter that does not exist, and
  a deadlock making a new alternatives child impossible without hand-editing a frozen artefact),
  one raised with the human (`.claude/settings.json` placeholders; the parent `CLAUDE.md` is in
  every session), one recorded. Report: `26-09-23_b19_cleanroomAndOutsider.md`. Nothing pushed.

- T16 (2026-09-23): Batch 20 opened by settling the one item T15 raised with the human and left
  open: `.claude/settings.json`'s `<PARENT_DIR>` / `<HOME>` placeholders, never substituted, so
  the parent vault-collection's `CLAUDE.md` loaded into every session of batches 1–19 alongside
  `AGENTS.md`. Settled at the human's instruction to work from this folder's `AGENTS.md` only.
  The analysis is unaffected — that file is cross-vault housekeeping, contains nothing about
  modelling, and was never acted on — but Rule 4 makes the instruction files part of the method,
  so the published set would have been short by one file that does not ship with the repository.
  **The obvious fix was the wrong one**: `.claude/settings.json` is tracked and public since
  batch 1, so substituting real paths there would have committed a home directory to a public
  remote and still left every cloner unprotected, since absolute paths do not transfer. Fixed in
  the gitignored `.claude/settings.local.json` instead; `setup-guide.md` §2 corrected to say so.
  Plan §4b records which instructions governed batches 1–19. Committed alone as a methodological
  change (`454698f`). Batch 20's own work — manuscript, repro report, release scan — not started.
- T17 (2026-09-23): Batch 20 — the release, everything but the push. Full manuscript from all 32
  claims (`26-09-23_twoStageDengueLaosManuscript.md`, ~7,200 words, sidecar of 127 rows;
  references re-verified, one corrected); `release_scan.sh` written and run (0 secret-shaped
  strings at HEAD or in 269 commits' added lines; 1 credential-shaped filename in history,
  `.claude/settings.local.json` 1f0a147..15b4ba9, examined: permission grants, no secret; home
  path in 4 tracked files, reported); data permission checked upstream (dhis2 repo has no
  licence file; OpenDengue CC BY 4.0; attribution appended to Archive provenance); clean-room and
  outsider re-run at release — the outsider's 14 findings triaged, 9 fixed, chief among them six
  provenance records naming the batch-2 lockfile digest and a `hashes` check that read only
  `script:` blocks (records appended; check extended, methodological-change commit);
  `repro_inventory.py` and the reproducibility report; hierarchical report build 2; prior-project
  prose swept; readme-at-start's status rewritten to lead with the current state. Release commit
  tagged `v1.0-release`. **Not pushed**: the push and the Zenodo deposit are the human's, with the
  scan's findings in front of them. Ledger row 20 blocked on the push alone.
- T18 (2026-09-23): Pushed the release at the human's instruction — `main` c8fd3f5 → b5fb880 with
  tag `v1.0-release`, 42 commits — after the batch-20 report had put the scan's findings before
  them; ledger row 20 done; plan §4b, readme-at-start and the batch report record the push.
