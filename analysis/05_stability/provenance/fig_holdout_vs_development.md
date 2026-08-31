# Provenance — the paired figure: development against the held-out year

```
result:              results/fig_holdout_vs_development.png
                     results/fig_holdout_vs_development.csv
script:              scripts/fig_holdout_vs_development.py
                     sha256:673b5537708019c1b3eafefd820cc426c8902e191083daa92a9ce3b7c114fffd
invocation:          "$PYTHON" scripts/fig_holdout_vs_development.py
                     (from 05_stability/, via run.sh)
inputs:              analysis/05_stability/results/holdout_vs_development.csv
                     analysis/05_stability/results/holdout_vs_development.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              609e1be
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: a dumbbell chart, one row per analysis with a line from its
                     development score to its holdout score. Rejected because the quadrants
                     are the reading — whether an analysis beat the reference on each
                     dataset — and a scatter against the diagonal shows both that and the
                     size of the drop, where a dumbbell shows only the drop.
agency:              agent-autonomous.
```

**What it establishes.** The set was fixed before the year was opened, so the cloud is not
selected. Twenty-eight of the thirty-two points are below the diagonal. Four points are in
the bottom-right quadrant — beat the reference on development, did not on 2010 — and three
are in the top-left, the same case with the sign reversed. The four rows that filter the
provinces are the extremes in both directions.

Plotted values are beside the image; nothing is aggregated in it, each coordinate being one
stored conclusion.
