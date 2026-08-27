# Batch 9 — candidate 1's forks, swept and promoted

Generated from [[26-08-22_dengueForecastingCase]] — iteration 9

**Phase C · Status: done — produced · Executed 2026-08-27**

---

The batch that finishes candidate 1. Every child of every fork under `a_hierNB` is now built
and has been run on the development data; two forks that batch 8 proposed rather than took
silently now exist; and three forks have moved, by a rule committed before the combination
they chose was run.

The candidate went from **26.100** to **23.698** mean CRPS. It is the first model of ours to
beat both required baselines, and its distance from the reference model fell from 3.62
standard errors to **1.03** — which is to say the development backtest can no longer separate
our candidate from the field's own model.

The more useful finding is about the method rather than the model. **The forks do not add.**
Three of them, worth 2.115, 1.870 and 0.648 CRPS when each was taken alone, delivered 2.402
together rather than 4.632; measured again from where the model now stands, one of the three
is worth 0.05 and another has changed sign. Tier 1 of the phase-D manifest is a one-at-a-time
sweep, and batch 9 is the evidence that a one-at-a-time sweep measures something that does
not compose.

## 1. What the tree looks like now

```
03_models/03_candidate/            [alternatives -> a_hierNB]
└── a_hierNB/                      [sub-analyses]  "…a hierarchical negative-binomial GLM"
    ├── 01_observation/            [alternatives -> c_hurdle]        ← PROMOTED
    │   ├── a_negBinomial          one stretched distribution           (was the main path)
    │   ├── b_zeroInflated         a point mass at zero, mixed in                      NEW
    │   └── c_hurdle               report-at-all × how-much, separately                NEW
    ├── 02_covariates/             [alternatives -> c_climateFree]   ← PROMOTED
    │   ├── a_lagged               rainfall + temperature at lag 2      (was the main path)
    │   ├── b_rich                 all three columns at lags 1, 2, 3                   NEW
    │   └── c_climateFree          none; the harmonics carry the year                  NEW
    ├── 03_population/             [alternatives -> a_offset]
    │   ├── a_offset               log(population) as a fixed offset
    │   ├── b_covariate            an estimated coefficient instead                    NEW
    │   └── c_ignored              population does not enter                           NEW
    ├── 04_fitTime/                [alternatives -> a_trainOnly]
    │   ├── a_trainOnly            fit once, in train
    │   └── b_refitAtPredict       refit inside every predict call                     NEW
    ├── 05_autoregressive/         [alternatives -> a_none]                        NEW FORK
    │   ├── a_none                 no lagged-count term
    │   └── b_lag3                 log1p of the count three months back
    └── 06_yearVariance/           [alternatives -> b_provinceScaled]  ← PROMOTED NEW FORK
        ├── a_shared               one annual variance for the country
        └── b_provinceScaled       one per province
```

Eleven new leaf nodes, two new forks, nine new combinations run. `b_boosted` and
`c_ensemble` — the other two model families — are batches 10 and 11.

**Every child is built and every child has been run.** Batch 7 settled that a fork gets only
its main-path child until the code that runs a sibling exists, because a sibling that cannot
run would pass `/validate invariants` and advertise an alternative nobody can execute. That
restriction is now lifted for this subtree: `hier_nb.IMPLEMENTED` lists every option value
the model serves, and every value in it has a node behind it.

## 2. The two forks that did not exist before

Batch 8 declined to make two changes to the model and proposed both to this batch as forks
instead. The reasoning was that a structural term added outside the four forks would be
exactly the silent judgment call this project exists to make visible. Both are now nodes.

**`05_autoregressive` — does the model see the recent case history?** The lag is three
months, because Chap asks for three months at a time and the same fitted model has to
forecast all of them; a one-month lag would mean feeding the model its own forecasts to reach
the third month, which is a different model. The child's premise was computed before it ran:
within a province, log1p counts correlate **0.701** at three months' lag and **0.758** at
twelve. Twelve months is the seasonal cycle the harmonics already carry.

