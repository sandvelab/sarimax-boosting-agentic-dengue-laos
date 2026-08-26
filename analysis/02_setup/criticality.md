# Criticality — what `02_setup` stores, and what it would cost to lose

Written by `/annotate-criticality`. Four rough judgments per artifact, so that pruning later
is targeted rather than a panic. **This file proposes nothing and deletes nothing.**

Everything here is regenerable by `bash analysis/02_setup/run.sh` in **about two seconds**,
from `01_data`. That is what makes the table below unremarkable, and it is recorded anyway,
because the judgment is cheap now and impossible later.

Total: **1.3 MB per combination**, of which 1.1 MB is five copies of the same 224 KB CSV.

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `results/$COMBO/analysis_dataset.csv` | 224 KB | **main result** | yes, ~2 s | **highest** | What every model in the project is evaluated on. On the main path it is byte-identical to `01_data`'s development file, so on that path it is a duplicate; off the main path it is not, and it is the only record of what a combination actually put in front of the models. |
| `results/$COMBO/setup_spec.json` | 3 KB | **main result** | yes, ~2 s | **highest** | The four choices, the four evaluation flags and where each flag came from. The smallest file in the project that a reader must not lose: without it nothing says what setting a score was produced under. |
| `results/$COMBO/setup_inputs.sha256` | 1 KB | side result | yes, ~2 s | high | The bytes each stage read and wrote, in chain order. Lets a clean-room run compare against archived outputs without re-deriving them. |
| `*/results/$COMBO/analysis_dataset.csv` (four stage copies) | 224 KB each | intermediate | yes, ~2 s | medium | Rule 5's intermediates: the dataset as it leaves each fork. On the main path all four are identical to each other and to the source, so **these are the first thing to prune** if storage ever binds — 900 KB per combination for four copies of one file. Off the main path they are the record of which stage changed what, and there they are worth keeping. |

**The storage question at scale.** The perturbation manifest is about 28 combinations, so
this node contributes roughly **36 MB** across the whole stability run, of which 25 MB is the
stage copies. That is not enough to act on. If it ever were, the rule would be: keep the
assembled dataset and the specification for every combination, drop the stage copies for
combinations where `setup_spec.json` records all four transforms as the identity.
