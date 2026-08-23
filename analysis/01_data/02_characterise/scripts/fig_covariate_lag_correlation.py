#!/usr/bin/env python3
"""Dengue counts against each climate covariate at lags of nought to six months.

Computed within province and then pooled, so a province being both wetter and more
affected than another does not enter as a climate signal.

Plotted values: results/fig_covariate_lag_correlation.csv.
Pre-aggregation values: the per-province correlations are not stored separately --
the summary in lag_correlation.csv carries the min, median, max and the count of
provinces on each side of zero, which is the spread the figure draws.

Seeds: none; the correlations are deterministic. Project seed 20260822 unused here.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NODE = Path(__file__).resolve().parent.parent
RESULTS = NODE / "results"
STEM = "fig_covariate_lag_correlation"

lag = pd.read_csv(RESULTS / "lag_correlation.csv")
lag.to_csv(RESULTS / f"{STEM}.csv", index=False)

colors = {"rainfall": "#2166ac", "mean_temperature": "#b2182b",
          "mean_relative_humidity": "#1b7837"}
fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
for cov, g in lag.groupby("covariate"):
    g = g.sort_values("lag_months")
    ax.fill_between(g["lag_months"], g["min_spearman"], g["max_spearman"],
                    color=colors[cov], alpha=0.13, lw=0)
    ax.plot(g["lag_months"], g["mean_spearman"], color=colors[cov], lw=1.8,
            marker="o", ms=4, label=f"{cov} (mean over provinces)")
ax.axhline(0, color="0.4", lw=0.8)
ax.set_xlabel("lag applied to the covariate (months)")
ax.set_ylabel("Spearman correlation with dengue count")
ax.set_title("Climate-dengue association by lag, within province, 1998-2009")
ax.legend(frameon=False, loc="lower left")
ax.spines[["top", "right"]].set_visible(False)

fig.savefig(RESULTS / f"{STEM}.png", dpi=150)
print(f"wrote {STEM}.png with its plotted values; the band is the min-max over provinces")
