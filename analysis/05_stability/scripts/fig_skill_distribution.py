#!/usr/bin/env python3
"""Every analysis the manifest named, on one axis, with the reported one marked.

This is the phase-D result as a picture: thirty-two conclusions, each from an analysis
that looked as reasonable as the one this project reports, ranked by the number the
project reports. Three reference lines carry the reading.

**Zero** is where our model and the reference model score the same. A point above it is an
analysis in which we beat the reference; the question the project asks is not where the
best point is but how many are on which side.

**The main path** is a line, not a highlight, because it is one member of the set and not
its centre. It sits thirteenth of thirty-two, which is the fact a single headline number
would hide.

**The band** is the reference's own re-run noise, measured rather than assumed: the
reference model is unseeded and was scored four times, and the band spans our model's skill
score against each of those four. A point inside it differs from the main path by less
than the reference's sampler moves it on its own, so that analysis has not been shown to
conclude anything different.

Colour is the fork's kind, which is what the figure is really about: the block that
scatters is the one that changes which model is ours, and the block that does not is the
one phase C spent three batches choosing inside.

`--dataset holdout` draws the same figure for the frozen phase-E set on the held-out
year, from that dataset's own rows and its own noise band. The two are separate figures
rather than two series on one, because the axis is a skill score against a reference that
faced a different year: the numbers are comparable, but a reader looking at one cloud
would read a spread across both datasets as a spread across analyses.

Plotted values: results/fig_skill_distribution.csv -- one row per point.
Pre-aggregation: none. Each point is one stored conclusion, not a summary of several;
the values these conclusions aggregate are the per-cell scores under
`04_score/01_collect/results/<combination>/metrics_cell.csv`, which the conclusion files
name and which no axis here averages.

Seeds: none.
"""
from __future__ import annotations

import argparse
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

parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
parser.add_argument("--dataset", choices=("development", "holdout"),
                    default="development")
args = parser.parse_args()
HOLDOUT = args.dataset == "holdout"
PREFIX = "holdout_" if HOLDOUT else ""
STEM = f"{PREFIX}fig_skill_distribution"

with (RESULTS / f"{PREFIX}distribution_rows.csv").open() as handle:
    rows = list(csv.DictReader(handle))
summary = json.loads((RESULTS / f"{PREFIX}distribution.json").read_text())
band = summary["reference_noise_band"]["skill_against_each_repeat"]
main_skill = summary["reported_conclusion"]["skill_score"]

shown = [{"combination": r["combination"], "tier": r["tier"], "kind": r["kind"],
          "skill_score": float(r["skill_score"]),
          "delta_skill_vs_main": float(r["delta_skill_vs_main"]),
          "inside_reference_noise_band": r["inside_reference_noise_band"]}
         for r in rows]
shown.sort(key=lambda r: r["skill_score"])
with (RESULTS / f"{STEM}.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(shown)

colour = assign(sorted({r["kind"] for r in shown}), PALETTE)

fig, ax = plt.subplots(figsize=(9.5, 9.0), constrained_layout=True)
ax.axvspan(min(band), max(band), color="0.85", zorder=0,
           label="the reference's own re-run spread")
ax.axvline(0.0, color="black", linewidth=1.0, zorder=1)
ax.axvline(main_skill, color="0.35", linestyle="--", linewidth=1.2, zorder=2)

for y, row in enumerate(shown):
    ax.scatter(row["skill_score"], y, s=95, color=colour[row["kind"]],
               marker="D" if row["tier"] == "2" else "o",
               edgecolor="white", linewidth=1.0, zorder=3)
ax.set_yticks(range(len(shown)))
ax.set_yticklabels([r["combination"] for r in shown], fontsize=8)
ax.set_ylim(-0.8, len(shown) - 0.2)
ax.set_xlabel("skill score against the reference model,  1 − CRPS(ours) / CRPS(reference)")
ax.annotate("the reference\nscores the same", (0.0, len(shown) - 0.6), fontsize=8,
            ha="center", va="top", color="black")
ax.annotate("reported", (main_skill, -0.7), fontsize=8, ha="center", va="bottom",
            color="0.35")
ax.set_title(f"{len(shown)} analyses that all looked reasonable, on the "
             f"{'held-out year' if HOLDOUT else 'development period'}\n"
             f"Diamonds move two forks at once; circles move one",
             fontsize=11, loc="left")
handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, label=k)
           for k, c in sorted(colour.items())]
ax.legend(handles=handles, loc="lower right", fontsize=9, frameon=False,
          title="fork kind", title_fontsize=9)
ax.grid(axis="x", alpha=0.25, zorder=0)

fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
