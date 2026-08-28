#!/usr/bin/env python3
"""Where each model's score actually comes from, province by province.

The headline mean is an unweighted mean over cells in provinces whose dengue burden
differs by four orders of magnitude, so it is an average of quite different failures. The
left panel puts every model's per-province mean CRPS on a log scale against the burden
that produced it; the right panel puts the 10-90 interval coverage beside it, because a
model can be well calibrated on average while being far too narrow in one province and far
too wide in another.

Plotted values: results/$COMBO/fig_crps_by_location.csv.
Pre-aggregation values: results/$COMBO/fig_crps_by_location_preaggregation.csv -- the
per-cell scores the province means average.

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
STEM = "fig_crps_by_location"


def chosen_aggregate(name: str) -> Path:
    found = sorted((SCORE / "02_aggregate").glob(f"*/results/{COMBO}/{name}.csv"))
    if len(found) != 1:
        raise SystemExit(f"02_aggregate: expected one child with {name}.csv for "
                         f"combination {COMBO!r}, found {len(found)}")
    return found[0]


per_location = pd.read_csv(chosen_aggregate("crps_by_location"))
cells = pd.read_csv(SCORE / "01_collect" / "results" / COMBO / "metrics_cell.csv",
                    dtype={"time_period": str, "split_first_period": str})

# The repeats of the unseeded reference are carried in the stored file; the figure shows
# the repeat mean, which is what the conclusion divides by.
shown = per_location[~per_location.model.str.contains(r"_r\d+$", regex=True)]
shown.to_csv(RESULTS / f"{STEM}.csv", index=False)
cells[cells.model.isin(shown.model.unique())].to_csv(
    RESULTS / f"{STEM}_preaggregation.csv", index=False)

models = sorted(shown.model.unique())
order = (shown[shown.model == models[0]].sort_values("observed_total").location.tolist())
colour = colours(models)
marker = markers(models)

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 5.4), constrained_layout=True,
                              sharey=True, width_ratios=[1.35, 1])
y = range(len(order))
for model in models:
    block = shown[shown.model == model].set_index("location").reindex(order)
    ax.plot(block.mean_crps.clip(lower=0.01), y, marker[model], color=colour[model],
            ms=6, alpha=0.85, label=model)
    ax2.plot(block.coverage_10_90, y, marker[model], color=colour[model], ms=6, alpha=0.85)

ax.set_yticks(list(y))
# The count is cases in the *evaluated* cells (2008-01 to 2009-12), not over the whole
# record: it is what the score is averaged against, and the two orderings are not the same.
ax.set_yticklabels([f"{loc}  ({int(t):,} cases evaluated)" for loc, t in zip(
    order, shown[shown.model == models[0]].set_index("location").reindex(order).observed_total)],
    fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("mean CRPS in the province (log scale)")
ax.set_title("score", fontsize=10)
ax.legend(fontsize=8, frameon=False, loc="lower right")

ax2.axvline(0.80, color="0.3", lw=1, ls="--")
ax2.set_xlim(-0.03, 1.03)
ax2.set_xlabel("10–90 interval coverage (nominal 0.80, dashed)")
ax2.set_title("calibration", fontsize=10)

fig.suptitle(f"Per-province score and calibration, provinces ordered by cases in the "
             f"evaluated cells — combination {COMBO}", fontsize=11)
fig.savefig(RESULTS / f"{STEM}.png", dpi=160)
print(f"{STEM}.png -> {RESULTS}")
