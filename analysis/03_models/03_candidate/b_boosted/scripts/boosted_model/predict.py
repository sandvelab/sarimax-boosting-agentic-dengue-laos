"""Forecast with the gradient-boosted candidate.

Chap hands this entry point the expanding historic frame and the three months of future
covariates it wants forecast. Both are used, and for different things:

* the **future** frame carries the climate columns of the months being forecast, so this
  model can use climate at lag zero. Only the target has to be lagged by three months,
  because only the target is unknown for the months being predicted;
* the **historic** frame carries the counts. Every lagged-count and rolling-count feature
  is read from it, which is why the two frames are prepared together and the forecast rows
  read off afterwards.

The fit is not revisited here. The boosters were fitted once, on the training frame, and
are applied to whatever features the expanding history now supports — so the model's
knowledge of the world is fixed at the end of the training period while its inputs are
current. That is a real limitation and it is named rather than worked around; the sibling
family has a fork that measures what refitting is worth.

## Where the forecast distribution comes from

Neither head produces a distribution as a by-product of being fitted, which is the whole
difficulty this family has and the reason `02_head` is a fork:

* **`negative_binomial`** — the booster gives a conditional mean and the head puts a
  negative binomial around it at the dispersion estimated during the fit. Nothing about
  the width is specific to the cell beyond its own predicted level;
* **`quantile_ensemble`** — fifteen boosters give fifteen points of the cell's own
  conditional distribution, made monotone and inverted at a uniform draw. The width is the
  fit's, not a functional form's, and the cost is that it is only as good as a ladder of
  fifteen independent fits can be.

What neither head carries, and candidate 1's does, is uncertainty about the fitted model
itself. A boosted ensemble has no posterior to draw coefficients from, so the forecast
spread here is the spread of the outcome around a model taken as known. That is a
structural difference between the two families rather than a setting.

Seeds: one NumPy generator, seeded with the `seed` option that the assembling node derived
from the project seed and wrote into the configuration file. Everything drawn here comes
from it, in a fixed order over rows sorted by location and period, so two runs of the same
split produce identical draws. Verified rather than asserted, by running the model twice
and diffing.

Usage:  python predict.py <model.json> <historic.csv> <future.csv> <out.csv> <config.yaml>
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from boosted import add_features, draw, read_options

# Draws per cell. Matched to the reference model's 1 000 posterior draws, to both
# baselines and to candidate 1, so the sample-based CRPS of every model in the project is
# computed at the same resolution.
N_SAMPLES = 1000


def main(model_path: str, historic_path: str, future_path: str, out_path: str,
         config_path: str) -> pd.DataFrame:
    options = read_options(config_path)
    model = json.loads(open(model_path).read())
    historic = pd.read_csv(historic_path, dtype={"time_period": str})
    future = pd.read_csv(future_path, dtype={"time_period": str})

    if model["options"] != options:
        raise SystemExit("the configuration handed to predict is not the one the model "
                         "was fitted under; refusing to forecast")

    # The lags of a forecast month fall inside the historic frame, so the features are
    # built on the two frames together and then read off the forecast rows.
    future_marked = future.assign(_is_forecast=True)
    historic_marked = historic.assign(_is_forecast=False)
    if "disease_cases" not in future_marked.columns:
        future_marked["disease_cases"] = np.nan
    combined = pd.concat([historic_marked, future_marked], ignore_index=True)
    prepared = add_features(combined, options)
    rows = (prepared[prepared["_is_forecast"]]
            .sort_values(["location", "_m"]).reset_index(drop=True))

    rng = np.random.default_rng(model["options"]["seed"])
    draws = draw(model, rows, options, rng, N_SAMPLES)

    out = pd.DataFrame([
        {"time_period": rows.at[position, "time_period"],
         "location": rows.at[position, "location"]}
        | {f"sample_{i}": int(v) for i, v in enumerate(draws[position])}
        for position in range(len(rows))
    ])
    out.to_csv(out_path, index=False)

    unseen = sorted({p for p in rows["location"] if p not in set(model["provinces"])})
    print(
        f"boosted_candidate ({model['head']}, {model['features']}, fitted in "
        f"{model['fitted_in']}) wrote {len(out)} cells x {N_SAMPLES} draws -> {out_path}"
        + (f"; provinces not seen in training: {unseen}" if unseen else "")
    )
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
