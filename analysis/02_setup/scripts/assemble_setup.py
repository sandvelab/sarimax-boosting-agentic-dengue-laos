"""Assemble the common ground: one dataset and one evaluation setting, for every model.

The four forks above this script each took one decision and handed the dataset on. This
script closes the chain: it reads whichever child of the last fork ran for this
combination, together with all four stage specifications, and writes the single dataset
and the single evaluation setting that every model node -- ours, the baselines and the
external reference -- then reads.

Why one assembled file rather than each model reaching into the last fork's directory:
the models must not need to know how many stages the setup has or which of them are forks.
They read `02_setup/results/$COMBO/analysis_dataset.csv` and the flags beside it, and the
setup can grow a stage without a single model script changing.

The backtest scheme is **not** decided here. `n_periods`, `n_splits` and `stride` were
fixed in batch 3 and written to `01_data/02_characterise/results/backtest_scheme_chosen.json`;
this script reads them from that file and passes them on, so no model script carries them
as a constant of its own and no value crosses a step by hand. `n_retrain` comes from the
fork that decides it.

Writes, under results/$COMBO/:
  analysis_dataset.csv   what every model is evaluated on
  setup_spec.json        the four choices, and the evaluation flags they imply
  setup_inputs.sha256    the bytes each stage read and wrote, in chain order
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import sys

import pandas as pd

NODE = Path(__file__).resolve().parents[1]
STAGES = ("01_population", "02_trainingWindow", "03_provinces", "04_retrain")
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



def chosen_child(fork: str, combo: str) -> Path:
    """The one child of `fork` that ran in this combination."""
    found = sorted((NODE / fork).glob(f"*/results/{combo}/setup_spec.json"))
    if len(found) != 1:
        raise SystemExit(
            f"{fork}: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(NODE)) for p in found]}")
    return found[0].parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    stages = []
    lines = []
    for fork in STAGES:
        results = chosen_child(fork, COMBO)
        spec = json.loads((results / "setup_spec.json").read_text())
        stages.append(spec)
        lines.append(f"{spec['input_sha256']}  {spec['input']}")
        lines.append(f"{spec['output_sha256']}  "
                     f"{(results / 'analysis_dataset.csv').relative_to(ROOT)}")

    # Copied as bytes, not round-tripped through a parser: what every model reads must
    # be the file the chain produced, not a re-formatting of it.
    last = chosen_child(STAGES[-1], COMBO) / "analysis_dataset.csv"
    (out / "analysis_dataset.csv").write_bytes(last.read_bytes())
    frame = pd.read_csv(out / "analysis_dataset.csv", dtype={"time_period": str})

    # Which of the two schemes batch 3 fixed: 3/8/3 over 2008-2009 on development,
    # 3/4/3 over 2010 on the holdout. Both are in the stored file and neither moves; the
    # combination's name decides which one it is evaluated under, in the one place that
    # decision is made.
    scheme = json.loads(combos.scheme_file(ROOT).read_text())
    scheme_key = combos.scheme_key()
    flags = {
        "n_periods": scheme[scheme_key]["n_periods"],
        "n_splits": scheme[scheme_key]["n_splits"],
        "stride": scheme[scheme_key]["stride"],
    }
    for spec in stages:
        flags.update(spec["eval_flags"])

    development = ROOT / combos.SOURCE_BY_DATASET["development"]
    source = combos.source_dataset(ROOT)
    assembled = {
        "combo": COMBO,
        "evaluated_on": combos.dataset(),
        "dataset": "analysis_dataset.csv",
        "source_dataset": str(source.relative_to(ROOT)),
        "identical_to_source_dataset":
            sha256(out / "analysis_dataset.csv") == sha256(source),
        # Kept as it was: it says whether what the models face is the development file,
        # and on a holdout combination the honest answer to that is no.
        "identical_to_development_file":
            sha256(out / "analysis_dataset.csv") == sha256(development),
        "dataset_sha256": sha256(out / "analysis_dataset.csv"),
        "rows": int(len(frame)),
        "locations": int(frame["location"].nunique()),
        "period_first": str(frame["time_period"].min()),
        "period_last": str(frame["time_period"].max()),
        "columns": list(frame.columns),
        "choices": {s["stage"]: s["choice"] for s in stages},
        "choice_nodes": {s["stage"]: s["node"] for s in stages},
        "eval_flags": flags,
        "eval_flags_source": {
            "n_periods": f"{combos.scheme_path()} -> {scheme_key}",
            "n_splits": f"{combos.scheme_path()} -> {scheme_key}",
            "stride": f"{combos.scheme_path()} -> {scheme_key}",
            "n_retrain": next(s["node"] for s in stages if "n_retrain" in s["eval_flags"]),
        },
        "stages": stages,
    }
    (out / "setup_spec.json").write_text(json.dumps(assembled, indent=1, sort_keys=True) + "\n")
    (out / "setup_inputs.sha256").write_text("\n".join(lines) + "\n")

    print(f"setup[{COMBO}] on {assembled['evaluated_on']}: "
          f"{assembled['rows']} rows, {assembled['locations']} locations, "
          f"{assembled['period_first']}..{assembled['period_last']}, "
          f"flags {flags}, choices {assembled['choices']}")


if __name__ == "__main__":
    main()
