# Batch 7 — erect the tree

Generated from [[26-08-22_dengueForecastingCase]] — iteration 7

**Phase B · Status: done — produced · Executed 2026-08-26**

---

The batch that moves the project inside the claim tree. From here, a result produced outside
it does not exist.

`analysis/run.sh` now reproduces the whole chain: the data, the common setup every model
faces, two baselines of our own, the field's reference model four times over, the scores at
every resolution, the paired comparison, two figures with their data, and the project's
conclusion as a computed file. Twenty minutes end to end, of which eighteen are the emulated
reference.

The batch also answers the question batch 4 left open and batch 5 called the most expensive
thing to discover late — **whether a paired per-cell comparison on 371 cells can separate two
models** — and the answer changes what phase C has to aim at.

## 1. What the tree looks like now

```
analysis/                       [sub-analyses]   scripts/conclude.py
├── 01_data/                    built in batch 3
├── 02_setup/                   [sub-analyses]   scripts/assemble_setup.py
│   ├── 01_population/          [alternatives → a_static]
│   ├── 02_trainingWindow/      [alternatives → a_from1998]
│   ├── 03_provinces/           [alternatives → a_chapFilter]
│   └── 04_retrain/             [alternatives → a_once]
├── 03_models/                  [sub-analyses]   scripts/lib/chap_eval.py
│   ├── 01_baselines/           [sub-analyses]
│   │   ├── 01_persistence/     [alternatives → a_empiricalChange]
│   │   └── 02_climatology/     [alternatives → a_expandingWindow]
│   └── 02_reference/           EWARS-csd, pinned by digest, four repeats
└── 04_score/                   [sub-analyses]
    ├── 01_collect/             per-cell scores, from chap-core's own metrics
    ├── 02_aggregate/           [alternatives → a_unweighted]
    └── 03_compare/             leaderboard, paired comparison, two figures
```

Twenty nodes, seven of them forks, each fork carrying its main-path child only. `05_stability`
is batch 12's and `03_models/03_candidate` is batch 8's; `06_holdout` does not exist until
batch 16, because a node that reads the sealed file must not be runnable while the seal is on.

**One child per fork is the plan's phase-B scope and it is a deliberate reading.** Batch 5's
design says batch 7 builds everything, and the plan's own batch-7 paragraph says "`02_setup`
and `04_score` with one child per fork". The narrower reading was taken: a sibling that exists
but does not run is worse than one that does not exist, because `/validate invariants` would
pass on it and the tree would advertise an alternative nobody could execute. The siblings
arrive when the code that runs them does.

### The forks that exist, and the two that batch 5 did not have

| Fork | Node | Main path | Siblings, unbuilt |
|---|---|---|---|
| Population column | `02_setup/01_population` | `a_static` | `b_backcast` |
| Training window | `02_setup/02_trainingWindow` | `a_from1998` | `b_from2003` |
| Province inclusion | `02_setup/03_provinces` | `a_chapFilter` | `b_dropSilent`, `c_mergeVientiane` |
| Retrain policy | `02_setup/04_retrain` | `a_once` | `b_everySplit` |
| Headline weighting | `04_score/02_aggregate` | `a_unweighted` | `b_populationWeighted`, `c_caseWeighted` |
| **Persistence's uncertainty** | `03_models/…/01_persistence` | `a_empiricalChange` | `b_negBinomial` |
| **Climatology's window** | `03_models/…/02_climatology` | `a_expandingWindow` | `b_trainOnly` |

The first five are batch 5's inventory. The sixth is batch 6's, found by building something.
**The seventh is this batch's, and it is worth a sentence about why it exists and why its
neighbour's does not.** A persistence forecast is a point, so a predictive distribution has to
be wrapped around it and how to do that is a real choice. A climatology forecast is a set of
past Julys, which is a distribution already — so that fork does not arise. What does arise is
*which window* estimates it: chap-core fits once but hands `predict` an expanding historic
frame at every split, so the seasonal table can be frozen at the training period or
re-estimated at each split. The main path re-estimates, on the grounds that the persistence
baseline's anchor already comes from the historic frame and a baseline artificially deprived
of two years would overstate whatever eventually beats it.

