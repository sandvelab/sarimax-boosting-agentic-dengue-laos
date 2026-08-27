"""Stage 3 of the candidate's configuration: how population enters the model.

**Not at all.** No offset and no covariate: a province's level is carried entirely by
its own pooled intercept, estimated from its record rather than from its size.

The position is that the population column is the weakest thing in this dataset. It is
a single figure per province, constant across thirteen years, and batch 3 recorded
that it is a 2020 snapshot -- so using it as a denominator projects one year's
demography onto the whole record. A pooled province intercept estimates the same thing
the offset was standing in for, from the data the model is actually fitted on, at the
cost of one parameter per province and of any ability to say anything about a province
with no record.

What is given up: the model can no longer be read as forecasting a rate, and it has
nothing to say about a province it has never seen -- the offset would at least have
given such a province the country's average incidence times its own size. Neither
matters for this backtest, where every evaluated province is in the training period,
and both would matter for a model deployed somewhere new.

Writes, under results/$COMBO/:
  model_option_spec.json   the choice, its option values, and the premise it rests on
"""

from __future__ import annotations

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
from combos import resolve  # noqa: E402


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    dataset, input_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})

    by_province = frame.groupby("location")["population"].first()

    premise = {
        "provinces": int(len(by_province)),
        "population_min": int(by_province.min()),
        "population_max": int(by_province.max()),
        "population_ratio_largest_to_smallest": float(by_province.max() / by_province.min()),
        # The column is constant per province, which is why an intercept can stand in
        # for it exactly rather than approximately.
        "population_is_constant_within_province": bool(
            frame.groupby("location")["population"].nunique().max() == 1),
        "distinct_population_values": int(frame["population"].nunique()),
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "population",
        "order": 3,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "c_ignored",
        "description": "population does not enter; the pooled province intercept carries the level",
        "user_option_values": {"population": "ignored"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"population/c_ignored[{COMBO}]: population dropped; it is constant within a "
          f"province ({premise['population_is_constant_within_province']}), so a pooled "
          f"intercept stands in for it exactly -> {out}")



if __name__ == "__main__":
    main()
