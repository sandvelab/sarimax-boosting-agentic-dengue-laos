# Batch 11 — candidate 3: the ensemble, and the close of phase C

Generated from [[26-08-22_dengueForecastingCase]] — iteration 11

**Phase C · Status: done — produced · Executed 2026-08-28**

---

The batch that builds candidate 3, chooses which family the project reports, and closes
phase C. `c_ensemble` and its one fork now exist, both combinations have been run on the
development data, the family fork has moved for the first time, and **the reported
conclusion is positive**.

**Mean CRPS 18.817 over the same 371 cells**, against the reference model's 22.098,
candidate 2's 20.771, candidate 1's 23.698, climatology's 24.337 and persistence's 24.879.
The skill score is **+0.1485**, the first positive figure this project has produced. The
paired difference against the reference is **−3.282** with a split-clustered standard error
of **1.726**, it is better in **six of the eight splits**, and it beats each of the
reference's four unseeded repeats individually by between 3.00 and 3.57 CRPS. At 1.90
standard errors it does not separate the two models, and this report does not say it does.

Two results matter more than the score.

**A registered prediction was wrong, and its being wrong is the finding.** Before the model
ran, `01_weighting/a_equal` wrote down that an equal pool would score *worse* than its best
member, because half its mass sits on the two required baselines. It beat its best member by
1.954 CRPS. The prediction reasoned about where the forecasts sit and not about how wide
they are.

**Estimating the weights cost 4.021 CRPS.** The sibling fits them to minimise the pool's own
CRPS on a year held back inside the training frame. It found the exact minimiser there — and
the member it concentrated 95 % of the pool on is the *worst* of the three non-baseline
members on the period the backtest scores. That is the failure the plan's phase C names,
measured rather than argued about, with both sides of it in one table.

## 1. What the tree looks like now

```
03_models/03_candidate/            [alternatives -> c_ensemble]              PROMOTED
├── a_hierNB/                      [sub-analyses] candidate 1, six forks   CRPS 23.698
│                                   now under its own combination family_hierNB
├── b_boosted/                     [sub-analyses] candidate 2, two forks   CRPS 20.771
│                                   under family_boosted
└── c_ensemble/                    [sub-analyses] "…a weighted combination CRPS 18.817  NEW
    │                               of the models this project already has"
    └── 01_weighting/              [alternatives -> a_equal]                          NEW
        ├── a_equal                every member 1/M, nothing estimated       18.817
        └── b_crpsWeighted         the minimum-CRPS weights on a validation  22.838
                                   period held back inside the training frame
```

`03_candidate` is an alternatives node, so promoting `c_ensemble` means `analysis/run.sh`
now reproduces the pool, and the two demoted families run under combinations of their own.
Candidate 1's `results/main/` were **removed** rather than renamed, as batch 9 removed the
demoted fork children's, for the same reason: they described a main path that no longer
exists and `04_score` discovers models by the fact of having run, so a `model_spec.json`
under `main` would have put a row on the reported leaderboard that `analysis/run.sh` does
not produce. Re-run under `family_hierNB`, candidate 1 produces **per-cell scores identical**
to the ones removed. Git holds the removed files at commit `4cdfd16`.

## 2. What the model is

A **linear opinion pool**: the members' predictive *distributions* averaged, not their point
forecasts.

    F(y) = Σ w_m F_m(y)

Averaging distributions and averaging points are different models, and the difference is why
this node can be worth having. A pool of point forecasts throws away every member's
uncertainty and has to invent a new one; a pool of distributions keeps all of it and adds the
members' disagreement as extra spread. On this dataset that second term is most of the
result: every member except candidate 2 under-covers its 10–90 interval, at 0.650, 0.666 and
0.701 against a nominal 0.80, and the pool reaches 0.863 by disagreeing with itself.