Building "a fork for each baseline" would have been tidier and would have asserted that the
two contain the same kind of choice. They do not.

## 2. The common ground, and one defect it caught

`02_setup` is four forks in sequence, each handing the dataset on, with the node's own script
assembling their output into the one dataset and the one set of evaluation flags every model
reads. Models never reach into a fork's directory and never learn how many stages the setup
has.

Each stage finds its input by **searching for the one child of the previous fork that has
results under this combination**, never by naming a child. That is what will let the stability
driver swap `a_static` for `b_backcast` without a single downstream script changing, and it is
the mechanism batch 5's design needs but does not name.

On the main path all four stages are the identity, and **that is checked rather than claimed**:
`setup_spec.json` carries `identical_to_development_file: true`, so the file every model faces
is the archived development file byte for byte.

That check exists because the first version failed it. The stages read the dataset with pandas
and wrote it back, which is the identity numerically and not at the level of bytes: the target
column holds integer counts and blanks, so a parser round trip returns `0` as `0.0`. Three
stages were declaring `dataset_transform: identity` while producing a different sha256 — a
specification saying something untrue. The stages now carry the dataset as text lines and
filter it with a predicate on lines, which is the choice batch 3 made for the partition and
made for this reason. **It was caught by comparing two hashes while waiting for a run**, which
is the kind of thing nothing finds unless something compares it, and the comparison is now in
the file.

The setup also recomputes, from the dataset and batch 3's stored scheme, that the metric is a
mean over **16 provinces and 371 cells**. It agrees with batch 3 and with what the evaluation
produced. Nothing about the metric's denominator is a constant typed into a script.

## 3. The models, and one route to the platform

Three models ran, all through **one** piece of code: `03_models/scripts/lib/chap_eval.py`,
which reads the dataset and every backtest flag from `02_setup`, hashes the model's own files
into its spec before the run, times the run and writes the cost to a file.

That is a structural answer to a constraint the plan states for phase C — *no candidate is
compared on a metric computed a different way*. A runner copied per model is a set of copies
that will drift, and the drift would show up as a model difference. `scripts/lib/` is a
subdirectory, so `node.py` does not put it in any node's `run.sh`; the steps are the
one-screen runners at the model nodes, which say what model they are running and nothing else.

**The persistence model moved into its node with its git history and without a byte
changing**, and reproduced batch 6's mean CRPS to the last digit: 24.879338288409706 both
times. That is the plan's requirement that batch 7 route the vertical slice through the tree,
and it is also evidence that the tree added no arithmetic of its own between the platform and
the number.

**The seasonal climatology baseline is new.** Its `MLproject` and `uv.lock` have the same
shape as the persistence model's, and the two lockfiles resolve to the identical six
packages, differing only in the project name — so the two baselines differ in what they
compute and in nothing else.

**The reference runs four times.** It is unseeded and cannot be seeded; the project's
conclusion divides by its CRPS, so an unaveraged denominator would carry a wobble the size of
the effects the stability run exists to detect. Every repeat is kept and the scoring node
forms the per-cell mean beside them.

| | Route | Cost, one backtest | Seeded |
|---|---|---|---|
| persistence | `MLproject`, `uv_env`, native | 28 s | no randomness at all |
| climatology | `MLproject`, `uv_env`, native | 28 s | no randomness at all |
| reference | chapkit service, amd64 image emulated | 241–285 s × 4 | unseeded, unseedable |

Batch 4's conclusion that implementation and not evaluation binds this project is confirmed
at both ends. The reference cost more per repeat than batch 4's 149 s, which is machine load
on the day rather than a change in what is computed.

**Both baselines are byte-identical across two independent runs** — per-cell scores, model
listing and fitted model (`AI-generated/determinism-checks/model_determinism.json`). Rule 6 is
satisfied for what this project builds and cannot be satisfied for what it is measured
against, and both halves of that are now demonstrated rather than argued.

