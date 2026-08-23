#!/usr/bin/env python3
"""National monthly dengue counts over the development period, with the per-province
series behind them.

Plotted values: results/fig_cases_timeline.csv (the national line).
Pre-aggregation values: results/fig_cases_timeline_preaggregation.csv (the province
series the national line sums over). Rule 7 -- the figure aggregates, so both are kept.

Seeds: none; the figure is a deterministic summary. Project seed 20260822 unused here.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NODE = Path(__file__).resolve().parent.parent
RESULTS = NODE / "results"
DEV = NODE.parent / "01_partition" / "results" / "development_1998-01_2009-12.csv"
STEM = "fig_cases_timeline"

national = pd.read_csv(RESULTS / "cases_national_monthly.csv", dtype={"time_period": str})
dev = pd.read_csv(DEV, dtype={"time_period": str})
preagg = dev[["time_period", "location", "location_name", "disease_cases"]]
preagg.to_csv(RESULTS / f"{STEM}_preaggregation.csv", index=False)
national[["time_period", "year", "month", "total_cases", "provinces_observed",
          "mean_cases_per_reporting_province"]].to_csv(RESULTS / f"{STEM}.csv", index=False)

x = range(len(national))
fig, (ax, ax2) = plt.subplots(
    2, 1, figsize=(11, 6), sharex=True, height_ratios=[3, 1], constrained_layout=True)

for _, g in preagg.groupby("location"):
    g = g.sort_values("time_period")
    ax.plot(x, g["disease_cases"].to_numpy(), color="0.75", lw=0.6, zorder=1)
ax.plot(x, national["total_cases"], color="#b2182b", lw=1.6, zorder=3,
        label="national total")
ax.set_ylabel("reported dengue cases")
ax.set_title("Monthly dengue counts, Laos admin-1, development period 1998-01 to 2009-12")
ax.legend(handles=[
    plt.Line2D([], [], color="#b2182b", lw=1.6, label="national total"),
    plt.Line2D([], [], color="0.75", lw=0.6, label="individual provinces"),
], loc="upper left", frameon=False)

ax2.step(x, national["provinces_observed"], where="mid", color="#2166ac", lw=1.0)
ax2.set_ylim(0, 18.5)
ax2.set_ylabel("provinces\nreporting")
ax2.axhline(18, color="0.6", ls=":", lw=0.8)

ticks = [i for i, tp in enumerate(national["time_period"]) if tp.endswith("-01")]
ax2.set_xticks(ticks)
ax2.set_xticklabels([national["time_period"][i][:4] for i in ticks], rotation=0)
ax2.set_xlabel("year")
for a in (ax, ax2):
    a.spines[["top", "right"]].set_visible(False)

fig.savefig(RESULTS / f"{STEM}.png", dpi=150)
print(f"wrote {STEM}.png with its plotted and pre-aggregation values")
