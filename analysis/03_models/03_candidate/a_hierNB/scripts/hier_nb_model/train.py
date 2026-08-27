"""Fit the hierarchical negative-binomial candidate on the training frame.

Everything about what the model is and how it is fitted is in `hier_nb.py`; this script
is the entry point Chap calls, and its job is to read the three files it is given, run the
fit once, and write the fitted object where `predict.py` will find it.

**Whether the fit happens here at all is a fork.** Under `fit_time = train` -- the main
path, taken by `04_fitTime/a_trainOnly` -- the model is fitted once on the frame Chap
hands this entry point, and `predict` applies the stored fit and ignores the expanding
historic window it is given at every split. Under `fit_time = predict`, taken by the
sibling `b_refitAtPredict`, the fit is deferred: this script writes the configuration and
the training period it saw, and `predict` fits on the history it is handed. The file
written here says which of the two happened, so a fitted object can never be mistaken for
a stub or the other way round.

The fitted object is JSON, not a pickle: it outlives the session (`AGENTS.md` Rule 5), and
it is the only place the fitted variance components and the posterior covariance the
forecasts are drawn from are recorded.

Seeds: none here. Nothing in the fit is random -- it is Fisher scoring from a fixed start
plus deterministic one-dimensional searches -- so two fits on the same frame give the same
file. All the model's randomness is in `predict.py`, seeded from the `seed` option that
the node above derived from the project seed.

Usage:  python train.py <train_data.csv> <model_out.json> <model_config.yaml>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from hier_nb import fit_model, read_options


def main(train_data_path: str, model_path: str, config_path: str) -> dict:
    options = read_options(config_path)
    frame = pd.read_csv(train_data_path, dtype={"time_period": str})

    if options["fit_time"] == "predict":
        # Nothing is fitted here, and the file says so rather than being an empty fit
        # that predict would have no way to tell from a real one.
        model = {
            "model": "hier_nb_candidate",
            "construction": "not fitted here: fit_time = predict",
            "fitted_in": "predict",
            "options": options,
            "training": {
                "rows": int(len(frame)),
                "first_period": str(frame["time_period"].min()),
                "last_period": str(frame["time_period"].max()),
            },
        }
        Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))
        print(f"hier_nb_candidate: fit_time = predict, so nothing is fitted at train "
              f"time; {len(frame)} training rows recorded -> {model_path}")
        return model

    model = fit_model(frame, options)
    model["fitted_in"] = "train"
    Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))
    training = model["training"]
    print(
        f"hier_nb_candidate ({model['observation']}) fitted on {training['rows_used']} rows "
        f"({training['first_period']}..{training['last_period']}), "
        f"{training['provinces']} provinces, {training['province_years']} province-years; "
        f"sigma_province {model['sigma_province']:.3f}, "
        f"sigma_province_year {model['sigma_province_year']:.3f}, "
        f"dispersion {model['dispersion']:.3f}, "
        f"converged {model['fit']['converged']} in {model['fit']['outer_rounds']} rounds "
        f"-> {model_path}"
    )
    return model


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