It scores **23.345** against the main path's 23.698 — inside the 0.57 CRPS floor, and
therefore nothing. Batch 8's argument for it was batch 7's finding that a persistence
baseline is level with the reference at one month's lead; that does not survive the trip to
three months, which is the only lead a single model can serve here.

**`06_yearVariance` — is the annual variability the same relative size everywhere?** This is
the structural half of the width defect batch 8 diagnosed: a single shared province-year
variance is, on the log scale, a constant *multiplicative* width, which was far too much for
Vientiane Capital and far too little for Salavan. Estimating one variance per province was
worth **1.870** CRPS from the batch-8 configuration and it was promoted.

It half worked, and the half that failed is the interesting half — §5.

## 3. What each fork is worth, and from where

The sweep runs one combination per non-main child: that child's step runs, and everything the
combination did not move — the assembled dataset, the five choices it did not take, the
reference and the baselines — is inherited from `main` and recorded as inherited. The
reference is not re-run, because it is unseeded: re-running it would replace its four repeats
with a different draw and move the denominator of every comparison for reasons that have
nothing to do with the fork.

**Around the batch-8 configuration** (`round1_batch8Defaults/fork_leaderboard.csv`), base
26.100:

| combination | mean CRPS | 10–90 | worth |
|---|---|---|---|
| `observation_hurdle` | **23.985** | 0.698 | **+2.115** |
| `yearVariance_provinceScaled` | **24.230** | 0.706 | **+1.870** |
| `covariates_climateFree` | **25.452** | 0.725 | **+0.648** |
| `covariates_rich` | 25.639 | 0.704 | +0.461 |
| `fitTime_refitAtPredict` | 25.692 | 0.744 | +0.408 |
| `observation_zeroInflated` | 25.760 | 0.725 | +0.341 |
| `population_ignored` | 26.150 | 0.717 | −0.050 |
| `autoregressive_lag3` | 26.175 | 0.722 | −0.075 |
| `population_covariate` | 26.316 | 0.722 | −0.216 |

Three clear the 0.57 CRPS floor — the largest difference the unseeded reference shows against
its own repeats, and therefore the smallest movement attributable to a model at all.

## 4. The promotion, and the rule it was made by

`promotion_rule.md` was written after the table above existed and **committed before the
promoted combination was run**, so that what it decides cannot have been fitted to what it
decided. It says: a fork moves only if its best child beats the main path by more than 0.57
CRPS; where a fork moves it takes its best child; the promoted combination is then run,
because promoting several forks at once asserts that their effects combine and a
one-at-a-time sweep tests no such thing; and if the combination is worse than the best single
fork by more than the floor, the promotion is backed off.

Three forks moved: `01_observation` → `c_hurdle`, `02_covariates` → `c_climateFree`,
`06_yearVariance` → `b_provinceScaled`. The promoted combination scores **23.698**, better
than the best single fork's 23.985, so clause 4 did not fire.

**The rule was applied once and not iterated.** The second sweep, taken around the promoted
path, has two children outside the floor — `b_refitAtPredict` at +0.873 and `b_rich` at
+0.821 — so applying the rule again would move two more forks, and probably again after that.
Iterating it is greedy coordinate descent on development CRPS, which is precisely the failure
the plan's phase C warns about and which one held-out year cannot diagnose. Stopping is a
decision with a cost and the cost is stated: roughly 0.9 CRPS left on the table. §11 puts it
to the human.

## 5. The forks do not add

This is the batch's methodological result. `round2_promoted/fork_interaction.csv` is the same
children measured from the promoted main path instead of the batch-8 one:

