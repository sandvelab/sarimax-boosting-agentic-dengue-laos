"""Stage 5 of the candidate's configuration: whether the recent case history enters.

**It does not.** The forecast for a province-month is built from the calendar, the
climate, the province's own level and its annual effect, and nothing about how the
current epidemic is going.

This is the main path, and it is the main path because it is what the model was when
batch 8 scored it -- not because it is the better answer. Batch 8 declined to add an
autoregressive term inside the four forks it had, on the grounds that a structural
term added outside the forks would be exactly the silent judgment call this project
exists to make visible; this node is that call made visible, and `b_lag3` is the term
it declined to add.

There is a reason to expect the sibling to win. Batch 7 found the persistence baseline
level with the reference model at one month's lead, which says there is information in
the last observed count that neither the reference nor our candidate uses. There is
also a reason to expect it not to: at three months' lead persistence loses badly, and
a term that has to serve all three horizons is a lag of three months for every one of
them. The premise below is the evidence that bears on it, computed rather than
argued.

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

    import numpy as np

    observed = frame.dropna(subset=["disease_cases"]).copy()
    # The file writes periods as YYYY-MM; the index below has to be arithmetic, so that
    # "three months earlier" is subtraction rather than string manipulation.
    compact = observed["time_period"].str.replace("-", "", regex=False)
    observed["_m"] = (compact.str[:4].astype(int) * 12
                      + compact.str[4:6].astype(int) - 1)
    observed = observed.sort_values(["location", "_m"])

    # Matched on (province, month index) rather than by row position, so a gap in a
    # province's record cannot pair a month with the wrong predecessor.
    earlier = dict(zip(zip(observed["location"], observed["_m"], strict=True),
                       observed["disease_cases"], strict=True))
    correlations, pairs = {}, {}
    for lag in (1, 2, 3, 12):
        now, before = [], []
        for location, m, value in zip(observed["location"], observed["_m"],
                                      observed["disease_cases"], strict=True):
            previous = earlier.get((location, m - lag))
            if previous is not None:
                now.append(value)
                before.append(previous)
        pairs[f"lag_{lag}"] = len(now)
        correlations[f"lag_{lag}"] = float(
            np.corrcoef(np.log1p(now), np.log1p(before))[0, 1])

    premise = {
        "observed_cells": int(len(observed)),
        # On log1p, within province. The comparison that matters is lag 3 against lag
        # 12: a lagged count that only tells the model what month of the year it is
        # tells it nothing the seasonal harmonics do not already say.
        "autocorrelation_of_log1p_cases": correlations,
        "pairs_available": pairs,
    }

    spec = {
        "combo": COMBO,
        # Which combination the input came from. Equal to `combo` on the main
        # path; a candidate-internal combination inherits the setup it did not
        # move, and inheriting silently is what this line exists to prevent.
        "input_from_combo": input_combo,
        "stage": "autoregressive",
        "order": 5,
        "node": str(NODE.relative_to(ROOT)),
        "choice": "a_none",
        "description": "no autoregressive term; season, climate and pooled effects only",
        "user_option_values": {"autoregressive": "none"},
        "additional_continuous_covariates": [],
        "premise": premise,
    }
    (out / "model_option_spec.json").write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n")

    print(f"autoregressive/a_none[{COMBO}]: no lagged-count term; the correlation it "
          f"leaves unused at lag 3 is "
          f"{premise['autocorrelation_of_log1p_cases']['lag_3']:.3f} -> {out}")



if __name__ == "__main__":
    main()
