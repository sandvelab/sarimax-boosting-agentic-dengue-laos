# Batch 5 — bootstrap

Generated from [[26-08-22_dengueForecastingCase]] — iteration 5

**Phase A · Status: done — expanded · Executed 2026-08-26**

---

The batch that turns the rest of the plan into batches. Phases C, D and E were written as
aims and constraints because the early batches genuinely did not know what the later ones
were; four batches of reconnaissance have now established the install, the metric, the data,
the scheme, the criterion and the cost of a run, so the remaining work can be named.

This batch produces **no analysis output**, and it is `done — expanded` by construction. What
it produces is a design: the claim tree that batch 7 builds, the fork inventory that phase D
perturbs, the output contract that makes both possible, and twelve concrete batches with a
revised budget. Every figure it uses to size that budget comes from a file produced by an
earlier batch, and every figure it *derives* from those is labelled an estimate.

## 1. What this batch decides, and what it does not

It decides the shape of the tree, the placement of every fork, the file contract between
nodes, the mechanism by which one code path serves both the main analysis and the stability
run, the composition and rough cost of the perturbation manifest, and the batch list.

It does not decide which model wins, which alternative is promoted, or what the manifest's
final cut is — those are phase C's and phase D's, and deciding them here from an armchair
would be exactly the silent judgment call the project exists to make visible. Where this
design fixes something that later evidence could overturn, it says which batch overturns it.

## 2. The claim tree

`analysis/` is the root. Sub-analyses children are numbered `NN_name` in run order;
alternatives children are lettered `a_`, `b_`, `c_`, because they are mutually exclusive and
unordered — only one ever runs on the main path. Bold is the main path.

