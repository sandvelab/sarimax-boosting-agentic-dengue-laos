"""Stage 3 of the common setup: which provinces are put in front of the models.

Two provinces are problems. Vientiane (LA-VI) reports no dengue case at any point in the
record, and chap-core's own region filter drops it before evaluation. Xaisomboun (LA-XN)
reports until 2005 and then stops; the filter looks only at the training period, so it
survives the filter and still contributes no evaluable cell. The headline mean is
therefore over 16 provinces and 371 cells, not the 18 provinces in the file.

This child hands the platform every province and lets it decide. That is the choice with
the fewest of our fingerprints on it: the alternative is for us to decide which provinces
are analysable, which is a judgment about data quality made by the party whose score
depends on it. The siblings -- dropping the two silent provinces outright, and merging
Vientiane into the prefecture that geographically contains it -- are the other readings,
and they change what the metric is a mean over, which is why the project's reported
conclusion is a ratio to the reference rather than a raw CRPS.

The transformation is the identity on the data: leaving inclusion to the platform means
passing the file through. What this script contributes is the record of *what the
platform will then do*, computed from the data rather than recalled from batch 3.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves this stage
  setup_spec.json        what this stage chose, and what the region filter implies
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
SETUP = NODE.parents[1]

# The evaluated span, as batch 3 fixed it and 02_setup re-reads from the scheme file.
# Kept here only to say which cells are counted as evaluable in the diagnostic below;
# the value itself comes from that file, never from this script.
SCHEME = "analysis/01_data/02_characterise/results/backtest_scheme_chosen.json"


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

    source = upstream("02_trainingWindow", COMBO)
    header, rows = read_table(source)
    write_table(out / "analysis_dataset.csv", header, rows)
    frame = pd.read_csv(out / "analysis_dataset.csv", dtype={"time_period": str})

    # What the platform's filter and the evaluated span imply, from this dataset.
    scheme = json.loads((ROOT / SCHEME).read_text())
    # The span this combination is evaluated over: 2008-01..2009-12 on development,
    # 2010-01..2010-12 on the holdout. Read from the stored scheme by the key
    # `combos` derives from the combination name, so a holdout row applies this fork's
    # rule to the year it is actually scored on rather than to development's.
    span_first, span_last = scheme[combos.span_key()]
    observed = frame.dropna(subset=["disease_cases"])
    never_reports = sorted(set(frame["location"]) - set(observed["location"]))
    in_span = observed[(observed["time_period"] >= span_first)
                       & (observed["time_period"] <= span_last)]
    silent_in_span = sorted(set(observed["location"]) - set(in_span["location"]))

    spec = {
        "combo": COMBO,
        "stage": "provinces",
        "order": 3,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_chapFilter",
        "description": "every province passed to the platform; inclusion left to its region filter",
        "dataset_transform": "identity",
        "input": str(source.relative_to(ROOT)),
        "input_sha256": sha256(source),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": len(rows),
        "rows_out": len(rows),
        "locations_in_file": int(frame["location"].nunique()),
        "locations_never_reporting": never_reports,
        "locations_with_no_observation_in_evaluated_span": silent_in_span,
        "evaluated_span": [span_first, span_last],
        "expected_locations_contributing": int(in_span["location"].nunique()),
        "expected_evaluable_cells": int(len(in_span)),
        "eval_flags": {},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"provinces/a_chapFilter: {frame['location'].nunique()} provinces in the file, "
          f"{spec['expected_locations_contributing']} expected to contribute "
          f"{spec['expected_evaluable_cells']} cells")


if __name__ == "__main__":
    main()
