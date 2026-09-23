# Outsider test at release — 2026-09-23 (batch 20)

The second outsider test (`/validate outsider`, `AGENTS.md` §5), run before the release. A fresh
agent with no conversation history was given the repository and asked to *follow* its
instructions, not judge them: read from the stated entry point, answer nine questions with
checkable answers from the instructions alone, trace the manuscript's held-out headline figure
to its raw file and command, run the invariant checker, and report every point at which it
guessed and every statement false about the repository as it is. It was told to change nothing,
and changed nothing. The working tree held this batch's uncommitted files while it ran, and it
was told so.

**Outcome.** It succeeded at everything the repository is built for: both interpreters found
and existing; the main path established three independent ways, agreeing; what may be done
with the held-out year stated correctly with its sources; the headline traced from the
manuscript sentence through the sidecar to claim C14, to `conclusion.json`, to the provenance
record, to the script and invocation, with twelve recorded digests verified against the current
files and the two means recomputed from the 192 scored rows of the per-cell file to match
99.20 and 128.51. It found fourteen false or stale statements. **Nine are fixed in this batch,
three were in-progress states of the batch itself, two are recorded and left.** The most
consequential finding is the fourth: six provenance records still named the batch-2 lockfile
digest, and the digest check did not look there.

## What was done with each finding

| # | Finding | Disposition |
|---|---|---|
| 1 | `Archive/lao-dataset/README.md` names a node `01_partition` that does not exist (it is `01_prepare`) | Fixed by appending a correction; `Archive/` is read-only |
| 2 | `claims.md` header says "No claims yet" above 32 claims | Fixed |
| 3 | `node.md`'s usage line gives a form `node.py new` rejects (the claim is `--claim`) | Fixed (methodological change, committed as such) |
| 4 | **Six provenance records name the batch-2 `lock.txt` digest with no appended section**; `check_hashes` reads only `script:` blocks, so `validate.md`'s "every digest a record gives is the file's current one" overstated the check | Fixed at the cause and at the check: each record has the section it owed (the lockfile changed at `fa71b3b`, batch 5; the results were reproduced byte for byte under the current lockfile by the clean-room runs), and `check_hashes` now verifies the lockfile digest in the `environment:` block as well (methodological change, committed as such) |
| 5 | `skill-references/README.md` says a skill with a reference says so explicitly; none did | Fixed: `track-result.md` now says to read `provenance-record.md` first |
| 6 | Plan §4's seed row points at `provenance-record.md` for the BLAKE2b construction, which is not there | Fixed: it points at `analysis/scripts/lib/project_seed.py`, where it is |
| 7 | `AI-generated/README.md` listed only `batch-reports/` | Already fixed earlier in this batch |
| 8 | `readme-at-start.md` describes the state at batch 19 while the tree holds batch 20's manuscript | In progress at the time of the test; updated at this batch's close |
| 9 | The manuscript's sidecar cites a batch-20 report and a release-time clean-room folder that did not yet exist | In progress; both exist at this batch's close |
| 10 | `useful-scripts/README.md` (HEAD) said a release scanner was still owed while the scanner existed untracked | In progress; committed in this batch |
| 11 | `check_invariants.py` comment cites `05_stability` and `06_external` "since batch 20" — prior-project nodes | Fixed in the same methodological-change commit as #4 |
| 12 | `.gitignore` named `install-chap.sh` and prior-project batch numbers | Fixed |
| 13 | `MOTIVATION.md` says `AI-generated/` holds the reproducibility report, which did not exist | True as of this batch: `AI-generated/repro-report/` |
| 14 | `04_stage2/claim.md`'s first answers paragraph still reads "`a_linearLags` remains the main path", superseded but unmarked; `readme-at-start.md` similarly names `g_oosErrorBoosting` as main path before naming `h` | Fixed: the node's answers carry a line saying they accumulate by batch and which main path is in force; `readme-at-start.md`'s status rewritten to lead with the current state |
| — | **Recorded, not fixed:** adding a new alternatives child today has no mechanised route to a new development-manifest version when the main path is unchanged — `02_plan_manifest.py` re-plans only when the frozen main path differs from the tree's — so the only exits are a hand edit of a frozen file (forbidden by the same message) or a change to the planner (a methodological change). Batch 19 fixed the messages; the route itself is still not mechanised. | Recorded in plan §4b and the batch-20 report, for the human |
| — | **Recorded, not fixed:** `AGENTS.md` said the mechanics of "the longer" skills live in `skill-references/`; one file lives there | Fixed: the sentence now names what is there |

