#!/usr/bin/env python3
"""Which judgment calls the conclusion is sensitive to, and which it is not.

The plan calls this the most valuable single output of the project, and it is one bar per
fork: how far the reported conclusion moves when that choice is taken differently, largest
first. Everything below the dashed line moves it by less than the reference model's own
unseeded re-run noise, and is therefore a choice this evaluation cannot see.

Two readings the ranking makes hard to avoid. The choice of **model family** is worth an
order of magnitude more than any choice made inside a family — so the eleven forks phase C
spent three batches selecting among sit below the line together, and the one decision that
mattered was which pool to build rather than how to configure its members. And the largest
move that touches no model at all is **how the headline mean is weighted**, which re-runs
nothing and re-aggregates a stored file.

`--dataset holdout` draws the same ranking for the held-out year, against that year's own
noise band. Whether the same forks come out above the line is the phase-E question about
this figure, and `results/fork_sensitivity_both.csv` is where the two rankings are joined.

Plotted values: results/fig_fork_sensitivity.csv -- one row per bar.
Pre-aggregation: results/fig_fork_sensitivity_preaggregation.csv -- the per-combination
moves each bar takes a maximum over, so a fork whose two children disagree can be seen to.

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
STEM = f"{PREFIX}fig_fork_sensitivity"

with (RESULTS / f"{PREFIX}sensitivity_by_fork.csv").open() as handle:
    forks = list(csv.DictReader(handle))
with (RESULTS / f"{PREFIX}distribution_rows.csv").open() as handle:
    analyses = list(csv.DictReader(handle))
summary = json.loads((RESULTS / f"{PREFIX}distribution.json").read_text())
floor = summary["reference_noise_band"]["skill_band"]

shown = [{"fork": f["fork"], "stage": f["stage"], "kind": f["kind"],
          "owner": f["owner"],
          "largest_abs_delta_skill": float(f["largest_abs_delta_skill"]),
          "signed_delta_skill": float(f["signed_delta_skill"]),
          "largest_move_combination": f["largest_move_combination"],
          "moves_more_than_reference_noise": f["moves_more_than_reference_noise"],
          "sensitivity_rank": f["sensitivity_rank"]}
         for f in forks if f["largest_abs_delta_skill"] != ""]
shown.sort(key=lambda f: f["largest_abs_delta_skill"])
with (RESULTS / f"{STEM}.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(shown)

# The per-row moves behind each bar: every tier-1 analysis, keyed by the fork it moved.
pre = [{"fork": r["fork"], "combination": r["combination"], "child": r["child"],
        "kind": r["kind"], "delta_skill_vs_main": r["delta_skill_vs_main"]}
       for r in analyses if r["tier"] == "1" and r["fork"] != "-"]
pre.sort(key=lambda r: (r["fork"], r["combination"]))
with (RESULTS / f"{STEM}_preaggregation.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(pre[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(pre)

behind = {}
for row in pre:
    behind.setdefault(row["fork"], []).append(float(row["delta_skill_vs_main"]))

colour = assign(sorted({f["kind"] for f in shown}), PALETTE)

fig, ax = plt.subplots(figsize=(9.5, 6.4), constrained_layout=True)
positions = range(len(shown))
ax.barh(list(positions), [f["largest_abs_delta_skill"] for f in shown],
        color=[colour[f["kind"]] for f in shown], height=0.66, zorder=3)
for y, entry in enumerate(shown):
    for value in behind.get(entry["fork"], []):
        ax.scatter(abs(value), y, s=16, color="white", edgecolor="0.25",
                   linewidth=0.8, zorder=4)
ax.axvline(floor, color="black", linestyle="--", linewidth=1.2, zorder=5)
ax.annotate("  the reference's own re-run noise", (floor, -0.4), fontsize=8.5,
            rotation=90, ha="left", va="bottom")
ax.set_yticks(list(positions))
ax.set_yticklabels([f"{f['stage']}" + (f"  ({f['owner']})" if f["owner"] != "-" else "")
                    for f in shown], fontsize=9)
ax.set_xlabel("largest move in the reported skill score when this fork is taken differently")
# Counted from the bars, not stated. The figure has to say the same thing on both
# datasets, and a number in a title that nothing computes is exactly the transcription
# `AGENTS.md` §1 is about.
above = sum(1 for f in shown if f["moves_more_than_reference_noise"] == "True")
ax.set_title(f"{above} of {len(shown)} judgment calls move the conclusion\n"
             f"further than the reference model moves on its own, on the "
             f"{'held-out year' if HOLDOUT else 'development period'}",
             fontsize=11, loc="left")
handles = [plt.Line2D([], [], marker="s", linestyle="", color=c, label=k)
           for k, c in sorted(colour.items())]
handles.append(plt.Line2D([], [], marker="o", linestyle="", color="white",
                          markeredgecolor="0.25", label="one child of the fork"))
ax.legend(handles=handles, loc="lower right", fontsize=9, frameon=False,
          title="fork kind", title_fontsize=9)
ax.grid(axis="x", alpha=0.25, zorder=0)

fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
