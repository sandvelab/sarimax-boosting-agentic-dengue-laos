#!/usr/bin/env python3
"""The same ranking for the held-out year, against that year's own noise band.

A one-screen runner over `scripts/lib/stability_figures.py`. Whether the same forks come out
above the line is the phase-E question about this figure; `fig_fork_sensitivity_both.py`
puts the two rankings on one set of axes and `results/fork_sensitivity_both.csv` is the
table behind it.

Plotted values: results/holdout_fig_fork_sensitivity.csv -- one row per bar.
Pre-aggregation: results/holdout_fig_fork_sensitivity_preaggregation.csv.

Seeds: none.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from stability_figures import fork_sensitivity  # noqa: E402

fork_sensitivity("holdout")