```
analysis/                          "Can a spatio-temporal model of monthly dengue across the
│                                   provinces of Laos beat its baselines and the reference,
│                                   and how far does that survive the alternatives?"
│                                  children: sub-analyses
│                                  own scripts: conclude.py, final_conclusion.py
│
├── 01_data/                       "What does the dataset contain, and on what part may
│   │                               development happen?"            [EXISTS — batch 3]
│   │                              children: sub-analyses
│   ├── 01_partition/              cuts off 2010; the only node that reads the full file
│   └── 02_characterise/           describes the development period; fixes the scheme
│
├── 02_setup/                      "What dataset and evaluation setting do all models — ours,
│   │                               the baselines and the reference — face in common?"
│   │                              children: sub-analyses
│   ├── 01_population/             "How should the static population figure enter the data?"
│   │   │                          children: alternatives
│   │   ├── **a_static**           the archived 2020 snapshot, constant across the period
│   │   └── b_backcast             a per-year series back-cast from a published growth rate
│   ├── 02_trainingWindow/         "How much of the record should models be allowed to learn
│   │   │                           from, given that the zero rate falls monotonically?"
│   │   │                          children: alternatives
│   │   ├── **a_from1998**         the whole development period
│   │   └── b_from2003            start at 2003, after the most zero-heavy years
│   ├── 03_provinces/              "Which provinces belong in the analysis at all?"
│   │   │                          children: alternatives
│   │   ├── **a_chapFilter**       inclusion left to chap-core's own region filter
│   │   ├── b_dropSilent           LA-VI and LA-XN removed before evaluation
│   │   └── c_mergeVientiane       LA-VI merged into LA-VT, which it geographically contains
│   └── 04_retrain/                "How often is a model refitted across the backtest?"
│       │                          children: alternatives
│       ├── **a_once**             chap-core's default, n-retrain 1
│       └── b_everySplit           refitted at every split
│
├── 03_models/                     "What forecast does each model make on that common ground?"
│   │                              children: sub-analyses
│   ├── 01_baselines/              "How well does the problem's own inertia forecast it?"
│   │   │                          children: sub-analyses
│   │   ├── 01_persistence/        next months = last observed month
│   │   └── 02_climatology/        next months = mean of that calendar month in training
│   ├── 02_reference/              "What does the field's own model score here?"
│   │                              chapkit_ewars_model at its own defaults, k repeats
│   └── 03_candidate/              "Which model family should ours be?"
│       │                          children: alternatives
│       ├── **a_hierNB/**          "…a hierarchical negative-binomial GLM"
│       │   │                      children: sub-analyses; own script runs chap eval
│       │   ├── 01_observation/    "What observation model do the counts get?"
│       │   │                      alternatives: **a_negBinomial** | b_zeroInflated | c_hurdle
│       │   ├── 02_covariates/     "Which climate covariates, at which lags?"
│       │   │                      alternatives: **a_lagged** | b_rich | c_climateFree
│       │   ├── 03_population/     "How does population enter the model?"
│       │   │                      alternatives: **a_offset** | b_covariate | c_ignored
│       │   └── 04_fitTime/        "Does the model do its fitting in train or in predict?"
│       │                          alternatives: **a_trainOnly** | b_refitAtPredict
│       ├── b_boosted/             "…gradient-boosted trees with a probabilistic head"
│       │   │                      children: sub-analyses
│       │   ├── 01_features/       alternatives: **a_lagBlock** | b_richCalendar
│       │   └── 02_head/           alternatives: **a_negBinomial** | b_quantileEnsemble
│       └── c_ensemble/            "…a weighted combination of the above and the baselines"
│           └── 01_weighting/      alternatives: **a_equal** | b_crpsWeighted
│
├── 04_score/                      "What does each model score, and how do they compare, at
│   │                               every resolution the platform allows?"
│   │                              children: sub-analyses
│   ├── 01_collect/                per-cell CRPS, coverage and MAE for every model, from
│   │                              chap-core's own metric API
│   ├── 02_aggregate/              "Over what weighting is the headline mean taken?"
│   │                              alternatives: **a_unweighted** | b_populationWeighted
│   │                                                             | c_caseWeighted
│   └── 03_compare/                leaderboard, and the paired per-cell comparison against
│                                  the reference with its spread
│
├── 05_stability/                  "How far does the conclusion survive the alternatives?"
│                                  children: sub-analyses; holds the manifest and the driver
│
└── 06_holdout/                    "Does the conclusion hold on a year no development ever
                                    saw?"                          [CREATED IN PHASE E]
```

`01_data` exists. Everything else is built in batch 7, except `06_holdout`, which does not
exist until batch 16 — a node that reads the sealed file must not be runnable while the seal
is on, and `analysis/run.sh` running it by accident is exactly the failure the seal is there
to prevent.

### Why the forks sit where they do

**Every fork under `02_setup` re-scores every model; every fork under `03_models/03_candidate`
moves only ours.** That is the plan's §4b rule about the two kinds of fork, and here it is a
property of the tree's shape rather than a convention someone has to remember. A fork placed
in the wrong subtree produces a comparison in which one side moved and the other did not, and
the tree makes that visible as a misplacement rather than leaving it as an oversight.

**`04_score/02_aggregate` is a third case that costs nothing.** Re-weighting the mean is a
re-aggregation of stored per-cell scores, so it re-scores every model without re-running any
of them. It is the same kind as a `02_setup` fork under §4b's rule — both sides move together
— and a different kind under the budget, which matters when the manifest is costed.

**The training-window fork does not change what is evaluated.** Batch 2 established that the
splits are laid out backwards from the last period of the file, so truncating the early years
leaves the evaluated cells identical while changing only what the models learn from. That is
what makes it a clean fork: the 371 cells are the same on both sides.

**The province fork does change what is evaluated**, and it is a fork anyway — because the
root's conclusion is a skill score. Raw CRPS is not comparable between `a_chapFilter` and
`c_mergeVientiane`; a ratio of our CRPS to the reference's, both computed on whatever cell
set that child produced, is. The plan's §4b decision to report a relative conclusion was
argued from the development-versus-holdout comparison, and it turns out to be what lets a
fork change the denominator of the metric at all. This design would not work with a raw
headline number.