## 4. What everything scored

Every figure below is read from `analysis/04_score/`, which is a `groupby` on one per-cell
file, which is written from chap-core's own registered metrics. This project implements no
metric.

| Model | Mean CRPS | MAE | Coverage 10–90 | Coverage 25–75 | Skill vs reference |
|---|---|---|---|---|---|
| **reference** (mean of 4) | **22.098** | 28.902 | 0.804 | 0.602 | 0 |
| reference, repeat range | 21.820 – 22.385 | | 0.782 – 0.817 | | ±0.013 |
| **climatology** | **24.337** | 30.620 | 0.650 | 0.542 | **−0.101** |
| **persistence** | **24.879** | 29.073 | 0.666 | 0.491 | **−0.126** |

371 cells, 16 provinces, 8 splits, 1 000 draws per cell for every model.

**The two baselines are 0.54 CRPS apart, which is inside what this evaluation resolves.** The
honest reading is that knowing the season and knowing the last observation are worth about the
same here — not that one is better.

### The reference's advantage is entirely at longer lead times

| Lead time | persistence | climatology | reference |
|---|---|---|---|
| 1 month | **16.43** | 22.31 | 16.54 |
| 2 months | 24.76 | 23.73 | 21.97 |
| 3 months | 33.45 | 26.97 | 27.79 |

**At one month, persistence is level with the reference** — 16.43 against 16.54, a difference
of a tenth of a CRPS on a model whose own re-runs move by half a one. What the reference buys
is the two- and three-month horizons, which is where a random walk must fail and does. The two
baselines cross each other: persistence is much the better at one month and much the worse at
three, which is the shape you would predict and had not been measured.

This matters for phase C because the evaluation scores all three horizons together. A
candidate that improves on the one-month forecast is improving on the part where a trivial
baseline already ties the field's model.

### The aggregate hides a great deal, and one of the things it hides may flip the ranking

Mean CRPS per province, ordered by the cases in the cells the score is averaged
over — 2008-01 to 2009-12, not the whole record:

| Province | Cases in the evaluated cells | persistence | climatology | reference |
|---|---|---|---|---|
| LA-VT Vientiane Capital | 3 707 | **59.78** | 80.18 | 92.81 |
| LA-CH Champasak | 2 431 | 41.62 | **38.37** | 52.25 |
| LA-SL Salavan | 1 455 | 58.60 | 52.10 | **38.44** |
| LA-LP Luang Prabang | 1 336 | 91.60 | 43.23 | **47.39** |
| LA-SV Savannakhet | 192 | 12.69 | 43.52 | **9.67** |
| LA-XA Xaignabouli | 125 | 3.95 | 5.90 | **3.26** |
| LA-PH Phongsaly | 0 | **0.00** | **0.00** | 0.05 |

(The full sixteen are in `crps_by_location.csv`.)

**The reference is beaten by both baselines in the two provinces carrying the most evaluated
cases**, and wins comfortably almost everywhere else. That is why it wins only **53 % to 56 %**
of cells: at the level of an
individual province-month the three models are close to a coin flip, and the reference's
aggregate advantage comes from a minority of cells.

It also means **the headline weighting fork may be consequential rather than cosmetic**. The
unweighted mean over cells gives Phongsaly, with no reported case in twelve years, the same
weight as Vientiane Capital. A case-weighted or population-weighted mean would move weight
toward exactly the provinces where the reference does worst. Whether the ranking flips is not
computed here — that is the sibling node's job and it is not built — but batch 5 costed the
weighting fork as the cheapest in the project, and this is the first evidence that it may also
be among the most informative. Batch 12 should not let it fall below the line.

**Calibration separates the models more cleanly than score does.** The reference is close to
nominal in the tails (0.804 against 0.80) and much too wide in the middle (0.602 against 0.50).
Both baselines are the mirror image: near-exact in the middle, far too thin in the tails. And
the reference's per-province coverage never drops below **0.542**, while persistence's reaches
**0.042** and climatology's **0.125**. A single coverage figure over sixteen very unequal
provinces is an average of opposite failures, which batch 3 predicted and batch 6 measured on
one model; here it is measured on three, and the *uniformity* of the reference's calibration
is the clearest thing that distinguishes it.

