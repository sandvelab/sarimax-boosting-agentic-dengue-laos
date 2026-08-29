# `seasonal_climatology_frozen` — the frozen-window climatology construction

The path this fork does not take on the main line. The seasonal climatology baseline needs no
decision about how to wrap uncertainty around a point — a set of past Julys is a distribution
already — but it does need a decision about **which window estimates that distribution**, and
that is what this fork is.

## What it forecasts

For each province and calendar month, the empirical distribution of the counts that province
reported in that month **in the training frame**, tabulated once by `train.py` and held fixed
across every split.

The sibling `a_expandingWindow` is the main path and does the opposite: chap-core fits this
model once (`n_retrain 1`) but hands `predict` an expanding historic window at every split, and
the sibling re-estimates the table from it, so the baseline uses everything observed by the time
the forecast is made — the same treatment the persistence baseline's anchor gets.

**This child does not read the historic frame at all.** A model fitted once knows what it knew
at fitting time, and on this dataset that gap is not small: the training period ends 2007-12 and
the evaluation runs to 2009-12, so the frozen table forecasts two dengue seasons it has never
seen, in a series whose reporting has been improving throughout. Whether that costs anything is
what the stability run measures.

## What the two children share, and why it is duplicated

The table build in `train.py` is the same computation on both sides of the fork, under different
values of one recorded field (`window`). It is duplicated rather than lifted into a library
because **a Chap contract directory is copied whole into the run directory**: chap-core builds
the model's environment inside it and runs its entry points there, so a module outside the
directory does not travel with the model. The alternative — one contract directory with a
configuration switch — was rejected for a different reason: it would change the bytes of the
model that produced six committed combinations' results, and the fork would become a
configuration option rather than a path in the tree, which is the opposite of what `/perturb`
asks for.

The fork's substance is entirely in `predict.py`, and that file is genuinely two different
models.

## A detail that matters on this dataset

**A province-month with fewer than three observed training years** falls back to that province's
whole observed training record, and a province absent from the training table falls back to
zero. Both are counted by `predict.py` rather than left silent. The threshold is the sibling's,
unchanged: it is not what this fork moves.

## Contract and environment

An `MLproject` with a `uv_env`, byte-for-byte the sibling's but for its name, so both children
of the fork reach `chap eval` by the identical route. `pyproject.toml` pins the interpreter to
the patch (`==3.13.0`) and the two dependencies exactly; `uv.lock` resolves the same six
packages at the same versions as the sibling's.

**No randomness.** The 1 000 draws per cell are the empirical quantile function evaluated at the
fixed levels `(i + 0.5)/1000`, not sampled from it, so Rule 6 is satisfied by there being
nothing to seed. 1 000 draws matches the reference and the other baselines, because sample-based
CRPS estimated at different draw counts is estimated at different resolutions.
