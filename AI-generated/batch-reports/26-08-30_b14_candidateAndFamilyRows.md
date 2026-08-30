# Batch 14 — `/perturb run`: the candidate and family rows, and tier 2

Generated from [[26-08-22_dengueForecastingCase]] — iteration 14

**Phase D · Status: done — produced · Executed 2026-08-30 to 08-31**

---

Three defects fixed, a fourth found by running into it, an assembler lift two batches had
deferred here, the fourteen rows that finish tier 1, and the eight pairs of tier 2. **32 of
the manifest's 33 rows now have a conclusion** — the 33rd perturbs nothing — so phase D's
development set is complete and batch 15 has a distribution to report.

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

**The mechanism is the pool, and it is not a criticism of the pool.** Phase C's own sweeps
record what these same forks are worth to a family *on its own*
(`AI-generated/candidate-forks/round2_promoted/fork_leaderboard.csv` and
`boosted_round1/fork_leaderboard.csv`). Candidate 1's observation model moves it from 23.698
to **24.299** CRPS there, a swing of 0.601; the same fork moves the pool from 18.817 to
18.919, a swing of **0.102**. Three of the pool's four members did not move, and a linear
pool's spread is the mean of its members' spreads plus the spread between their means — so a
change confined to one member reaches the reported number damped.

**Damped, but not simply scaled, and one row reverses sign.** Candidate 2's quantile head
makes candidate 2 *worse* on its own, 20.771 to 20.960, and makes the pool *better*, 18.817
to 18.776. A member that is worse but disagrees differently can improve the pool, which is
the same fact batch 22 found from the other side when a sharper persistence member made a
worse pool.

So the reading is not that those choices were unimportant *as modelling* — they move their
own model by up to 0.601 CRPS. It is that **the quantity this project reports is insensitive
to them**, and a stability run reports what moves the reported conclusion.

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

## 6. Tier 2: the pairs are not the sum of their parts

The rule was fixed and hashed in batch 12, before any tier-1 row had run; batch 13 changed
*when* it may be applied, not what it says, and its sha256 is the one written that day. Applied
to a completed tier 1 it selects **group S** = the two highest-ranked `setup` rows, **group M**
= the two highest-ranked rows of the kinds that move our model, **group A** = the highest-ranked
`scoring` row, and every cross-group pair. No group fell short.

| Pair | Our model | CRPS | Skill | Δ vs main | If they added | **Interaction** | 10–90 cov. |
|---|---|---|---|---|---|---|---|
| `provinces_reportingOnly × aggregate_caseWeighted` | ensemble | 89.279 | +0.1662 | +0.0177 | +0.1211 | **−0.1033** | 0.693 |
| `provinces_mergeVientiane × aggregate_caseWeighted` | ensemble | 90.410 | +0.2239 | +0.0754 | +0.1064 | **−0.0310** | 0.693 |
| `provinces_mergeVientiane × weighting_crpsWeighted` | ensemble | 23.092 | −0.0285 | −0.1770 | −0.1591 | **−0.0179** | 0.725 |
| `provinces_mergeVientiane × family_hierNB` | hier_nb | 23.656 | −0.0509 | −0.1994 | −0.1980 | **−0.0014** | 0.701 |
| `weighting_crpsWeighted × aggregate_caseWeighted` | ensemble | 108.100 | +0.0618 | −0.0867 | −0.0985 | **+0.0117** | 0.468 |
| `family_hierNB × aggregate_caseWeighted` | hier_nb | 112.258 | +0.0257 | −0.1228 | −0.1374 | **+0.0145** | 0.458 |
| `provinces_reportingOnly × family_hierNB` | hier_nb | 23.602 | −0.0049 | −0.1534 | −0.1833 | **+0.0299** | 0.704 |
| `provinces_reportingOnly × weighting_crpsWeighted` | ensemble | 22.580 | +0.0465 | −0.1020 | −0.1444 | **+0.0424** | 0.730 |

