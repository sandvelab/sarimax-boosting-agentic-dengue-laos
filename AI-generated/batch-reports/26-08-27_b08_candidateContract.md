# Batch 8 — the candidate contract, and candidate 1

Generated from [[26-08-22_dengueForecastingCase]] — iteration 8

**Phase C · Status: done — produced · Executed 2026-08-27**

---

The batch that gives the project a model of its own. `03_models/03_candidate` now exists as
the alternatives node holding the model families, with `a_hierNB` — a hierarchical
negative-binomial GLM — and one main-path child under each of its four configuration forks.
The model is written against the Chap contract, configured from a file the forks assemble,
seeded from the project seed, and evaluated through the same `chap eval` path as the
baselines and the reference.

It scores **26.100** mean CRPS. That is last of the four models the project has scored, and
worse than both required baselines.

Two things make that a more interesting result than a bad number. The same model has the
**best point forecast in the project** — mean absolute error 27.106, against the reference's
28.902 — so its centre is right and its width is wrong. And it is the first model whose gap
to the reference the evaluation can actually resolve: batch 7 measured the comparison's
resolution at about 4 CRPS using the baselines, and this candidate's paired difference of
4.00 CRPS carries a clustered standard error of **1.11**, less than half of theirs. The
resolution of the comparison turns out to depend on which model is being compared.

## 1. What the tree looks like now

```
03_models/
├── 01_baselines/         persistence · climatology            [batch 7]
├── 02_reference/         chapkit_ewars_model × 4              [batch 7]
└── 03_candidate/         [alternatives -> a_hierNB]           NEW
    └── a_hierNB/         [sub-analyses]  "…a hierarchical negative-binomial GLM"
        ├── 01_observation/  [alternatives -> a_negBinomial]
        ├── 02_covariates/   [alternatives -> a_lagged]
        ├── 03_population/   [alternatives -> a_offset]
        ├── 04_fitTime/      [alternatives -> a_trainOnly]
        └── scripts/         assemble_candidate_config.py · run_hier_nb.py
                             hier_nb_model/  ← the Chap model contract directory
```

Each fork holds only its main-path child, which is the narrow reading batch 7 settled: a
sibling that exists but cannot run would pass `/validate invariants` and advertise an
alternative nobody can execute. The seven unbuilt siblings — `b_zeroInflated`, `c_hurdle`,
`b_rich`, `c_climateFree`, `b_covariate`, `c_ignored`, `b_refitAtPredict` — are batch 9's,
and until they exist the model refuses their option values rather than quietly serving the
main path's behaviour. That refusal is in `hier_nb.IMPLEMENTED`, and it matters: a run that
reported a zero-inflated model and fitted a plain one would be wrong in a way nothing
downstream could detect.

`03_candidate` is an alternatives node with one child, so the switch it performs is not yet a
choice. `b_boosted` and `c_ensemble` are batches 10 and 11.

## 2. How configuration reaches an `MLproject` model

Open since batch 2, restated as unknown by batches 4 and 7, and unexercised because neither
baseline has any configuration — chap-core wrote each of them an empty
`model_configuration_for_run.yaml`. The route is chap-core's own, and it is a file at every
step:

1. `chap eval --model-configuration-yaml <file>` parses the file into a `ModelConfiguration`
   — two fields, `user_option_values` and `additional_continuous_covariates`, with extra
   fields forbidden;
2. chap-core writes it back out as `model_configuration_for_run.yaml` inside the run
   directory it creates for the model;
3. it substitutes that filename for the `{model_config}` placeholder in the `MLproject` entry
   points, which is how the model learns where its own configuration is;
4. the model reads it. Nothing about a run's configuration lives only in a command line.

What the model *declares* as configurable is the `user_options` block of its `MLproject` — a
JSON-schema-shaped dict. chap-core does not validate values against it, so the block is a
contract with the reader rather than with the platform, and the model validates its own
options on the way in.

