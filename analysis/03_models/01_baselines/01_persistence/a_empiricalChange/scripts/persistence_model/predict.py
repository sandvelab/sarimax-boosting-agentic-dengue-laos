"""Forecast with the persistence baseline: last observed value plus fitted changes.

The point forecast is each province's last observed count in the *historic* frame,
which chap-core expands at every split -- so although `n_retrain 1` means this model
is fitted once, its forecasts always start from the most recent observation available
at the split, which is what a persistence forecast means.

The predictive distribution is that value plus the fitted empirical distribution of
h-step changes, truncated at zero. The draws are produced by evaluating the empirical
quantile function at the N midpoints (i + 0.5) / N rather than by sampling from it, so
**the model contains no randomness at all**: two runs are byte-identical, and Rule 6 is
satisfied by there being nothing to seed rather than by a seed being recorded.

Nearest-rank quantiles are used, so every draw is an integer that actually occurred as
a change in the training data. The forecast is a distribution over counts and it is
kept on the scale of counts.

Usage:  python predict.py <model.json> <historic_data.csv> <future_data.csv> <out_file.csv>
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

# Draws per cell. Matched to the reference model's 1 000 posterior draws so that the
# sample-based CRPS of the two is computed at the same resolution.
N_SAMPLES = 1000

QUANTILE_LEVELS = (np.arange(N_SAMPLES) + 0.5) / N_SAMPLES


def month_index(period: str) -> int:
    text = str(period)
    year, month = int(text[:4]), int(text[5:7]) if "-" in text else int(text[4:6])
    return year * 12 + (month - 1)


def last_observed(historic: pd.DataFrame) -> float | None:
    """The most recent non-missing count for one province, or None if it never reported."""
    observed = historic.dropna(subset=["disease_cases"])
    if observed.empty:
        return None
    order = [month_index(p) for p in observed["time_period"]]
    return float(observed["disease_cases"].iloc[int(np.argmax(order))])


def draws(anchor: float, changes: list[int]) -> np.ndarray:
    """The predictive distribution: anchor + empirical changes, truncated at zero."""
    quantiles = np.quantile(np.asarray(changes, dtype=float), QUANTILE_LEVELS, method="inverted_cdf")
    return np.clip(anchor + quantiles, 0.0, None)


def predict(model_path: str, historic_path: str, future_path: str, out_path: str) -> pd.DataFrame:
    model = json.loads(open(model_path).read())
    historic = pd.read_csv(historic_path)
    future = pd.read_csv(future_path)

    by_province = model["changes_by_province"]
    pooled = model["changes_pooled"]

    rows = []
    silent = []
    for province, block in future.groupby("location", sort=True):
        anchor = last_observed(historic[historic["location"] == province])
        if anchor is None:
            # A province that never reported has no value to persist. Zero is the
            # honest forecast and the case is recorded rather than passed over;
            # chap-core's region filter removes such provinces before evaluation, so
            # this branch exists for completeness rather than for the headline number.
            anchor, changes_source = 0.0, "none"
            silent.append(province)
        else:
            changes_source = "province" if province in by_province else "pooled"

        block = block.assign(_m=[month_index(p) for p in block["time_period"]]).sort_values("_m")
        for horizon, (_, cell) in enumerate(block.iterrows(), start=1):
            key = str(min(horizon, model["max_horizon"]))
            changes = (
                by_province[province][key]
                if changes_source == "province" and key in by_province[province]
                else pooled[key]
            )
            rows.append(
                {"time_period": cell["time_period"], "location": province}
                | {f"sample_{i}": v for i, v in enumerate(draws(anchor, changes))}
            )

    out = pd.DataFrame(rows)
    out.to_csv(out_path, index=False)
    print(
        f"persistence_baseline wrote {len(out)} cells x {N_SAMPLES} draws -> {out_path}"
        + (f"; provinces with no observed history: {silent}" if silent else "")
    )
    return out


if __name__ == "__main__":
    predict(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
