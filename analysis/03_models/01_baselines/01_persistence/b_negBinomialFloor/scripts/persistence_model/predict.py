"""Forecast with the parametric persistence baseline: a negative binomial about the last count.

The point forecast is each province's last observed count in the *historic* frame, which
chap-core expands at every split -- so although `n_retrain 1` means this model is fitted
once, its forecasts always start from the most recent observation available at the split.
That is what a persistence forecast means, and the sibling construction does the same.

The predictive distribution is `NB(mean = max(last observed, 0.2), dispersion = r)`, with
`r` re-estimated by maximum likelihood from the last five observations in the same historic
frame. **The same distribution is used at every horizon**, which is the source's own rule
for horizons beyond the first and is where this construction differs most sharply from its
sibling: the empirical-change construction widens with the horizon because it is built from
h-step changes, and this one does not widen at all.

The draws are the quantile function evaluated at the N midpoints (i + 0.5) / N rather than
sampled from it, so **the model contains no randomness**: two runs are byte-identical and
Rule 6 is satisfied by there being nothing to seed. Nearest-rank quantiles, so every draw
is an integer count.

Usage:  python predict.py <model.json> <historic_data.csv> <future_data.csv> <out_file.csv>
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from negbinom import fit_dispersion, quantiles
from train import MIN_PAIRS, month_index, recent_pairs

# Draws per cell. Matched to the reference model's 1 000 posterior draws, and to the other
# baselines', so that the sample-based CRPS of all of them is computed at the same
# resolution.
N_SAMPLES = 1000

QUANTILE_LEVELS = (np.arange(N_SAMPLES) + 0.5) / N_SAMPLES


def last_observed(historic: pd.DataFrame) -> float | None:
    """The most recent non-missing count for one province, or None if it never reported."""
    observed = historic.dropna(subset=["disease_cases"])
    if observed.empty:
        return None
    order = [month_index(p) for p in observed["time_period"]]
    return float(observed["disease_cases"].iloc[int(np.argmax(order))])


def predict(model_path: str, historic_path: str, future_path: str, out_path: str) -> pd.DataFrame:
    model = json.loads(open(model_path).read())
    floor = float(model["floor"])
    window = int(model["recent_observations"])
    stored = model["dispersion_by_province"]
    pooled = model["dispersion_pooled"]["dispersion"]

    historic = pd.read_csv(historic_path)
    future = pd.read_csv(future_path)

    rows = []
    silent, at_bound, on_stored, truncated = [], [], [], []
    for province, block in future.groupby("location", sort=True):
        seen = historic[historic["location"] == province]
        anchor = last_observed(seen)
        if anchor is None:
            # A province that never reported has no value to persist. Zero is the honest
            # forecast, floored like any other, and the case is recorded rather than
            # passed over; chap-core's region filter removes such provinces before
            # evaluation, so this branch exists for completeness.
            anchor = 0.0
            silent.append(province)

        y, mu = recent_pairs(seen, window)
        if len(y) >= MIN_PAIRS:
            fitted = fit_dispersion(y, mu)
        elif province in stored:
            # Not enough consecutive months here: the estimate from the training frame is
            # what the model knew, and it is used rather than inventing a wider default.
            fitted = stored[province]
            on_stored.append(province)
        else:
            fitted = {"dispersion": pooled, "at_bound": "pooled"}
            on_stored.append(province)
        if fitted["at_bound"]:
            at_bound.append(f"{province}:{fitted['at_bound']}")

        draws, cut = quantiles(max(anchor, floor), float(fitted["dispersion"]),
                               QUANTILE_LEVELS)
        if cut:
            truncated.append(province)

        for _, cell in block.iterrows():
            rows.append(
                {"time_period": cell["time_period"], "location": province}
                | {f"sample_{i}": v for i, v in enumerate(draws)})

    out = pd.DataFrame(rows)
    out.to_csv(out_path, index=False)
    print(
        f"persistence_negbinomial_floor wrote {len(out)} cells x {N_SAMPLES} draws "
        f"-> {out_path}"
        + (f"; dispersion at a bound: {sorted(set(at_bound))}" if at_bound else "")
        + (f"; on the stored or pooled dispersion: {sorted(set(on_stored))}" if on_stored else "")
        + (f"; pmf summation truncated for: {sorted(set(truncated))}" if truncated else "")
        + (f"; provinces with no observed history: {sorted(set(silent))}" if silent else "")
    )
    return out


if __name__ == "__main__":
    predict(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