## The report, as delivered

The agent's report follows verbatim.

---

# Outsider test — 2026-09-23 (working tree dirty; batch-20 release work in progress and being edited concurrently)

Nothing was written, edited, created, deleted or moved. Read-only git commands and the repository's own inspection tools only.

## (i) Files read, in order

1. `CLAUDE.md` (pointer) → 2. `readme-at-start.md` → 3. `AGENTS.md` → 4. `MOTIVATION.md` (the order `CLAUDE.md` gives)
5. `setup-guide.md`, `README.md` (root)
6. `analysis/run.sh`, `analysis/04_stage2/claim.md`, `analysis/04_stage2/run.sh`
7. `analysis/06_stability/results/run_status_holdout.csv`
8. `.claude/commands/node.md`, `validate.md`, `release.md`, `do.md`, `track-result.md`, `perturb.md` (head)
9. `AI-internal/skill-references/README.md`, `provenance-record.md`; `AI-internal/useful-scripts/README.md`; `AI-internal/README.md`
10. `environment/README.md`, `install-env.sh`, `lock.txt`, `environment.yml`; `.claude/settings.json`, `.claude/settings.local.json`
11. Plan `Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md` §3, §4, §4b (batch 17 onward), §5, §6
12. `node.py` help/`tree`/`show analysis/04_stage2` output; `check_invariants.py` run
13. Manuscript `26-09-23_twoStageDengueLaosManuscript.md` (grep for the figure), its `_claims.md` sidecar (header, Abstract, §4.6 rows); `manuscript/README.md`, `manuscript/provenance.md`
14. `claims/claims.md` (header, C1, C14, C16), `claims/README.md`
15. `analysis/claim.md`; `analysis/06_stability/claim.md` (batch-17 answer); `06_stability/run.sh`; `04_stage2/h_levelOnlyBoosting/{claim.md,run.sh}`
16. `06_stability/provenance/run_holdout.md`, `report_holdout.md`; `02_stage1/provenance/sarimax_backtest.md`
17. `06_stability/results/main@h__holdout/{conclusion.json,per_cell_scores.csv}`, `conclusions_holdout.csv`
18. `.gitignore`; READMEs: `Human-AI-collaboration/`, `AI-generated/`, `AI-generated/validation/`, `AI-generated/batch-reports/`, `AI-generated/hierarchical-report/`, `Archive/`, `Archive/lao-dataset/`, `Human-input/`, `Human-input/Plans…/`
19. Code: `node.py` (`create_node`), `check_invariants.py` (`check_hashes`, `check_combos`, `check_freeze`), `06_stability/scripts/02_plan_manifest.py` (verify branch), `07_plan_holdout_manifest.py` (`verify_only`); `AI-generated/validation/2026-09-23_outsider-test.md` (deadlock rows)

## (ii) Answers

**1. Interpreters.** `analysis/` scripts: `environment/env/bin/python` (AGENTS.md §8 line 120; every `run.sh` sets `PYTHON="$REPO_ROOT/environment/env/bin/python"`, e.g. `analysis/run.sh` line 11). Machinery under `AI-internal/useful-scripts/`: `.venv/bin/python` (AGENTS.md §8 line 120; `setup-guide.md` §3 lines 53–58; `useful-scripts/README.md` line 6). Both exist: `.venv/bin/python` → CPython 3.13.7; `environment/env/bin/python` → symlink to a uv CPython 3.13.0. Matches `readme-at-start.md` lines 123–124.

**2. Main path of `analysis/04_stage2`.** (a) `analysis/04_stage2/claim.md` line 8: `main-path: h_levelOnlyBoosting`. (b) `analysis/04_stage2/run.sh` line 15: `bash "h_levelOnlyBoosting/run.sh"` (only child call; line 14 lists the nine not taken). (c) `node.py show analysis/04_stage2`: `kind: alternatives   main-path: h_levelOnlyBoosting`. All three agree. Caveat: `claim.md` lines 16–24 (the first "Answers" paragraph) still say "`a_linearLags` remains the (still-losing) main path by default"; it is superseded by the batch-10 and batch-14 paragraphs below it (lines 167–168, 207) but is not marked as superseded.

