#!/usr/bin/env python3
"""The same thirty-two analyses, on the year they were developed against and on 2010.

One point per analysis, its development skill score against its holdout skill score. The
frozen set is what makes the figure honest: which analyses appear here was fixed before
the year was opened, so a point cannot have been added because of where it landed.

Three lines carry the reading.

**The diagonal** is where an analysis scored the same on both. Points below it did better
on the data they were developed against than on the year they had never seen, and the
vertical distance from the diagonal is exactly the inflation the plan asks this project to
measure. Points above it did better on 2010.

**Zero on each axis** is where our model and the reference model score the same on that
dataset. The quadrant a point is in says whether the conclusion -- we beat the field's own
model -- held on that dataset, and the bottom-right quadrant is the one the plan warns
about: analyses that beat the reference on development and did not on the holdout.

**The reported analysis** is marked, because it is one member of the set and the reader
needs to see where in the cloud it sits rather than be told.

Colour is the fork's kind, as in the two ranked figures beside this one, so the block that
scatters can be recognised across all three.

Plotted values: results/fig_holdout_vs_development.csv -- one row per point.
Pre-aggregation: none. Each coordinate is one stored conclusion; the values those
conclusions aggregate are the per-cell scores under
`04_score/01_collect/results/<combination>/metrics_cell.csv`, which no axis here averages.

Seeds: none.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "lib"))
from palette import assign, PALETTE  # noqa: E402

NODE = Path(__file__).resolve().parent.parent
RESULTS = NODE / "results"
STEM = "fig_holdout_vs_development"

with (RESULTS / "holdout_vs_development.csv").open() as handle:
    rows = list(csv.DictReader(handle))
summary = json.loads((RESULTS / "holdout_vs_development.json").read_text())
reported = summary["the_reported_analysis"]

shown = [{"combination": r["combination"], "tier": r["tier"], "kind": r["kind"],
          "development_skill_score": float(r["development_skill_score"]),
          "holdout_skill_score": float(r["holdout_skill_score"]),
          "skill_holdout_minus_development":
              float(r["skill_holdout_minus_development"])}
         for r in rows]
shown.sort(key=lambda r: r["combination"])
with (RESULTS / f"{STEM}.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(shown)

colour = assign(sorted({r["kind"] for r in shown}), PALETTE)
xs = [r["development_skill_score"] for r in shown]
ys = [r["holdout_skill_score"] for r in shown]
lo = min(min(xs), min(ys), 0.0) - 0.05
hi = max(max(xs), max(ys), 0.0) + 0.05

fig, ax = plt.subplots(figsize=(8.4, 8.0), constrained_layout=True)
ax.plot([lo, hi], [lo, hi], color="0.35", linestyle="--", linewidth=1.2, zorder=1,
        label="the same score on both")
ax.axhline(0.0, color="black", linewidth=1.0, zorder=1)
ax.axvline(0.0, color="black", linewidth=1.0, zorder=1)

for row in shown:
    ax.scatter(row["development_skill_score"], row["holdout_skill_score"], s=95,
               color=colour[row["kind"]],
               marker="D" if row["tier"] == "2" else "o",
               edgecolor="white", linewidth=1.0, zorder=3)

ax.scatter([reported["development_skill_score"]], [reported["holdout_skill_score"]],
           s=320, facecolor="none", edgecolor="black", linewidth=1.6, zorder=4)
ax.annotate("  the reported analysis",
            (reported["development_skill_score"], reported["holdout_skill_score"]),
            fontsize=9, ha="left", va="center")

ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.set_aspect("equal")
ax.set_xlabel("skill score on the development period,  1 − CRPS(ours) / CRPS(reference)")
ax.set_ylabel("skill score on the held-out year")
ax.set_title(f"{len(shown)} analyses, fixed before 2010 was opened\n"
             f"{summary['the_gap']['rows_worse_on_the_holdout']} of {len(shown)} scored "
             f"worse on the year they had not seen",
             fontsize=11, loc="left")
handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, label=k)
           for k, c in sorted(colour.items())]
handles.append(plt.Line2D([], [], linestyle="--", color="0.35",
                          label="the same score on both"))
ax.legend(handles=handles, loc="upper left", fontsize=9, frameon=False,
          title="fork kind", title_fontsize=9)
ax.grid(alpha=0.25, zorder=0)

fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
