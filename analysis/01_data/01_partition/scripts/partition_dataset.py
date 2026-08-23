#!/usr/bin/env python3
"""Cut the archived Lao dataset into a development period and a sealed holdout year.

This is the only script in the project that reads the full file. Everything
downstream reads `results/development_1998-01_2009-12.csv`; the held-out year is
written and then left alone until phase E (plan §3).

What it establishes, all of it to disk:
  * that the archived source still hashes to what was fetched;
  * that the two parts partition the source exactly -- every data line in one part
    or the other, none in both, none lost, and the header preserved;
  * the structure of each part: rows, provinces, period span, missing cells in the
    province x month grid, duplicate primary keys, and per-column null counts;
  * the row-count discrepancy between the schema (2575) and the file, resolved
    against candidate explanations computed from the data itself.

Structure is all it reports about the holdout. No case value of 2010 is read,
summarised or plotted here -- completeness counts are what plan §3 permits and
they are the boundary.

Seeds: none. Nothing here draws randomness; the partition is a deterministic
filter on `time_period`, so the project seed 20260822 has no surface.

Usage:  "$PYTHON" scripts/partition_dataset.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parent.parent
ROOT = NODE.parents[2]
SOURCE = ROOT / "Archive" / "lao-dataset" / "chap_LAO_admin1_monthly.csv"
SCHEMA = ROOT / "Archive" / "lao-dataset" / "chap_LAO_admin1_monthly_schema.json"
MANIFEST = ROOT / "Archive" / "lao-dataset" / "sha256sums.txt"
RESULTS = NODE / "results"

DEV_FIRST, DEV_LAST = "1998-01", "2009-12"
HOLDOUT_FIRST, HOLDOUT_LAST = "2010-01", "2010-12"
DEV_OUT = RESULTS / "development_1998-01_2009-12.csv"
HOLDOUT_OUT = RESULTS / "holdout_2010_SEALED.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_archive() -> dict:
    """Re-check the archived files against the manifest written when they were fetched."""
    proc = subprocess.run(
        ["shasum", "-a", "256", "-c", MANIFEST.name],
        cwd=MANIFEST.parent, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"archive checksum mismatch:\n{proc.stdout}{proc.stderr}")
    return {
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "checked": [l.strip() for l in proc.stdout.strip().splitlines()],
        "source_sha256": sha256(SOURCE),
    }


def is_subsequence(part: list[str], whole: list[str]) -> bool:
    """Does `part` appear in `whole` in the same relative order? A part that lost the
    file's ordering would still pass a set comparison, and ordering is what a rolling
    backtest reads."""
    it = iter(whole)
    return all(line in it for line in part)


def months_between(first: str, last: str) -> list[str]:
    y0, m0 = (int(x) for x in first.split("-"))
    y1, m1 = (int(x) for x in last.split("-"))
    return [f"{y0 + (m0 - 1 + i) // 12:04d}-{(m0 - 1 + i) % 12 + 1:02d}"
            for i in range((y1 - y0) * 12 + (m1 - m0) + 1)]


def describe(name: str, frame: pd.DataFrame, first: str, last: str) -> dict:
    """Structural description of one part. Structure only -- no values are summarised."""
    expected_months = months_between(first, last)
    locations = sorted(frame["location"].unique())
    present = set(zip(frame["location"], frame["time_period"]))
    expected = {(loc, m) for loc in locations for m in expected_months}
    observed_months = sorted(frame["time_period"].unique())
    return {
        "part": name,
        "rows": int(len(frame)),
        "locations": len(locations),
        "location_ids": ",".join(locations),
        "period_first": observed_months[0] if observed_months else "",
        "period_last": observed_months[-1] if observed_months else "",
        "months_observed": len(observed_months),
        "months_expected": len(expected_months),
        "months_missing": ",".join(sorted(set(expected_months) - set(observed_months))) or "-",
        "grid_cells_expected": len(expected),
        "grid_cells_missing": len(expected - present),
        "duplicate_primary_keys": int(len(frame) - len(present)),
        **{f"nulls_{c}": int(frame[c].isna().sum()) for c in frame.columns},
    }


def reconcile_row_count(source: pd.DataFrame, schema: dict) -> dict:
    """The schema states 2575 rows; the file carries a different number. Establish which
    is right, and test candidate explanations for the stated figure against the data."""
    stated = int(schema["dataset"]["row_count"])
    actual = int(len(source))
    n_loc = source["location"].nunique()
    n_months = source["time_period"].nunique()
    candidates = {
        "rows_in_file": actual,
        "locations_x_months": int(n_loc * n_months),
        "rows_with_disease_cases_not_null": int(source["disease_cases"].notna().sum()),
        "rows_with_disease_cases_nonzero": int((source["disease_cases"].fillna(0) > 0).sum()),
        "rows_with_no_null_in_any_column": int(source.notna().all(axis=1).sum()),
        "rows_excluding_first_year": int((source["time_period"] < "1999-01").pipe(lambda s: (~s).sum())),
        "rows_excluding_final_year": int((source["time_period"] < "2010-01").sum()),
        "distinct_primary_keys": int(len(source.drop_duplicates(["location", "time_period"]))),
    }
    return {
        "schema_states": stated,
        "file_carries": actual,
        "schema_matches_file": stated == actual,
        "panel_is_complete_rectangle": actual == n_loc * n_months,
        "n_locations": int(n_loc),
        "n_months": int(n_months),
        "candidate_explanations_for_stated_figure": candidates,
        "candidates_matching_stated_figure":
            sorted(k for k, v in candidates.items() if v == stated),
        "schema_created_utc": schema["dataset"]["created_utc"],
        "schema_names_geojson": schema["dataset"]["admin_geojson_file"],
        "geojson_actually_present":
            (ROOT / "Archive" / "lao-dataset" / "chap_LAO_admin1_monthly.geojson").name,
    }


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    archive = verify_archive()

    raw = SOURCE.read_text().splitlines(keepends=True)
    header, body = raw[0], raw[1:]

    # Partition on the text lines, so exactness is a statement about the file and not
    # about how a parser happened to round a float on the way out.
    DEV_OUT.write_text(header + "".join(l for l in body if l.split(",", 1)[0] <= DEV_LAST))
    HOLDOUT_OUT.write_text(header + "".join(l for l in body if l.split(",", 1)[0] > DEV_LAST))

    # Verify against what is on disk, not against the lists just held in memory: the
    # files are what everything downstream reads, and a round trip through the
    # filesystem is exactly the step a memory-only check would not cover.
    dev_raw = DEV_OUT.read_text().splitlines(keepends=True)
    hold_raw = HOLDOUT_OUT.read_text().splitlines(keepends=True)
    dev_lines, hold_lines = dev_raw[1:], hold_raw[1:]

    # The source is ordered by province and then by month, so a cut on time is not a
    # prefix and a suffix of the file. Union-of-content and order-within-part are
    # therefore checked separately; concatenating the parts would not rebuild the file.
    union_hash = hashlib.sha256("".join(sorted(dev_lines + hold_lines)).encode()).hexdigest()
    source_hash = hashlib.sha256("".join(sorted(body)).encode()).hexdigest()

    partition_check = {
        "source_lines_data": len(body),
        "development_lines": len(dev_lines),
        "holdout_lines": len(hold_lines),
        "counts_sum_to_source": len(dev_lines) + len(hold_lines) == len(body),
        "no_line_in_both": len(set(dev_lines) & set(hold_lines)) == 0,
        "content_union_is_byte_identical_to_source": union_hash == source_hash,
        "sorted_union_sha256": union_hash,
        "sorted_source_sha256": source_hash,
        "development_is_a_subsequence_of_source": is_subsequence(dev_lines, body),
        "holdout_is_a_subsequence_of_source": is_subsequence(hold_lines, body),
        "header_preserved_in_both":
            dev_raw[0] == header and hold_raw[0] == header,
        "development_period_range": [
            min(l.split(",", 1)[0] for l in dev_lines),
            max(l.split(",", 1)[0] for l in dev_lines)],
        "holdout_period_range": [
            min(l.split(",", 1)[0] for l in hold_lines),
            max(l.split(",", 1)[0] for l in hold_lines)],
        "development_span_declared": [DEV_FIRST, DEV_LAST],
        "holdout_span_declared": [HOLDOUT_FIRST, HOLDOUT_LAST],
        "archive": archive,
    }
    partition_check["spans_match_declaration"] = (
        partition_check["development_period_range"] == [DEV_FIRST, DEV_LAST]
        and partition_check["holdout_period_range"] == [HOLDOUT_FIRST, HOLDOUT_LAST]
    )
    partition_check["partition_is_exact"] = all(
        partition_check[k] for k in (
            "counts_sum_to_source", "no_line_in_both",
            "content_union_is_byte_identical_to_source",
            "development_is_a_subsequence_of_source",
            "holdout_is_a_subsequence_of_source",
            "header_preserved_in_both", "spans_match_declaration",
        )
    )

    source = pd.read_csv(SOURCE, dtype={"time_period": str})
    dev = pd.read_csv(DEV_OUT, dtype={"time_period": str})
    hold = pd.read_csv(HOLDOUT_OUT, dtype={"time_period": str})

    structure = pd.DataFrame([
        describe("source", source, DEV_FIRST, HOLDOUT_LAST),
        describe("development", dev, DEV_FIRST, DEV_LAST),
        describe("holdout", hold, HOLDOUT_FIRST, HOLDOUT_LAST),
    ])
    structure.to_csv(RESULTS / "part_structure.csv", index=False)

    schema = json.loads(SCHEMA.read_text())
    (RESULTS / "rowcount_reconciliation.json").write_text(
        json.dumps(reconcile_row_count(source, schema), indent=2) + "\n")
    (RESULTS / "partition_check.json").write_text(
        json.dumps(partition_check, indent=2) + "\n")

    # Hash exactly what this script wrote, listed explicitly rather than globbed, so a
    # later script adding a file to results/ cannot silently change what the manifest
    # claims to cover.
    (RESULTS / "partition_outputs.sha256").write_text("".join(
        f"{sha256(f)}  {f.name}\n" for f in (
            DEV_OUT, HOLDOUT_OUT,
            RESULTS / "part_structure.csv",
            RESULTS / "rowcount_reconciliation.json",
            RESULTS / "partition_check.json",
        )
    ))

    print(f"partition exact: {partition_check['partition_is_exact']}")
    print(f"development rows: {len(dev_lines)}   holdout rows: {len(hold_lines)}")
    print(f"wrote {len(list(RESULTS.glob('*')))} files to {RESULTS.relative_to(ROOT)}")
    return 0 if partition_check["partition_is_exact"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