**3. Held-out year (2010).** Permitted now: reading and reporting the stored results. Forbidden: adding, dropping, re-tuning, re-running or promoting anything on held-out evidence; a further opening would be a second row in the status file plus a recorded §4b decision. Sources: `readme-at-start.md` line 131 (settings table, "Held-out data") and lines 146–148; plan §3 first bullet; plan §4b "2026-09-22 — batch 17" first row; `06_stability/provenance/run_holdout.md` lines 32–36, 61–63. Opening recorded in `analysis/06_stability/results/run_status_holdout.csv`: one data row, `opening_number` = 1, 2026-09-22 19:59:33, commit `8eda4fd`, 33/33 rows, 622.9 s. Opened once. (Working-tree marker `analysis/06_stability/.holdout_opened` exists, gitignored, as `.gitignore` lines 33–38 say.)

**4. Adding a new stage-2 alternatives child today.** Instructions: AGENTS.md §2 line 41 and `node.md` line 12 say use `/node`, never hand-make directories; naming lettered (`k_shortName`) per AGENTS.md §8 lines 111–117. The tool's real syntax (`node.py new --help`): `node.py new analysis/04_stage2 k_name --claim "…"`. `create_node` (node.py lines 183–208) scaffolds `claim.md`/`scripts`/`results`/`provenance`, does not touch the parent's main path because one is already set, and rebuilds the parent `run.sh` (unchanged for an alternatives node). Then `/validate invariants` `combos` (check_invariants.py lines 471–479) fails: "a path not taken with no row in the stability manifest… If it is [frozen], adding this path is a change to the frozen set: record it in the plan's §4b and plan a new version — never edit manifest.csv by hand, and note that after the holdout is opened a new path cannot enter the phase-E set at all." Re-running `02_plan_manifest.py` refuses with the matching message (lines 270–284). So the legal route is: build and score on development, record in §4b, plan a new development manifest version (the rewrite path in `02_plan_manifest.py` is taken only when the freeze's `main_path` ≠ tree main path, line 251 — so a v3 with the same main path cannot be produced by the script as written), and accept the node can never enter the phase-E set. Dead ends / edits to protected files: (a) no instruction says how to "plan a new version" when the main path is unchanged; the script's rewrite branch is unreachable in that case, so the only ways out are editing `manifest.csv`/`manifest_freeze.json` by hand (forbidden by the same message) or changing the script's condition (a methodological change); (b) `07_plan_holdout_manifest.py verify_only` (lines 363–400) only checks that frozen tier-1 rows still exist in the tree, so a new sibling passes it — consistent with "cannot enter the phase-E set". The batch-19 deadlock fix (outsider-test row 2) improved the messages but the v3 route is still not mechanised. Also `node.md` lines 5–6 give a usage that does not run (`/node new <parent> <name> "<claim>"`; the script needs `--claim`).

**5. Headline figure trace.** Manuscript line 31 / 399 / table line 420–423: "99.20 against stage 1's 128.51 (−22.81%)". Sidecar `_claims.md` line 33 (Abstract) and line 128 (§4.6) → **C14**. `claims.md` line 124–130, C14: grounds `analysis/06_stability/results/distribution_holdout.json · results/main@h__holdout/conclusion.json · results/conclusions_holdout.csv`. `conclusion.json`: `stage1_alone.mean_crps` 128.50904…, `two_stage.mean_crps` 99.19891…, `pct_change_vs_stage1` −22.8078…; `conclusions_holdout.csv` line 2 same values. Provenance: `06_stability/provenance/run_holdout.md` (result `results/$COMBO/conclusion.json`, script `scripts/08_run_holdout.py`, invocation `../../environment/env/bin/python scripts/08_run_holdout.py`) and `report_holdout.md` (09/10/11). Digests verified with `shasum -a 256`, all match the record's current section: `08_run_holdout.py` = 97b5c8ea… (batch-19 appended section; original 2acfd8c5… kept as history), `10_report_holdout.py` = 8997bf12…, `09_collect_holdout.py` = 79f8447e…, `11_characterise_holdout_year.py` = 872a01a2…, `lib/holdout_eval.py` = 2c7d9990…, `lib/stage2_perturb.py` = b5371bb8…, `lib/backtest.py` = bb036170…, `lib/crps.py` = 90f29c83…, `holdout.csv` = 389e4f49…, `development.csv` = 138c568c…, `manifest_holdout.csv` = 835bb52c…, `environment/lock.txt` = 2ed8d10e…. Recomputation from `results/main@h__holdout/per_cell_scores.csv` (204 rows; 192 with a score; the 12 unscored are LA-XN, all splits/horizons, `actual` empty): mean `crps_stage1` = 128.509044, mean `crps` = 99.198915, change −22.807834 %. **Matches 128.51 / 99.20 / −22.81 %.**

**6. Invariant checker**, run as `validate.md` line 24 says (`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`), full output:
```
ok    tree
ok    provenance
ok    hashes
ok    plots
ok    seeds
ok    claims
ok    combos
ok    freeze
FAIL  git  (1)
        .: working tree not clean (9 changed path(s))
ok    crossing
ok    pool

1 invariant failure(s). Fix the cause, not the check.
exit=1
```
(By the end of my session `git status` showed 14 changed paths — files were being edited concurrently.)

**7. Reproduction.** Whole analysis: `analysis/run.sh` (AGENTS.md §2 line 39; MOTIVATION.md line 90; root README line 23). Environment first: `environment/install-env.sh` builds `environment/env/` from `environment/lock.txt` (`readme-at-start.md` line 123; `environment/README.md` lines 12–14; `.gitignore` lines 26–28); `.venv` by `setup-guide.md` §3. Clean-room: `bash AI-internal/useful-scripts/cleanroom.sh` (`validate.md` lines 37–38; `useful-scripts/README.md`). Exists. Release scan: committed `release.md` names no script and `useful-scripts/README.md` (HEAD) says "a release scanner is still owed by ledger row 20"; the working-tree (uncommitted) `release.md` lines 12–14 name `bash AI-internal/useful-scripts/release_scan.sh`, which exists untracked, with output already in `AI-generated/validation/2026-09-23_release-scan/`. Neither was run.

**8. Conclusion (two sentences).** A residual-correction stage trained on stage 1's multi-step out-of-sample error earns its place: on the held-out year it scores mean CRPS 99.20 against stage 1 alone's 128.51 (−22.81 %), with coverage improved and the sign stable across all 26 frozen perturbations. But the whole two-stage model is beaten on that year by the seasonal-climatology baseline (77.29) and every model's coverage collapses, so the correction improves "a first stage that is itself the wrong model for the year it was tested on" (`analysis/claim.md` lines 217–235; `readme-at-start.md` lines 95–101; claims C14, C17).

**9. Path checks.** Root `README.md` (depth 0): all 18 paths exist. `AI-internal/README.md` (depth 1): `reconnaissance/`, `data-acquisition/` missing but the README says "None exist yet" — consistent. `Archive/lao-dataset/README.md` (depth 2): **`analysis/01_data/01_partition` does not exist** (line 26; the node is `01_data/01_prepare`). Also checked `AI-generated/validation/README.md` (depth 2): every named file exists; it omits `2026-09-22_cleanroom-artefacts/follow-up.md`, the empty untracked `2026-09-23_cleanroom-artefacts/` and the untracked `2026-09-23_release-scan/`. Provenance `02_stage1/provenance/sarimax_backtest.md`: all 8 paths exist. `06_stability/provenance/run_holdout.md`: all paths exist except the literal `results/$COMBO/…` (a placeholder for the 33 `*__holdout` directories, which do exist).

## (iii) Where I guessed or was uncertain

- Q7 "release scan": had to choose between the committed instruction (no script; "still owed") and the uncommitted one (`release_scan.sh`). Reported both.
- Q4: whether "plan a new version" is possible with the main path unchanged — inferred from `02_plan_manifest.py` line 251 that it is not; no instruction file says so.
- Q5: `results/$COMBO/…` in `run_holdout.md` — assumed placeholder, not a path.
- `readme-at-start.md` line 111 says 32 claims; `grep -c "^## C"` gives 33 — assumed the extra is the format example `## C1` in the header (it is).
- `AGENTS.md` line 136 says longer skills' mechanics live in `AI-internal/skill-references/`; only `provenance-record.md` exists and no skill file mentions it — assumed `track-result.md`'s inline record format is the operative reference.
- Whether to treat the first "Answers" paragraph of `04_stage2/claim.md` (says `a_linearLags` is main) as stale or as history — read on to later paragraphs to resolve.
- `.gitignore` HEAD version line 43 cites "Batches 18, 25, 27 and 31" — prior-project numbering; the uncommitted diff is already rewriting neighbouring lines, so unclear whether it is being fixed.

## (iv) Statements false about the repository as it is

1. `Archive/lao-dataset/README.md` line 26: "Read the whole file only through `analysis/01_data/01_partition`" — no such node; it is `analysis/01_data/01_prepare`.
2. `Human-AI-collaboration/claims/claims.md` line ~19: "No claims yet — the tree has not produced a result." — 32 claims follow.
3. `.claude/commands/node.md` lines 5–6: usage `/node new <parent> <name> "<claim>"` — `node.py new` requires `--claim` (positional claim errors); lines 17–18 show the correct form.
4. Six provenance records name `environment/lock.txt sha256:1d10c3af…` (the batch-2 lockfile) with no appended section; the current file hashes `2ed8d10e…` since commit `fa71b3b` (batch 5): `02_stage1/provenance/sarimax_backtest.md` line 11, `03_baselines/01_persistence/provenance/persistence_backtest.md`, `03_baselines/02_climatology/provenance/climatology_backtest.md`, `03_baselines/provenance/comparison.md`, `04_stage2/a_linearLags/provenance/compare_to_stage1.md`, `04_stage2/a_linearLags/provenance/stage2_linear_lags.md`. This violates `provenance-record.md` lines 57–60 ("the digest in it has to be the digest of the file that is there"), and `check_hashes` misses it because it only reads `script:` blocks (check_invariants.py lines 335–337) — so `validate.md` line 28's "every digest a record gives is the file's current one" overstates the check.
5. `AI-internal/skill-references/README.md` lines 7–8: "A skill that has a reference says so explicitly" — no file in `.claude/commands/` mentions `skill-references/` or `provenance-record.md`. `AGENTS.md` line 136 ("the mechanics of the longer ones in `AI-internal/skill-references/`") likewise describes one file.
6. Plan §4 line 38 (Project seed row): "by the same BLAKE2b construction … (`AI-internal/skill-references/provenance-record.md` if it needs restating)" — that file contains no BLAKE2b construction.
7. `AI-generated/README.md` line 13 (HEAD): "Currently here: `batch-reports/`" only — `hierarchical-report/` and `validation/` also exist (the uncommitted diff adds them).
8. `readme-at-start.md` line 108: "Manuscript: `26-09-22_twoStageDengueLaos.md`" and line 35 "batches 1–19 complete" — true at HEAD, but the working tree holds a full manuscript `26-09-23_twoStageDengueLaosManuscript.md` and plan §4b already has a "batch 20" entry; `manuscript/provenance.md` (HEAD) has no section for the new manuscript (the uncommitted diff adds one). In-progress, reported as-is.
9. Sidecar `26-09-23_…_claims.md` line 26: "the release-time clean-room run recorded in the batch-20 report" — no batch-20 report exists; `AI-generated/validation/2026-09-23_cleanroom-artefacts/` is empty. In-progress.
10. `AI-internal/useful-scripts/README.md` line 24 (HEAD): "a release scanner is still owed by ledger row 20" — `release_scan.sh` exists (untracked) and has already been run. In-progress.
11. `check_invariants.py` line 443–444 comment: "There are two of them since batch 20 — `05_stability` and `06_external`" — neither node exists here (prior-project prose; outsider-test row 6 says such comments were "labelled", this one is not).
12. `.gitignore` (HEAD) line 27: "rebuilt … by `environment/install-chap.sh`" — script is `install-env.sh` (the uncommitted diff fixes it); line 43 cites batches 25/27/31 this project never had.
13. `MOTIVATION.md` line 64: `AI-generated/` holds "the reproducibility report" — no `AI-generated/repro-report/` exists yet.
14. `04_stage2/claim.md` lines 23–24 "`a_linearLags` remains the … main path" — superseded, unmarked.

## (v) Nearly did wrong because of how something was written

- Nearly typed `/node new analysis/04_stage2 k_x "claim"` from `node.md`'s usage line; the script would have rejected it. Harmless here (I ran only `--help`), but a contributor following the usage line fails at step one.
- Nearly reported "no release-scan script exists" from `release.md` (HEAD) and `useful-scripts/README.md`; the uncommitted files say otherwise. The committed instructions and the working tree currently disagree on Q7.
- Nearly trusted `validate.md`'s "every digest a record gives is the file's current one" as covering the `lock.txt` digests; it does not, and six records are stale in exactly the way `provenance-record.md` warns about.
- Nearly followed `Archive/lao-dataset/README.md` to a node `01_partition` that does not exist.
- The first "Answers" paragraph of `04_stage2/claim.md` reads as the current state; had I stopped there I would have reported `a_linearLags` as main. `node.py show` and `run.sh` settled it.
- `readme-at-start.md` line 49 ("`g_oosErrorBoosting` is `04_stage2`'s main path") is also superseded 22 lines later; a skim would take it as current.
