"""Forecast with the seasonal climatology baseline: what this month usually brings.

For each province and each month to be forecast, the predictive distribution is the
empirical distribution of the counts that province reported in that calendar month, over
every year available in the **historic** frame -- the expanding window chap-core hands to
`predict` at each split. So although `n_retrain 1` means this model is fitted once, its
seasonal table is re-estimated at every split, in the same way the persistence baseline's
anchor is the most recent observation available at the split. That is this node's choice
and the fitted table from `train.py` records what the alternative would have used.

The draws are produced by evaluating the empirical quantile function at the N midpoints
(i + 0.5) / N rather than by sampling from it, so **the model contains no randomness at
all**: two runs are byte-identical, and Rule 6 is satisfied by there being nothing to
seed rather than by a seed being recorded. Nearest-rank quantiles are used, so every draw
is a count that province actually reported in that month of some year.

Usage:  python predict.py <model.json> <historic_data.csv> <future_data.csv> <out_file.csv>
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

# Draws per cell. Matched to the reference model's 1 000 posterior draws, and to the
# persistence baseline's, so that the sample-based CRPS of all three is computed at the
# same Monte Carlo resolution.
N_SAMPLES = 1000

QUANTILE_LEVELS = (np.arange(N_SAMPLES) + 0.5) / N_SAMPLES


def calendar_month(period: str) -> int:
    text = str(period)
    return int(text[5:7]) if "-" in text else int(text[4:6])


def draws(values: list[int]) -> np.ndarray:
    """The predictive distribution: the empirical quantile function of past counts."""
    return np.clip(
        np.quantile(np.asarray(values, dtype=float), QUANTILE_LEVELS, method="inverted_cdf"),
        0.0, None)


def predict(model_path: str, historic_path: str, future_path: str, out_path: str) -> pd.DataFrame:
    model = json.loads(open(model_path).read())
    min_years = int(model["min_years_for_own_distribution"])

    historic = pd.read_csv(historic_path).dropna(subset=["disease_cases"]).copy()
    historic["month"] = [calendar_month(p) for p in historic["time_period"]]
    future = pd.read_csv(future_path)

    rows = []
    silent = []
    fallbacks = []
    for province, block in future.groupby("location", sort=True):
        seen = historic[historic["location"] == province]
        province_values = [int(round(v)) for v in seen["disease_cases"]]
        for _, cell in block.iterrows():
            month = calendar_month(cell["time_period"])
            month_values = [int(round(v)) for v in seen[seen["month"] == month]["disease_cases"]]

            if len(month_values) >= min_years:
                values = month_values
            elif province_values:
                # Too few years of this month: fall back to everything the province has
                # reported. Recorded rather than passed over.
                values, source = province_values, "province"
                fallbacks.append(f"{province}:{month}")
            else:
                # A province that never reported has no climatology. Zero is the honest
                # forecast; chap-core's region filter removes such provinces before
                # evaluation, so this branch exists for completeness.
                values = [0]
                silent.append(province)

            rows.append(
                {"time_period": cell["time_period"], "location": province}
                | {f"sample_{i}": v for i, v in enumerate(draws(values))}
            )

    out = pd.DataFrame(rows)
    out.to_csv(out_path, index=False)
    print(
        f"seasonal_climatology wrote {len(out)} cells x {N_SAMPLES} draws -> {out_path}"
        + (f"; province-months on the province-wide fallback: {len(set(fallbacks))}" if fallbacks else "")
        + (f"; provinces with no observed history: {sorted(set(silent))}" if silent else "")
    )
    return out


if __name__ == "__main__":
    predict(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
