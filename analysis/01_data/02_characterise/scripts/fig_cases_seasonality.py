#!/usr/bin/env python3
"""The calendar-month profile of dengue counts against rainfall and humidity.

Plotted values: results/fig_cases_seasonality.csv.
Pre-aggregation values: results/fig_cases_seasonality_preaggregation.csv -- the
province-month observations the monthly means are taken over.

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
STEM = "fig_cases_seasonality"

season = pd.read_csv(RESULTS / "seasonality_by_month.csv")
nat = season[season["scope"] == "national"].sort_values("month").reset_index(drop=True)
nat.to_csv(RESULTS / f"{STEM}.csv", index=False)

dev = pd.read_csv(DEV, dtype={"time_period": str})
dev["month"] = dev["time_period"].str.slice(5, 7).astype(int)
dev[["time_period", "month", "location", "disease_cases", "rainfall",
     "mean_relative_humidity"]].to_csv(RESULTS / f"{STEM}_preaggregation.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
ax.bar(nat["month"], nat["mean_cases"], color="#b2182b", alpha=0.85,
       label="mean cases per province-month")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
ax.set_ylabel("mean reported cases per province-month")
ax.set_xlabel("calendar month")
ax.spines[["top"]].set_visible(False)

ax3 = ax.twinx()
ax3.plot(nat["month"], nat["mean_rainfall"], color="#2166ac", lw=1.8, marker="o",
         ms=4, label="mean rainfall (mm/day)")
ax3.plot(nat["month"], nat["mean_mean_relative_humidity"] / 10, color="#1b7837",
         lw=1.8, marker="s", ms=4, label="mean relative humidity (% / 10)")
ax3.set_ylabel("rainfall (mm/day)   ·   humidity (% / 10)")
ax3.spines[["top"]].set_visible(False)

handles = ([plt.Rectangle((0, 0), 1, 1, color="#b2182b", alpha=0.85)]
           + ax3.get_lines())
ax.legend(handles, ["mean cases per province-month", "mean rainfall (mm/day)",
                    "mean relative humidity (% / 10)"], loc="upper left", frameon=False)
ax.set_title("Dengue seasonality against climate, 1998-2009 development period")

fig.savefig(RESULTS / f"{STEM}.png", dpi=150)
print(f"wrote {STEM}.png with its plotted and pre-aggregation values")
