# Provenance — three countries, two arrangements, one axis

```
result:              results/fig_external_skill.png
                     results/fig_external_skill.csv   (the plotted values)
script:              scripts/fig_external_skill.py
                     sha256:97d62741f233a158cbf92d7520e954d2df076bc75536597292170ff87e555425
invocation:          "$PYTHON" scripts/fig_external_skill.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              results/external_conclusions.csv
                     results/external_vs_laos.json
                     analysis/scripts/lib/palette.py (one colour per country, stable)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     matplotlib with the Agg backend
seeds:               none.
commit:              bfbc096 — the tree the four rows ran from. The script
                     itself is carried by batch 20's closing commit, which
                     changed nothing under analysis/ that had already run.
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                analysis/06_external
produced:            2026-09-04
alternatives-considered: a bar chart per country and arrangement, which shows the six
                     values and hides the thing the figure is for — the slope between a
                     country's two points is the development-to-final-year drop, and a
                     slope is what the eye reads without being told.
agency:              agent-autonomous
```

**Plotted values** are in `fig_external_skill.csv`, one row per point with its band, as Rule
7 requires. **Pre-aggregation values**: none at this node. Each point is one stored
`conclusion.json`; the values it aggregates are the per-cell scores under
`analysis/04_score/01_collect/results/<combination>/metrics_cell.csv`, which no axis here
averages and which the hierarchical report descends to.

**The band on each point** is the reference model's own re-run spread on that dataset,
expressed in skill. It is drawn per point rather than as one rule across the figure because
it is a draw and not a constant: the reference is unseeded, and on Laos's development
backtest this project has drawn that band four times, at 0.0218 to 0.0483 of skill.

---

## 2026-09-04 — batch 20 — the province count moves into the legend

```
script:              analysis/06_external/scripts/fig_external_skill.py
                     sha256:85b823a4c2ab01a7435d811509404713c2169c34bd6acd1c55a3c3cd0ee311e8
commit:              bfbc096
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
```

**What changed.** The province count moved from an annotation beside each country's
development point into the legend, and the title's third line was wrapped. Thailand and
Vietnam score within 0.0004 of each other on that arrangement, so the two annotations were
drawn on top of one another; and the title ran off the canvas.

**What it changed in the plotted values: nothing.** `fig_external_skill.csv` is written
before any drawing and is byte-identical across the two renders. The figure this record
describes is the second render.

**What has run under this version.** The render of
`results/fig_external_skill.png` that is in the repository.