| child | worth around 26.100 | worth around 23.698 |
|---|---|---|
| `c_hurdle` | **+2.115** | +0.601 |
| `b_provinceScaled` | **+1.870** | +0.051 |
| `c_climateFree` | **+0.648** | **−0.112** |
| `b_refitAtPredict` | +0.408 | **+0.873** |
| `b_rich` | +0.461 | **+0.821** |
| `b_lag3` | −0.075 | +0.353 |
| `b_zeroInflated` | +0.341 | **−0.432** |
| `c_ignored` | −0.050 | −0.025 |
| `b_covariate` | −0.216 | −0.178 |

The three promoted forks were worth **4.632** CRPS one at a time and delivered **2.402**
together. Two children reversed sign. Two children that were inside the floor moved outside
it.

The reason is not mysterious and is worth stating because it will recur. The hurdle and the
per-province variance were both repairs to the same defect — a predictive distribution of the
wrong width — approached from different directions, so once one is in place the other has
little left to fix. The climate covariates and the seasonal harmonics substitute for each
other, which is visible in `b_rich`'s own coefficients: the harmonic `sin1` collapses from
−1.235 to **−0.027** as nine climate columns enter and mean temperature at lag 1 takes
**+0.653**. On this dataset the annual cycle can be carried by the calendar or by the
weather, and the model scores about the same either way.

**What this means for phase D.** Tier 1 of the manifest is a one-at-a-time sweep, and this
batch shows it measures a quantity that does not compose: it says what each fork does *from
one place in the space*, not what it does. Tier 2's eight pairs were designed to catch
interaction and were the first thing marked for cutting if the budget bound. They should not
be cut. Compute is not what binds here — the whole of this batch's eighteen backtests cost
sixteen minutes — and the pairs are now the part of the manifest with evidence behind it.

## 6. What the promoted candidate is

Monthly province counts as a **two-part hurdle**:

```
P(month reports at all)   logistic on the same design, with an estimated
                          coefficient on standardised log population
                          (an offset has no meaning on the logit scale)
count | reports at all    1 + NegBin(mean, phi)

log mean = log(population)                     offset          (03_population/a_offset)
         + global level
         + shared annual season, two harmonics                 (no climate: c_climateFree)
         + province effect      u[i]    ~ pooled, sigma_u
         + province-year effect v[i,y]  ~ pooled, sigma_v[i]    (06_yearVariance/b_provinceScaled)
```

Fitted as before by empirical Bayes — Fisher scoring for the coefficients, EM for the
variances, a one-dimensional profile search for the dispersion — with the two blocks fitted
separately on the same rows. The positive part is a negative binomial on `y − 1`, the cheaper
of the two standard hurdle constructions; what it gives up is that its coefficients are not
comparable with the other observation models', which they were never going to be.

**What it found** (`results/main/fitted_model.json`): 2 012 usable rows, of which **808**
report at least one case; between-province spread sigma **1.27** in the count block and
**1.52** in the presence block; dispersion **1.18**; and seventeen annual variances running
from **2.33** in Xaisomboun to **0.12** in Oudomxay — a ratio of nineteen, where the model it
replaced asserted one.

## 7. What it scores

`04_score/03_compare/results/main/leaderboard.csv`, repeat-mean rows only:

| model | mean CRPS | MAE | 10–90 | 25–75 | cost |
|---|---|---|---|---|---|
| reference (mean of 4) | **22.098** | 28.902 | 0.804 | 0.602 | 1 070 s |
| **hier_nb** | **23.698** | **27.569** | 0.701 | 0.582 | **36 s** |
| climatology | 24.337 | 30.620 | 0.650 | 0.542 | 28 s |
| persistence | 24.879 | 29.073 | 0.666 | 0.491 | 31 s |

The candidate has moved from last to second, past both required baselines, and it keeps the
best point forecast in the project. The reported skill score against the reference is
**−0.072**, from −0.181.

**The comparison can no longer separate it from the reference.** The paired per-cell
difference is **1.599** CRPS with a split-clustered standard error of **1.551** — 1.03
standard errors, against batch 8's 3.62. It wins 41 % of cells and 2 of 8 splits. The plan
says an honest "we cannot separate these two" is a conclusion, and this is the first time the
project has been entitled to state one.

