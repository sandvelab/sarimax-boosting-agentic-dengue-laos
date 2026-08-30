# Batch 14 — `/perturb run`: the candidate and family rows, and the close of tier 1

Generated from [[26-08-22_dengueForecastingCase]] — iteration 14

**Phase D · Status: done — produced · Executed 2026-08-30**

---

Three defects fixed, one found by running into them, an assembler lift two batches had
deferred here, and the fourteen rows that finish tier 1. **All 24 tier-1 combinations now
have a conclusion**, and the shape of the stability answer is complete for one fork at a
time.

**The choice of model family moves the reported conclusion twenty-seven times more than any
choice inside a family.** Swapping the reported pool for candidate 1 costs **0.2209** of
skill and for candidate 2 **0.0884**. The eleven forks *inside* those two families — the
observation model, the covariate set, the lag structure, how population enters, where the
fitting happens, how the year variance is pooled, the boosted features and its probabilistic
head — move it by at most **0.0081**, and their whole span in CRPS is 18.638 to 18.933, a
range of **0.295 against the reference's own 0.57 re-run spread**. Phase C spent three
batches choosing among analyses this evaluation cannot tell apart.

**The exception is the pool's own fork, and it is the second-largest move in the set.**
Fitting the pool's weights by minimising its CRPS on a year held back inside the training
frame costs **0.1820** of skill and takes the reported model to 22.838 CRPS — *behind* the
reference. It is 22 times what any member's fork is worth, and it is the one candidate-internal
fork that is not inside a member.

**The two weighting rows had been reporting the main path's paired numbers.** `03_compare`
computed its paired difference, its three standard errors and its noise floor with every cell
counting once, while the leaderboard beside it followed the weighting fork — so batch 13's two
rows carried `main`'s −3.282 ± 1.726 against a 0.565 floor, beside a re-weighted CRPS, three
times over. Under their own weighting the pool separates from the reference further than
anywhere else in the project: **−26.732 ± 9.321** case-weighted and **−8.478 ± 3.693**
population-weighted, 2.87 and 2.30 standard errors against `main`'s 1.90.

---

## 1. What ran

| | |
|---|---|
| Rows run | 14 assigned to this batch, plus batch 13's two weighting rows re-run under the corrected comparison |
| Wall clock, tier 1 | **1 293 s** against batch 12's planned 1 224 — 5.7 % over on the total, 0.51 to 1.91 per row |
| Rows that failed first time | one, `weighting_crpsWeighted`, at its second step in two seconds |
| Scripts changed | four defects, one library lifted, three runners rewritten |
| Tier-1 rows with a conclusion | **24 of 24** |

The step lists came from `run_manifest.py --dry-run`, which batch 12 wrote as the
specification each row has to satisfy. Every command the driver issued is a `run.sh` or a
node script the main path also runs, with `COMBO` set.

## 2. The three defects the ledger named, and the fourth

All four have one shape: **a step that discovers something from the tree, written when every
fork had exactly one child that did anything.** Batch 22 counted three instances; this batch
found the fourth and the last one the tier-1 set can reach.

**`prepare_members.py` ran every member fork's main-path child.** When the pool assembles a
member family's configuration it runs that family's own scripts, which is right — a second
place that knew how to configure candidate 1 would be a second place that could be wrong
about it. But it ran *every* fork of that family at its main path, and a candidate-internal
row has already run the moved child of one of them. Two children of one fork under one
combination, and the family's assembler refuses them, correctly. That is what blocked all
twelve candidate rows. A fork is now run only where this combination cannot resolve it at
all — not under `COMBO`, not under `COMBO_BASE` — using `resolve_glob`, the same lookup the
assembler itself resolves a fork with.

**`conclude.py` resolved our reported model from `claim.md`.** The `main-path` field at
`03_models/03_candidate` names the child the *reported* analysis takes and does not move with
the combination, so a family row found no results under the child it named and fell through
to "the best-scoring model of ours" with `candidate_exists: false` — on a row whose entire
content is which candidate ran. The family fork is now read off the results, in the order
every other combination-aware step in this project reads a fork. **Two families with results
under one combination is now a hard failure**, which is what would have caught the twelve
stale phase-C directories had they been left in place.

