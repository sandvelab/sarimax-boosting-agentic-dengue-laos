# Provenance — the distribution of conclusions

```
result:              results/conclusions.csv
                     results/conclusions_notes.json
script:              scripts/collect_conclusions.py
                     sha256:8576a07dbdea528c4a21968aee7b71008d90e287d16ba300c4ac5d9007d42e13
invocation:          "$PYTHON" scripts/collect_conclusions.py
                     (from 05_stability/, via run.sh)
inputs:              analysis/05_stability/results/manifest.csv
                     analysis/05_stability/results/run_status.csv
                     analysis/results/<combination>/conclusion.json — one per combination
                       that has run; at this batch, `main` alone
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              26dca49
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** The table the phase-D result is read from: one row per manifest
combination, every column copied out of that combination's own `conclusion.json`. The one
value computed here is `delta_skill_vs_main`, a subtraction of two columns on the table,
and it is here so that no report has to do it in prose.

**What it says at this batch.** 1 of 33 rows has a conclusion. That is the point of the
file's shape: rows without one are kept, each with the reason — the child has no scripts
yet, the batch that owns it has not happened, the tier-2 slot is unresolved, or the run
failed and here is the log. A stability table that silently contained only the analyses
that happened to have run would report a distribution over a set nobody chose, which is the
failure this whole node exists to prevent, one level up.

**It is not yet the phase-D result** and the file says so in
`conclusions_notes.json["note"]`. It becomes one when every row it names has run.

alternatives-considered: writing the table only once the manifest is complete — rejected,
because the record of how much of the manifest is answered is worth having at every point
between now and batch 15, and a file that appears at the end cannot be checked on the way.
Recomputing the skill score here from the leaderboards rather than reading it from
`conclusion.json` — rejected outright: the root's `conclude.py` is the only place in this
repository that states the conclusion, and a second computation of it is a second thing to
drift.

agency: agent-autonomous.
