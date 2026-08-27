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

## Currently here

- **`01_data`** (sub-analyses) — what the dataset contains, and on what part of it
  development may happen.
  - **`01_partition`** — cuts the archived file into the development period (1998-01 to
    2009-12) and the sealed 2010 holdout, and verifies the two partition it exactly. **This
    is the only node licensed to read the full file**, and the holdout it writes
    (`holdout_2010_SEALED.csv`) stays unopened until phase E.
  - **`02_characterise`** — describes the development period only, and fixes the backtest
    scheme that every later number is computed under.
- **`02_setup`** (sub-analyses) — the common ground every model faces. Four forks in
  sequence, each handing the dataset on: `01_population`, `02_trainingWindow`,
  `03_provinces`, `04_retrain`. The node's own script assembles their output into the one
  `analysis_dataset.csv` and the one set of evaluation flags every model reads, so a model
  never needs to know how many stages the setup has. **Every fork here re-scores every
  model, ours and the reference alike.**
- **`03_models`** (sub-analyses) — what each model forecasts on that common ground.
  - **`01_baselines`** — `01_persistence` (a fork on how a predictive distribution is
    wrapped around a point forecast) and `02_climatology` (a fork on which window estimates
    the seasonal distribution).
  - **`02_reference`** — WHO EWARS-csd at its own defaults, pinned by image digest, served
    as a container, run four times because it is unseeded.
  - **`03_candidate`** (alternatives) — our own model families, one child per family.
    `a_hierNB` is the main path and so far the only one built: a hierarchical
    negative-binomial GLM, with four sub-analysis forks deciding what it is —
    `01_observation`, `02_covariates`, `03_population`, `04_fitTime`. Each writes a
    `model_option_spec.json`; the node's own `assemble_candidate_config.py` merges
    whichever child of each ran into the one `model_configuration.yaml` that `chap eval`
    is pointed at, and adds the component seed. `b_boosted` and `c_ensemble` are batches
    10 and 11. **Every fork here moves only our model**, which is what distinguishes this
    subtree from `02_setup`.
  - `scripts/lib/chap_eval.py` is the single route by which a model of ours reaches
    `chap eval`. It is a library, not a step.
- **`04_score`** (sub-analyses) — `01_collect` (per-cell scores for every model that ran,
  from chap-core's own metrics), `02_aggregate` (a fork on the weighting of the headline
  mean), `03_compare` (the leaderboard, and the paired per-cell comparison against the
  reference with the noise floor beside it).
- The root's own `scripts/lib/project_seed.py` reads the one project seed from
  `readme-at-start.md` and derives a component seed from it by BLAKE2b. A library, not a
  step; imported by the nodes that have something to seed. First used by `03_candidate`,
  which is the first component in the project that draws at all.
- The root's own `scripts/conclude.py` writes `results/$COMBO/conclusion.json`: the skill
  score against the reference, with raw CRPS and coverage beside it. **Nothing anywhere else
  in the repository states the conclusion**, so nothing can drift from it.

Still to come: `05_stability` (batch 12), which holds the perturbation manifest and the
driver, and `06_holdout` (batch 16). The holdout node does not exist while the seal is on,
because `analysis/run.sh` must not be able to open the sealed file by accident.

The tree's full design — every node, every fork, the file contract between them and the
`COMBO` mechanism — is in `AI-generated/batch-reports/26-08-26_b05_bootstrapPlan.md` §2–4.

**A result produced outside this tree does not exist.**
