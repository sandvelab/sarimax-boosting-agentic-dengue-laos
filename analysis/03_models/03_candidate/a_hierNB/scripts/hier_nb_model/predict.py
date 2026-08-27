"""Forecast with the hierarchical negative-binomial candidate.

Chap hands this entry point the expanding historic frame and the three months of future
covariates it wants forecast. What the script does with the historic frame is itself a
fork:

* under `fit_time = train` -- the main path -- it uses it for exactly one thing, to look
  up the lags a forecast month needs, since the covariate two months before a forecast
  month is usually an observed month rather than a forecast one. No case count from it
  enters the fit, because the fit is not revisited;
* under `fit_time = predict`, the model is refitted here on everything the historic frame
  contains. By the last split of the development backtest that is two more years of
  observations than a train-time fit ever saw. The reference model this project is
  measured against refits inside predict, which is what makes the fork worth having.

An autoregressive term reads the historic frame either way: `autoregressive = lag3` puts
the count three months before a forecast month into the design, and at a three-month
horizon that count is always an observed one, whichever of the three months is being
forecast.

## Where the forecast distribution comes from

Three sources, and each answers a different question about what is not known:

1. **the coefficients** -- drawn from the Laplace approximation to their posterior, the
   normal centred at the fit with the inverse penalised information as covariance. This is
   what "we do not know the seasonal shape or the climate effect exactly" contributes;
2. **the province-year effect** -- drawn from its estimated distribution rather than
   fitted, because a forecast month lies in a year the fit never saw. This is what "some
   years are worse than others and we do not know which kind this one is" contributes,
   and it is drawn once per province-year per sample, so the three months of a split move
   together in a draw rather than independently;
3. **the observation model** -- the negative binomial on top of both, and, where the
   `01_observation` fork asks for one, the mixture or the two-part construction around it.

Leaving out the second of those is the standard way a count model ends up confidently
wrong: it would forecast each province's own average year, with only parameter and
observation noise around it.

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

from hier_nb import add_features, draw, fit_model, lag_columns, read_options

# Draws per cell. Matched to the reference model's 1 000 posterior draws and to both
# baselines, so the sample-based CRPS of every model in the project is computed at the
# same resolution.
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

    if options["fit_time"] == "predict":
        # The whole point of this child: everything observed up to this split, including
        # the two years a train-time fit never saw.
        model = fit_model(historic, options)
        model["fitted_in"] = "predict"

    # The lag of a forecast month usually falls inside the historic frame, so the lags
    # are built on the two frames together and then read off the forecast rows.
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

    missing_lags = int(sum(
        pd.to_numeric(rows[column], errors="coerce").isna().sum()
        for column in lag_columns(options)))
    unseen = sorted({p for p in rows["location"] if p not in set(model["provinces"])})
    print(
        f"hier_nb_candidate ({options['observation']}, fitted in {model['fitted_in']}) "
        f"wrote {len(out)} cells x {N_SAMPLES} draws -> {out_path}"
        + (f"; provinces not seen in training: {unseen}" if unseen else "")
        + (f"; forecast rows with a missing lag: {missing_lags}" if missing_lags else "")
    )
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
