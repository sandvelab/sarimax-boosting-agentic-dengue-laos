"""Fit the gradient-boosted candidate on the training frame.

Everything about what the model is and how it is fitted is in `boosted.py`; this script is
the entry point Chap calls, and its job is to read the three files it is given, run the fit
once, and write the fitted object where `predict.py` will find it.

**The fit happens here and only here.** Candidate 1 has a fork asking whether it fits in
`train` or inside `predict`; this candidate does not, and the reason is in the node's
claim: with the ladder head the fit is fifteen boosters and two passes over the data for
the stopping rule, so refitting inside every `predict` call would multiply the backtest's
cost by the number of splits to answer a question the sibling family has already answered
on a cheaper model. It is a decision with a cost rather than an oversight, and batch 21's
finding — that refitting inside `predict` is the configuration under which a model has no
stored fitted object at all — is a reason to prefer fitting here in any case.

The fitted object is JSON: the boosters are written out as trees with their split
features, thresholds, missing-value directions and leaf values, so what was fitted can be
read without scikit-learn and without unpickling anything (`AGENTS.md` Rule 5). Before it
is written, `fit_model` evaluates the stored form against scikit-learn's own prediction on
the training rows and fails if they differ.

Seeds: the boosters take the configured seed as their `random_state`. With early stopping
disabled and no subsampling nothing in the fit is random, so two fits on the same frame
give the same file either way. All the model's randomness is in `predict.py`.

Usage:  python train.py <train_data.csv> <model_out.json> <model_config.yaml>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from boosted import fit_model, read_options


def main(train_data_path: str, model_path: str, config_path: str) -> dict:
    options = read_options(config_path)
    frame = pd.read_csv(train_data_path, dtype={"time_period": str})

    model = fit_model(frame, options)
    model["fitted_in"] = "train"
    Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))

    training, fit = model["training"], model["fit"]
    print(
        f"boosted_candidate ({model['head']}, {model['features']}) fitted on "
        f"{training['rows_used']} rows "
        f"({training['first_period']}..{training['last_period']}), "
        f"{training['provinces']} provinces, "
        f"{len(model['feature_names'])} features; "
        f"{fit['boosters']} booster(s), rounds {fit['rounds']} of {fit['rounds_cap']}, "
        f"{fit['trees']} trees / {fit['nodes']} nodes; "
        f"stored form agrees to {fit['stored_form_max_abs_difference']:.2g} "
        f"-> {model_path}"
    )
    return model


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