**The values are assembled, not checked in.** `a_hierNB/scripts/assemble_candidate_config.py`
searches each of the four forks for the one child with results under this combination, merges
their option values, refuses a collision, and writes `model_configuration.yaml`. That is the
same mechanism `02_setup/scripts/assemble_setup.py` uses for the dataset, and for the same
reason: a configuration file checked in beside the model would be a fifth place where the
four forks' decisions are recorded, and the one the model actually read. Assembling it means
that changing which child of a fork runs changes the configuration, with no edit anywhere.

The route was confirmed against `chap-models/ewars_plus_template`, the clean
re-implementation of the reference family that batch 5 flagged and left unread. It declares
seven `user_options` and takes `{model_config}` in both entry points, which is the same
mechanism this model now uses.

## 3. The project seed gets a derivation

The candidate is the first component in this project with anything to seed. Both baselines
contain no randomness at all — their predictive distributions are empirical quantile
functions evaluated at fixed levels — so Rule 6 had been satisfied so far by there being
nothing to seed.

`analysis/scripts/lib/project_seed.py` reads the project seed from the settings table in
`readme-at-start.md` that declares it, and derives a component seed as

```
int(blake2b("<project_seed>:<component>", digest_size=8), 16) % 2**32
```

For `03_models/03_candidate/a_hierNB` that is **849 487 747**, from project seed 20260822.
Three properties were wanted and each is a deliberate choice. The number lives in **one**
place, so it cannot disagree with itself — the module raises rather than falling back to a
default if the table is ever reworded. The derivation is BLAKE2b rather than Python's `hash`,
which is salted per process and would give a different component seed on every run. And the
derived seed is written **into the configuration file**, so the number a model used sits
beside that model's results rather than in a script somewhere upstream.

`verify_model_determinism.sh` now reads the project seed through the same module instead of
carrying its own copy, and covers the candidate. Its report: **identical**, for all three of
our models.

## 4. The model

Monthly province counts as negative-binomial draws around a log-linear mean:

```
log mean[i,t] = log(population[i])                    offset          (03_population/a_offset)
              + global level
              + shared annual season, two harmonics
              + standardised rainfall and mean temperature at lag 2   (02_covariates/a_lagged)
              + province effect       u[i]        ~ pooled, sigma_u
              + province-year effect  v[i,year]   ~ pooled, sigma_v
```

`u` and `v` are the hierarchy: each is penalised toward zero by a variance the fit estimates,
so a province with a thin record is pulled toward the country's common level and one with
twelve full years is not. That is what carries 194 parameters on 1 978 observations.

**`v` is also where the forecast gets its width.** A forecast month lies in a year the fit
never saw, so its year effect cannot be estimated and is drawn from its estimated
distribution instead — once per province-year per sample, so the three months of a split move
together within a draw. How much annual dengue activity varies around a province's own
average therefore enters every forecast as uncertainty rather than being set to zero. The
reference model carries a per-district, per-year effect for the same reason, and batch 7
found both baselines badly under-dispersed at 0.65 coverage against a nominal 0.80.

Fitted by empirical Bayes: Fisher scoring for the coefficients given the variances, EM
updates for the variances (fitted effects **plus their posterior variances**, which is what
stops the estimate collapsing toward zero), a one-dimensional search on the profile
likelihood for the dispersion, repeated until nothing moves. The posterior is then the
Laplace approximation, and forecast draws come from it, from the prior on `v`, and from the
negative binomial on top of both.

Three pinned dependencies — numpy, pandas, pyyaml — on CPython 3.13.0, from a `uv.lock` that
travels with the model. No sampler, no compiler, no statistics package. The fit takes about
two seconds.

**What it found** (`results/main/fitted_model.json`): between-province spread on the
log-incidence scale **sigma 2.06**, between-year spread within a province **sigma 1.47**,
dispersion **0.83**, converged in 24 EM rounds on 1 978 usable rows over 17 provinces and 168
province-years. The 1 978 is 2 040 minus the 62 rows whose two-month covariate lag falls
before the record starts — dropped at fit time rather than imputed.