**Its members are not reimplemented, and they are not copied.** Each member is run through
**its own Chap entry points**, with the command string read out of the member's own
`MLproject` and the placeholders filled in — so the pool talks to its members through the
same contract the platform does. There is one copy of every member's code in the repository,
at the node that owns it, and a change to a member is a change to this model with no file
here to keep in step.

What that costs is stated in `pyproject.toml` rather than discovered: the pool runs its
members in its own interpreter, so its environment is the **union** of theirs — the first
model here to depend on numpy, pandas, pyyaml *and* scikit-learn together.
`prepare_members.py` compares every member's pins against that file and fails the run if one
asks for a version it does not carry. The alternative was to build four environments and
shell out to four interpreters, which is chap-core's `uv_env` machinery reimplemented inside
a model, and wrong in a different way than chap-core whenever the two disagreed.

**Which models it contains is a document, not a list in the code.** `prepare_members.py`
globs for `MLproject` under `03_models`, so a model joins the pool by existing in the tree.
For the two members that take a configuration, it runs **that family's own fork main-path
children and that family's own assembler, under the running combination** — which is what
makes the pool follow a perturbation in phase D: a combination that moves candidate 1's
observation model moves the pool's candidate-1 member with it, because both are configured by
the same fork nodes. `AGENTS.md` §2 sanctions a node running its siblings' scripts; it is how
the stability node executes the paths not taken, and this node's claim is about its siblings
in the same way.

The membership document's path and sha256 are in the model configuration, and the model
refuses to pool anything if the file it finds is not the file the configuration names.

## 3. The fork, and what estimating the weights cost

| combination | CRPS | MAE | 10–90 | 25–75 | skill | s |
|---|---|---|---|---|---|---|
| `family_ensemble` (main path) | **18.817** | **23.214** | 0.863 | 0.749 | +0.1485 | 60 |
| `weighting_crpsWeighted` | 22.838 | 27.191 | **0.725** | **0.590** | −0.0335 | 77 |

Batch 9's promotion rule requires a fork's best child to beat the main path by more than the
0.565 CRPS floor. The alternative is **4.021 worse** — seven times the floor, in the wrong
direction — so `a_equal` stays, and by the largest margin any fork in this project has
produced.

**The solve did not fail.** The minimum-CRPS pool is the standard construction, and it is
computed exactly rather than searched for: for sample-based forecasts
`CRPS = E|X − y| − 0.5 E|X − X′|`, so the pool's CRPS is `Σ w_m A_m − 0.5 wᵀBw` with
`A_m = E|X_m − y|` and `B_mk = E|X_m − X′_k|`, a small quadratic that is convex on the simplex
because the matrix of expected absolute distances between distributions is conditionally
negative definite. It is minimised by projected gradient and then checked against every
single-member solution and against equal weights, so the fit cannot return something worse
than what it was initialised at.

On the validation year it did exactly what it was asked:

| | persistence | climatology | candidate 1 | candidate 2 | the pool |
|---|---|---|---|---|---|
| CRPS on the validation year (2007) | 24.981 | 23.566 | **14.253** | 17.140 | 14.227 at the fitted weights, 17.026 at equal |
| fitted weight | 0.047 | 0.000 | **0.953** | 0.000 | |
| CRPS on the evaluated period (2008–09) | 24.879 | 24.337 | **23.698** | 20.771 | 22.838 |

The member that was best on the validation year is the worst of the three non-baseline
members on the evaluated period. **One year of held-back data does not say which member will
be best on the next two.** Fitting looked worth 2.799 CRPS where it was fitted and cost 4.021
where it was scored.

That is also the answer to an obvious objection to the batch's headline. If the pool's win
came from an inadvertent look at the evaluated period, the *fitted* pool — which looks harder
— would win by more. It loses.

**Two of three registered predictions held.** `b_crpsWeighted` predicted before the run that
the minimum-CRPS solution would put at least one member below weight 0.05 (three are at or
below), and that it would place more weight on the candidate families than on the required
baselines (0.953 against 0.047). Its third said the fitted pool would beat the equal pool by
*less* than the 2.799 it beat it by on the validation period. It did not beat it by less; it
lost to it by 4.021. Reporting that as two-for-three rather than three-for-three is the honest
count.

