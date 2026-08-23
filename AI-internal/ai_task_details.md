# Task details

The expanded entry for each task in `ai_task_history.md`: what was produced, the design
decisions, the files affected, and what a future session would need to know. Include
follow-ups, and say plainly where something did not work.

## T1: Batch 1 — orient and set up

Executed the first batch of `Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`,
which is deliberately a set-up batch: no analysis, no data, no Chap. Read all five source
documents in `Archive/case-source-material/`, initialised git (branch `main`, no remote),
created `.venv` (CPython 3.13.7, macOS 26.6.2 arm64 — the interpreter for the repository's
own machinery, not the analysis environment), replaced the template text in
`readme-at-start.md` and `README.md`, wrote the root node's analytical aim into
`analysis/claim.md`, and created `AI-generated/batch-reports/` with its README and the
batch-1 report `26-08-23_b01_orientAndSetUp.md`.

The substantive output is the report's §3: ten points where the instructions or the source
material are inconsistent, under-specified, or would mislead someone arriving cold. Two are
worth a future session's attention before they bite. The manuscript's Appendix still
specifies a genomic region-set co-occurrence analysis as its illustrating case, including
the worked claim-tree skeleton — I have assumed the dengue case replaces it, and phase E's
write-up depends on that assumption being right. And the plan's §2 defines "decent" partly
as "within reach of the best already-integrated Chap model" with no threshold attached;
since §10 reserves changes to §2 to the human, I have taken the reading that the reference
model's CRPS is reported beside the candidate's with the per-split spread and no verdict
drawn, and flagged it rather than deciding it.

One finding came from the machinery rather than the reading: `.claude/settings.local.json`
was being silently excluded from git by a user-level ignore file at `~/.config/git/ignore`,
outside the repository and invisible to `git status`. Under Rule 4 that file is method, so
it was force-added; the general point is that `check_invariants.py`'s git check asserts the
working tree is clean but not that everything expected to be tracked actually is, and a
clean-room check on a clone would not catch it either.

**Follow-ups for batch 2** — the five acceptance criteria from `chapOrientation.md` §5, of
which two govern everything downstream: whether `chap eval` takes a local model directory
or only a URL, and whether per-region and per-split CRPS values are recoverable from the
`.nc`. `environment/environment.yml` still carries the template's `python=3.12`, which is a
placeholder rather than a decision and which batch 2 may have to change once `chap-core`'s
requirement is known.

**Extension, same day — settling §2.** Both open questions were resolved in dialogue rather
than by the agent. The reference model is `https://github.com/chap-models/chapkit_ewars_model`,
to be beaten on the development backtest and on the held-out year; statistical significance is
acknowledged in advance as unattainable and the call is to be reported as uncertain; and the
phase-D stability spread is carried forward to the held-out year, so the final validation
reports a distribution rather than a point. The dengue case definitively replaces the genomic
region-set case in the manuscript's Appendix, and `settings.local.json` was untracked as a
personal working preference rather than method.

Three consequences the agent proposed and the human accepted: the holdout perturbation
manifest is frozen before the holdout is opened, and nothing is re-run after a holdout number
has been seen (without this, "a spread on the holdout" degenerates into selection); forks that
change the data or the evaluation re-score every model including the reference, while forks
internal to our candidates move only ours; and the root's computed conclusion is a skill score
against the reference, `1 − CRPS_ours / CRPS_ewars`, rather than raw CRPS, because raw CRPS is
not comparable across the two datasets and a raw dev→holdout gap would confound the agent
inflating its own performance with 2010 being a harder year.

The plan as delivered is archived at `Archive/plan-as-delivered/` (sha256 `f17c3fd6…`), and its
drift from the live plan is now a phase-E deliverable: how much of the original design survived
and who drove each change is evidence about how far an agentic system can be handed a plan and
left to run it. **Already 164 changed lines before any analysis has been run.** The plan's new
§4b logs each decision with its agency — five human-set, three agent-on-human-assessment, two
agent-autonomous.

**Metrics**
- Iterations: 3 exchanges (one `/do` invocation, two rounds of settling)
- Input vs. generated text: ~26,000 words read in / ~8,500 words written out
- Type: machinery