The climate coefficients are small: **−0.111** for standardised lagged rainfall and **+0.083**
for standardised lagged mean temperature, against seasonal terms of −1.48 and −0.71. Whatever
this model knows about the annual cycle, it knows from the calendar rather than from the
weather. That is the first evidence bearing on `c_climateFree`, the sibling whose whole point
is to ask whether the covariates are decoration.

## 5. What it scored

The leaderboard, `04_score/03_compare/results/main/leaderboard.csv`, repeat-mean rows only:

| model | mean CRPS | MAE | 10–90 coverage | 25–75 coverage | cost |
|---|---|---|---|---|---|
| reference (mean of 4) | **22.098** | 28.902 | 0.804 | 0.602 | 1 070 s |
| climatology | 24.337 | 30.620 | 0.650 | 0.542 | 28 s |
| persistence | 24.879 | 29.073 | 0.666 | 0.491 | 31 s |
| **hier_nb** | **26.100** | **27.106** | **0.720** | **0.590** | **43 s** |

Last on the metric the project is scored by, first on the metric that scores only the point
forecast, and the closest of our models to both nominal interval levels.
`fig_accuracy_and_spread.png` is that in one image.

**Where the CRPS goes.** Two provinces carry 2.4 of the 4.0 CRPS gap to the reference
(`crps_by_location.csv`):

| province | hier_nb CRPS | reference CRPS | hier_nb 10–90 coverage | observed cases |
|---|---|---|---|---|
| Vientiane Capital (LA-VT) | 111.60 | 92.81 | **1.000** | 3 707 |
| Salavan (LA-SL) | 57.45 | 38.44 | **0.125** | 1 455 |
| Luang Prabang (LA-LP) | 41.58 | 47.39 | 0.583 | 1 336 |

An interval that covers *every* outcome is far too wide; one that covers an eighth of them is
far too narrow. Both come from the same feature: the province-year variance is a single
number shared by all provinces, which on the log scale is a constant *multiplicative* width —
too much for the province with the largest burden and too little for the one whose epidemic
years are sharpest. **The aggregate coverage of 0.720 sits between two failures and describes
neither.** That is the finding batch 9 has to answer, and it is why the plan's instruction to
report calibration beside CRPS is not on its own enough to diagnose a model.

**By lead time**, the candidate is level with climatology at one month (22.88 against 22.31)
and loses ground at three (29.81 against 26.97). The reference's own profile is 16.54 / 21.97
/ 27.79. Nothing our models do at one month's lead is competitive with the reference except
persistence, which batch 7 already found.

## 6. The comparison is much tighter against this model than against the baselines

Batch 7's headline methodological finding was that the development backtest resolves about
**4 CRPS**, wider than the whole corridor from persistence to the reference. That figure was
measured with the two baselines. The candidate changes it:

| model vs reference | mean diff | sd of per-cell diff | se clustered by split | diff / se |
|---|---|---|---|---|
| climatology | 2.238 | 25.74 | 1.919 | 1.17 |
| persistence | 2.781 | 39.40 | 2.985 | 0.93 |
| **hier_nb** | **4.002** | **18.11** | **1.105** | **3.62** |

The candidate's per-cell differences against the reference are **half as variable** as
persistence's, because the two models are structurally alike — both are seasonal regressions
on the same covariates with a per-province-per-year term — so they fail on the same cells and
the paired difference cancels most of the difficulty. The result is that this is the first
comparison in the project that clears two standard errors, and what it says is that **our
candidate is worse than the reference**, on 235 of 371 cells and on 7 of 8 splits.

That is worth stating carefully, because it cuts both ways. The evaluation's resolution is
not a property of the dataset alone, as batch 7's single figure implied: it is a property of
the pair being compared, and it is better for a candidate that resembles the reference than
for one that does not. A candidate built to be structurally unlike the reference would be
compared less tightly and would need a larger margin to be distinguishable. That is a
consideration for how phase C's candidates are chosen, and it was not visible before this
batch.

## 7. The conclusion moved, correctly, in the wrong direction

`analysis/results/main/conclusion.json` now reports `candidate_exists: true` and takes its
headline from the main path through `03_models/03_candidate` rather than from the
best-scoring baseline standing in. So the project's skill score against the reference went
from **−0.101** to **−0.181**.

