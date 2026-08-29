# Criticality — what `05_stability` stores, and what the manifest will store

Written by `/annotate-criticality`. **This file proposes nothing and deletes nothing.**

Two things are annotated here: the node's own outputs, which are tiny and mostly
regenerable, and **the storage the perturbation manifest implies**, which is the batch's
real answer to the reproducibility-against-storage trade-off. Every figure below is read
from `results/manifest_notes.json["storage"]`, which measures the parts on disk rather
than estimating them.

## This node's own outputs

Total: **under 200 KB**, all of it regenerable by `bash analysis/05_stability/run.sh` in
about fifteen seconds.

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `results/manifest.csv` | 8 KB | **main result** | yes, ~2 s, but see below | **highest** | The set of analyses phase D runs, fixed before any of them ran. The single most important small file in the phase: a reader who wants to know whether the stability result was selected after the fact reads this and its commit date. |
| `results/tier2_rule.md` | 2 KB | **main result** | yes, ~0 s — it is a constant in the planner | **highest** | The pair-selection rule, and the thing that makes tier 2 honest. Its sha256 is in `manifest_notes.json`; a change to the text is a change to the method and shows up as one. |
| `results/manifest_notes.json` | 8 KB | **main result** | yes, ~2 s | **highest** | The totals, the budget, the cut order, what is not costed, and the twelve directories a manifest row would overwrite. Everything a reader needs to check that the absences were decided rather than defaulted. |
| `results/forks.csv` | 2 KB | main result | yes, ~1 s | high | The inventory: 17 forks, their kinds, their children, which are built. |
| `results/conclusions.csv` | 8 KB now, ~12 KB full | **main result** | yes, ~1 s, **only while the combinations' `conclusion.json` files survive** | **highest** | What phase D concludes, one row per analysis. The proviso is the whole storage question and it is settled at `03_models`, not here. |
| `results/conclusions_notes.json` | 2 KB | main result | yes, ~1 s | high | How much of the manifest is answered, and why the rest is not. |
| `results/step_costs.json` | 1 KB | side result | yes, ~15 s — **and it comes back different** | medium | Wall-clock measurements. Re-measuring changes the numbers by tens of percent and changes nothing about the manifest's row set. |
| `results/run_status.csv` | 1 KB | side result | **no** — it records what happened when the driver ran | high | Per row: ran, failed, not built, pending. A history, not a derivation. |
| `results/logs/*.log` | ~1 KB per row now; up to a few MB for a setup row | intermediate | no | medium | The driver's own transcript per combination. Not regenerable in the sense that matters: a re-run writes a new one. First candidate for pruning at this node, and the node is not where the storage question is. |

**`manifest.csv` is regenerable and must not be regenerated casually.** The planner rebuilds
it from the tree, so re-running it after a fork is added is correct and required. Re-running
it after tier 1 has conclusions *fills in* tier 2 and is also correct. What would not be
correct is rebuilding it with the tier-2 rule changed, and the rule's recorded sha256 is
what makes that visible.

## What the manifest implies for the rest of the tree

| | Measured |
|---|---|
| Everything under `analysis/**/results/` now | **234 MB** |
| One `eval.nc` | 9.4 MB |
| The per-cell CSV derived from it | 0.18 MB |
| One setup combination — dataset, four models, scores | ~82 MB |
| One candidate combination — our model and scores | ~12 MB |
| One scoring combination — re-aggregation only | ~1.5 MB |
| Tier 1 on development, 23 new combinations | **575 MB** |
| Tier 1 on development **and** holdout | **1.15 GB** |

Tier 2 adds perhaps another 500 MB depending on how many of its pairs move a setup fork.
So phase D roughly **doubles the repository's stored results twice over**, to somewhere
near 2 GB, and nothing about that binds: the built model environments under
`analysis/**/work/` are already 2.1 GB and are gitignored and regenerable.

**The prune target is unambiguous and it is not here.** `chap eval`'s NetCDF is fifty times
the size of the per-cell CSV that everything downstream actually reads. The trade-off — for
our own models the `.nc` is regenerable in about a minute, and for the reference it is not
regenerable at all because the model is unseeded — is annotated at `03_models/criticality.md`
where those files live, and phase D changes the scale of that judgment without changing its
shape.

**Nothing is deleted now.** `AGENTS.md` §6: keep everything while it is affordable and
annotate it well enough that pruning later is targeted. At 2 GB on a laptop it is
affordable, and the annotation is here for the day it is not.

## Added in batch 22 — two more rows against the projection

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `results/logs/{climatology_frozenWindow,persistence_negBinomialFloor}.log` | 12 KB together | intermediate | yes, with the row | medium | Each row's step-by-step transcript. Small, and the only place a row's failure mode is legible after the fact — the first attempt at both rows failed here before anything was written. |
| `results/conclusions.csv` | 4 KB | **main result** | yes, seconds, from the conclusion files | **highest** | Ten of thirty-three rows. It is the distribution phase D exists to produce. |

**Ten rows of the twenty-four, and the storage projection is the number to watch.** Every
combination on disk now holds **660.2 MB**, against a projection of **584.7 MB for the whole
of tier 1 on development** and **1 169.4 MB across both datasets**
(`results/manifest_notes.json["storage"]`, where all three are computed by the planner from
measured parts rather than estimated). The development projection is already exceeded, because
what is on disk includes the fourteen phase-C combinations the manifest does not count as tier
1 — so the projection is not wrong, but the disk is filling from two sources and only one of
them was budgeted. Compute is still four times inside its budget; storage is the one that will
bind first. Nothing is deleted, and the table above says what would go first if anything did.
