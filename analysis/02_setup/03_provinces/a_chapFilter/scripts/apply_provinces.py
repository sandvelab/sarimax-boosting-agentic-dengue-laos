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


def upstream(fork: str, combo: str) -> Path:
    found = sorted((SETUP / fork).glob(f"*/results/{combo}/analysis_dataset.csv"))
    if len(found) != 1:
        raise SystemExit(
            f"{fork}: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(SETUP)) for p in found]}")
    return found[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    source = upstream("02_trainingWindow", COMBO)
    frame = pd.read_csv(source, dtype={"time_period": str})

    frame.to_csv(out / "analysis_dataset.csv", index=False)

    # What the platform's filter and the evaluated span imply, from this dataset.
    scheme = json.loads((ROOT / SCHEME).read_text())
    span_first, span_last = scheme["development_evaluated_span"]
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
        "rows_in": int(len(frame)),
        "rows_out": int(len(frame)),
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
