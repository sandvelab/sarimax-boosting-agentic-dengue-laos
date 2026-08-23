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
