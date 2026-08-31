"""Stage 1 of the common setup: the population column, taken as the archive supplies it.

The source file carries one population figure per province for the whole 1998-2010
record. It is a 2020 snapshot, so it is wrong by a decade of growth at the start of the
period and by a decade of decline in nothing at all -- population rose throughout. Any
model that uses population as an offset is therefore working with a denominator that is
too large early and about right late, and the same is true for the reference.

This child takes the column unchanged. That is the honest reading of "what the dataset
says", and it is what every published run of this dataset has used; the sibling that
back-casts a per-year series from a published growth rate is the alternative, and the
stability run is where the difference is measured rather than argued.

The transformation is the identity on the data. What this script contributes is the
**check** that the column really is constant per province, which the description above
assumes and which nothing had verified.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves this stage
  setup_spec.json        what this stage chose, and what it did to the data
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]


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

    The dataset is carried through the setup chain as text. Batch 3 made the same choice
    for the partition and for the same reason: a parser round trip re-formats the file --
    an integer count in a column that also holds blanks comes back as `0.0` -- so a stage
    that declares the identity would produce a file that is not identical. Filtering rows
    is a predicate on lines; the columns filtered on are codes and periods with no commas
    in them. Everything the specification reports is computed with pandas from the same
    file, which is a read and changes nothing.
    """
    text = path.read_text()
    header, _, body = text.partition("\n")
    return header, [line for line in body.split("\n") if line]


def write_table(path: Path, header: str, rows: list[str]) -> None:
    path.write_text(header + "\n" + "".join(line + "\n" for line in rows))


def column(header: str, name: str) -> int:
    return header.split(",").index(name)


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    header, rows = read_table(SOURCE)
    write_table(out / "analysis_dataset.csv", header, rows)

    # The property the choice rests on, checked rather than assumed.
    frame = pd.read_csv(SOURCE, dtype={"time_period": str})
    per_province = frame.groupby("location")["population"].nunique()
    varying = sorted(per_province[per_province > 1].index)

    spec = {
        "combo": COMBO,
        "stage": "population",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_static",
        "description": "the archived population column, one constant per province",
        "dataset_transform": "identity",
        "input": str(SOURCE.relative_to(ROOT)),
        "input_sha256": sha256(SOURCE),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": len(rows),
        "rows_out": len(rows),
        "locations": int(frame["location"].nunique()),
        "period_first": str(frame["time_period"].min()),
        "period_last": str(frame["time_period"].max()),
        "population_constant_per_province": not varying,
        "provinces_with_varying_population": varying,
        "population_min": int(frame["population"].min()),
        "population_max": int(frame["population"].max()),
        "eval_flags": {},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"population/a_static: {len(rows)} rows, constant per province "
          f"{spec['population_constant_per_province']} -> {out}")


if __name__ == "__main__":
    main()