## 5. The question this batch existed to answer

Batch 4 measured the split-to-split standard error of the reference's own CRPS at 5.65 —
recomputed here as **5.68** — and argued that a paired per-cell comparison would be far
tighter, without being able to compute one. Batch 5 made computing it batch 7's reason for
existing, because if the answer were no, phase C's design changes rather than phase D
discovering it.

It is tighter. It is not tight enough.

| | climatology | persistence |
|---|---|---|
| mean paired difference vs reference | **+2.238** | **+2.781** |
| sd of the per-cell differences | 25.74 | 39.40 |
| standard error, cells treated as independent | 1.336 | 2.045 |
| standard error, clustered by province | 2.684 | 3.925 |
| standard error, clustered by split | **1.919** | **2.985** |
| standard error, split-level comparison (8 numbers) | 2.058 | 3.139 |
| cells where the model beats the reference | 44.5 % | 46.9 % |
| splits where the model beats the reference | 2 of 8 | 3 of 8 |

Pairing takes the standard error from 5.68 to between 1.3 and 3.0 depending on how honestly
the correlation between cells is treated — a factor of two to four. But the differences being
measured are 2.2 and 2.8, so **both are inside two standard errors of zero on every one of
those readings.** Neither baseline has been shown to be worse than the reference, despite
being worse by a tenth of its score.

**So the development backtest resolves differences of roughly 4 CRPS.** That is wider than the
entire gap between the persistence baseline and the reference. It is the number phase C has to
plan against.

### The noise floor, computed rather than assumed

The reference is unseeded, so two of its repeats differ by its sampler and by nothing else.
The same paired statistic between two repeats of the same model is therefore a difference of
exactly zero, contaminated only by the sampler — which makes it the comparison's resolution,
in the comparison's own units, on the same cells.

Across the six pairs of four repeats, the mean paired difference ranges from **−0.467 to
+0.565**, with clustered standard errors of 0.13 to 0.48. **Nothing below about 0.57 CRPS can
be attributed to a model at all.** Batch 4 estimated ~0.4 from the spread of aggregate scores;
the paired form gives a slightly larger and much better-founded figure.

### What this changes

1. **A candidate that beats the reference by one or two CRPS will not have been shown to beat
   it**, and the report must say so rather than round it up. The plan settled before any number
   existed that significance is not attainable here and is not to be implied (§4b, human-set);
   this is the measurement that makes the settlement concrete.
2. **Phase C's stopping rule survives and its threshold is about right.** It stops when the
   leaderboard's best moves by less than 0.4 CRPS in a batch. The measured floor is 0.57, so if
   anything the rule is slightly too permissive; it is left where batch 5 fixed it, because a
   stopping rule adjusted after seeing a number is not a stopping rule, and the difference is
   small.
3. **Calibration and lead-time structure should be reported beside CRPS in phase C, not after
   it.** They separate these three models where the headline mean does not, and a candidate
   selected on mean CRPS alone would be selected on the least discriminating thing measured.
4. **The paired machinery is in the tree and costs seconds.** Every phase-C candidate gets the
   comparison automatically by having run.

Two figures carry this, with their plotted values and their pre-aggregation values beside
them: `fig_paired_vs_reference.png` (three readings of the comparison, with the reference's
own repeat band shaded) and `fig_crps_by_location.png` (score and calibration per province,
ordered by burden).

## 6. The conclusion is a file

`analysis/scripts/conclude.py` writes `results/$COMBO/conclusion.json`: the skill score, raw
CRPS, both coverage figures, the paired difference, the resolvable floor. **Nothing anywhere
else in the repository states the conclusion**, so nothing can drift from it. Phase D's driver
calls the same script once per combination, so the development spread will be a set of these
files rather than a second implementation of the analysis.

