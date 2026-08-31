#!/usr/bin/env python3
"""Which judgment calls the conclusion is sensitive to on the development period.

A one-screen runner. The drawing is in `scripts/lib/stability_figures.py`, because the same
figure is drawn for the held-out year by `holdout_fig_fork_sensitivity.py`. What the bars
are, and what the dashed line is measured from, is in that module's docstring.

Plotted values: results/fig_fork_sensitivity.csv -- one row per bar.
Pre-aggregation: results/fig_fork_sensitivity_preaggregation.csv -- the per-combination
moves each bar takes a maximum over.

Seeds: none.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from stability_figures import fork_sensitivity  # noqa: E402

fork_sensitivity("development")