That is the machinery working. The conclusion is defined as what our *candidate* does, not as
what our best model does, and `conclude.py` was written in batch 7 to resolve that from the
tree rather than by picking a winner. A version that reported the best of our models would
have kept the number at −0.101 and hidden the fact that the candidate the project is actually
developing is behind its own baselines.

## 8. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| Configuration reaches the model through an assembled file, not a checked-in one | The forks are then the only source of what the model is; a checked-in file would be a fifth record of their decisions and the one that actually ran | agent-autonomous |
| The component seed is BLAKE2b of `"<project seed>:<component>"`, read from `readme-at-start.md` | One seed, derived downward, with no second copy that could disagree; `hash` is salted per process and would not be stable | agent-autonomous |
| Rainfall and mean temperature at lag 2 as the default covariate set | It is the reference family's own published configuration for this country (`laos_eval_config.yaml` in `chap-models/ewars_plus_template`), so the candidate's first configuration is a comparable one rather than a differently-tuned one | agent-on-human-assessment; the configuration was `agent-retrieved` |
| **No autoregressive term on lagged counts**, although lag 3 is available at every horizon | It is a structural choice no fork of this node covers, and adding it silently would be exactly the judgment call the project exists to make visible. Proposed to batch 9 as a fifth fork instead | agent-autonomous |
| Two harmonics; Laplace approximation rather than a sampler; the province-year effect drawn from its prior at forecast time | Model-internal choices, each stated in `hier_nb_model/README.md` with what it gives up | agent-autonomous |
| **The reference was not re-run in this batch** | It is unseeded, so re-running replaces batch 7's four repeats with a different draw and moves the denominator of every conclusion. All models were scored on the same 371 cells of the same dataset — verified by comparing `dataset_sha256` across the specs — which is what makes the comparison paired. Re-running it would confound "the candidate scored this" with "the reference drew differently" | agent-autonomous |
| The `crossing` invariant's separator narrowed from any whitespace to spaces and tabs | `\s` matches newlines, so the pattern was matching a constant followed by a blank line and an unrelated paragraph. The check's docstring says "a comment naming another step", meaning a trailing comment; the fix restores the documented meaning and nothing that was a finding before stops being one | agent-autonomous |
| Phase C's 0.4 CRPS stopping rule is **not** triggered by this batch | Its operative sentence is "adding a further *candidate* batch requires that the last one moved it by more". Batch 9 is candidate 1's internal forks, not a further candidate. Batch 10's admissibility depends on what batch 9 moves. The rule is applied as written and not adjusted — see §12 | agent-autonomous |

## 9. Compliance for this batch

- **Rule 1** — every number in this report is read from a file an executed script wrote. Seven
  provenance records: four fork children, the assembler, the model run, the new figure.
- **Rule 2** — nothing produced was edited. One defect was fixed at the source and the step
  re-executed: `run_hier_nb.py` looked for the shared library two directories too far up,
  which failed loudly rather than silently.
- **Rule 3** — the model ships its own `pyproject.toml` and `uv.lock`, and the runner verified
  after the run that the lockfile chap-core built from is byte-identical to the tracked one.
- **Rule 4** — two commits bracketing the run, and the analysis re-run from the committed
  state reproduced every figure exactly. `check_invariants.py` changed and the commit says so
  in those terms; `AGENTS.md` and `.claude/` did not.
- **Rule 5** — the fitted object as JSON, not a pickle: both variance components, the
  dispersion, every coefficient, the Cholesky factor the forecasts are drawn from, and the EM
  history. Plus the four option specifications, the assembled configuration, the model
  specification and the run cost.
- **Rule 6** — the project's first seeded component, and the first whose Rule 6 claim is
  "seeded" rather than "nothing to seed". Verified by running the model twice under scratch
  combinations and diffing: identical per-cell scores and an identical fitted object.
- **Rule 7** — one new figure with its plotted values, its pre-aggregation values and its
  script; the two existing figures regenerated with the candidate in them.
