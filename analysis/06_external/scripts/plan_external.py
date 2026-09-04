#!/usr/bin/env python3
"""Plan the external check: which rows it runs, what each is estimated to cost, and the cut.

The check is four analyses -- two countries, each in the two arrangements that mirror
Laos's development backtest and its final year. They are not perturbations: no fork moves,
the model does not change, and the reported configuration is the one that runs. What
changes is the file underneath, which `analysis/scripts/lib/combos.py` derives from the
combination's dataset suffix exactly as it derives the held-out year's.

**Why a manifest at all for four rows.** Two reasons, both of them properties this
repository already has and would otherwise lose here.

`/validate invariants`'s `combos` check closes the combination space: a `results/`
directory no manifest names is an analysis that is in the repository and not in anything
reported. Without a third planned source, four external directories at every node would
have to be excused, and an excused directory is how the check stops meaning anything.

And `AGENTS.md` §6 asks for the cost of each unit, the ranking, and where the line fell.
The Thai file carries 77 provinces against Laos's 18 and the reference model runs four
unseeded repeats through an emulated amd64 image, so this is the one part of batch 20 that
could plausibly exceed its budget. The estimate below is written before anything runs, from
this project's own measured per-cell costs, and `run_external.py` records what it actually
took beside it -- which is the comparison batch 13 and batch 15 both made and both found
the total right and no individual row right.

**The cut order, and the unit.** Rows are cut in **country pairs**, never singly: what the
check measures is the *drop* from the development arrangement to the final year, so half a
country answers nothing. Vietnam is ranked first because its file already runs 1998-01 to
2010-12 and needs no truncation to sit on the Lao calendar, and because it is the smaller
of the two. Nothing is cut unless the estimate exceeds the budget, and where the line fell
is written into the plan whether or not it bit.

**The plan is written once and verified thereafter, never recomputed.** Its estimate is
built from a *measured wall-clock duration* -- the seconds the held-out `main` row took --
and `05_stability/run.sh` rewrites that measurement every time it runs, which on
`analysis/run.sh` is immediately before this script. So a plan that recomputed itself would
come back with different numbers from a clean checkout, and the claim that it was committed
before the rows ran would be a claim about a file that had since been rewritten. This is the
fourth time this project has had to separate a recorded decision from a derivation over
values that do not reproduce: batch 24's frozen manifest, batch 26's tier-1 order and tier-2
selection, batch 30's frozen development figure, and this.

The split is the one those three arrived at. **The rows are structural** -- they come from
the tree and from the sibling scheme, and a change to them means the plan describes an
analysis nobody planned, so it is fatal. **The seconds are a measurement**, so a change to
them is reported and carried on from.

Writes:
  results/manifest_external.csv    the rows, their rank, their estimate, their status.
                                   Written once; afterwards read and verified
  results/external_plan.json       the budget, the cut order, the rule, and what it cut.
                                   Written once, beside the manifest
  results/external_plan_check.json what a re-plan today would say, against what is recorded

Seeds: none. Planning reads sizes and writes a table.

Usage:  "$PYTHON" scripts/plan_external.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parent.parent
ROOT = NODE.parents[1]
RESULTS = NODE / "results"
SCHEME = ROOT / "analysis/01_data/03_siblings/results/backtest_scheme_external.json"
LAO_SCHEME = ROOT / "analysis/01_data/02_characterise/results/backtest_scheme_chosen.json"
STABILITY = ROOT / "analysis/05_stability/results"

sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
import combos  # noqa: E402

#: The budget for this batch's runs, in hours, set before anything was costed so the cut
#: order has something to be a cut against. Six hours is what `analysis/run.sh` already
#: costs: an external check on the analysis should not cost more than the analysis.
BUDGET_HOURS = 6.0

#: The rows, in the order they are cut from the bottom. A country is one unit.
COUNTRIES = [
    ("vnm", "VNM", "Vietnam"),
    ("tha", "THA", "Thailand"),
]
ARRANGEMENTS = [("", "development backtest, 3/8/3, evaluating 2008-01..2009-12"),
                ("Final", "final year, 3/4/3, evaluating 2010")]


def measured_cost_per_cell() -> dict:
    """What one evaluated cell has cost this project, on its own runs.

    Read from the two Lao arrangements rather than assumed: `05_stability`'s status files
    record what each combination took, and the main row of each is the same pipeline these
    four rows run -- every setup fork at its main child, both baselines, the reference's
    four repeats, the reported pool and the scoring chain.
    """
    lao = json.loads(LAO_SCHEME.read_text())
    out = {}
    for dataset, status_name, cells_key in (
            ("development", "run_status.csv", "cells_metric_averages_development_effective"),
            ("holdout", "run_status_holdout.csv", None)):
        path = STABILITY / status_name
        rows = {r["combination"]: r for r in csv.DictReader(path.open())}
        name = "main" if dataset == "development" else "main__holdout"
        seconds = float(rows[name]["seconds"]) if rows[name]["seconds"] else None
        cells = lao[cells_key] if cells_key else 192
        out[dataset] = {
            "from_row": name,
            "from_file": str(path.relative_to(ROOT)),
            "seconds": seconds,
            "cells": cells,
            "seconds_per_cell": (seconds / cells) if seconds else None,
        }
    return out


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    scheme = json.loads(SCHEME.read_text())
    per_cell = measured_cost_per_cell()

    # The development `main` row runs `conclude.py` alone -- the main path is the analysis
    # that already ran -- so it costs nothing and cannot be the unit. The holdout `main`
    # row ran the whole pipeline on a fresh dataset, which is exactly what every external
    # row does, so that is the measurement the estimate is built on.
    unit = per_cell["holdout"]["seconds_per_cell"]

    planned = []
    for rank_country, (code, upper, country) in enumerate(COUNTRIES):
        for suffix, description in ARRANGEMENTS:
            name = f"{code}{suffix}"
            detail = scheme[f"{name}_detail"]
            cells = detail["cells_metric_averages_effective"]
            planned.append({
                "rank": len(planned) + 1,
                "country": country,
                "country_rank": rank_country + 1,
                "combination": f"main__{name}",
                "dataset": name,
                "kind": "main",
                "fork": "-",
                "child": "-",
                "combo_base": "-",
                "built": "True",
                "tier": "1",
                "arrangement": description,
                "source": detail["source"],
                "locations_evaluated": detail["locations_evaluated"],
                "cells": cells,
                "planned_seconds": round(cells * unit, 1),
            })

    total = sum(r["planned_seconds"] for r in planned)
    budget_seconds = BUDGET_HOURS * 3600
    # The cut, applied to whole countries from the bottom of the ranking.
    cut: list[str] = []
    kept = list(planned)
    while sum(r["planned_seconds"] for r in kept) > budget_seconds and kept:
        drop = max(r["country_rank"] for r in kept)
        cut += [r["combination"] for r in kept if r["country_rank"] == drop]
        kept = [r for r in kept if r["country_rank"] != drop]
    for row in planned:
        row["status"] = "planned" if row["combination"] not in cut else "cut for budget"

    fields = ["rank", "combination", "dataset", "kind", "fork", "child", "combo_base",
              "built", "tier", "country", "country_rank", "arrangement", "source",
              "locations_evaluated", "cells", "planned_seconds", "status"]
    manifest = RESULTS / "manifest_external.csv"

    # Everything in a row except the estimate. These come from the tree and the sibling
    # scheme, so a disagreement means the recorded plan describes an analysis this tree can
    # no longer produce -- which is fatal, before anything is written.
    STRUCTURAL = [f for f in fields if f != "planned_seconds"]

    if manifest.exists():
        recorded = list(csv.DictReader(manifest.open()))
        today = {r["combination"]: r for r in planned}
        moved = []
        for row in recorded:
            mine = today.get(row["combination"])
            if mine is None:
                moved.append(f"{row['combination']}: recorded, and this tree has no such row")
                continue
            for field in STRUCTURAL:
                if str(mine[field]) != row[field]:
                    moved.append(f"{row['combination']}.{field}: recorded {row[field]!r}, "
                                 f"this tree says {str(mine[field])!r}")
        for name in sorted(set(today) - {r["combination"] for r in recorded}):
            moved.append(f"{name}: this tree has it and the recorded plan does not")
        if moved:
            raise SystemExit(
                "the recorded external plan is not one this tree can produce:\n  "
                + "\n  ".join(moved)
                + "\nThe rows are structural. Fix the tree or delete the record "
                  "deliberately; do not let this script rewrite it.")

        drift = {row["combination"]: {
            "recorded_planned_seconds": float(row["planned_seconds"]),
            "a_re_plan_today_would_say": today[row["combination"]]["planned_seconds"],
            "difference": round(today[row["combination"]]["planned_seconds"]
                                - float(row["planned_seconds"]), 1),
        } for row in recorded}
        moved_seconds = {k: v for k, v in drift.items() if v["difference"]}
        (RESULTS / "external_plan_check.json").write_text(json.dumps({
            "what_this_is": (
                "the recorded plan against what a re-plan would say today. The rows are "
                "verified and never rewritten; the estimate is a measured wall-clock "
                "duration and is reported when it drifts"),
            "manifest": str(manifest.relative_to(ROOT)),
            "rows_agree": True,
            "cost_unit_recorded": json.loads(
                (RESULTS / "external_plan.json").read_text())["cost_unit_value"],
            "cost_unit_today": unit,
            "estimates_that_drifted": len(moved_seconds),
            "drift": drift,
            "why_drift_is_not_fatal": (
                "the unit is the seconds the held-out `main` row took, read from "
                "05_stability/results/run_status_holdout.csv, which every run of "
                "05_stability/run.sh rewrites -- and that runs immediately before this "
                "script. An estimate that reproduced would mean the run it was measured "
                "from had not happened"),
        }, indent=2) + "\n")
        print(f"external plan: {len(recorded)} rows verified against the record, "
              f"{len(moved_seconds)} estimate(s) drifted (reported, not rewritten)")
        for row in recorded:
            print(f"{row['rank']}. {row['combination']:18s} {row['country']:9s} "
                  f"{row['locations_evaluated']:>3s} provinces  {row['cells']:>5s} cells  "
                  f"~{float(row['planned_seconds']) / 60:6.1f} min  {row['status']}")
        return 0

    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in planned:
            writer.writerow(row)

    (RESULTS / "external_plan.json").write_text(json.dumps({
        "what_this_is": (
            "the external check's four rows, planned and committed before any of them "
            "ran. No fork moves in any of them: the reported model runs unchanged and "
            "the dataset underneath is what differs"),
        "budget_hours": BUDGET_HOURS,
        "budget_basis": (
            "what analysis/run.sh already costs. An external check on the analysis should "
            "not cost more than the analysis. Set before anything here was costed"),
        "cost_unit": "seconds per evaluated cell",
        "cost_unit_value": unit,
        "cost_unit_measured_from": per_cell,
        "cost_unit_why": (
            "the holdout main row is the same pipeline these four rows run, on a dataset "
            "where nothing had run before -- every setup fork at its main child, both "
            "baselines, the reference's four unseeded repeats, the reported pool and the "
            "scoring chain. The development main row runs conclude.py alone and costs "
            "nothing, so it cannot be the unit"),
        "cut_order": [c[2] for c in reversed(COUNTRIES)],
        "cut_unit": "whole country, because the check measures the drop between a "
                    "country's two arrangements and half a country measures nothing",
        "planned_seconds_total": round(total, 1),
        "planned_hours_total": round(total / 3600, 2),
        "within_budget": total <= budget_seconds,
        "cut": cut,
        "cut_none_because": (
            None if cut else
            f"the estimate, {round(total / 3600, 2)} h, is inside the {BUDGET_HOURS} h "
            f"budget"),
    }, indent=2) + "\n")

    for row in planned:
        print(f"{row['rank']}. {row['combination']:18s} {row['country']:9s} "
              f"{row['locations_evaluated']:3d} provinces  {row['cells']:5d} cells  "
              f"~{row['planned_seconds'] / 60:6.1f} min  {row['status']}")
    print(f"total ~{total / 3600:.2f} h against a {BUDGET_HOURS} h budget; "
          f"cut: {cut or 'nothing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