**`n_retrain` is a fork and the backtest scheme is not.** Batch 3 fixed `n_periods`,
`n_splits` and `stride` and said they do not move again; `n_retrain` was never part of that
triple and was explicitly flagged as a fork left at chap-core's default. It sits under
`02_setup` because it changes how every model is evaluated.

**The candidate fork's children have different internal forks, and that is fine.** The
combination space is conditional, not a product: `a_hierNB`'s observation model has no
meaning under `b_boosted`. The manifest enumerates combinations, not a cross-product, and
says so.

## 3. The three properties a stability run needs

The manuscript's Appendix requires three things of a tree a stability run can walk
([[reproAgenticAiManuscript]], *What a PCS stability analysis requires of the tree*). Each is
checked here rather than assumed, because a fork that fails one of them has to move before it
is built, not after.

**(i) A shared output contract per fork.** Every child of every fork writes the same files
with the same schema as its siblings:

| Node | Writes | Schema |
|---|---|---|
| `02_setup/*/child` | `results/$COMBO/analysis_dataset.csv`, `setup_spec.json` | the Chap CSV columns unchanged; the spec names the child taken and the eval flags implied |
| `03_models/*/model` | `results/$COMBO/eval.nc`, `model_spec.json`, `run_cost.json` | chap eval's own NetCDF |
| `04_score/01_collect` | `results/$COMBO/metrics_cell.csv` | `model, location, time_period, horizon_distance, crps, abs_error, in_10_90, in_25_75, observed` |
| `04_score/02_aggregate/child` | `results/$COMBO/metrics_summary.csv` | `model, weighting, n_cells, mean_crps, mae, coverage_10_90, coverage_25_75` |
| `04_score/03_compare` | `results/$COMBO/leaderboard.csv`, `paired_vs_reference.csv` | one row per model; one row per cell per reference repeat |
| root `conclude.py` | `results/$COMBO/conclusion.json` | `combo, dataset, skill_score, crps_ours, crps_reference, coverage, n_cells` |
| `05_stability` | `results/manifest.csv`, `conclusions.csv` | one row per combination |

The two forks that could have failed this test are the ones discussed above, and both pass at
the level they are placed: `02_setup`'s children all emit a dataset of the same schema, and
`03_candidate`'s children all emit an `eval.nc`. A fork on the *metric* would have failed —
which is one more reason this project never implements one.

**(ii) A computed conclusion at the root.** `analysis/scripts/conclude.py` reads
`04_score/03_compare/results/$COMBO/` and writes `conclusion.json`: the skill score
`1 − CRPS_ours / CRPS_reference` fixed by §4b, with raw mean CRPS and both coverage figures
beside it. It is invoked once per combination — by `analysis/run.sh` for the main path, and by
the stability driver for every other. `final_conclusion.py` runs after it and assembles the
development spread, the holdout spread and the main-path number into the reported result.
Nothing states the conclusion in prose anywhere it could drift from the file.

**(iii) An enumerated perturbation set with a budget.** §5 below. The enumeration is frozen in
batch 12 for development and in batch 15 for the holdout, and the cut is recorded with what
fell below it.

## 4. One code path for the main analysis and the stability run

The mechanism is a single environment variable.

- `COMBO` names the combination; it defaults to `main`.
- Every node reads its inputs from and writes its outputs to `results/$COMBO/`.
- The **main path is combination `main`**, so `bash analysis/run.sh` is an ordinary run of the
  pipeline with the variable unset, and reproduces the reported result exactly as `AGENTS.md`
  §2 requires.
- The stability driver at `05_stability/scripts/` reads `manifest.csv`, and for each row sets
  `COMBO` and calls the named children's `run.sh` directly — which is what the manuscript
  specifies a stability node does, and what makes the alternatives run without the main
  path's `run.sh` files being touched.

