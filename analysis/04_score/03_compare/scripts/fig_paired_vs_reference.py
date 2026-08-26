#!/usr/bin/env python3
"""What the paired comparison against the reference can and cannot separate.

Three panels, left to right, each a stricter reading of the same numbers.

  * the per-cell paired differences, as a distribution -- wide, long-tailed, and the
    reason a comparison of aggregate means is not the whole story;
  * the split-level paired means, eight numbers per model, which is the comparison that
    assumes nothing about independence within a split;
  * the mean paired difference per model with the honest error bar beside the naive one,
    against the shaded band the reference's own unseeded re-runs occupy. A model whose
    interval overlaps that band has not been distinguished from the reference by this
    evaluation, however large its aggregate margin looks.

Plotted values: results/$COMBO/fig_paired_vs_reference.csv.
Pre-aggregation values: results/$COMBO/fig_paired_vs_reference_preaggregation.csv --
the per-cell paired differences the panels summarise.

Seeds: none; every panel is a deterministic summary of stored scores.
"""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NODE = Path(__file__).resolve().parent.parent
COMBO = os.environ.get("COMBO", "main")
RESULTS = NODE / "results" / COMBO
STEM = "fig_paired_vs_reference"
REFERENCE = "reference"

pairs = pd.read_csv(RESULTS / "paired_vs_reference.csv",
                    dtype={"time_period": str, "split_first_period": str})
summary = pd.read_csv(RESULTS / "paired_summary.csv")
by_split = pd.read_csv(RESULTS / "paired_by_split.csv", dtype={"split_first_period": str})
noise = pd.read_csv(RESULTS / "reference_repeat_noise.csv")

cells = pairs[pairs.against == REFERENCE]
splits = by_split[by_split.against == REFERENCE]
stats = summary[summary.against == REFERENCE].sort_values("mean_diff")
models = list(stats.model)

stats.to_csv(RESULTS / f"{STEM}.csv", index=False)
cells.to_csv(RESULTS / f"{STEM}_preaggregation.csv", index=False)

floor = noise["mean_diff"].abs().max() if len(noise) else 0.0

fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), constrained_layout=True,
                         width_ratios=[1.2, 1, 1.1])
colour = {m: c for m, c in zip(models, ["#2166ac", "#b2182b", "#4d9221", "#8c510a"])}

ax = axes[0]
for model in models:
    d = cells.loc[cells.model == model, "diff"]
    ax.hist(d, bins=60, histtype="step", lw=1.6, color=colour[model], label=model)
ax.axvline(0, color="0.3", lw=1)
ax.set_xscale("symlog", linthresh=1)
ax.set_xlabel("per-cell CRPS difference (ours − reference)")
ax.set_ylabel("cells")
ax.set_title("every cell, symlog scale", fontsize=10)
ax.legend(fontsize=8, frameon=False)

ax = axes[1]
for i, model in enumerate(models):
    s = splits[splits.model == model].sort_values("split_first_period")
    ax.plot(range(len(s)), s.mean_diff, "o-", color=colour[model], ms=5, label=model)
    ax.set_xticks(range(len(s)))
    ax.set_xticklabels(s.split_first_period, rotation=60, fontsize=7)
ax.axhline(0, color="0.3", lw=1)
ax.set_ylabel("mean CRPS difference in the split")
ax.set_title("by backtest split", fontsize=10)

ax = axes[2]
ax.axhspan(-floor, floor, color="0.85", zorder=0,
           label=f"reference vs its own repeats (±{floor:.2f})")
for i, row in enumerate(stats.itertuples()):
    ax.errorbar(i - 0.11, row.mean_diff, yerr=1.96 * row.se_cell_naive, fmt="o",
                color=colour[row.model], ms=6, alpha=0.4, capsize=4)
    ax.errorbar(i + 0.11, row.mean_diff, yerr=1.96 * row.se_cluster_split, fmt="s",
                color=colour[row.model], ms=6, capsize=4)
ax.axhline(0, color="0.3", lw=1)
ax.set_xticks(range(len(stats)))
ax.set_xticklabels(stats.model, rotation=20, fontsize=8)
ax.set_ylabel("mean paired CRPS difference")
ax.set_title("faded: per-cell error bar; solid: clustered by split", fontsize=10)
ax.legend(fontsize=8, frameon=False, loc="upper left")

fig.suptitle(f"Paired per-cell comparison against the reference — combination {COMBO}",
             fontsize=11)
fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
