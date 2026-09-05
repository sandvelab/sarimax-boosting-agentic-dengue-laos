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

## T3: Batch 3 — reconnaissance: the data

Executed the third batch of `Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`.
The first batch to put anything in the claim tree, and the batch that closes the held-out
year off before anything else looks at the data.

**What was produced.** `Archive/lao-dataset/` holds the three Lao files at commit
`af362d5260c6e7de1739f3d05314a844bd272613` of `dhis2/climate-health-data`, fetched by
`AI-internal/data-acquisition/fetch_lao_dataset.sh`, with a checksum manifest the partition
node re-verifies on every run. `analysis/01_data` has two children: `01_partition`, the only
node licensed to read the full file, which writes the development period and
`holdout_2010_SEALED.csv` and verifies the partition; and `02_characterise`, which describes
the development period only and fixes the backtest scheme. Nine provenance records, five
figures with their plotted and pre-aggregation values, a criticality annotation, and the
batch report `26-08-23_b03_dataCharacterisation.md` (~3,900 words). `bash analysis/run.sh`
reproduces all of it from the archive in about fifteen seconds.

**Design decisions worth knowing.** The obvious partition check — concatenate the parts and
hash against the source — fails on this file for a reason that is not a defect: the CSV is
ordered by province and then by month, so a cut on time interleaves rather than splitting
into a prefix and a suffix. Exactness is checked instead as sorted-content equality plus an
order-preserving-subsequence test on each part, on the files as written to disk rather than
on lists held in memory. The partition works on text lines, not through pandas, because a
parser round trip re-formats floats and would make "the parts contain exactly the source" a
claim about a formatter. Data acquisition was kept out of the claim tree, on the same
reasoning batch 2 used for reconnaissance and because a node writing into `Archive/` would
break the read-only rule.

**A defect in the machinery, fixed.** `node.py` generated `run.sh` calling
`../.venv/bin/python`, which resolves to nothing below the first level of the tree and named
the repository's own machinery rather than the pinned analysis environment. It now resolves
the repository root at the node's actual depth and calls `environment/chapenv/bin/python`, so
a node's declared environment and its generated main script agree. Rule 4 makes this a
methodological change and it is committed as one.

**What was established.** The source is a complete rectangular panel, 18 provinces × 156
months, no missing months, no duplicate keys; only `disease_cases` has gaps, 233 of them. The
schema's `row_count: 2575` counts complete records, not rows — a label error rather than a
stale figure, which answers the discrepancy `chapOrientation.md` §4 raised by name. The
schema is also wrong about `rainfall`: declared as a monthly total in millimetres, it is a
mean daily rate — read as declared a province's year comes to 50–78 mm, read as mm/day to
1 518–2 383 mm. Nothing downstream depends on it, but any knowledge-informed prior taken from
the literature would be wrong by a factor of thirty. There is no conversion step for
`chap eval`: the archived CSV is already in the form it reads, and chap-core's own loader
takes both parts losslessly.

The development period is small, zero-heavy and strongly seasonal: 8.1% of target cells
missing, 56.3% of the observed ones zero, a July–September peak at about fourteen times the
February trough, and 77 031 cases in total. Climate leads dengue consistently in sign and
loosely in size — rainfall at lag 1, temperature at 2–3, humidity at 0–1, each positive in 16
or 17 of 17 provinces with a min–max band across provinces of roughly 0.0 to 0.7. The zero
rate falls monotonically from 64% in 1998 to 34% in 2009.

**The finding that matters most.** `validate_and_filter_dataset_for_evaluation` drops
Vientiane province, which reports no dengue count in any of the 144 months. That leaves 17
provinces. But missing observations are dropped before the metric too, and Xaisomboun — which
reports through 2005-12 and then stops, so it survives a filter that looks only at the
training period — contributes zero evaluable cells in the 2008–2009 evaluated span, while
Phongsaly contributes 11 of 24. **The headline mean is over 16 provinces and 371 cells, not
18 and 408**, and six of those sixteen report zero in more than 85% of their observed months.
This is a property of the plan's chosen metric on this dataset, not of any modelling choice,
and it was established before any model exists.

**The backtest scheme, fixed and not to be moved.** Development `n_periods 3`, `n_splits 8`,
`stride 3`, `n_retrain 1`, evaluating 2008-01 to 2009-12 from a training set ending 2007-12.
Phase E `3, 4, 3` on the full file, evaluating exactly 2010-01 to 2010-12 from a training set
ending 2009-12 — confirmed on a synthetic calendar rather than on the archived original,
since a split schedule depends only on the period range. `n_periods = 3` is not a free choice:
it follows from the human's selection of `chapkit_ewars_model`. `stride 3` because
overlapping splits break the balance batch 2's metric identity depends on. `n_splits 8` from
seven costed candidates, as the middle between one evaluated season and a training fit that
ends three years before the last prediction.

**What a future session needs.** Batch 4 still needs Docker running, and now has a concrete
cost question: how long an emulated amd64 R-INLA fit takes at 8 splits. Phase E will need to
know where the holdout's 24 missing target cells fall — deliberately not examined here, since
§3 permits completeness counts and nothing further, so 24 of 216 province-months cannot be
scored. And the zero rate falling across the record means 2008–2009 is the *easiest* stretch
of the development period, so some development-to-holdout drop is predicted by the data
independently of anything the agent does; recording that now is what will make the
distinction credible when phase E reports a gap.

Ten data problems are listed in the report's §8 as phase-D fork candidates, with which are
data-or-evaluation forks that re-score every model including the reference (1, 2, 3, 5, 6)
and which are internal to our candidates (4, 7, 8). That list is what batch 5's perturbation
manifest starts from.

**Metrics**
- Iterations: 1 `/do` invocation
- Files: 9 analysis scripts, 1 fetch script, 37 result files, 9 provenance records, 5 figures, 1 criticality annotation, 1 batch report (~3,900 words)
- Wall clock: `bash analysis/run.sh` ≈ 15 s; run twice, byte-identical including PNGs
- Storage: 1.6 MB in `analysis/`, 8.7 MB in `Archive/lao-dataset/` (8.4 MB of it the GeoJSON)
- Type: analysis output — the first in the project

---

## T4 (2026-08-23) — Batch 4: reconnaissance, methods

**What was produced.** `AI-generated/method-reconnaissance/`, with the reference model's
evaluation on the development dataset and everything derived from it, plus an inventory of
Chap's model library; five new scripts under `AI-internal/reconnaissance/`; and the batch
report `26-08-23_b04_methodSurvey.md` (~4,000 words). Nothing entered the claim tree: the
reference run is reconnaissance, and the reported reference score will be produced from a
node once the tree exists in batch 7.

**The result that unblocks the project.** `chapkit_ewars_model` runs. Mean CRPS **21.891**
over 16 provinces and 371 cells with 1 000 draws per cell, MAE 28.504, 10–90 coverage 0.817,
25–75 coverage 0.617. The 16-province, 371-cell figure was batch 3's prediction from
chap-core's splitter and is now confirmed by a model actually being scored. The calibration
pattern is the most actionable thing in it: nearly nominal in the tails, half again too wide
in the middle, so a candidate that sharpens the core without losing the tails has a route to
a better CRPS that does not require better point forecasts.

**Three findings that were not asked for and matter more than the score.** First, the
reference is unseeded — `scripts/predict.R` calls `inla.posterior.sample` and `rnbinom` and
never `set.seed`, and the chapkit service exposes no seed — so four identical runs gave
21.712–22.166 (sd 0.196). This is the first thing in the project that is not
bit-reproducible and the cause is in the reference, not here. Second, the unpaired
split-level standard error is 5.65 CRPS, 26 % of the mean; that is the right number for how
variable dengue forecasting difficulty is across 2008–2009 and the *wrong* number for how
small a model difference is detectable, because the paired comparison phase C runs cancels
most of it. Both figures are recorded so the crude one is not later quoted as the
comparison's sensitivity. Third, the reference's `train.R` is a placeholder and its INLA fit
happens in `predict.R`, so despite `n_retrain 1` it refits at every split — which makes
"does our candidate refit at predict time" a fork rather than a convention.

**Cost, which revises the budget.** 149 s for an eight-split backtest of the reference under
amd64 emulation; 56 s for a native Python model through `MLproject` + `uv_env`. Evaluation
is cheap and implementation is not, so batch 5 should write the §9 budget in implementation
effort, and phase D's perturbation manifest is far less constrained than the plan assumed.
The 4.7 GB image took about six minutes to pull, once.

**What went wrong.** Two script bugs, both corrected at the source with the pipeline re-run
rather than patched in the output: `get_metric()` returns the metric *class*, not an
instance, and `DataFrame.style` is pandas' Styler, which silently shadowed a column named
`style`. The `chap eval` log emits `Column 'rainfall' ... not used by the model` for all three
climate columns; this is cosmetic — the container's own log shows the training frame arriving
with all nine columns — and is recorded because a reader seeing only the warning would think
the reference had been run without climate data.

**Files affected.** New: `AI-internal/reconnaissance/{run_ewars_reference.sh,
ewars_reproducibility.sh, capture_model_library.sh, measure_native_cost.sh,
score_evaluation.py, reference_spread.py}`, `AI-generated/method-reconnaissance/` (README,
provenance, 30 outputs). Modified: `.gitignore` (three work directories),
`AI-generated/README.md`, `AI-internal/reconnaissance/README.md`, `folder-structure.md`,
`readme-at-start.md` (reference pin, score and unseededness), and the plan — batch 4 marked
`done — produced`, seven decisions appended to §4b with their agency. Commits `fb100a9`
(before) and `e644dfc` (after).

**What a future session needs.** Docker Desktop must be running for anything that touches the
reference, phase E included; starting it is the only manual step in the recipe so far.
Batch 5 should make the paired per-cell comparison an explicit early check rather than a
phase-D discovery, and should read `ewars_plus_template` — newer than the published sweep,
and the closest existing thing to the shortlist's first candidate — before implementing.
Still unexercised: `--model-configuration-yaml` and `user_options` on the `MLproject` route,
and whether the Docker layer of `environment/` builds now that the daemon is up.

**Metrics**
- Iterations: 1 `/do` invocation
- Files: 6 reconnaissance scripts, 33 stored outputs, 1 provenance file with four sections, 1 batch report (~4,000 words)
- Wall clock: reference backtest 149 s; three repeats 8 min; native model 56 s; image pull ~6 min
- Storage: ~11 MB tracked, 10 MB of it the reference's evaluation `.nc` — kept rather than pruned because the reference is unseeded and it cannot be regenerated identically
- Type: reconnaissance — establishes the criterion; not yet a result of the analysis

---

## T5 (2026-08-26) — Batch 5: the bootstrap

