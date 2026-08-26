# vertical-slice — batch 6

The scripts of the vertical slice: one model, end to end, through Chap's own
evaluation on the real development dataset, at the scheme batch 3 fixed.

The point is not the score. The point is that every link in the chain has been
exercised once, with a file at every join — archived data → development file → model
contract → `chap eval` → chap-core's own metric → the contract files batch 5's design
says the claim tree consumes. Until that had happened, nothing about the modelling was
real and any effort spent on model design was effort spent on assumptions.

These live here rather than in `analysis/` because the tree is erected in batch 7.
`persistence_model/` is not a throwaway — it is one of the two baselines the plan's §4
requires — and batch 7 moves it into
`analysis/03_models/01_baselines/01_persistence/` and re-runs it from the node, so its
history follows it.

| File | Role |
|---|---|
| `persistence_model/` | the Chap-compatible model; see its own `README.md` |
| `run_vertical_slice.sh` | runs `chap eval`, times it, writes the contract files |
| `collect_metrics.py` | one evaluation file → the contract files; implements no metric |
| `verify_determinism.sh` | Rule 6: two runs, compared byte for byte |

Outputs go to `AI-generated/vertical-slice/`, which carries the `provenance.md`.
`collect_metrics.py` is the routine `analysis/04_score/01_collect` will run once the
tree exists; it accumulates rows per model, so the same call adds each later model to a
shared leaderboard without any value being retyped between steps.