## T2: Batch 2 — reconnaissance: Chap

The batch the plan called its largest unknown, and the install turned out not to be the hard
part. `environment/install-chap.sh` builds a project-local virtual environment on CPython
3.13.0 and installs `chap-core==2.1.0`, resolving 174 packages, all wheels, no compilation,
no Docker and no R. The pin was verified rather than asserted: the environment was deleted
and rebuilt, and the second resolution was identical. The Python patch version is pinned
because `uv venv --python 3.13` silently resolves to whichever 3.13 the machine holds — here
uv's own 3.13.0, while the repository's `.venv` runs 3.13.7. `environment/environment.yml`
and `environment/Dockerfile` were rewritten away from the conda framing they carried as
template text, which had never described anything that had been built. The Docker layer is
written but **unbuilt**: no daemon is running on this machine, and `environment/README.md`
says so rather than implying the third layer of Rule 3 exists.

Two new folders: `AI-internal/reconnaissance/` for scripts that establish facts about
external systems the project depends on but does not control, and
`AI-generated/chap-reconnaissance/` for what they produce, with a `provenance.md` binding
every file to script, pin and commit. Neither is a node in the claim tree — the tree holds
the analysis of dengue in Laos, and "what does `chap eval` compute" is a question about the
instrument. `/validate invariants` covers only `analysis/`, so this is a place the structural
checks do not reach and the `provenance.md` convention of `AGENTS.md` §8 does the work
instead.

**What was established.** `chap eval --model-name` accepts a local directory, so development
happens locally; it also accepts `https://github.com/org/repo@<commit>`, which settles the
plan's §4b conditional about vendoring the reference model. A Chap model is a directory with
an `MLproject` file declaring its target, required covariates, user options, a runtime
(`uv_env` / `renv_env` / `conda_env` / `docker_env`) and two shell commands; the exchange is
CSVs, so the contract is language-agnostic, and `predict` writes one column per forecast
sample. The backtest is expanding-window rolling-origin with the splits laid out backwards
from the last period of the file, so the evaluated span is always
`n_periods + (n_splits−1)·stride` periods ending at the final period — which makes phase E's
preferred route available and retires the script-computed-CRPS fallback batch 3 was told to
prepare. CRPS is the sample-based energy form, unweighted mean over
`(location, time_period, horizon_distance)`; `chap export-metrics` gives the global aggregate
only, but chap-core's own `CRPSMetric.get_metric(..., dimensions=...)` gives any breakdown,
and the split is recoverable as `time_period − (horizon_distance − 1)`. **The project
therefore never implements CRPS**, which is now a standing decision: aggregation level is
ours, the score is always the platform's.

**What a future session needs.** Batch 4 needs Docker running — `chapkit_ewars_model` is a
chapkit REST service whose image is `linux/amd64` only because R-INLA is, so on this arm64
machine it needs a daemon plus emulation, and how slow that is could bind the whole project.
Batch 3 should fix `n_periods = 3`: `chap-core` carries an explicit special case forcing it
for the EWARS model, and the chapkit version defaults to it. Batch 3 should also watch
`validate_and_filter_dataset_for_evaluation`, which silently drops regions whose target is
entirely missing over the training window — on the zero-heavy Lao data that could change what
the headline mean is a mean over. And `/validate cleanroom` must not byte-compare `.nc`
files: repeated identical runs agree on every number but write `split_periods` and
`org_units` from unordered sets, so their order varies. Also unverified: whether
`chap-models-checker`, which claims to run `chap eval` across all 37 repositories in
`github.com/chap-models`, publishes scores — if it does, it answers `chapOrientation.md`
§5's last question cheaply.

The documentation and the artifact disagree on one point, recorded in the report: the
`eval-reference` page describes the `.nc` dimensions as "time, location, quantile, split",
and the file has `sample`, not `quantile`, and no `split` dimension at all.

**Metrics**
- Iterations: 1 `/do` invocation
- Files: 2 scripts written, 17 reconnaissance outputs captured, 1 batch report (~3,400 words)
- Wall clock for the evaluation: 42 s for 4 splits × 5 regions with a trivial model — a floor, not an estimate
- Type: machinery and environment; no analysis output
