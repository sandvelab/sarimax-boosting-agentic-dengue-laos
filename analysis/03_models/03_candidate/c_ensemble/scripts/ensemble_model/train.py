"""Fit the ensemble candidate: fit its members, and settle the weights.

What "fitting" means here is two things that are worth keeping apart:

1. **Every member is fitted on the frame Chap handed us**, through its own `train` entry
   point, and its fitted object is embedded in ours. After this the pool carries its
   members whole, so `predict` needs no file but the one chap-core passes it.
2. **The weights are settled.** Under `equal` there is nothing to settle. Under
   `min_crps` the last few forecast blocks of the training frame are held back, every
   member is **refitted without them**, each member forecasts them through its own
   `predict`, and the weights that minimise the pool's CRPS over those cells are computed
   exactly from the sample-based CRPS identity.

**The validation fits are thrown away.** They exist to score the members on months they
did not see; the members that go into the pool are the ones fitted on the whole frame.
Using the validation fits for the forecast would hand the pool a model trained on less
data than every other model on the leaderboard.

**Nothing here sees the evaluated period.** The frame this script is given is whatever
chap-core's splitter says the training data is, and the hold-back is taken from the end of
*that*. The weights are therefore fitted on data the members were going to be fitted on
anyway, which is the only way an estimated weight can be honest in a backtest.

Seeds: this script draws nothing of its own. The validation forecasts are draws, and they
come from each member's own generator through the member's own entry point; the weight fit
on top of them is a deterministic solve. The pool's own component seed is recorded in the
fitted object under `seed`, where `predict.py` and the node's record can both find it, and
it is spent there rather than here.

Usage:  python train.py <train_data.csv> <model_out.json> <model_config.yaml>
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from ensemble import (N_SAMPLES, crps_terms, min_crps_weights, pooled_crps,
                      predict_members, read_members, read_options, stacked,
                      train_members)

# The forecast block length. The same three months the backtest asks for, so a validation
# block is the same shape of problem as an evaluated block.
BLOCK = 3

# A member needs at least this many months to be refitted on for a validation fit to mean
# anything. Below it the hold-back is skipped and the weights fall back to equal, with the
# fallback recorded in the fitted object rather than left as a silently different model.
MIN_TRAINING_MONTHS = 60


def month_index(period: str) -> int:
    text = str(period)
    year, month = int(text[:4]), int(text[5:7]) if "-" in text else int(text[4:6])
    return year * 12 + (month - 1)


def fit_weights(members: list[dict], frame: pd.DataFrame, options: dict,
                work: Path) -> dict:
    """The minimum-CRPS weights, from a validation period held back inside the frame."""
    names = [m["name"] for m in members]
    periods = sorted(frame["time_period"].unique(), key=month_index)
    held = options["validation_blocks"] * BLOCK

    if len(periods) - held < MIN_TRAINING_MONTHS:
        return {"method": "equal",
                "weights": [1.0 / len(names)] * len(names),
                "fell_back": True,
                "fell_back_because": (
                    f"holding back {held} months would leave "
                    f"{len(periods) - held} to refit the members on, below the "
                    f"{MIN_TRAINING_MONTHS} this model requires"),
                "members": names}

    validation_periods = periods[-held:]
    reduced = frame[frame["time_period"].isin(periods[:-held])]
    fitted = train_members(members, reduced, work / "validation_fit")

    blocks, observed_blocks = [], []
    for start in range(0, held, BLOCK):
        block_periods = validation_periods[start:start + BLOCK]
        historic = frame[frame["time_period"].isin(
            periods[:len(periods) - held + start])]
        future = frame[frame["time_period"].isin(block_periods)].drop(
            columns=["disease_cases"])
        forecasts = predict_members(members, fitted, historic, future,
                                    work / f"validation_block_{start // BLOCK}")
        block, index = stacked(forecasts, names)

        truth = (frame.set_index(["location", "time_period"])
                 .loc[index, "disease_cases"].to_numpy(float))
        keep = np.isfinite(truth)
        blocks.append(block[:, keep, :options["weight_samples"]])
        observed_blocks.append(truth[keep])

    block = np.concatenate(blocks, axis=1)
    observed = np.concatenate(observed_blocks)
    A, B = crps_terms(block, observed)
    solved = min_crps_weights(A, B)

    return {
        "method": "min_crps",
        "weights": solved["weights"],
        "members": names,
        "fell_back": False,
        "validation": {
            "periods": validation_periods,
            "blocks": options["validation_blocks"],
            "block_months": BLOCK,
            "cells_scored": int(len(observed)),
            "draws_per_member_per_cell": int(block.shape[2]),
            "members_refitted_on_months": len(periods) - held,
            "member_mean_absolute_distance_to_outcome": dict(zip(names, A.tolist())),
            "member_pairwise_mean_absolute_distance": {
                names[m]: dict(zip(names, B[m].tolist())) for m in range(len(names))},
            "member_own_crps": dict(zip(
                names, [float(A[m] - 0.5 * B[m, m]) for m in range(len(names))])),
            "pooled_crps_at_equal_weights": pooled_crps(
                np.full(len(names), 1.0 / len(names)), A, B),
            "pooled_crps_at_fitted_weights": pooled_crps(
                np.asarray(solved["weights"]), A, B),
        },
        "solve": solved,
    }


def main(train_data_path: str, model_path: str, config_path: str) -> dict:
    options = read_options(config_path)
    members = read_members(options)
    frame = pd.read_csv(train_data_path, dtype={"time_period": str})
    names = [m["name"] for m in members]

    work = Path(tempfile.mkdtemp(prefix="ensemble_train_"))
    try:
        if options["weighting"] == "equal":
            weighting = {"method": "equal", "members": names, "fell_back": False,
                         "weights": [1.0 / len(names)] * len(names)}
        else:
            weighting = fit_weights(members, frame, options, work)

        fitted = train_members(members, frame, work / "fit")
    finally:
        shutil.rmtree(work, ignore_errors=True)

    observed = pd.to_numeric(frame["disease_cases"], errors="coerce")
    model = {
        "model": "ensemble_candidate",
        "fitted_in": "train",
        "options": options,
        # The pool's own component seed, recorded here as well as inside `options`, so the
        # fitted object states on its face which stream every draw in `predict` came from.
        "seed": options["seed"],
        "members": [
            {k: v for k, v in member.items() if k != "entry_points"} | {
                "entry_points": member["entry_points"],
                "weight": weight,
            }
            for member, weight in zip(members, weighting["weights"], strict=True)],
        "weighting": weighting,
        "n_samples": N_SAMPLES,
        "training": {
            "rows": int(len(frame)),
            "provinces": int(frame["location"].nunique()),
            "first_period": str(min(frame["time_period"], key=month_index)),
            "last_period": str(max(frame["time_period"], key=month_index)),
            "observed_target_cells": int(observed.notna().sum()),
        },
        "member_models": fitted,
    }
    Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))

    shown = ", ".join(f"{n} {w:.3f}" for n, w in zip(names, weighting["weights"]))
    print(
        f"ensemble_candidate ({options['weighting']}) fitted {len(members)} members on "
        f"{model['training']['rows']} rows "
        f"({model['training']['first_period']}..{model['training']['last_period']}); "
        f"weights {shown}"
        + (f"; fell back to equal: {weighting['fell_back_because']}"
           if weighting.get("fell_back") else "")
        + f" -> {model_path}"
    )
    return model


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