**`03_compare` computed its paired spread unweighted.** The leaderboard on that node is the
weighting fork's own summary and always followed it; the paired difference, the three
standard errors, the split-level comparison and the noise floor did not. So the two weighting
rows reported a re-weighted CRPS with `main`'s own unweighted spread beside it — the same
−3.282 ± 1.726 against the same 0.565 floor, three times over, under three different headline
means, and nothing in the file said so. Every figure on the node now takes its weights from
the chosen child's own `weights.csv`. Within a split the cells carry their weights; across
splits the eight numbers still count equally, because the split-level statistic exists as the
one that assumes nothing about independence inside a split.

**And the fourth, found by running into it.** The driver ran the moved fork child and then
the family's `run.sh`. An alternatives parent runs every fork below it at the main path —
that is what the relationship *means* — so on the one row whose moved fork belongs to the
family that is running, `c_ensemble/run.sh` ran `01_weighting/a_equal` after the driver had
already run `b_crpsWeighted`. Such a row now takes that family's forks itself and then runs
the family's **own scripts**, read out of its `run.sh` under the `# Own scripts` marker
`node.py` writes rather than listed in the driver. It is the treatment `02_setup` already
had, where the driver calls `assemble_setup.py` rather than `02_setup/run.sh`. Checked
against the whole dry run: exactly one row's step list changes, by exactly four commands.

## 3. The result: what tier 1 says, one fork at a time

Twenty-four analyses, every one of which a competent person could have run.

| Combination | Kind | Our model | CRPS | Skill | Δ vs main | 10–90 cov. | SE vs ref |
|---|---|---|---|---|---|---|---|
| `family_hierNB` | family | hier_nb | 23.698 | −0.0724 | **−0.2209** | 0.701 | 1.03 |
| `weighting_crpsWeighted` | candidate / pool | ensemble | 22.838 | −0.0335 | **−0.1820** | 0.725 | 0.48 |
| `family_boosted` | family | boosted | 20.771 | +0.0601 | −0.0884 | 0.825 | 1.20 |
| `persistence_negBinomialFloor` | baseline | ensemble | 19.434 | +0.1206 | −0.0279 | 0.817 | 1.97 |
| `trainingWindow_from2004` | setup | ensemble | 18.751 | +0.1266 | −0.0219 | 0.836 | 2.18 |
| `popColumn_backCast` | setup | ensemble | 19.011 | +0.1347 | −0.0138 | 0.865 | 1.71 |
| `observation_zeroInflated` | candidate / hierNB | ensemble | 18.933 | +0.1433 | −0.0052 | 0.863 | 1.88 |
| `observation_negBinomial` | candidate / hierNB | ensemble | 18.919 | +0.1439 | −0.0046 | 0.860 | 1.88 |
| `climatology_frozenWindow` | baseline | ensemble | 18.872 | +0.1460 | −0.0025 | 0.863 | 1.89 |
| `population_ignored` | candidate / hierNB | ensemble | 18.860 | +0.1465 | −0.0020 | 0.860 | 1.89 |
| `population_covariate` | candidate / hierNB | ensemble | 18.845 | +0.1472 | −0.0013 | 0.860 | 1.90 |
| `yearVariance_shared` | candidate / hierNB | ensemble | 18.840 | +0.1474 | −0.0011 | 0.860 | 1.92 |
| `covariates_lagged` | candidate / hierNB | ensemble | 18.817 | +0.1485 | −0.0000 | 0.863 | 1.92 |
| **`main`** | — | ensemble | **18.817** | **+0.1485** | — | 0.863 | 1.90 |
| `autoregressive_lag3` | candidate / hierNB | ensemble | 18.813 | +0.1487 | +0.0002 | 0.860 | 1.90 |
| `features_richCalendar` | candidate / boosted | ensemble | 18.812 | +0.1487 | +0.0002 | 0.860 | 1.87 |
| `head_quantileEnsemble` | candidate / boosted | ensemble | 18.776 | +0.1503 | +0.0018 | 0.838 | 1.85 |
| `fitTime_refitAtPredict` | candidate / hierNB | ensemble | 18.690 | +0.1542 | +0.0057 | 0.865 | 1.92 |
| `covariates_rich` | candidate / hierNB | ensemble | 18.638 | +0.1566 | +0.0081 | 0.857 | 1.99 |
| `retrain_everySplit` | setup | ensemble | 18.552 | +0.1651 | +0.0166 | 0.868 | 2.04 |
| `provinces_mergeVientiane` | setup | ensemble | 19.006 | +0.1714 | +0.0229 | 0.865 | 2.24 |
| `provinces_reportingOnly` | setup | ensemble | 18.843 | +0.1861 | +0.0376 | 0.863 | 2.32 |
| `aggregate_populationWeighted` | scoring | ensemble | 28.577 | +0.2288 | +0.0803 | 0.920 | 2.30 |
| `aggregate_caseWeighted` | scoring | ensemble | 88.484 | +0.2320 | +0.0835 | 0.701 | 2.87 |

