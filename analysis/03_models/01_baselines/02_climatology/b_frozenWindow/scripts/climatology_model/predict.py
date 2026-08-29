"""Forecast with the frozen seasonal climatology baseline: what this month used to bring.

For each province and each month to be forecast, the predictive distribution is the
empirical distribution of the counts that province reported in that calendar month **in the
training frame**, as `train.py` tabulated them. The table does not move for the rest of the
backtest.

**The historic frame is deliberately not read.** chap-core hands `predict` an expanding
window at every split, and the sibling construction re-estimates from it; this child does
not, which is the whole content of the fork. The frame is still a parameter of the entry
point because the contract says so, and leaving it unused is the honest way to say that a
model fitted once knows what it knew at fitting time. What that costs is measurable here:
the training period ends 2007-12 and the evaluation runs to 2009-12, so this model forecasts
two dengue seasons from a table that has never seen them.

The draws are produced by evaluating the empirical quantile function at the N midpoints
(i + 0.5) / N rather than by sampling from it, so **the model contains no randomness at
all**: two runs are byte-identical, and Rule 6 is satisfied by there being nothing to seed
rather than by a seed being recorded. Nearest-rank quantiles are used, so every draw is a
count that province actually reported in that month of some training year.

Usage:  python predict.py <model.json> <historic_data.csv> <future_data.csv> <out_file.csv>
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

# Draws per cell. Matched to the reference model's 1 000 posterior draws, and to the other
# baselines', so that the sample-based CRPS of all of them is computed at the same
# Monte Carlo resolution.
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
    by_province_month = model["values_by_province_month"]
    by_province = model["values_by_province"]
    future = pd.read_csv(future_path)

    rows = []
    silent = []
    fallbacks = []
    for province, block in future.groupby("location", sort=True):
        for _, cell in block.iterrows():
            month = str(calendar_month(cell["time_period"]))
            month_values = by_province_month.get(province, {}).get(month)

            if month_values:
                values = month_values
            elif by_province.get(province):
                # Too few training years of this month: fall back to everything the
                # province reported in the training frame. The same fallback the sibling
                # uses, applied to the frozen table, and counted rather than passed over.
                values = by_province[province]
                fallbacks.append(f"{province}:{month}")
            else:
                # A province with nothing in the training frame has no climatology. Zero
                # is the honest forecast; chap-core's region filter removes such provinces
                # before evaluation, so this branch exists for completeness.
                values = [0]
                silent.append(province)

            rows.append(
                {"time_period": cell["time_period"], "location": province}
                | {f"sample_{i}": v for i, v in enumerate(draws(values))})

    out = pd.DataFrame(rows)
    out.to_csv(out_path, index=False)
    print(
        f"seasonal_climatology_frozen wrote {len(out)} cells x {N_SAMPLES} draws "
        f"-> {out_path}"
        + (f"; province-months on the province-wide fallback: {len(set(fallbacks))}" if fallbacks else "")
        + (f"; provinces absent from the frozen table: {sorted(set(silent))}" if silent else "")
    )
    return out


if __name__ == "__main__":
    predict(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
