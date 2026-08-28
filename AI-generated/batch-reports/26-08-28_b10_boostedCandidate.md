# Batch 10 — candidate 2: gradient-boosted trees with a probabilistic head

Generated from [[26-08-22_dengueForecastingCase]] — iteration 10

**Phase C · Status: done — produced · Executed 2026-08-28**

---

The batch that builds candidate 2. `b_boosted` and its two internal forks now exist, all
three combinations have been run on the development data, and for the first time in this
project a model of ours leads the leaderboard.

**Mean CRPS 20.771 over the same 371 cells**, against the reference model's 22.098,
candidate 1's 23.698, climatology's 24.337 and persistence's 24.879. It is ahead of each of
the reference's four unseeded repeats individually — the best of them is 21.820 — and its
paired difference against the reference is **−1.327** with a split-clustered standard error
of **1.110**, which is 1.20 standard errors on the far side of zero where batch 9's candidate
was 1.03 on the near side. It clears the 0.565 CRPS floor the reference's own re-runs
occupy, which no margin in this project had done before.

It still does not *separate* the two models, and the plan forbids implying that it does. What
changed is the sign of the point estimate, not the resolution of the comparison.

The more interesting result is the one batch 4 asked for. **The probabilistic head is where
this family fails, exactly as predicted and for a reason that was written down before the
model ran** — and the failure is smaller than expected, because the negative-binomial head
turns out not to need repairing.

## 1. What the tree looks like now

```
03_models/03_candidate/            [alternatives -> a_hierNB]
├── a_hierNB/                      [sub-analyses]  candidate 1, six forks     CRPS 23.698
└── b_boosted/                     [sub-analyses]  "…gradient-boosted trees   CRPS 20.771  NEW
    │                               with a probabilistic head"
    ├── 01_features/               [alternatives -> a_lagBlock]                          NEW
    │   ├── a_lagBlock             climate at lags 0–3, counts at 3–6 and 12    20.771
    │   └── b_richCalendar         plus harmonics, year, province, rollings      20.375
    └── 02_head/                   [alternatives -> a_negBinomial]                       NEW
        ├── a_negBinomial          one mean booster, one dispersion              20.771
        └── b_quantileEnsemble     fifteen quantile boosters, inverted           20.960
```

`03_candidate` remains an alternatives node with `a_hierNB` on the main path, so
`analysis/run.sh` still reproduces candidate 1 and nothing here has changed what the project
reports. **The family fork is not promoted in this batch, and that is by design rather than
by hesitation**: batch 5 assigns the choice of family main path to batch 11, after the
ensemble exists, and promoting now would pre-empt a decision that has to be made again in one
batch's time. §9 says what the rule would have decided if applied today.

Candidate 2's main path runs under its own combination, `family_boosted`, because a sibling
alternative never runs on `main`. It **inherits** the dataset, the setup choices and the other
four models' scores from `main` — the reference is not re-run, for the reason batch 8 fixed:
it is unseeded, and re-running it would move the denominator of every comparison for reasons
unrelated to this candidate.

## 2. What the model is

Two pieces, and the split between them is the whole shape of the family:

| | |
|---|---|
| **where the count sits** | histogram gradient-boosted regression trees over lagged climate, lagged counts and log population |
| **how wide the distribution is** | a head built around that number, because a tree returns one value and not a distribution |

The trees assume nothing: no link between covariate and count beyond monotone splits, no
additivity, no assumption that rainfall means the same thing in a large province and a small
one. What they cannot do is extrapolate. Candidate 1 is the opposite bargain — a functional
form that extrapolates and a hierarchy that pools, in exchange for assuming the form is
right — and that is what makes the two a fair pair of alternatives rather than two attempts
at one thing.

**The lag structure is asymmetric, and the asymmetry is the forecasting problem rather than a
choice.** `chap eval` hands the model the climate of the months it is asked to forecast — a
rainfall value in a forecast month is known, because it comes from a reanalysis whether or
not a case was reported — so climate enters at lag 0. Only the target is unknown, and only
the target is lagged by three, which is the freshest count the third month of a block can
see.

