Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 1)

# Batch 1 — orient and set up

Deliberately a set-up batch: no analysis, no data acquisition, no modelling.

## 1. What this batch did

**Reset the repository for a new project.** This repository previously carried a completed
project (comparing candidate forecasting models against the WHO EWARS-csd reference on the
Laos dengue dataset), developed to batch 33 and released publicly at
`github.com/sandvelab/veridical-agentic-dengue-laos`. On the human's instruction — the prior
project's full record already exists at that separate remote — its analysis tree
(`analysis/`), claim collection and manuscript (`Human-AI-collaboration/`), all derived
documents (`AI-generated/`), its project-specific machinery
(`AI-internal/data-acquisition/`, `AI-internal/reconnaissance/`, `AI-internal/vertical-slice/`,
and the useful-scripts built to defend that project's specific checks — release, clean-room,
determinism, fork-sweep and outsider-critique scripts), its case-source-material and its
delivered-plan snapshot were removed from this repository (`git rm`, staged and committed).
`AGENTS.md`, `CLAUDE.md`, `MOTIVATION.md`, both licences, `.claude/`, and the four generic
`useful-scripts/` the skills call directly (`node.py`, `check_invariants.py`, `claims.py`,
`build_hierarchical_report.py`) were kept unchanged, since none of them is specific to either
project. **The three archived raw datasets** (`Archive/lao-dataset/`, `Archive/lao-population/`,
`Archive/sibling-datasets/`) were kept: they are imports from outside the project, not the
prior project's own output, and re-acquiring them would be pure overhead.

**One methodological change, Rule 4**: `AI-internal/useful-scripts/node.py`'s generated
`run.sh` template hard-coded `environment/chapenv/bin/python` — a name specific to the prior
project's Chap-based environment, leaked into otherwise-generic machinery. Changed to
`environment/env/bin/python`; `environment/README.md` updated to match.

**Wrote the new plan**,
`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`: the aim (a
two-stage SARIMAX/residual-correction ensemble; §1), what "earning its place" means (§2, the
primary comparison is the two-stage ensemble against stage 1 alone, not a re-run of the prior
project's external reference), non-negotiables carried over from the prior project's own
(the 2010 holdout stays sealed the same way; §3), decisions already made (§4, including
re-using the archived dataset and **not** routing evaluation through Chap this time, since the
question is the architecture, not platform integration), and a batch ledger sketching phases
A–F (§6). Archived to `Archive/plan-as-delivered/26-09-20_sarimaxResidualBoostingCase_asDelivered.md`
before this batch's execution touched it, per the same convention the prior project's plan
used for itself.

**Wrote `readme-at-start.md` and `README.md`** for the new project, replacing the prior
project's text; both explain that a different, completed project previously occupied this
repository and where its record now lives.

**Reset the remaining folder scaffolding** to a blank state: `AI-generated/`,
`Human-AI-collaboration/claims/claims.md`, `Human-AI-collaboration/manuscript/`,
`AI-internal/ai_task_history.md`, `AI-internal/ai_task_details.md`,
`AI-internal/useful-scripts/README.md`, `AI-internal/README.md`, `Archive/README.md`,
`Human-input/Plans for AI generation/README.md`, and `environment/` (README and a placeholder
`environment.yml`; the prior pinned `chap-core` environment, its lockfile, its Dockerfile and
its install script were removed with the rest of the prior project's machinery).

**Verified the reused archived data is intact**: `shasum -a 256 -c sha256sums.txt` passes for
both `Archive/lao-dataset/` (three files) and `Archive/lao-population/` (one file), against the
checksums the prior project recorded when it first archived them.

**Created the repository's own machinery interpreter**, `.venv` (CPython 3.13.7,
`python3 -m venv .venv`, macOS, this session's host), per `setup-guide.md` §3.

**Wrote the root claim-tree node** by hand (`node.py` creates children of an existing node,
not the root itself): `analysis/claim.md` states this project's top-level aim and points at
the plan; `analysis/run.sh` is the generated-shape skeleton with no children yet;
`analysis/scripts/`, `analysis/results/`, `analysis/provenance/` exist, empty.

## 2. Checks run

- `.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all checks pass except
  `git` (working tree not yet committed at the time it was run mid-batch — expected, and
  resolved by this batch's commits).
- `.venv/bin/python AI-internal/useful-scripts/node.py tree`: prints the single root node
  correctly.
- Dataset checksums: both archived datasets verified against their recorded `sha256sums.txt`.

## 3. Open questions for the human

Raised rather than decided silently, per `AGENTS.md` §4 and the plan's own discipline:

1. **Backtest scheme.** The prior project's `n_periods 3 / n_splits 8 / stride 3` was shaped
   partly by a Chap-imposed constraint (EWARS forces `n_periods=3`) that does not bind this
   project, since evaluation is native this time (plan §4). Batch 2 will propose a scheme
   against this project's own cost and data, defaulting to re-using the prior scheme for
   comparability unless there is a concrete reason not to — flagged here rather than decided
   without the human's chance to weigh in, since it affects how directly this project's
   numbers can be set beside the prior one's.
2. **Whether the prior project's EWARS-csd score is worth citing at all.** The plan (§1, §2)
   makes it optional context, not a requirement. If it adds nothing beyond scale, it may be
   simpler to drop the mention entirely and let this project stand on its own comparison
   (two-stage vs. stage-1-alone, vs. baselines).
3. **Environment scoping.** Batch 1 deliberately did not choose or pin the SARIMAX and stage-2
   libraries — that is better decided once batch 2 has looked at what stage 1 actually needs
   (e.g. `statsmodels` vs. `pmdarima` for the SARIMAX fit) rather than guessed now. Flagged as
   deferred, not forgotten.

## 4. Agency

The decision to delete rather than archive-move the prior project's content, and to run this
reset in this repository rather than a new one, was **human-set**, in dialogue before this
batch started. The specific split of what to keep (raw data) versus remove (the prior
project's own analysis and machinery) was **agent-on-human-assessment** — proposed by the
agent from the folder structure and `AGENTS.md`'s own rules, and the human confirmed the
overall approach without reviewing the file-by-file list in advance. The plan's content
(aim, success criterion, non-negotiables, decisions) is **agent-on-human-assessment**: the
architecture (SARIMAX stage 1, open-family residual-correction stage 2) is the human's, given
directly in conversation; everything else in the plan — the internal-comparison framing, the
decision not to route through Chap, the reused holdout discipline — is the agent's proposal,
not yet reviewed sentence by sentence by the human.
