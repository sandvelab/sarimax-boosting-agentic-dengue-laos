# analysis — the claim tree

This is the project. Everything else in the repository is in service of it.

Each node is an **analytical aim** — a question to be explored — with the analysis that
addresses it. `analysis/` is the root node; children are subdirectories. The two
relationship types (`alternatives`, `sub-analyses`) and the shape of a node are specified in
`AGENTS.md` §2 and in `/node`.

**Two properties must always hold.** `analysis/run.sh` reproduces the entire reported
analysis, following the main path at every alternatives fork. And the paths not taken stay
here, complete and runnable — they are executed by the stability node, which calls its
siblings' main scripts.

Never create or rewire nodes by hand:

```bash
.venv/bin/python AI-internal/useful-scripts/node.py tree
.venv/bin/python AI-internal/useful-scripts/node.py new analysis 01_prepare --claim "…"
```

## How a combination reaches every node

Every node below `01_data` reads its inputs from and writes its outputs to
`results/$COMBO/`, where `COMBO` is an environment variable naming one combination of
choices and defaulting to `main`. So `bash analysis/run.sh` is an ordinary run of the
pipeline with the variable unset and reproduces the reported result; the stability node
will set it and call individual children directly, which is how the alternatives get run
without the main path's `run.sh` files being touched. One code path serves both.

Where a fork's output feeds the next stage, the next stage finds it by **searching for the
one child of that fork with results under this combination**, never by naming a child. That
is what lets an alternative be swapped in without a single downstream script changing.

A second variable, `COMBO_BASE`, says which combination this one may **inherit** from. A
combination that moves one fork has nothing of its own at the other five, at `02_setup`, or
at the models it did not re-run, and takes them from the base — per artefact, never per
combination, and always recorded in the file that reports it (`input_from_combo`,
`choice_combos`, `setup_from_combo`, `scored_under_combo`). `analysis/run.sh` sets no base,
so **the reported analysis inherits nothing**: a missing input there is an error, not a
substitution. `analysis/scripts/lib/combos.py` is the whole mechanism.

## Currently here

- **`01_data`** (sub-analyses) — what the dataset contains, and on what part of it
  development may happen.
  - **`01_partition`** — cuts the archived file into the development period (1998-01 to
    2009-12) and the sealed 2010 holdout, and verifies the two partition it exactly. **This
    is the only node licensed to read the full file.** Batch 16 opened the seal here, with
    `open_holdout.py`: it puts the two parts back together in the archived source's own
    order and checks that the result is byte-identical to that source, so phase E reads a
    file this node produced rather than reaching into `Archive/`. The licence is exercised,
    not repealed — and the proof that the two parts partition the source exactly, which is
    what makes putting them back together legitimate, is this node's too.
  - **`02_characterise`** — describes the development period only, and fixes the backtest
    scheme that every later number is computed under.
- **`02_setup`** (sub-analyses) — the common ground every model faces. Four forks in
  sequence, each handing the dataset on: `01_population`, `02_trainingWindow`,
  `03_provinces`, `04_retrain`. The node's own script assembles their output into the one
  `analysis_dataset.csv` and the one set of evaluation flags every model reads, so a model
  never needs to know how many stages the setup has. **Every fork here re-scores every
  model, ours and the reference alike.** Batch 13 built the five children the main path does
  not take: `b_backCast` (the snapshot scaled to each year by the archived national
  population series), `b_from2004` (the second half of the record only, cut at the calendar
  midpoint so the cut is not chosen by the zero rate it probes), `b_reportingOnly` (the two
  provinces with no evaluable cell removed before the platform sees them, by a rule rather
  than by name), `c_mergeVientiane` (the silent province folded into the capital, counts and
  population summed and climate area-weighted from the archived polygons) and `b_everySplit`
  (`n_retrain` set to the scheme's `n_splits`, read from the same file `assemble_setup.py`
  reads it from).
