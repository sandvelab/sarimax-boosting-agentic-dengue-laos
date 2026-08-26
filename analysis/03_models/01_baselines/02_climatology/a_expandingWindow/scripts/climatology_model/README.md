# `seasonal_climatology` — a Chap-compatible seasonal baseline

The second of the two baselines the plan's §4 requires. It knows the season and nothing
else: no covariates, no trend, no recent level.

## What it forecasts

For each province and each calendar month, the predictive distribution is the **empirical
distribution of the counts that province reported in that calendar month**, over the years
available at the time the forecast is made. A July forecast for Champasak is the set of
Julys Champasak has had.

Unlike the persistence baseline beside it, this model needs no decision about how to wrap
uncertainty around a point: a set of past Julys is a distribution already. That asymmetry
is why `01_persistence` forks on the construction of its predictive distribution and this
node does not — and it is worth stating, because "both baselines have a fork" would have
been the tidier-looking tree and the less honest one.

## The judgment call it does contain

**Which window estimates the seasonal distribution.** chap-core fits this model once
(`n_retrain 1`) but hands `predict` an expanding historic window at every split, so there
are two defensible readings:

- **taken** — re-estimate from the historic frame at each split, so the baseline uses
  everything observed by the time the forecast is made. This is the same treatment the
  persistence baseline gets: its anchor is the most recent observation in the historic
  frame, not in the training frame;
- **not taken** — freeze the table at the training period, so a model fitted once really is
  fitted once. `train.py` builds and stores that table, so what the alternative would have
  used is in the record rather than only described.

The node is a fork for this reason and the sibling is built when the stability manifest
needs it. The choice matters: on this dataset the training period ends 2007-12 and the
evaluation runs to 2009-12, so a frozen table would ignore two years of a series whose
reporting has been improving throughout.

**A province-month with fewer than three observed years** falls back to that province's
whole observed record. The fallback is counted and reported by `predict.py` rather than
being silent.

## Contract and environment

An `MLproject` directory with a `uv_env`, the same shape as the persistence baseline's, so
that both baselines reach `chap eval` by the identical route. `pyproject.toml` pins the
interpreter to the patch (`==3.13.0`) and the two dependencies exactly; `uv.lock` resolves
six packages, and the runner checks after every run that the lockfile chap-core built from
is byte-identical to the tracked one.

**No randomness.** The 1 000 draws per cell are the empirical quantile function evaluated
at the fixed levels `(i + 0.5)/1000`, not sampled from it, so Rule 6 is satisfied by there
being nothing to seed. 1 000 draws matches the reference and the other baseline, because
sample-based CRPS estimated at different draw counts is estimated at different resolutions.