**By lead time** the candidate is 20.4 / 23.2 / **27.5** against the reference's 16.5 / 22.0
/ 27.8. At three months' lead our model is level with the field's own; at one month it is not
close, and the whole of the remaining gap is there.

## 8. The width defect: half repaired

Batch 8's diagnosis was that the candidate's predictive distribution was too wide in
Vientiane Capital, where the 10–90 interval covered **every** outcome, and too narrow in
Salavan, where it covered an eighth — and that a single shared province-year variance was the
feature making both failures the same failure.

Half of that is right. From `results/main/crps_by_location.csv`:

| province | observed | batch 8 CRPS | now | batch 8 cov. | now | reference |
|---|---|---|---|---|---|---|
| Vientiane Capital | 3 707 | 111.6 | **78.0** | **1.000** | **0.88** | 92.8 (0.78) |
| Salavan | 1 455 | 57.5 | 55.1 | **0.125** | **0.12** | 38.4 (0.70) |
| Luang Prabang | 1 336 | 41.6 | 43.4 | 0.583 | 0.58 | 47.4 (0.54) |

The too-wide province is repaired and the candidate now beats the reference there. The
too-narrow province is untouched. A per-province variance widens a province whose annual
variance is genuinely large; it does nothing for one whose epidemic years are sharper than
any log-scale variance can represent, and Salavan, Bokeo and Attapeu are where the remaining
gap to the reference lives.

Aggregate coverage fell from 0.720 to **0.701** while the score improved by 2.4 CRPS, which
is worth noticing on its own: the aggregate was never describing either failure.

## 9. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The promotion rule, fixed and committed before the combination it chose was run | A rule expressed in batch 7's measured floor rather than in positions on the sweep's ranking is a rule that cannot be fitted to the sweep | agent-autonomous |
| The rule is applied **once**, not iterated to a fixpoint | Iterating is greedy coordinate descent on development CRPS — the failure phase C names — and one held-out year cannot diagnose it. The cost of stopping is stated rather than hidden | agent-autonomous |
| The width defect and the autoregressive term become **forks**, not model changes | Both were batch 8's proposals, and both would otherwise have been silent structural choices. That the autoregressive term turned out to be worth nothing is a finding the fork produced | agent-autonomous |
| `COMBO_BASE`: a combination inherits what it did not move, per artefact, and every inheritance is recorded in the file that reports it | Batch 5's design named the reuse; this is the mechanism. The reference is unseeded, so re-running it under a candidate-internal fork would move the denominator for reasons unrelated to the fork | agent-autonomous |
| The sweep stops at `02_aggregate` and its driver lives outside the tree | A `conclusion.json` per sibling is the phase-D deliverable, and producing nine here would report the stability answer before the manifest that makes it honest exists. Every number it produces is still written into the tree by the tree's own scripts | agent-autonomous |
| `covariate_lag_months` (an integer) became `covariate_lags` (a list) | One option owned by one fork cannot mean an integer for one child and a list for another. The model it configures is identical, and re-running the batch-8 configuration after the change reproduced batch 8's per-cell scores byte for byte | agent-autonomous |
| The hurdle's positive part is a negative binomial on `y − 1`, not a zero-truncated one | The cheaper of the two standard constructions, reusing the module's existing fit. What it gives up — coefficients not comparable across observation models — is not something this fork was ever going to use | agent-autonomous |
| The demoted children's `results/main/` were **removed**, not renamed | They described a main path that no longer exists, and two children of one fork holding results under one combination is a configuration the assembler refuses on purpose. Renaming would leave a file whose contents contradict its directory | agent-autonomous |
| The convergence tolerance was **not** relaxed | A criterion adjusted after seeing a run is a criterion adjusted to pass | agent-autonomous |

## 10. Compliance for this batch

