# `boosted_model` — the gradient-boosted candidate

A Chap model contract directory. `MLproject` declares it, `pyproject.toml` and `uv.lock`
pin its environment, `boosted.py` is the model, and `train.py` and `predict.py` are the two
entry points chap-core calls. It is candidate 2 of the Lao dengue forecasting case; the node
above it, `analysis/03_models/03_candidate/b_boosted/`, is where its claim, its two
configuration forks and its results live.

## What the model is

Two pieces, and the split between them is the shape of this family:

    where the count sits   histogram gradient-boosted regression trees over
                           lagged climate, lagged counts and log population
    how wide it is         a head built around that number, because a tree
                           returns one value and not a distribution

The trees assume nothing: no link between covariate and count beyond monotone splits, no
additivity, no assumption that rainfall means the same thing in a large province and a small
one. What they cannot do is extrapolate — outside the range of the training data a tree
returns the value of its nearest leaf, forever. Candidate 1 is the opposite bargain: a
functional form that extrapolates and a hierarchy that pools, in exchange for assuming the
form is right.

## The two forks

| Option | Values | Fork |
|---|---|---|
| `features` | `lag_block`, `rich_calendar` | `01_features` |
| `head` | `negative_binomial`, `quantile_ensemble` | `02_head` |

The lag structure is asymmetric and the asymmetry is the forecasting problem rather than a
choice: `chap eval` hands the model the climate of the months it is asked to forecast, so
climate enters at lag 0, while the count — the unknown thing — cannot be seen fresher than
three months back by a model that has to serve all three horizons at once.

## The boosting hyper-parameters are not forks

Shrinkage, tree size, leaf minimum, L2 penalty and the round cap are set once here, and the
number of rounds is then chosen from the data by an early-stopping split taken **by month**
rather than at random — a stopping rule that scores itself on rows interleaved with the
training rows is choosing a model for a different problem than the backtest poses. Making
them forks would enumerate a tuning grid whose siblings all have to be re-run in phase D and
on the holdout, to answer a question about tuning rather than about a judgment call an
analyst would plausibly make differently. `AGENTS.md` §3 allows a judgment call to be a node
**or** a logged decision; this is the second, logged here, in `boosted.py`'s docstring, and
in the node's claim.

## The fitted model is JSON, and it is meant to be read

Rule 5 forbids a language-specific pickle for anything outliving the session, and the fitted
object outlives it. So the boosters are written out as trees — split feature, threshold, the
direction a missing value takes, the two children, the leaf values — as parallel arrays, and
`boosted.py`'s own `raw_predict` walks that structure with nothing but numpy. Reading the
stored model needs no scikit-learn, which has been checked by importing the module with
scikit-learn blocked.

Because that traversal is a *second* prediction path, and a second path can disagree, the
fit checks it rather than trusting it: every booster's stored form is evaluated on the
training rows and compared with scikit-learn's own `predict`, and the run fails if the
largest difference is not at machine precision. It has been 0.0 on every run so far.

## Dependencies

Four, pinned exactly in `uv.lock`: numpy, pandas, pyyaml and **scikit-learn**. The last is
the first dependency in this project beyond the three every other model shares, and the
reason is in `pyproject.toml`: gradient boosting is not two functions, and a hand-written
version would be both unreadable and incomparable with anything published — the opposite of
the case for hand-writing candidate 1's Fisher-scoring fitter.

## Seeds

Nothing in the fit is random: early stopping is disabled and the round count is fixed before
the final fit, so two fits on one frame are identical. Every forecast draw comes from one
NumPy generator seeded with the component seed the node above derives from the project seed
and writes into the configuration file. Verified by
`AI-internal/useful-scripts/verify_model_determinism.sh`, which reports `identical`.