Each combination re-runs the whole chain from `02_setup` down, because the dataset stages cost
seconds and a chain that partially reuses another combination's intermediates is a chain
nobody can read. The one exception is deliberate and recorded: **models are re-run only when a
fork upstream of them moved.** A combination that changes only a candidate-internal fork
reuses the reference and baseline scores from the setup combination it shares, and
`manifest.csv` carries the reuse as a column, so which numbers were computed and which were
inherited is on the face of the file rather than in the driver's control flow.

Two consequences worth stating now. `/validate invariants` will need to know that a `results/`
subdirectory per combination is expected, and batch 12 extends it rather than exempting the
directory. And storage grows with the manifest: about 10 MB per `eval.nc`, which at 25
combinations is a few hundred megabytes. `/annotate-criticality` covers it in batch 12, and
the per-cell CSVs — which are what everything downstream reads — are two orders of magnitude
smaller than the NetCDF they come from.

## 5. The fork inventory and the perturbation manifest

Ten forks, from batch 3's data-problem list and batch 4's method survey, confirmed against
what those batches actually found.

| # | Fork | Node | Children | Kind |
|---|---|---|---|---|
| F1 | Population column | `02_setup/01_population` | 2 | setup — all models re-run |
| F2 | Training window | `02_setup/02_trainingWindow` | 2 | setup — all models re-run |
| F3 | Province inclusion | `02_setup/03_provinces` | 3 | setup — all models re-run |
| F4 | Retrain policy | `02_setup/04_retrain` | 2 | setup — all models re-run |
| F5 | Headline weighting | `04_score/02_aggregate` | 3 | scoring — re-aggregation only |
| F6 | Model family | `03_models/03_candidate` | 3 | candidate — ours re-run |
| F7 | Observation model | `…/a_hierNB/01_observation` | 3 | candidate — ours re-run |
| F8 | Covariates and lags | `…/a_hierNB/02_covariates` | 3 | candidate — ours re-run |
| F9 | Population in the model | `…/a_hierNB/03_population` | 3 | candidate — ours re-run |
| F10 | Fit time | `…/a_hierNB/04_fitTime` | 2 | candidate — ours re-run |

**The forecast horizon is not on this list, and the plan's phase D says it should be.** It
cannot be. Batch 3 established that `n_periods = 3` follows from the human's choice of
reference model — chap-core forces it for EWARS and the chapkit service declares
`prediction_periods: 3` — so a combination at a different horizon is one in which the
reference cannot be scored, and the root's conclusion is a ratio to the reference. A fork
whose conclusion is uncomputable is not a fork. This is the one item of the plan's phase-D
list that reconnaissance removed rather than refined.

**Population appears twice and they are different questions.** F1 is what the *column*
contains and moves every model including the reference. F9 is how *our* model uses it and
moves only ours. Batch 3's list had one entry; the tree needs two, and conflating them would
have put a candidate-internal choice into the subtree that re-scores the reference.

### The manifest

**Tier 1 — one at a time.** The main path, plus every non-main child of every fork taken
alone: 1 + (1+1+2+1) setup + 2 scoring + (2+2+2+2+1) candidate = **20 combinations**. This is
the tier that answers "does the conclusion move when this choice is taken instead", which is
the question the plan calls the most valuable single output of the project.

**Tier 2 — pairs, selected by a rule fixed in advance.** The two setup forks and the two
candidate forks with the largest absolute change in skill score in tier 1, crossed: **8
combinations**. The rule is written into the manifest before tier 1 runs, and the selection is
made by the script from tier 1's `conclusions.csv`, so which pairs get run is computed rather
than chosen by looking.

