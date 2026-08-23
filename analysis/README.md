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

## Currently here

`claim.md` carries the project's top-level analytical aim — whether a spatio-temporal model
of monthly dengue counts across the provinces of Laos, developed as autonomously as this
setup allows, beats its baselines and the reference model under Chap's own backtest, and how
far that answer survives the reasonable alternatives.

One child so far:

- **`01_data`** (sub-analyses) — what the dataset contains, and on what part of it
  development may happen.
  - **`01_partition`** — cuts the archived file into the development period (1998-01 to
    2009-12) and the sealed 2010 holdout, and verifies the two partition it exactly. **This
    is the only node licensed to read the full file**, and the holdout it writes
    (`holdout_2010_SEALED.csv`) stays unopened until phase E.
  - **`02_characterise`** — describes the development period only, and fixes the backtest
    scheme that every later number is computed under.

`bash analysis/run.sh` reproduces both from `Archive/lao-dataset/`, in about fifteen seconds,
and was verified to give byte-identical output on two consecutive runs.

The rest of the decomposition is designed in batch 5 of the plan and built in batch 7; the
first modelling result — one trivial model through `chap eval`, end to end — is batch 6.
Until then nothing about the modelling is real, and **a result produced outside this tree
does not exist.**
