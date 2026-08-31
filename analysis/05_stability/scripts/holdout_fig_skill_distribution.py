#!/usr/bin/env python3
"""The same figure for the frozen phase-E set, on the held-out year.

A one-screen runner over `scripts/lib/stability_figures.py`. It is a separate figure rather
than a second series on the development one: the skill scores are comparable, being ratios
to a reference that faced the same year as the model it is scoring, but one cloud would read
as a spread across analyses when half of it is a spread across years. The two meet in
`fig_holdout_vs_development.py`, one point per analysis.

The noise band drawn here is 2010's own, from the four repeats of the unseeded reference on
that year.

Plotted values: results/holdout_fig_skill_distribution.csv -- one row per point.
Pre-aggregation: none; each point is one stored conclusion.

Seeds: none.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from stability_figures import skill_distribution  # noqa: E402

skill_distribution("holdout")