**What was asked.** Run the next open batch of
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`. That was batch 5,
whose entire job is to replace the sketched phases C–E with concrete batches now that four
batches of reconnaissance have established the install, the metric, the data, the scheme, the
criterion and the cost of a run.

**What was produced.** A design, not a result. `26-08-26_b05_bootstrapPlan.md` carries: the
full claim tree with every node's claim, kind and main path; the fork inventory with the
subtree each fork belongs to; the per-stage output contract as a schema table; the `COMBO`
mechanism; the two-tier perturbation manifest with its cost estimate and what falls below the
line; a table of what reconnaissance changed in phases C–E and why; and twelve batches with
aims, outputs and costs.

**The three properties the manuscript requires of a tree a stability run can walk were
checked rather than assumed.** A shared output contract per fork — the two forks that could
have failed it, the province fork and the model-family fork, both pass at the level they are
placed, and a fork on the *metric* would have failed, which is one more reason this project
never implements one. A computed conclusion at the root — `conclude.py`, invoked once per
combination by `run.sh` for the main path and by the stability driver for every other. An
enumerated set with a budget — frozen in batch 12 for development and batch 15 for the
holdout.

**Two structural findings.** The plan's §4b rule about which forks re-score which models is
made structural by where a node sits, rather than left as a convention to be applied correctly
each time. And the §4b decision to report a *skill score* rather than a raw CRPS — argued
originally from the development-versus-holdout comparison — turns out to be what makes the
province fork possible at all: raw CRPS is not comparable across children that change the cell
set, a ratio computed within each child is. The design would not work with a raw headline
number.

**What was removed.** The forecast horizon, which the plan's phase-D list names as a fork.
Batch 3 established that `n_periods = 3` follows from the human's choice of reference model,
so a combination at another horizon has no reference to be compared against and the root's
conclusion is uncomputable there. Recorded in §4b as `agent-on-human-assessment`, since it
follows from a human decision rather than from an agent one.

**What was split.** Population, which batch 3's data-problem list carried as one entry. What
the column contains moves every model including the reference; how our model uses it moves
only ours. Conflating them would have put a candidate-internal choice into the subtree that
re-scores the reference.

**Estimates, marked as estimates.** The manifest's cost table is arithmetic on two measured
figures from batch 4 — 149 s for the emulated reference and 56 s for a native model, per
eight-split backtest. Nothing in it is a result, the report says so in two places, and batch
12 replaces it with measured per-combination costs. This is the one place in the batch where
the temptation to present derived numbers as findings existed.

**Files affected.** New: `AI-generated/batch-reports/26-08-26_b05_bootstrapPlan.md`.
Modified: the plan (batch 5 marked `done — expanded`, the ledger extended from 7 rows to 20,
thirteen decisions appended to §4b with their agency, phases B–E revised, §9 budget rewritten
in implementation effort, the report linked), `readme-at-start.md` (status, stability budget,
a pointer to the tree design), `AI-generated/batch-reports/README.md` (batches 4 and 5 added
to *Currently here*, batch 4 having been missed), `analysis/README.md`. Commit `bd33f71`;
no before-commit, because no script was written and the tree was already clean at `f8c1bac`.

**What a future session needs.** Batch 6 builds the vertical slice and must write the
contract files even with one child per fork. Batch 7 additionally builds `02_setup`,
`04_score` and the reference node, computes the first paired per-cell comparison — the answer
decides whether phase C's design holds — settles whether the Docker layer of `environment/`
builds, and makes `AGENTS.md` §8 say that alternatives children are lettered. Read
`ewars_plus_template` before batch 8 implements candidate 1.

**Metrics**
- Iterations: 1 `/do` invocation
- Files: 1 batch report (~4,500 words), 4 files modified
- Wall clock: reading and design only; nothing was executed but `/validate invariants`
- Storage: negligible
- Type: design — `done — expanded`; produces no analysis output by construction

---

## T6 (2026-08-26) — Batch 6: the vertical slice

**What was asked.** Run the next open batch. That was batch 6: one trivial model against
the Chap contract, run through `chap eval` on the development dataset, producing a real
mean CRPS with its per-region and per-split values — the point being that every link in
the chain has been exercised once, not that the score is good.

**What was produced.** `AI-internal/vertical-slice/` holds a Chap-compatible persistence
model (`MLproject` + `uv_env`, four files plus a lockfile), the runner, the metrics
collector and the determinism check. `AI-generated/vertical-slice/` holds the evaluation
`.nc`, the fitted model, the log, six contract files under `results/main/`, the input
hashes, the run cost and the determinism result, with `README.md`, `provenance.md`
(three records) and `criticality.md` beside them.

**The number.** Mean CRPS 24.879 over 371 cells, 16 provinces and 8 splits, with MAE
29.073 and coverage 0.666 (10–90) and 0.491 (25–75). CRPS by lead time 16.4 / 24.8 /
33.4 at one, two and three months; per split 6.6 to 45.4. The run's log carries
`Rejected regions: ['LA-VI']` and Phongsaly contributes 11 cells against every other
province's 24 — batch 3's prediction, arrived at there from chap-core's splitter,
reproduced here by a model of our own being scored.

**The judgment call inside a "trivial" baseline.** The plan defines persistence as a
point forecast and CRPS scores a distribution, so a construction had to be chosen. Two
published ones exist and they disagree: the US COVID-19 Forecast Hub's non-parametric
form (last observation plus the empirical distribution of past h-step changes and their
negations, truncated at zero) and the KIT baseline's parametric form (negative binomial
with a dispersion fitted by MLE and the mean floored at 0.2 to avoid zero variance). The
non-parametric one was taken because 56 % of observed months here are zero, so the
parametric floor would be an arbitrary constant setting the distribution's width in the
majority of cells. Both were read rather than recalled; what was read in full and what
was read only in summary is recorded in `provenance.md`. The choice is now a fork under
the baseline node, added to batch 5's inventory and to the plan's phase-D list.

**Two findings beyond the score.** The model's `uv.lock` in chap-core's run directory is
byte-identical to the tracked one, so the shipped lockfile is what the run used — which
closes, for models of our own, the gap batch 2 identified when it found that pinning
`chap-core` pins the platform and the metric but not the models. And the two models now
scored on this dataset are miscalibrated in opposite directions, which is a more useful
observation for phase C than either coverage figure alone.

**What was deliberately not done, and why it was tempting.** The paired per-cell
comparison against the reference. Both per-cell files exist and the join is seconds of
work, but batch 4's reference figure is explicitly reconnaissance and batch 5 assigned
the comparison to batch 7, where both models are scored from nodes. A comparison
assembled from one number inside the tree and one outside it is not the comparison the
project reports. The temptation is recorded in the report's §7 rather than passed over.

**What went wrong.** One thing, small: the runner's first version located the fitted
model with `find -newermt`, which BSD `find` does not accept. Corrected at the source and
the pipeline re-run; no output file was patched (Rule 2). The run directory is now
cleared before each run so the file copied out is unambiguously the one that run made.

**Files affected.** New: `AI-internal/vertical-slice/` (model directory of six files,
runner, collector, determinism check, README), `AI-generated/vertical-slice/` (18 files),
`AI-generated/batch-reports/26-08-26_b06_verticalSlice.md`. Modified: `.gitignore` (the
77 MB working directory), `AI-generated/README.md`, `AI-internal/README.md`,
`folder-structure.md`, `readme-at-start.md`, and the plan — batch 6 marked
`done — produced`, the report linked, and the new fork added to phase D's list. Commits
`ced3e1a` (before) and `17c0df8` (after).

**What a future session needs.** Batch 7 erects the tree, moves `persistence_model/`
into `analysis/03_models/01_baselines/01_persistence/` with `git mv` so its history
follows, adds seasonal climatology and the reference node, and computes the paired
comparison — the answer to which decides whether phase C's design holds. Also batch 7's:
whether the Docker layer of `environment/` builds. Still unexercised:
`--model-configuration-yaml` and `user_options`, which batch 8's candidate needs; this
model has no configuration and chap-core wrote it an empty
`model_configuration_for_run.yaml`.

**Metrics**
- Iterations: 1 `/do` invocation
- Files: 10 new scripts and model files, 18 stored outputs, 3 provenance records, 1 batch report (~3,000 words)
- Wall clock: 16 s per eight-split backtest, 2.0 s per split; the determinism check runs it twice more
- Storage: 10.2 MB tracked, 9.8 MB of it the evaluation `.nc` — and unlike the reference's, fully regenerable, so it is flagged as the first candidate for pruning
- Type: analysis — the first model of the project's own, though not yet a reported result

## T7 (2026-08-26) — Batch 7: erecting the claim tree

**What was produced.** Twenty nodes under `analysis/`, built with `node.py`, and the chain
that runs them: `02_setup` with four alternatives forks in sequence and an assembly step;
`03_models` with `01_baselines/01_persistence` (moved from the vertical slice with `git mv`),
`01_baselines/02_climatology` (new), and `02_reference` (EWARS-csd, pinned by image digest,
four repeats because it is unseeded); `04_score` with `01_collect`, the `02_aggregate`
weighting fork and `03_compare`; and `analysis/scripts/conclude.py` at the root.
`bash analysis/run.sh` exits 0 and produces every reported figure. Thirteen provenance
records, three `criticality.md` files, answers in every node's `claim.md`, two figures with
their plotted and pre-aggregation values, a clean-room record and a determinism record.

**The design decisions a future session should know.** Each fork got **only its main-path
child**: batch 5's design says "everything" and the plan's batch-7 paragraph says "one child
per fork", and the narrower reading was taken because a sibling that exists but cannot run
would pass `/validate invariants` while advertising an alternative nobody can execute. Each
setup stage finds its input by **searching for the one child of the previous fork that has
results under this combination**, never by naming a child — that is the mechanism batch 5's
file contract needs and does not name, and it is what will let the stability driver swap a
child without any downstream script changing. Every model of ours reaches `chap eval` through
**one shared library**, `03_models/scripts/lib/chap_eval.py`, so the phase-C constraint that no
candidate is compared on a differently computed metric holds structurally. `conclude.py` was
written now, with `candidate_exists: false` and a baseline named in the file as a placeholder,
rather than deferred to phase C — the vertical slice's argument one level up. Climatology got
a fork on its **estimation window** and no fork on how its uncertainty is constructed, because
a set of past Julys is already a distribution while a persistence point forecast is not;
symmetry between the two baselines would have been tidier and would have asserted something
false.

**The finding.** The paired per-cell comparison, which batch 4 left open and batch 5 made this
batch's reason for existing, is two to four times tighter than the unpaired split-level figure
and still cannot separate a 2 CRPS difference. Standard errors: 1.34 and 2.05 per-cell naive,
2.68 and 3.93 clustered by province, 1.92 and 2.99 clustered by split, against differences of
2.24 and 2.78. The noise floor from the reference against its own four repeats is 0.57.
**Phase C must plan against a backtest that resolves about 4 CRPS.** Also: persistence ties the
reference at one month's lead and loses at three, and the reference loses in the two provinces
with the most evaluated cases — so the weighting fork should not be cut from the manifest.

**What went wrong, and what it cost.** An early clean-room attempt mounted the repository
**writable** into the container and wrote symlinks into `environment/chapenv`, breaking the
host analysis environment. Recoverable — the environment is a build artifact — but the repair
revealed a Rule 3 defect that had been in the repository since batch 2: `install-chap.sh`
resolved `chap-core==2.1.0` afresh and *wrote* `lock.txt` from the result, so the lockfile was
a report of one install rather than a specification of the next, and a rebuild three days
later produced `click 8.5.0` where the lockfile said 8.4.2. `environment/Dockerfile` had
always installed from the lockfile, so the two would have drifted apart silently. The
installer now installs from `lock.txt`, re-resolves only under `RESOLVE=1`, and compares the
built environment against the lockfile at the end of every build. The environment was rebuilt
from the pinned 174 packages and verified to reproduce the recorded per-cell scores exactly.
Five smaller corrections in commit `f13dba4`, each found by a run or a check rather than by
review, each fixed at the cause with the affected steps re-executed. The machine was also
heavily loaded by unrelated system processes for part of the batch, which is why the
reference's recorded run costs are an upper bound rather than a measurement.

**Files.** New: `analysis/02_setup/**`, `analysis/03_models/**`, `analysis/04_score/**`,
`analysis/scripts/conclude.py`, `AI-internal/useful-scripts/verify_model_determinism.sh`,
`AI-generated/validation/`, `AI-generated/determinism-checks/`,
`AI-generated/batch-reports/26-08-26_b07_erectTheTree.md`. Modified: `AGENTS.md` §8 (node
naming, now checked), `.claude/commands/node.md`, `AI-internal/useful-scripts/node.py`
(a subdirectory of `scripts/` is not a callable step) and `check_invariants.py` (the naming
check; the script walk no longer descends into built environments),
`environment/install-chap.sh`, `environment/Dockerfile`, `environment/README.md`,
`analysis/README.md`, `.gitignore`, `readme-at-start.md` and the plan. Six commits,
`cf97b81` → `8a32e92`.

**What a future session needs.** Batch 8 implements the hierarchical negative-binomial GLM as
`03_models/03_candidate/a_hierNB` with its four fork nodes, and is the first node that needs
model configuration to reach an `MLproject` model — still unexercised since batch 2. Read
`ewars_plus_template` before implementing. Phase C should report calibration and lead-time
structure beside CRPS, because they separate these three models where the headline mean does
not. Batch 12 should re-measure the reference's run cost on a quiet machine before costing the
manifest, and should not let the weighting fork fall below the budget line. Any candidate that
reads a climate covariate should use `pd.read_csv(..., float_precision="round_trip")` — the
clean-room run showed the macOS and Linux wheels of the same pandas version disagree by one
ULP on some parses.

**Metrics**
- Iterations: 1 `/do` invocation
- Files: 20 nodes, 12 new scripts, 2 model contract directories, 75 stored results, 13 provenance records, 3 criticality files, 1 batch report (~5,000 words)
- Wall clock: ~20 min for `analysis/run.sh`; 28 s per native model, 241–285 s per reference repeat; ~7 min to build the environment image; ~20 min for the clean-room run
- Storage: 56 MB tracked per combination, 38 MB of it the reference's four irreproducible evaluations
- Type: analysis — the project's first results produced from inside the tree

## T8 (2026-08-27) — Batch 8: the candidate contract, and candidate 1

**What was produced.** Ten nodes under `analysis/03_models/03_candidate`: the alternatives
node for the model families, `a_hierNB`, its four configuration forks and the one main-path
child of each. The model itself is `a_hierNB/scripts/hier_nb_model/` — a Chap contract
directory with `MLproject`, a `uv.lock` pinning numpy, pandas and pyyaml on CPython 3.13.0,
`hier_nb.py` (options, features, design, fit) and two thin entry points. Beside it,
`assemble_candidate_config.py` builds the configuration from the forks and
`run_hier_nb.py` sends it through the shared `chap_eval` library, which now carries a model
configuration, hashes it and records its contents. `analysis/scripts/lib/project_seed.py` is
new and is where Rule 6's derivation lives. One new figure at `04_score/03_compare`, seven
provenance records, criticality appended at two nodes, answers in every new `claim.md`.

**The design decisions a future session should know.** Configuration is **assembled from the
forks**, not checked in beside the model: a checked-in file would be a fifth record of the
four forks' decisions and the one that actually ran. The assembler **searches** each fork for
the child with results under this combination rather than naming it, which is the same
mechanism `02_setup` uses and is what lets the stability driver swap a child. The model
**refuses** option values whose sibling has not been built (`hier_nb.IMPLEMENTED`), because a
run that reported a zero-inflated model and fitted a plain one would be wrong in a way
nothing downstream could detect. The seed is read from `readme-at-start.md` rather than
copied, and derived by BLAKE2b rather than `hash`, which is salted per process. **No
autoregressive term** was added, although a three-month lag is available at every horizon and
it is probably what the model is missing: no fork covers it, and adding a structural term
outside the four forks would be the silent judgment call this project exists to prevent — it
is proposed to batch 9 as a fifth fork. **The reference was not re-run**: it is unseeded, so
re-running moves the denominator of every conclusion, and what makes the comparison paired is
that every model saw the same dataset (checked by comparing `dataset_sha256` across the
specs), not that every model ran on the same day.

**The finding, and it is two-sided.** The candidate scores mean CRPS **26.100** — last of the
four models, behind both required baselines — and mean absolute error **27.106**, the best in
the project and ahead of the reference's 28.902. The centre is right and the width is wrong,
and wrong **locally**: Vientiane Capital's 10–90 interval covers 1.000 of outcomes and
Salavan's covers 0.125, and those two provinces carry 2.4 of the 4.0 CRPS gap to the
reference. One province-year variance shared across provinces is a constant multiplicative
width on the log scale, which is too much where the burden is largest and too little where
the epidemic years are sharpest. The aggregate coverage of 0.720 — the best of our models —
sits between two failures and describes neither, which is a caution about the plan's
instruction to report calibration beside CRPS: the headline calibration figure is not on its
own a diagnosis.

**What revises an earlier batch.** Batch 7 measured the development backtest's resolution at
about 4 CRPS using the two baselines. The candidate's paired difference against the reference
is 4.00 CRPS with a **clustered standard error of 1.11**, against persistence's 2.99, because
the two models are structurally alike and fail on the same cells so the paired difference
cancels most of the difficulty. Resolution is a property of the pair, not of the dataset, and
a candidate built to be structurally unlike the reference will be harder to distinguish from
it. This is the first comparison in the project that clears two standard errors and what it
says is that our candidate is worse.

**Follow-ups.** Batch 9 has three things rather than one: build the seven unbuilt siblings,
test whether the width defect is structural (province-scaled year variance) or an artefact of
the Laplace approximation, and decide on the proposed fifth fork. The phase-C stopping rule
was applied as written — it governs *further candidate* batches, and batch 9 is not one — but
the human has been asked whether "the leaderboard's best" meant the best of ours or the best
candidate, because this batch added a model and moved the best of ours by zero. Batch 12
should take the candidate's measured 43 s rather than batch 5's 120 s estimate, and still
needs the reference's cost on a quiet machine.

- Files: `analysis/03_models/03_candidate/**`, `analysis/scripts/lib/project_seed.py`,
  `analysis/03_models/scripts/lib/chap_eval.py`,
  `analysis/04_score/03_compare/scripts/fig_accuracy_and_spread.py`,
  `AI-internal/useful-scripts/{check_invariants,verify_model_determinism}.*`,
  `AI-generated/batch-reports/26-08-27_b08_candidateContract.md`
- Wall clock: ~2 s to fit, 43 s for the eight-split backtest, ~6 min for the three-model
  determinism check
- Storage: 10 MB tracked per combination for the candidate, 9.8 MB of it one NetCDF; 77 MB
  untracked under `work/`
- Type: analysis — the project's first model of its own design

## T9 — Batch 9: candidate 1's forks, swept and promoted (2026-08-27)

**What was produced.** Eleven new leaf nodes and two new forks under
`analysis/03_models/03_candidate/a_hierNB`, so that every child of every fork is built and
has been run; `analysis/scripts/lib/combos.py`, which is the `COMBO_BASE` inheritance
mechanism batch 5's design named and left to batch 12; `AI-internal/useful-scripts/candidate_fork_sweep.py`,
which drives one combination per non-main child through the tree's own scripts and tabulates
what they score; `AI-generated/candidate-forks/` with two rounds of that sweep, the promotion
rule and the round-to-round interaction table; and the batch report
`AI-generated/batch-reports/26-08-27_b09_candidateForks.md`.

**The design decisions a future session needs.** The sweep driver lives outside the tree and
stops at `04_score/02_aggregate` **on purpose**: a `conclusion.json` per sibling is the
phase-D deliverable, and producing nine of them in phase C would report the stability answer
before the manifest that makes it honest has been frozen. Every number the sweep produces is
nevertheless written *into* the tree by the tree's own scripts; only the cross-combination
table is outside it. A sweep is taken around one main path, so each round has its own
labelled directory and `summarise` refuses to rebuild a table whose recorded base
configuration is no longer the tree's — round 1's per-combination results are **not** in the
working tree, having been replaced by round 2, and are at commit `49825b5`.

**What to be careful of.** Promoting a fork invalidates the demoted child's `results/main/`,
and leaving it there would give one fork two children with results under one combination,
which `assemble_candidate_config.py` refuses by design. The three demoted directories were
removed rather than renamed, because a specification file records the combination it was
produced under and a renamed directory would contradict its contents. The three combination
directories named after promoted children were removed for the same reason.

**Follow-ups.**
1. **Whether phase C iterates the promotion rule** is the open question for the human, and
   it is stated in the report's §13 and the plan's §4b. Two children are outside the 0.57
   floor from the promoted path.
2. **Batch 12 must not cut tier 2 of the manifest.** The interaction table is the evidence.
   Batch 12 should also take the measured per-combination costs from
   `a_hierNB/results/*/run_cost.json` (28–36 s, and 108 s for the refit-at-predict child)
   rather than batch 5's 120 s estimate.
3. **The convergence criterion is a genuine loose end.** It was deliberately not relaxed in
   this batch, because adjusting it after seeing a run would be adjusting it to pass. If a
   later batch wants to change it, the change belongs in a commit that says so in
   methodological terms, and the parameters' stability at the cap is recorded in the fitted
   object's EM history.
4. **Salavan is where the remaining gap to the reference lives**, along with Bokeo and
   Attapeu — the provinces whose intervals are far too narrow. Neither a hurdle nor a
   per-province variance touched it. A heavier-tailed observation model is the obvious next
   fork of `01_observation` and does not exist.
5. **Batch 8's question about the phase-C stopping rule is still open** — whether "the
   leaderboard's best" means the best of ours or the best model on the board. It does not
   bind batch 10; it will bind batch 11.

## T10 — Batch 10: candidate 2, gradient-boosted trees with a probabilistic head (2026-08-28)

**What was produced.** Seven new nodes under `analysis/03_models/03_candidate/b_boosted` —
the family node, two forks and their four children; the model contract directory
`b_boosted/scripts/boosted_model/` (`MLproject`, `boosted.py`, `train.py`, `predict.py`,
`pyproject.toml`, `uv.lock`, `README.md`); the node's own configuration assembler, runner
and premise check; `analysis/scripts/lib/palette.py`; three scored combinations under
`family_boosted`, `features_richCalendar` and `head_quantileEnsemble`;
`AI-generated/candidate-forks/boosted_round1/`; and the report
`AI-generated/batch-reports/26-08-28_b10_boostedCandidate.md`.

**The design decisions a future session needs.**

*Candidate 2 is not on the main path, and that is deliberate.* `03_candidate` is an
alternatives node, so a sibling family never runs under `main`. Batch 5's design assigns the
choice of family main path to **batch 11**, after `c_ensemble` exists. So candidate 2 runs
under its own combination `family_boosted`, `analysis/run.sh` still reproduces candidate 1,
and `analysis/results/main/conclusion.json` still reports candidate 1's −0.072. Candidate 2
leads candidate 1 by 2.927 CRPS, five times the resolvable floor, so batch 9's rule would
move the fork on today's evidence; that is written into the batch report §9 and the plan's
§4b so batch 11 cannot decide otherwise without saying why. **Promoting it means:** re-run
`a_hierNB` under a combination of its own, remove its `results/main`, run `b_boosted` under
`main`, re-run `04_score` and `conclude.py`, and `/node promote 03_candidate b_boosted`.

*Two roles for a combination name, and they are not the same.* The sweep driver now takes
`--base` (what a row is **measured against**) and `--inherit-from` (where it takes the
dataset and the other models from). For candidate 1 both are `main`. For candidate 2 the
base is `family_boosted` and the inheritance is `main`, because `family_boosted` holds
candidate 2's two choices but neither the dataset nor the other four models —
`combos.py` resolves exactly one level of base by design, so pointing `COMBO_BASE` at
`family_boosted` would have failed rather than inherited. The driver also runs an untouched
fork's main child when the inheritance base does not hold it, which is what makes candidate
2's sweep work and changes nothing for candidate 1's.

*`03_compare` runs for a swept combination; `conclude.py` does not.* Batch 9's reason for
stopping at `02_aggregate` was that a `conclusion.json` per sibling is the phase-D
deliverable. That still holds. `03_compare` produces the **leaderboard**, which phase C
requires to be script-maintained and never typed, and the paired comparison saying what it
can resolve — and without it the only model of ours that has ever led would never have been
put beside the reference by the node that exists for it.

*The fitted model is JSON that this repository's own code walks.* `boosted.py` writes each
tree as parallel arrays and reads them back with `raw_predict`; scikit-learn is imported
lazily, inside `_booster`, so the module can be imported and the model evaluated without it.
Because that traversal is a second prediction path, `fit_model` evaluates the stored form
against scikit-learn's `predict` on the training rows and **raises** if the largest absolute
difference is not below 1e-6. If a future scikit-learn changes its node layout, that check is
what will say so, loudly, rather than the forecasts quietly changing.

*The boosting hyper-parameters are a logged decision, not forks.* Deliberate, and argued in
four places (node claim, module docstring, model README, provenance record). The round count
**is** chosen from the data, by a time-ordered split — `_rounds` fits on the earlier rows and
scores every round on the latest 15 % — because a stopping rule scored on interleaved rows
chooses a model for a different problem than the backtest poses.

*The premise-and-check pattern is worth reusing.* `02_head/b_quantileEnsemble` computes its
premise and writes a prediction into `model_option_spec.json` **before** anything is fitted;
`scripts/check_head_premise.py` runs after the model and writes the comparison to
`head_premise_check.json`. Seven of eight predicted levels flat at zero, the eighth flat in
the province the prediction was about. About twenty lines of code, and it is the shape of
evidence the manuscript's veridical argument wants. The batch report's §13 recommends it for
phase D.

**What went wrong, and what it implies.** The premise check's first version bounded each
booster over *every possible input* rather than over the file's rows, and reported zero flat
levels where seven are — it answered a different question than the premise asked. A zsh loop
wrote one mangled line into two provenance records, because zsh does not word-split unquoted
parameter expansions; `/validate invariants` caught it. And `boosted.py` changed after the
three evaluations had run, leaving every `model_spec.json` naming a hash no longer on disk,
so all three were re-run — identical, as the determinism check had already implied.

*The determinism check names candidate 2 by its leaf, not by the family node.* Every other
model of ours is named by the node that routes to it, because that node's `run.sh` runs the
main path. `03_candidate` routes *past* candidate 2, so naming it that way would have run
candidate 1 twice under a combination called `determinism_boosted` and reported it identical
— true, and about the wrong model. A green check hiding a wrong model is the same shape as
the defect repaired on 2026-08-27. Worth revisiting whether the model list should discover
the leaves of `03_candidate` once a third family exists.

**The defect worth remembering.** All three comparison figures built their colour and marker
maps by zipping the models present against a four-entry list. `zip` stops at the shorter
argument, so the fifth model would have drawn as **no series at all** in two of the three
figures, with no error — and `/validate invariants` could not have seen it, because the
figure would still exist with its plotted values beside it. It bears directly on `AGENTS.md`
§5: a deterministic check has no attention budget, but it also has no imagination. The fix
keys the palette on the model's **own name**, not its position among the models present, so
that adding a model does not re-colour the others and two figures drawn for two combinations
stay comparable.

## T21 — Batch 21: the greedy branch (2026-08-27)

**Where it lives.** Everything this batch produced is on the git branch **`greedy`**, which
branches from `782be5f` and is **never merged**. On `main` the batch left three things: the
ledger row, a §4b entry in the plan recording what the branch settled, and a line in
`readme-at-start.md`. The batch report is deliberately *not* copied to `main`, because every
file it cites is on the branch.

**What was produced (on the branch).** `AI-generated/candidate-forks/greedy/` — the rule
(`greedy_rule.md`), one record and one log per round, the cross-round trajectory
(`greedy_path.json`), the figure and its two value files, and each round's own sweep in the
format `candidate_fork_sweep.py` writes. `AI-internal/useful-scripts/greedy_iterate.py`
(executes the rule) and `greedy_trajectory.py` (the figure).
`03_models/03_candidate/a_hierNB` moved four of its six forks, and every node from the
candidate down to `analysis/scripts/conclude.py` was re-run under `COMBO=main`.

**The design decisions a future session needs.** The rule is executed by a script and each
round's record is written *before* the tree is touched, so the selection cannot be fitted to
what it selected; the rule itself was committed at `cb61c1d`, before the first round it
decided was run. Round 1 reused batch 9's `round2_promoted` sweep rather than re-running it,
and the driver checks the recorded base-configuration hash against the tree before believing
a reused table. The reference and the baselines were never re-run — nothing the branch moves
changes what they face, and the reference is unseeded — so `04_score` inherits them from what
they scored on the main line, and only `hier_nb` differs. The holdout was not opened.

**What to be careful of.** Two record failures, both real and both kept. (1) The loop ran
unattended, so no commit falls between the rounds: the main-path markers moved twice inside
one commit, and round 2's per-combination results were replaced by round 3 before any commit
held them. What survives is `round_02.json`, `round02/fork_leaderboard.csv` and the sweep
logs; recovering the files means re-running the branch from `cb61c1d`, which is deterministic
and costs about half an hour. Batch 9's hand-run rounds did not have this problem. If the
loop is ever run again, commit per round. (2) The model the branch selected has **no fitted
object** — `fit_time = predict` fits inside chap-core's untracked run directories — so Rule
5 is satisfied only for what that configuration has, and the determinism check's
fitted-object comparison is vacuous for it.

**Follow-ups.**
1. **`verify_model_determinism.sh` needs a decision from the human.** It has reported
   `status: differs` since `models.csv` gained `scored_under_combo`, because the check
   compares that column between two scratch combinations whose names differ by construction.
   `metrics_cell.csv` and `fitted_model.json` match in every case. Batch 9's report and T9
   both cite the file as `identical`, which is what its *contents* support and not what its
   status field says. The honest repairs are to exclude that column from the comparison or to
   drop the file from it and say so; both change main-line machinery and a written report, so
   neither was done.
2. **Batch 12 must not cut tier 2 of the manifest.** Two independent demonstrations now, in
   opposite directions: batch 9's three forks that overstated their combined worth, and this
   branch's fork that was worth nothing until another one moved.
3. **Whether the greedy model joins phase E** is the human's and is not settled. It would
   spend part of the holdout's single opening on a path the project does not report.
4. **The refit is a fair fix and the rest is selection, and nothing separates them.**
   `b_refitAtPredict` corrects a real asymmetry — the reference model refits inside its own
   predict endpoint and ours did not — and it alone was worth 0.873 of the branch's 2.42. A
   later batch that wants to argue the main line is under-powered rather than under-fitted
   should start there, and it would be a fork moved on a structural argument rather than on a
   development score.

### T21, continued — the determinism check, repaired (2026-08-27)

**What was produced.** A repaired `AI-internal/useful-scripts/verify_model_determinism.sh`,
a re-run `AI-generated/determinism-checks/model_determinism.json` reading `identical` for all
three of our models, an addendum in that folder's `provenance.md`, a refreshed `README.md`
there, and a dated correction section appended to
`AI-generated/batch-reports/26-08-27_b09_candidateForks.md`. On `main` at commit `41e27ee`.

**What was wrong, and why it was worth stopping for.** Batch 9 added a `scored_under_combo`
column to `04_score/01_collect/results/<combo>/models.csv`. The check ran its two passes
under scratch combinations named `determinism_<model>_1` and `_2` and compared that file byte
for byte, so from `dec4116` it was comparing a field whose value *is* the pass's own scratch
name: `differs` for every model on every run, whatever the models did. The status word was
the small part. The large part is that **Rule 6's only instrument was reporting failure
unconditionally**, so a model that genuinely lost its seeding would have produced the verdict
the project had already been recording for two batches — the failure `AGENTS.md` §5 exists to
guard against, arriving inside the guard. Demonstrated rather than inferred: two hand-run
passes of the persistence baseline differed in one line of one file, in that field, while the
372-line `metrics_cell.csv` and the fitted object were byte-identical.

**The design decision a future session needs.** The repair removes the *difference*, not the
comparison. Both passes run under one combination name; pass 1's three files are copied to a
`mktemp -d` that a trap removes; pass 2 overwrites the results in place; the copy is compared
with what replaced it. So `scored_under_combo` matches by construction rather than by
exemption, and every byte of all three files is still compared. **Do not turn this into an
exemption list** — that was the rejected alternative, on the grounds that a list of excluded
fields is where a second exclusion gets added later without anyone noticing. The one standing
exclusion remains `eval.nc`, for batch 2's reason.

**What to be careful of.** The check's fitted-object comparison is vacuous for any
configuration with `fit_time = predict`, because that configuration writes a stub — it does
not affect `main`, whose candidate fits in `train`, and it does affect the `greedy` branch,
whose selected model has no fitted object at all. And the check is not free: six backtests,
about eight minutes now that the candidate is in it.

**Follow-ups.**
1. **The `greedy` branch still carries the old script and the old red file**, deliberately:
   its report §9 and §11 describe the state as it was when the branch ran. If the repair is
   propagated there, the branch report needs an annotation saying so, or it will read as
   describing a defect the branch no longer has.
2. **Phase E should re-run this check once more** after the last model change, so the
   published record's Rule 6 evidence is from the final code state rather than from here.
3. **`check_invariants.py` does not look at this file.** Nothing would have caught a check
   that always fails, and nothing would catch it again. Whether the invariants should read
   `model_determinism.json`'s status is a real question for batch 18 — it is the class of
   defect an outsider test is least likely to find, because the file exists and looks
   populated.

---

## T11 — Batch 11: candidate 3, the ensemble, and the close of phase C (2026-08-28)

**What was produced.** Four new nodes under `analysis/03_models/03_candidate/c_ensemble` —
the family node, one fork and its two children; the model contract directory
`c_ensemble/scripts/ensemble_model/` (`MLproject`, `ensemble.py`, `train.py`, `predict.py`,
`pyproject.toml`, `uv.lock`); the node's own `prepare_members.py`,
`assemble_candidate_config.py`, `run_ensemble.py` and `check_pool.py`; three scored
combinations of the pool (`main`, `family_ensemble`, `weighting_crpsWeighted`); candidate 1
re-run under `family_hierNB`; `AI-internal/useful-scripts/family_leaderboard.py`;
`AI-generated/candidate-forks/ensemble_round1/`, `families/` and `family_rule.md`; and the
report `AI-generated/batch-reports/26-08-28_b11_ensembleCandidate.md`.

**The design decision the node rests on.** The pool holds no member code. Each member is run
through **its own Chap entry points**, with the command string read out of the member's own
`MLproject` and chap-core's placeholders substituted, so the pool is a consumer of the
platform's contract rather than a second implementation of four models — one copy of every
member's code, at the node that owns it. The two members that take configuration are
configured by **their own family's fork main-path children and their own family's assembler,
run under the running combination** by `prepare_members.py`; that is what makes a phase-D
perturbation of a member's fork move the pool's member with it, and it is sanctioned by
`AGENTS.md` §2, which has the stability node calling its siblings' main scripts. The price,
paid in `pyproject.toml` and checked pin by pin before anything runs, is that the pool's
environment is the union of its members'.

**What the numbers are.** Mean CRPS **18.817** over the 371 cells against the reference's
22.098 — skill **+0.1485**, the project's first positive conclusion — with a paired difference
of −3.282 at a split-clustered standard error of 1.726 (1.90 se, six of eight splits, ahead of
each of the reference's four repeats individually). The fitted-weights sibling scores 22.838.
Per province the pool is best in the two highest-burden provinces and beaten in three of the
next four, winning 43 % of cells while being 3.282 better on average. By lead time: 14.66 /
18.23 / 23.56 against the reference's 16.54 / 21.97 / 27.79 — it wins the one-month lead,
which neither candidate could, and it gets that from persistence.

**The two findings worth carrying forward are negative.** A prediction registered before the
run — that an equal pool would score worse than its best member — was **wrong** by 1.954 CRPS,
because it reasoned about location and not about width. And fitting the weights to minimise
the pool's own CRPS on a year held back inside the training frame **cost 4.021 CRPS**: the
solve found the true optimum there and concentrated 95 % of the pool on the member that was
best on the validation year and worst on the evaluated one. That is the plan's phase-C warning
measured inside the tree, and it is also the answer to the obvious objection to the headline —
if the pool's win came from an inadvertent look at the evaluated period, the pool that looks
harder would win by more; it loses.

**Calibration is reported beside the score, per the plan's §2.** The pool is the most
over-dispersed model in the project (10–90 0.863 against 0.80; 25–75 0.749 against 0.50). The
zero-atom explanation was measured and rejected: `pool_check.json` records the share of cells
where each model's own quartiles coincide, and the pool is at 0.240 against 0.412–0.547 for
three of its four members. Locally it is wrong in both directions — three provinces at 10–90
coverage 1.000, Attapeu at 0.542.

**The promotion.** `family_rule.md` — batch 9's 0.57 CRPS threshold unchanged, each family
compared at its own main path, plus a calibration veto that did not fire — was written after
`families/family_leaderboard.csv` existed and committed at `4cdfd16`, before the promoted
family ran under `main`. Candidate 1's `results/main/` were removed (not renamed) and it was
re-run under `family_hierNB`, where its per-cell scores are identical. The reference was not
re-run: it is unseeded and would move every denominator in the project.

**What went wrong, kept.** The equal-weight fork child's first version read `04_score`'s
leaderboard for its premise — a model node depending on a scoring node, invisible under `main`
where an earlier leaderboard was on disk, and fatal the moment the determinism check ran it
under a scratch combination. `check_pool.py` made the same mistake one step later. Both now
read only what is upstream of them. `train.py` changed after the three evaluations had run
(the invariant check found it drew through its members and recorded no seed of its own), so
all three combinations were re-run; every figure came back identical. The family leaderboard's
first version compared fork *stage* names against fork *directory* names and found no families
at all.

**For a future session.** Phase C is closed and batch 12 (`/perturb plan`) is next. Three
things it should know. The reported model now refits four models when it runs, so a manifest
entry that moves a `02_setup` fork re-scores all four inside the pool as well as separately —
budget about 11 MB and 90 seconds per combination that includes the pool. `check_pool.json` is
produced by reconstructing the pool from its members' own stored `eval.nc`, so pruning
`family_hierNB` or `family_boosted` evaluations would disable the only independent check on
the reported model, and the check degrades silently by design. And the lift of the three
candidates' near-duplicate configuration assemblers into `03_models/scripts/lib/` is
**scheduled for batches 13–14**, when the frozen manifest re-runs every combination and
regenerating the thirteen provenance records that name those scripts costs nothing extra.
Two candidate ideas were deliberately not built and are in the report §12: a width fork on the
pool (it would be a repair fitted to the calibration number it repairs) and a
candidates-only pool (it would say how much of the win is persistence).

---

## T12 — Batch 12: `/perturb plan`, the perturbation manifest (2026-08-29)

**What was produced.** `analysis/05_stability` — claim, `run.sh`, five scripts, four
provenance records, a `criticality.md`, and ten result files: `forks.csv`, `manifest.csv`,
`manifest_notes.json`, `tier2_rule.md`, `step_costs.json`, `conclusions.csv`,
`conclusions_notes.json`, `run_status.csv` and the driver's log. Nine new scaffolded nodes
under `02_setup`, `04_score/02_aggregate` and `03_models/01_baselines`. A new `combos` check
in `AI-internal/useful-scripts/check_invariants.py`. An addendum to
`analysis/03_models/criticality.md`. The report
`AI-generated/batch-reports/26-08-29_b12_perturbationManifest.md`.

**The decision the batch rests on: the inventory is computed, not listed.** Batch 5 wrote out
ten forks by hand. `lib/inventory.py` walks `analysis/` for alternatives nodes and finds
**seventeen** — five added by phase C while building the candidates, and two baseline forks
that were never on the list although the plan's own phase D names one of them. A list would
have been short again the next time a fork was added; a walk makes a missing fork a missing
node, which a deterministic check can see. The new `combos` invariant closes the loop: the
manifest's tier-1 rows must agree exactly with the tree's non-main children, and every
`results/<name>/` directory must be a combination the manifest names.

**What the tree had not been carrying.** Four `02_setup` forks, the scoring fork and both
baseline forks each had exactly one child. Their claims said the sibling "is not built yet",
which was true and invisible — a fork with one child is a well-formed alternatives node.
`/perturb` says to prefer making a judgment call an alternatives node so the path not taken
survives, so the nine siblings were created with claims and no scripts. The driver's
`--dry-run` prints the ordered step list for each, which is the specification batches 13 and
22 build to.

**A fork's reach is a property of the tree at the moment you run it.** Batch 5 costed the
persistence fork as moving one leaderboard row. Batch 11's promotion made the reported model
a pool that takes both required baselines as members, so how persistence wraps a distribution
around its point forecast is now a choice inside the model this project reports. Nothing
about the fork changed. The plan's phase-D text was corrected rather than left disagreeing
with the tree.

**Costing.** Model terms from nineteen measured `run_cost.json` files; pipeline terms from
`measure_step_costs.py`, which times `02_setup/run.sh`, `04_score/run.sh` and `conclude.py`
by re-running them under `COMBO=main` and verifies with git that they leave the working tree
byte-identical — a step that is not idempotent cannot be timed that way, and the check says
so rather than a comment. `03_models` is deliberately not timed: re-running it re-runs the
unseeded reference and would move the denominator of every comparison for a stopwatch. A fork
inside a member of the pool gets a fourth term, that member's own measured delta, which is
why `fitTime_refitAtPredict` costs 154 s and not 70. Storage is projected the same way, part
by part from the largest measured example on disk: 575 MB for tier 1 on development, 1.15 GB
across both datasets, against 234 MB of stored results today.

**Where phase D's time actually goes**, and it is the batch's most quotable finding: of 124
development minutes, **89 are the reference model** — five setup rows × four unseeded repeats
× an amd64 image under emulation — for the one model the plan forbids perturbing. All
fourteen candidate, family and baseline rows together cost 24 minutes. The dominant cost of
the stability run is holding the denominator still.

**Tier 2's rule, fixed and hashed before tier 1 ran.** Rank tier-1 rows by |Δ skill| from the
main path; take the top two `setup` rows, the top two of the three kinds that move our model,
and the top `scoring` row; every cross-group pair is a tier-2 combination, 2×2 + 2×1 + 2×1 =
8. Batch 5 fixed the count and a phrase whose arithmetic only closes under the cross-group
reading; that reading is fixed here with the count it was chosen to preserve. The rule's
sha256 is in `manifest_notes.json`, so it cannot be edited into a different rule once the
numbers are in. Tier 2 is not cut, because batches 9 and 21 each measured one-at-a-time fork
effects failing to compose.

**What planning found that running would have found later.** Twelve tier-1 rows hold results
produced around a main path that has since moved — `observation_negBinomial` meant "our model
is candidate 1 with a plain negative binomial" in phase C and means "our model is the pool,
whose candidate-1 member has a plain negative binomial" now, same name and different analysis.
Which is which is not guessed: `01_collect` writes a `models.csv` naming every model it
scored, and the planner compares it against what the row would produce, which correctly clears
`family_hierNB` and `weighting_crpsWeighted` and correctly flags `family_boosted`. And two
defects block every built candidate and family row: `prepare_members.ensure_configuration`
runs *every* member fork's main-path child, which gives the assembler two children of a
moved fork and it fails by design; and `conclude.py` resolves our reported model from
`claim.md`'s `main-path` field, which does not move with the combination, so every family row
would write `candidate_exists: false`. Both go to batch 14, alongside the assembler lift
batch 11 deferred there — the batch that re-runs those rows anyway, so regenerating their
provenance costs nothing extra. Fixing them here would have changed hashes named in the
provenance of three combinations' results.

**The driver is written and deliberately not in `run.sh`.** Nine children have no scripts and
twelve built rows are blocked, so calling it from `analysis/run.sh` today would write a dozen
failed combinations into the tree on every run. It joins in batch 15, when every row can run
— recorded in the node's `claim.md`, in a comment in `run.sh` itself, and in the plan's §4b.

**What went wrong, kept.** The cost model was wrong three times before it was right: the main
path's holdout cost came out at 5.6 s because the estimator scaled a development figure that
stood for "already computed" (on the held-out year the main path is a cold start and the most
expensive row there); the member-delta term silently did nothing because it looked for
candidate 1's cost under `family_a_hierNB` when the combination is `family_hierNB`; and the
first stale-directory test flagged rows by kind, wrongly listing a row that had been run
around the pool. All three were caught by reading the produced table against what it should
say, which is an argument for the manifest being a file rather than a paragraph. Separately,
`plan_manifest.py` was extended after its provenance record was written, leaving that record
naming bytes no longer on disk; corrected by an appended section rather than by editing the
line, and the sequence is itself the finding — the third batch running to end this way.

**Compute.** Nothing in the manifest was run. One row, `main`, went through the driver to
exercise it end to end; its `conclusion.json` came back byte-identical. The root
`analysis/run.sh` was **not** run end to end, because it re-runs the unseeded reference and
would move the reported denominator — the same call batch 11 made and for the same reason.

**Commits.** `26dca49` (node, manifest, invariant), `2e186f6` (records, annotations, report,
plan), `5d21182` (the provenance correction).

## T13 — Batch 13: the setup and scoring rows (2026-08-29)

**What ran.** The first batch of phase D that runs anything. Seven of the manifest's
twenty-four tier-1 combinations, and the seven fork children they needed, which the tree had
named in prose since batch 5 and carried as empty nodes since batch 12: `01_population/b_backCast`,
`02_trainingWindow/b_from2004`, `03_provinces/b_reportingOnly`, `03_provinces/c_mergeVientiane`,
`04_retrain/b_everySplit`, and `02_aggregate/b_populationWeighted` and `c_caseWeighted`.

**The five `02_setup` forks do not move the conclusion.** Skill spans +0.1266 to +0.1861 around
the main path's +0.1485, and every gap is smaller than the reference model's own 0.57 CRPS
re-run spread; our pool's raw CRPS spans 18.552 to 19.011 across the five, a range smaller than
the noise on the number it is compared against.

**The one scoring fork moves it four times as much**, from re-weighting a stored per-cell file
and re-running no model: +0.2288 population-weighted and +0.2320 case-weighted, both about
+0.08 of skill from the main path. The cheapest row in the manifest — thirteen seconds against
twenty minutes — is the one the conclusion is most sensitive to.

**The finding worth carrying.** Under case weighting the required persistence baseline beats
the model this project reports, 86.598 against 88.484, and the pool's 10–90 coverage falls from
0.863 to 0.701. It is too wide on the quiet months that dominate the unweighted mean and too
narrow on the outbreak months that dominate this one, and no single weighting shows that. It
does not overturn the headline, which is defined against Chap's own unweighted mean; §2's rule
that a badly calibrated winner has not won is why it is reported beside the score. Case
weighting is not a better summary either: it gives 137 of 371 cells zero weight, shrinks the
Kish effective sample to 65, and puts 62.3 % of the weight in the top decile of cells, because
its weight is a function of the outcome.

**Three of the five setup rows move the reference rather than us.** Removing the two
unevaluable provinces costs the reference 1.052 CRPS and our pool 0.026; merging Vientiane
costs it 0.839 against our 0.189. EWARS pools across provinces while fitting and our pool's
members largely do not, so a setup choice that looks like data hygiene is, for this comparison,
a change to the opponent — invisible in a headline reporting only our own score, and an
argument for the ratio §4b had already fixed.

**The population series.** `Archive/lao-population/` holds the World Bank's annual national
series for Lao PDR (`SP.POP.TOTL`, 1990–2021), fetched by a script, checksummed and
provenanced; the back-cast scales the snapshot by 0.7144 in 1998 to 0.8496 in 2009. From it,
**the archived population column does not have the level its schema claims**: it sums to
4 961 076, where the national total at the schema's stated 2020 reference was 7 346 533 and the
nearest year is 1995 — the third statement in that schema found not to describe the file, after
the row count and the rainfall unit. The anchor is used as declared and the discrepancy
recorded, because under a log offset the anchor is a constant the intercept absorbs. The series
is national, so the fork probes a trend and not a provincial differential; the provincial
censuses that would answer that have no pinnable machine-readable release, and a PDF
transcribed by hand is the manual step Rule 2 exists to keep out.

**Where batch 12 found two defects by planning, this batch found three by running.**
`conclude.py` resolved our reported model by globbing under `results/$COMBO/` only, so on a
combination that re-runs no model of ours it fell through to "best-scoring model of ours" — and
under case weighting that is *persistence*, so `aggregate_caseWeighted/conclusion.json` named a
required baseline as the project's model, internally consistent and wrong. **The reference
model crashes about once in a hundred jobs** (`Prediction script did not create output file`),
so a 36-job setup row failed about a third of the time for reasons that say nothing about the
row; each repeat now gets up to three attempts and `attempts_per_repeat` is recorded, which is
legitimate only because the model is unseeded. **One container was serving all four repeats**,
slowing monotonically — 3.6, 5.6, then 7.5 minutes — until it disconnected; each repeat now gets
its own. And **a failed re-run left a results directory that looked complete**: three repeats
from the new run, one from the old, and the previous run's `model_spec.json` beside them, a
per-cell reference mean spanning two commits with nothing downstream able to detect it. That
one is the most dangerous, because it produces a wrong number no check was looking for; the node
now clears `results/$COMBO/` before writing.

**The cost model predicts the total and not the rows.** 6 041 s planned against 5 901 s actual,
ratio 0.977, with individual rows from 0.577 to 1.851 and all five setup rows costed
identically — the model summed each row's parts as measured under `main` and could not know
that a row changes how much work a part does. The cut order within a kind is therefore ranked
on a constant. Nothing was cut, so nothing rests on it.

**Two decisions about method.** `plan_manifest.py` now refuses to apply the tier-2 rule until
every tier-1 row has been attempted: applied after this batch it would have selected two pairs
instead of eight and recorded a shortfall that is an artefact of the running order. What
changed is *when* a rule about the ranking of tier 1 may read a tier 1, so `tier2_rule.md` and
its sha256 are unchanged. And the weighting fork's three children were put on one shared
implementation, `04_score/scripts/lib/aggregate.py`, with the unweighted case kept as its own
code path inside it — weighting by ones and taking a mean are the same number in arithmetic and
not always the same float; re-run, `results/main/` is byte-identical.

**What went wrong, kept.** A diagnosis of host memory pressure was made under time pressure and
was wrong — the retry disproved it, and the correct reading, an intermittent per-job crash at
about 1 %, only became visible after counting failures across every attempt. `node.py rebuild`
silently re-added the stability driver to `run.sh`, because the generator lists `scripts/`
alphabetically and batch 12 had deliberately kept it out; caught by reading the generated file,
and the block now carries a warning. And the first driver run was killed mid-row by the
session, which is how the mixed reference directory went unnoticed for an hour — `run_status.csv`
is written once at the end of an invocation, so a killed run leaves no record of itself.

**Compute.** 5 901 seconds over seven rows, from 13 s for a scoring row to 2 226 s for
`retrain_everySplit`.

**Commits.** `40b6936` (the seven children, the archived population series, two driver fixes),
`ce0eb34` (a fresh reference container per repeat, and `conclude.py` resolving through
`COMBO_BASE`), `7035515` (the reference node's retry and its results-directory clear),
`6a68f23` (results, provenance records, claim answers, criticality), `bb834e1` (the report, the
cost comparison, the plan's phase D). Rows were produced at `ce0eb34` except the two re-run at
`7035515`, and each record says which.

## T22 — Batch 22: the two baseline forks' children (2026-08-29)

**What was built.** The two children the tree has named in prose since batch 5 and carried as
empty nodes since batch 12. `01_persistence/b_negBinomialFloor` is the parametric construction
of a probabilistic persistence baseline: mean = last observed count floored at 0.2, dispersion
by maximum likelihood from the last five observations, the same distribution at every horizon.
Every constant is the KIT baseline's (`github.com/KITmetricslab/KIT-baseline`, re-read for the
horizon rule), because a stability alternative whose constants the agent chose could be tuned
against the path taken. `02_climatology/b_frozenWindow` estimates the seasonal table once from
the training frame and holds it fixed where the main path re-estimates from the expanding
historic frame.

Both are separate Chap contract directories rather than one directory with a switch: chap-core
copies a contract directory whole into its run directory, so a library outside it does not
travel with the model, and a switch would have re-hashed a model that produced six committed
combinations' results. The cost, paid explicitly, is a duplicated table build in the
climatology pair.

**What the rows found.** They are the extremes of the tier-1 set. `climatology_frozenWindow`
moves the reported skill by 0.0025 and its own baseline by 0.532 CRPS, inside the 0.565 floor,
although the frozen table forecasts two dengue seasons it never saw.
`persistence_negBinomialFloor` moves the reported skill by −0.0279, the largest move of any row
and the first downward one that clears the noise, and its baseline by **4.181 CRPS** — in the
direction the main path did not take. That baseline beats the reference model at −1.400 ±
1.424 (0.98 standard errors, which does not separate them).

**The finding worth carrying.** A better member is a worse pool. With the sharper persistence
member every summary of the pool's inputs improves — best member 20.771 → 20.698, mean of the
members' means 23.421 → 22.376 — and the pool scores 0.617 CRPS worse, its margin over its own
best member falling from 1.954 to 1.264. Its 10–90 coverage falls from 0.863 to 0.817, closer
to nominal on the row where it scores worse. A linear opinion pool's advantage comes from its
members disagreeing, and this is the second independent demonstration of that after batch 11's
weight-fitting result.

**Two defects, both a glob that ignores the tree's forks**, neither reachable until a fork had
two built children. `prepare_members.py` discovered pool membership by globbing for `MLproject`,
so the two new contracts would have made the reported model a six-member pool containing two
persistence baselines and two climatologies — silently, at equal weights, under every
combination including `main`. `01_collect` inherited a missing model from `COMBO_BASE` per node
rather than per fork, so a baseline row would have carried the sibling construction over from
`main` and put both on one leaderboard. Both now resolve the fork by the same `resolve_glob`
lookup `04_score` already used; both leave every existing result byte-identical, verified by
re-running and comparing. With batch 12's two, that is four instances of the same shape.

**What went wrong, kept.** Both rows failed at their first step on the first attempt —
`ModuleNotFoundError`, because the two new runners resolved the shared `chap_eval` library with
`parents[3]` where a fork child needs `parents[2]`; the siblings they were written from sit one
level shallower. And a comment in the parametric model's `train.py` gave the zero share as
52 %, which is zeros over every row including the missing ones rather than over the observed
ones; correcting it changed the script's sha256 after the row had run, so the row was **re-run
at the correcting commit** rather than the record adjusted. Every number came out identical.

**A gap recorded, not closed.** The dispersion the parametric baseline forecast with was
re-estimated inside `predict` at every split and chap-core does not surface a model's stdout,
so those estimates are in no file. Third instance of moving fitting into `predict` costing the
record rather than the score, after batch 4 on the reference and batch 21 on
`04_fitTime/b_refitAtPredict`. Left to batch 14, which touches the shared `chap_eval.py`.

**Compute and storage.** 139 s and 137 s for the two rows against 104.5 s and 117.9 s planned.
Storage, not compute, is now the number to watch: 660.2 MB on disk against the planner's
projection of 584.7 MB for the whole of tier 1 on development and 1 169.4 MB across both
datasets.

**Commits.** `f83acf7` (the children and the two fixes), `d8f93ca` (the import-path repair),
`a5bec23` (results, records, claims, criticality), `5c41aad` (the zero-share correction, plan,
readme, report), `5ec569b` (the re-run at the correcting commit).

## T14 — Batch 14: the candidate and family rows, and tier 2 (2026-08-31)

**What it produced.** The last fourteen tier-1 rows of the frozen perturbation manifest and
all eight tier-2 pairs, so 32 of the manifest's 33 rows have a `conclusion.json` and phase D's
development set is complete. Batch 15 has a distribution to report and a holdout manifest to
freeze; nothing is left open in tier 1.

**The result, and it is a ratio rather than a score.** The model family moves the reported
conclusion 0.2209 of skill; the eleven forks inside the two member families move it by at most
0.0081, spanning 18.638 to 18.933 CRPS against the reference's own 0.57 re-run spread. Three
phase-C batches and a whole counterfactual branch went into choosing among analyses this
evaluation cannot separate. The exception is the pool's own weighting fork at 0.1820 — the one
candidate-internal fork that is not inside a member — which takes the reported model behind the
reference. If the manuscript keeps one number from phase D, the 27:1 ratio is the one.

**Tier 2 justified itself.** The interaction column now in `conclusions.csv` runs −0.1033 to
+0.0424; the extreme is bigger than either main effect behind it, because removing the two
unevaluable provinces and weighting by cases are largely the same re-weighting reached twice
and almost exactly cancel. Batch 12 declined to cut tier 2 on two prior demonstrations that
forks do not compose; this is the third and the first on the reported conclusion.

**Four defects, one class.** Every one is a step that discovers something from the tree,
written when every fork had exactly one child that did anything: the pool's member assembler,
the root's resolution of which model is ours, the comparison node's weighting, and the
stability driver's handling of a fork belonging to the family that runs. Three were named in
advance by batch 12's planning and batch 13's reading; the fourth surfaced two seconds into
the fourteenth row, and the assembler that refused it was the invariant working. I believe
that is now all of them within reach of the manifest, but the class is created by the tree
growing rather than by any one script being careless, so a fifth would not be surprising.

**Files affected.** New: `analysis/03_models/scripts/lib/assemble_config.py`. Changed:
`c_ensemble/scripts/prepare_members.py`, `analysis/scripts/conclude.py`,
`04_score/03_compare/scripts/compare_models.py`, all three
`assemble_candidate_config.py`, `05_stability/scripts/run_manifest.py` and
`collect_conclusions.py`. Removed with git as the witness: the twelve phase-C combination
directories the manifest's rows replace. Provenance sections added at eight nodes; the plan's
§4b, `readme-at-start.md`, `analysis/README.md`, `05_stability/claim.md` and its
`criticality.md` all updated.

**A correction made before it could be read as a result.** A draft sentence said a linear pool
"moves a quarter as far as one member does". The eleven ratios actually run from about zero to
1.7 and one is negative, so it was replaced by two figures read from phase C's committed
sweeps. The negative one is the more useful half: candidate 2's quantile head makes candidate
2 worse and the pool better.

**Two things a future session needs.** First, the per-split diagnostics gap batch 22 left here
is **still open**, and the reason is in the plan's §4b — closing it re-hashes the models and
forces a re-run of the reported analysis, which must not happen between the manifest freezing
and the holdout opening. If it is to be closed, it is a post-holdout batch. Second, tier 2's
two setup slots both landed on children of `03_provinces`, so nothing in the manifest says how
the training window, the population column or the retraining frequency interact with anything.
The rule was hashed before that was knowable and was not adjusted; if the human wants that
coverage it is a new batch, not an edit to `tier2_rule.md`.

**Commits.** `9993d37` (the three fixes and the assembler lift, before the run), `679772c`
(the twelve stale directories removed), `3fb1280` (the tier-1 run and the driver's fourth
fork-blindness), `ba3cf8d` (tier 2 selected by the frozen rule), `c31da5a` (the tier-2 run and
the interaction columns), and the report commit.

## T15 — Batch 15: `/perturb report`, and the close of phase D (2026-08-31)

**What was produced.** Five scripts at `analysis/05_stability`: `report_distribution.py`
(writing `distribution.json`, `distribution_rows.csv` and `sensitivity_by_fork.csv`), three
figure scripts with their plotted values, and `freeze_holdout_manifest.py` (writing
`manifest_holdout.csv` and `holdout_freeze.json`). The node's `run.sh` was rebuilt around
them with `run_manifest.py` in it for the first time. Five provenance records written and two
appended to. Twelve claims added — the first entries in the collection. `check_invariants`'
`combos` check extended to read both manifests.

**The design decision worth carrying forward is the yardstick.** "Does the conclusion move"
needs a scale, and any threshold chosen here would have been a silent judgment call inside
the node whose job is to prevent them. The scale is instead measured from the reference
model's own unseededness: `03_compare` already scores our model against each of the four
repeats, and the spread of those four skill scores — 0.0218 — is how far the reported
conclusion moves when nothing about the analysis changes. It is the skill-space twin of the
0.565 CRPS floor and comes from the same four repeats.

**The second is that CRPS is summarised within a weighting and never across one**, with a
row's weighting read from its own fork columns rather than inferred from the size of the
number. Under case weighting the mean is near 90 rather than near 19; one range over all
thirty-two would have reported an artefact of the unit.

**Why re-planning the manifest was run rather than reasoned about.** `05_stability/run.sh`
re-plans on every run, and the manifest is the frozen artefact whose commit date is the
evidence that the perturbation set was not chosen after the numbers were in. Before the
driver could join that file the question was whether re-planning moves it. It does not:
`manifest.csv` came back byte-identical, same rows, ranks and pairs, and the only field that
changed anywhere was a measurement of disk usage. That is what makes `analysis/run.sh` at
four hours a legitimate reproduction rather than a rewrite of its own inputs.

**Files affected.** `analysis/05_stability/{scripts,results,provenance,claim.md,criticality.md,run.sh}`,
`AI-internal/useful-scripts/check_invariants.py`,
`Human-AI-collaboration/claims/claims.md`, the plan's ledger, §4b and phase D section,
`readme-at-start.md`, and `AI-generated/batch-reports/README.md`.

**Three things a future session needs.** First, **`manifest_holdout.csv` must not be
regenerated after phase E has begun.** It would produce the same rows and destroy the
ordering that makes it evidence — the commit adding it precedes any file under
`analysis/results/*__holdout/`. Batch 16 runs the holdout and does not re-freeze it. Second,
**how `02_setup` reaches the full file does not exist yet** and is batch 16's implementation;
`holdout_freeze.json["left_to_batch_16"]` records that it may not change the rows, the
scheme, the models or the pairing. Third, **`plan_manifest.py`'s `--freeze-check` docstring
is knowingly wrong** and was left standing rather than corrected, because correcting it means
editing the script whose output is the frozen manifest; the finding is in
`provenance/plan_manifest.md` and in the plan's §4b, and a later batch that touches that
script for another reason should fix the docstring then.

**Two open questions put to the human in the report.** Whether `analysis/run.sh` should stay
a four-hour full reproduction or be split so the stability run is invoked separately; and
whether the per-split diagnostics gap — now permanently closed off on the development side,
since closing it would re-run the reported analysis after the freeze — should be closed on
the holdout side before batch 16 runs.

**Commits.** `9ad6578` (the scripts, the rebuilt `run.sh` and the extended invariant, before
the run) and the results-and-records commit after it.

## T16 — Batch 16: the holdout, opened once, on the frozen manifest (2026-08-31)

**What was produced.** The held-out year was opened and the thirty-two analyses frozen in
batch 15 ran against it. `analysis/results/main__holdout/conclusion.json` carries the
project's headline number and `analysis/05_stability/results/holdout_vs_development.json`
carries the answer phase E exists for: the two datasets side by side, paired row by row on a
pairing fixed before the seal came off. Beside it, `holdout_distribution.json`,
`holdout_distribution_rows.csv`, `holdout_sensitivity_by_fork.csv`,
`fork_sensitivity_both.csv`, `holdout_conclusions.csv`, `run_status_holdout.csv`,
`holdout_cost_planned_vs_actual.{csv,json}` and four figures with their plotted values.

**The mechanism, and why it is where it is.** Three things differ on the phase-E side — the
file the setup chain starts from, the backtest scheme, and the span the province and
training-window forks call "evaluated" — and six setup scripts plus `conclude.py` needed all
three. They are answered in one place, the phase functions at the foot of
`analysis/scripts/lib/combos.py`, keyed on the `__holdout` suffix the frozen manifest already
names its rows with. Deriving the dataset from the combination name means the driver sets one
variable, `COMBO`, exactly as for every other row, so there is no second switch to set
inconsistently with it. `01_data/01_partition/scripts/open_holdout.py` opens the seal by
reassembling the archived file from the two parts beside it, in the source's own line order,
verified byte-identical — chosen over pointing `02_setup` at `Archive/` because the archive is
`(IS_SHADOW)` material a setup stage reaching into it would read outside the tree, and because
the proof that the two parts partition the source exactly, which is what makes reassembly
legitimate, lives at that node.

**No node was added.** `analysis/README.md` had reserved `06_holdout` for this batch. The
holdout is the stability question asked of a second year, over the identical set of analyses,
against the identical yardstick, with the frozen manifest and freeze record already at
`05_stability`; a node whose claim restated that one's would make the tree larger and not
clearer. The README now says so where it used to reserve the node.

**Files affected.** New: `01_partition/scripts/open_holdout.py`,
`05_stability/scripts/{pair_holdout_development,fig_holdout_vs_development,fig_fork_sensitivity_both,holdout_fig_skill_distribution,holdout_fig_fork_sensitivity}.py`,
`05_stability/scripts/lib/stability_figures.py`. Changed: `combos.py`, `conclude.py`,
`assemble_setup.py`, six setup fork scripts, `run_manifest.py`, `collect_conclusions.py`,
`report_distribution.py`, `compare_planned_cost.py`, `freeze_holdout_manifest.py`, both
`run.sh` files that gained steps. Records: four new provenance records, phase-E sections
appended to seven at `05_stability` and thirteen at the candidate nodes the holdout rows
reach, a criticality section, and the root and stability `claim.md` answers.

**Three defects kept in the record.** The driver had no reason to skip a row that had already
run, so its first pass over the whole manifest began re-running `main__holdout`; since the
reference is unseeded that would have replaced the denominator of every reported number with a
different draw. Stopped at the persistence baseline, files restored from the previous commit,
the reference never reached, and the guard added — plan §3's second half turned from an
instruction into code. `freeze_holdout_manifest.py` wrote HEAD into `frozen_at_commit`, so
every run overwrote the evidence the field carries; it now reads the commit that adds the
manifest from git. And `fig_fork_sensitivity.py` had "Six of seventeen" in a title string
rather than counting its bars.

**For a future session.** `analysis/run.sh` is now about six hours and has never been run end
to end from cold; `/validate cleanroom` in batch 18 is where that gets a number, and it is the
largest untested claim in the repository. Nothing may be re-run or re-tuned now that holdout
numbers have been seen, which closes the per-split diagnostics gap permanently on both sides.
Two questions stand for the human: whether `analysis/run.sh` should be split so the stability
and phase-E runs are invoked separately, and whether the case write-up's judgment about where
this setup was more trouble than it was worth should be theirs rather than the agent's.

**Commits.** `895a9f8` (the switch, the opened seal and the main holdout row, before the rest
of the set), `609e1be` (the once-only guard) and `48edaea` (the results and records).

## T17 — batch 17: the claim collection completed, and the report that descends to the values

**What was produced.** Eighteen claims, C22–C39, appended through `claims.py add` — the
phase-A, -B and -C half of the collection, which batches 15 and 16 had not written because
their own work was the perturbation set and the held-out year. And
`AI-generated/hierarchical-report/`, built for the first time from a substantially extended
`AI-internal/useful-scripts/build_hierarchical_report.py`. Nothing under `analysis/` changed,
which is the constraint every batch after the holdout opening works under.

**What the report is.** Four levels below the tree, one directory per scored combination:
the conclusion as `conclusion.json` states it; the national mean from `metrics_summary.csv`,
also cut by split and by horizon; the province means from `crps_by_location.csv`; and each
province month by month from `metrics_cell.csv`, with the observed count, the split and
horizon, each model's CRPS, and whether the outcome fell inside its 10–90 interval. 65
combinations, 1 040 province pages, 69 node pages, 1 175 in all. The node pages gained a
"Claims resting on this node" section fed from the collection, so descending the tree reaches
the statement and the values it rests on in one place. Which child of the weighting fork a
combination was aggregated under is **discovered** — the one child of `04_score/02_aggregate`
with results under that combination — never named, which is the rule the tree itself follows.

**Three design decisions a future session should not undo.** The report **displays and never
computes**: every figure comes from the file that holds it, because a report that re-derived
its own means could disagree with the analysis and look right doing it. It is built for
**every** scored combination, not only `main`, because the project's finding is that the
reported analysis is one member of a distribution and a report that let a reader descend only
that member would contradict it structurally. And what it lists is decided by **git** —
`ls-files --others --ignored --exclude-standard --directory` — not by a skip list, so what is
not part of the method cannot appear in it.

**Two defects found by building.** `c_ensemble`'s "Scripts" section was 6 117 files of a
`uv`-built virtual environment against 11 of the node's own; that is what the git filter fixes,
and it took the first build from 21 MB to 18. And the build crashed sorting a province whose
mean CRPS is empty — Xaisomboun contributes no evaluable cell, so an empty mean is correct
and a zero would be a score; blanks now sort last and print as an em dash.

**One rule that changed what several claims say.** A claim states the figures a file holds and
never a ratio between two of them that no file computes. `readme-at-start.md` reports the pool
as 1.90 standard errors from the reference; the paired difference and its standard error are
stored and the ratio is not, so C23 gives both stored figures instead. C29 and C31 were shaped
the same way. The alternative — a two-line step at `04_score/03_compare` that divides and
stores — is a change to the analysis, and phase E forbids re-running anything, so it is the
human's call and is flagged in the batch report.

**Files affected.** `Human-AI-collaboration/claims/claims.md` (C22–C39);
`AI-internal/useful-scripts/build_hierarchical_report.py`; `.gitignore` (the report's contents
ignored rather than its directory, so the build record can be tracked);
`AI-generated/hierarchical-report/provenance.md` (the only versioned file in that folder);
`AI-generated/README.md`, `AI-generated/batch-reports/README.md`, `readme-at-start.md`, and
the plan's ledger, report links and §4b.

**For a future session.** Forty-nine stored results are cited by no claim; twenty-four are
figures and their plotted values, and the way to find out about the rest is to write the case
study and see what it needs, which is batch 19. `/validate outsider` in batch 18 is the first
time anyone but the author looks at the report, and legibility is the thing the link check
cannot test. The report is gitignored, so `/release` in batch 19 has to build it rather than
assume it.

**Commits.** `ce43d47` (the claims and the extended builder, before the build), `cf6005e` (the
report, its provenance record and the surrounding documents) and `e69870c` (the rebuild once
C39 closed the collection).

### T17, extended — the decisions settled after the batch report

**What happened.** Batch 17's report ended with a question and repeated one of batch 16's;
the human answered both and, asked what else was open, settled four more. Seven decisions,
all in the plan's §4b with their agency. No analysis ran and nothing under `analysis/` moved.

**The one that changed a claim.** Batch 17 had adopted a rule of its own — a claim states the
figures a file holds and never a ratio between two of them that no file computes — and phrased
C23, C29 and C31 by it. The human set a wider line: **a claim may state what follows trivially
from the figures it cites, a ratio or a ranking, and may not state anything that needed a step
nobody ran.** The reasoning recorded is that a reader can check a quotient of two cited figures
at a glance and cannot check a number standing for a computation nobody ran; only the second is
the transcription `AGENTS.md` §1 forbids. C23 now states 3.282 CRPS, its split-clustered
standard error of 1.726, and the **1.90 standard errors** they come to, and its agency moved
from `agent-autonomous` to `agent-on-human-assessment`. The rule lives in
`Human-AI-collaboration/claims/README.md`, which is what a future session writing claims
reads, and in `readme-at-start.md`. Batch 17's own narrower rule is marked superseded in §4b
rather than deleted.

**What the other six settle.** The case write-up's judgment about where this setup was more
trouble than it was worth is the agent's, offered back for comment — and batch 19 must label it
`agent-autonomous`, not jointly held, because the delegation is the human's decision and the
verdict is not. `analysis/run.sh` is not split. Batch 20 is confirmed rather than cut, and
**moves ahead of batch 19** (the agent's call, logged as such) so the case study can use it,
making the remaining order 18, 20, 19. A remote is created after all, reversing §10, at
`github.com/sandvelab/veridical-agentic-dengue-laos` — owner the human's, name delegated and
chosen here — pushed as the last step of batch 19's `/release`, after the scan and both
validations, with the agent asking first. The target venue is *PLoS Computational Biology*.
And `/validate outsider`'s findings in the instruction files are fixed by the agent and
committed as Rule 4 methodological changes rather than proposed first.

**Checked before promising the push.** `.git` is 131 MB packed and no tracked file exceeds
50 MB, against a 1.6 GB working tree — so GitHub's per-file limit is not near and the push is
feasible. `gh` is authenticated as `sandve` with `repo` scope. The repository does not exist
yet and the name is free to change until batch 19 creates it.

**Files affected.** `Human-AI-collaboration/claims/claims.md` (C23),
`Human-AI-collaboration/claims/README.md`, `readme-at-start.md` (remote, venue, status, "left
to the human"), the plan's §4b, §10, ledger row 20 and budget table, and
`AI-generated/hierarchical-report/provenance.md`, which gained a build record because the node
pages carry the collection and a corrected claim leaves the report stale until it is rebuilt.
The batch report itself is **not** edited: it is the record of batch 17 as it happened, and
§4b is where a decision taken afterwards belongs.

**For a future session.** Batch 18 is next and is the six-hour clean-room run. Batch 20 then
batch 19. Batch 19 must remember three things this entry carries and the batch report does
not: the write-up's judgment is labelled `agent-autonomous`, the push is the last step and is
asked about first, and the venue is fixed.

**Commits.** `a87f6ce` (the task log for batch 17 proper), then the ruling on C23, batch 16's
two questions, and phase E's four remaining decisions.

## T18 — batch 18: the clean-room, the outsider check, and the plan's own drift (2026-09-01)

Phase E's three verification obligations, two of which had never been run in this repository:
`/validate outsider` not once, and `/validate cleanroom` not since batch 7, when the tree had
no stability node, no phase E and no candidate models. Between them they found nine defects,
three wrong numbers and a broken provenance link, and **every one was a statement that is true
on the page and false when executed** — which is precisely the class `/validate invariants`
cannot see, because it verifies shape and never content.

**The clean-room's largest finding preceded its first executed line.** A fresh `git clone`
skipped all 32 phase-E rows, because the seal plan §3 requires rested on
`05_stability/results/run_status_holdout.csv`, which is versioned and therefore ships with
every copy of the repository. `collect_conclusions.py --dataset holdout` then re-read the
committed conclusions and the phase-E half of `analysis/run.sh` reproduced its outputs
byte-identically while running none of the analysis behind them. `run_manifest.py`'s
docstring, `05_stability/run.sh` and `readme-at-start.md` all asserted the opposite. The fix
keeps both properties the original design wanted at once: the seal now needs the versioned
status row **and** `05_stability/.holdout_opened`, which is gitignored, so deleting a row to
force a re-run still shows in git while a clone is not sealed by a record it merely inherited.
The marker sits at the node root rather than under `results/` because `/validate invariants`
objected — correctly — that everything there needs a provenance record, and it is working-tree
state rather than a result.

**What the run verified, and where it stopped.** The environment built from
`environment/lock.txt` and reported matching it exactly (174 packages, chap 2.1.0); 3 994 of
4 284 tracked files came back byte-identical. Every model this project wrote reproduced its
mean CRPS to the last digit — persistence 24.879338288409706, climatology 24.336908636118597,
the reported pool 18.816872064690028 — on a fresh clone with no prior state, which is the
independent confirmation of what the determinism checks claimed. The reference model is
unseeded and redrew {21.917, 22.272, 22.385, 21.820} → {22.436, 22.473, 22.024, 22.145},
moving the headline skill +0.1485 → +0.1550. **Everything that moved in `conclusion.json`
moved because of that and nothing else.** Two incidental findings worth more than they look:
the **resolvable-difference floor is itself a random variable** (0.565 archived, 0.449
re-run), so every "nothing below 0.57 CRPS is attributable" statement describes one sample of
four repeats; and the clean-room produced four `member_selection.json` files the archive
lacks, because five combinations predate the `prepare_members.py` fix that writes it — so
"re-running reproduces the archive" is slightly false. **The run was then interrupted at 8 of
32 development rows**, so neither distribution is verified from cold and the phase-E half has
still never executed from a clean checkout. `readme-at-start.md`'s first invariant now says
so, and batch 19's release must not claim more than the validation document supports.

**The outsider check used two agents on disjoint tasks** — one writing into the tree, one
tracing the headline result back to the archived data — each given a throwaway clone and no
context. They failed in different places, which is the argument for two. The reader found
that "the eleven forks inside the two member families" are **eight** forks whose eleven
non-main children are the eleven, a noun error originating in a batch-14 table whose column
was a row count and copied into four places **including claim C3**; that "nine of the eleven
below the noise band are candidate-internal" is eight; and that a cost ratio was rounded up
from 0.514. It also found six provenance records naming `9993d37`, orphaned by a history
rewrite in batch 14, with `87440bc` surviving at the same tree — invisible because
`git cat-file -e` answers whether an object is in the store, orphans stay in the store, and a
**local** clone hardlinks the object directory, so it looked present everywhere and would have
vanished on the first push. Separately the anchored `commit:` pattern skipped `conclude.md`
entirely for annotating its two hashes, meaning the headline result's record was the one
record never checked. The writer found that `freeze_holdout_manifest.py` **rebuilds the frozen
phase-E manifest on every run of `analysis/run.sh`** — byte-identical only because the tree
has not changed — and produced a 34-row frozen set once a fork child was added.

**The plan's drift is measured rather than described**, by
`AI-internal/useful-scripts/plan_drift.py` into `AI-generated/plan-drift/`. 89.1% of delivered
lines survive byte-for-byte and 94.6% of words, while the document is five times its delivered
length: the plan did not drift, it grew. The aim survives at 1.000 and was never revised; what
moved is what was labelled provisional — the budget (0.563), which guessed phase C was elastic
and was wrong about compute binding at all, and the ledger (0.500), whose seven named batches
and three placeholders became twenty-two. Of 169 §4b decisions, 145 are `agent-autonomous` and
15 `human-set`; six of those fifteen sit inside batches' own tables, so counting occasions
rather than decisions would have attributed them to the agent. Two figures in the report's
first draft were counted by eye and both were wrong, and are now computed by the script —
§1 in miniature.

**Files.** `AI-generated/validation/26-08-31_outsider.md` and `26-09-01_cleanroom.md`, with
`26-09-01_cleanroom_comparison.json` and `provenance.md`; `AI-generated/plan-drift/` (report,
`plan_drift.json` and four CSVs, README, provenance); `AI-internal/useful-scripts/`
gained `plan_drift.py`, `run_cleanroom.sh` and `cleanroom_compare.py`, and
`check_invariants.py` now requires ancestry of HEAD and reads every hash on a `commit:` line.
The root `README.md` was rewritten and **no longer restates project state at all**, which is
the durable fix for having described batch 1 through four phases. `AGENTS.md` §8 gained the
node-directory exemption from README-per-folder, the by-location interpreter rule, and a rule
for work arriving outside `/do`.

**Follow-ups, all in the ledger.** Batch 23: 16 of 77 provenance records name a script version
that no longer exists, worst `analysis/provenance/conclude.md`, whose newest section predates
batch 16 changing `conclude.py` and running it — so no record names the invocation that wrote
`main__holdout/conclusion.json`. The fix is an invariant plus sixteen appended sections and
they must land together. Batch 24: the recomputed freeze. Batch 25: finish the clean-room.
Batch 19 goes last. **One question is carried to the human**: plan §3 does not say which
artefact its freeze binds, and §10 reserves changes to the non-negotiables. The connected
question was answered on 2026-09-01 — **the perturbation set stays at 32** — which also means
the tree does not grow before release and batch 24's defect is fixed for the reader rather
than for this project.

### T18, extended — §3 says which artefact its freeze binds

**What happened.** Batch 18's report closed with one question carried to the human: plan §3
says *"nothing is added, dropped, re-tuned or re-run after a holdout number has been seen"*
and does not say what that binds. The human first settled the operational half — the
perturbation set stays at 32 — and then, asked what keeping the set costs, asked for the
interpretation to be written into §3 rather than left implicit. No analysis ran and nothing
under `analysis/` moved.

**Why the ambiguity is real and not pedantry.** Batch 18's outsider agent was asked to add a
training-window alternative and walked straight into it: `/validate invariants`'s `combos`
check *requires* every non-main child in the tree to have a row in the development manifest,
while §3 read literally forbids adding anything at all once the holdout is open. Two rules in
the same repository, contradicting each other, with no text saying which yields. The agent
took the narrow reading and recorded the guess in three places rather than deciding quietly,
which is the behaviour the check exists to produce.

**What the text now says.** The freeze binds `manifest_holdout.csv` and nothing else, because
what it protects is the set evaluated on 2010 — that is what makes the holdout spread a
measurement rather than a selection. The tree and the development manifest may still grow. A
development row added after the opening has no holdout twin, can never acquire one, and is
reported as an unpaired analysis outside the distribution rather than joining the 32. The
clause ends by saying that nothing further is added in *this* project, so a reader cannot
mistake the clarification for a licence this run used.

**Where it went.** The sub-clause in the plan's §3; two mirrored sentences in
`readme-at-start.md`'s "What must not happen" #1, which carries the same rule verbatim and
would otherwise drift; and a §4b row in the 2026-09-01 table, above the human's 32-analyses
ruling.

**Agency, and why it is not `human-set`.** Recorded as `agent-on-human-assessment`: the
narrow reading is the agent's, the decision to write it into a non-negotiable is the human's,
and `AGENTS.md` §10 reserves changes to §3. Calling it `human-set` would overstate the
human's part and `agent-autonomous` would overstate the agent's — and this project reports
its own agency as a result, so the distinction is not bookkeeping.

**What this changes about the follow-ups.** Batch 24 — the frozen phase-E manifest being
recomputed on every run of `analysis/run.sh` — loses its practical urgency, because the tree
does not grow again before release and the defect is therefore unreachable in this project.
It stays in the ledger because it is a defect for anyone reproducing the method. The
remaining order is unchanged: 23, 24, 25, 20, 19.

## T19 — batch 23: a record's digest must be the file's (2026-09-01)

**What was produced.** A new deterministic check, `hashes`, in
`AI-internal/useful-scripts/check_invariants.py`, and twenty appended provenance sections
that make it pass. They landed in one commit (`477115f`) because either alone is worse than
neither: the check without the sections is a failing check, the sections without the check
are twenty corrections with nothing to stop the twenty-first. The report is
`AI-generated/batch-reports/26-09-01_b23_provenanceHashes.md`.

**What the check says, and what it deliberately does not.** For every file a record gives a
`sha256:` for, the file must exist and the record must name its current digest *somewhere* —
not in the newest section, because an old section names the version that ran under it and is
right to keep it. Abbreviated digests (`sha256:cbd3158db12438ac…`, the form the model
contract files use) satisfy it as a prefix. It parses each `script:` field with its
continuation lines and pairs a named file with the digest that is the next token after it, so
`scripts/run_hier_nb.py   (unchanged)` followed by the model files that did change claims
none of their digests. 109 file-digest pairs across the 77 records pass. It does **not**
verify that a digest is paired with the run it sits beside, that a library a script imports
is named at all, or that anything in the record is true.

**Why twenty rather than batch 18's sixteen.** Batch 18 scanned `script:` lines. Four records
— the two baselines, the reference model and candidate 1 — name
`analysis/03_models/scripts/lib/chap_eval.py` on a continuation line with a digest of its
own, and that library changed at `4563baf` (the `--model-configuration-yaml` route) and at
`49825b5` (resolving `02_setup`'s output through `COMBO_BASE`). A check on the runner alone
passes all four. This is the same shape as the defect batch 18 found in its own `commit:`
pattern — a record more informative than the pattern expected, skipped for being so — found
again in the estimate that diagnosis produced.

**The cause, which is worth carrying forward.** Nineteen of the twenty are one failure: a
batch appends its section when it runs the script, changes the script again later in the same
batch, and does not append again. Nothing looks wrong afterwards and no number moves. The
obligation "record what you produce" is discharged at a point in time; the property "the
record describes what is there" is continuous, and nothing continuous was watching it.

**Two judgment calls about re-running.** The development stability figures were re-drawn —
batch 16's refactor moved the drawing into `scripts/lib/stability_figures.py` *after* they
had been drawn — and came back byte-identical, PNG and CSV, so the archived figures are now
ones the current scripts have actually produced. The reported development conclusion was not
re-run: `results/main/conclusion.json` was written at `87440bc` by the batch-14 version of
`conclude.py`, and re-running it would be a re-run made for a record's benefit rather than
the analysis's. What covers it is batch 18's clean-room rebuild, which rebuilt every input as
well as the script. The rule the batch worked to: where re-running would have meant re-running
an analysis, it did not.

**A gap recorded and not closed by code.** Both stability figure records attribute their
held-out figures to `fig_*.py --dataset holdout`. The refactor removed that flag and gave each
its own runner, `holdout_fig_*.py`, which no section named. `hashes` cannot catch this — it
checks the files a record hashes — and `check_provenance` is satisfied because the file *is*
named. The new sections carry both runners and the shared library; the check that would catch
it in general is `/validate cleanroom`, at a different cost.

**Files affected.** `AI-internal/useful-scripts/check_invariants.py`; twenty records under
`analysis/**/provenance/`; `AI-internal/skill-references/provenance-record.md`,
`.claude/commands/track-result.md` and `.claude/commands/validate.md` (a Rule 4 methodological
change — the digest is required, and a changed script gets an appended section rather than an
edited one); `AI-internal/useful-scripts/README.md`; the plan's ledger row, report link and a
§4b table; `readme-at-start.md`, which also had a sentence repaired that batch 18 left
half-edited, the greedy branch's description having been orphaned onto batch 19's release.

**Follow-ups.** None from this batch. The remaining order is **24** (the frozen phase-E
manifest is recomputed on every run of `analysis/run.sh`), **25** (the clean-room run to
completion), **20** (the external check on `tha` and `vnm`), **19** (the case write-up, the
reproducibility report and the release).

## T20 — batch 24: the frozen set wins over the recomputation (2026-09-01)

**What the batch was for.** Batch 18's outsider check found that
`analysis/05_stability/scripts/freeze_holdout_manifest.py` rebuilt the frozen phase-E
manifest on every run of `analysis/run.sh`, and deferred the fix. The manifest is the
artefact plan §3 rests the whole holdout spread on: it fixes *what* is evaluated on 2010
before 2010 is opened, so that the spread is a measurement rather than a selection. The
script sits at the end of the development half of `05_stability/run.sh`, later in the same
block than `plan_manifest.py`, which re-derives the **development** manifest from the tree — which it is
supposed to do, and which the 2026-09-01 clarification permits to grow. So a fork child
added after the opening was one run of the analysis away from entering the frozen set, and
the byte-identity everyone had relied on was a property of the tree not having moved.

**What was built.** The frozen file is authoritative and the script has two modes, chosen by
whether it exists. Missing → the freeze, batch 15's path, with one new refusal. Present → a
verification: the set the tree would produce now is derived by the *same function* that would
have written it, `manifest_holdout.csv` and `holdout_freeze.json` are not touched, and the
comparison goes to `results/holdout_freeze_check.json`. A development row with no frozen twin
is reported **unpaired** and never added; a frozen row the tree no longer carries, or one
whose structural columns moved, is **fatal** and stops the run; a frozen row whose numbers
moved is recorded, because the reference model is unseeded and batch 25's clean-room run
moves them by about 0.006 on an honest re-draw. And if the file is missing while the year has
already been opened — `run_status_holdout.csv` records a row as `ran`, or a
`results/*__holdout/` directory exists — the script refuses and says to restore it from git.
The guard deliberately does not consult the gitignored `.holdout_opened`: that says only that
*this working tree* opened the year, which is the driver's question, and batch 18 was caught
by the mirror image of using the wrong one.

**The second half of the fix.** `check_invariants.py` gains `freeze`, so the file is checked
and not only the script that writes it: the frozen manifest must still hash to what
`holdout_freeze.json` recorded, the row count must agree, and no file under
`analysis/results/*__holdout/` may exist at the commit that added the frozen set. That last
is the claim `holdout_freeze.json`'s own `commit_note` makes and it is the entire evidence
that the set predates the opening; it was prose until now and it is one `git ls-tree` away.
The other digests the record carries — `conclusions.csv`, `distribution.json`, the
development manifest — are deliberately not checked, being context recorded at the freeze
rather than the frozen artefact.

**How it was checked.** `AI-internal/useful-scripts/check_freeze_defence.py`, new: eleven
situations, seven to the script and four to the invariant, on throwaway copies built from the
live files. Four of them corrupt the frozen manifest, which is why none runs against the live
tree. All eleven behaved as specified
(`AI-generated/validation/26-09-01_freezeDefence.json`, written up in the `.md` beside it).
Two matter: `added` is batch 18's defect reproduced — 33 rows and one unpaired row where the
superseded script produced 34 — and `refreeze_from_cold` is the regression test, deleting the
frozen file with no trace of an opening and getting batch 15's manifest back byte for byte,
which is what says restructuring the script did not restructure the set. **Run against the
superseded version, six of the seven script scenarios fail and every one exits 0.**

**A second hole, found on the way.** `holdout_freeze.json`'s `frozen_on` was written from
`date.today()` on every invocation; run today the superseded script moved it 2026-08-31 →
2026-09-01 with the other eighteen keys identical. Batch 16 found and fixed exactly this in
`frozen_at_commit`, one line above, and left the date. The durable fix was never the field —
it was that a value recording history must not be derived at run time.

**Files.** Changed: `analysis/05_stability/scripts/freeze_holdout_manifest.py`,
`analysis/05_stability/run.sh` (its comment asserted byte-identity as a guarantee),
`AI-internal/useful-scripts/check_invariants.py`, that folder's `README.md`, and
`.claude/commands/validate.md` — an instructions change under Rule 4. Added:
`AI-internal/useful-scripts/check_freeze_defence.py`,
`analysis/05_stability/results/holdout_freeze_check.json`, and the two validation documents.
Records appended to `analysis/05_stability/provenance/freeze_holdout_manifest.md`,
`AI-generated/validation/provenance.md`, `claim.md` and `criticality.md`. Commits `595c32d`
(before the run) and the one after it. `/validate invariants`: all ten checks pass.

**Nothing in the analysis was re-run** and no reported number moves. The frozen manifest and
`holdout_freeze.json` are byte-for-byte what batch 15 froze and batch 16 ran.

**Follow-ups.** Batch 25 runs `/validate cleanroom` to completion — batch 18's reached 8 of
32 development rows, so both distributions are unverified from cold and the phase-E half has
never run from a clean checkout. It is also the first run that exercises this batch's fix end
to end, and `analysis/run.sh` can now fail in a way it could not before: a tree that has moved
under the frozen set stops the run instead of quietly bringing the set along. Then batch 20
(`tha` and `vnm`), then batch 19 (write-up, reproducibility report, release).

**Two parent READMEs, brought into line afterwards.** `AI-internal/README.md` enumerated the
five scripts under `useful-scripts/` and had not been extended since batch 7, so batch 24's
new script was the sixth thing missing from it; `AI-generated/README.md` listed what every
batch report established and stopped at batch 17 while the ledger reached 24, and described
`validation/` as holding only what `/validate` produced. In both cases the enumeration
duplicated a list the folder itself already keeps, so the fix is batch 18's rather than a
fresher copy: **the parent points at the child's own README and stops restating it.** Only
`validation/`'s one-line description is rewritten in place, because that folder's contents
genuinely changed — it now holds a check written for a single defect as well as the two
`/validate` runs.

## T23 — batch 25: the clean-room, stopped by the project's own check (2026-09-02)

**State: blocked.** `/validate cleanroom` was to be run to completion. It was not.
`analysis/run.sh` ran **3 h 48 m (13 669 s)**, completed the whole development half, and
**exited 1** at the freeze check. The phase-E half has still never been executed from a clean
checkout — batch 18 could not reach it because the seal sealed clones, and this run could not
reach it because the run aborts first.

### How it was run

Clone at `ae0f62d` into a scratch directory, `environment/chapenv` built from
`environment/lock.txt`, `bash analysis/run.sh` from cold, on the host so the containerised
reference model can run. The harness `run_cleanroom.sh` and comparison `cleanroom_compare.py`
were **verified by digest against batch 18's provenance record before the run**, so "the same
check, run further" is a checked claim rather than an assumption.

The run was launched **detached from the session** with `nohup`. Batch 18's clean-room died
because its session was cut off; this one outlived two of its own monitors being killed.

### What it verified, and it is more than batch 18 could

`install-chap.sh` reported **"matches environment/lock.txt exactly (174 packages)"**,
`chap 2.1.0` on CPython 3.13.0. Of **4 306 tracked files, 3 458 identical**, 848 differing,
93 untracked.

**Every model this project wrote reproduced its CRPS exactly in every combination it appears
in** — 32 for persistence, 32 for climatology, 27 for the reported ensemble, 4 for `hier_nb`,
1 for `boosted`, and **zero moved between them**. The unseeded reference moved in **26 of 32**
and is identical only in the 6 that inherit rather than re-run it. On the main path it went
22.098446 → 22.383842 (+0.285 CRPS), carrying skill +0.148498 → +0.159355 (+0.0109);
`beats_reference` and `beats_all_baselines` stay true.

### Why it stopped

`manifest.csv`'s 24 tier-1 rows are planned from the tree. Its **8 tier-2 rows are not** —
they are selected from tier 1's own results by `tier2_rule.md`: rank each tier-1 row by
distance in skill score from the main path, take the top two `setup`, top two model and top
`scoring` rows, pair the groups. **Skill divides by the unseeded reference**, so the ranking
ranks numbers that do not reproduce.

| group | archived | clean-room |
|---|---|---|
| S (setup) | `provinces_reportingOnly`, `provinces_mergeVientiane` | `provinces_reportingOnly`, `trainingWindow_from2004` |
| M (model) | `family_hierNB`, `weighting_crpsWeighted` | unchanged |
| A (scoring) | `aggregate_caseWeighted` | `aggregate_populationWeighted` |

Two selected rows changed; the groups are paired, so **six of the eight pairs changed**. The
freeze check reported `9 difference(s) the frozen set cannot absorb` — six frozen rows the
tree no longer carries, three whose `rank` moved — and refused to rewrite `manifest_holdout.csv`,
which is intact at 33 rows and `fc9d1a16…`. `set -e` did the rest.

**The margins say it was never stable.** The deciding margin is how far the last row admitted
sits above the first excluded: group S **0.001002**, group A **0.003211**, group M 0.093547,
against a reference noise band of 0.043084. The two decided inside the noise both flipped; the
one decided by twice the band did not.

**What is and is not in question.** The phase-E results stand — the set was frozen in batch 15,
committed before 2010 was opened, and batch 16 ran exactly it. What is not reproducible is the
*derivation*. The eight pairs are a **decision**, correctly recorded, that the project has been
treating as a **derivation** — batch 24's own lesson (*a value that records history must not be
derived at run time*) standing one file upstream of where batch 24 applied it.

### The band is a draw, and the phase-D headline moves with it

| | archived | clean-room |
|---|---|---|
| skill against the four repeats | 0.1376, 0.1415, 0.1551, 0.1594 | 0.1448, 0.1512, 0.1521, **0.1879** |
| skill band (max − min) | **0.021778** | **0.043084** |
| CRPS floor | 0.565 | 1.167 |
| forks above the band | **6 of 17** | **3 of 17** |

The three that crossed — `02_setup/02_trainingWindow`, `02_setup/03_provinces`,
`03_models/01_baselines/01_persistence` — **did not move** (0.021875→0.037047,
0.037553→0.041809, 0.027933→0.027576). The yardstick moved. Only `family`, `weighting` and
`aggregate` are clear on both draws. The CRPS floor has now been drawn three times: 0.565,
0.449 (batch 18), 1.167.

Claims **C3 and C4** gained that contingency in their `scope:` fields, as did
`readme-at-start.md`'s stability row and its first "what has to stay true". **How it should be
reported is carried to the human** — quoting it with its uncertainty, re-estimating it from
more repeats, or demoting it to an order of magnitude all change what phase D reports.

### The row that crashed

`trainingWindow_from2004__weighting_crpsWeighted` failed at `check_pool.py`:
`fitted["weighting"]["validation"]`, `KeyError`. The pipeline was right — `run_ensemble.py`
recorded `"fell_back": true`, *"holding back 12 months would leave 36 to refit the members on,
below the 60 this model requires"*, `"method": "equal"`. `check_pool.py` branches on the
**configured** choice, `stage["choice"] == "b_crpsWeighted"`, not on what the weighting did.
Fork-blindness, the family batch 14 found four times.

Unreachable until the selection drifted — and **the pair is degenerate anyway**: under a
training window from 2004 the weighting fork cannot take effect, so had it run it would have
duplicated the training-window row under another row's name.

### Added, and what is left

`AI-internal/useful-scripts/cleanroom_tier2_drift.py` — the per-model reproduction table, the
tier-2 selection both ways with its deciding margins, and the band. It carries a **self-check**:
applying its copy of the rule to the archived conclusions must return the frozen eight pairs,
and does; nothing under `tier2` is readable if that field is false.
`AI-generated/validation/26-09-02_cleanroom.md`, two JSON results, and
`26-09-02_cleanroom-artefacts/` holding what the run itself wrote, copied out before the
throwaway clone was discarded.

**Nothing under `analysis/` was run, edited or re-run.**

**Batch 26** — the development manifest stops being re-derived: the tier-1 rank order and the
tier-2 selection recorded and verified rather than recomputed, the `combos` invariant still
supplying membership from the tree, and `check_pool.py`'s fork-blindness with it. This does not
touch §3, which the clarification of 2026-09-01 binds to `manifest_holdout.csv` alone.
**Batch 27** — the clean-room, again. Then 20 and 19.

### One thing about this batch's own record

Writing the provenance section for `26-09-02_cleanroomTier2Drift.json` I produced a
**fabricated sha256** for `plan_manifest.py` — a plausible 64-hex string that was no file's
digest — in the middle of a document about provenance. It was caught before the commit by
hashing every digest in the new records against the files they name, and the record carries
`ffb398e8…`, which is the file's. Worth keeping: the failure mode this repository exists to
prevent is one its agent will commit unprompted, and what caught it was running a check rather
than re-reading.

## T24 — batch 26: the selection is recorded, not re-decided (2026-09-02)

**State: done — produced.** What batch 25 was blocked on. `plan_manifest.py` derived two
things from numbers that do not reproduce, and both had to become recorded decisions.

**The tier-1 order** breaks its ties on `est_seconds_dev`, a *measured wall-clock duration*
summed from each model's `run_cost.json`. The five `setup` rows have no informativeness prior
and equal reach, so their order is that tiebreak alone — `provinces_reportingOnly` took 821 s
in this tree and 1 039 s in the clean room and moved from rank 5 to 7. **The tier-2 pairing**
ranks tier-1 rows by skill score, which divides by the unseeded reference; the clean room
re-selected six of the eight pairs.

Both are now recorded in `results/manifest_selection.json`, **written once and never
rewritten**, with `frozen_at_commit` read from the commit that *adds* the file rather than
HEAD — batch 16's and batch 24's lesson applied without having to relearn it. Membership still
comes from the tree on every run, because `combos` requires the manifest and the tree to agree
and §3's clarification of 2026-09-01 lets the development manifest grow: a combination the
tree has and the record does not is **appended and reported**; one the record has and the tree
does not is **fatal**; a recorded pair whose halves are gone is fatal. A **drifted selection is
reported and never fatal** — the rule still runs and now decides nothing, existing only so
`manifest_selection_check.json` can say whether it would still choose the recorded pairs. After
any re-run of the development half it generally will not, and a check a correct clean-room run
cannot pass is a check that gets weakened the first time it fires.

**Five situations, all passing** — `AI-internal/useful-scripts/check_selection_defence.py` →
`AI-generated/validation/26-09-02_selectionDefence.json`. The important one is driven by **the
clean-room run's own `conclusions.csv`** rather than a synthetic perturbation: the rule chooses
the same six different pairs it chose in batch 25, the recorded eight stand, `manifest.csv`
comes back byte-identical, and the disagreement is reported. Plus two fatal paths, a
never-rewritten check, and `refreeze_from_cold`, which deletes the record, runs the freeze path
again and returns the same order and the same eight pairs — the regression test that this
refactor did not change what phase E was frozen against. Each scenario restores from git
unconditionally.

**`check_pool.py` now branches on what the weighting did**, not on `stage["choice"]`.
`run_ensemble.py` falls back to equal weights when the training frame cannot hold a validation
block back, so a row that asked for CRPS weighting and correctly got equal weighting died with
`KeyError: 'validation'` — how batch 25 lost `trainingWindow_from2004__weighting_crpsWeighted`
and finished 31 of 33 rather than 32. The two new keys are written **only on the fallback
path**, which no archived combination takes, so all 51 `pool_check.json` files stay
byte-identical.

**Nothing reported moves.** `manifest.csv`, `manifest_notes.json`, `forks.csv` and
`tier2_rule.md` are byte-identical across a freeze run and repeated replays;
`manifest_holdout.csv` still hashes to `fc9d1a16…`.

**A third and larger defect was found and deliberately left standing as batch 28.**
`matching_evaluation` globs sibling result directories and breaks ties with `found[0]`, so
which evaluation it names — and whether it finds one at all — depends on which combinations
exist on disk. Re-running the **unmodified** script changes **18 of 51** pool checks;
`main__holdout`'s archived copy records its reconstruction as impossible (*"no stored
evaluation of ['hier_nb', 'boosted']"*) because batch 16 ran it before those directories
existed, and today it reconstructs and returns **76.646** against the reported 76.731. No
number inside the eighteen moves. Verified to pre-date this batch by restoring `HEAD`'s own
copy of the script and re-running it. Repairing the tie-break alone would rewrite eighteen
archived files while leaving the time-dependence in place.

Follow-ups: batch 27 (the clean-room to completion — the first run to exercise the record from
a clean checkout, and it *should* report a drifted selection, which is the designed outcome
not a failure), then 28, 20, 19.

## T25 — the record's own bookkeeping, outside a batch (2026-09-02)

Not a batch of the plan. It arrived from a question at the end of the session — *is everything
ready for the next batch* — and `AGENTS.md` §8 requires work that does not come through `/do`
to get a ledger row and a §4b entry anyway. It is **row 29**.

**The ledger would have sent the next session to the wrong batch.** §5 says the ledger is
executed top to bottom. For the phase-E tail it is not: **19 and 20 have been open since batch
5 and sit above 27 and 28**, which run first, with 19 last because a release must not claim
more than its checks support. Only `readme-at-start.md` carried that order, and a fresh session
following §5 would have opened the release with two checks outstanding. The ledger now states
its execution order in its own header, with the reason and the date. The trap had been latent
since batch 18 appended 23, 24 and 25 below rows 19 and 20; it never bit because every session
so far had read `readme-at-start.md` first. Batch 27's row was also moved above batch 28's,
since they had been appended in creation order rather than run order.

**Two task-log entries had reused `T` numbers already taken.** Batch 25 was logged as T21 and
batch 26 as T22, but batch 21 already held T21 in `ai_task_details.md` and batch 22 already
held T22 in `ai_task_history.md` — the project having logged those two out of sequence back on
2026-08-29. So the details file carried two `T21` headings and the history file two `T22`
lines. They are renumbered **T23** and **T24**; the entries' text is unchanged and only the
identifiers move. The `T` number is the log's only index, and a duplicated identifier makes it
useless as one. `T21 continued` on line 20 of the history is a deliberate continuation of batch
21 and is not a collision. Recorded rather than done quietly, because a log that silently
renumbers itself is worth less than one that says it did.

Also checked and found already on disk, needing nothing: batch 27's expectation that a drifted
`manifest_selection_check.json` is the designed outcome (b26 report §8 and the `plan_manifest`
provenance record); batch 28 in the ledger, §4b, the b26 report and as a `KNOWN DEFECT` comment
at the defect's own line in `check_pool.py`; and batch 25's noise-band question to the human in
§4b, `readme-at-start.md` and claim C4's scope field.

**What is left to run: 27, then 28, then 20, then 19.** Batch 27 is a ~4 h run and must be
launched detached from the session, as batch 25's was — batch 18's clean-room died with its
session. It needs disk: 28 GB were free at the end of this session and 11 GB of that is batch
25's scratch clone, whose contents are already committed under
`AI-generated/validation/26-09-02_cleanroom-artefacts/`.

## T26 — batch 27: the clean-room reaches phase E, and stops at the last script (2026-09-03)

**State: blocked.** `/validate cleanroom` was to be run to completion and was not.
`analysis/run.sh` exited 1 at `pair_holdout_development.py`, the last script in the tree,
after the phase-E half had finished. Ledger row 27 is `blocked`; batches 30 and 31 added.

### The run

Clone at `80276f3`, 4 329 tracked files, no `.holdout_opened` so the seal released.
Harness and both comparison scripts verified by digest against batch 25's provenance record
before starting (`846911b2…`, `33010dd1…`, `3d98ea7e…`) — the same check, run further.
Launched detached, which earned its keep: the session's wait process was killed twice while
the analysis ran on untouched.

`run_seconds.txt` records 81 335 s, but the host slept for a large part of that, so it is
wall clock and not compute. The development half took about 4 h 20 m against batch 25's
3 h 48 m for the same work. The `holdout: planned 7 468 s vs actual 65 818 s (ratio 8.814)`
line the run printed is contaminated the same way and is reported as such rather than as a
cost finding.

### What reproduced

192 model-combination scores, 96 per half, from models this project wrote — **0 moved**:

| model | development | holdout |
|---|---|---|
| persistence | 32 identical, 0 moved | 32 identical, 0 moved |
| climatology | 32 identical, 0 moved | 32 identical, 0 moved |
| ensemble (reported) | 27 identical, 0 moved | 27 identical, 0 moved |
| hier_nb | 4 identical, 0 moved | 4 identical, 0 moved |
| boosted | 1 identical, 0 moved | 1 identical, 0 moved |
| **reference** (unseeded) | 0 identical, 32 moved | 0 identical, 32 moved |

Reported paths: development ensemble CRPS 18.816872064690028 identical, reference
22.098446493261456 → 22.255807673854445, skill +0.006021. Holdout ensemble CRPS
76.73108261979166 identical, reference 84.02620178776041 → 83.79891141666666, skill
−0.002477. `beats_reference` and `beats_all_baselines` unchanged on both. 2 224 of 4 329
tracked files identical.

**Phase E reproduces on every count it reports**: beats the reference 26 of 32, beats both
required baselines 27 of 32, 17 rows inside the noise band, 5 forks above it — and the same
five by name (`02_trainingWindow`, `03_provinces`, `03_candidate`, `a_hierNB/02_covariates`,
`02_aggregate`). The four fields that moved are skill, reference CRPS, rank (18→16) and the
band (0.014023 → 0.013410), each downstream of the reference. The holdout band is nearly
steady across draws where the development band is not.

### Batch 26 and batch 24, exercised from cold

`manifest_selection_check.json` after tier 1 re-ran: the tier-1 order **would** have moved
four positions (`provinces_reportingOnly` 5→6, `popColumn_backCast` 6→5,
`provinces_mergeVientiane` 7→8, `retrain_everySplit` 8→7) and the tier-2 rule **would** have
chosen six different pairs. Both reported, neither acted on; the recorded eight ran.
`holdout_freeze_check.json`: *the frozen set is intact*, 33 rows, `fc9d1a16…`, 0 fatal, 0
unpaired, 32 rows whose numbers drifted.

**`manifest.csv` is not byte-identical from cold**, contrary to batch 26's report: all 32
rows differ in `est_seconds_dev` and `est_seconds_holdout` only, which are measured
durations summed from each model's `run_cost.json`. Order, names, node paths, skill values,
statuses and all eight pairs are identical — the property batch 26 built. The claim was true
of the tree batch 26 tested in, where the timings were not re-measured.

### Why it stopped

`pair_holdout_development.py` takes each holdout row's development figure from the frozen
`manifest_holdout.csv`, which is correct. It then asserts each frozen figure still equals
`conclusions.csv` **today** to `1e-9` — a tolerance its comment calls "not a tolerance for
drift: it is float formatting through a CSV". The development skill score divides by the
unseeded reference, so **the assertion can hold only on a tree that has not been re-run.**

From `26-09-03_cleanroomHoldoutReproduction.json`: **32 rows drifted, 0 rows had their
pairing move**, `manifest_holdout.csv` byte-identical between the trees, and every drift
inside the band this run measured for itself — largest −0.025673
(`provinces_reportingOnly__weighting_crpsWeighted`, 0.046500 → 0.020827) against 0.034944.
Its message — *"The pairing this compares on is no longer the pairing that was frozen"* — is
not what the data shows.

**The tree contradicts itself.** `holdout_freeze_check.json`, written minutes earlier,
reports the same drift on the same 32 rows under `drift_under_an_unchanged_set` and
concludes the frozen set is intact. One script reports this drift by design; the next treats
it as fatal. Nothing checks that a tree agrees with itself about what is fatal.

Third member of the family: batch 24 found a frozen artefact recomputed at run time, batch
26 a recorded selection re-derived at run time, this a recorded figure re-asserted against a
recomputed one. Each found one file further downstream than the last, by the same method —
running the whole thing from nothing. Two code reviews and an outsider test found none.

### Fixed here, and the line

`install-chap.sh` printed `DOES NOT MATCH environment/lock.txt` against an environment that
**matched exactly (174 packages)**. `uv pip freeze` colours its output when the invoking
shell asks, and the launching session had `FORCE_COLOR=3`: every line failed the byte diff
on its `\033[1m…\033[0m` wrapper, and `sort` ordered the wrapped names differently, leaving
8 packages out of position even after stripping. **The same freeze writes `lock.txt`** on the
`RESOLVE=1` branch, so a lockfile produced from such a shell would carry escapes and would
not install; `environment/lock.txt` is clean and was not written by this run. Both uses now
go through a `freeze()` helper setting `NO_COLOR` and stripping survivors, and the failure
branch reports how many packages fall on each side instead of a truncated raw diff. Verified
against the live `chapenv` with `FORCE_COLOR=3` and `CLICOLOR_FORCE=1` set: *matches
environment/lock.txt exactly (174 packages)*.

This was fixed and the phase-E defect was not, because it is reporting machinery outside the
analysis tree whose repair cannot change a result and takes seconds to verify, where
`pair_holdout_development.py` writes a reported phase-E result and needs a defence of its
own. That is the line batch 25 drew when it left batch 26's defect standing.

### Also found

The clean-room wrote **50 `member_selection.json` files; the archive has 45**. The five
setup combinations concerned have not been re-run since batch 14 added the file, so the
archive never received it. Nothing computed differs — a record never written rather than a
value that moved. Recorded, not manufactured; one copy preserved in the artefacts.

### Files

Added `AI-internal/useful-scripts/cleanroom_holdout_reproduction.py`, so the holdout
per-model table, the phase-E headline beside the archive, the environment comparison and the
stop analysis all come from an executed file (§1) rather than the transcript — its
environment section reads the clone's own preserved `freeze_raw.txt`, escapes included, so
it still answers after the clone is gone. Added `26-09-03_cleanroom.md`,
`26-09-03_cleanroom_comparison.json`, `26-09-03_cleanroomTier2Drift.json`,
`26-09-03_cleanroomHoldoutReproduction.json` and `26-09-03_cleanroom-artefacts/` with a
README. Changed `environment/install-chap.sh`. Three provenance sections appended. Nothing
under `analysis/` was run, edited or re-run; the 18 GB clone was discarded after the
artefacts were copied out.

### Carried to the human, unchanged and with a third draw

The development reference noise band is a max minus a min over four draws of an unseeded
model: 0.021778 (batch 15), 0.043084 (batch 25), **0.034944** (batch 27) — a factor of two
apart, giving a headline of 6, 3 and 3 forks of 17. What is stable on all three draws is
*which* forks clear it — `family`, `weighting`, `aggregate` — so stating the finding by
identity rather than by count may be the cheapest resolution. Still a question about what
the project reports, and not the agent's.

Remaining order: **30, 31, 28, 20, 19**.

---

## T27 — the noise band settled, and batch 30: the frozen figure is reported (2026-09-03)

### The human's decision, and its reversal

Batches 25, 26 and 27 carried one question: whether the development reference noise band
should stay a max minus a min over four draws of an unseeded model. Three draws gave
0.021778, 0.043084 and 0.034944, on which the same file reads **6, 3 and 3 forks of 17**.
Batch 27 proposed stating the finding by *identity* instead — `family`, `weighting` and
`aggregate` clear the band on all three draws.

The human took that resolution and **reversed it the same day**: the count stands. Nothing
in the tree changed in either direction, because the count is what every claim, provenance
record and figure already says; the only edits were to the plan. Ledger row 32, opened to
carry the restatement, was withdrawn. Both decisions are in §4b and commit `1140a7d` remains
in the history asserting the first — §4b's preamble asks for the shape of the dialogue and
not only its outcome, and a record that smoothed this over would contradict the repository's
own git log. `readme-at-start.md` no longer says the question is carried to the human; it
still cites only two of the three draws, which belongs to whoever next writes that file.

### Batch 30 — what was wrong

`pair_holdout_development.py` read each frozen `development_skill_score` from
`manifest_holdout.csv` — correctly — and then asserted it still equalled `conclusions.csv`
**today** to `1e-9`. The development skill score divides by the reference model, which is
unseeded, so **the assertion could hold only on a tree whose development half had not been
re-run**. It passed exactly where it was not needed and exited 1 on batch 27's clean-room
run, at the last script in the tree, with all 32 held-out analyses already scored.

Re-measured here from the preserved artefacts rather than taken from batch 27's report:
**32 drifted figures, 0 moved pairings**, largest 0.025673 on
`provinces_reportingOnly__weighting_crpsWeighted`, against the 0.034944 band that run drew
for itself. The message it died with described a condition the data did not contain.

### What replaced it

A **drifted figure** is reported under `frozen_pairing_verified.frozen_figures_that_drifted`,
with the largest move and the band beside it. A **moved pairing** — a frozen row whose
development twin `conclusions.csv` no longer concludes — is fatal and raises before anything
is written. A twin present but unconcluded is reported, not fatal.

**Widening the tolerance to the noise band was the obvious alternative and was rejected**:
the band is itself a draw of the same unseeded model, so the threshold would be redrawn on
every run, and a check whose threshold moves with its input is not a check. The distinction
that holds is categorical — a figure that moved against a pairing that moved.

### The fourth instance, three lines away

`development_beats_reference` was read from today's `conclusions.csv`, which
`manifest_holdout.csv` does not carry. On batch 27's clean-room conclusions **one row flips**
(`provinces_reportingOnly__family_hierNB`, `False` → `True`) and the reported development
count in `holdout_vs_development.json` reads **28 of 32 rather than 27**. A reported phase-E
figure following a re-derived table — batch 24's family, fourth member, in the same file as
the third.

Fixed here rather than deferred, and the line is stated: it **moved a reported number** on
data already in hand, and the repair needed no new frozen data. `conclude.py` defines the
field as `ours.mean_crps < reference.mean_crps` and both sides are frozen beside the row, so
it derives from the freeze and **reproduces the archived value on all 32 rows** — which is
why the output table stays byte-identical.

`development_beats_all_baselines` cannot be derived from the freeze: it compares against the
baselines' own CRPS, which was never frozen, and freezing it now would rewrite
`manifest_holdout.csv` — bound by §3 and digest-recorded in `holdout_freeze.json`. So it
stays re-derived and the output **names it** as the one development figure that can move on a
re-run.

### The defence

`AI-internal/useful-scripts/check_pairing_defence.py` →
`AI-generated/validation/26-09-03_pairingDefence.json`, **five of five pass**.

`drifted_frozen_figures` swaps in the clean-room's own `conclusions.csv` **and its own
`distribution.json`** — both from the same run deliberately, because measuring batch 27's
drift against batch 15's band would compare two different draws of the same unseeded model.
Result: exit 0, 32 drifted, 0 moved, 0.025673 inside 0.034944, and the comparison verified to
have used the frozen figures by hashing the output's `development_skill_score` column across
the swap. `pairing_moved` removes a twin and confirms exit 1 **with nothing written**.
`beats_reference_comes_from_the_freeze` inverts the boolean on every development row and
confirms the output does not move. Plus a blanked-twin case and a two-run stability case.
Each scenario restores from git unconditionally; nothing touches `manifest_holdout.csv`.

### What did not move

`holdout_vs_development.csv` and `fork_sensitivity_both.csv` byte-identical.
`holdout_vs_development.json` changed only in `frozen_pairing_verified` and two lines naming
where each development count comes from — no reported number moved.
`manifest_holdout.csv` still `fc9d1a16…`. All ten invariants hold.

### What this says about the method

Batch 27 read this script closely enough to diagnose its assertion exactly, write the fix
into the ledger, and explain why it was not fixing it that day — and did not notice that the
line below took a reported development count from a table the same argument said could not be
trusted. **The class is not found by reading; it is found by running from nothing and looking
at what moved**, and here by a defence script that swapped in the real drifted input and
asserted on a number nobody had thought to check.

Remaining order: **31, 28, 20, 19**. Nothing is carried to the human.

---

## T28 — batch 31: the clean-room runs to the end (2026-09-04)

### What happened

`/validate cleanroom` on the tree batch 30 repaired. **`analysis/run.sh` exited 0 from a
clean checkout** — both datasets, all 64 combinations, both distributions, every figure and
the last script in the tree. The first time in this project.

The repository was cloned at `c94e85f` (4 366 tracked files, no `.holdout_opened`, so the
seal released), `environment/chapenv` built from `environment/lock.txt`, and
`bash analysis/run.sh` run from cold. **41 677 s, 694 min.** The run was launched detached
and under `caffeinate -ims`; the session's wait process was killed **three times** and the
analysis was untouched by it.

Holding the host awake was the deliberate change from batch 27, whose 81 335 s was wall clock
across a sleeping machine and had to be discarded along with the cost finding inside it. It
costs nothing and turns the harness's own timing into data.

### The four attempts

Each was stopped one step further down the tree than the last:

| | reached | stopped by |
|---|---|---|
| batch 18 | 8 of 32 development rows | its own session dying |
| batch 25 | all 32 development rows | a recorded *selection* re-derived, at the freeze check |
| batch 27 | all of phase E | a recorded *figure* re-asserted, at the last script |
| **batch 31** | **the end** | — |

Batches 26 and 30 fixed the second and third. All three checks held on this run, and each
against a fresh draw that disagreed with the record: batch 26's reported the rule *would* now
choose six different pairs and the recorded eight ran; batch 24's returned *the frozen set is
intact*; batch 30's reported 32 drifted figures and 0 moved pairings and carried on.

### Batch 30's split, vindicated by the margin

The largest frozen-figure drift was **+0.051016** against a development noise band of
**0.048273** — *outside* it, where batch 27's +0.025673 had been inside its own 0.034944.

Batch 30 recorded considering and rejecting the obvious alternative, widening the tolerance
to the width of the band, on the grounds that the band is itself a draw of the same unseeded
model and *"a check whose threshold is redrawn on every run is not a check."* **Had it taken
that option, this run would have exited 1** — on a difference that is not a defect, in a tree
where nothing had moved. The reasoning was recorded as principle; this run made it a
consequence, and it could not have been tested any other way.

### What reproduced

**192 model-combination scores from models this project wrote, and not one moved**, on both
halves: persistence 32, climatology 32, ensemble 27, `hier_nb` 4, `boosted` 1 on each. The
unseeded reference moved in all 32 combinations of both halves, for each of its four repeats
and their mean. The reported pool returns **18.816872064690028** on development and
**76.73108261979166** on the holdout, digit for digit.

**2 248 of 4 366 tracked files came back byte-identical**, 2 118 differ in something computed,
**0** differ only in the repository path, 5 untracked — the same five `member_selection.json`
files batch 27 found, for setup combinations not re-run since batch 14 added the file.

The phase-E answer's counts are identical: 26 of 32 beat the reference, 27 of 32 beat both
required baselines, the reported model ranks 18th. What moved is the skill score, the
reference CRPS, the noise band, the rows inside it and the forks above it — the reference and
what divides by it, and nothing else.

The environment reported `matches environment/lock.txt exactly (174 packages)` with **0
colour-wrapped lines**: batch 27's own repair to `install-chap.sh`, verified from cold on a
session that also had colour forced, where batch 27's run had reported a mismatch that was
not one.

### The three files no clean-room run had ever compared

Batch 27 exited 1 **at** `pair_holdout_development.py`, so `holdout_vs_development.json`,
`holdout_vs_development.csv` and `fork_sensitivity_both.csv` were carried unchanged out of
the clone's index and its comparison reported them **identical** — wrong in exactly the way
batch 25's holdout half had to be read as absent. *A file that was never written cannot have
reproduced.* This run wrote them.

New script `cleanroom_phase_e_answer.py` classifies each scalar **reference-derived** or
**structural** by a field path listed in the script rather than by a heuristic:

- `holdout_vs_development.csv` — **544 of 640 cells identical**. Three columns moved, all the
  reference on the holdout side. **Every development column held**, including the two batch 30
  made read from the freeze.
- It also held `development_beats_all_baselines`, the one development figure batch 30 named
  as re-derived and therefore able to move. It did not move on this draw, which is not a
  guarantee about the field, and the caveat batch 30 wrote into the output stands.
- `holdout_vs_development.json` — 56 of 80 scalars identical; 14 reference-derived moved, 10
  structural, four of them the `frozen_pairing_verified` block reporting the drift.
- `fork_sensitivity_both.csv` — 129 of 221 cells identical; only `fork`, `stage`, `kind`,
  `owner` held.

### The finding that is not about reproduction succeeding

`agreeing_on_whether_the_fork_matters` came back **identical at 14**. The sets behind it did
not:

| | archived | clean-room |
|---|---|---|
| matter on both | `aggregate`, `family`, `provinces`, `trainingWindow` | `family` |
| matter on development only | `persistence`, `weighting` | `aggregate`, `weighting` |
| matter on the holdout only | `covariates` | `provinces` |

Four forks matter on both in the archive and **one** does here; the sets share only `family`.
The count is preserved because forks moved out of "both" into the single-dataset lists in
matching numbers, and a count cannot see that. The rank correlations underneath moved —
analyses 0.395747 → 0.368985, forks 0.678922 → 0.789216.

**Every check this project has compares values, so all of them call that field reproduced.**
Batch 18 wrote that these checks *"verify shape and never content — a number can be right and
its noun wrong, and nothing here looks at nouns."* This is the first demonstration of that gap
on a figure the analysis actually reports, and it came free from a run whose purpose was to
confirm that things match.

The consequence for batch 19 is narrow and concrete: where the write-up reports agreement
between the two datasets, it reports *which* forks agree and not only how many.

### Batch 27's holdout-band claim, corrected

Batch 27 reported the held-out band at 0.013410 against 0.014023 and concluded *"the figure
phase E is measured against is not the unstable one."* A third draw gives **0.050443** — 3.6×
the archive, and wider than any of the four development draws.

| | batch 15 | batch 25 | batch 27 | batch 31 |
|---|---|---|---|---|
| development | 0.021778 | 0.043084 | 0.034944 | **0.048273** |
| forks above it (of 17) | 6 | 3 | 3 | **3** |
| holdout | 0.014023 | — | 0.013410 | **0.050443** |

Corrected in the check and in `readme-at-start.md`, which carried the claim too. It does not
reopen the human's 2026-09-03 decision that the count stands as the headline; it adds a fourth
development draw and removes an exemption batch 27 had granted the holdout.

### Cost

| | rows | planned | actual | ratio |
|---|---|---|---|---|
| development | 24 | 7 470 s | 9 882 s | 1.32 |
| development, less one row | 23 | 7 393 s | 6 671 s | 0.90 |
| holdout | 32 | 7 468 s | 7 394 s | **0.99** |

The holdout's 0.99 replaces batch 27's `ratio 8.814`, which that batch flagged as contaminated
and refused to report — correctly, as the same rows awake come in at 0.99 against an estimate
frozen before any of them ran.

**One row is 37× its archived duration and nothing else is.** `yearVariance_shared`: 3 210.7 s
against 85.6 s, its ensemble step 1 508 s against 62 s, 188.4 s per split against 7.7 —
producing **CRPS 18.840, identical**, from the same seed and the same four members. Every
other row on both halves is within about a factor of two of its archived time. It was the
**last** development row, not the first, so it is not a cold environment build. The record
does not say what happened and it is reported as an unexplained timing outlier. Its log is
preserved in the artefacts so a reader can check that.

### The last defect, in a script that had run three times

`cleanroom_holdout_reproduction.py` hardcoded `install_chap_sh_reported: "DOES NOT MATCH
environment/lock.txt"` — which batch 27's own repair had since made false — and named its
payload key `why_the_run_stopped`, with `rows_it_stopped_on` inside it, on a run that exits 0.
The environment block now reads the reported line out of `install_env.log`, and the key is
`the_frozen_figure_comparison` with `rows_whose_frozen_figure_drifted`. **No arithmetic
changed.** The same test batch 30 applied decides it: it costs nothing, needs no new data, and
the alternative is a record that describes a different run than the one it reports on.

The defect family batch 24 opened — an artefact recorded once and then recomputed at run time
— is closed at four members. All four were found by running the whole thing from nothing;
none by reading the code. Two code reviews and an outsider test found none of them.

### State

Nothing under `analysis/` was run, edited or re-run. The clean-room ran in a throwaway 18 GB
clone, whose outputs were copied to `AI-generated/validation/26-09-04_cleanroom-artefacts/`
before it was discarded. `manifest_holdout.csv` is `fc9d1a16…`, as batch 15 froze it.

**Batch 19 may now state that `analysis/run.sh` reproduces this analysis from a clean
checkout**, with the qualification in the same breath: our models are bit-identical, the
unseeded reference is not, and every figure dividing by it is a draw.

`/validate invariants` passes, all ten. Added no batches. **Remaining order: 28, 20, 19.**

---

## T29 — batch 28: the pool's second path stops depending on what is on disk (2026-09-04)

### What happened

The last of the three defects batch 26 named, and the one it declined to fix in passing.
`check_pool.py` rebuilds each pool from its members' **own** stored evaluations — the files
each member produced when it was run on its own, through its own node — and it found them by
globbing the member's sibling result directories for a run whose `configuration_sha256`,
dataset hash and backtest flags matched, then taking `found[0]`.

The configuration test is right and is unchanged. The tie-break was not a tie-break: it was a
record of which combinations existed on disk when the script happened to run. Two strengths
of the same defect:

| | archived | re-run today |
|---|---|---|
| `main`, the persistence member | `main` | `climatology_frozenWindow` |
| `main__holdout`, `mean_crps_rebuilt` | `null` | **76.646** |
| `main__holdout`, `not_done_because` | *"no stored evaluation of ['hier_nb', 'boosted']"* | `null` |

**For five batches the record said the second path behind this project's headline held-out
result could not be run.** Batch 16 ran the holdout's main row before the holdout's family
rows, so at that moment candidate 1 and candidate 2 genuinely had no separate evaluation of
2010 — and the file recorded that as a property of the pool.

### Why a tie-break alone was not enough, which is the batch's methodological point

Our candidate families are evaluated on their own **only** under the family fork's own
combination — `family_hierNB`, `family_boosted` — because the main path runs the pool. Those
are stability rows. So on a run of `analysis/run.sh` from nothing, every pool is checked hours
before the runs it needs exist. Batch 31's clean-room run shows it: 13 `pool_check.json` files
came back changed, `main` among them.

So **making the derivation deterministic is not the same as making it right**. A rule over the
combination names is deterministic given a set of directories, and what it ranges over is
produced by the run it sits inside. A check that depends on its own position in the run is a
report on progress. That is the third instance of batch 24's family: batch 24, *a value that
records history must not be derived at run time*; batch 26, *a derivation over the filesystem
is a claim about when it ran*; this one, *and a deterministic derivation over it is still one*.

### What was built

**The rule** — `combos.tokens()` and `combos.implies()`, beside the `__holdout` suffix in
`analysis/scripts/lib/combos.py`, which is where a combination's name is read. `check_pool.py`
now names, among the evaluations matching on configuration, dataset and flags: this
combination's own run of the member where there is one; otherwise the run that moved the
**fewest forks among the combinations this one implies**, ties broken by name — where implying
means every fork the candidate moves is one this combination moves too, family tokens aside.
Each file records which clause chose it, in a `chosen_by` field. The list of candidates the
rule chose from is deliberately **not** written into those files: that list is a function of
what is on disk, and putting it there would return the dependence the change removes.

**The sweep** — `analysis/05_stability/scripts/reconstruct_pools.py`, the last step of that
node's `run.sh`. For every combination with a pool it asks `check_pool`'s own rule — imported,
never restated — which evaluations should be named, and re-runs `check_pool.py` as a
subprocess where the file names others. It is the shape this node already has twice, in the
second passes of `plan_manifest.py` and `collect_conclusions.py`. It rewrote 49 files in
2 min 28 s; the second invocation rewrote none, took 1.2 s and returned a byte-identical
summary.

### What changed in the files, computed rather than eyeballed

`AI-internal/useful-scripts/pool_check_rewrite.py` flattens `HEAD`'s copy of every file and
the new one to their leaves and classifies each differing key
(`26-09-04_poolCheckRewrite.json`): **51 files, 43 changed in naming and the added field
only, 4 gained the full reconstruction, 4 gained a member match, 0 numeric changes to values
that existed before, 0 rows lost anything.**

The four that gained a reconstruction are all held-out rows: `main__holdout` 76.646 against
76.731, `climatology_frozenWindow__holdout` the same figures, `persistence_negBinomialFloor__
holdout` 77.414 against 77.504, `weighting_crpsWeighted__holdout` 77.610 against 77.746.

### What the holdout row now says

The residual is **0.085** over 192 cells, the same relative size as development's 0.016 over
371. **The pool beats its best member on 2010 by 4.767 CRPS** — climatology 81.498,
candidate 2 81.679, candidate 1 84.707, persistence 128.052 — and **the prediction registered
before any of it ran fails there in both halves**, where on development one half held: the
pool's 10–90 coverage is 0.755 against candidate 2's 0.854, so the clause that a linear pool
covers at least as widely as its widest member does not hold on the held-out year.

**Eleven of the 51 pool rows can be reconstructed; forty cannot**, and no order of execution
would help — a row that moves a fork inside a member has no separate run of that member under
the configuration the pool gave it. `05_stability/results/pool_reconstruction.json` names
them with the reason, so the absence is a recorded decision.

### The defence

`AI-internal/useful-scripts/check_reconstruction_defence.py` puts four states to the sweep on
the live tree, restoring each: the record batch 16 left (rewritten to 76.646), a file already
right (not re-run, not touched), a missing file (produced), and `covariates_rich`, which no
order of execution could reconstruct (left saying so, still naming candidate 1 as the member
it lacks). All four pass, every file back to its committed digest, `analysis/` clean by git's
own account.

### Why this does not reopen the holdout

§3 as the human clarified it on 2026-09-01 binds `manifest_holdout.csv`. It is untouched, the
set is still 32, no model was re-fitted, no evaluation recomputed and no reported score moved.
What ran is a check over batch 16's own stored evaluations — the standing this project already
gives a clean-room re-run of the whole phase-E half, which batches 25, 27 and 31 each did. The
reading is recorded in the plan's §4b rather than assumed.

### State

`done — produced`. Claims **C40** and **C41** added; all ten invariants hold. **20 and 19 are
the only open rows**, in that order.

## T30 — batch 20: the external check, and the drop replicates (2026-09-04)

### What happened

The plan's §4 named `tha` and `vnm` as an optional external check; the human confirmed it on
2026-08-31 and moved it ahead of the release so the case write-up could use it. This is that
batch. The reported model — candidate 3, the linear opinion pool, at the configuration the
tree already carries — was run **unchanged** on the Thai and Vietnamese files of the same
harmonisation, in the same two arrangements Laos is reported in and on the same months.

Four rows: `main__vnm`, `main__vnmFinal`, `main__tha`, `main__thaFinal`. Each runs the whole
reported pipeline — every setup fork at its main child, the assembler, both required
baselines, the reference model's four unseeded repeats, the pool and the scoring chain — and
**no fork moves in any of them**. What differs is the file underneath.

### The result

| country | development | final year | drop | beats reference | reference's own band |
|---|---|---|---|---|---|
| Laos | +0.1485 | +0.0868 | −0.0617 | yes, yes | 0.565 / 1.296 CRPS |
| Thailand | +0.0856 | +0.0197 | −0.0659 | yes, yes | **0.032** / 0.124 |
| Vietnam | +0.0852 | **−0.0862** | −0.1714 | yes, **no** | **7.082** / 0.513 |

Six of six beat both required baselines. All three drops exceed the two reference bands they
are measured against, taken together.

**Three things this establishes.** The drop is not about 2010 alone — the final year is harder
in the same direction in two countries the model never saw. The country the model was
developed on is the one it scores highest on, by 0.063, while the two independent countries
agree to 0.0004. And what the backtest can resolve is a property of the country: the same
unseeded reference model at the same configuration has a re-run spread that varies by a factor
of **215** across three countries of one harmonisation, so Vietnam's margin falls inside its
own noise floor while Thailand's identical margin is thirty-five times its band.

**What it does not establish, and the files say so in their own text.** The two sibling final
years were not held out from anything, because nothing was developed on those files — so the
replication is evidence about the year, not a second measurement of optimisation inflation.
And the 0.063 development gap is not attributable to development alone: the three countries
differ in province count, burden and reporting system, and nothing here varies development
while holding the country fixed.

### What had to be built

`Archive/sibling-datasets/` (six files, same pinned commit as the Lao ones, so a difference
between countries is not also a difference between harmonisations);
`analysis/01_data/03_siblings`, the only node licensed to read them, which cuts each country
onto the Lao calendar and checks against chap-core's own splitter that both arrangements land
on 2008-01..2009-12 and exactly 2010; and `analysis/06_external`, which plans, runs and
reports the four rows.

**Thailand is truncated from its own 1993–2022 record.** That is the node's judgment call and
its basis is in `claim.md`: the check asks whether the Lao result holds in another *place*, so
the years are held fixed. Its other twenty-two years are the material for whether 2010 in
particular was hard, and are left unspent as a recorded decision.

### Three moves rather than three copies, each verified before anything ran

- **`combos.py`**: the four sibling datasets are *dataset suffixes* on the mechanism
  `__holdout` already uses, because the analysis does not move and the country does. With them
  the **scheme file became a property of the dataset**, retiring a constant repeated in six
  setup scripts — the fifth instance of the shape this project keeps correcting, caught before
  it bit. All six re-run under combinations they had already produced: byte-identical.
- **`05_stability/scripts/lib/driver.py`**: the step-list construction and row execution moved
  out of `run_manifest.py`, because a check running a second implementation of the pipeline
  would measure the code and not the model. Dry-run output byte-identical for all 32
  development rows and the holdout set.
- **`reconstruct_pools.py`**: reads the rows it settles off the two manifests rather than off
  the directories on disk. Without it, a node running *after* `05_stability` whose rows are
  pools would have made batch 28's own repair order-dependent again, one node further out.
  Verified with all four external pools present: `pool_reconstruction.json` still `977f3302…`,
  no `pool_check.json` rewritten.

`/validate invariants` gained a **third planned manifest rather than an exemption** — the
`combos` check closes the combination space, and a directory it is told to excuse is a check
that has stopped meaning anything — and its manifest-node exclusion is now derived from where
the manifests are rather than listed.

### The budget

Six hours, set before anything was costed, at what `analysis/run.sh` already costs. Planned
3.14 h, actual **1.81 h**, ratio 0.58, nothing cut, and the cut order (whole country pairs
from the bottom) recorded although it never bit. Phase D's two halves came out at 1.00 and
1.15; this one is out by a factor of two, because the unit — seconds per evaluated cell,
measured on 192 Lao cells — does not transfer to 1 824 Thai ones. **The total being right
twice was a property of estimating a set against itself.**

### Recorded as not done

The pool's independent reconstruction is unavailable on these datasets: a member is evaluated
on its own only under the family fork's own combination, and this check moves no fork, so no
order of execution would produce the missing runs. Different from batch 28's ordering defect,
and `results/pool_reconstruction_external.json` says which it is and what it would have cost
(two more model evaluations per dataset).

### A fourth instance of batch 24's family, found by asking rather than by a run failing

`plan_external.py` as first written recomputed the plan it had committed. Its estimate
divides a measured wall-clock duration — the seconds the held-out `main` row took, out of
`05_stability/results/run_status_holdout.csv` — and `05_stability/run.sh` rewrites that file
one step before this node runs. From a clean checkout the plan would have come back with a
different estimate in every row, and "committed before the rows ran" would have been a claim
about a file that had since been rewritten.

Same family as batch 24's frozen manifest, batch 26's tier-1 order and tier-2 selection, and
batch 30's frozen development figure — each of which was found by a clean-room run exiting
non-zero. This one was found by asking what the next such run would do. Same repair: rows are
structural and a disagreement is fatal before anything is written; the estimate is a
measurement and a drift goes into `results/external_plan_check.json`.
`check_external_plan_defence.py` puts four situations to it, all passing, the drifted-unit
one using the size and direction batch 31's clean-room run changed that duration by.

### Files, and what a later session needs

New: `AI-internal/data-acquisition/fetch_sibling_datasets.sh`, `Archive/sibling-datasets/`,
`analysis/01_data/03_siblings/`, `analysis/06_external/`,
`analysis/05_stability/scripts/lib/driver.py`. Changed: `analysis/scripts/lib/combos.py`, six
setup scripts, `run_manifest.py`, `reconstruct_pools.py`, `check_invariants.py`,
`analysis/run.sh`, `analysis/README.md`, `analysis/claim.md`, `analysis/01_data/claim.md`,
three READMEs, `folder-structure.md`, `readme-at-start.md`, the plan. Claims C42–C47.

**Two things batch 19 has to carry.** `analysis/run.sh` now calls `06_external`, so batch 31's
clean-room verification predates this node and does not cover its scripts — a
`/validate cleanroom` would settle it at the cost of 1.81 h on top of eleven, and the
qualification is written into `readme-at-start.md` either way. And the release must not repeat
the sentence this batch corrected: the 0.57 CRPS floor is a property of the Lao dataset, and
the same measurement gives 0.032 on Thailand and 7.082 on Vietnam.

Fixed in passing, while updating the same index: the plan's reports section had no entry for
batch 28.

## T31 — batch 19: the case, the report, and the release that waits (2026-09-05)

### What happened

The last batch the plan named, and it produced all three of its deliverables and then declined
to take the fourth step. The case write-up, the reproducibility report and the release are
done; **the push is not**, because batch 19's own outsider check found a defect in forty
committed files and a release must not claim more than its checks support.

### The three deliverables

**The case write-up** (`Human-AI-collaboration/manuscript/26-09-05_illustratingCase.md`) is
the document that could be lifted into the manuscript's *An illustrating case* section, and it
supplies what that paper's Appendix supplies for the case this one replaces: the worked
claim-tree skeleton in dengue terms, the seventeen forks in four families, and the judgment
about where this setup was more trouble than it was worth. Written through Rule 9's two steps,
with a sidecar mapping every passage to its claims or to what kind of statement it is instead
— design, record, or judgment.

**The reproducibility report** has ten entries under *what does not hold*, four of them found
while writing it. Every count comes from `repro_inventory.py`, and writing that script caught
two things the report would have got wrong: walking `AI-internal/useful-scripts/` counted the
clean-room's own clone as 15 078 machinery files, and the claim parser counted the collection's
fenced example block as a 48th claim with a broken pointer.

**The release** is scanned and assembled. No credential in 4 840 tracked files or 8 875 history
blobs; all five archived directories carry a licence statement after the human set Creative
Commons for the two that had none; everything Rule 10 names is present; the 23 paths not taken
all have an entry point.

### The clean-room, and the claim it withdrew

`analysis/run.sh` exited 0 from a clean checkout in 14.87 h — the first run to reach the end
with `analysis/06_external` in the tree, which the reproducibility report had named hours
earlier as the gap in the previous verification.

**207 of 207 scores from models this project wrote came back identical.** 340 of 345 reference
scores did not. That is the project's central claim with its qualification attached.

**All four defences held from cold**, including batch 20's external plan on its first cold
test: the cost unit moved from 2.2568 to 2.1505 s/cell, exactly the drift the defence was
built for.

**And it withdrew batch 20's band clause.** False for Laos (predicted) and false for Thailand
(not predicted, and for a different reason — its drop halved rather than its band widening).
Direction, ordering and the sign of the Vietnamese loss survive; the quantification against
the reference's own noise does not.

### The outsider check

Two agents. **One died to an account spend limit**, and it was the one asked to write into the
tree — the half that in batch 18 found the freeze rule contradicting the `combos` invariant.
Recorded as not run.

The other found seven things, of which the two that matter most are:

- **The resolution yardstick had been applied to one number out of six.** The held-out
  headline is 0.94 standard errors from the reference, below the project's own 1.03 line, and
  no document said so. C48.
- **`choose_weighting.py` records a six-member pool where four ran, in 40 of 47 combinations.**
  Fifth instance of the fork-blindness family. No score moves; the registered prediction is
  written on a premise the file contradicts.

### What a later session needs

**Batch 32** fixes `choose_weighting.py`, and its defence is built against **this clean-room
run's own output** — `AI-generated/validation/26-09-05_cleanroom-artefacts/`. That is why it
was not fixed in batch 19: fixing it while the confirming evidence was still being gathered
would have thrown the evidence away. Batches 26, 30 and 28 each worked this way.

**Batch 33** creates the remote and pushes. Both human answers are recorded in the plan's §4b
— Creative Commons for the two archived directories, and the home-directory path staying in
the run logs — so batch 32 is its only remaining blocker. The agent still asks before the push.

**Unestablished:** whether an outsider following these instructions can still add an
alternative to the tree. That check has not run since batch 18.

### What `/log-tasks` found afterwards, and why it is here rather than in a T32

Running `/log-tasks` after the batch closed did what its step 4 asks — check that what the
work changed is recorded where it should be — and found three gaps, all of them batch 19's own
housekeeping rather than new work. They extend this entry rather than opening a new one.

- **`AI-generated/README.md` named `reproducibility-report/`**, a folder that has never
  existed; the folder is `repro-report/`. A stale path in the index of the directory it
  indexes, written when the folder was still hypothetical.
- **`release/` was missing from that README entirely**, both from its table and from its
  *Currently here* list.
- **Neither outsider record had a provenance section** — not batch 19's, and not batch 18's,
  which had gone without one since 2026-08-31. `AGENTS.md` §8 asks for one section per file in
  any folder holding generated documents.

The outsider entry is the interesting one to write, because **it is the one record in this
repository that cannot promise reproduction**. Re-running an outsider check at the same commit
with the same task will not return the same findings: the agents are not seeded, are not the
same agents, and what they look at is not determined. What the record fixes is the
*conditions* — the commit, the task verbatim, and what the agent was and was not given — so a
reader can judge whether the check was fair and run another. It also records that batch 19's
run is **incomplete**, one agent having been killed by an account spend limit.

The plan-drift entry in the same README still quoted §4b's decision count as 169, which is
what batch 18 measured; batch 19 remeasured it at 247. Both figures are now there with their
batches, because the point of that entry is that the count grew.