For this combination it records `skill_score: −0.101`, and it records
`candidate_exists: false` — the project has baselines and no candidate, so the file says in as
many words that a baseline is standing in for one. Which model is "ours" is resolved from the
tree: once `03_models/03_candidate` exists, the script reads its `main-path` field, so
`/node promote` changes the reported conclusion and the commit that promotes it is the record
of when the reported model changed.

Writing it now, with a placeholder it names as a placeholder, is the vertical slice's argument
one level up: a contract first exercised when it has to carry a real result is a contract first
tested at the worst moment.

## 7. Two things settled that had been open since batch 2

**The environment's Docker layer builds.** It had never been built — no daemon was available on
the machine that wrote it — and it was carried as a specification through five batches. It
builds in about seven minutes to 1.62 GB, giving CPython 3.13.0 and `chap 2.1.0`.

**The clean-room check ran inside it**, and reported differences rather than success. Thirty of
the thirty-one files `01_data` produces are byte-identical, `02_setup`'s three are
byte-identical, and both baselines' per-cell scores match exactly. Two differences, both real:
one pre-aggregation file differs by one unit in the last place on two rainfall values, because
pandas' default CSV float parser is fast rather than correctly rounded and the macOS and Linux
wheels of the same version disagree; and one aggregation differs by 2.8 × 10⁻¹⁴ from summation
order. **A lockfile pins packages, not the compiled code inside them** — which will matter in
phase C, when the first candidate reads a climate covariate, and the fix is
`float_precision="round_trip"`.

The check also cannot cover the reference node, and that is structural: the reference is
distributed as a container and the node starts one, so verifying it from nothing needs a Docker
daemon outside the clean room. Recorded so that `/release` does not claim more than the check
supports.

Full record: [[26-08-26_cleanroom]].

## 8. What went wrong, kept

**An early clean-room attempt mounted the repository writable into the container** and wrote
symlinks into `environment/chapenv`, pointing the host's analysis environment at a path that
exists only inside the image. The environment is a build artifact and `install-chap.sh` is the
documented recovery, so the damage was recoverable. The later attempt copies the repository
into the container and mounts the source read-only.

**The recovery is what found the batch's most serious defect.** Rebuilding the environment
produced a *different package set* from the one pinned three days earlier — `click 8.5.0` where
`lock.txt` said 8.4.2, and a dozen other moves. `install-chap.sh` resolved `chap-core==2.1.0`
afresh and then *wrote* `lock.txt` from what it got, so the lockfile was a report of one
install rather than a specification of the next. `environment/Dockerfile` had always installed
from `lock.txt`. The image and the local environment would have drifted apart, silently, and
the README said of the lockfile "this is what reproduces" while nothing installed from it.

`install-chap.sh` now installs from the lockfile when there is one, re-resolves only under
`RESOLVE=1`, and **compares the built environment against the lockfile and prints the
difference at the end of every build**. The environment was rebuilt from the pinned 174
packages, verified to match, and verified to reproduce the recorded per-cell scores exactly.

**That defect had been in the repository since batch 2 and no amount of reading would have
found it.** It took a rebuild, and the rebuild happened only because something broke. It is the
strongest argument this project has yet produced for `/validate`'s claim that clean-room checks
belong on a schedule rather than at submission.

**Five smaller corrections**, each found by the run or by a check and each fixed at the cause
(commit `f13dba4`): the invariants checker walked into the environment chap-core builds inside
a model directory and reported 458 findings about numpy; both baselines' `train.py` asserted
they were not random without recording what that means for Rule 6; the comparison reported an
unpaired standard deviation where batch 4 had published a standard error; the conclusion said a
model beat all the baselines when it was itself one of them; and the paired-difference
histogram used linear bins on a symlog axis, drawing a picture of the binning.

**The machine was heavily loaded by unrelated processes** for part of the batch — a system
crash reporter at 90 % of a core, load average above 60 — which made the emulated reference run
about ten times slower than batch 4 measured it. Nothing about the results depends on it; the
run costs recorded for the reference are therefore an upper bound rather than a measurement,
and batch 12 should re-measure them on a quiet machine before costing the manifest.

