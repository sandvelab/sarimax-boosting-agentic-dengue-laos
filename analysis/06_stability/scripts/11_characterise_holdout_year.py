#!/usr/bin/env python3
"""What kind of year 2010 turned out to be -- written after the year was opened, so that the
held-out numbers can be read rather than merely reported.

Every model scores roughly five times worse on the held-out year than on the development
backtest. A report that gave the margin without saying that would be true and useless: the
reader cannot tell whether the second stage helped because it is good or because there was an
unusual amount left to correct. This script describes the year from the cells that were
actually scored, beside the development span the same models were measured on.

**This is a description of the opened year, not a row of the frozen set.** It adds nothing to
the manifest, re-tunes nothing and re-runs nothing; the plan's §3 binding rule is about the set
evaluated on the holdout, and characterising the data after it is opened is what the opening is
for. It is written as its own result with its own provenance, so that it cannot be mistaken for
part of the frozen comparison.

Reads only per-cell files two earlier scripts wrote: the held-out main path's and the
development main path's (`04_stage2/h_levelOnlyBoosting/results/per_cell_scores.csv`).

Seeds: none drawn.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ANALYSIS = NODE.parents[0]
RESULTS = NODE / "results"
HOLDOUT_CELLS = RESULTS / "main@h__holdout" / "per_cell_scores.csv"
DEV_CELLS = ANALYSIS / "04_stage2" / "h_levelOnlyBoosting" / "results" / "per_cell_scores.csv"


def scored(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return [r for r in csv.DictReader(f) if r["crps"] not in ("", None) and r["actual"] not in ("", None)]


def describe(rows: list[dict], label: str) -> dict:
    actuals = [float(r["actual"]) for r in rows]
    by_month: dict[str, float] = defaultdict(float)
    for r in rows:
        by_month[r["month"]] += float(r["actual"])
    over = sum(1 for r in rows if float(r["stage1_mean"]) > float(r["actual"]))
    return {
        "span": label, "n_cells": len(rows),
        "n_provinces": len({r["province"] for r in rows}), "n_months": len(by_month),
        "cases_total": sum(actuals), "cases_mean_per_cell": st.mean(actuals),
        "cases_median_per_cell": st.median(actuals), "cases_max_cell": max(actuals),
        "monthly_national_total_mean": st.mean(by_month.values()),
        "monthly_national_total_max": max(by_month.values()),
        "peak_month": max(by_month, key=by_month.get),
        "share_cells_stage1_over_predicts": over / len(rows),
        "national_total_by_month": {m: by_month[m] for m in sorted(by_month)},
    }


def main() -> None:
    holdout, development = scored(HOLDOUT_CELLS), scored(DEV_CELLS)
    h, d = describe(holdout, "2010 (held out)"), describe(development, "2008-01..2009-12 (development backtest)")

    # Where the held-out error sits, by province and by month, for the main path.
    by_province = defaultdict(lambda: {"cases": 0.0, "crps_stage1": 0.0, "crps_two_stage": 0.0, "n": 0})
    for r in holdout:
        e = by_province[r["province"]]
        e["cases"] += float(r["actual"])
        e["crps_stage1"] += float(r["crps_stage1"])
        e["crps_two_stage"] += float(r["crps"])
        e["n"] += 1
    provinces = sorted(({"province": p, **v, "delta_crps_sum": v["crps_two_stage"] - v["crps_stage1"]}
                        for p, v in by_province.items()), key=lambda r: -r["cases"])

    summary = {
        "what_this_is": ("a description of the held-out year, written after it was opened, so that "
                         "the frozen comparison can be read. Not a row of the frozen set."),
        "holdout": h, "development_backtest": d,
        "ratio_cases_mean_per_cell": h["cases_mean_per_cell"] / d["cases_mean_per_cell"],
        "ratio_monthly_national_total_mean": h["monthly_national_total_mean"] / d["monthly_national_total_mean"],
        "provinces_by_cases_held_out": provinces,
        "note_on_cells": ("204 cell slots, 192 scored: LA-XN reports no cases for any month of 2010, "
                          "so its 12 cells carry no actual to score against. LA-VI was already "
                          "outside the modelable set on development data. Batch 1's completeness "
                          "check recorded rows and months present, which they are; it did not "
                          "record whether disease_cases was populated."),
    }
    (RESULTS / "holdout_year_context.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "provinces_by_cases_held_out"}, indent=2))


if __name__ == "__main__":
    main()
