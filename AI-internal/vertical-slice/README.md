# vertical-slice — batch 6

The scripts of the vertical slice: one model, end to end, through Chap's own
evaluation on the real development dataset, at the scheme batch 3 fixed.

The point is not the score. The point is that every link in the chain has been
exercised once, with a file at every join — archived data → development file → model
contract → `chap eval` → chap-core's own metric → the contract files batch 5's design
says the claim tree consumes. Until that had happened, nothing about the modelling was
real and any effort spent on model design was effort spent on assumptions.

These live here rather than in `analysis/` because the tree was erected in batch 7.
`persistence_model/` was not a throwaway — it is one of the two baselines the plan's §4
requires — and **batch 7 moved it into
`analysis/03_models/01_baselines/01_persistence/a_empiricalChange/scripts/persistence_model/`**
and re-ran it from the node, unchanged, where it reproduced this batch's mean CRPS to the
last digit. Its git history followed it, so the move is one commit rather than a copy that
will drift.

`run_vertical_slice.sh` therefore points at a directory that has moved on, and it is left
that way on purpose: it is the record of what batch 6 ran, and batch 6 is reproducible from
the commit its provenance records name (`ced3e1a`). The model is not duplicated here,
because two copies of a model are two models.

| File | Role |
|---|---|
| `run_vertical_slice.sh` | runs `chap eval`, times it, writes the contract files |
| `collect_metrics.py` | one evaluation file → the contract files; implements no metric |
| `verify_determinism.sh` | Rule 6: two runs, compared byte for byte |

Outputs go to `AI-generated/vertical-slice/`, which carries the `provenance.md`. **None
of those numbers is a reported result of the project** — the tree's are, and the tree
reproduces them.

`collect_metrics.py` was the routine `analysis/04_score/01_collect` now runs. The node's
version discovers the models that ran instead of being told one per call, and carries the
unseeded reference's repeats; what it does not do is implement a metric, which is the part
that had to be right and was.
