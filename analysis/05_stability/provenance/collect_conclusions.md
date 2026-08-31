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


---

## Batch 22 — ten of thirty-three rows

```
result:              results/conclusions.csv
                     results/conclusions_notes.json
script:              scripts/collect_conclusions.py — unchanged by this batch
invocation:          environment/chapenv/bin/python \
                       analysis/05_stability/scripts/collect_conclusions.py
inputs:              analysis/results/<combination>/conclusion.json for every combination
                     the manifest names, and results/manifest.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** Ten of the twenty-four tier-1 rows now have conclusions. Skill
across them spans **+0.1206 to +0.2320**, and the two new rows are the extremes of the
*model* forks: `persistence_negBinomialFloor` is the lowest skill score in the set so far and
`climatology_frozenWindow` is the closest to the main path of any row at all. **The main path
is no longer at the bottom of the range**, which it was after batch 13.

alternatives-considered: none at this node.

agency: agent-autonomous.
information: agent-retrieved — read from results/conclusions.csv.

---

## The phase-E half (batch 16)

```
result:              results/holdout_conclusions.csv
                     results/holdout_conclusions_notes.json
script:              scripts/collect_conclusions.py
                     sha256:c3f6dd74899b7440f178a1f8f6cd461ac217cb42745658cf29002cf97a787f89
invocation:          "$PYTHON" scripts/collect_conclusions.py --dataset holdout
                     (from 05_stability/, via run.sh)
inputs:              analysis/05_stability/results/manifest_holdout.csv
                     analysis/05_stability/results/run_status_holdout.csv
                     analysis/results/<combination>__holdout/conclusion.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every column is copied, and the three that are not are
                     subtractions on this table's own columns.
commit:              609e1be
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: one table with a dataset column, holding both. Rejected because a
                     summary over it would pool 2009 and 2010 rows, and phase E's whole
                     shape is the two spreads read side by side. They are joined, row by
                     row on the frozen pairing, by pair_holdout_development.py.
agency:              agent-autonomous.
```

**What it establishes.** 32 of the frozen set's 33 rows have a conclusion on the held-out
year; the one that does not is the held row, and its reason is carried from the driver
rather than restated. Deltas are measured from `main__holdout`, found by its kind rather
than by its name — naming the combination would have worked on development and silently
found nothing here.
