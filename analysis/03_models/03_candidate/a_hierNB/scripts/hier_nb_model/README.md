# `hier_nb_model` — the hierarchical negative-binomial candidate

A Chap model contract directory. `MLproject` declares it, `pyproject.toml` and `uv.lock`
pin its environment, `hier_nb.py` is the model, and `train.py` and `predict.py` are the two
entry points chap-core calls. It is candidate 1 of the Lao dengue forecasting case; the
node above it, `analysis/03_models/03_candidate/a_hierNB/`, is where its claim, its four
configuration forks and its results live.

## What the model is

Monthly province counts as negative-binomial draws around a log-linear mean:

    log mean = log(population)                       population offset
             + global level
             + shared annual season (two harmonics)
             + standardised climate covariates at a fixed lag
             + province effect                       pooled toward the common level
             + province-year effect                  pooled toward the common level

The last two lines are the hierarchy. Each is penalised toward zero by a variance the fit
estimates, so a province with a thin record is pulled toward the country's common level
while a province with twelve full years is not. That is what lets the model carry 194
parameters on about 1 900 observations.

The **province-year effect is also where the forecast gets its width**. A forecast month is
in a year the fit never saw, so its year effect cannot be estimated and is drawn from its
estimated distribution instead: how much annual dengue activity varies around a province's
own average enters every forecast as uncertainty. Batch 7 found both of this project's
baselines badly under-dispersed — 0.65 interval coverage against a nominal 0.80 — and this
term is the model's answer to that.

## How it is fitted

Empirical Bayes, not sampling. Fisher scoring maximises the penalised log-likelihood given
the variances and the dispersion; the variances are then re-estimated by the EM update
(fitted effects plus their posterior variances, which is what stops the estimate collapsing
to zero); the dispersion is re-estimated by a one-dimensional search on the profile
likelihood; repeat until nothing moves. The posterior is then approximated by a normal
centred at the fit — the Laplace approximation — and forecast draws come from it, from the
prior on the year effect, and from the negative binomial on top of both.

About two seconds to fit, under a second to forecast a split, on three pinned dependencies.
The bargain: no account of skewness in the posterior of the variance components, in exchange
for a fit that is fast, readable and exactly reproducible from a seed. The sibling families
in the tree are where a different bargain gets struck.

## Configuration

The model reads its configuration from a file. chap-core writes
`model_configuration_for_run.yaml` into the run directory from whatever
`chap eval --model-configuration-yaml` was given, and substitutes its name for the
`{model_config}` placeholder in the entry points above. The options are declared under
`user_options` in `MLproject` and their values are assembled from the four fork nodes above
this model by `../assemble_candidate_config.py` — so no option is set here, and every one of
them is a node in the claim tree with a sibling that would set it otherwise.

`hier_nb.IMPLEMENTED` lists the option values this code actually implements. A value from a
sibling that has not been built yet raises rather than falling through to the main path's
behaviour: a run that reported a zero-inflated model and fitted a plain one would be wrong
in a way nothing downstream could detect.

## Seeds

`train.py` draws nothing — Fisher scoring from a fixed start and a deterministic search, so
two fits on one frame give one file. All randomness is in `predict.py`, from a single NumPy
generator seeded with the `seed` option, which the assembling node derives from the project
seed 20260822 and writes into the configuration. Two runs are identical, and that is checked
rather than asserted by `AI-internal/useful-scripts/verify_model_determinism.sh`.

## Files

| File | What it is |
|---|---|
| `MLproject` | the contract: name, target, `user_options`, `uv_env`, entry points |
| `pyproject.toml`, `uv.lock` | the model's own pinned environment — numpy, pandas, pyyaml |
| `hier_nb.py` | the model: options, features, design, fit |
| `train.py` | entry point: fit once, write the fitted object as JSON |
| `predict.py` | entry point: apply the fit, write 1 000 draws per cell |
