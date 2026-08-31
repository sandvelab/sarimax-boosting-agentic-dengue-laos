#!/usr/bin/env python3
"""Whether two judgment calls taken together do what they do apart.

Tier 2 exists to answer one question: can the one-at-a-time table be added up? Each point
is a pair of forks, at its additive prediction on the horizontal axis — the sum of the two
rows' own moves — and at what the pair actually did on the vertical. The diagonal is where
a pair would sit if the two choices did not interact.

Nothing is on the diagonal, and the distance from it is the finding. The extreme pair is
larger than either main effect behind it: removing the two provinces with no evaluable cell
and weighting the headline mean by cases each improve the reported skill on their own, and
almost exactly cancel when both are taken, because both work by re-weighting what the mean
is over and taking both does not do it twice.

Plotted values: results/fig_pair_interaction.csv -- one row per point.
Pre-aggregation: results/fig_pair_interaction_preaggregation.csv -- the two tier-1 moves
whose sum is each point's horizontal coordinate.

Seeds: none.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "lib"))
from palette import assign, PALETTE  # noqa: E402

NODE = Path(__file__).resolve().parent.parent
RESULTS = NODE / "results"
STEM = "fig_pair_interaction"

with (RESULTS / "conclusions.csv").open() as handle:
    rows = list(csv.DictReader(handle))
tier1 = {(r["fork"], r["child"]): r for r in rows
         if r["tier"] == "1" and r["delta_skill_vs_main"] != ""}

shown, pre = [], []
for row in rows:
    if row["tier"] != "2" or row["interaction"] == "":
        continue
    parts = [tier1[move] for move in
             zip(row["fork"].split("+"), row["child"].split("+"))]
    shown.append({"combination": row["combination"],
                  "observed_delta_skill": float(row["delta_skill_vs_main"]),
                  "additive_delta_skill": float(row["delta_skill_additive"]),
                  "interaction": float(row["interaction"]),
                  "part_a": parts[0]["combination"], "part_b": parts[1]["combination"],
                  "kinds": "+".join(p["kind"] for p in parts)})
    for part in parts:
        pre.append({"pair": row["combination"], "part": part["combination"],
                    "kind": part["kind"], "fork": part["fork"], "child": part["child"],
                    "delta_skill_vs_main": part["delta_skill_vs_main"]})
shown.sort(key=lambda r: r["interaction"])

with (RESULTS / f"{STEM}.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(shown)
with (RESULTS / f"{STEM}_preaggregation.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(pre[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(pre)

colour = assign(sorted({r["kinds"] for r in shown}), PALETTE)

fig, ax = plt.subplots(figsize=(8.2, 7.2), constrained_layout=True)
values = [v for r in shown for v in (r["observed_delta_skill"],
                                     r["additive_delta_skill"])]
lo, hi = min(values) - 0.03, max(values) + 0.03
ax.plot([lo, hi], [lo, hi], color="black", linewidth=1.0, zorder=1)
ax.annotate("the two forks compose", (hi, hi), fontsize=8.5, ha="right", va="bottom",
            rotation=45, rotation_mode="anchor")
ax.axhline(0.0, color="0.7", linewidth=0.8, zorder=0)
ax.axvline(0.0, color="0.7", linewidth=0.8, zorder=0)

for row in shown:
    ax.plot([row["additive_delta_skill"]] * 2,
            [row["additive_delta_skill"], row["observed_delta_skill"]],
            color="0.6", linewidth=1.0, zorder=2)
    ax.scatter(row["additive_delta_skill"], row["observed_delta_skill"], s=110,
               color=colour[row["kinds"]], edgecolor="white", linewidth=1.1, zorder=3)
    # Labels lean away from the edge the point sits nearest, so a pair in the top
    # right corner is not written off the canvas.
    right = row["additive_delta_skill"] > 0
    ax.annotate(f"{row['part_a']}\n+ {row['part_b']}",
                (row["additive_delta_skill"], row["observed_delta_skill"]),
                textcoords="offset points", xytext=(-10 if right else 10, -4),
                ha="right" if right else "left", fontsize=7.5,
                color=colour[row["kinds"]])

ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.set_xlabel("what the two forks predict together, added: Δskill(a) + Δskill(b)")
ax.set_ylabel("what taking both actually did: Δskill(a and b)")
ax.set_title("Fork effects do not compose\n"
             "The vertical gap is the interaction; the largest one exceeds both\n"
             "main effects behind it", fontsize=11, loc="left")
handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, label=k)
           for k, c in sorted(colour.items())]
ax.legend(handles=handles, loc="upper left", fontsize=8.5, frameon=False,
          title="kinds paired", title_fontsize=9)
ax.grid(alpha=0.25, zorder=0)

fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
