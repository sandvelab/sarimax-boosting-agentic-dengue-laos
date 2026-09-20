# Task details

The expanded entry for each task in `ai_task_history.md`: what was produced, the design
decisions, the files affected, and what a future session would need to know. Include
follow-ups, and say plainly where something did not work.

## T1: Reset for a new project, and batch 1 — orient and set up

Full account in `AI-generated/batch-reports/26-09-20_b01_orientAndSetUp.md`; this entry
summarises it.

**Context.** The human asked to start a new, genuinely different project in this repository
(not an extension of the one already here), specified as: a SARIMAX-family model (stage 1)
whose residuals are corrected by a second model of an open family (stage 2), a two-stage
boosting-style ensemble in the general statistical sense — not an ensemble built from
gradient-boosted trees specifically. Since `AGENTS.md` §1/§9 hold this repository to one
project at a time, and the prior project's full record already exists at a separate GitHub
remote, the human confirmed: delete the prior project's own content here rather than
archive-move it.

**What was removed** (git history retains it; the separate remote has the full record too):
`analysis/`, `Human-AI-collaboration/{claims content, manuscript files}`, `AI-generated/`
(all of it), `Archive/case-source-material/`, `Archive/plan-as-delivered/` (the prior plan's
snapshot), the prior project's environment pin (`environment/{environment.yml,Dockerfile,
install-chap.sh,lock.txt}`), `AI-internal/{data-acquisition,reconnaissance,vertical-slice}/`,
the prior plan file, and every `AI-internal/useful-scripts/*.py|*.sh` file not directly
referenced by a generic skill command or `.claude/settings.json` (checked by grep before
deleting — 4 scripts survive: `node.py`, `check_invariants.py`, `claims.py`,
`build_hierarchical_report.py`; everything else, e.g. the clean-room harness and the various
`check_*_defence.py` outsider-critique scripts, was built to defend that specific project's
specific findings and does not generalise).

**What was kept**: `Archive/lao-dataset/`, `Archive/lao-population/`, `Archive/sibling-datasets/`
(raw imports, not that project's output — re-verified by checksum, both pass); `AGENTS.md`,
`CLAUDE.md`, `MOTIVATION.md`, both licences, `folder-structure.md`, `setup-guide.md`,
`.claude/` (all generic method files, unchanged); `AI-internal/skill-references/`.

**What was reset to blank** (folder kept, content cleared, README updated to drop dead
references): `AI-generated/README.md` and its `.gitkeep`; `Human-AI-collaboration/claims/
claims.md` (template only); `Human-AI-collaboration/manuscript/README.md`'s "Currently here";
`Archive/README.md`'s "Currently here"; `Human-input/Plans for AI generation/README.md`'s
"Currently here"; `AI-internal/README.md`'s folder table; `AI-internal/useful-scripts/README.md`'s
script table (4 rows instead of ~20); `AI-internal/ai_task_history.md` and
`ai_task_details.md`; `environment/README.md` and a placeholder `environment/environment.yml`.

**New content written**: the plan
(`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md` — aim, success
criterion centred on the internal stage-1-vs-two-stage comparison rather than an external
platform-comparison exercise, non-negotiables carried over from the prior project's holdout
discipline, decisions already made including *not* routing evaluation through Chap this
time, and a six-phase, fifteen-row batch ledger sketch); `readme-at-start.md`; the top-level
`README.md`; the root `analysis/claim.md` and a childless `analysis/run.sh`;
`Archive/plan-as-delivered/` recreated for this plan (copy, `(IS_SHADOW)`-marked, with
`provenance.md` recording both checksums).

**One methodological change (Rule 4)**: `AI-internal/useful-scripts/node.py`'s
`RUN_HEADER` template hard-coded `environment/chapenv/bin/python`. That is a name specific to
the prior project's Chap-based pinned environment, not a property of the generic node
machinery — found by grepping the whole repository for `chapenv` and finding this one
surviving reference outside deleted files. Changed to `environment/env/bin/python`;
`environment/README.md` updated to state the convention explicitly (build the pinned
environment at `environment/env/`, invoke directly, never activate — matching `.venv`'s own
convention in `AGENTS.md` §8).

**Checks run**: `check_invariants.py` passes except `git` (working tree uncommitted at the
point it was run mid-batch, resolved by this batch's commit); `node.py tree` prints the
single root node; both archived datasets' `sha256sums.txt` verify with `shasum -a 256 -c`.

**Follow-ups / open questions**, raised to the human rather than settled silently: the
backtest scheme (the prior project's was partly shaped by a Chap constraint that does not
apply here); whether the prior project's EWARS score is worth citing at all, given the plan
already makes it optional; and environment scoping, deliberately deferred to batch 2 once
stage 1's actual library needs are known rather than guessed now.
