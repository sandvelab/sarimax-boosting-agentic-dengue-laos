"""Stage 3 of the common setup: only the provinces that can be evaluated are passed on.

Two provinces cannot contribute an evaluable cell. Vientiane province (LA-VI) reports no
dengue case anywhere in the record, and chap-core's own region filter drops it before
evaluation. Xaisomboun (LA-XN) reports until 2005 and then stops; the filter looks only
at the training period, so it survives and still contributes nothing to the metric.

The sibling hands the platform every province and lets it decide, which is the choice
with the fewest of our fingerprints on it. This child removes them here instead, and the
difference is not cosmetic: a province dropped by the region filter is still in the file
the models train on, so a hierarchical model has been pooling across a province of
structural zeros and a boosted model has been fitting trees to it. Removing them before
the platform sees them changes what every model learns from, while leaving the 371
evaluated cells exactly as they were.

**Which provinces go is derived, not listed.** The two are found by the same computation
the sibling reports -- never reports in the record, or reports nothing inside the
evaluated span read from the stored scheme -- so a province that went silent for some
other reason would be caught by the rule rather than missed by a hard-coded pair. What is
fixed in advance is the *rule*, and it is stated in the specification this writes.

Writes, under results/$COMBO/:
  analysis_dataset.csv   the dataset as it leaves this stage
  setup_spec.json        what this stage chose, which provinces went, and on what rule
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


def column(header: str, name: str) -> int:
    return header.split(",").index(name)


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    source = upstream("02_trainingWindow", COMBO)
    header, rows = read_table(source)

    # The rule, applied to this dataset and this stored span.
    incoming = pd.read_csv(source, dtype={"time_period": str})
    scheme = json.loads(combos.scheme_file(ROOT).read_text())
    # The span this combination is evaluated over: 2008-01..2009-12 on development,
    # 2010-01..2010-12 on the holdout. Read from the stored scheme by the key
    # `combos` derives from the combination name, so a holdout row applies this fork's
    # rule to the year it is actually scored on rather than to development's.
    span_first, span_last = scheme[combos.span_key()]
    observed = incoming.dropna(subset=["disease_cases"])
    in_span = observed[(observed["time_period"] >= span_first)
                       & (observed["time_period"] <= span_last)]
    keep = set(in_span["location"])
    removed = sorted(set(incoming["location"]) - keep)

    location = column(header, "location")
    kept_rows = [line for line in rows if line.split(",")[location] in keep]
    write_table(out / "analysis_dataset.csv", header, kept_rows)
    frame = pd.read_csv(out / "analysis_dataset.csv", dtype={"time_period": str})

    spec = {
        "combo": COMBO,
        "stage": "provinces",
        "order": 3,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_reportingOnly",
        "description": "provinces with no evaluable cell removed before the platform sees them",
        "dataset_transform": "rows of the removed provinces dropped; every kept row unchanged",
        "removal_rule": "a province is removed when it carries no non-missing "
                        "disease_cases inside the evaluated span read from the stored "
                        "backtest scheme",
        "input": str(source.relative_to(ROOT)),
        "input_sha256": sha256(source),
        "output_sha256": sha256(out / "analysis_dataset.csv"),
        "rows_in": len(rows),
        "rows_out": len(kept_rows),
        "locations_in_file": int(frame["location"].nunique()),
        "locations_removed": removed,
        "locations_never_reporting": sorted(set(incoming["location"])
                                            - set(observed["location"])),
        "evaluated_span": [span_first, span_last],
        "expected_locations_contributing": int(in_span["location"].nunique()),
        "expected_evaluable_cells": int(len(in_span)),
        "eval_flags": {},
    }
    (out / "setup_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"provinces/b_reportingOnly: removed {removed}; "
          f"{frame['location'].nunique()} provinces, {len(kept_rows)} rows, "
          f"{spec['expected_evaluable_cells']} cells expected")


if __name__ == "__main__":
    main()