**Missing values are handled by the trees rather than by us.** The boosters learn a default
direction for a missing feature at every split, so 209 of the 2 012 fitted rows have a lag
falling before the record begins and are fitted on rather than dropped. Candidate 1 drops
them. It is a real difference between the families and not a setting.

## 3. What is a fork here, and what is a logged decision

Two forks, and the boosting hyper-parameters are deliberately not among them.

Shrinkage, tree size, leaf minimum, L2 penalty and the round cap are set once, and the
**number of rounds is then chosen from the data** by an early-stopping split taken **by
month**: fit on the earlier rows, score every round on the latest 15 %, take the best. The
split is not random, because the question the backtest asks is how the model does on the
period after the one it was fitted on, and a stopping rule scored on rows interleaved with
the training rows is choosing a model for a different problem.

Making the hyper-parameters forks would enumerate a tuning grid whose siblings all have to be
re-run in phase D and again on the holdout, to answer a question about tuning rather than
about a judgment call an analyst would plausibly make differently. The plan's §3 allows a
judgment call to be a node **or** a logged decision; this is the second, and it is logged in
the node's claim, in the model's docstring, in its README and in the provenance record —
which is four places a reader can find it and none of them a memory.

## 4. What each fork is worth

Swept around candidate 2's own main path, one non-main child at a time, everything else held
(`AI-generated/candidate-forks/boosted_round1/fork_leaderboard.csv`):

| combination | CRPS | MAE | 10–90 | 25–75 | skill | s |
|---|---|---|---|---|---|---|
| `features_richCalendar` | **20.375** | 28.251 | 0.857 | 0.720 | +0.0780 | 55 |
| `family_boosted` (main path) | 20.771 | **26.953** | 0.825 | 0.693 | +0.0601 | 46 |
| `head_quantileEnsemble` | 20.960 | 33.020 | **0.798** | 0.652 | +0.0515 | 57 |

**Neither fork moves.** Batch 9's rule requires a fork's best child to beat the main path by
more than the 0.565 CRPS floor; the richer feature set is worth 0.396 and the quantile head
costs 0.189. The rule is applied as written, including where it says no to a number that
looks better.

That is worth pausing on. `b_richCalendar` scores better on the headline metric and the rule
still leaves it demoted, because 0.396 is inside the interval within which the reference
model disagrees with *itself*. A rule that only ever said yes would not be a rule.

**The richer feature set buys width, not accuracy.** Its point forecast is worse — MAE 28.251
against 26.953 — and its intervals are wider, 10–90 coverage 0.857 against 0.825, further
from nominal on the over-covering side. That is the signature of a model that has fitted the
training years more closely and is correspondingly less certain about a period it cannot
extrapolate into. Both costs were registered before the run: sixteen provinces as an
identifier are fifteen extra cuts available on two thousand rows, and a year index is a
feature every forecast month falls beyond. The run is consistent with both and separates
neither.

**So the twelve-month lag was enough.** `a_lagBlock` has no month, no year and no province
identifier, and describing all three explicitly moved the score by less than the evaluation
can resolve. On this dataset a tree given last year's count in the same province has already
been told what the calendar would tell it.

## 5. The head fork: a prediction registered before the run, and then measured

This is the batch's methodological centre and the answer to the question batch 4 left open at
§11.2 of the bootstrap plan.

**Before anything was fitted**, `02_head/b_quantileEnsemble/scripts/choose_head.py` computed a
premise and wrote a prediction into it:

> 8 of the 15 ladder levels sit below the target's zero share of 0.563. A pinball loss at
> those levels starts at the marginal quantile — zero — and finds a residual of exactly zero
> at 56 % of rows, where its gradient is at the kink and says nothing about direction. Those
> levels are predicted to stay flat at zero for every province, so the lower 50 % of every
> forecast distribution collapses onto zero — including for 1 province(s) that never report
> one.

**After the run**, `scripts/check_head_premise.py` evaluates every level of the stored ladder
on every row of the analysis dataset and compares
(`b_boosted/results/head_quantileEnsemble/head_premise_check.json`):

