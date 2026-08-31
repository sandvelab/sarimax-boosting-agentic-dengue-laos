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