## 4. The prediction that was wrong

`a_equal`'s premise, written into its option specification before anything was fitted:

> an equally weighted pool puts half its mass on the two required baselines, which are the
> two worst-scoring models of ours, so it is predicted to score worse than the best member
> and better than the mean of the members; and because a linear pool's variance is the mean
> of its members' variances plus the spread between their means, its 10–90 coverage is
> predicted to be at least the largest of its members'.

Measured afterwards by `check_pool.py` (`results/main/pool_check.json`):

| | predicted | measured |
|---|---|---|
| pool against its best member (20.771) | worse | **better by 1.954** |
| pool against the mean of its members (23.421) | better | better by 4.604 |
| pool's 10–90 coverage against the largest member's (0.825) | at least | 0.863 |

The first line is wrong and the argument behind it is where the error is: it reasoned about
where the forecasts sit and not about how wide they are, and CRPS is a function of both. The
second and third are right, and the third is right for the reason given — which is also what
makes the first wrong, since the widening the prediction anticipated is worth more than the
two weak members cost.

**This is the second batch running to register a prediction and then measure it, and the
second time the interesting result has been in the gap.** Batch 10's head prediction was
right in seven of eight named cases and over-reached on the eighth. This one was wrong in its
headline claim. Neither would have been visible if the premise had been written after the
number.

## 5. The pool, rebuilt by a second path

A model that beats every model in it deserves more than one route to the claim. So
`check_pool.py` rebuilds the pool **from the members' own stored evaluations** — the
`eval.nc` files produced when each member was run on its own, through its own node — pools
their samples at the same weights, and scores the result with chap-core's own CRPS. Nothing
of the ensemble's own forecast is used.

| | mean CRPS |
|---|---|
| the pool as it ran | 18.817 |
| the pool rebuilt from its members' own evaluations | **18.801** |
| difference | −0.016 |

The two cannot agree exactly: the members' draws are the same draws — same code, same frames,
same seeds — but the pool takes a seeded subsample of each member's thousand and the
reconstruction takes a different one. What is left is the sampling error of the allocation.
The members' scores computed by that second path reproduce their leaderboard rows to every
printed digit, so the models inside the pool are the models on the leaderboard.

**A member's evaluation is matched by configuration hash, not by combination name.** Candidate
2 has never run under `main` or under anything the pool inherits from, so a name-based lookup
would either fail or — worse — find a differently configured run of the same member and compare
against it silently.

## 6. The calibration, which is the cost of the win

The plan's §2: *a model that wins on mean CRPS while being badly calibrated has not won.* So:

| model | 10–90 (nominal 0.80) | 25–75 (nominal 0.50) |
|---|---|---|
| **ensemble** | 0.863 | **0.749** |
| boosted | **0.825** | 0.693 |
| reference | 0.804 | 0.602 |
| hier_nb | 0.701 | 0.582 |
| persistence | 0.666 | 0.491 |
| climatology | 0.650 | 0.542 |

The pool is the most over-dispersed model in the project. At the 10–90 level its error is
+0.063 and on the conservative side, and it is the second-closest to nominal of the six; at
the 25–75 level its error is +0.249 and large.

**The obvious innocent explanation was measured and does not hold.** 56 % of this dataset's
observed province-months are exactly zero, so a model with a large atom at zero has a 25–75
interval of [0, 0] in many cells and every zero outcome falls inside it whatever the model
believes. If that were what the 0.749 was showing, the pool would be more exposed to it than
its members. It is less:

| share of cells where the model's own interval is a single point | 25–75 | 10–90 |
|---|---|---|
| persistence | 0.547 | 0.267 |
| climatology | 0.420 | 0.251 |
| hier_nb | 0.412 | 0.256 |
| **ensemble** | **0.240** | 0.003 |
| boosted | 0.000 | 0.000 |

