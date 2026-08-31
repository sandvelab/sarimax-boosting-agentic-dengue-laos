"""Stage 1 of the common setup: the population column, back-cast to a per-year series.

The sibling takes the archived column as it stands: one figure per province, held
constant across thirteen years, which the dataset's schema attributes to WorldPop and
dates to 2020. This child takes the other reading. A denominator that is right at one
end of the record and a decade of growth wrong at the other is not a constant, and a
model that divides by it is being handed a covariate whose error is a trend.

**The construction.** For each year of the record the province's figure is the snapshot
scaled by how much the country grew between that year and the snapshot's reference year:

    population(province, year) = snapshot(province) x N(year) / N(reference year)

with N the national annual total archived in `Archive/lao-population/`. The snapshot's
own level and its split across provinces are left exactly as the archive supplies them;
only the year-to-year movement is added.

**What this construction cannot do, said here rather than discovered later.** The series
is national, so every province is scaled by the same factor and the fork does not probe
whether Vientiane Capital grew faster than Phongsaly -- which it certainly did. What it
does probe is whether a *trend* in the denominator moves the conclusion, which is the
part a single snapshot gets wrong for every province at once. A provincial series would
need the 1995, 2005 and 2015 censuses, and `Archive/lao-population/provenance.md` records
why those are not here.

**Two things about the anchor year.** The schema says 2020, and that is what is used,
read from the schema file rather than typed. But the archived column sums to about
5.0 million across the eighteen provinces, and the national total was 7.35 million in
2020 and last stood near 5.0 million around 1996 -- so either the snapshot is not a 2020
level, or it is a WorldPop total that does not reconcile with the UN's. This script
computes that comparison and writes it into the specification rather than asserting
anything about it, and it is the third statement in that schema found not to describe the
file (the row count and the rainfall unit were the first two).

The anchor matters less than it looks. Changing the reference year multiplies every
population in the file by one constant, so for any model that uses population as a log
offset the choice is absorbed by the intercept and only the shape of the trend survives.
That is why the fork is worth running with an anchor whose level is in doubt, and the
doubt is recorded either way.

Writes, under results/$COMBO/:
  analysis_dataset.csv    the dataset as it leaves this stage
  setup_spec.json         what this stage chose, and what it did to the data
  population_series.csv   the per-province per-year series, so the column that reached
                          the models can be read without re-deriving it
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]

# The national series, and the archive's statement about the snapshot it anchors to.
SERIES = "Archive/lao-population/worldbank_SP.POP.TOTL_LAO_1990-2021.json"
SERIES_SUMS = "Archive/lao-population/sha256sums.txt"
SCHEMA = "Archive/lao-dataset/chap_LAO_admin1_monthly_schema.json"


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")
sys.path.insert(0, str(ROOT / "analysis" / "scripts" / "lib"))
import combos  # noqa: E402

# Which of the two files `01_partition` wrote: the development period, or the whole
# record phase E evaluates on. The suffix on the combination name decides, in one place.
SOURCE = combos.source_dataset(ROOT)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[str, list[str]]:
    """The file as its header line and its data lines, unparsed.

    The dataset is carried through the setup chain as text, for the reason the sibling
    gives: a parser round trip re-formats the file, so a stage that declares the identity
    would produce a file that is not identical. This stage does not declare the identity
    -- it rewrites one column -- but it rewrites only that column's field, leaving every
    other byte of every line where it was, so that the difference between this file and
    the archived one is exactly the change this stage claims to have made.
    """
    text = path.read_text()
    header, _, body = text.partition("\n")
    return header, [line for line in body.split("\n") if line]


def write_table(path: Path, header: str, rows: list[str]) -> None:
    path.write_text(header + "\n" + "".join(line + "\n" for line in rows))


def column(header: str, name: str) -> int:
    return header.split(",").index(name)


def verify_archive() -> None:
    """The archived series is what it was when it was fetched, or this stage stops.

    `01_partition` re-verifies the dengue data against its manifest on every run; a
    population series that reaches the models is an input on the same footing.
    """
    expected = {}
    for line in (ROOT / SERIES_SUMS).read_text().splitlines():
        digest, _, name = line.partition("  ")
        expected[name.strip()] = digest.strip()
    name = Path(SERIES).name
    found = sha256(ROOT / SERIES)
    if expected.get(name) != found:
        raise SystemExit(
            f"{SERIES} does not match {SERIES_SUMS}: expected {expected.get(name)}, "
            f"found {found}. The archive is write-once; refetching it is not a fix.")


def national_series() -> dict[int, int]:
    payload = json.loads((ROOT / SERIES).read_text())
    rows = payload[1]
    series = {int(r["date"]): int(r["value"]) for r in rows if r["value"] is not None}
    if not series:
        raise SystemExit(f"no observations in {SERIES}")
    return series


def anchor_year() -> int:
    """The snapshot's reference year, as the dataset's own schema states it."""
    schema = json.loads((ROOT / SCHEMA).read_text())
    field = next(f for f in schema["fields"] if f["name"] == "population")
    return int(field["source"]["snapshot_ref"])


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    verify_archive()
    national = national_series()
    anchor = anchor_year()
    if anchor not in national:
        raise SystemExit(f"the series has no {anchor}, which the schema names as the "
                         f"snapshot's reference year")

    header, rows = read_table(SOURCE)
    period_at = column(header, "time_period")
    location_at = column(header, "location")
    population_at = column(header, "population")

    snapshot: dict[str, int] = {}
    for line in rows:
        fields = line.split(",")
        snapshot.setdefault(fields[location_at], int(fields[population_at]))

    years = sorted({int(line.split(",")[period_at][:4]) for line in rows})
    missing = [y for y in years if y not in national]
    if missing:
        raise SystemExit(f"the series does not cover {missing}")

    # The scaled column, rounded to whole persons because the source column is an
    # integer count and a fractional person in a covariate is a formatting artefact.
    factor = {y: national[y] / national[anchor] for y in years}
    scaled = []
    for line in rows:
        fields = line.split(",")
        year = int(fields[period_at][:4])
        fields[population_at] = str(round(snapshot[fields[location_at]] * factor[year]))
        scaled.append(",".join(fields))
    write_table(out / "analysis_dataset.csv", header, scaled)

    frame = pd.read_csv(out / "analysis_dataset.csv", dtype={"time_period": str})
    series = (frame.assign(year=frame["time_period"].str[:4].astype(int))
              .groupby(["location", "year"], as_index=False)["population"].first()
              .sort_values(["location", "year"]))
    series["national_total"] = series["year"].map(national)
    series["scale_from_snapshot"] = series["year"].map(factor)
    series["snapshot"] = series["location"].map(snapshot)
    series.to_csv(out / "population_series.csv", index=False)

    snapshot_total = sum(snapshot.values())
    spec = {
        "combo": COMBO,
        "stage": "population",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_backCast",
        "description": "the archived snapshot scaled to each year by the national series",
        "dataset_transform": "population column rewritten; every other field unchanged",
        "input": str(SOURCE.relative_to(ROOT)),
        "input_sha256": sha256(SOURCE),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": len(rows),
        "rows_out": len(scaled),
        "locations": int(frame["location"].nunique()),
        "period_first": str(frame["time_period"].min()),
        "period_last": str(frame["time_period"].max()),
        "series_file": SERIES,
        "series_sha256": sha256(ROOT / SERIES),
        "series_vintage": json.loads((ROOT / SERIES).read_text())[0]["lastupdated"],
        "anchor_year": anchor,
        "anchor_year_source": f"{SCHEMA} -> fields[population].source.snapshot_ref",
        "national_at_anchor": national[anchor],
        "scale_first_year": factor[years[0]],
        "scale_last_year": factor[years[-1]],
        "population_min": int(frame["population"].min()),
        "population_max": int(frame["population"].max()),
        # The check on the anchor. Reported, not acted on: this stage takes the schema
        # at its word and says how far the file is from it.
        "snapshot_total_over_provinces": snapshot_total,
        "national_at_anchor_over_snapshot_total": national[anchor] / snapshot_total,
        "year_whose_national_total_is_nearest_the_snapshot_total": min(
            national, key=lambda y: abs(national[y] - snapshot_total)),
        "provincial_growth_is_uniform_by_construction": True,
        "eval_flags": {},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"population/b_backCast: {len(scaled)} rows, anchor {anchor}, "
          f"scale {factor[years[0]]:.4f}..{factor[years[-1]]:.4f}, "
          f"snapshot total {snapshot_total} vs national {national[anchor]} at anchor "
          f"(nearest year {spec['year_whose_national_total_is_nearest_the_snapshot_total']})")


if __name__ == "__main__":
    main()