- **Rule 8, 9, 10** — no surface here; batches 17 and 19 give them one.
- **`/annotate-criticality`** — appended to `03_models/criticality.md` and
  `04_score/criticality.md` rather than folded into the batch-7 tables, because what an
  earlier batch judged is part of the record.
- **`/validate invariants`** — passes: tree, provenance, plots, seeds, claims, git, crossing.

## 10. What went wrong, kept

**The candidate is worse than the baselines it was meant to beat.** That is the batch's
result, not a failure of the batch, and it stays in the record with the diagnosis in §5.

**`run_hier_nb.py` computed the wrong path to the shared library.** The persistence runner
sits three levels below `03_models` and this one sits two, and the parent index was copied
across. It failed with `ModuleNotFoundError` on the first run — the good kind of failure. It
is worth noting only because the same copied index would have been silent if it had happened
to resolve to a directory that existed.

**`/validate invariants` reported a false positive and the check was changed, not the code.**
`HARMONICS = 2` in the model was flagged as a value that may have crossed a step by hand,
because the pattern's whitespace class matched across the blank line to a paragraph of prose
two lines below. The rule is to fix the cause and never weaken the check; the cause here was
in the check, whose own docstring says it looks for a *trailing* comment. The separator was
narrowed to spaces and tabs, which is what "trailing" means, and no previously-caught pattern
stops being caught. Recorded here because "we changed the check" is a sentence that should
never appear without its argument.

## 11. What is still unknown

1. **Whether the width problem is in the model or in the approximation.** The province-year
   variance being a single shared number is the obvious suspect, and it is a structural fix.
   The Laplace approximation's symmetry on the log scale is the other, and it is a
   dependency-heavy fix. Batch 9 can distinguish them cheaply by making the year variance
   province-scaled and seeing whether Vientiane's coverage falls off 1.000.
2. **Whether an autoregressive term is what this model is missing.** No fork covers it, and
   at one month's lead the persistence baseline is still level with the reference, which says
   there is information in the last observed count that neither our candidate nor the
   reference uses. Proposed as a fifth fork.
3. **Whether a gradient-boosted model can be given a calibrated probabilistic head on this
   data.** Batch 10's, unchanged.
4. **Whether the headline weighting fork flips the ranking.** Batch 7 raised it; the candidate
   sharpens it, since it does worst in the two highest-burden provinces. Batch 12's, and it
   costs seconds.
5. **What the reference actually costs on a quiet machine.** Batch 7's figure is contaminated
   by machine load; this batch did not re-run it, so it is still open for batch 12.

## 12. For the human

- **The project has a candidate and it is behind its own baselines.** Mean CRPS 26.10 against
  climatology's 24.34. The reported skill score against the reference is now −0.181, worse
  than the −0.101 the placeholder showed, and that is the machinery working rather than a
  regression.
- **The same model has the best point forecast in the project**, better than the field's own
  model on mean absolute error. The problem is entirely in the width of its predictive
  distribution, and the width is wrong in opposite directions in different provinces. That is
  a diagnosable defect with a cheap test, which is a better position than a model that is
  uniformly mediocre.
- **The evaluation is sharper than batch 7 suggested — for models that resemble the
  reference.** The candidate's gap to the reference clears two standard errors comfortably.
  Batch 7's "the backtest resolves about 4 CRPS" needs the qualification that resolution
  depends on the pair, and a candidate built to be structurally unlike the reference will be
  harder to distinguish from it, not easier.
- **One question for you, on the stopping rule.** The rule fixed in batch 5 says phase C ends
  when the leaderboard's best moves by less than 0.4 CRPS in a batch. This batch moved the
  best of our models by **zero**. Applied as written the rule bears on *further candidate
  batches*, so batch 9 — candidate 1's internal forks — proceeds and batch 10's admissibility
  depends on what batch 9 moves. I have not adjusted the rule, and I am not proposing to.
  But it was written before anyone knew that a batch could add a model and move the best by
  nothing, and you may want to say whether "the leaderboard's best" was meant to be the best
  of ours or the best candidate. They are different numbers now.