**Below the line, recorded as cut.** The full conditional product is 24 setup-and-scoring
combinations × 54 candidate combinations under `a_hierNB` alone — over a thousand analyses,
which is weeks of compute for a return that tier 1 and tier 2 already give the shape of. Also
below the line: perturbing the reference model, which §4 of the plan forbids because it is an
external reference at its own configuration; and the fine-tuned foundation model of batch 4's
shortlist, which stays a phase-C option only if the budget survives.

### What it costs, estimated

The two measured figures are batch 4's: an eight-split development backtest costs **149 s** for
the reference through the emulated amd64 image (`ewars_run_cost.json`) and **56 s** for a
native `uv_env` model (`native_run_cost.json`). Everything below is arithmetic on those two
numbers and is an **estimate, not a result** — batch 12 replaces it with measured
per-combination costs when it writes the manifest for real.

| | Estimate |
|---|---|
| A real candidate's development backtest | ~120 s (the native floor plus a fit) |
| One setup combination, development: 3 native models + 4 reference repeats | ~16 min |
| Tier 1 setup combinations (6, including main) | ~1.6 h |
| Tier 1 scoring combinations (2) | seconds |
| Tier 1 candidate combinations (12) | ~25 min |
| Tier 2 (8, mixed) | ~1 h |
| Development total, 20 + 8 combinations | **~3 h** |
| Holdout, same manifest at 4 splits instead of 8 | **~1.5 h** |

**The reference is re-scored four times wherever it is re-scored at all.** It is unseeded, and
batch 4 measured its re-run spread at sd 0.196 CRPS. Since the skill score divides by it, an
unaveraged denominator would put a ~2 % wobble on every combination's conclusion — comparable
to the fork effects the manifest exists to measure. Four repeats put that term at about 0.1
CRPS, and cost about ten minutes per setup combination, which the budget above already
carries.

**Compute is not what binds this project.** Under five hours for the whole manifest, run
twice, on a laptop. What binds is implementation effort, and the batch list below is sized in
that unit.

## 6. What reconnaissance changed in phases C–E

The plan asks this batch to revise what reconnaissance showed to be wrong, and to say what
changed.

| Changed | Why |
|---|---|
| **The horizon is removed from phase D's fork list** | It is forced by the reference model, and a fork the reference cannot be scored under has no computable conclusion (§5). |
| **Population becomes two forks, not one** | The column and the use of the column move different sets of models (§5). |
| **The §9 budget is expressed in implementation effort, not evaluation runs** | Batch 4 measured a full backtest at one to three minutes. The original budget was written when a run's cost was unknown and the phase-D manifest was assumed to be constrained by it; it is not (§5). |
| **Phase C gets 4 batches rather than 6–10, with a stated extension rule** | The shortlist is three candidates and their internal forks, all cheap to evaluate. Adding batches on a schedule rather than on evidence is the drift `AGENTS.md` §6 warns about. |
| **Batch 7 additionally builds `02_setup`, `04_score` and the reference node** | Batch 4's §9.1 leaves the paired sensitivity of the comparison open, and it is the single thing most expensive to discover late — if a paired comparison on 371 cells cannot separate two models, phase C's design changes. It needs only the reference and one trivial model, both of which batch 7 has. |
| **Batch 6 writes the contract files even with one child per fork** | A contract first exercised when it has to carry alternatives is a contract first tested in phase D. |
| **The holdout node does not exist until batch 16** | `analysis/run.sh` must not be able to open the sealed file while the seal is on. |
| **Phase E's holdout run re-scores the reference four times too** | For the same reason as development: the conclusion is a ratio to an unseeded denominator. |

Unchanged and worth saying so: the split scheme, the metric, the criterion, the success
condition, the two required baselines, the reference model, the freeze discipline, and the
route phase E takes. Reconnaissance confirmed all of them.

## 7. The batches

Phase B's two batches are unchanged apart from the two additions in §6. Batches 8 onward are
new. Costs are in sessions of implementation effort.

### Phase C — model development

