"""Forecast with the hierarchical negative-binomial candidate.

`train.py` fitted the model once; this script applies it. It is handed the expanding
historic frame and the three months of future covariates that Chap wants forecast, and it
uses the historic frame for exactly one thing -- to look the covariate lags up, since the
covariate two months before a forecast month is usually an observed month rather than a
forecast one. No case count from the historic frame enters anything, because under
`fit_time = train` the fit is not revisited.

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
3. **the negative binomial** -- the observation model on top of both.

Leaving out the second of those is the standard way a count model ends up confidently
wrong: it would forecast each province's own average year, with only parameter and
observation noise around it.

Seeds: one NumPy generator, seeded with the `seed` option that the assembling node derived
from the project seed 20260822 and wrote into the configuration file. Everything drawn
here comes from it, in a fixed order over rows sorted by location and period, so two runs
of the same split produce identical draws. Verified rather than asserted, by running the
model twice and diffing.

Usage:  python predict.py <model.json> <historic.csv> <future.csv> <out.csv> <config.yaml>
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from hier_nb import ETA_CLIP, add_features, fixed_design, offset, read_options

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

    # The covariate lag of a forecast month usually falls inside the historic frame, so
    # the lags are built on the two frames together and then read off the forecast rows.
    future_marked = future.assign(_is_forecast=True)
    historic_marked = historic.assign(_is_forecast=False)
    if "disease_cases" not in future_marked.columns:
        future_marked["disease_cases"] = np.nan
    combined = pd.concat([historic_marked, future_marked], ignore_index=True)
    prepared = add_features(combined, options)
    rows = (prepared[prepared["_is_forecast"]]
            .sort_values(["location", "_m"]).reset_index(drop=True))

    F, _ = fixed_design(rows, options, model["standardisation"])
    off = offset(rows, options)

    n_fixed = len(model["fixed_names"])
    provinces = list(model["provinces"])
    province_index = {p: i for i, p in enumerate(provinces)}
    mean_level = np.array(
        [model["fixed_effects"][name] for name in model["fixed_names"]]
        + [model["province_effects"][p] for p in provinces])
    cholesky = np.array(model["level_cholesky"])

    rng = np.random.default_rng(model["options"]["seed"])

    # One draw of the level parameters per sample: fixed effects and every province's
    # effect jointly, because they are correlated and forecasting each province from an
    # independently drawn intercept would understate how much they move together.
    level = mean_level[:, None] + cholesky @ rng.standard_normal((len(mean_level), N_SAMPLES))
    fixed_draws = level[:n_fixed]
    province_draws = level[n_fixed:]

    sigma_province_year = model["sigma_province_year"]
    sigma_province = model["sigma_province"]
    dispersion = model["dispersion"]

    # A province-year effect per (province, year) appearing among the forecast rows,
    # drawn from its estimated distribution. Drawn once per key so that the months of a
    # split share it within a sample.
    seen_years = {(p, int(y)) for p, y in
                  [tuple(k) for k in model["province_years_seen"]]}
    keys = sorted({(location, int(year)) for location, year in
                   zip(rows["location"], rows["_year"], strict=True)})
    province_year_draws = {key: rng.standard_normal(N_SAMPLES) * sigma_province_year
                           for key in keys}
    years_already_fitted = sorted(f"{p}:{y}" for p, y in keys if (p, y) in seen_years)

    unseen_provinces = sorted({p for p in rows["location"] if p not in province_index})
    unseen_draws = {p: rng.standard_normal(N_SAMPLES) * sigma_province
                    for p in unseen_provinces}

    lag_columns = [f"{c}_lag" for c in options["covariates"]]
    missing_lag_cells = int(sum(
        pd.to_numeric(rows[column], errors="coerce").isna().sum() for column in lag_columns))

    records = []
    for position in range(len(rows)):
        location = rows.at[position, "location"]
        year = int(rows.at[position, "_year"])
        level_term = (province_draws[province_index[location]]
                      if location in province_index else unseen_draws[location])
        eta = (off[position]
               + F[position] @ fixed_draws
               + level_term
               + province_year_draws[(location, year)])
        mu = np.exp(np.clip(eta, -ETA_CLIP, ETA_CLIP))
        draws = rng.negative_binomial(dispersion, dispersion / (dispersion + mu))
        records.append(
            {"time_period": rows.at[position, "time_period"], "location": location}
            | {f"sample_{i}": int(v) for i, v in enumerate(draws)})

    out = pd.DataFrame(records)
    out.to_csv(out_path, index=False)
    print(
        f"hier_nb_candidate wrote {len(out)} cells x {N_SAMPLES} draws -> {out_path}"
        + (f"; provinces not seen in training: {unseen_provinces}" if unseen_provinces else "")
        + (f"; forecast rows with a missing covariate lag: {missing_lag_cells}"
           if missing_lag_cells else "")
        + (f"; forecast province-years the fit had already seen: {years_already_fitted}"
           if years_already_fitted else "")
    )
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
