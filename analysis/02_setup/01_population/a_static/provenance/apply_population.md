# Provenance — the population column, taken as the archive supplies it

```
result:              results/main/analysis_dataset.csv
                     results/main/setup_spec.json
script:              scripts/apply_population.py
                     sha256:8e70f8cc37d08e0aac52262de8f4769aa4741c424f9283cc8fb097b0b647e83e
invocation:          "$PYTHON" scripts/apply_population.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so the combination
                     is `main` and results go to results/main/.)
inputs:              analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage is the identity on the data and the diagnostic is a
                     count of distinct values; project seed 20260822 has no surface here.
commit:              959f63c
instructions-commit: cf97b81 (AGENTS.md §8 now states the node-naming rule, and
                     check_invariants enforces it; node.py no longer treats a
                     subdirectory of scripts/ as a callable step)
node:                analysis/02_setup/01_population/a_static
produced:            2026-08-26
```

**What it establishes.** The population column is constant within every province across the
whole development period — checked here rather than assumed, because the whole reason this
node is a fork is that a constant is the wrong shape for a decade of a growing population.
The stage passes the dataset through unchanged, so the file it writes is the archived
development file byte for byte.

**Why the transformation is the identity and the node still exists.** A fork whose main path
does nothing is not a redundant fork: it is the place where "we used the column as supplied"
stops being an unexamined default and becomes a recorded choice with a sibling that would do
otherwise. The sibling (`b_backcast`, a per-year series back-cast from a published growth
rate) is not implemented yet; it is built when the stability manifest needs it, in phase D.

alternatives-considered: the back-cast series is the alternative and it is the sibling this
node's parent exists to hold. A third option — dropping the population column entirely, so
that no model can use it — was rejected because it removes a covariate from the reference
model as well, and the reference is run at its own configuration, not at one we choose for
it. A fourth — normalising the column to a rate here rather than letting each model decide —
was rejected because how population enters a model is a candidate-internal question and
belongs in the subtree that moves only our own models.

agency: agent-autonomous. That the population figure is static and therefore a problem was
established by batch 3 from the data; that the main path takes it unchanged is the agent's,
on the reasoning that it is the reading with the fewest of our fingerprints on it.
information: agent-retrieved — the column's behaviour is read from the file, not recalled.