**Batch 8 — the candidate contract, and candidate 1 at its defaults.** Implement the
hierarchical negative-binomial GLM as an `MLproject` model with a `uv_env`, seeded from the
project seed; create `03_models/03_candidate/a_hierNB` with its four fork nodes each holding
only its main child; run it on development through the same `chap eval` path as everything
else; put it on the leaderboard. Answers batch 4's open question on how configuration reaches
an `MLproject` model. *Output: the node, its results, `26-08-2x_b08_*.md`. ~1 session.*

**Batch 9 — candidate 1's internal forks.** Build the sibling children of F7–F10, run each on
development, and promote the main path with `/node promote`. Every sibling is retained and
every one of them is re-run in phase D and on the holdout, which is what keeps a selection
made on development CRPS from being a hidden one: the cost of the selection is measured rather
than argued about. *Output: seven or eight sibling nodes, the leaderboard, a report. ~1
session.*

**Batch 10 — candidate 2: gradient-boosted trees with a probabilistic head.** `b_boosted` and
its two internal forks. Batch 4 named the probabilistic head as where this family fails; if it
cannot be made to produce calibrated output, that is the finding and it stays in the record.
*Output: the node or the documented failure. ~1–2 sessions.*

**Batch 11 — candidate 3: the ensemble, and the close of phase C.** `c_ensemble` over the
candidates and baselines that exist; the family-fork main path chosen; the paired comparison
against the reference reported with its spread; optionally the three integrated models batch 4
named as leaderboard context. **Phase C ends here unless the leaderboard's best moved by more
than 0.4 CRPS in this batch** — the reference's own re-run noise, and therefore the smallest
movement that means anything. The stopping rule is fixed now, before any leaderboard exists.
*Output: the node, the phase-C closing report. ~1 session.*

### Phase D — stability and the veridical record

**Batch 12 — `/perturb plan`.** Build `05_stability`, the combination driver, and
`manifest.csv` with tier 1, tier 2's selection rule, measured per-combination costs, the
budget line and what falls below it. Extend `/validate invariants` for combination-scoped
results and run `/annotate-criticality` over the storage the manifest implies. *Output: the
node, the frozen development manifest. ~1 session.*

**Batch 13 — `/perturb run`, the setup and scoring forks.** The six setup combinations and
the two scoring ones; every model re-scored under each, the reference four times. *Output:
`conclusions.csv` for those rows. ~1 session, mostly compute.*

**Batch 14 — `/perturb run`, the candidate forks and tier 2.** The twelve candidate
combinations, then tier 2's eight pairs selected by the script from tier 1's results.
*Output: the rest of `conclusions.csv`. ~1 session.*

**Batch 15 — `/perturb report`, and the freeze.** The distribution of conclusions over the
28 analyses; which forks the conclusion is insensitive to and which it is not; the plots and
their data. Then **freeze the holdout manifest** — the identical set — commit it, and record
its hash in the report. Nothing is added, dropped or re-tuned after this point. *Output: the
stability report, `holdout_manifest.csv`, its commit. ~1 session.*

### Phase E — closing

**Batch 16 — the holdout, opened once.** Create `06_holdout`; run exactly the frozen manifest
on the archived original at `n_periods 3, n_splits 4, stride 3`, by the route batch 2
established; report the holdout spread beside the development spread for the same models and
the same combinations. If the gap is large, it is the project's most interesting result and it
is reported plainly. *Output: the node, the final numbers. ~1 session.*

**Batch 17 — claims and the hierarchical report.** `/claims` for the headline claim, the
stability claim, the negative claims and their supporting claims, each bound to a stored
result; `/hierarchical-report` with the tree supplying the upper levels and each node's
within-result detail below. *Output: `claims.md`, the report. ~1 session.*

