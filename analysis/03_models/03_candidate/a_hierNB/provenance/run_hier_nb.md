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

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

```
result:              results/main/eval.nc · eval.log · model_spec.json · run_cost.json
                     results/main/fitted_model.json
                     autoregressive_lag3/eval.nc
                     autoregressive_lag3/eval.log
                     autoregressive_lag3/model_spec.json
                     autoregressive_lag3/run_cost.json
                     autoregressive_lag3/fitted_model.json
                     covariates_lagged/eval.nc
                     covariates_lagged/eval.log
                     covariates_lagged/model_spec.json
                     covariates_lagged/run_cost.json
                     covariates_lagged/fitted_model.json
                     covariates_rich/eval.nc
                     covariates_rich/eval.log
                     covariates_rich/model_spec.json
                     covariates_rich/run_cost.json
                     covariates_rich/fitted_model.json
                     fitTime_refitAtPredict/eval.nc
                     fitTime_refitAtPredict/eval.log
                     fitTime_refitAtPredict/model_spec.json
                     fitTime_refitAtPredict/run_cost.json
                     fitTime_refitAtPredict/fitted_model.json
                     observation_negBinomial/eval.nc
                     observation_negBinomial/eval.log
                     observation_negBinomial/model_spec.json
                     observation_negBinomial/run_cost.json
                     observation_negBinomial/fitted_model.json
                     observation_zeroInflated/eval.nc
                     observation_zeroInflated/eval.log
                     observation_zeroInflated/model_spec.json
                     observation_zeroInflated/run_cost.json
                     observation_zeroInflated/fitted_model.json
                     population_covariate/eval.nc
                     population_covariate/eval.log
                     population_covariate/model_spec.json
                     population_covariate/run_cost.json
                     population_covariate/fitted_model.json
                     population_ignored/eval.nc
                     population_ignored/eval.log
                     population_ignored/model_spec.json
                     population_ignored/run_cost.json
                     population_ignored/fitted_model.json
                     yearVariance_shared/eval.nc
                     yearVariance_shared/eval.log
                     yearVariance_shared/model_spec.json
                     yearVariance_shared/run_cost.json
                     yearVariance_shared/fitted_model.json
script:              scripts/run_hier_nb.py   (unchanged)
                     scripts/hier_nb_model/hier_nb.py   sha256:5bdb59a5b3986d68dec84d66afd1e199a927acf4829f7807be4d759bcdea35be
                     scripts/hier_nb_model/train.py     sha256:1f53ccdb593e62f044c4358e7555fc6b2ba5eb58258eda75853b710529276f0f
                     scripts/hier_nb_model/predict.py   sha256:1cdb6ce0e971bbb3f3a86a4d60e3b52ab93eab300b316736cd1af007c6cd3135
                     scripts/hier_nb_model/MLproject    sha256:38964b3208a2662a13ff832357310794aa5ac778d4cf7d75080447e389ccdde3
                     (full digests per combination in each results/<combo>/model_spec.json)
```

**What the model gained.** Code for all six options: a zero-inflation EM step, a two-part
hurdle whose presence block is a penalised logistic fit on the same design, covariates at
several lags, a lagged-count column, a refit inside `predict`, and a province-year variance
estimated per province. `fit_model` and `draw` are new, and they are what let `train` and
`predict` share one fit rather than two implementations of it -- which is what
`b_refitAtPredict` needs to exist at all.

**The rewrite changed nothing on the main path.** Re-running the batch-8 configuration
after it reproduced `04_score/01_collect/results/main/metrics_cell.csv` byte for byte,
which is a stronger check than the tests that would have been written instead.

**What the promoted main path scores.** Mean CRPS **23.698** over the same 371 cells,
against 24.337 for climatology, 24.879 for persistence and 22.098 for the reference. It is
the first model of ours to beat both required baselines. Mean absolute error **27.569**,
the best in the project; 10–90 coverage **0.701** against a nominal 0.80, so it is still
under-dispersed. 36 seconds for the eight-split backtest.

**Every combination was scored on the same data.** `dataset_sha256` is
`c9bf8b0849c7…` in all ten `model_spec.json` files, which is what makes the comparison
paired and is checked rather than assumed.

**The fit does not converge under `year_variance: province_scaled`.** Every combination
carrying that child runs to the 200-round cap; `yearVariance_shared` converges in 48. The
convergence test is a maximum over the relative movement of all seventeen variances, and
the smallest of them keep it above tolerance long after the parameters have stopped moving:
`sigma_province` is 1.265204 at round 197 and 1.265199 at round 200, and the log-likelihood
moves in its sixth significant figure. The tolerance was **not** relaxed -- a criterion
adjusted after seeing a run is a criterion adjusted to pass.

**Rule 6, verified rather than asserted.** Two independent runs of every model of ours
under scratch combinations produced identical per-cell scores and identical fitted objects,
the promoted hurdle candidate included
(`AI-generated/determinism-checks/model_determinism.json`, status `identical`).

