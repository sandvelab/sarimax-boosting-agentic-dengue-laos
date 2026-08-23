#!/usr/bin/env python3
"""Where the dengue target is present, by province and year.

The figure is what decides which provinces the headline metric is a mean over, so it
is worth having as a picture rather than only as a count.

Plotted values: results/fig_completeness.csv (the province x year grid).
Pre-aggregation values: results/fig_completeness_preaggregation.csv (the individual
province-months that are absent).

Seeds: none; the figure is a deterministic summary. Project seed 20260822 unused here.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

NODE = Path(__file__).resolve().parent.parent
RESULTS = NODE / "results"
STEM = "fig_completeness"

comp = pd.read_csv(RESULTS / "completeness_by_province_year.csv")
order = (comp.groupby(["location", "location_name"])["cells_observed"].sum()
             .sort_values(ascending=False).reset_index())
grid = comp.pivot_table(index="location", columns="year", values="cells_observed")
grid = grid.reindex(order["location"])
grid.to_csv(RESULTS / f"{STEM}.csv")

missing = pd.read_csv(RESULTS / "target_missing_cells.csv")
missing.to_csv(RESULTS / f"{STEM}_preaggregation.csv", index=False)

labels = [f"{r.location}  {r.location_name}" for r in order.itertuples()]
fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
im = ax.imshow(grid.to_numpy(), cmap="YlGnBu", vmin=0, vmax=12, aspect="auto")
ax.set_xticks(range(len(grid.columns)))
ax.set_xticklabels(grid.columns, rotation=90)
ax.set_yticks(range(len(grid.index)))
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("year")
ax.set_title("Months with a reported dengue count, by province and year (of 12)")
for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        v = grid.to_numpy()[i, j]
        if not np.isnan(v) and v < 12:
            ax.text(j, i, int(v), ha="center", va="center", fontsize=7,
                    color="#b2182b" if v == 0 else "0.2")
fig.colorbar(im, ax=ax, label="months observed", shrink=0.7)

fig.savefig(RESULTS / f"{STEM}.png", dpi=150)
print(f"wrote {STEM}.png with its plotted and pre-aggregation values")
