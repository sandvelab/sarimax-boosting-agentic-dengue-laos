"""Stage 1 of candidate 2's configuration: the lag block, plus the calendar and the map.

The same lags the sibling takes, and then four things said directly rather than left to be
inferred: the month as two pairs of harmonics, a year index, the province as an identifier,
and rolling means of the province's own recent counts.

**What the fork is actually asking.** A tree can only cut a feature it has been given.
`a_lagBlock` says the twelve-month lag of the count is enough for the model to find the
annual cycle; this child says the cycle should be described to it. Both are things an
analyst would plausibly do and the tree is where they get compared, which is the plan's §3
rule about judgment calls made visible.

**Two of the four additions are expected to hurt, and saying so before the run is the
point.** A province identifier lets the boosters cut one province from the rest, which is
sixteen more ways to fit a training set of about two thousand rows. A year index is worse:
trees cannot extrapolate, so every forecast month falls beyond the last year the fit saw
and lands in whatever leaf the final training year occupies. Neither is a mistake to be
corrected here — they are what "the rich calendar" means, and a fork whose non-main child
was built to lose would tell nobody anything.

**The rolling means end at the third lag**, not at the previous month, so a summary never
contains a month the forecast's own horizon puts out of reach. Three, six and twelve
months: the current season's level, the year's, and a full cycle.

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

# Identical to the sibling's, deliberately: the fork is about what is added on top of the
# lag block, so a difference in the block itself would confound the two questions.
CLIMATE_COLUMNS = ("rainfall", "mean_temperature", "mean_relative_humidity")
CLIMATE_LAGS = (0, 1, 2, 3)
COUNT_LAGS = (3, 4, 5, 6, 12)

# What this child adds. The model implements them under `features = rich_calendar`; the
# names are here so that the specification says what was asked for rather than only which
# switch was thrown.
ADDED = ("month as two harmonic pairs", "a year index", "the province as an identifier",
         "rolling means of the count over 3, 6 and 12 months ending at lag 3")


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

    missing = [c for c in CLIMATE_COLUMNS if c not in frame.columns]
    if missing:
        raise SystemExit(f"the assembled dataset has no column(s) {missing}; this child "
                         f"cannot be taken on combination {COMBO!r}")

    provinces = int(frame["location"].nunique())
    years = sorted({str(p)[:4] for p in frame["time_period"]})

    spec = {
        "combo": COMBO,
        "input_from_combo": dataset_combo,
        "stage": "features",
        "order": 1,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "b_richCalendar",
        "description": ("the lag block, plus " + "; plus ".join(ADDED)),
        "user_option_values": {
            "features": "rich_calendar",
            "climate_columns": list(CLIMATE_COLUMNS),
            "climate_lags": list(CLIMATE_LAGS),
            "count_lags": list(COUNT_LAGS),
        },
        "additional_continuous_covariates": list(CLIMATE_COLUMNS),
        "adds_over_the_sibling": list(ADDED),
        "premise": {
            "rows": int(len(frame)),
            "provinces": provinces,
            "training_years": len(years),
            "first_year": years[0],
            "last_year": years[-1],
            "n_features": (len(CLIMATE_COLUMNS) * len(CLIMATE_LAGS)
                           + len(COUNT_LAGS) + 1 + 4 + 2 + 3),
            "n_features_added_over_the_sibling": 4 + 2 + 3,
        },
        # Registered before the run, so that what the numbers say afterwards can be read
        # against what was expected rather than against a memory of it.
        "expected_cost": {
            "province_identifier": (
                f"{provinces} provinces are {provinces - 1} extra cuts available on a "
                f"training set of about two thousand rows"),
            "year_index": (
                "trees cannot extrapolate, so every forecast month lies beyond "
                f"{years[-1]} and is scored in the leaf the last training year occupies; "
                "the feature can therefore only cost, never help, out of sample"),
        },
    }
    (out / "model_option_spec.json").write_text(
        json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"features/b_richCalendar[{COMBO}]: {spec['premise']['n_features']} features "
          f"({spec['premise']['n_features_added_over_the_sibling']} more than the "
          f"sibling) -> {out}")


if __name__ == "__main__":
    main()