`delta_skill_additive` and `interaction` are columns of `conclusions.csv`, computed by
`collect_conclusions.py` from the table's own `delta_skill_vs_main`; a pair's two rows are
matched by the fork and child it moved, not by splitting its name.

**The interaction runs from −0.1033 to +0.0424, and the extreme is larger than either main
effect behind it.** Removing the two provinces with no evaluable cell is worth **+0.0376**
alone. Weighting the headline mean by cases is worth **+0.0835** alone. Additively that is
+0.1211; together they come to **+0.0177**, which is the main path to within a fifth of the
smallest fork effect in tier 1. Two choices that each flatter the reported model almost exactly
cancel when both are taken.

The mechanism is visible in the numbers rather than inferred: both moves work by re-weighting
what the mean is over. The province filter drops two provinces that contribute no evaluable
cell, and case weighting drives the mean onto the outbreak months of the large provinces —
which is largely the same re-weighting reached twice, so taking it twice does not do it twice.

**Batch 12's argument for not cutting tier 2 was right, and this is the third demonstration.**
Batches 9 and 21 each found that one-at-a-time fork effects do not compose in model
configuration; tier 2 finds it across kinds of fork, on the reported conclusion. **A stability
report built from one-at-a-time rows alone would have been wrong about the pairs by up to 0.10
of skill** — two thirds of the entire main-path skill score.

## 7. The distribution, over all 32 analyses

| | |
|---|---|
| Analyses with a conclusion | **32** of the manifest's 33 rows |
| The 33rd | `family_ensemble` — the main path's own choice under its own name, which perturbs nothing |
| Skill score | **−0.0724 to +0.2320**, main path +0.1485 |
| Our model beats the reference | **27 of 32** |
| Our model beats both required baselines | **27 of 32** |
| 10–90 interval coverage | **0.458 to 0.920**, nominal 0.80 |

**The five rows our model loses on are the five that replace it or re-weight its weights.**
`family_hierNB` alone and in two pairs, and `weighting_crpsWeighted` alone and paired with
`provinces_mergeVientiane`. No choice about the data, the evaluation, the scoring or the
baselines takes our model below the reference on any row.

**The five rows a required baseline beats it on are the five case-weighted rows** — every
combination in which case weighting appears, without exception. Batch 13 reported this for the
single row it had; with five it is not a property of one analysis.

**Calibration moves far more than the score does.** 10–90 coverage runs from 0.458 to 0.920
against a nominal 0.80 while the skill score stays positive on 27 of 32 rows. The two extremes
are both case-weighted: the pool under population weighting is at 0.920, badly over-dispersed,
and candidate 1 under case weighting at 0.458, badly under-dispersed. §2's rule that a badly
calibrated CRPS winner has not won bites hardest exactly where the CRPS looks best.

## 8. Cost, and what the cost model is still wrong about

| | Planned | Actual | Ratio |
|---|---|---|---|
| Tier 1, this batch's fourteen rows | 1 224 s | 1 293 s | 1.06 |
| Tier 2, eight pairs | 6 047 s | 5 703 s | 0.94 |
| Per row, worst over-estimate | | | 0.52 |
| Per row, worst under-estimate | | | 1.91 |

**Batch 13's finding repeats exactly.** The total is right to within 6 % in both directions and
no individual row is. Batch 12's model sums each row's parts as measured under `main` and cannot
know that a row changes how much work a part does. The whole of phase D has now cost about
**3.2 hours of the 12-hour budget** across tier 1 and tier 2 on development, and 87 % of tier
2's time was the reference model running four unseeded repeats through an amd64 image under
emulation, for the one model the plan forbids perturbing.

## 9. What went wrong, kept

**The fourteenth row failed at its second step, and the design is why it was caught.** The
driver's step list ran the moved fork child and then the family's `run.sh`, which runs every
fork below it at the main path. On the one row whose moved fork belongs to the family that
runs, both children of that fork ended up under one combination, and the pool's assembler
refused them. The refusal is the invariant working — it is the same check that would have
caught a doubled member — and what was wrong was the driver. Two seconds, one log, and the fix
is its own commit so the failure is in the history rather than smoothed out of it.

