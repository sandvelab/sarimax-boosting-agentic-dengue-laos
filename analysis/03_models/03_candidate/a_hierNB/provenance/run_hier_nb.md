# Provenance — candidate 1, the hierarchical negative-binomial GLM, evaluated

```
result:              results/main/eval.nc
                     results/main/eval.log
                     results/main/model_spec.json
                     results/main/run_cost.json
                     results/main/fitted_model.json
script:              scripts/run_hier_nb.py
                     sha256:f6f6a96aefe64e6dba05a5b3e7f9c98667f4935eb514bbc1824aed575e7b420b
                     analysis/03_models/scripts/lib/chap_eval.py
                     sha256:028835c823eacb999ea60125be3a871b2c4c58985538574d7afa8b61525df21a
                     the model itself, scripts/hier_nb_model/:
                     MLproject       sha256:aaa3bb10be0325fb…
                     hier_nb.py      sha256:94300ffe80f98789…
                     train.py        sha256:656dc6551056cc60…
                     predict.py      sha256:7b84349d2728a2a3…
                     uv.lock         sha256:a5a6840b752fc538…
                     (the full digests are in results/main/model_spec.json, written by
                     the run before it started)
invocation:          "$PYTHON" scripts/run_hier_nb.py
                     which issues
                     environment/chapenv/bin/chap eval
                       --model-name <node>/scripts/hier_nb_model
                       --dataset-csv analysis/02_setup/results/main/analysis_dataset.csv
                       --output-file results/main/eval.nc
                       --backtest-params.n-periods 3 --backtest-params.n-splits 8
                       --backtest-params.stride 3 --backtest-params.n-retrain 1
                       --model-configuration-yaml results/main/model_configuration.yaml
                     with every flag read from the assembled setup and every option from
                     the assembled configuration, neither chosen by this script. The
                     exact command line is the first line of results/main/eval.log.
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     analysis/02_setup/results/main/setup_spec.json (the flags)
                     results/main/model_configuration.yaml (the options and the seed)
                     sha256:ddfa21a670e4… (full digest in model_spec.json)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     for the platform. The *model* runs in its own environment, which
                     chap-core builds from the model's pyproject.toml and uv.lock —
                     numpy 2.5.2, pandas 3.0.5, pyyaml 6.0.3 on CPython 3.13.0. The
                     runner verifies after the run that the lockfile chap-core built
                     from is byte-identical to the tracked one and records it as
                     `shipped_lockfile_is_the_one_built_from`, which was true.
seeds:               project seed 20260822 → component seed 849487747 for
                     03_models/03_candidate/a_hierNB, derived and recorded by
                     scripts/assemble_candidate_config.py and carried into the model
                     inside model_configuration.yaml. One NumPy generator in predict.py
                     serves all three sources of randomness — the Laplace posterior of
                     the coefficients, the prior draw of the province-year effect, and
                     the negative-binomial observation draw. The fit itself is
                     deterministic. Verified rather than asserted: two independent runs
                     under scratch combinations produce identical per-cell scores and an
                     identical fitted object
                     (AI-generated/determinism-checks/model_determinism.json).
commit:              4563baf
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB
produced:            2026-08-27
```

**What it establishes.** The project's first candidate scores a development mean CRPS of
**26.100** over the same 371 cells as everything else, against 24.337 for climatology, 24.879
for persistence and 22.098 for the reference. It is **last on the headline metric and first
on mean absolute error** — 27.106, better than the reference's 28.902 — and it has the best
interval coverage of any model of ours, 0.720 at 10–90 against a nominal 0.80. The fit took
about two seconds; the eight-split backtest 43 seconds, 5.3 per split.

**What the fitted object records.** Between-province spread on the log-incidence scale
sigma 2.06, between-year spread within a province sigma 1.47, negative-binomial dispersion
0.83, converged in 24 EM rounds on 1 978 usable rows over 17 provinces and 168
province-years. The 1 978 is 2 040 minus the 62 rows whose two-month covariate lag falls
before the record starts, dropped rather than imputed at fit time.

**Where the CRPS goes.** Two provinces carry 2.4 of the 4.0 CRPS by which the candidate
trails the reference: Vientiane Capital, where its 10–90 interval covers **every** outcome
and so is far too wide, and Salavan, where it covers **0.125** and so is far too narrow. The
province-year variance is one number shared by every province, and on the log scale that is
a constant multiplicative width — which is too much for the province with 3 707 observed
cases and too little for the one whose epidemic years are sharper than its variance implies.
That is a structural finding about this configuration, and it is what batch 9's forks have to
answer.

**Cost.** 43 seconds for the full eight-split backtest (`results/main/run_cost.json`),
against 28 for each baseline and about 18 minutes for the reference's four repeats. Batch 5's
manifest estimate for a real candidate was 120 seconds; the measured figure is a third of
that, which batch 12 should carry rather than the estimate.

alternatives-considered: a Bayesian sampler (PyMC or NumPyro) instead of the Laplace
approximation, which would drop the symmetry assumption and add a large dependency with a
compiler in it; rejected for the defaults, and it is the natural sibling if the width problem
above turns out to be in the approximation rather than in the model. An autoregressive term
on lagged counts, which no fork of this node covers and which would give the model
information about the current epidemic that a seasonal-plus-climate regression cannot have;
**not taken**, because adding a structural term outside the four forks would be a silent
judgment call, and it is proposed to batch 9 as a fifth fork instead. Estimating the variance
components by MCMC or REML rather than by the EM update; rejected as a difference the fits
here are too small to feel.

agency: agent-autonomous. The candidate family is batch 4's shortlist and batch 5's design
(`human-set` at the level of "several candidates from the shortlist"); every choice inside
the model — the two harmonics, the Laplace approximation, the province-year prior draw, the
EM update — is this batch's, and each is stated in scripts/hier_nb_model/README.md.
