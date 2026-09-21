#!/usr/bin/env python3
"""Gather one conclusion per manifest row into `results/conclusions.csv` -- the table the
stability report (batch 13) is written from. Tier 1 from each sibling's own
`results/comparison.json`; tier 2 from `results/<combination>/conclusion.json`; tier 3 as
rows marked not run, with their reason, so the table shows the whole planned set and not only
what ran. Nothing is computed here beyond reading and copying.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
ANALYSIS = NODE.parents[0]
RESULTS = NODE / "results"
FIELDS = ["combination", "tier", "status", "stage1_mean_crps", "two_stage_mean_crps", "pct_change_vs_stage1",
          "stage1_coverage_90", "two_stage_coverage_90", "beats_stage1_on_crps", "coverage_not_worse",
          "n_splits_improved", "n_splits", "share_cells_improved", "n_cells", "informativeness_rank", "reason_if_not_run"]


def main() -> None:
    with (RESULTS / "manifest.csv").open(newline="") as f:
        manifest = list(csv.DictReader(f))
    rows = []
    # The main path itself, as the reference row.
    g = json.loads((ANALYSIS / "04_stage2" / "g_oosErrorBoosting" / "results" / "comparison.json").read_text())
    rows.append({"combination": "main (04_stage2=g_oosErrorBoosting)", "tier": 0, "status": "run",
                 "stage1_mean_crps": g["stage1_alone"]["mean_crps"], "two_stage_mean_crps": g["two_stage_ensemble"]["mean_crps"],
                 "pct_change_vs_stage1": g["pct_change_vs_stage1"], "stage1_coverage_90": g["stage1_alone"]["coverage_empirical"],
                 "two_stage_coverage_90": g["two_stage_ensemble"]["coverage_empirical"], "beats_stage1_on_crps": g["earns_its_place"],
                 "coverage_not_worse": g["two_stage_ensemble"]["coverage_empirical"] >= g["stage1_alone"]["coverage_empirical"],
                 "n_splits_improved": g["n_splits_improved_of_8"], "n_splits": 8, "share_cells_improved": g["share_cells_improved"],
                 "n_cells": g["n_cells"], "informativeness_rank": "-", "reason_if_not_run": ""})
    for r in manifest:
        if r["tier"] == "1":
            c = json.loads((ANALYSIS.parent / r["node"] / "results" / "comparison.json").read_text())
            rows.append({"combination": r["combination"], "tier": 1, "status": "run",
                         "stage1_mean_crps": c["stage1_alone"]["mean_crps"], "two_stage_mean_crps": c["two_stage_ensemble"]["mean_crps"],
                         "pct_change_vs_stage1": c["pct_change_vs_stage1"], "stage1_coverage_90": c["stage1_alone"]["coverage_empirical"],
                         "two_stage_coverage_90": c["two_stage_ensemble"]["coverage_empirical"], "beats_stage1_on_crps": c["earns_its_place"],
                         "coverage_not_worse": c["two_stage_ensemble"]["coverage_empirical"] >= c["stage1_alone"]["coverage_empirical"],
                         "n_splits_improved": c.get("n_splits_improved_of_8", ""), "n_splits": 8,
                         "share_cells_improved": c.get("share_cells_improved", ""), "n_cells": c["n_cells"],
                         "informativeness_rank": r["informativeness_rank"], "reason_if_not_run": ""})
        elif r["tier"] == "2":
            path = RESULTS / r["combination"] / "conclusion.json"
            if r["status"] != "planned" or not path.exists():
                rows.append({"combination": r["combination"], "tier": 2, "status": r["status"] if r["status"] != "planned" else "planned_not_run",
                             "informativeness_rank": r["informativeness_rank"], "reason_if_not_run": r["reason_if_not_run"]})
                continue
            c = json.loads(path.read_text())
            rows.append({"combination": r["combination"], "tier": 2, "status": "run",
                         "stage1_mean_crps": c["stage1_alone"]["mean_crps"], "two_stage_mean_crps": c["two_stage"]["mean_crps"],
                         "pct_change_vs_stage1": c["pct_change_vs_stage1"], "stage1_coverage_90": c["stage1_alone"]["coverage_90"],
                         "two_stage_coverage_90": c["two_stage"]["coverage_90"], "beats_stage1_on_crps": c["two_stage_beats_stage1_on_crps"],
                         "coverage_not_worse": c["coverage_not_worse_than_stage1"], "n_splits_improved": c["n_splits_improved"],
                         "n_splits": c["n_splits"], "share_cells_improved": c["share_cells_improved"], "n_cells": c["n_cells_scored"],
                         "informativeness_rank": r["informativeness_rank"], "reason_if_not_run": ""})
        else:
            rows.append({"combination": r["combination"], "tier": 3, "status": "not_run",
                         "informativeness_rank": "-", "reason_if_not_run": r["reason_if_not_run"]})
    with (RESULTS / "conclusions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    ran = [r for r in rows if r["status"] == "run"]
    print(f"{len(rows)} rows, {len(ran)} run; two-stage beats stage 1 on CRPS in "
          f"{sum(1 for r in ran if r['beats_stage1_on_crps'])} of them, with coverage not worse in "
          f"{sum(1 for r in ran if r['beats_stage1_on_crps'] and r['coverage_not_worse'])}")


if __name__ == "__main__":
    main()
