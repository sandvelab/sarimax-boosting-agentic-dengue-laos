"""Stage 2 of the common setup: only the second half of the record reaches the models.

The share of province-months reporting zero dengue cases falls monotonically across the
development period. Either transmission declined or a reporting system came into
service, and the data cannot tell those apart. The sibling keeps everything, on the
ground that discarding years is a claim they are uninformative. This child takes the
other reading: if the early years are a different measurement process, a model that
learns from them is learning a regime the evaluated window no longer belongs to.

**Where the cut falls, and why not somewhere better.** 2004-01 is the calendar midpoint
of 1998-01 to 2009-12. It is deliberately *not* chosen by the zero rate, even though the
zero rate is the reason the fork exists: a threshold fitted to the quantity the fork
means to probe would let the alternative be tuned, and a perturbation that can be tuned
measures the tuner rather than the analysis. The midpoint is arbitrary in the one way
that matters -- it was fixed before this ran, by a rule anybody can restate.

**What the fork does not change is what gets evaluated.** chap-core lays its splits out
backwards from the last period of the file, so truncating the early years leaves the
371 evaluated cells identical and moves only the record models learn from. That is what
makes the two children directly comparable, and it is checked here: the periods this
stage removes are all earlier than the evaluated span, read from the stored scheme.

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
FORK_PARENT = NODE.parent          # 02_trainingWindow
SETUP = FORK_PARENT.parent         # 02_setup

# The calendar midpoint of the development period. `None` would mean "no lower bound".
FIRST_PERIOD: str | None = "2004-01"
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
    """The file as its header line and its data lines, unparsed. See the sibling."""
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

    period = column(header, "time_period")
    dropped = [line for line in rows if line.split(",")[period] < FIRST_PERIOD]
    rows = [line for line in rows if line.split(",")[period] >= FIRST_PERIOD]

    write_table(out / "analysis_dataset.csv", header, rows)
    frame = pd.read_csv(out / "analysis_dataset.csv", dtype={"time_period": str})

    # The property that makes the two children comparable, checked rather than argued.
    scheme = json.loads(combos.scheme_file(ROOT).read_text())
    # The span this combination is evaluated over: 2008-01..2009-12 on development,
    # 2010-01..2010-12 on the holdout. Read from the stored scheme by the key
    # `combos` derives from the combination name, so a holdout row applies this fork's
    # rule to the year it is actually scored on rather than to development's.
    span_first, span_last = scheme[combos.span_key()]
    latest_dropped = max((line.split(",")[period] for line in dropped), default=None)

    spec = {
        "combo": COMBO,
        "stage": "trainingWindow",
        "order": 2,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_from2004",
        "description": "the second half of the development period; 1998-01 to 2003-12 dropped",
        "dataset_transform": "rows before the cut removed; every kept row unchanged",
        "first_period_kept": FIRST_PERIOD,
        "cut_rule": "the calendar midpoint of the development period, fixed before the "
                    "run and not chosen by the zero rate the fork exists to probe",
        "input": str(source.relative_to(ROOT)),
        "input_sha256": sha256(source),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": rows_in,
        "rows_out": len(rows),
        "rows_dropped": len(dropped),
        "latest_period_dropped": latest_dropped,
        "evaluated_span": [span_first, span_last],
        "evaluated_span_untouched": bool(latest_dropped is None
                                         or latest_dropped < span_first),
        "locations": int(frame["location"].nunique()),
        "period_first": str(frame["time_period"].min()),
        "period_last": str(frame["time_period"].max()),
        "eval_flags": {},
    }
    if not spec["evaluated_span_untouched"]:
        raise SystemExit(
            f"the cut at {FIRST_PERIOD} removes periods inside the evaluated span "
            f"{span_first}..{span_last}; the two children of this fork would then be "
            f"scored on different cells and would not be comparable")
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"trainingWindow/b_from2004: {rows_in} -> {len(rows)} rows "
          f"({spec['period_first']}..{spec['period_last']}), "
          f"{len(dropped)} dropped, latest dropped {latest_dropped}")


if __name__ == "__main__":
    main()
