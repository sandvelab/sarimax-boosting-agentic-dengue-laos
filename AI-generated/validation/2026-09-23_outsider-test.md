# Outsider test — 2026-09-23 (batch 19)

`/validate outsider`: a fresh agent with no conversation history was given the repository and
asked to **follow** its instructions, not to judge them — to read from the stated entry point,
answer six questions about the project from the instructions alone, run the repository's own
verification, trace one reported number from the summary to the raw file and the command, and
state what the project concluded. It was told to change nothing, and changed nothing.

The point of the exercise is the failures. A system asked whether instructions are clear says
yes; a system asked to *follow* them fails visibly at the ambiguous step.

## What it got right without help

The entry point (`CLAUDE.md` → `readme-at-start.md` → `AGENTS.md` → `MOTIVATION.md`) was
unambiguous and stated consistently. It found the main path two independent ways that agreed
(`node.py tree`, and `04_stage2/claim.md`'s `main-path:` field with the single `run.sh` call). It
ran `/validate invariants` from the command in `validate.md`. It traced the headline development
figure — 24.35, −6.53% — from `readme-at-start.md` to claim C31 to
`04_stage2/h_levelOnlyBoosting/results/comparison.json` to the provenance record naming script,
inputs, environment, seed and commit, verified all three recorded digests with `shasum`, and
recomputed the mean from the raw per-cell file to fifteen significant figures. It stated the
project's two-part conclusion correctly from three independent places.

## The twelve findings, and what was done

| # | Finding | Status |
|---|---|---|
| 1 | **`AGENTS.md` §8 named an interpreter that does not exist** — `environment/chapenv/bin/python`, a prior-project path. `readme-at-start.md` and all eleven `run.sh` files were correct; the file declared the single source of truth was the only one wrong. Batch 1 grepped for `chapenv`, fixed the `run.sh` template, and left this occurrence. | **Fixed** — now `environment/env/bin/python`. |
| 2 | **Adding a new alternatives child was a deadlock, and the invariant's own remedy failed.** `combos` fails on a non-main child with no manifest row and says to re-run the planner; the planner refuses because re-planning would change the frozen set; the only unblocked branch is changing the main path, which plan §4b forbids after the holdout is opened. A contributor obeying the error message ends up hand-editing a frozen artefact. | **Fixed** — both messages now name the situation, the recorded-decision route, and the fact that after the holdout opens a new path cannot enter the phase-E set at all. |
| 3 | **`folder-structure.md` described a different repository** — ten absent paths, a Docker image the project does not use, a `$COMBO` convention no node follows, and a closing section stating that node directories are numbered, which is false for alternatives children and enforced against by `/validate invariants`. Its own diagram showed both conventions three lines apart. The outsider reports it nearly created a numbered alternatives child on the strength of that sentence. | **Fixed** — rewritten to this repository, with the lettered/numbered rule stated in full and the node-README exemption noted. |
| 4 | **`Archive/` READMEs and provenance records named nodes and scripts that do not exist** — `analysis/06_external/01_ingest`, `AI-internal/data-acquisition/fetch_*.sh`, and a correction that itself named a non-existent `analysis/01_data/03_siblings`. No archived dataset's provenance record could be re-enacted as written. | **Corrected by appending**, since these files are append-only: each now says the paths belong to the prior project, that the data was reused rather than re-fetched, and where the fetch scripts actually live. |
| 5 | **`.claude/settings.json` still holds literal `<PARENT_DIR>` and `<HOME>` placeholders**, and the safeguard they exist for has failed: the parent directory's `CLAUDE.md` — an unrelated multi-vault instruction telling agents to copy "generalizable insights" between `CLAUDE.md` files — is loaded into every session here alongside this project's instructions. By this repository's own Rule 4, every session has run under an instruction set nobody intended. | **Not changed — raised with the human.** This alters what instructions govern the repository and is not a change to make on an agent's say-so. |
| 6 | **Prior-project batch numbers were cited as this project's own history** in `validate.md`, `track-result.md`, `provenance-record.md` and `check_invariants.py`. `validate.md` credited "batch 18" with an outsider-test finding when this project's batch 18 was claims and report and the outsider test is row 19 — this run. | **Fixed** in the three prose files; the remaining occurrences in `check_invariants.py` comments are labelled where they were already correct and are noted below. |
| 7 | **`readme-at-start.md`'s settings table still said the holdout was "sealed until the final validation"** after it had been opened, and still listed the line-ending item as unsettled. The prose above the table was right; the table is where a reader checks a fact. | **Fixed** — both rows rewritten, including what is and is not permitted now. |
| 8 | **`/validate cleanroom` and `/validate outsider` had no runnable command**, and `useful-scripts/README.md` said "None exist yet beyond the four above". | **Fixed** — `cleanroom.sh` was written this batch and both files now document it; the outsider section now says what to give the fresh agent. |
| 9 | **`/validate invariants` is required "before every commit" but its `git` check fails on any dirty tree**, including the commit you are about to make. | **Fixed** — `validate.md` now says how to read that. |
| 10 | **`validate.md` and `useful-scripts/README.md` under-described the checks**, omitting `combos` and `pool`. | **Fixed** — all eleven named in both. |
| 11 | Smaller: every `run.sh` cited "AGENTS.md §2" for a rule in §8; Rule 3 promised an image the project does not use; three tracked folders lacked a `README.md`. | **Fixed** — template and all eleven `run.sh` files, Rule 3, and the three READMEs. |
| 12 | Batch 19 was running concurrently, so the outsider's first `invariants` run failed on a file that process had not yet committed. No lock or marker tells a second agent a batch is in flight. | **Recorded, not fixed.** Noted for a future batch. |

## What this says about the repository

Eleven of the twelve findings are **stale text inherited from the prior project that this one
did not sweep**, concentrated in `folder-structure.md`, `Archive/*/README.md` and
`provenance.md`, and `.claude/commands/` prose. One (#2) is a genuine regression introduced by
this project in batch 18, when the planner was made to verify rather than rewrite: the guard was
right and its error message left a contributor with no legal move.

The pattern is the one this repository already knows about and had found twice by hand — the
invariant checker's freeze check looking in an empty place (batch 16), and the hierarchical
report's drill-down addressing paths that do not exist (batch 18). The outsider test found seven
more of the same kind in a single pass. **The lesson recorded for row 20: a project that inherits
a repository inherits its prose, and prose does not fail.**

The outsider's own suggestion is worth keeping: a grep pass for `chapenv`, `06_external`,
`data-acquisition`, `$COMBO`, `05_stability` and `batch [23][0-9]` would have found nearly all of
them mechanically.
