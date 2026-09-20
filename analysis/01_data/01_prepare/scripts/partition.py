#!/usr/bin/env python3
"""Partition the archived Laos dataset into development and sealed holdout files.

Verifies the archive's own checksums first (Rule 1: no step trusts an input it has not
checked), splits on time_period <= "2009-12" vs >= "2010-01" (plan §4: development is
1998-01 to 2009-12, held out is 2010), and writes a completeness report for the holdout
that looks only at row counts, provinces present and months present -- never at
disease_cases values, per the plan's §3 non-negotiable that the holdout is not
characterised beyond completeness before it opens.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
ARCHIVE = REPO_ROOT / "Archive" / "lao-dataset"
SOURCE_CSV = ARCHIVE / "chap_LAO_admin1_monthly.csv"
DEV_CUTOFF = "2009-12"  # inclusive
RESULTS = NODE / "results"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_archive_checksums() -> None:
    sums_file = ARCHIVE / "sha256sums.txt"
    recorded = {}
    for line in sums_file.read_text().splitlines():
        digest, _, name = line.strip().partition("  ")
        if name:
            recorded[name] = digest
    for name, digest in recorded.items():
        actual = sha256_of(ARCHIVE / name)
        if actual != digest:
            raise SystemExit(
                f"checksum mismatch for {name}: recorded {digest}, actual {actual}"
            )


def partition() -> dict:
    with SOURCE_CSV.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    dev_rows = [r for r in rows if r["time_period"] <= DEV_CUTOFF]
    holdout_rows = [r for r in rows if r["time_period"] > DEV_CUTOFF]

    RESULTS.mkdir(exist_ok=True)

    def write_csv(path: Path, out_rows: list[dict]) -> None:
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(out_rows)

    write_csv(RESULTS / "development.csv", dev_rows)
    write_csv(RESULTS / "holdout.csv", holdout_rows)

    # Completeness only: row count, provinces present, months present. No case values.
    completeness = {
        "n_rows": len(holdout_rows),
        "n_provinces": len(sorted({r["location"] for r in holdout_rows})),
        "provinces": sorted({r["location"] for r in holdout_rows}),
        "months": sorted({r["time_period"] for r in holdout_rows}),
        "n_months": len(sorted({r["time_period"] for r in holdout_rows})),
        "expected_n_rows": 18 * 12,
        "complete": len(holdout_rows) == 18 * 12
        and sorted({r["time_period"] for r in holdout_rows})
        == [f"2010-{m:02d}" for m in range(1, 13)],
    }
    (RESULTS / "holdout_completeness.json").write_text(
        json.dumps(completeness, indent=2) + "\n"
    )

    summary = {
        "source": str(SOURCE_CSV.relative_to(REPO_ROOT)),
        "source_sha256": sha256_of(SOURCE_CSV),
        "n_rows_total": len(rows),
        "n_rows_development": len(dev_rows),
        "n_rows_holdout": len(holdout_rows),
        "development_range": [dev_rows[0]["time_period"], dev_rows[-1]["time_period"]],
        "holdout_complete": completeness["complete"],
    }
    (RESULTS / "partition_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    verify_archive_checksums()
    result = partition()
    print(json.dumps(result, indent=2))
