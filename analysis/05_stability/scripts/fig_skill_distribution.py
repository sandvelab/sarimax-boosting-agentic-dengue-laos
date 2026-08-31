#!/usr/bin/env python3
"""Every analysis the development manifest named, on one axis, with the reported one marked.

A one-screen runner. The drawing is in `scripts/lib/stability_figures.py`, because the same
figure is drawn for the held-out year by `holdout_fig_skill_distribution.py` and a copy per
dataset is a copy that will drift. What the figure shows, and why each of its three
reference lines is there, is in that module's docstring.

Plotted values: results/fig_skill_distribution.csv -- one row per point.
Pre-aggregation: none; each point is one stored conclusion.

Seeds: none.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from stability_figures import skill_distribution  # noqa: E402

skill_distribution("development")
