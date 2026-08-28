#!/usr/bin/env python3
"""Point accuracy against distributional accuracy, and where the two disagree.

CRPS is the project's headline metric and it scores a whole predictive distribution: a
model is rewarded for putting mass near the outcome and penalised for spreading it wide.
Mean absolute error scores only the point forecast. A model can therefore be the most
accurate in the project on one and the worst on the other, and when that happens the
disagreement is the informative part -- it says the model's centre is right and its width
is wrong, which is a different repair from the one a model with a bad centre needs.

The left panel puts every model at its (mean CRPS, MAE), so the disagreement is one
glance. The right panel puts the two interval coverages beside their nominal levels, and
its point is that they do not explain the ranking either: a model can sit closer to
nominal than every other model of ours and still score worst, because coverage averaged
over provinces cannot see an interval that is far too wide in one and far too narrow in
another. Where that happens is `fig_crps_by_location`, panel two.

Plotted values: results/$COMBO/fig_accuracy_and_spread.csv.
Pre-aggregation values: results/$COMBO/fig_accuracy_and_spread_preaggregation.csv -- the
per-cell scores every one of these summaries averages.

Seeds: none; a deterministic summary of stored scores.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "lib"))
from palette import colours, markers  # noqa: E402

NODE = Path(__file__).resolve().parent.parent
SCORE = NODE.parent
COMBO = os.environ.get("COMBO", "main")
RESULTS = NODE / "results" / COMBO
STEM = "fig_accuracy_and_spread"

# The nominal coverage of each stored interval. Properties of the interval's definition,
# not values measured anywhere: a 10-90 interval covers 80 % of a calibrated forecast's
# outcomes because that is what "10 to 90" means.
NOMINAL = {"coverage_10_90": 0.80, "coverage_25_75": 0.50}


def chosen_aggregate(name: str) -> Path:
    found = sorted((SCORE / "02_aggregate").glob(f"*/results/{COMBO}/{name}.csv"))
    if len(found) != 1:
        raise SystemExit(f"02_aggregate: expected one child with {name}.csv for "
                         f"combination {COMBO!r}, found {len(found)}")
    return found[0]


summary = pd.read_csv(chosen_aggregate("metrics_summary"))
cells = pd.read_csv(SCORE / "01_collect" / "results" / COMBO / "metrics_cell.csv",
                    dtype={"time_period": str, "split_first_period": str})

# The repeats of the unseeded reference are carried in the stored file; the figure shows
# the repeat mean, which is what the conclusion divides by.
shown = summary[~summary.model.str.contains(r"_r\d+$", regex=True)].copy()
shown = shown.sort_values("mean_crps").reset_index(drop=True)
shown.to_csv(RESULTS / f"{STEM}.csv", index=False)
cells[cells.model.isin(shown.model.unique())].to_csv(
    RESULTS / f"{STEM}_preaggregation.csv", index=False)

colour = colours(shown.model.unique())

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.0), constrained_layout=True,
                              width_ratios=[1, 1.1])

for row in shown.itertuples():
    ax.scatter(row.mean_crps, row.mae, s=110, color=colour[row.model],
               edgecolor="white", linewidth=1.2, zorder=3)
    ax.annotate(row.model, (row.mean_crps, row.mae), textcoords="offset points",
                xytext=(9, 4), fontsize=10, color=colour[row.model])
ax.set_xlabel("mean CRPS over 371 cells  (lower is better)")
ax.set_ylabel("mean absolute error  (lower is better)")
ax.set_title("The distribution and the point forecast\ndo not rank the models the same way",
             fontsize=11, loc="left")
ax.grid(alpha=0.25, zorder=0)

width = 0.36
positions = range(len(shown))
for offset, (column, nominal) in enumerate(NOMINAL.items()):
    ax2.barh([p + (offset - 0.5) * width for p in positions], shown[column],
             height=width, color=[colour[m] for m in shown.model],
             alpha=1.0 if offset == 0 else 0.55,
             label=f"{column.replace('coverage_', '').replace('_', '-')} interval")
for column, nominal in NOMINAL.items():
    ax2.axvline(nominal, color="black", linestyle="--", linewidth=1.1, zorder=4)
    ax2.annotate(f"nominal {nominal:.2f}", (nominal, -0.62),
                 rotation=90, fontsize=8, ha="right", va="bottom")
# Room below the bottom bar for the nominal-level labels, which sit under the axis line.
ax2.set_ylim(-1.15, len(shown) - 0.4)
ax2.set_yticks(list(positions))
ax2.set_yticklabels(shown.model)
ax2.set_xlabel("share of outcomes inside the interval")
ax2.set_title("Nor does calibration: the candidate is the closest of ours\nto both nominal levels",
              fontsize=11, loc="left")
ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=2, fontsize=9,
           frameon=False)
ax2.grid(axis="x", alpha=0.25)

fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