**Batch 18 — validation and the plan's own drift.** `/validate cleanroom` and
`/validate outsider`, with what the outsider misunderstood recorded and fixed; the plan-drift
section generated from the diff between `Archive/plan-as-delivered/` and the live plan and
from that file's commit history, with §4b's agency column. *Output: the validation record,
the drift section. ~1 session.*

**Batch 19 — the case write-up, the reproducibility report, the release.** The document that
could be lifted into the manuscript's *An illustrating case* section — including the worked
claim-tree skeleton and the perturbation families in dengue terms, which is what the archived
Appendix supplied for the case this one replaces, and including where this setup was more
trouble than it was worth. Then `/repro-report` and `/release`, which stops before creating a
remote. *Output: the write-up, the report, the prepared repository. ~1 session.*

**Batch 20 — the external check (optional).** The final model unchanged on `tha` and `vnm`.
The project is complete without it and it is the first thing cut. *~½ session.*

## 8. The revised budget

| Phase | Batches | Original | Now |
|---|---|---|---|
| A — orientation and bootstrap | 1–5 | 5 | 5, done |
| B — vertical slice and tree | 6–7 | 2 | 2 |
| C — model development | 8–11 | ~6–10 | 4, extended only by the §7 stopping rule |
| D — stability | 12–15 | ~4–6 | 4 |
| E — closing | 16–19 | ~4 | 4 |
| Optional | 20 | — | 1 |
| **Total** | | **~21–27** | **19, plus one optional** |

Two things moved. The unit is implementation effort rather than evaluation runs, because
evaluation turned out to cost one to three minutes. And phase C shrank, because its content is
now known: three candidates and their internal forks, not an open-ended search. The plan's
instruction to protect phase E before phase C is preserved — E keeps its four batches, and the
stopping rule cuts C rather than E if anything binds.

## 9. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The two kinds of fork become a property of the tree's shape: everything under `02_setup` re-scores every model, everything under `03_candidate` moves only ours | §4b's rule was a convention someone had to apply correctly each time. Placed in the tree it is checkable, and a misplaced fork is visible as a misplacement. | agent-autonomous |
| A third case is recorded: the scoring fork, which re-scores every model without re-running any | Re-weighting the headline mean re-aggregates stored per-cell scores. It is §4b's first kind by semantics and a different thing entirely by cost, which matters when the manifest is costed. | agent-autonomous |
| The combination is an environment variable, `COMBO`, defaulting to `main`, and every node reads and writes under `results/$COMBO/` | It makes the main path combination `main`, so `analysis/run.sh` and the stability run are the same code. A separate stability pipeline would be a second implementation of the analysis, and the two would drift. | agent-autonomous |
| Models are re-run only when a fork upstream of them moved, and the reuse is a column in the manifest | Re-running the emulated reference under a fork that cannot affect it buys nothing. Putting the reuse in the file rather than in the driver's logic keeps which numbers were computed and which inherited on the face of the record. | agent-autonomous |
| The forecast horizon is removed from phase D's fork list | Forced by the reference model, so a combination at another horizon has no reference to compare against and the root's conclusion is uncomputable there. | agent-on-human-assessment |
| Population becomes two forks — the column, and the model's use of it | They move different sets of models. Batch 3's single entry would have put a candidate-internal choice in the subtree that re-scores the reference. | agent-autonomous |
| The reference is re-scored four times wherever it is re-scored | It is unseeded and the conclusion divides by it; an unaveraged denominator carries a ~2 % wobble, which is the size of the effects being measured. Cost is about ten minutes per setup combination. | agent-autonomous |
| Tier 2's pairs are selected by a rule written before tier 1 runs, and applied by a script | Choosing which pairs to explore after seeing tier 1's numbers is selection with extra steps, which is the objection the plan makes to an unfrozen holdout manifest, applied one level down. | agent-autonomous |
| Phase C ends when the leaderboard's best moves by less than 0.4 CRPS in a batch | The reference's own re-run spread. A stopping rule fixed before any leaderboard exists is the only kind that cannot be adjusted to suit the leaderboard. | agent-autonomous |
| Alternatives children are lettered, sub-analyses children numbered | `AGENTS.md` §8 says node directories are `NN_shortName`, "numbered in the order the parent runs them" — which is the ordered case. Alternatives are unordered and mutually exclusive, and the manuscript's own worked skeleton letters them. Batch 7 makes §8 say so explicitly, as a methodological change under Rule 4. | agent-autonomous |
| `06_holdout` is not created until batch 16 | A node that reads the sealed file must not be runnable while the seal is on. Once created, re-running `analysis/run.sh` re-reads the holdout, and that is reproduction of a reported result rather than a second look — recorded once, in batch 16. | agent-autonomous |
| Batch 7 additionally builds `02_setup`, `04_score` and the reference node | The paired sensitivity of the comparison is batch 4's first open question and the most expensive one to discover late; it needs only the reference and one trivial model. | agent-autonomous |
| The budget is expressed in implementation effort and phase C is cut to four batches | Batch 4 measured evaluation at one to three minutes a run. Batches allocated on a schedule rather than on evidence are the expansion-without-decision `AGENTS.md` §6 names. | agent-autonomous |

