# Criticality — what the vertical slice stores

Written by `/annotate-criticality`. Four rough judgments per artifact, so pruning later
is targeted rather than a panic. **This file proposes nothing and deletes nothing.**

Everything here is regenerable by `bash AI-internal/vertical-slice/run_vertical_slice.sh`
in **16 seconds**, from a model whose environment is pinned by a tracked lockfile and a
dataset pinned by checksum. That is what makes most of this table unremarkable — and it
is the first place in this project where a whole result set is that cheap to rebuild,
because unlike the reference model this one is deterministic.

Total tracked: **10.2 MB**, of which 9.8 MB is the evaluation `.nc`. The untracked
`slice-work/` is a further 77 MB.

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `results/main/metrics_cell.csv` | 27 KB | **main result** | yes, 16 s | **highest** | Every other number in this batch is an aggregation of this file. A reader who checks one file checks this one. |
| `results/main/metrics_summary.csv` | 197 B | main result | yes, 16 s | **highest** | The headline row. |
| `results/main/crps_by_location.csv` | 1.4 KB | main result | yes, 16 s | high | Per-province CRPS and calibration — the spread the plan requires beside the mean. |
| `results/main/crps_by_split.csv` | 350 B | main result | yes, 16 s | high | Per-split CRPS, the other required spread. |
| `results/main/crps_by_region_split.csv` | 5.6 KB | side result | yes, 16 s | medium | The two crossed. Cheap, and what a paired comparison will group on. |
| `results/main/crps_by_horizon.csv` | 151 B | side result | yes, 16 s | medium | CRPS by lead time. |
| `persistence_fitted_model.json` | 168 KB | intermediate | yes, 16 s | high | The fitted change distributions. Not a score, but it is where the whole predictive spread comes from, so a reader questioning the calibration reads this. |
| `persistence_development_eval.nc` | 9.8 MB | intermediate | yes, 16 s | medium | chap-core's own output, 371 cells × 1 000 draws. **Unlike the reference's `.nc`, this one is fully regenerable** — the model is deterministic and its environment is locked — so it is the first candidate for pruning if the manifest's storage becomes a problem. Kept for now because 16 seconds is a poor reason to discard the platform's own artifact while the tree is still being built. |
| `persistence_development_eval.log` | 2.6 KB | side result | yes, 16 s | high | Carries the rejected-region line, which is the evidence for what the headline mean is a mean over. |
| `slice_run_cost.json` | 276 B | side result | no | medium | A wall-clock measurement on one machine. Re-running gives a different number. |
| `slice_inputs.sha256` | 744 B | intermediate | yes, 16 s | high | The bytes that went in. |
| `determinism_check.json` | 800 B | main result | yes, ~35 s | **highest** | The evidence for Rule 6 at this batch. The claim it records — that there is nothing to seed — is only worth anything because it was checked. |

**The one thing here that cannot be regenerated** is `slice_run_cost.json`, and only
because wall clock is a property of the machine and the moment. Everything else is a
deterministic function of tracked inputs, which is a stronger position than batch 4
could take for the reference model.