| level | 0.01 | 0.05 | 0.10 | 0.20 | 0.25 | 0.30 | 0.40 | 0.50 | 0.60 | … |
|---|---|---|---|---|---|---|---|---|---|---|
| largest count returned anywhere | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.3 | 0.3 | 297 | 872 | … |
| boosting rounds chosen | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 400 | 400 | … |

**Seven of the eight named levels are flat at zero across the whole file.** The eighth, 0.50,
is not flat file-wide — but in Vientiane Capital, the one province that never reports a zero
and whose observed median is 109 cases, the fitted median ladder is
`0 0 0 0 0 0 0 0 122 153 164 196 208 248 384`. So in the province the prediction was actually
about, the bottom half is zero, and file-wide it is the bottom 40 %.

The mechanism is not a defect in the boosters and not a hyper-parameter mistake. It was
checked against both of scikit-learn's independent implementations and against a synthetic
two-group problem a single split should solve, and the same collapse appears. 56.3 % of
observed province-months in this dataset are **exactly zero**, so at any level below that
share the majority of residuals sit precisely on the pinball loss's kink, where the gradient
carries no information about direction.

**The failure is kept rather than repaired.** The repair — a model for whether the month
reports at all, with the ladder fitted only to the months that do — is the hurdle
construction candidate 1's `01_observation` fork promoted in batch 9. It would be a **third
child of this fork**, not a change to this one. A child quietly rebuilt until it worked would
leave the tree with no record that the plain construction does not.

**The two heads fail in opposite directions, and that is the useful part.** The ladder has the
project's closest interval coverage — **0.798** against a nominal 0.80, closer than anything
else ever produced here — and its worst point forecast, MAE 33.020, because a median pinned
at zero is far below the outcome in every province that reports steadily. It is the plan's
"a model that wins on mean CRPS while being badly calibrated has not won", arriving with the
halves swapped: well calibrated on the summary number, wrong in the middle of the
distribution. Reporting the coverage without the MAE would have made it look like the better
head.

## 6. What the winning model actually does better

Not a uniform improvement. Per province, against the reference
(`04_score/02_aggregate/a_unweighted/results/family_boosted/crps_by_location.csv`), on the six
highest-burden provinces:

| province | cases | boosted | hier_nb | reference |
|---|---|---|---|---|
| LA-VT Vientiane Capital | 3 707 | **72.97** | 77.99 | 92.81 |
| LA-CH Champasak | 2 431 | **46.10** | 54.08 | 52.25 |
| LA-SL Salavan | 1 455 | **35.44** | 55.09 | 38.44 |
| LA-LP Luang Prabang | 1 336 | 43.46 | **43.35** | 47.39 |
| LA-KH Khammouane | 1 056 | 36.50 | **32.48** | 32.49 |
| LA-BK Bokeo | 927 | 36.01 | 37.50 | **29.71** |

**It repairs the failure candidate 1 could not.** Salavan carried the largest single piece of
candidate 1's gap to the reference — batch 9 reported its 10–90 coverage at 0.12 and its mean
CRPS at 55.09, and a per-province variance fork did not fix it. Candidate 2 scores 35.44
there, ahead of the reference. The reason is structural rather than lucky: candidate 1's width
was a constant multiplicative factor on the log scale, so it could not be too narrow in
Salavan and too wide in Vientiane Capital at once. A tree that separates the two provinces
gives them different widths as a by-product of giving them different means.

**It is the first model of ours whose intervals are not too narrow.** 10–90 coverage 0.825
against nominal 0.80 — over-covering, where every previous model of ours under-covered. It is
still badly calibrated somewhere: Attapeu at 0.417 and Bokeo at 0.500 are far too narrow, and
Bokeo is the one high-burden province where the reference clearly wins.

**The lead-time pattern is the reverse of candidate 1's:**

| lead | boosted | hier_nb | reference |
|---|---|---|---|
| 1 month | 18.36 | 20.36 | **16.54** |
| 2 months | **19.25** | 23.23 | 21.97 |
| 3 months | **24.69** | 27.50 | 27.79 |