## 10. Compliance for this batch

- **Rule 1** — this batch produced no result. Every figure it quotes comes from a file an
  earlier batch produced: `ewars_run_cost.json`, `native_run_cost.json`,
  `ewars_repeatability_summary.csv`, `evaluable_cells_by_province.csv`,
  `backtest_scheme_chosen.json`. Every figure it *derives* from those — the manifest's cost
  table — is labelled an estimate in §5 and is replaced by measured costs in batch 12.
- **Rule 4** — committed after the batch, with the batch named. No script was written, so
  there was nothing to commit before it.
- **Rules 2, 3, 5, 6, 7** — no surface: nothing was produced to edit, the environment did not
  change, no intermediate was computed, nothing ran, no plot was drawn.
- **Rules 8, 9, 10** — no surface, and the batches that give them one are 17 and 19.
- **`/validate invariants`** — run at the end of the batch; outcome in the ledger entry.

## 11. What is still unknown

1. **Whether a paired per-cell comparison on 371 cells can separate two models.** Batch 4
   argued it is far tighter than the unpaired 5.65 CRPS and could not compute it with one
   model. Batch 7 now computes it, and if the answer is no, phase C's design changes rather
   than phase D discovering it.
2. **Whether a gradient-boosted model can be given a calibrated probabilistic head on this
   data.** Batch 4 named it as where that family fails. Batch 10 settles it.
3. **How model configuration reaches an `MLproject` model in practice.** Unexercised since
   batch 2 flagged it; batch 8 is the first node that needs it.
4. **Whether the Docker layer of `environment/` builds.** Open since batch 2, cheap, and now
   worth doing in batch 7 while the tree is small.
5. **What `ewars_plus_template` is.** The closest published thing to candidate 1, newer than
   the library sweep, and worth reading before batch 8 implements anything.

## 12. For the human

- **The project has 14 batches left, plus one optional**, against the plan's original estimate
  of 16–22. Phase C shrank because reconnaissance showed evaluation is cheap and the shortlist
  is short; phase E is untouched, as §9 of the plan requires.
- **The tree makes the plan's fork rule structural.** Which forks re-score the reference and
  which move only our candidates is now decided by where a node sits, not by remembering a
  rule at the moment it applies. This is the design decision in this batch I would most want
  looked at, because everything downstream leans on it.
- **The horizon is no longer available as a fork.** It is forced by the reference model, so
  the plan's phase-D list loses one item — the only one reconnaissance removed outright.
- **Nothing about the criterion, the scheme or the seal moved.** All four reconnaissance
  batches confirmed the plan rather than contradicting it, which is worth one sentence
  somewhere in the manuscript: the parts of a plan that survive contact are as informative as
  the parts that do not.
