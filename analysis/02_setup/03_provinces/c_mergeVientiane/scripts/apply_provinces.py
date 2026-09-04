"""Stage 3 of the common setup: Vientiane province is merged into Vientiane Capital.

Vientiane Capital is a prefecture carved out of Vientiane province and geographically
surrounded by it. The province reports no dengue case anywhere in the record while the
capital reports the largest counts in the country, which is not plausible as
epidemiology: the two are one settlement system with an administrative line through it,
and the line is where the reporting stops rather than where the disease does.

The other two children of this fork treat the silent province as a unit that is either
dropped by the platform (`a_chapFilter`) or removed by us (`b_reportingOnly`). This child
treats it as part of its neighbour, so the map has no hole in it and the capital's
denominator is the population that actually surrounds it. It is the only child of the
three that changes the *cells* the metric is a mean over, which is why the project's
reported conclusion is a ratio to the reference computed on whatever cell set a child
produced, and not a raw CRPS.

**Three merge rules, each a judgment and each recorded.**

*Counts add.* The merged unit's `disease_cases` is the sum of what its constituents
reported. A constituent that reported nothing in a month contributes nothing to that
month; the merged value is missing only when every constituent is missing. The
alternative -- missing when *any* constituent is missing -- was rejected because the
donor here never reports at all, so it would erase the capital's entire series and
replace the fork with a deletion.

*Population adds.* The merged unit serves the merged population, and it is summed per
row rather than per province, so the rule survives unchanged if the population column is
a per-year series rather than a snapshot.

*Climate is an area-weighted mean.* The three climate columns are ERA5-Land fields
aggregated over the admin polygon, so they are area means already, and the mean over a
union of polygons is the area-weighted mean of the parts. The weights are geodesic areas
computed from the archived boundary file, not typed. Weighting by population instead was
rejected: it would answer "what climate did the average person experience", which is a
different quantity from the one the column holds, and mixing the two inside one column is
the kind of silent redefinition this project exists to make visible.

**Which units merge is a named geographic judgment, not a derivation.** Nothing in the
data says Vientiane Capital lies inside Vientiane province. The pair is declared below,
checked against the file, and stated in the specification; it is `agent-autonomous` and
it is the substantive content of this child.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves this stage
  setup_spec.json        the merge, its rules, its weights, and what it did to the data
  merge_weights.csv      the geodesic area and merged population behind each rule
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd
from pyproj import Geod
from shapely.geometry import shape

NODE = Path(__file__).resolve().parents[1]
SETUP = NODE.parents[1]

# donor -> receiver. Vientiane province into Vientiane Capital.
MERGE = {"LA-VI": "LA-VT"}
COUNT_COLUMNS = ("disease_cases",)
SUM_COLUMNS = ("population",)
AREA_MEAN_COLUMNS = ("rainfall", "mean_temperature", "mean_relative_humidity")
BOUNDARIES = "Archive/lao-dataset/chap_LAO_admin1_monthly.geojson"
# Which stored scheme file this combination reads is a property of the dataset it
# faces, not a constant of this script: the Lao schemes are in `01_data/02_characterise`
# and the sibling calendars the external check runs on are in `01_data/03_siblings`.
# `combos` is the one place that decision lives, as it is for the source file.


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")
sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
import combos  # noqa: E402



def upstream(fork: str, combo: str) -> Path:
    found = sorted((SETUP / fork).glob(f"*/results/{combo}/analysis_dataset.csv"))
    if len(found) != 1:
        raise SystemExit(
            f"{fork}: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(SETUP)) for p in found]}")
    return found[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[str, list[str]]:
    """The file as its header line and its data lines, unparsed. See `a_chapFilter`."""
    text = path.read_text()
    header, _, body = text.partition("\n")
    return header, [line for line in body.split("\n") if line]


def write_table(path: Path, header: str, rows: list[str]) -> None:
    path.write_text(header + "\n" + "".join(line + "\n" for line in rows))


def geodesic_areas() -> dict[str, float]:
    """Square metres per province, from the archived boundary polygons."""
    geod = Geod(ellps="WGS84")
    features = json.loads((ROOT / BOUNDARIES).read_text())["features"]
    out = {}
    for feature in features:
        area, _ = geod.geometry_area_perimeter(shape(feature["geometry"]))
        out[feature["properties"]["shapeISO"]] = abs(area)
    return out


def number(value: float, like: str) -> str:
    """Render a merged value the way the column it belongs to is rendered.

    `like` is one of the values that went into it, so a column of whole numbers stays a
    column of whole numbers and a column of full-precision floats keeps its precision.
    """
    if value != value:                       # NaN
        return ""
    if "." not in like and "e" not in like.lower():
        return str(int(round(value)))
    return repr(float(value))


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    source = upstream("02_trainingWindow", COMBO)
    header, rows = read_table(source)
    columns = header.split(",")
    at = {name: columns.index(name) for name in columns}

    present = {line.split(",")[at["location"]] for line in rows}
    for donor, receiver in MERGE.items():
        if donor not in present or receiver not in present:
            raise SystemExit(f"the merge {donor} -> {receiver} names a province the "
                             f"dataset does not carry: it has {sorted(present)}")

    areas = geodesic_areas()
    missing_areas = sorted(set(MERGE) | set(MERGE.values()) - set(areas))
    if any(code not in areas for code in [*MERGE, *MERGE.values()]):
        raise SystemExit(f"{BOUNDARIES} has no polygon for {missing_areas}")

    # Group the rows that will merge, keyed by (receiver, period).
    parsed = [line.split(",") for line in rows]
    groups: dict[tuple[str, str], list[list[str]]] = {}
    for fields in parsed:
        location = fields[at["location"]]
        receiver = MERGE.get(location, location)
        if receiver in MERGE.values():
            groups.setdefault((receiver, fields[at["time_period"]]), []).append(fields)

    merged_lines: dict[tuple[str, str], str] = {}
    partial_cells = 0
    for (receiver, period), members in groups.items():
        template = next(f for f in members if f[at["location"]] == receiver)
        fields = list(template)
        for name in COUNT_COLUMNS:
            values = [f[at[name]] for f in members]
            reported = [float(v) for v in values if v != ""]
            if len(reported) not in (0, len(values)):
                partial_cells += 1
            fields[at[name]] = ("" if not reported
                                else number(sum(reported), next(v for v in values if v != "")))
        for name in SUM_COLUMNS:
            values = [f[at[name]] for f in members]
            fields[at[name]] = number(sum(float(v) for v in values), values[0])
        for name in AREA_MEAN_COLUMNS:
            weights = [areas[f[at["location"]]] for f in members]
            values = [float(f[at[name]]) for f in members]
            weighted = sum(w * v for w, v in zip(weights, values)) / sum(weights)
            fields[at[name]] = number(weighted, template[at[name]])
        merged_lines[(receiver, period)] = ",".join(fields)

    # Rebuild in the incoming order: donors drop out, receivers are replaced.
    kept: list[str] = []
    for line, fields in zip(rows, parsed):
        location = fields[at["location"]]
        if location in MERGE:
            continue
        if location in MERGE.values():
            kept.append(merged_lines[(location, fields[at["time_period"]])])
        else:
            kept.append(line)
    write_table(out / "analysis_dataset.csv", header, kept)

    frame = pd.read_csv(out / "analysis_dataset.csv", dtype={"time_period": str})
    scheme = json.loads(combos.scheme_file(ROOT).read_text())
    # The span this combination is evaluated over: 2008-01..2009-12 on development,
    # 2010-01..2010-12 on the holdout. Read from the stored scheme by the key
    # `combos` derives from the combination name, so a holdout row applies this fork's
    # rule to the year it is actually scored on rather than to development's.
    span_first, span_last = scheme[combos.span_key()]
    observed = frame.dropna(subset=["disease_cases"])
    in_span = observed[(observed["time_period"] >= span_first)
                       & (observed["time_period"] <= span_last)]

    weights = pd.DataFrame([
        {"receiver": receiver, "constituent": code,
         "geodesic_area_m2": areas[code],
         "area_weight": areas[code] / sum(areas[c] for c in
                                          [receiver, *[d for d, r in MERGE.items()
                                                       if r == receiver]]),
         "population_first_period": int(frame.loc[frame.location == receiver, "population"]
                                        .iloc[0]) if code == receiver else None}
        for receiver in sorted(set(MERGE.values()))
        for code in [receiver, *sorted(d for d, r in MERGE.items() if r == receiver)]])
    weights.to_csv(out / "merge_weights.csv", index=False)

    spec = {
        "combo": COMBO,
        "stage": "provinces",
        "order": 3,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "c_mergeVientiane",
        "description": "Vientiane province merged into Vientiane Capital",
        "dataset_transform": "donor rows removed; receiver rows replaced by merged values",
        "merge": MERGE,
        "merge_basis": "geographic: Vientiane Capital is a prefecture carved out of "
                       "Vientiane province and surrounded by it. Declared, not derived "
                       "from the data, and agent-autonomous.",
        "merge_rules": {
            "disease_cases": "sum of the constituents that reported; missing only when "
                             "every constituent is missing",
            "population": "sum, per row",
            "rainfall / mean_temperature / mean_relative_humidity":
                "area-weighted mean, weights = geodesic polygon areas from "
                + BOUNDARIES,
        },
        "merged_unit_reported_under": {r: "the receiver's own code and location_name; "
                                          "the constituents are named in `merge`"
                                       for r in sorted(set(MERGE.values()))},
        "geodesic_areas_m2": {code: areas[code]
                              for code in sorted(set(MERGE) | set(MERGE.values()))},
        "boundaries": BOUNDARIES,
        "boundaries_sha256": sha256(ROOT / BOUNDARIES),
        "cells_where_some_but_not_all_constituents_reported": partial_cells,
        "input": str(source.relative_to(ROOT)),
        "input_sha256": sha256(source),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": len(rows),
        "rows_out": len(kept),
        "locations_in_file": int(frame["location"].nunique()),
        "locations_never_reporting": sorted(set(frame["location"])
                                            - set(observed["location"])),
        "evaluated_span": [span_first, span_last],
        "expected_locations_contributing": int(in_span["location"].nunique()),
        "expected_evaluable_cells": int(len(in_span)),
        "eval_flags": {},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"provinces/c_mergeVientiane: {MERGE}; {len(rows)} -> {len(kept)} rows, "
          f"{frame['location'].nunique()} provinces, "
          f"{spec['expected_locations_contributing']} expected to contribute "
          f"{spec['expected_evaluable_cells']} cells")


if __name__ == "__main__":
    main()
