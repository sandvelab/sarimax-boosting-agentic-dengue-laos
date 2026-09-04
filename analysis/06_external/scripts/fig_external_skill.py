#!/usr/bin/env python3
"""Three countries, two arrangements each, on one axis.

The reported model's skill score against the reference model, on the development backtest
and on the final year, for Laos and for the two sibling countries it was never developed
on. One line per country, joining its two points, so the **slope** is the thing the eye
reads: that slope is the development-to-final-year drop, which is what phase E measured on
Laos and could not tell apart from 2010 being a hard year.

Two things are drawn around the points rather than stated beside them.

**Zero** is where our model and the reference score the same. A point below it is a country
where the reported model, unchanged, lost to the field's own model.

**The band on each point** is the reference model's own re-run spread on that dataset,
expressed in skill: the largest paired difference between two of its four unseeded repeats,
divided by its mean CRPS. A difference smaller than that band cannot be attributed to a
model at all. The band is itself a draw and not a constant, which is why it is drawn per
point rather than as one rule across the figure.

Plotted values: results/fig_external_skill.csv -- one row per point, with its band.
Pre-aggregation: none at this node. Each point is one stored `conclusion.json`; the values
it aggregates are the per-cell scores under
`04_score/01_collect/results/<combination>/metrics_cell.csv`.

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
STEM = "fig_external_skill"

ORDER = ["development", "final"]
LABELS = {"development": "development backtest\n2008-01..2009-12, 8 splits",
          "final": "final year\n2010, 4 splits"}

with (RESULTS / "external_conclusions.csv").open() as handle:
    table = list(csv.DictReader(handle))
summary = json.loads((RESULTS / "external_vs_laos.json").read_text())

shown = [{"country": r["country"],
          "arrangement": r["arrangement"],
          "combination": r["combination"],
          "skill_score": float(r["skill_score"]),
          "reference_repeat_spread_skill": float(r["reference_repeat_spread_skill"]),
          "crps_ours": float(r["crps_ours"]),
          "crps_reference": float(r["crps_reference"]),
          "n_cells": int(r["n_cells"]),
          "n_locations": int(r["n_locations"])}
         for r in table]
shown.sort(key=lambda r: (r["country"], ORDER.index(r["arrangement"])))
with (RESULTS / f"{STEM}.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(shown)

countries = sorted({r["country"] for r in shown})
colour = assign(countries, PALETTE)
x = {name: i for i, name in enumerate(ORDER)}

fig, ax = plt.subplots(figsize=(7.6, 6.4), constrained_layout=True)
ax.axhline(0.0, color="black", linewidth=1.0, zorder=1,
           label="our model and the reference score the same")

for country in countries:
    points = [r for r in shown if r["country"] == country]
    points.sort(key=lambda r: ORDER.index(r["arrangement"]))
    xs = [x[r["arrangement"]] for r in points]
    ys = [r["skill_score"] for r in points]
    # The province count goes in the legend, not beside the point: Thailand and Vietnam
    # score within 0.0004 of each other on the development arrangement, so two labels
    # there would sit on top of one another.
    ax.plot(xs, ys, color=colour[country], linewidth=2.0, marker="o", markersize=11,
            markeredgecolor="white", markeredgewidth=1.2, zorder=3,
            label=f"{country} — {points[0]['n_locations']} provinces")
    for r in points:
        band = r["reference_repeat_spread_skill"]
        ax.errorbar(x[r["arrangement"]], r["skill_score"], yerr=band, fmt="none",
                    ecolor=colour[country], elinewidth=1.4, capsize=6, alpha=0.65,
                    zorder=2)
    ax.annotate(f"  {country}", (xs[-1], ys[-1]), fontsize=10, ha="left", va="center",
                color=colour[country])

ax.set_xticks(list(x.values()))
ax.set_xticklabels([LABELS[name] for name in ORDER], fontsize=9)
ax.set_xlim(-0.55, len(ORDER) - 0.25)
ax.set_ylabel("skill score,  1 − CRPS(ours) / CRPS(reference)")
drops = "   ".join(f"{k} {v:+.3f}" for k, v in sorted(
    {**{"Laos": summary["lao_drop"]}, **summary["external_drops"]}.items())
    if v is not None)
ax.set_title("the reported model, unchanged, on two countries it was never developed on\n"
             f"the drop to the final year, in skill:\n{drops}",
             fontsize=10.5, loc="left")
ax.legend(loc="lower left", fontsize=9, frameon=False)
ax.grid(alpha=0.25, axis="y", zorder=0)

fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
