# `persistence_baseline_negbinomial` — the parametric persistence construction

The path this fork does not take on the main line. A persistence forecast is a point, CRPS
scores a distribution, and there are two published ways to put one around the other; the
sibling `a_empiricalChange` is the non-parametric one and is the main path, and this is the
parametric one. The fork exists because the two disagree, and the disagreement sets the
calibration of one of the two baselines the plan's §2 defines success against — and, since
batch 11, of a member of the model this project reports.

## What it forecasts

The point forecast is the province's **last observed count** in the historic frame, carried
across the three-month horizon: the same point forecast as the sibling, because that is what
persistence means and it is not what this fork moves.

The predictive distribution around it is **negative binomial**, with

- **mean** = the last observed count, **floored at 0.2** when that count is zero;
- **dispersion** estimated by **maximum likelihood from the last five observations**, each
  taken against the mean the construction would have given it — the previous month's count,
  floored the same way;
- **the same distribution at every horizon**. The source states this for horizons beyond the
  first, and it is the sharpest contrast with the sibling, whose spread is built from *h*-step
  changes and therefore widens with the horizon. This one does not widen at all.

## The constants are the source's

The floor, the window and the estimator are all taken from the **KIT baseline for the German
COVID-19 Forecast Hub** (<https://github.com/KITmetricslab/KIT-baseline>, read 2026-08-26 and
re-read 2026-08-29), which states: set the predictive mean to the observed number in the
previous period; if none was observed set it to 0.2, *"necessary to avoid zero variance in
parametric predictive distribution"*; and *"estimate overdispersion parameter of a negative
binomial distribution from the last five observations (maximum likelihood; with the respective
means as defined above)"*.

**None of them is ours, and that is the point.** A stability fork whose alternative was tuned
against the path taken measures the tuning, not the alternative. What *is* recorded is that
five weekly observations there are five monthly ones here — a window that is much longer in
time and much thinner in dengue seasons — and that this is a property of transplanting the
construction rather than something to be repaired by choosing a different number.

## The second arbitrary constant, which the source does not have to state

On this dataset the maximum-likelihood dispersion often **does not exist**. When every
observation in the window is zero and each mean is the floor, the log-likelihood increases
monotonically as the dispersion goes to zero, where the distribution becomes a point mass at
zero; symmetrically, a window no more spread than a Poisson pushes it up without limit. So the
estimator needs bounds, `[0.01, 1000]`, and they are not cosmetic: on the development training
frame they bind for **six of eighteen provinces**, five at the lower bound and one at the upper.

That is the fork's own claim arriving in the arithmetic. The main path rejects this
construction because an arbitrary floor would be doing visible work in the majority of months
that report zero; the floor turns out to be the *first* of two arbitrary constants, and the
second one — the bound — is doing its work in exactly the provinces where the first one is.

## Two details that matter on this dataset

**The dispersion is re-estimated at every split, from the historic frame.** chap-core fits this
model once (`n_retrain 1`) and hands `predict` an expanding historic window, and the source's
"last five observations" means the last five available when the forecast is made. Estimating
the dispersion at training time while taking the mean from the historic frame would be a hybrid
neither construction describes. `train.py` builds and stores the training-frame estimate anyway,
so what the model knew at fitting time is in the record and is the fallback for a province the
historic frame cannot fit.

**A province needs two consecutive observed months** to be fitted at all; below that it takes
the estimate pooled across provinces, and the fallback is recorded rather than silent.

## Contract

`MLproject` declares a `uv_env`, the same shape as the sibling's, so both children of this fork
reach `chap eval` by the identical route — a fork whose two sides took different routes would be
measuring the route. `uv.lock` resolves to the **same six packages at the same versions** as the
sibling's. The negative binomial is implemented from its own pmf rather than pulled in from
scipy, which keeps that true and keeps the pool's environment — the union of its members' — where
it was.

| File | Role |
|---|---|
| `MLproject` | the contract chap-core parses: target, period type, the two entry points |
| `pyproject.toml` | exact dependency pins and `requires-python = "==3.13.0"` |
| `uv.lock` | the resolved environment, six packages |
| `negbinom.py` | the distribution: the bounded maximum-likelihood fit and the quantile function |
| `train.py` | fits the dispersion at the end of the training frame; writes JSON, not a pickle |
| `predict.py` | re-fits from the historic frame, anchors on the last observation, 1 000 draws |

**Nothing in it is random.** The fit is a deterministic search on a fixed grid and the draws are
the quantile function evaluated at the 1 000 midpoints `(i + 0.5) / 1000` rather than sampled
from it, so two runs are byte-identical and Rule 6 is satisfied by there being nothing to seed.
The draw count matches the reference model's 1 000 posterior draws so that the sample-based CRPS
of the two is computed at the same resolution.
