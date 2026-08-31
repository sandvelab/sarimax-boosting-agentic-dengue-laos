#!/usr/bin/env python3
"""Whether the same judgment calls matter on the year the analysis had never seen.

Phase D's ranking says six of seventeen forks move the conclusion further than the
reference model moves on its own, and that the eleven that do not are almost exactly the
ones phase C spent three batches choosing among. That ranking was computed on the data the
choices were made against. This figure asks whether it survives.

One fork per row, two bars: how far that fork moved the conclusion on development, and how
far the same fork moved it on the held-out year. Each bar is judged against **its own**
dataset's noise band -- the reference was re-scored four times on 2010 as it was on
development -- because a band imported from one dataset would be a number from one analysis
deciding what counts as a move in another. The two bands are drawn separately for that
reason.

What to read: a fork whose two bars agree about which side of its band it falls on is a
judgment call whose importance was correctly assessed from development alone. One that
disagrees is a call the development set could not have told you about, in either direction.

Plotted values: results/fig_fork_sensitivity_both.csv -- one row per fork, two bars.
Pre-aggregation: results/fig_fork_sensitivity_preaggregation.csv and its holdout twin --
the per-combination moves each bar takes a maximum over.

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
STEM = "fig_fork_sensitivity_both"

with (RESULTS / "fork_sensitivity_both.csv").open() as handle:
    forks = list(csv.DictReader(handle))
development = json.loads((RESULTS / "distribution.json").read_text())
holdout = json.loads((RESULTS / "holdout_distribution.json").read_text())
dev_band = development["reference_noise_band"]["skill_band"]
hold_band = holdout["reference_noise_band"]["skill_band"]

shown = [{"fork": f["fork"], "stage": f["stage"], "kind": f["kind"], "owner": f["owner"],
          "development_largest_abs_delta_skill":
              float(f["development_largest_abs_delta_skill"]),
          "holdout_largest_abs_delta_skill":
              float(f["holdout_largest_abs_delta_skill"]),
          "development_moves_more_than_noise": f["development_moves_more_than_noise"],
          "holdout_moves_more_than_noise": f["holdout_moves_more_than_noise"],
          "agrees_on_whether_it_matters": f["agrees_on_whether_it_matters"]}
         for f in forks
         if f["development_largest_abs_delta_skill"] != ""
         and f["holdout_largest_abs_delta_skill"] != ""]
shown.sort(key=lambda f: f["development_largest_abs_delta_skill"])
with (RESULTS / f"{STEM}.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(shown)

colour = assign(sorted({f["kind"] for f in shown}), PALETTE)
height = 0.38
fig, ax = plt.subplots(figsize=(9.5, 6.8), constrained_layout=True)
for y, entry in enumerate(shown):
    ax.barh(y + height / 2, entry["development_largest_abs_delta_skill"],
            height=height, color=colour[entry["kind"]], zorder=3)
    ax.barh(y - height / 2, entry["holdout_largest_abs_delta_skill"],
            height=height, color=colour[entry["kind"]], alpha=0.45,
            hatch="///", edgecolor="white", linewidth=0.0, zorder=3)

ax.axvline(dev_band, color="black", linestyle="--", linewidth=1.2, zorder=5)
ax.axvline(hold_band, color="black", linestyle=":", linewidth=1.4, zorder=5)
ax.annotate("  development noise band", (dev_band, -0.45), fontsize=8.5,
            rotation=90, ha="left", va="bottom")
ax.annotate("  holdout noise band", (hold_band, -0.45), fontsize=8.5,
            rotation=90, ha="left", va="bottom")

ax.set_yticks(range(len(shown)))
ax.set_yticklabels([f"{f['stage']}" + (f"  ({f['owner']})" if f["owner"] != "-" else "")
                    for f in shown], fontsize=9)
ax.set_xlabel("largest move in the reported skill score when this fork is taken differently")
agree = sum(1 for f in shown if f["agrees_on_whether_it_matters"] == "True")
ax.set_title(f"{agree} of {len(shown)} forks agree across the two datasets about\n"
             f"whether they move the conclusion  (solid: development, hatched: 2010)",
             fontsize=11, loc="left")
handles = [plt.Line2D([], [], marker="s", linestyle="", color=c, label=k)
           for k, c in sorted(colour.items())]
ax.legend(handles=handles, loc="lower right", fontsize=9, frameon=False,
          title="fork kind", title_fontsize=9)
ax.grid(axis="x", alpha=0.25, zorder=0)

fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