So the over-dispersion is real, and it is the textbook property of a linear opinion pool:
a pool is over-dispersed even when every member is calibrated. The diagnostic earns its place
by killing an excuse rather than by supporting a claim.

Locally it is worse in both directions. Three provinces are at 10–90 coverage **1.000** —
Vientiane Capital, Savannakhet and Xayabury, where the pool's interval contains every outcome
— and Attapeu is at 0.542 and Salavan at 0.583. Calibration averaged over sixteen provinces
continues to hide more than it shows on this dataset, which was batch 9's finding about
candidate 1 and is not repaired by pooling.

## 7. What the pool actually does better

Per province, against its own members and the reference, on the six highest-burden provinces
(`04_score/02_aggregate/a_unweighted/results/*/crps_by_location.csv`):

| province | cases | ensemble | boosted | hier_nb | reference | climatology | persistence |
|---|---|---|---|---|---|---|---|
| LA-VT Vientiane Capital | 3 707 | **58.62** | 72.97 | 77.99 | 92.81 | 80.18 | 59.78 |
| LA-CH Champasak | 2 431 | **37.51** | 46.10 | 54.08 | 52.25 | 38.37 | 41.62 |
| LA-SL Salavan | 1 455 | 40.59 | **35.44** | 55.09 | 38.44 | 52.10 | 58.60 |
| LA-LP Luang Prabang | 1 336 | 43.48 | 43.46 | 43.35 | 47.39 | **43.23** | 91.60 |
| LA-KH Khammouane | 1 056 | **29.39** | 36.50 | 32.48 | 32.49 | 31.59 | 43.73 |
| LA-BK Bokeo | 927 | 29.06 | 36.01 | 37.50 | **29.71** | 36.63 | 38.44 |

**The pool is best in the two highest-burden provinces and beaten in three of the other
four**, and that is the shape of the whole result: it wins only **43 % of individual cells**
while being 3.282 CRPS better on average. It is not right more often. It is much less wrong
where it is wrong, which is what a hedge is.

Vientiane Capital is the clearest case. The best single member there is **persistence**, at
59.78 — the crudest model in the project, in the one province where the count is large and
autocorrelated enough for last month's value to be a good forecast — and the two candidates
are at 72.97 and 77.99. No selection rule operating on the leaderboard would ever have picked
persistence, and the pool gets its contribution without picking it.

**And the pool wins at every lead time, including the one neither candidate could:**

| lead | ensemble | boosted | hier_nb | reference |
|---|---|---|---|---|
| 1 month | **14.66** | 18.36 | 20.36 | 16.54 |
| 2 months | **18.23** | 19.25 | 23.23 | 21.97 |
| 3 months | **23.56** | 24.69 | 27.50 | 27.79 |

Batch 10 left "what the one-month lead needs" as an open question, with the reference at 16.54
and our best at 18.36, and named the reference's freshness as the likely reason. The pool is
at 14.66. It gets that from persistence, whose whole content is freshness, and which is on the
board only because the plan requires it as a baseline.

## 8. The promotion, and the rule it was made by

`AI-generated/candidate-forks/family_rule.md` was written after
`families/family_leaderboard.csv` existed and **committed before the promoted family was run
under `main`** (commit `4cdfd16`), so what it decides cannot have been fitted to what it
decided. It is batch 9's threshold unchanged, with one clause added that an internal fork does
not need:

1. the family fork moves only if the best family beats the current main path by more than
   0.57 CRPS;
2. each family is compared **at its own main path**;
3. the moved family is then run under `main` and the whole scoring chain re-run there;
4. **a family that wins on mean CRPS while being badly calibrated has not won** — if the
   winner's 10–90 coverage is further from nominal than the current main path's, the promotion
   is not taken on CRPS alone and the case goes to the human.