Candidate 1 lost the one-month lead heavily and only drew level at three. Candidate 2 loses
the one-month lead by 1.8 and wins both of the others. The reference refits inside `predict`
and carries a per-district random walk; this model does neither, and one month ahead is where
that costs most.

## 7. The fitted model is a document, not a pickle

Rule 5 forbids a language-specific pickle for anything outliving the session, and the fitted
object outlives it: chap-core writes it between `train` and `predict`, and the node copies it
into `results/`. A boosted ensemble has no natural JSON form, so one was written — each tree
as parallel arrays of split feature, threshold, missing-value direction, children and leaf
values — and `boosted.py` walks that structure itself with nothing but numpy.

Because that traversal is a **second prediction path**, and a second path can disagree, the
fit checks it rather than trusting it: every booster's stored form is evaluated on the
training rows and compared with scikit-learn's own `predict`, and the run fails if the
largest absolute difference is not at machine precision. It is **0.0** on all three
combinations. The stored model was also read back with scikit-learn blocked from importing,
which is the property the format exists to give.

This is the direct descendant of batch 21's finding — that the greedy branch's rule selected
the one configuration under which the model has no stored fitted object at all, and that a
rule selecting on development CRPS cannot see whether the model it selects can be inspected.
Here the object is not merely stored but readable without the library that made it.

## 8. Two defects fixed at their cause

**The comparison figures could only draw four models.** All three built their colour and
marker maps by zipping the models they found against a four-entry list. `zip` stops at the
shorter argument, so a fifth model would have drawn as *no series at all* in two of the
figures, silently, and raised a `KeyError` in the third. The silent half is the one worth
naming: a figure missing a series is a figure a reader believes.

The fix is `analysis/scripts/lib/palette.py`, one mapping for all three, with the property
the per-script versions lacked: a model's colour comes from **its own name**, by the same
BLAKE2b construction the project uses to derive component seeds, rather than from its
position among the models present. Positional assignment would re-colour every model whenever
one was added, so two figures from two combinations could not be laid side by side — and
figures are drawn per combination. `main`'s three figures were redrawn under the new code and
**no plotted value changed**; the CSVs beside them are byte-identical.

**The fork sweep driver was hardcoded to candidate 1 around `main`.** It now takes
`--candidate`, `--base` and `--inherit-from`, with defaults that leave every invocation
recorded before this batch meaning what it meant, and it reads the candidate node's own
scripts out of its `run.sh` rather than naming them. A second copy with two names changed was
the obvious alternative, and it is precisely what `chap_eval.py` argues against.

The third parameter is the one that mattered. A swept row is **measured against**
`family_boosted` and **inherits** from `main`; collapsing the two would have made one of them
wrong, because `family_boosted` holds candidate 2's two choices but neither the dataset nor
the other models.

