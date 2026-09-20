#!/usr/bin/env python3
"""Per-province characterisation of the development file only.

Reads only `01_prepare/results/development.csv` -- never the holdout -- and reports, per
province: number of months present, number missing, first and last non-missing month, and
the zero-rate among non-missing observations. A province is judged modelable if it has at
least 24 non-missing months (two years -- the minimum for a SARIMAX with a 12-month seasonal
term to estimate anything at all); this is a judgment call, logged below rather than left
silent (plan §3).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
DEV_CSV = NODE.parent / "01_prepare" / "results" / "development.csv"
RESULTS = NODE / "results"
MIN_MODELABLE_MONTHS = 24


def characterise() -> list[dict]:
    with DEV_CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))

    by_loc: dict[str, list[dict]] = {}
    for r in rows:
        by_loc.setdefault(r["location"], []).append(r)

    out = []
    for loc in sorted(by_loc):
        recs = sorted(by_loc[loc], key=lambda r: r["time_period"])
        present = [r for r in recs if r["disease_cases"] != ""]
        n_total, n_present = len(recs), len(present)
        n_zero = sum(1 for r in present if float(r["disease_cases"]) == 0)
        out.append({
            "location": loc,
            "location_name": recs[0]["location_name"],
            "n_months_total": n_total,
            "n_months_present": n_present,
            "n_months_missing": n_total - n_present,
            "first_present_month": present[0]["time_period"] if present else None,
            "last_present_month": present[-1]["time_period"] if present else None,
            "zero_rate": round(n_zero / n_present, 4) if n_present else None,
            "modelable": n_present >= MIN_MODELABLE_MONTHS,
        })

    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "province_summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    modelable = [r["location"] for r in out if r["modelable"]]
    not_modelable = [r["location"] for r in out if not r["modelable"]]
    summary = {
        "min_modelable_months": MIN_MODELABLE_MONTHS,
        "n_provinces_total": len(out),
        "n_modelable": len(modelable),
        "modelable_provinces": modelable,
        "excluded_provinces": not_modelable,
    }
    (RESULTS / "modelability_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return out


if __name__ == "__main__":
    result = characterise()
    excluded = [r for r in result if not r["modelable"]]
    print(f"{len(result)} provinces, {len(result) - len(excluded)} modelable")
    for r in excluded:
        print(f"  excluded: {r['location']} ({r['location_name']}) - "
              f"{r['n_months_present']}/{r['n_months_total']} months present")