## 9. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| Each fork gets **only its main-path child** in this batch | Batch 5's design and the plan's batch-7 paragraph differ on this; the narrower reading was taken because a sibling that exists but cannot run would pass `/validate invariants` and advertise an alternative nobody can execute. | agent-autonomous |
| A setup stage finds its input by **searching for the one child of the previous fork with results under this combination**, never by naming a child | It is what lets the stability driver swap a child without any downstream script changing, and it fails loudly rather than silently if a combination somehow has two. Batch 5's contract needs the mechanism and does not name it. | agent-autonomous |
| `02_setup` gains **an assembly step of its own** that writes the single dataset and the single flag set | Otherwise every model must reach into the last fork's directory and know how many stages the setup has. Not in batch 5's design; it is what the design's file contract turned out to need. | agent-autonomous |
| The dataset is carried through the setup chain **as text lines, not through a parser** | A pandas round trip returns an integer count in a column with blanks as `0.0`, so three stages were declaring the identity while producing different bytes. Batch 3 made the same choice for the partition for the same reason. | agent-autonomous |
| **One shared `chap_eval.py`** for every model of ours, in `03_models/scripts/lib/` | "No candidate is compared on a metric computed a different way" is a phase-C constraint and is cheapest to enforce structurally. A runner copied per model is a set of copies that will drift. | agent-autonomous |
| `node.py` no longer treats a **subdirectory of `scripts/`** as a callable step | A node has to be able to hold a model contract directory beside the script that runs it. Methodological change under Rule 4. | agent-autonomous |
| `check_invariants` **enforces the node-naming rule** — numbered sub-analyses, lettered alternatives — and `AGENTS.md` §8 states it | Batch 5 settled the convention and left it to be remembered. A convention nobody checks is a convention that holds until it does not. Methodological change under Rule 4. | agent-autonomous |
| `02_climatology` is **a fork on the estimation window**, and there is no fork on how its uncertainty is constructed | A climatology forecast is already a distribution; a persistence forecast is a point. Symmetry between the two baselines would have been tidier and would have asserted something false. | agent-autonomous |
| The climatology baseline re-estimates from the **expanding historic frame** at each split | The persistence baseline's anchor already comes from the historic frame, and a baseline artificially deprived of two years overstates whatever beats it. The frozen-window sibling holds the alternative and `train.py` stores the table it would have used. | agent-autonomous |
| `conclude.py` is written **now**, with a placeholder it names as a placeholder | A contract first exercised when it has to carry a real result is a contract first tested at the worst moment. Which model is ours is resolved from the tree, so no second declaration of the main path exists. | agent-autonomous |
| The comparison reports **four standard errors and a computed noise floor**, and no significance test | The naive per-cell error assumes 371 independent observations and they are not. The floor from the reference's own repeats is the only figure here that needs no assumption at all. Significance is ruled out by §4b. | agent-autonomous |
| `install-chap.sh` **installs from `lock.txt`** and reports any difference between the built environment and it | Rule 3. The previous behaviour meant the lockfile was a report of one install rather than a specification of the next, and the local environment and the Docker image would have drifted apart. Methodological change under Rule 4. | agent-autonomous |
| The reference's run costs from this batch are recorded as an **upper bound**, not a measurement | The machine was heavily loaded by unrelated processes for part of the run. Recording a contaminated figure as a measurement would put it into batch 12's manifest costing. | agent-autonomous |

## 10. Compliance for this batch

- **Rule 1** — thirteen provenance records, one per result group, each naming its script with a
  hash, its exact invocation, its inputs with hashes, the environment, the seeds, the commit,
  the instruction-set commit, the alternatives considered and the agency. Every figure in this
  report is read from a file produced by an executed script; nothing crossed a step in a
  transcript.
- **Rule 2** — nothing produced was edited. Five defects were corrected **at the source and the
  affected steps re-executed**, which is what the rule requires instead. The models are
  deterministic, so the re-execution produced identical scores and that is verifiable.
