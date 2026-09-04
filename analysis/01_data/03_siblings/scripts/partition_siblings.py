#!/usr/bin/env python3
"""Cut the two sibling datasets into the same two arrangements the Lao file was cut into.

The plan's §4 names `tha` and `vnm` as the external check: the reported model, unchanged,
on two other countries. `01_partition` is the only node that reads the archived Lao file;
this is the only node that reads the archived sibling files, and everything downstream
reads what it writes.

**Nothing here is sealed and nothing here is a holdout.** The seal in plan §3 protects the
Lao 2010 because the model was developed against Lao 1998-2009 and a leak would have made
the headline number a lie. No model is developed on these two files -- the check runs the
model the tree already reports, at the configuration it already has -- so there is nothing
for these years to leak into. What they are is a second and a third measurement of the same
pair of backtests, and the two arrangements below are what make them that.

## The two arrangements, and why the calendar is held fixed

For each country, mirroring Laos exactly:

  * `<CODE>_development_1998-01_2009-12.csv` -- run under 3/8/3, which evaluates
    2008-01 to 2009-12 from a training set ending 2007-12. The analogue of the
    development backtest.
  * `<CODE>_full_1998-01_2010-12.csv` -- run under 3/4/3, which evaluates exactly 2010
    from a training set ending 2009-12. The analogue of the held-out year.

Vietnam's file already runs 1998-01 to 2010-12, so it needs only the first cut. Thailand's
runs 1993-01 to 2022-12 and is **truncated to the Lao calendar**, which is a judgment call
and is this script's, recorded here and in the node's `claim.md`: the question the external
check asks is whether the Lao result holds in another *place*, so the years are held fixed
and the country is what varies. Thailand's other twenty-two years are a different question
-- whether 2010 in particular was hard -- and this batch does not spend them.

What it establishes, all of it to disk:

  * that the archived sibling files still hash to what was fetched;
  * that each country's parts are exact subsets of its source, sharing its header, with no
    row invented, duplicated or lost inside the window;
  * the structure of each part: rows, provinces, span, missing cells in the province x
    month grid, duplicate primary keys, per-column nulls;
  * what each schema claims about its own file, against what the file contains -- the row
    count, the rainfall unit and whether population is static.

Seeds: none. Every cut is a deterministic filter on `time_period`, so the project seed
20260822 has no surface here.

Usage:  "$PYTHON" scripts/partition_siblings.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parent.parent
ROOT = NODE.parents[2]
ARCHIVE = ROOT / "Archive" / "sibling-datasets"
MANIFEST = ARCHIVE / "sha256sums.txt"
RESULTS = NODE / "results"

# The Lao calendar, which both siblings are put on. Read from the Lao partition's own
# output rather than repeated as a constant: those two files are what "the same calendar"
# means, and a constant here could fall out of step with them.
LAO_DEV = ROOT / "analysis/01_data/01_partition/results/development_1998-01_2009-12.csv"
LAO_FULL = ROOT / "analysis/01_data/01_partition/results/phase_e_1998-01_2010-12.csv"

COUNTRIES = {
    "THA": ARCHIVE / "tha" / "chap_THA_admin1_monthly.csv",
    "VNM": ARCHIVE / "vnm" / "chap_VNM_admin1_monthly.csv",
}
SCHEMAS = {
    "THA": ARCHIVE / "tha" / "chap_THA_admin1_monthly_schema.json",
    "VNM": ARCHIVE / "vnm" / "chap_VNM_admin1_monthly_schema.json",
}

DAYS_PER_MONTH = 30.4  # only to say which order of magnitude the rainfall column is in


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
        cwd=ARCHIVE, capture_output=True, text=True)
    return {
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "output": proc.stdout.strip().split("\n"),
    }


def read_table(path: Path) -> tuple[str, list[str]]:
    """The file as its header line and its data lines, unparsed.

    Carried as text for the same reason `01_partition` carries the Lao file as text: a
    parser round trip re-formats it -- an integer count in a column that also holds blanks
    comes back as `0.0` -- so a cut that claims to be a subset would produce a file that
    is not one. Every figure reported below is computed with pandas from the same bytes,
    which is a read and changes nothing.
    """
    text = path.read_text()
    header, _, body = text.partition("\n")
    return header, [line for line in body.split("\n") if line]


def write_table(path: Path, header: str, rows: list[str]) -> None:
    path.write_text(header + "\n" + "".join(line + "\n" for line in rows))


def months_between(first: str, last: str) -> list[str]:
    return [str(p) for p in pd.period_range(first, last, freq="M")]


def lao_span(path: Path) -> tuple[str, str]:
    periods = pd.read_csv(path, usecols=["time_period"], dtype=str)["time_period"]
    return periods.min(), periods.max()


def describe(name: str, frame: pd.DataFrame, first: str, last: str) -> dict:
    """The structure of one part, in the terms `01_partition` describes the Lao parts."""
    months = months_between(first, last)
    locations = sorted(frame["location"].unique())
    grid = len(locations) * len(months)
    return {
        "part": name,
        "rows": int(len(frame)),
        "locations": len(locations),
        "period_first": str(frame["time_period"].min()),
        "period_last": str(frame["time_period"].max()),
        "months_in_span": len(months),
        "grid_cells": grid,
        "rectangular": bool(len(frame) == grid),
        "missing_grid_cells": int(grid - len(frame)),
        "duplicate_primary_keys": int(
            frame.duplicated(subset=["location", "time_period"]).sum()),
        "target_observed": int(frame["disease_cases"].notna().sum()),
        "target_missing": int(frame["disease_cases"].isna().sum()),
        "nulls_by_column": {c: int(frame[c].isna().sum()) for c in frame.columns},
    }


def reconcile_schema(code: str, frame: pd.DataFrame, schema: dict) -> dict:
    """What the schema claims about its own file, against what the file contains.

    Three claims, each of which the Lao schema also makes and two of which it also gets
    wrong (`Archive/lao-dataset/provenance.md`). Answering them here for the siblings is
    what turns a Lao finding into a statement about the harmonisation.
    """
    declared = schema.get("dataset", {}).get("row_count")
    observed = int(frame["disease_cases"].notna().sum())
    annual = frame.groupby([frame["location"], frame["time_period"].str[:4]])["rainfall"].sum()
    per_province = frame.groupby("location")["population"].nunique()
    rainfall_field = next((f for f in schema.get("fields", [])
                           if f.get("name") == "rainfall"), {})
    population_field = next((f for f in schema.get("fields", [])
                             if f.get("name") == "population"), {})
    return {
        "country": code,
        "row_count_declared": declared,
        "rows_in_file": int(len(frame)),
        "rows_with_an_observed_target": observed,
        "row_count_means": (
            "rows in the file" if declared == len(frame)
            else "rows carrying a non-missing disease_cases" if declared == observed
            else "neither the row count nor the count of complete records"),
        "rainfall_unit_declared": rainfall_field.get("unit"),
        "rainfall_description_declared": rainfall_field.get("description"),
        "annual_sum_of_monthly_rainfall_min": float(annual.min()),
        "annual_sum_of_monthly_rainfall_median": float(annual.median()),
        "annual_sum_of_monthly_rainfall_max": float(annual.max()),
        "annual_rainfall_if_column_is_a_daily_rate_median":
            float(annual.median() * DAYS_PER_MONTH),
        "rainfall_column_is_a_daily_rate": bool(annual.median() < 200),
        "population_description_declared": population_field.get("description"),
        "population_constant_per_province": bool((per_province == 1).all()),
        "provinces_with_a_varying_population": int((per_province > 1).sum()),
        "provinces": int(len(per_province)),
    }


def cut(header: str, rows: list[str], period_column: int,
        first: str, last: str) -> list[str]:
    return [line for line in rows
            if first <= line.split(",")[period_column] <= last]


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    archive_check = verify_archive()
    if not archive_check["ok"]:
        raise SystemExit(f"archived sibling files do not match {MANIFEST}: "
                         + "\n".join(archive_check["output"]))

    dev_first, dev_last = lao_span(LAO_DEV)
    full_first, full_last = lao_span(LAO_FULL)

    structure, reconciliations, parts, checks = [], [], {}, {}
    for code, source in COUNTRIES.items():
        header, rows = read_table(source)
        period = header.split(",").index("time_period")
        schema = json.loads(SCHEMAS[code].read_text())
        whole = pd.read_csv(source, dtype={"time_period": str})
        reconciliations.append(reconcile_schema(code, whole, schema))

        written = {}
        for name, (first, last) in {
                "development": (dev_first, dev_last),
                "full": (full_first, full_last)}.items():
            kept = cut(header, rows, period, first, last)
            out = RESULTS / f"{code}_{name}_{first}_{last}.csv"
            write_table(out, header, kept)
            frame = pd.read_csv(out, dtype={"time_period": str})
            row = describe(f"{code}_{name}", frame, first, last)
            row["file"] = str(out.relative_to(ROOT))
            row["sha256"] = sha256(out)
            structure.append(row)
            written[name] = (out, kept)

        # The parts are subsets of one source, sharing its header, and the development
        # part is a subset of the full part. Checked as sets of lines rather than as
        # counts: a count agreeing is not the same as the rows being the same rows.
        source_lines = set(rows)
        dev_lines = set(written["development"][1])
        full_lines = set(written["full"][1])
        checks[code] = {
            "source": str(source.relative_to(ROOT)),
            "source_sha256": sha256(source),
            "source_rows": len(rows),
            "source_period_first": str(whole["time_period"].min()),
            "source_period_last": str(whole["time_period"].max()),
            "window_kept": [full_first, full_last],
            "rows_outside_the_window": len(rows) - len(full_lines),
            "development_rows_all_from_source": dev_lines <= source_lines,
            "full_rows_all_from_source": full_lines <= source_lines,
            "development_is_a_subset_of_full": dev_lines < full_lines,
            "no_row_duplicated_in_a_part":
                len(written["development"][1]) == len(dev_lines)
                and len(written["full"][1]) == len(full_lines),
            "full_minus_development_is_exactly_the_final_year": sorted({
                line.split(",")[period][:4]
                for line in full_lines - dev_lines}) == [full_last[:4]],
            "header_preserved": True,
        }
        parts[code] = written

    pd.DataFrame(structure).to_csv(RESULTS / "part_structure.csv", index=False)
    (RESULTS / "schema_reconciliation.json").write_text(
        json.dumps({"countries": reconciliations,
                    "what_this_is": (
                        "each sibling schema's claims about its own file, against the "
                        "file. The Lao schema makes the same three claims and gets two "
                        "of them wrong; these say whether that is the harmonisation's "
                        "or the Lao file's")},
                   indent=2) + "\n")
    (RESULTS / "sibling_partition_check.json").write_text(
        json.dumps({"archive_verification": archive_check,
                    "lao_calendar": {
                        "development": [dev_first, dev_last],
                        "full": [full_first, full_last],
                        "read_from": [str(LAO_DEV.relative_to(ROOT)),
                                      str(LAO_FULL.relative_to(ROOT))]},
                    "countries": checks}, indent=2) + "\n")
    (RESULTS / "sibling_outputs.sha256").write_text("".join(
        f"{sha256(p)}  {p.relative_to(ROOT)}\n" for p in sorted(
            [written[n][0] for written in parts.values() for n in written]
            + [RESULTS / "part_structure.csv",
               RESULTS / "schema_reconciliation.json",
               RESULTS / "sibling_partition_check.json"])))

    for row in structure:
        print(f"{row['part']:20s} {row['rows']:6d} rows  {row['locations']:3d} provinces  "
              f"{row['period_first']}..{row['period_last']}  "
              f"target observed {row['target_observed']}")
    for rec in reconciliations:
        print(f"{rec['country']}: row_count {rec['row_count_declared']} means "
              f"{rec['row_count_means']}; rainfall is a daily rate: "
              f"{rec['rainfall_column_is_a_daily_rate']}; population constant per "
              f"province: {rec['population_constant_per_province']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