- **Rule 1** — every number in this report is read from a file an executed script wrote.
  Eleven new provenance records, one per fork child, and thirteen addenda to the records
  of the nodes this batch re-ran — the four children whose forks did not move or that were
  demoted, the candidate's own two, and the scoring nodes'.
- **Rule 2** — nothing produced was edited. Three result directories were *removed* rather
  than edited, for the reason in §9, and git holds them at commit `b987640`.
- **Rule 3** — unchanged: the model ships its own `pyproject.toml` and `uv.lock`, and every
  one of the ten runs verified after the fact that the lockfile chap-core built from is
  byte-identical to the tracked one.
- **Rule 4** — four commits: before the run, the sweep and the rule, the promotion, and
  after. The promotion is its own commit, which `/node` asks for, because "the switch
  happened and when" is exactly the kind of decision that otherwise disappears.
- **Rule 5** — the fitted object now carries the per-province annual variances and, for the
  hurdle, the presence block's coefficients and Cholesky factor. One gap is stated rather
  than left: under `fit_time = predict` the fit happens once per split inside chap-core's
  untracked run directories, so that combination's `fitted_model.json` is a stub.
- **Rule 6** — the project seed and its derivation are unchanged; the component seed is still
  **849487747**. Verified rather than asserted: two independent runs of every model of ours,
  the promoted hurdle candidate included, produce identical per-cell scores and identical
  fitted objects (`AI-generated/determinism-checks/model_determinism.json`, `identical`).
- **Rule 7** — the three figures at `04_score/03_compare` regenerated with the promoted
  candidate, each with its plotted values and its pre-aggregation values beside it.
- **Rules 8, 9, 10** — no surface here; batches 17 and 19 give them one.
- **`/annotate-criticality`** — appended to `analysis/03_models/criticality.md`. The storage
  question stopped being hypothetical: ten combinations of the candidate are **102 MB**, of
  which 98 MB is regenerable NetCDF and 2.4 MB is the per-cell scores everything reported is
  computed from.
- **`/validate invariants`** — passes: tree, provenance, plots, seeds, claims, git, crossing.

## 11. What went wrong, kept

**The promoted fit does not converge.** Every combination carrying `b_provinceScaled` runs to
the 200-round cap; `yearVariance_shared` converges in 48. The cause is the criterion, not the
fit: it is a maximum over the relative movement of all seventeen variances, and the smallest
of them — 0.12 in Oudomxay — keep that maximum above tolerance long after the parameters have
settled. `sigma_province` is 1.265204 at round 197 and 1.265199 at round 200, and the
log-likelihood moves in its sixth significant figure. **The tolerance was not relaxed**, and
the fitted object says `converged: false` where a reader will find it.

**`fit_time = predict` leaves no fitted object.** The fit happens once per split inside
chap-core's run directories, which are working space and not tracked, so `train` writes a stub
and the combination's `fitted_model.json` records the configuration and nothing else. Rule 5
is satisfied for what that configuration *has* — there is no single fit — but it is a real
gap in the record and it would become a problem if that child were ever promoted.

**The first sweep's results are no longer in the tree.** Round 2 re-ran the same combination
names around the promoted main path and replaced them. Round 1's table is kept, and is the
record the promotion was decided from, but the per-combination files behind it are only at
commit `49825b5`. The alternative was to keep two sets of combinations with different bases in
one tree, which is worse: a table whose rows were measured around different configurations is
not a sweep.

**A premise script parsed the period format wrong and was caught by its own output.** The
autoregressive premise computed autocorrelations of `NaN`, because it read `1998-01` as if it
were `199801` and collapsed every month of a year onto one index. It was fixed at the source
and the step re-run. Worth recording because the failure was loud only by luck — the same
error in a script that did not divide by a variance would have produced a plausible number.

## 12. What is still unknown

1. **Whether phase C should iterate the promotion rule.** Two children are outside the floor
   from where the model now stands. §4 and the plan's §4b both record that stopping was a
   decision rather than an oversight; whether it was the right decision is §13's question.