- **Rule 3** — the environment's Docker layer built for the first time, and `install-chap.sh`
  was found to be resolving rather than installing from the lockfile and fixed. Each model
  ships its own `uv.lock`, and the runner verifies after every run that the lockfile chap-core
  built from is the tracked one. The reference is pinned by image digest, with its source
  revision read back out of the image at every run.
- **Rule 4** — four commits: before the run, a corrected before-the-run commit, the five
  corrections, and after the run. The instruction files changed — `AGENTS.md` §8, `/node`,
  `check_invariants.py`, `node.py` — and each commit says so in those terms.
- **Rule 5** — every stage of the setup chain, every model's fitted object, every evaluation,
  the per-cell scores and four reporting resolutions, in CSV, JSON and NetCDF. No pickle.
  56 MB of NetCDF per combination, annotated in three `criticality.md` files.
- **Rule 6** — verified for both of our models by running each twice and diffing:
  byte-identical. Not satisfiable for the reference, and quantified instead — its four repeats
  span 0.57 CRPS, which the comparison then uses as its resolution.
- **Rule 7** — two figures, each with its plotted values, its pre-aggregation values and its
  script, and each with a provenance record.
- **Rule 8, 9, 10** — no surface here; batches 17 and 19 give them one.
- **`/validate invariants`** — passes: tree, provenance, plots, seeds, claims, git, crossing.
  The seeds check failed first with 458 findings and the walk was fixed, not the check.
- **`/validate cleanroom`** — run, with its differences and its limitation recorded in
  [[26-08-26_cleanroom]].

## 11. What is still unknown

1. **How model configuration reaches an `MLproject` model.** Unexercised since batch 2 — neither
   baseline has configuration, and chap-core wrote each an empty
   `model_configuration_for_run.yaml`. Batch 8's candidate is the first that needs it.
2. **Whether a gradient-boosted model can be given a calibrated probabilistic head on this
   data.** Batch 4 named it as where that family fails. Batch 10 settles it.
3. **What `ewars_plus_template` is.** To be read before batch 8 implements candidate 1. Open
   since batch 5 and not yet worth a batch of its own.
4. **Whether the headline weighting fork flips the ranking.** §4 gives the first evidence that
   it might: the reference loses in the two highest-burden provinces. It costs seconds to
   answer and it is batch 12's.
5. **What the reference actually costs on a quiet machine.** This batch's figure is
   contaminated by machine load.

## 12. For the human

- **The tree runs end to end and the vertical slice reproduces inside it exactly.** Everything
  from here happens in `analysis/`.
- **The comparison cannot resolve the gap we are trying to close.** Both baselines are about
  2.5 CRPS worse than the reference and neither difference clears two standard errors, on any
  of four ways of computing them. The development backtest resolves roughly 4 CRPS; the whole
  corridor from persistence to the reference is 2.8. **This is the batch's most important
  result and it is uncomfortable**: it means a candidate can win the leaderboard without the
  evaluation being able to say it won. The project's success criterion — beat the reference —
  is still the right target, but "beat" will have to be reported with the spread beside it and
  a plain statement that the two could not be separated. That is exactly the outcome §4b
  anticipated when it settled, before any number existed, that significance is not attainable
  here. It is better to have measured it in batch 7 than in batch 15.
- **At one month's lead, a persistence baseline is level with the field's model** (16.43
  against 16.54). The reference earns its aggregate advantage at two and three months. If
  there is a modelling story in this project, that is where it starts.
- **The reference loses in Vientiane Capital and Champasak** — half the country's reported
  dengue — and wins nearly everywhere else. Which is why the choice of how to weight the
  headline mean, the cheapest fork in the project, may also be one of the most consequential.
- **A defect that had been in the repository since batch 2 was found by accident**: the
  environment installer was writing its lockfile rather than installing from it, so the pinned
  environment was not pinned. It was found because a clean-room attempt broke something and the
  repair had to rebuild. That is the argument for the clean-room check, and it arrived with an
  example rather than as an assertion.
