#!/usr/bin/env python3
"""How unevenly the dengue burden sits across provinces.

This is the figure behind the warning about the headline metric: an unweighted mean
CRPS over provinces gives a province with four cases in twelve years the same weight
as the capital with twenty-eight thousand.

Plotted values: results/fig_province_burden.csv.
Pre-aggregation values: results/fig_province_burden_preaggregation.csv -- the
province-month counts the totals sum over.

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
STEM = "fig_province_burden"

prov = pd.read_csv(RESULTS / "cases_by_province.csv")
prov.to_csv(RESULTS / f"{STEM}.csv", index=False)
pd.read_csv(DEV, dtype={"time_period": str})[
    ["time_period", "location", "location_name", "disease_cases"]
].to_csv(RESULTS / f"{STEM}_preaggregation.csv", index=False)

p = prov.sort_values("total_cases")
labels = [f"{r.location}  {r.location_name}" for r in p.itertuples()]
colors = ["#bdbdbd" if r.cells_observed == 0 else
          ("#f4a582" if r.total_cases < 100 else "#b2182b") for r in p.itertuples()]

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 5.5), constrained_layout=True,
                              sharey=True, width_ratios=[2, 1])
ax.barh(labels, p["total_cases"].clip(lower=0.5), color=colors)
ax.set_xscale("log")
ax.set_xlabel("total reported cases, 1998-2009 (log scale)")
ax.set_title("Reported dengue burden by province")
ax.spines[["top", "right"]].set_visible(False)

ax2.barh(labels, p["zero_share"].fillna(0), color=colors)
ax2.set_xlim(0, 1)
ax2.set_xlabel("share of observed months reporting zero")
ax2.set_title("Zero-inflation")
ax2.spines[["top", "right"]].set_visible(False)

fig.savefig(RESULTS / f"{STEM}.png", dpi=150)
print(f"wrote {STEM}.png with its plotted and pre-aggregation values")
