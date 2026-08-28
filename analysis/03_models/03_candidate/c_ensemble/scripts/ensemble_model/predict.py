"""Forecast with the ensemble candidate: ask every member, then draw from the pool.

Chap hands this entry point the expanding historic frame and the three months of future
covariates it wants forecast. Both are passed on to every member unchanged, through the
member's own `predict` entry point, so each member sees exactly the frames it would see
if it were being evaluated on its own. That is the property the whole node rests on: the
pool's members are not approximations of the models on the leaderboard, they are those
models, run.

**The members are not refitted here.** They were fitted once, in `train`, and are carried
inside the fitted object this script is handed. A member that refits inside its own
`predict` -- candidate 1 has a fork that does -- still does so, because it is its own code
that runs.

## Where the forecast distribution comes from

The pool's 1 000 draws are allocated across the members by the largest-remainder rule at
the fitted weights, and drawn from each member's own 1 000 without replacement. So the
pool contains no distributional assumption of its own at all: every draw in it was drawn
by one of the members, and the only thing this model contributes is how many draws each
member gets. A pool built by averaging the members' quantiles would have been the other
construction, and it is a different model -- it narrows where the members disagree, where
a linear pool widens. This is the linear pool, and the widening is the point.

**Cells are the ones every member returned.** If a member drops a cell -- a province it
never saw, a period it cannot lag into -- the pool drops it too, rather than quietly
becoming a pool of a different membership in that cell. How many cells that cost is
printed and, when it is not zero, is a fact about the members rather than about the pool.

Seeds: one NumPy generator, seeded with the `seed` option the assembling node derived from
the project seed. It draws in a fixed order over cells sorted by location and period, so
two runs of the same split produce identical pools. The members' own draws come from the
members' own seeds, through their own entry points; this model does not reach into them.

Usage:  python predict.py <model.json> <historic.csv> <future.csv> <out.csv> <config.yaml>
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from ensemble import N_SAMPLES, pool, predict_members, read_options, stacked


def main(model_path: str, historic_path: str, future_path: str, out_path: str,
         config_path: str) -> pd.DataFrame:
    options = read_options(config_path)
    model = json.loads(Path(model_path).read_text())
    historic = pd.read_csv(historic_path, dtype={"time_period": str})
    future = pd.read_csv(future_path, dtype={"time_period": str})

    if model["options"] != options:
        raise SystemExit("the configuration handed to predict is not the one the model "
                         "was fitted under; refusing to forecast")

    members = model["members"]
    names = [m["name"] for m in members]
    weights = np.asarray([m["weight"] for m in members], dtype=float)

    work = Path(tempfile.mkdtemp(prefix="ensemble_predict_"))
    try:
        forecasts = predict_members(members, model["member_models"], historic, future,
                                    work)
        block, index = stacked(forecasts, names)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    rng = np.random.default_rng(options["seed"])
    draws = pool(block, weights, rng, N_SAMPLES)

    out = pd.DataFrame([
        {"time_period": period, "location": location}
        | {f"sample_{i}": int(round(v)) for i, v in enumerate(draws[position])}
        for position, (location, period) in enumerate(index)
    ])
    out.to_csv(out_path, index=False)

    asked = len(future.drop_duplicates(["location", "time_period"]))
    print(
        f"ensemble_candidate ({model['weighting']['method']}, {len(members)} members) "
        f"wrote {len(out)} cells x {N_SAMPLES} draws -> {out_path}"
        + (f"; {asked - len(out)} of {asked} cell(s) dropped because not every member "
           f"returned them" if asked != len(out) else "")
    )
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
