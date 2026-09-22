#!/usr/bin/env python3
"""Gather one conclusion per frozen phase-E row into `results/conclusions_holdout.csv` -- the
table the held-out report is written from.

Every row of the frozen manifest appears, including the ten that were never planned to run, so
the table shows the whole set and not only the part that produced numbers. A row that ran is
copied from its own `results/<combination>/conclusion.json`; nothing is computed here beyond
reading, copying, and one subtraction.

**The pairing is part of the table**, because the freeze's reporting rule asks that every
held-out margin be read beside its development counterpart rather than on its own. Each row
carries its development v2 margin (from `results/conclusions_v2.csv`, matched by the
`development_row` column the manifest already holds) and the shift in percentage points.
The four tier-1 rows pair with the siblings' own development comparisons, which is what
`conclusions_v2.csv` holds for them.

Baselines have no stage-1 ablation -- they are not two-stage models -- so they carry
`mean_crps` and `coverage_90` in their own columns and leave the ablation columns empty. The
`model_type` column says which kind of row it is.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
RESULTS = NODE / "results"
MANIFEST = RESULTS / "manifest_holdout.csv"

FIELDS = ["combination", "tier", "model_type", "status", "stage1_mean_crps", "two_stage_mean_crps",
          "pct_change_vs_stage1", "stage1_coverage_90", "two_stage_coverage_90",
          "baseline_mean_crps", "baseline_coverage_90", "beats_stage1_on_crps",
          "coverage_not_worse", "n_splits_improved", "n_splits", "share_cells_improved",
          "n_cells", "development_row", "development_pct_change", "shift_points",
          "informativeness_rank", "reason_if_not_run"]


def fnum(x):
    return float(x) if x not in ("", None, "-") else None


def main() -> None:
    with MANIFEST.open(newline="") as f:
        manifest = list(csv.DictReader(f))
    with (RESULTS / "conclusions_v2.csv").open(newline="") as f:
        development = {r["combination"]: r for r in csv.DictReader(f)}
    # The development main-path row is labelled with its node, not with the bare row name the
    # manifest carries, so it is matched by prefix the same way the report reads it.
    dev_main = next((r for r in development.values() if r["tier"] == "0"), None)

    rows = []
    for m in manifest:
        dev_key = m["development_row"]
        dev = development.get(dev_key) or (dev_main if dev_key == "main@h" else None)
        dev_pct = fnum(dev["pct_change_vs_stage1"]) if dev else None
        row = {"combination": m["combination"], "tier": int(m["tier"]), "status": m["status"],
               "development_row": dev_key, "development_pct_change": dev_pct,
               "informativeness_rank": m["informativeness_rank"],
               "reason_if_not_run": m["reason_if_not_run"], "model_type": "", "shift_points": None}
        path = RESULTS / m["combination"] / "conclusion.json"
        if m["status"] != "planned" or not path.exists():
            row["status"] = m["status"] if m["status"] != "planned" else "planned_not_run"
            rows.append(row)
            continue
        c = json.loads(path.read_text())
        row["status"] = "run"
        if "two_stage" in c:
            row.update({"model_type": "two_stage",
                        "stage1_mean_crps": c["stage1_alone"]["mean_crps"],
                        "two_stage_mean_crps": c["two_stage"]["mean_crps"],
                        "pct_change_vs_stage1": c["pct_change_vs_stage1"],
                        "stage1_coverage_90": c["stage1_alone"]["coverage_90"],
                        "two_stage_coverage_90": c["two_stage"]["coverage_90"],
                        "beats_stage1_on_crps": c["two_stage_beats_stage1_on_crps"],
                        "coverage_not_worse": c["coverage_not_worse_than_stage1"],
                        "n_splits_improved": c["n_splits_improved"], "n_splits": c["n_splits"],
                        "share_cells_improved": c["share_cells_improved"],
                        "n_cells": c["n_cells_scored"]})
            if dev_pct is not None:
                row["shift_points"] = c["pct_change_vs_stage1"] - dev_pct
        else:
            row.update({"model_type": "baseline", "baseline_mean_crps": c["mean_crps"],
                        "baseline_coverage_90": c["coverage_90"], "n_splits": c["n_splits"],
                        "n_cells": c["n_cells_scored"]})
        rows.append(row)

    with (RESULTS / "conclusions_holdout.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    ran = [r for r in rows if r["status"] == "run" and r["model_type"] == "two_stage"]
    print(f"{len(rows)} frozen rows, {len([r for r in rows if r['status'] == 'run'])} run "
          f"({len(ran)} two-stage). On the held-out year the two-stage ensemble beats stage 1 "
          f"alone on CRPS in {sum(1 for r in ran if r['beats_stage1_on_crps'])} of them, with "
          f"coverage not worse in {sum(1 for r in ran if r['beats_stage1_on_crps'] and r['coverage_not_worse'])}")


if __name__ == "__main__":
    main()
