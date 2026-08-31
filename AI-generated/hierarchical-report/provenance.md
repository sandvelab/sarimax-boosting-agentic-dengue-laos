# Provenance — the hierarchical report

The append-only record of each build. Everything else in this folder is generated and is
rebuilt by the command below; this file is not, and is never overwritten.

## The first build — 2026-08-31, batch 17

```
result:              AI-generated/hierarchical-report/   (index.html and 1 175 pages)
script:              AI-internal/useful-scripts/build_hierarchical_report.py
                     sha256:bd4855e7282a9bc0604d0a1263a02060fd1d257eeaa5969b2b153e9b534cd28e
                     imports AI-internal/useful-scripts/claims.py
                     sha256:f9c2951668c503c726ead0dabf626cf1a56875554ea62c3dc78516c7e4330ab3
invocation:          .venv/bin/python AI-internal/useful-scripts/build_hierarchical_report.py
                     (from the repository root; /hierarchical-report adds --open)
inputs:              analysis/ -- every node's claim.md, results/, scripts/, provenance/ and
                     run.sh; Human-AI-collaboration/claims/claims.md, for the claims each
                     node carries; and, for the levels below the tree,
                     04_score/01_collect/results/<combo>/metrics_cell.csv and models.csv,
                     the child of 04_score/02_aggregate that ran under each combination,
                     04_score/03_compare/results/<combo>/leaderboard.csv, and
                     analysis/results/<combo>/conclusion.json
environment:         .venv/bin/python -- CPython 3.13.7, the repository's own machinery
                     interpreter. The report reads files and does not run the analysis, so
                     environment/ is not involved
seeds:               none; the build draws nothing
commit:              ce43d47
instructions-commit: cf97b81
node:                not a node -- a view over the tree, like check_invariants.py is a check
                     on it
produced:            2026-08-31
```

**What it establishes.** That a reported number can be descended to the values it is made
of, by clicking rather than by asking. The tree supplies the upper levels; below them sit
four more — the national mean each model is reported at, that mean by province, each
province by month, and the per-cell CRPS everything above is an average of — for each of
the 65 combinations that were scored, on both datasets.

**Reproducible, and checked by running it twice.** Two builds into different directories
are byte-identical, README included. The only inputs that move between builds are the
date and the commit, both of which are recorded on the page.

**Nothing here recomputes an aggregate.** Every figure shown is displayed from the file the
analysis wrote — `metrics_summary.csv` for the national level, `crps_by_location.csv` for
the province level, `metrics_cell.csv` for the values, `conclusion.json` for the
conclusion. A report that re-derived its own means could disagree with the analysis about a
number and look right doing it, which is the failure `AGENTS.md` §1 is about, arriving in
the thing that displays the results rather than in the thing that computes them. The one
consequence is that the report cannot show what the analysis did not store: there is no
per-split, per-province breakdown anywhere below the province page, because the aggregation
node does not write one. That is the diagnostics gap batch 22 opened and batches 14, 15 and
16 declined to close, seen from the other end.

**Which child of the weighting fork a combination was aggregated under is discovered, not
named** — the one child of `04_score/02_aggregate` with results under that combination.
That is the rule every downstream step in the tree already follows, and it is why the
case-weighted and population-weighted rows show their own weighting in the page's tag
rather than the main path's.

**Two things it deliberately does not list.** Paths the repository declines to version —
the virtual environment `uv` builds inside a model's contract directory, `__pycache__`,
chap-core's per-split `work/` — because they are not the analysis's material. Before that
filter, `c_ensemble`'s "Scripts" section was 6 117 files, of which 11 were the node's.
And combinations that appear in a manifest but produced no scores: the report shows what is
on disk, and `05_stability/results/run_status.csv` is where a row that did not run is
reported.

**Why the folder's own README is generated and this file is not.** A hand-kept description
of a generated folder goes stale silently, which is the failure the "never hand-edit"
rule exists to prevent, so the README is written by the build. A record of *how* the build
happened cannot be written by the build without becoming an assertion the build makes about
itself, so it is written here, appended to, and versioned — which is why `.gitignore` now
excludes the folder's contents rather than the folder.

alternatives-considered: linking each node's results as a flat file list, which is what the
report did through batch 16 and which stopped being readable at sixty-five combinations —
the reported analysis would have been one entry among sixty-four perturbations of itself;
grouping by combination, with `main` and its holdout twin open and the rest folded, is what
replaced it. Building the detail pages only for `main` and `main__holdout`, which would
have been a tenth of the pages and would have made the reported analysis the only one a
reader could descend, in a project whose whole finding is that the reported analysis is one
member of a distribution. Sharing one stylesheet instead of inlining the CSS in every page,
which would save about 1.8 MB of 18; rejected because a page that carries its own styling
still opens in twenty years if it is moved on its own, and storage is not a constraint here
(human-set, 2026-08-29).

agency: agent-autonomous. Rule 8 and the requirement that the levels run national → province
→ month down to the values are the plan's; how the tree and the stored files are turned into
those levels is this batch's.

## Rebuilt after the collection closed — 2026-08-31, batch 17

```
result:              AI-generated/hierarchical-report/   (unchanged in structure)
script:              unchanged
invocation:          unchanged
inputs:              Human-AI-collaboration/claims/claims.md, which gained C39 after the
                     first build; the rest unchanged
commit:              cf6005e
produced:            2026-08-31
```

The claim collection is an input to the report — each node page carries the claims resting
on it — so adding a claim after a build leaves the report a claim short. Rebuilt, and the
count on the node pages is now the 39 the collection holds. Recorded rather than folded into
the entry above, because the first build's commit is what its own README and index page
state, and overwriting that would make the page disagree with the record of it.
