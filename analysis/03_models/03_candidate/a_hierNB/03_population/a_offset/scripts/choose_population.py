"""Stage 3 of the candidate's configuration: how population enters the model.

As a fixed offset, `log(population)`. The linear predictor becomes an incidence rate on
the log scale and the province's size multiplies it back up, so the fit never spends a
parameter learning how large a province is -- which matters here, where the provinces
differ in population by a factor of twenty-four and in reported burden by four orders of
magnitude.

An offset is a coefficient fixed at one rather than estimated, and that is the assumption:
that reported cases scale proportionally with population. The siblings are where it is
relaxed -- `b_covariate` estimates the coefficient instead, and `c_ignored` drops
population entirely so that a province's level is carried only by its own pooled
intercept.

The choice is not free of the setup. `02_setup/01_population` decides what the column
*contains* -- the archive's constant, or a back-cast per-year series -- and that fork
re-scores every model including the reference. This one decides what our model does with
whatever it was handed, and moves only ours. The two were one entry on batch 3's list and
are two nodes here for that reason.

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

    dataset, dataset_combo = resolve(
        ROOT / "analysis/02_setup/results", "analysis_dataset.csv")
    frame = pd.read_csv(dataset, dtype={"time_period": str})

    # log(population) is only defined where population is positive, and an offset that is
    # undefined for one province is a model that cannot be fitted. Checked, not assumed.
    nonpositive = sorted(frame.loc[frame["population"] <= 0, "location"].unique())
    if nonpositive:
        raise SystemExit(f"population is not positive for {nonpositive}; a log offset is "
                         f"undefined and this child cannot be taken on {COMBO!r}")

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": dataset_combo,
        "stage": "population",
        "order": 3,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_offset",
        "description": "log(population) as a fixed offset; the model forecasts a rate",
        "user_option_values": {"population": "offset"},
        "additional_continuous_covariates": [],
        "premise": {
            "population_min": int(frame["population"].min()),
            "population_max": int(frame["population"].max()),
            "population_ratio_largest_to_smallest":
                float(frame["population"].max() / frame["population"].min()),
            "provinces_with_nonpositive_population": nonpositive,
        },
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"population/a_offset[{COMBO}]: log(population) offset; largest/smallest "
          f"{spec['premise']['population_ratio_largest_to_smallest']:.1f} -> {out}")


if __name__ == "__main__":
    main()