Clause 1: the pool beats candidate 1 by **4.881** CRPS, 8.6 times the floor. Clause 4: the
pool's 10–90 error is +0.063 against candidate 1's −0.099, so it is closer to nominal and the
clause does not fire. What the clause does *not* say is worth naming: candidate 2 at 0.825 is
closer to nominal than either, and the rule ranks on CRPS with calibration as a veto rather
than as a second score.

**The reference was not re-run.** It is unseeded and costs eighteen minutes, and re-running it
would move the denominator of every comparison in the project for reasons unrelated to this
batch. Only the promoted family, `04_score` and `conclude.py` were re-run under `main`.

## 9. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The family fork is promoted to `c_ensemble` | `family_rule.md` clause 1, applied to a table that existed before the rule was written and to a threshold fixed in batch 7. Batch 10 recorded what the rule would have decided then, so batch 11 could not decide otherwise without saying so; it decides the same way, one family further on | agent-autonomous |
| Candidate 1's `results/main/` are **removed**, and it is re-run under `family_hierNB` | They describe a main path that no longer exists, and `01_collect` discovers models by the `model_spec.json` they wrote. Batch 9's precedent for demoted children, applied one level up. The re-run reproduces its per-cell scores identically, which is what makes the promotion's cost measurable | agent-autonomous |
| The pool runs its members through **their own entry points**, read from their own `MLproject` | Four copies of member code would drift, and the node's claim is that these are the models on the leaderboard rather than versions of them. The cost — one environment that is the union of four — is paid in `pyproject.toml` and checked in `prepare_members.py` | agent-autonomous |
| The members' configurations are **assembled under the running combination** by this node, not read from a named one | It is what makes the pool follow a phase-D perturbation of a member's fork. A combination name in the configuration would leave the pool's member behind whenever a fork moved | agent-autonomous |
| The weights fork has two children and no third | `equal` estimates nothing; `min_crps` is the standard optimal-linear-pool construction and is knob-free. Weights proportional to `1/CRPS` were rejected before being built: the members span roughly 21 to 25, so the weights would span 0.22 to 0.27 and the fork would measure a rounding error at full compute cost | agent-autonomous |
| The validation hold-back is four blocks of the forecast horizon — a logged decision, not a fork | §3 permits either. Shorter than the horizon fits weights for a different problem; longer takes training data from the members being weighted; four is the smallest that gives each member more than one block to be wrong in. A fork here would enumerate a tuning grid to be re-run in phase D and on the holdout | agent-autonomous |
| The pool's draws are **allocated** across members by largest remainder, not drawn member-by-sample | An exact sample of the mixture with one fewer source of Monte Carlo noise, and a small-weight member contributes its share in every cell instead of by luck | agent-autonomous |
| `check_pool.py` reconstructs the pool from the members' stored evaluations and **degrades rather than fails** when one is missing | A model that beats every model in it needs a second path to the claim. It degrades because which combinations have been run is a fact about the project's history, and failing would make `analysis/run.sh` depend on results it does not itself produce; the absence is recorded in the file | agent-autonomous |
| The flat-interval diagnostic was added to kill an explanation | The 25–75 over-coverage has an innocent reading on a 56 %-zero target. Measuring the exposure showed the pool is *less* exposed than three of its members, so the reading is wrong and the over-dispersion is real. Reporting the coverage without it would have left the excuse standing | agent-autonomous |
| `family_leaderboard.py` is a **new script**, not a subcommand of the fork sweep | It answers a different question — across families rather than within one candidate — and adding it to `candidate_fork_sweep.py` would change that file's sha256, which is named in the provenance of the two sweeps it has already produced | agent-autonomous |
| The assembler lift batch 10 scheduled for this batch is **deferred to batches 13–14**, and said so | Rewriting the two existing assemblers changes their sha256, and that hash is in the provenance record of every combination they configured — thirteen — whose results would then name a script that never produced them. Batches 13–14 re-run every combination in the frozen manifest, which is when regenerating those records costs nothing extra. Recorded in four places rather than in nobody's notes | agent-autonomous |
| Phase C is **closed** although its stopping rule permits another candidate batch | The rule makes a further batch admissible, not required: the best moved by 1.954 CRPS against the 0.4 threshold. Closing is the judgment that the stability answer is worth more than a better CRPS — the plan's own words — and that another round of selection on development CRPS is the failure phase C warns about. Put to the human in §13 with the reversal named | agent-autonomous |

