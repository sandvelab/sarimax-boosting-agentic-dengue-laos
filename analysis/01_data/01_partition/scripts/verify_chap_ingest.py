#!/usr/bin/env python3
"""Confirm both parts are already in the form `chap eval` expects, losslessly.

The plan asks for the conversion to Chap's input format and for evidence that it is
lossless. The finding is that there is no conversion: `chap eval` takes a CSV with
`time_period`, `location`, `disease_cases` and covariate columns, which is what the
archived file already is. What has to be shown is therefore that chap-core's own
reader takes each part without dropping or altering anything -- so the check loads
each part through `DataSet.from_csv`, brings it back with `to_pandas`, and compares
cell by cell against the file.

The holdout is loaded and counted, never summarised: the comparison is an equality
test against the file it came from, which reveals nothing about 2010 that the file
does not already have to be for the test to pass.

Seeds: none. The comparison is deterministic; the project seed 20260822 has no
surface here.

Usage:  "$PYTHON" scripts/verify_chap_ingest.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from chap_core.spatio_temporal_data.temporal_dataclass import DataSet

NODE = Path(__file__).resolve().parent.parent
RESULTS = NODE / "results"
PARTS = {
    "development": RESULTS / "development_1998-01_2009-12.csv",
    "holdout": RESULTS / "holdout_2010_SEALED.csv",
}


def check(name: str, path: Path) -> dict:
    on_disk = pd.read_csv(path, dtype={"time_period": str})
    loaded = DataSet.from_csv(str(path)).to_pandas()

    # `to_pandas` groups by location, so align both on the primary key before comparing.
    key = ["location", "time_period"]
    a = on_disk.sort_values(key).reset_index(drop=True)
    b = loaded.astype({"time_period": str}).sort_values(key).reset_index(drop=True)

    shared = [c for c in a.columns if c in b.columns]
    added = [c for c in b.columns if c not in a.columns]
    dropped = [c for c in a.columns if c not in b.columns]

    mismatches = {}
    for c in shared:
        if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c]):
            differs = ~((a[c] - b[c]).abs().le(0) | (a[c].isna() & b[c].isna()))
        else:
            differs = (a[c].astype(str) != b[c].astype(str)) & ~(a[c].isna() & b[c].isna())
        if int(differs.sum()):
            mismatches[c] = int(differs.sum())

    return {
        "part": name,
        "file": str(path.relative_to(NODE)),
        "rows_on_disk": int(len(a)),
        "rows_after_load": int(len(b)),
        "row_counts_agree": len(a) == len(b),
        "locations_on_disk": int(a["location"].nunique()),
        "locations_after_load": int(b["location"].nunique()),
        "columns_shared": shared,
        "columns_added_by_loader": added,
        "columns_dropped_by_loader": dropped,
        "target_nulls_on_disk": int(a["disease_cases"].isna().sum()),
        "target_nulls_after_load": int(b["disease_cases"].isna().sum()),
        "cells_differing_by_column": mismatches,
        "lossless": (len(a) == len(b) and not dropped and not mismatches
                     and int(a["disease_cases"].isna().sum())
                     == int(b["disease_cases"].isna().sum())),
    }


def main() -> int:
    report = {
        "reader": "chap_core.spatio_temporal_data.temporal_dataclass.DataSet.from_csv",
        "conversion_required": False,
        "conversion_note": (
            "`chap eval` reads the CSV directly; the archived file already carries "
            "time_period, location, disease_cases and the covariate columns it expects. "
            "No intermediate format is written, so there is no conversion step that "
            "could lose anything."
        ),
        "parts": [check(n, p) for n, p in PARTS.items()],
    }
    report["all_parts_lossless"] = all(p["lossless"] for p in report["parts"])
    (RESULTS / "chap_ingest_check.json").write_text(json.dumps(report, indent=2) + "\n")

    for p in report["parts"]:
        print(f"{p['part']}: lossless={p['lossless']} rows={p['rows_after_load']} "
              f"locations={p['locations_after_load']} added={p['columns_added_by_loader']}")
    return 0 if report["all_parts_lossless"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
