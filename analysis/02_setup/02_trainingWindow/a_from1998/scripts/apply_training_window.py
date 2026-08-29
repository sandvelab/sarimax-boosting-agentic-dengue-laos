"""Stage 2 of the common setup: how much of the record models may learn from.

The share of province-months reporting zero dengue cases falls monotonically across the
development period, which is either a real decline in transmission or a reporting system
coming into service -- the data cannot tell those apart. If it is the second, the early
years describe a different measurement process and every model is being asked to learn
from two regimes at once.

This child keeps the whole development period. It is the alternative that assumes least:
discarding years is a claim that they are uninformative, and nothing in the data
establishes that. The sibling that starts at 2004, the calendar midpoint of the
period, is the other reading.

What the fork does **not** change is what gets evaluated. chap-core lays its splits out
backwards from the last period of the file, so truncating the early years leaves the
evaluated cells identical and changes only the record models learn from -- which is what
makes this a clean fork rather than two different analyses.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves this stage
  setup_spec.json        what this stage chose, and what it did to the data
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
FORK_PARENT = NODE.parent          # 02_trainingWindow
SETUP = FORK_PARENT.parent         # 02_setup

# This stage keeps everything from here on. `None` means "no lower bound".
FIRST_PERIOD: str | None = None


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")


def upstream(fork: str, combo: str) -> Path:
    """The dataset the previous fork produced for this combination.

    Exactly one child of a fork runs in any one combination, so exactly one of them has
    results under this combination id. Resolving by search rather than by name is what
    lets the stability driver swap a child without any downstream script changing.
    """
    found = sorted((SETUP / fork).glob(f"*/results/{combo}/analysis_dataset.csv"))
    if len(found) != 1:
        raise SystemExit(
            f"{fork}: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(SETUP)) for p in found]}")
    return found[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[str, list[str]]:
    """The file as its header line and its data lines, unparsed.

    The dataset is carried through the setup chain as text. Batch 3 made the same choice
    for the partition and for the same reason: a parser round trip re-formats the file --
    an integer count in a column that also holds blanks comes back as `0.0` -- so a stage
    that declares the identity would produce a file that is not identical. Filtering rows
    is a predicate on lines; the columns filtered on are codes and periods with no commas
    in them.
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

    source = upstream("01_population", COMBO)
    header, rows = read_table(source)
    rows_in = len(rows)

    if FIRST_PERIOD is not None:
        period = column(header, "time_period")
        rows = [line for line in rows if line.split(",")[period] >= FIRST_PERIOD]

    write_table(out / "analysis_dataset.csv", header, rows)
    frame = pd.read_csv(out / "analysis_dataset.csv", dtype={"time_period": str})

    spec = {
        "combo": COMBO,
        "stage": "trainingWindow",
        "order": 2,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_from1998",
        "description": "the whole development period; no year discarded",
        "dataset_transform": "identity",
        "first_period_kept": FIRST_PERIOD or "(all)",
        "input": str(source.relative_to(ROOT)),
        "input_sha256": sha256(source),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": rows_in,
        "rows_out": len(rows),
        "locations": int(frame["location"].nunique()),
        "period_first": str(frame["time_period"].min()),
        "period_last": str(frame["time_period"].max()),
        "eval_flags": {},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"trainingWindow/a_from1998: {rows_in} -> {len(rows)} rows "
          f"({spec['period_first']}..{spec['period_last']})")


if __name__ == "__main__":
    main()
