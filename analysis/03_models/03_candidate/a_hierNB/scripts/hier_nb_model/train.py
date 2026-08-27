"""Fit the hierarchical negative-binomial candidate on the training frame.

Everything about what the model is and how it is fitted is in `hier_nb.py`; this script
is the entry point Chap calls, and its job is to read the three files it is given, run the
fit once, and write the fitted object where `predict.py` will find it.

The fit happens here and only here. That is the `fit_time = train` option, taken by the
`04_fitTime` fork above this model: chap-core hands `predict` an expanding historic window
at every split of the backtest, and this configuration ignores it. The sibling that uses
it has to bring its own code, and `hier_nb.read_options` refuses the option until it does.

The fitted object is JSON, not a pickle: it outlives the session (`AGENTS.md` Rule 5), and
it is the only place the fitted variance components and the posterior covariance the
forecasts are drawn from are recorded.

Seeds: none here. Nothing in the fit is random -- it is Fisher scoring from a fixed start
plus a deterministic one-dimensional search -- so two fits on the same frame give the same
file. All the model's randomness is in `predict.py`, seeded from the `seed` option that
the node above derived from the project seed.

Usage:  python train.py <train_data.csv> <model_out.json> <model_config.yaml>
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from hier_nb import build_design, fit, read_options, standardisation, add_features


def main(train_data_path: str, model_path: str, config_path: str) -> dict:
    options = read_options(config_path)
    frame = pd.read_csv(train_data_path, dtype={"time_period": str})

    stats = standardisation(add_features(frame, options), options)
    design = build_design(frame, options, stats)
    fitted = fit(design)

    theta = fitted["theta"]
    n_fixed, n_province = design["n_fixed"], design["n_province"]
    province_effects = theta[n_fixed:n_fixed + n_province]
    province_year_effects = theta[n_fixed + n_province:]

    model = {
        "model": "hier_nb_candidate",
        "construction": ("hierarchical negative-binomial GLM, empirical-Bayes fit by "
                         "Fisher scoring with EM updates for the variance components"),
        "options": options,
        "standardisation": stats,
        "fixed_names": design["fixed_names"],
        "fixed_effects": dict(zip(design["fixed_names"],
                                  [float(x) for x in theta[:n_fixed]], strict=True)),
        "provinces": design["provinces"],
        "province_effects": {p: float(x) for p, x in
                             zip(design["provinces"], province_effects, strict=True)},
        "sigma_province": math.sqrt(fitted["sigma2_province"]),
        "sigma_province_year": math.sqrt(fitted["sigma2_province_year"]),
        "dispersion": fitted["dispersion"],
        # Lower-triangular Cholesky factor of the Laplace covariance of the fixed effects
        # and the province effects, in that order. It is what `predict.py` draws
        # coefficient vectors from, and storing the factor rather than the covariance
        # means the forecast never has to re-decompose anything.
        "level_cholesky": [[float(x) for x in row] for row in fitted["cholesky"]],
        "level_names": design["fixed_names"] + [f"province[{p}]" for p in design["provinces"]],
        "province_years_seen": design["province_years"],
        "province_year_effects": {
            f"{p}:{y}": float(x) for (p, y), x in
            zip([tuple(k) for k in design["province_years"]], province_year_effects,
                strict=True)},
        "training": {
            "rows": int(len(frame)),
            "rows_used": design["rows_used"],
            "rows_dropped_missing_target_or_lag": design["rows_dropped"],
            "provinces": design["n_province"],
            "province_years": design["n_province_year"],
            "first_period": design["first_period"],
            "last_period": design["last_period"],
            "observed_zero_share": float((design["y"] == 0).mean()),
        },
        "fit": {
            "converged": fitted["converged"],
            "outer_rounds": fitted["rounds"],
            "loglik": fitted["loglik"],
            "history": fitted["history"],
        },
    }

    Path(model_path).write_text(json.dumps(model, indent=1, sort_keys=True))
    print(
        f"hier_nb_candidate fitted on {design['rows_used']} rows "
        f"({design['first_period']}..{design['last_period']}), "
        f"{design['n_province']} provinces, {design['n_province_year']} province-years; "
        f"sigma_province {model['sigma_province']:.3f}, "
        f"sigma_province_year {model['sigma_province_year']:.3f}, "
        f"dispersion {model['dispersion']:.3f}, "
        f"converged {fitted['converged']} in {fitted['rounds']} rounds -> {model_path}"
    )
    return model


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