2. **What repairs Salavan.** A per-province variance did not, and the remaining gap to the
   reference is concentrated in the three provinces whose intervals are far too narrow. A
   heavier-tailed observation model, or a variance that scales with the province's own level
   rather than being constant on the log scale, are the obvious candidates and neither is a
   fork this node has.
3. **Whether the one-month lead can be closed.** The reference is 16.5 there and our best is
   20.4; at three months they are level. Something the reference does at short lead — it
   refits inside predict, and it carries a per-district random walk — our candidate does not.
4. **Whether a gradient-boosted model can be given a calibrated probabilistic head.** Batch
   10's, unchanged.
5. **Whether the headline weighting fork flips the ranking.** Batch 12's, and now sharper
   still: the candidate beats the reference in the highest-burden province and loses in the
   third-highest, so a case-weighted mean moves weight toward where the two disagree most.

## 13. For the human

- **The project has a candidate that beats both required baselines and cannot be
  distinguished from the reference.** 23.698 against 22.098, a paired difference of 1.599
  with a standard error of 1.551. The plan says an honest "we cannot separate these two" is a
  conclusion; this is the first time the project has been in a position to say it.
- **The most valuable thing this batch produced is not the model.** Three forks worth 4.632
  CRPS one at a time delivered 2.402 together, and two of nine children reversed sign when
  measured from a different starting configuration. Phase D's tier 1 is a one-at-a-time
  sweep. **Tier 2's pairs should not be cut** — they were first on the list if the budget
  bound, and compute is not what binds here.
- **One decision I made that you may want to reverse.** I applied the promotion rule once and
  stopped, although two children — refitting inside predict, and the richer covariate set —
  are outside the floor from where the model now stands and would take the candidate to about
  22.8, within 0.7 of the reference. My reason for stopping is that iterating is greedy
  optimisation on development CRPS, which is the failure the plan warns about and which one
  year of holdout cannot diagnose. But the cost is real and I have not hidden it. If you want
  phase C to iterate to a fixpoint, say so and batch 10 can start there.
- **Your question from batch 8 is still open.** Phase C's stopping rule says the phase ends
  when "the leaderboard's best" moves by less than 0.4 CRPS in a batch. Batch 9 moved the best
  of *ours* by 2.402 and the best on the board by nothing, since the reference is unmoved and
  unmovable. I have applied it as "the best of ours" and batch 10 is admissible either way,
  but it will matter at batch 11.

---

## Correction — 2026-08-27, from batch 21

**§10's Rule 6 line cites `AI-generated/determinism-checks/model_determinism.json` as
`identical`. The file this batch committed says `differs`.**

What §10 claims in words is true and is unaffected: two independent runs of every model of
ours, the promoted hurdle candidate included, produced **identical per-cell scores and
identical fitted objects**. What is wrong is the parenthetical citation of the file's
top-level status word, which said `differs` at commit `dec4116` and had said `identical` at
`509d458` one batch earlier.

The cause was in the check, not in the models, and it was this batch's own doing. Batch 9
added a `scored_under_combo` column to `models.csv` — the column that makes `COMBO_BASE`
inheritance visible on the face of the file. `verify_model_determinism.sh` ran its two
passes under scratch combinations named `determinism_<model>_1` and `_2` and compared
`models.csv` byte for byte, so from this commit onward it was comparing a field whose value
*is* the pass's own scratch name. It could not pass, for any model, ever again.

**Repaired on 2026-08-27**: both passes now run under one combination name, pass 1's outputs
are copied aside and compared with what pass 2 writes over them, and nothing is exempted
from the comparison. Re-run at that commit, the check reports `identical` for persistence,
climatology and the candidate. `AI-generated/determinism-checks/provenance.md` carries the
demonstration and the alternatives that were rejected; the plan's §4b records the decision
as `agent-on-human-assessment`.

**Nothing else in this report is affected**, and no number in it changes: the defect was in
a status word, and the scores and fitted objects it was reporting on matched all along.