## 9. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The family fork is **not** promoted here, although candidate 2 beats candidate 1 by 2.927 CRPS — five times the floor | Batch 5's design assigns the family main path to batch 11, after `c_ensemble` exists. Promoting now would pre-empt a choice that has to be made again one batch later, and would require moving candidate 1's `main` results and re-running the whole scoring chain twice. What the rule would decide today is recorded here so that batch 11 cannot quietly decide it differently without saying so | agent-autonomous |
| Neither internal fork moves; batch 9's promotion rule applied unchanged | 0.396 and −0.189 CRPS against the 0.565 floor. The rule was fixed before candidate 2 existed, which is what makes applying it to a second candidate evidence rather than a choice | agent-autonomous |
| scikit-learn enters the project, in one model's environment, pinned by the lockfile beside it | Gradient boosting is binning, split finding, shrinkage and a stopping rule, each with choices in it. A hand-written version would be unreadable *and* incomparable with anything published — the opposite of the case for hand-writing candidate 1's Fisher-scoring fitter, which is two functions | agent-autonomous |
| The fitted ensembles are stored as JSON that this project's own code can walk, and the walk is checked against scikit-learn's on every fit | Rule 5 forbids a pickle for an object that outlives the session. A second prediction path is a path that can disagree, so it is verified rather than asserted, and the largest difference is recorded in the fitted object | agent-autonomous |
| The boosting hyper-parameters are a logged decision rather than forks; the round count is chosen by a **time-ordered** early-stopping split | §3 permits either. Forks here would enumerate a tuning grid whose siblings re-run in phase D and on the holdout, to answer a question about tuning rather than about a judgment call. The split is by month because a stopping rule scored on interleaved rows chooses a model for a different problem than the backtest poses | agent-autonomous |
| Candidate 2 has **no** `fit_time` fork; it fits at train only | With the ladder head the fit is fifteen boosters and two passes, so refitting per split multiplies the backtest by the number of splits to answer a question candidate 1's cheaper fork has already answered — and batch 21 found refit-at-predict is the configuration under which a model has no stored fitted object at all | agent-autonomous |
| `03_compare` **is** run for `family_boosted`, although batch 9's sweep stopped at `02_aggregate` | Batch 9's reason stands and does not apply: what it withheld was a `conclusion.json` per sibling, which is the phase-D deliverable. This node produces the leaderboard, which phase C requires to be script-maintained and never typed, and the paired comparison saying what it can resolve. The root's `conclude.py` was not run | agent-autonomous |
| The quantile head's failure is kept, not repaired | The plan's §3: failures stay in the record. The repair is a hurdle over the ladder, which would be a third child of `02_head` rather than a change to this one | agent-autonomous |
| The colour map moved into a shared library keyed on the model's name | Two of three figures would have dropped a series silently. Keyed on the name rather than on position, so a model keeps its colour across combinations and two figures remain comparable | agent-autonomous |
| The sweep driver was generalised rather than copied | `chap_eval.py`'s argument, applied to the driver: a copy per model is a set of copies that will drift | agent-autonomous |
| The two candidates' configuration assemblers remain near-duplicates | Lifting the shared part into `03_models/scripts/lib/` would rewrite the script that produced the reported main path's configuration, whose hash is in a provenance record and whose results would then need regenerating. Batch 11 adds a third candidate and is where the lift belongs. Logged rather than left in nobody's notes | agent-autonomous |

## 10. Compliance for this batch

| Rule | What was done |
|---|---|
| 1 — track results | Ten provenance records written or extended: three at `b_boosted`, one per fork child, and appended sections at `01_collect`, `02_aggregate`, `03_compare` and all three figures. Every one names its script's sha256, its inputs, its environment, its commit, its alternatives-considered and its agency |
| 2 — no manual manipulation | No file produced by this batch was edited. The three combinations were **re-run** after `boosted.py` changed, so that the `model_files_sha256` in every `model_spec.json` names bytes that are still on disk — checked, and all six files agree in all three combinations |
| 3 — pinned environments | The model's own `pyproject.toml` and `uv.lock` pin four packages exactly, and chap-core reports on every run that the lockfile it built from is the one shipped. First appearance of scikit-learn and scipy in this project |
| 4 — version control | Committed before the run (`4705c5f`), after it (`6cb1163`), and once more to write that hash into the records |
| 5 — intermediates | Every stage writes a file: the fork children's option specs, the assembled configuration, the evaluation, the fitted ensembles as JSON, the run cost, the premise check. `/annotate-criticality` extended at `03_models` for the 32.5 MB the three combinations add |
| 6 — seeds | Component seed 1877199108, derived from project seed 20260822 by the node's path — a different component from candidate 1, so the two families cannot share a stream. `verify_model_determinism.sh` extended to name candidate 2 by its own path (the family node would have run candidate 1 twice) and reports **identical** for all four models |
| 7 — plots | The three comparison figures redrawn for `family_boosted` and for `main`, each with its plotted values and its pre-aggregation values beside it |
| 8 — hierarchical report | Not due |
| 9 — claims | Answers written into all seven new `claim.md` files, each citing the file the number comes from. `/claims add` is batch 17's |
| 10 — release | Not due |
| `/validate invariants` | **All invariants hold** |

## 11. What went wrong, kept