## 10. Compliance for this batch

| Rule | What was done |
|---|---|
| 1 — track results | Six new provenance records at the three new nodes, and eleven addenda at the nodes this batch re-ran: candidate 1's six fork children and its two node records, candidate 2's two fork children and its assembler, the three scoring nodes, the three figures and the root's conclusion. Every one names its script's sha256, its inputs, its environment, its commit, its alternatives-considered and its agency |
| 2 — no manual manipulation | No file produced by this batch was edited. Candidate 1's `results/main/` were **removed**, not edited, for the reason in §1, and git holds them at `4cdfd16`. The three ensemble combinations were **re-run** after `ensemble_model/train.py` changed, so that the `model_files_sha256` in every `model_spec.json` names bytes still on disk — checked, and all six files agree in all three combinations. Every figure in the batch came back identical from that re-run |
| 3 — pinned environments | The model's own `pyproject.toml` and `uv.lock` pin four packages exactly, and chap-core reports on every run that the lockfile it built from is the one shipped. `prepare_members.py` additionally checks every member's pins against the pool's and fails the run on a mismatch, which is a new check rather than a new pin |
| 4 — version control | Four commits: before the run, the sweep and the family rule, the promotion on its own, and after the run. The promotion is its own commit, which `/node` asks for |
| 5 — intermediates | Every stage writes a file: the fork child's option spec, the membership document, the assembled configuration, the evaluation, the fitted object with its four members embedded, the run cost, the pool check. `/annotate-criticality` extended at `03_models` for the 33 MB the three combinations add, with one dependency recorded that phase D must not prune blind |
| 6 — seeds | Component seed 1648567750, derived from project seed 20260822 by the node's own path — a third component, distinct from both candidates', so no two models of ours share a stream. `verify_model_determinism.sh` now names **all three** candidates by their own node paths: naming one by the family node would have run whichever child was on the main path and reported it under another model's name, which the promotion would have turned from a near miss into a wrong answer |
| 7 — plots | The three comparison figures redrawn for `main` and for `family_ensemble`, each with its plotted values and its pre-aggregation values beside it. Batch 10's name-keyed palette held across the change of membership |
| 8 — hierarchical report | Not due |
| 9 — claims | Answers written into all four new `claim.md` files and the family node's, each citing the file the number comes from. `/claims add` is batch 17's |
| 10 — release | Not due |
| `/validate invariants` | **All invariants hold** |

## 11. What went wrong, kept

**A model node read a scoring node.** The first version of `a_equal/choose_weighting.py` read
`04_score`'s leaderboard, to put the members' scores in its specification alongside the
prediction. That is a circular dependency — `03_models` runs before `04_score` — and it was
invisible under `main`, where a leaderboard from an earlier run happened to be on disk. It
failed the moment the determinism check ran the node under a scratch combination whose scoring
chain had not run. The premise now reads only the shape of the tree, and the numbers about
members are measured afterwards by `check_pool.py`, which is where a number about a member
belongs. **Caught by a check, not by reading the code.**

**A check that could not run yet.** The first version of `check_pool.py` read the aggregated
scores for its own model's CRPS — the same error one step later, and it failed on the sweep's
first combination. It now scores the pool from its own stored evaluation by the same path it
scores the members, which is better than the version that worked by accident: every number in
the file now comes from one path over one set of cells.

**`train.py` changed after the three evaluations had run**, when the invariant check pointed
out that it draws through its members and records no seed of its own. Fixing the cause — the
fitted object now states the pool's component seed on its face — left every `model_spec.json`
naming a hash no longer on disk. Re-running all three was the only honest fix, and every
figure came back identical, which the determinism check had predicted. This is the second
batch in a row to end this way, and the pattern is worth naming: **a model file that changes
after its evaluation costs a re-run, so the invariant check is cheapest when it runs before the
evaluation rather than after it.**