alternatives-considered: a zero-truncated negative binomial for the hurdle's positive part
instead of the shifted one; rejected for the cost of a score function this module does not
have, and recorded because it is the obvious next version. Fitting the presence block with
the population offset rather than an estimated log-population coefficient; rejected because
an offset is a statement on the log-mean scale and has no meaning on the logit scale.
Raising the outer-round cap above 200 so the province-scaled fits converge; not taken,
because the parameters are already stable to six figures and the cap is the honest record
of where the procedure stopped.

agency: agent-autonomous.

---

## Batch 11 — candidate 1 under its own combination, `family_hierNB`

```
result:              family_hierNB/candidate_spec.json
                     family_hierNB/eval.log
                     family_hierNB/eval.nc
                     family_hierNB/fitted_model.json
                     family_hierNB/model_configuration.yaml
                     family_hierNB/model_spec.json
                     family_hierNB/run_cost.json
script:              scripts/run_hier_nb.py
                     sha256:f6f6a96aefe64e6dba05a5b3e7f9c98667f4935eb514bbc1824aed575e7b420b
invocation:          bash analysis/03_models/03_candidate/a_hierNB/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB
produced:            2026-08-28
```

**What it establishes.** That the demotion cost nothing. Batch 11 promoted the family fork to
`c_ensemble`, so candidate 1 stops being the model `analysis/run.sh` produces and moves to a
combination of its own — the same arrangement candidate 2 has had since batch 10. Run there,
it produces **per-cell scores identical to the ones it produced as the main path**: mean CRPS
23.698, MAE 27.569, 10–90 coverage 0.701, and `metrics_cell.csv` restricted to this model
diffs clean against the file `main` held before the promotion.

**Why the results it produced as the main path were removed rather than kept.** They described
a main path that no longer exists, and `04_score/01_collect` discovers models by the fact of
having run — a `model_spec.json` under `main` would have put a row on the reported leaderboard
that `analysis/run.sh` does not produce. Batch 9 removed the demoted fork children's
`results/main/` for the same reason and this follows it. Git holds them at commit `4cdfd16`.

**What did not move.** The component seed is still **849487747** and the configuration is the
one batch 9 promoted; only the combination the results are filed under changed. The
`model_configuration.yaml` under `family_hierNB` is byte-identical to the one that was under
`main`.

alternatives-considered: renaming the `main` result directory to `family_hierNB` rather than
re-running (rejected — every file in it records `"combo": "main"` internally, so the rename
would leave a directory whose name contradicts its contents, which is batch 9's stated reason
for removing rather than renaming); leaving the results under `main` (rejected — see above);
not giving candidate 1 a combination at all until phase D (rejected — the pool's check
reconstructs itself from its members' own evaluations, and candidate 1 is a member).
agency: agent-autonomous

---

## Batch 14 — candidate 1 as the family a combination runs

```
result:              results/$COMBO/eval.nc
                     results/$COMBO/eval.log
                     results/$COMBO/model_spec.json
                     results/$COMBO/run_cost.json
                     results/$COMBO/fitted_model.json
                     results/$COMBO/model_configuration.yaml
                     results/$COMBO/candidate_spec.json
combinations:        family_hierNB (re-run), provinces_reportingOnly__family_hierNB,
                     provinces_mergeVientiane__family_hierNB,
                     family_hierNB__aggregate_caseWeighted
script:              scripts/run_hier_nb.py
                     sha256:f6f6a96aefe64e6dba05a5b3e7f9c98667f4935eb514bbc1824aed575e7b420b
                     (unchanged; the batch changed this node's assembler, not its runner)
invocation:          bash analysis/03_models/03_candidate/a_hierNB/run.sh, with COMBO set
                     by analysis/05_stability/scripts/run_manifest.py and COMBO_BASE=main
inputs:              analysis/02_setup/results/$COMBO/analysis_dataset.csv and
                     setup_spec.json, resolved under the combination or its base
                     results/$COMBO/model_configuration.yaml (the options and the seed)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               component seed 849487747, derived from project seed 20260822 from
                     this node's path; unchanged
commit:              3fb1280 (family_hierNB), ba3cf8d (the three pairs)
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB
produced:            2026-08-30
```

**What it establishes.** Candidate 1's score on the four combinations that run it as the
family, which is the largest single-fork move in the whole stability set. Under
`family_hierNB` it is **23.698 CRPS against the reference's 22.098** — identical to batch
11's re-run of the demoted family, which is a determinism check nobody had to design — for a
skill score of −0.0724 and `beats_reference: false`. Its 10–90 coverage is 0.701 against a
nominal 0.80: candidate 1 is the under-dispersed end of the project's models, the pool the
over-dispersed end.

Paired with the two province rows it moves very little — 23.602 and 23.656 — and paired with
case weighting it goes to 112.258 with 10–90 coverage **0.458**, the worst calibration any
row of this project has recorded. Under case weighting the outbreak months carry the mean,
and candidate 1's intervals are far too narrow there.

alternatives-considered: none new at this node; its configuration is batch 9's promoted one
and this batch did not touch it.

agency: agent-autonomous.