**The first version of the premise check measured the wrong thing.** It bounded each booster
by its baseline plus the largest leaf value of every tree — a statement about every input the
booster could ever be handed, needing no data at all. One positive leaf reachable by no actual
province makes that bound non-zero, and it reported **zero** flat levels where seven plainly
are. It was answering a different question than the premise asked, and the premise's question
is about provinces. Replaced with an evaluation of the ladder on the file's own rows.

**The registered prediction over-reached by one level.** It named eight; seven met the test as
stated. Reporting it as eight-for-eight would have required either the weaker file-wide claim
about 0.50 or silence about the discrepancy, and both are available in the JSON.

**A shell loop wrote one mangled line into two provenance records.** zsh does not word-split
unquoted parameter expansions, so a list of three combinations became one string and
`/validate invariants` failed on fourteen results whose records existed but named nothing.
Caught by the check, which is what it is for.

**`boosted.py` changed after the three evaluations had run**, when scikit-learn's import was
made lazy so the stored model could be read without it. That left every `model_spec.json`
naming a hash no longer on disk. Re-running all three was the only honest fix; the numbers
came back identical, which the determinism check had already predicted.

## 12. What is still unknown

1. **Which family the main path should take.** Batch 11's, and now a real question rather than
   a formality: candidate 2 leads by five times the floor, and the ensemble may lead both.
2. **Whether a hurdle over the quantile ladder rescues that head.** It is the obvious third
   child of `02_head` and would test whether the ladder's per-cell width is worth having once
   the zeros are taken out of its way. Not built here, because a fork child rebuilt until it
   worked would erase the finding.
3. **What the one-month lead needs.** The reference is 16.54 there and our best is 18.36. Both
   things the reference does that neither candidate does — refitting inside `predict`, and a
   per-district random walk — are freshness at short lead.
4. **Whether Bokeo and Attapeu are the new Salavan.** Candidate 2's two worst-covered provinces
   are 0.417 and 0.500 against nominal 0.80, and Bokeo is the one high-burden province where
   the reference clearly wins. Candidate 1's local width defect was repaired by changing family
   rather than by any fork; this one has not been diagnosed at all.
5. **Whether the headline weighting fork flips the ranking.** Batch 12's, and sharper again:
   candidate 2's margin over the reference is concentrated in the two highest-burden provinces,
   so a case-weighted mean would widen it and a population-weighted one might not.

## 13. For the human

- **The project has a model that beats the reference on development.** 20.771 against 22.098,
  and ahead of each of the reference's four repeats individually. It also beats both required
  baselines comfortably and is, so far, the only model of ours whose intervals are too wide
  rather than too narrow. The paired margin is 1.20 standard errors, so the honest statement
  is still "we cannot separate these two" — with the sign now on our side.
- **I did not promote the family fork, on purpose.** Batch 5 puts that choice in batch 11, and
  candidate 2's margin over candidate 1 is 2.927 CRPS — five times the floor — so on today's
  evidence the rule would move it. I have recorded that in §9 so batch 11 cannot decide
  otherwise without saying why. If you would rather the main path move now, it is one
  `/node promote` and a re-run of the scoring chain.
- **The batch's best evidence is not the score.** The head fork wrote down what it expected to
  happen before it ran, and a script afterwards compared the two: seven of eight predicted
  levels flat at zero, the eighth flat in the one province the prediction was about. That is
  the pattern the manuscript's veridical argument wants, and it cost about twenty lines of
  code. It is worth doing again in phase D.
- **A figure could have gone missing without anyone noticing.** Two of the three comparison
  figures would have drawn the new model as no series at all, silently, because of a `zip`
  against a four-item list. The invariant checks did not catch it — the figure would have
  existed, with its plotted values beside it, and only looked wrong to someone counting
  series. Worth remembering when reading §5 of `AGENTS.md`: what a deterministic check can see
  is not everything.
- **Phase C's stopping rule does not stop the phase.** Batch 10 moved the best of ours by
  **2.927** CRPS, against the 0.4 the rule asks for. Batch 11 is admissible on either reading
  of your batch-8 question — and since the best model on the board is now one of ours, that
  ambiguity has resolved itself.