**The family leaderboard found no families.** Its first version matched each family's stored
choices against its forks' declared main paths by comparing stage names, and a fork's directory
name and the stage name its children write are different strings by design — `06_yearVariance`
and `year_variance`. It reported that candidate 1 had never run at its own main path. Comparing
chosen child *node paths* instead is both correct and shorter.

## 12. What is still unknown

1. **Whether the pool's margin survives the weighting fork.** Batch 12's, and sharper than it
   was: the pool's advantage is concentrated in the two highest-burden provinces, so a
   case-weighted headline mean would widen it and a population-weighted one might not.
2. **Whether the pool is over-dispersed everywhere or in particular places.** Three provinces
   are at 10–90 coverage 1.000 and two are below 0.60. A width fork on the pool — trimming or
   sharpening the linear pool, which is the standard repair for its known over-dispersion — is
   the obvious fourth child of `01_weighting` and was not built, because a fork child added
   after seeing the calibration would be a repair fitted to the number it repairs.
3. **How much of the pool's win is diversity and how much is persistence.** Persistence is the
   best single member in the highest-burden province and at the shortest lead, and it is on the
   board only because the plan requires it. A pool of the two candidates alone would answer
   this and is not in the tree.
4. **Whether the weight-fitting failure is about the year or about the method.** The validation
   year is 2007 and the evaluated years are 2008–09; whether the rank reversal is a property of
   that particular year is a question the holdout can ask once and phase D cannot ask at all.
5. **What the pool costs on the holdout.** Its members were each selected on development, and
   the pool inherits every one of those selections. That is four selections deep, and the
   held-out year is the only instrument that can price it.

## 13. For the human

- **The project has met its criterion on development.** Mean CRPS 18.817 against the reference
  model's 22.098 — skill **+0.1485** — ahead of both required baselines, ahead of each of the
  reference's four repeats individually, and better in six of the eight splits. The paired
  margin is 1.90 standard errors, so the honest statement is still that we cannot separate the
  two models, but the margin is now nearly six times the floor rather than inside it.
- **The winning model is also the worst-calibrated in the middle of its distribution**, and
  your §2 says that has to be said out loud rather than hidden. Its 10–90 coverage is 0.863
  against 0.80, which is fine and conservative; its 25–75 coverage is 0.749 against 0.50, which
  is not. I checked whether the zero-heavy target explains it and it does not.
- **The batch's best evidence is the fork that lost.** Fitting the pool's weights to a year
  held back inside the training frame found the exact optimum there and cost 4.021 CRPS where
  it was scored, because the best member on the validation year is the worst on the evaluated
  one. That is the plan's phase-C warning happening, measured, inside the tree, with both sides
  in one table — and it is a stronger argument for the equal pool than the equal pool's own
  score.
- **A prediction I registered before the run was wrong.** I wrote that the equal pool would
  score worse than its best member; it beat it by 1.954. I have left the prediction where it
  was written and the measurement beside it rather than adjusting either.
- **Phase C's stopping rule does not stop the phase, and I closed it anyway.** Batch 11 moved
  the best of ours by 1.954 CRPS against the 0.4 the rule asks for, so a further candidate batch
  would be admissible. I judged that another round of selection on development CRPS is what
  phase C warns about and that the stability work is worth more than a better score — your
  plan's words. If you would rather have one more candidate round, say so and I will append it
  to the ledger; the two obvious targets are in §12, items 2 and 3.
- **One thing I deferred that batch 10 scheduled for this batch.** The three candidates'
  configuration assemblers are near-copies and the shared part should be lifted into a library.
  Doing it now would change two scripts whose hashes are in the provenance of thirteen
  combinations' results. Batches 13–14 re-run all of them for the manifest, so that is where I
  have put it, in the plan's §4b rather than in a comment.