- **`03_models`** (sub-analyses) — what each model forecasts on that common ground.
  - **`01_baselines`** — `01_persistence` (a fork on how a predictive distribution is
    wrapped around a point forecast: `a_empiricalChange`, the symmetrised distribution of past
    h-step changes, against `b_negBinomialFloor`, a negative binomial about the last count
    with the mean floored and the dispersion fitted) and `02_climatology` (a fork on which
    window estimates the seasonal distribution: `a_expandingWindow`, re-estimated from the
    historic frame at each split, against `b_frozenWindow`, the training-frame table held
    fixed). Batch 22 built both `b_` children and ran their rows. **Since batch 11 these two
    forks also move the reported model**, which takes both baselines as pool members.
  - **`02_reference`** — WHO EWARS-csd at its own defaults, pinned by image digest, served
    as a container, run four times because it is unseeded.
  - **`03_candidate`** (alternatives) — our own model families, one child per family, with
    **`c_ensemble` on the main path since batch 11**. The three are compared at their own
    main paths in `AI-generated/candidate-forks/families/family_leaderboard.csv`, and the
    rule the fork was moved by is `family_rule.md` beside it.
    `a_hierNB` is candidate 1: a hierarchical
    negative-binomial GLM, with **six** sub-analysis forks deciding what it is —
    `01_observation`, `02_covariates`, `03_population`, `04_fitTime`, `05_autoregressive`
    and `06_yearVariance`, the last two added in batch 9. Each writes a
    `model_option_spec.json` carrying the choice and the premise it rests on; the node's own
    `assemble_candidate_config.py` discovers the forks, merges whichever child of each ran
    into the one `model_configuration.yaml` that `chap eval` is pointed at, and adds the
    component seed. **Every child of every fork is built and has been run**; batch 9
    promoted `c_hurdle`, `c_climateFree` and `b_provinceScaled` onto the main path. Since
    batch 11 it runs under its own combination `family_hierNB`, where its per-cell scores
    are identical to the ones it produced when it was the main path.
    `b_boosted` is candidate 2, added in batch 10: gradient-boosted trees with a
    probabilistic head, and **two** forks — `01_features` (a block of lags, or that block
    plus the calendar and the map) and `02_head` (a negative binomial around a fitted mean,
    or a ladder of quantile boosters). Neither moved. It scores **20.771** on development
    against candidate 1's 23.698 and the reference's 22.098, but it is a sibling alternative,
    so it never runs on `main` — it runs under its own combination `family_boosted`, and
    which family the main path takes is chosen in batch 11, when `c_ensemble` exists. Its
    model directory is the first in the project to depend on scikit-learn, and the first to
    store a fitted object this repository's own code walks rather than a library's.
    `c_ensemble` is candidate 3, added in batch 11 and **the model the project now
    reports**: a linear opinion pool over the other two families and both required
    baselines, with **one** fork — `01_weighting` (equal weights, or the weights minimising
    the pool's CRPS on a validation period held back inside the training frame). The fork
    does not move; estimating the weights costs 4.021 CRPS. The pool scores **18.817** on
    development against the reference's 22.098, the first positive skill score this project
    has produced. It contains no model code of its own: each member is run through **its
    own Chap entry points**, read out of the member's own `MLproject`, so there is one copy
    of every member's code in the repository, at the node that owns it. Which models it
    contains and how they are configured is `results/$COMBO/members.json`, whose path and
    hash are in the model configuration; `prepare_members.py` assembles it by running the
    fork children the running combination has not already chosen and that family's own
    assembler, so a perturbation of a member's fork moves the pool's member with it. **A
    fork it can already resolve — under `COMBO` or from `COMBO_BASE` — is left alone**, which
    is batch 14's fix: running the main child as well would give the family's assembler two
    children of one fork, and that is what blocked every candidate row until then.
    **Every fork here moves only our model**, which is what distinguishes this subtree from
    `02_setup`.
  - `scripts/lib/chap_eval.py` is the single route by which a model of ours reaches
    `chap eval`, and `scripts/lib/assemble_config.py` the single way a candidate family's
    configuration is assembled from the forks above it — the lift batches 10 and 11 both
    logged and batch 14 carried out, because it rewrites scripts whose hash is in the
    provenance of every combination they configured. Both are libraries, not steps; the
    three families are one-screen runners naming the candidate, and what is particular to
    the pool — its membership document and the union of its members' covariates — is passed
    in as data.
- **`04_score`** (sub-analyses) — `01_collect` (per-cell scores for every model that ran,
  from chap-core's own metrics), `02_aggregate` (a fork on the weighting of the headline
  mean), `03_compare` (the leaderboard, and the paired per-cell comparison against the
  reference with the noise floor beside it). The weighting fork re-scores every model
  without re-running any of them, which makes it the cheapest row in the manifest by three
  orders of magnitude. Batch 13 built `b_populationWeighted` and `c_caseWeighted`, and put
  all three children on one implementation — `scripts/lib/aggregate.py`, a library rather
  than a step — so that the diff between two children of the fork is the weight and the
  reason for it. `a_unweighted` was moved onto it and reproduces its main-path output byte
  for byte, which is the check that the refactor changed no reported number. The two
  weighted children also write `weights.csv` and `weighting_notes.json`, which say how
  concentrated the weighting is and how much of the cell set it silences. **Batch 14 made
  `03_compare` follow that fork too**: its paired difference, its three standard errors, its
  split-level comparison and its noise floor are taken under the chosen child's own
  `weights.csv`, where before they counted every cell once beside a leaderboard that did
  not — so the two weighted rows had been reporting the main path's spread under a
  re-weighted mean. Within a split the cells carry their weights; across splits the eight
  numbers count equally, because that is the figure which assumes nothing about
  independence inside a split.
- `scripts/lib/palette.py` gives every model one colour and one marker, keyed on the model's
  own name so that a model keeps its colour across combinations and two figures drawn for
  different combinations can be laid side by side. A library, not a step; imported by the
  three figures under `04_score/03_compare`. Added in batch 10, when a fifth model showed
  that each of those figures had been building its own four-entry map.
- The root's own `scripts/lib/project_seed.py` reads the one project seed from
  `readme-at-start.md` and derives a component seed from it by BLAKE2b. A library, not a
  step; imported by the nodes that have something to seed. First used by `03_candidate`,
  which is the first component in the project that draws at all.
- The root's own `scripts/conclude.py` writes `results/$COMBO/conclusion.json`: the skill
  score against the reference, with raw CRPS and coverage beside it. **Nothing anywhere else
  in the repository states the conclusion**, so nothing can drift from it. Which model is
  ours is **read off the results** — the child of `03_candidate` with a model scored under
  this combination, else under `COMBO_BASE` — not off `claim.md`'s `main-path`, which names
  the reported analysis's family and does not move with the combination. Two families with
  results under one combination is a hard failure: exactly one is on any one combination's
  path, and the project cannot report two models as its own.

- **`05_stability`** (no children) — the perturbation manifest and the driver, built in
  batch 12. `scripts/lib/inventory.py` walks the tree for alternatives nodes rather than
  carrying a list, so the manifest counts **17 forks** and grows by itself when one is
  added; `plan_manifest.py` writes `results/manifest.csv` — 24 tier-1 combinations, 8
  tier-2 slots filled by `tier2_rule.md` once tier 1 has conclusions, and one combination
  that exists and perturbs nothing — with each row's measured cost, projected storage and
  owning batch. `run_manifest.py` is the driver: it calls **the tree's own scripts** with
  `COMBO` set, substituting the moved child for the main one at each fork, because both
  assemblers in this project fail if they find two children of one fork under a
  combination. Where the moved fork belongs to the family that is *running*, it takes that
  family's forks itself and then the family's **own scripts**, read out of its `run.sh`
  under the `# Own scripts` marker — calling the family's `run.sh` would run the moved
  fork's sibling, which is what an alternatives parent does. `--dry-run` prints each row's
  step list, which is the specification the batches that build the missing children worked
  to. `collect_conclusions.py` gathers every combination's `conclusion.json` into one table
  **and keeps the rows that have none, with the reason**. Batches 13, 22 and 14 ran all 24
  tier-1 rows, and batch 14 filled the eight tier-2 slots from `tier2_rule.md`, whose
  sha256 is unchanged from the day it was written.

  **Batch 16 ran the same set on the held-out year, from this node.** `run_manifest.py
  --dataset holdout` reads `manifest_holdout.csv` and issues, for each row, the same commands
  its development twin issued — the dataset reaches the steps through the combination name
  and nothing else. Its one different row is the main path: on development that is
  `conclude.py` alone, because the analysis had already run, and on the holdout it is the
  whole pipeline, expressed by moving no fork and opening the setup gate rather than by a
  second list of the pipeline kept in the driver. A row already recorded as run is not run
  again, which is plan §3 enforced rather than remembered. `pair_holdout_development.py`
  joins the two halves on the pairing frozen in batch 15 and refuses to report if the
  development half has moved since; the two ranked figures are drawn for either dataset from
  `scripts/lib/stability_figures.py`, with one-screen runners as the steps.

  **Batch 15 put the driver into this node's `run.sh` and reported the set.** The order is
  the phase's own — cost, plan, run tier 1, collect, plan again so the frozen pair rule can
  select from a tier 1 that exists, run tier 2, collect, report — and the two repeated steps
  are what make the node reproducible from nothing rather than from the results already on
  disk. It was safe to add because re-planning against a completed tier 1 returns
  `manifest.csv` byte-identical, which batch 15 established by running it and diffing.
  `report_distribution.py` writes the phase-D answer (`distribution.json`,
  `distribution_rows.csv`, `sensitivity_by_fork.csv`) with three figures beside it, and
  `freeze_holdout_manifest.py` writes `manifest_holdout.csv` — the set phase E runs, fixed
  before the year is opened, under `__holdout` names so a holdout row cannot overwrite the
  development result it is to be compared against. **`bash analysis/run.sh` is therefore
  about six hours rather than twenty minutes**, and reproduces both distributions as well as
  the reported result.

The tree gained no node in batch 16. An earlier note here reserved `06_holdout` for it; the
holdout turned out not to be a separate question but the same one — how far the conclusion
survives a differently-but-equally-reasonably conducted analysis — asked of a second year,
over the identical set of analyses, against the identical yardstick, with the frozen manifest
and the freeze record already living here. A node whose claim would have restated this one's
and whose scripts would have been this one's under other names is a node that makes the tree
larger and not clearer. The headline holdout number is where the headline development number
is: at the root, in `analysis/results/main__holdout/conclusion.json`, written by the same
`conclude.py`.

The tree's full design — every node, every fork, the file contract between them and the
`COMBO` mechanism — is in `AI-generated/batch-reports/26-08-26_b05_bootstrapPlan.md` §2–4.

**A result produced outside this tree does not exist.**
