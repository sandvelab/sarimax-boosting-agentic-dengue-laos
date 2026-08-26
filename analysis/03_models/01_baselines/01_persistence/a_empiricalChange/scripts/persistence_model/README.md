# `persistence_baseline` — a Chap-compatible probabilistic persistence model

One of the two baselines the plan's §4 requires. It is here rather than in the claim
tree because batch 6 is the vertical slice and batch 7 erects the tree; batch 7 moves
this directory to `analysis/03_models/01_baselines/01_persistence/scripts/model/` and
re-runs it from there.

## What it forecasts

The point forecast is the province's **last observed count**, carried forward over the
three-month horizon — which is what "persistence" means and what the plan names.

A point forecast is not a comparison. CRPS scores a distribution, and a point forecast
dressed as one scores badly for a reason that says nothing about the method: batch 4
measured a single-draw model at CRPS 44.055, exactly equal to its MAE, with both
coverage metrics at zero. So the baseline needs a predictive distribution, and how to
put one around a persistence forecast is a judgment call with two published answers.

**The one taken here** is the non-parametric hub form: the predictive distribution is
the last observed value plus the empirical distribution of past *h*-step changes,
each change entered together with its negation so the predictive median stays exactly
on the last observation, truncated at zero. It estimates nothing, so a baseline cannot
be accidentally tuned into a competitor.

**The one not taken** is parametric: a negative binomial with mean equal to the last
observation and a dispersion fitted by maximum likelihood from recent observations,
with a small floor on the mean to stop the distribution collapsing when the last
observation is zero. That floor is why it is not the main path here — 56 % of observed
months in this dataset are zero, so an arbitrary constant would be doing visible work
in a majority of cells. It is retained as the sibling of the phase-D fork on how
uncertainty is wrapped around a point baseline.

Sources for both constructions are in `AI-generated/vertical-slice/provenance.md`.

## Two details that matter on this dataset

**Changes are pooled within a province, never across provinces.** Provincial burdens
differ by four orders of magnitude, so a pooled distribution of absolute changes would
be set by Vientiane Capital and would be absurd for Phongsaly, which reports four cases
in twelve years. A province with fewer than ten observed pairs falls back to the pooled
distribution, and the fitted model records which provinces those were — on the
development data at the fixed scheme, none of them.

**The anchor comes from the historic frame, the spread from the training frame.** With
`n_retrain 1` chap-core fits once and then hands `predict` an expanding historic window
at every split. The spread is therefore fixed after the single fit while the point
forecast always starts from the most recent observation available at that split, which
is the honest reading of a persistence forecast under this backtest.

## Contract

`MLproject` declares a `uv_env`, so chap-core builds the model's environment itself
from `pyproject.toml` and `uv.lock` — no Docker and no image. Both files are pinned to
the patch, interpreter included, for the reason batch 2 pinned the analysis
environment: a version that depends on what the building machine happens to hold is not
a specification.

| File | Role |
|---|---|
| `MLproject` | the contract chap-core parses: target, period type, the two entry points |
| `pyproject.toml` | exact dependency pins and `requires-python = "==3.13.0"` |
| `uv.lock` | the resolved environment, six packages |
| `train.py` | fits the *h*-step change distributions; writes JSON, not a pickle |
| `predict.py` | anchor + changes, truncated at zero, 1 000 draws per cell |

**Nothing in it is random.** The draws are the empirical quantile function evaluated at
the 1 000 midpoints `(i + 0.5) / 1000` rather than sampled from it, so two runs are
byte-identical and Rule 6 is satisfied by there being nothing to seed. The draw count
matches the reference model's 1 000 posterior draws so that the sample-based CRPS of
the two is computed at the same resolution.