**The failed attempt left a file that should not exist**: a `model_option_spec.json` for the
weighting fork's *other* child under that combination. It was removed before the re-run, which
is the same care batch 13 recorded for the reference node's half-complete results directory.

**A stale committed file, found on the way past.** `member_selection.json` under `main` had been
committed by batch 22 in a state written before that batch's own two contract directories
existed, so it did not record them as contracts considered and rejected. Re-running either
version of the script produces the corrected record, which is what establishes it as staleness
rather than a consequence of this batch's change; `members.json`, the file the reported model's
configuration hashes, was unchanged.

**And one thing this batch was expected to close and did not.** Batch 22 left the per-split
diagnostics gap here, on the reasoning that batch 14 "touches `chap_eval.py` and re-runs
everything it configured". It touched the *assemblers*, not `chap_eval.py`, and the premise does
not hold: a model can only write per-split diagnostics from inside its own contract directory,
and changing a file there re-hashes the model, which re-hashes the pool's `members.json`, which
re-hashes the reported model's configuration — so closing the gap forces a re-run of the
reported analysis and of every combination in the frozen manifest. That is not a batch-14
change; it is a phase-E or post-holdout one, and it is recorded as deferred rather than done.

## 10. Storage, measured now that the manifest has run

| | Measured |
|---|---|
| Everything git tracks, whole repository | **1.1 GB** |
| Everything under `analysis/**/results/` | 1.1 GB |
| `analysis/**/work/` — chap-core's per-split run directories | **8.8 GB**, gitignored |

**The repository is 1.1 GB and the disk holds 10 GB, and the whole difference is
disposable.** `work/` is what chap-core builds per split, a `.venv` per model per
combination included; it has been gitignored since batch 7, every node clears its own before
running, and nothing reads it after a run finishes. Against the human's settlement of
2026-08-29 the tracked repository is comfortably inside "a few gigabytes", and since the
holdout backtest is four splits rather than eight, phase E will not change that.

## 11. Decisions taken in this batch

Full table in the plan's §4b, dated 2026-08-31. The four worth arguing with:

| Decision | Basis |
|---|---|
| A member family's fork is run only where the combination cannot already resolve it, from `COMBO` **or** `COMBO_BASE` | The alternative — running the main child whenever nothing exists under `COMBO` alone — would re-run every fork of every member family on every candidate row and record a combination as having taken choices it inherited. It also means batch 22's two rows and this batch's twelve record their inherited choices differently; the configurations are identical, so no number moves, and the rows are not re-run for bookkeeping |
| The driver reads a family's own scripts out of its `run.sh` rather than carrying a list | A list in the driver is a second copy of `run.sh` free to fall out of step with it, which is the objection the driver's own docstring makes to a second implementation of the analysis. Reading the tree instead of carrying a summary of it is the same choice `inventory.py` made about forks |
| `interaction` is computed by `collect_conclusions.py` into `conclusions.csv`, not in this report | Tier 2's entire content is whether the pairs add up. A number computed in prose from two columns has no provenance, which is `AGENTS.md` §1 exactly, and the temptation to do it in prose is strongest for arithmetic that looks too simple to need a file |
| The per-split diagnostics gap is **not** closed, against batch 22's expectation | Its premise was that this batch touches `chap_eval.py`. It does not — the lift was of the assemblers — and a model can only write per-split diagnostics from inside its own contract directory, which re-hashes the model, the pool's membership and the reported model's configuration. Closing it forces a re-run of the reported analysis and of the frozen manifest, which is not a change to make between the manifest freezing and the holdout opening |

## 12. Compliance for this batch