Raw CRPS is comparable down a block and not across the weighting rows, which is the reason
§4b fixed the skill score as the reported conclusion.

**Our model beats the reference on 22 of the 24, and all three baselines-and-reference tests
on 23.** The two it loses are the two that replace it with a different model of ours; the one
row where a required baseline beats it is `aggregate_caseWeighted`, which batch 13 already
reported.

## 4. The finding: the effort went into the choices that matter least

Ranked by the widest move any child of that kind produces:

| Kind of fork | Rows | Widest move in skill |
|---|---|---|
| the model family | 2 | **0.2209** |
| the pool's own weighting | 1 | **0.1820** |
| the weighting of the headline mean | 2 | 0.0835 |
| the dataset and the evaluation (`02_setup`) | 5 | 0.0376 |
| how a baseline is constructed | 2 | 0.0279 |
| **the eleven forks inside the member families** | 11 | **0.0081** |

The eleven forks inside candidate 1 and candidate 2 span **18.638 to 18.933 CRPS** — a range
of 0.295, about **half the reference's own 0.57 re-run spread**. Nothing in that block can be
attributed to a model at all. Phase C spent batches 8, 9 and 10 selecting among them, and
batch 21's counterfactual spent a whole branch iterating that selection to a fixpoint.

**The mechanism is the pool, and it is not a criticism of the pool.** A linear opinion pool
over four members moves a quarter as far as any one member does when that member's
configuration changes, because three members did not move. The same averaging is why the pool
wins. So the reading is not that those choices were unimportant *as modelling*, but that
**the quantity this project reports is insensitive to them**, and a stability run reports what
moves the reported conclusion.

**The two exceptions say where the sensitivity actually lives.** Which family is on the main
path is worth 0.2209 — more than every setup, scoring and baseline fork put together. And the
one candidate-internal fork that is *not* inside a member, the pool's own weighting, is worth
0.1820: fitting the weights on a held-back year rather than fixing them equal takes the
reported model from 18.817 to **22.838**, behind the reference, and its paired comparison from
1.90 standard errors to **0.48**. Batch 11 measured that fork as 4.021 CRPS and called it the
batch's most useful result; on the skill scale the whole set is now read on, it is the second
largest single-fork move the project has.

## 5. The two weighting rows had been reporting the main path's spread

Under the fix:

| Row | Paired mean diff | SE (split-clustered) | Noise floor | Standard errors |
|---|---|---|---|---|
| `main` (unweighted) | −3.282 | 1.726 | 0.565 | 1.90 |
| `aggregate_populationWeighted` | −8.478 | 3.693 | 0.835 | 2.30 |
| `aggregate_caseWeighted` | −26.732 | 9.321 | 5.502 | 2.87 |

Before the fix both weighted rows carried the top line's three numbers verbatim.

**The noise floor grows with the weighting, and that is what keeps the rows comparable.** The
floor is the largest paired difference between two repeats of the same unseeded reference
model, so re-weighting the cells re-weights the reference's own sampler along with everything
else. Case weighting concentrates the mean on outbreak months, where every model's CRPS is
large and the reference's draw-to-draw variation is largest: 5.502 CRPS, ten times the
unweighted floor. The pool's margin grows faster than the floor does, which is why the
case-weighted row is the **strongest separation in the project at 2.87 standard errors** while
also being the row where a required baseline beats the reported model.

**Both facts are true of the same row and neither is the headline.** The plan defines the
headline against Chap's own unweighted mean; §2's rule that a badly calibrated CRPS winner has
not won is why the coverage sits beside it, and under case weighting the pool's 10–90 coverage
is 0.701 against a nominal 0.80 — the reported model is over-dispersed on the quiet months
that dominate the unweighted mean and under-dispersed on the outbreak months that dominate
this one.