| Rule | What was done |
|---|---|
| 1 — track results | Eight provenance records: new sections at `03_compare`, the root's `conclude`, all three candidate assemblers, `prepare_members`, `run_hier_nb`, `b_crpsWeighted/choose_weighting` and the stability driver, one for tier 1 and one for tier 2. Every one names its script's sha256, its inputs, its environment, its commit, its alternatives-considered and its agency |
| 2 — no manual manipulation | No result was edited. The two weighting rows and the fourteenth row were **re-run at the correcting commit** rather than adjusted, which is what Rule 2 prescribes and what batch 22 did for the same reason |
| 3 — pinned environments | Unchanged: `environment/` at CPython 3.13.0 and `chap-core==2.1.0`; the reference at its pinned image digest |
| 4 — version control | Six commits: the fixes before the run, the twelve stale directories removed, the tier-1 run, the tier-2 selection, the tier-2 run, and the record. The instruction files were not changed by this batch |
| 5 — intermediates | Every combination keeps its `eval.nc`, its per-cell scores, its configuration and its specification. Nothing was pruned |
| 6 — seeds | Unchanged and verified unchanged: candidate 1 at 849487747, candidate 2 at 1877199108, candidate 3 at 1648567750, each re-derived by the lifted assembler and each producing a byte-identical configuration |
| 7 — plots | The three figures at `03_compare` are regenerated per combination with their plotted values and pre-aggregation values beside them, as before |
| 8 — hierarchical report | Not this batch; batch 17 |
| 9 — claims | Not this batch. The claim collection is written in batch 17 and the stability claims belong to `/perturb report` in batch 15, which is where the distribution is reported rather than accumulated |
| 10 — release | Not this batch |
| Validation | `/validate invariants` passes: tree, provenance, plots, seeds, claims, combos, crossing, and a clean tree at the closing commit |

## 13. What is still unknown

- **Whether the holdout behaves like development.** Everything here is one year of a real
  epidemic away from the number the project reports. The manifest is frozen and batch 16 runs
  it once.
- **Whether the interaction structure survives to the holdout.** Eight pairs on development
  say the forks do not compose; nothing says the same pairs interact the same way in 2010.
- **What tier 2 cannot say about setup.** Both group-S rows turned out to be children of one
  fork, `03_provinces`, so tier 2 crosses the province filter with the model choices and says
  nothing about how the training window, the population column or the retraining frequency
  interact with them. The rule was fixed before that was knowable and is not adjusted for it.
- **Whether the reported main path should have been the pool at all.** Two rows now say a
  different family scores worse, one says a required baseline scores better under a defensible
  weighting, and batch 22's row says a rejected baseline construction beats the reference.
  Phase C is closed and none of it is promoted, which is the ordering the design exists to
  protect — but the record now contains the argument for reopening it, and that is the human's
  call, not mine.

## 14. For the human

- **The most useful thing in this batch is not a score.** It is that the eleven forks phase C
  spent three batches choosing among move the reported conclusion by less than half the
  reference model's own re-run noise, while the one choice phase C made almost in passing —
  which family goes on the main path — moves it twenty-seven times further. If the manuscript
  keeps one number from phase D, that ratio is the one.
- **Tier 2 earned its place.** The largest interaction, −0.1033, is bigger than either main
  effect behind it, so a one-at-a-time stability report would have been wrong about that pair
  by two thirds of the whole main-path skill score. Batch 12 declined to cut tier 2 on the
  strength of two prior demonstrations that forks do not compose; this is the third and the
  first on the reported conclusion.
- **Four fork-blind steps, and I think that is now all of them.** Every one was a step that
  discovered something from the tree, written when every fork had exactly one child that did
  anything. Three were found by planning or by reading output and one by running into it. The
  pattern is worth a sentence in the manuscript: the defect class is created by the tree
  growing, not by any one script being careless, and it is invisible until a second child
  exists.
- **One thing I did not do that batch 22 expected of me**, in §9 and §11: the per-split
  diagnostics gap stays open, because closing it would force a re-run of the reported analysis
  between the manifest freezing and the holdout opening. If you would rather have it closed
  before phase E, say so and I will append a batch for it — it needs the reported analysis
  re-run and the manifest's development rows re-run with it, which is about four hours.
- **Phase D has one batch left.** Batch 15 is `/perturb report`, which turns these 32 rows
  into the distribution the phase exists to produce, puts the driver into `analysis/run.sh`
  now that every row can run, and freezes the holdout manifest. Then the seal comes off.
