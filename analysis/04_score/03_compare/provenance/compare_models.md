# Provenance — the leaderboard and the paired comparison against the reference

```
result:              results/main/leaderboard.csv
                     results/main/paired_vs_reference.csv
                     results/main/paired_summary.csv
                     results/main/paired_by_split.csv
                     results/main/reference_repeat_noise.csv
                     results/main/comparison_notes.json
script:              scripts/compare_models.py
                     sha256:6d6748b30ef2c185f6742f1e7586f3f85f4c5614f4dd6b200b94c97e2d8ae9d2
invocation:          "$PYTHON" scripts/compare_models.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/04_score/01_collect/results/main/metrics_cell.csv
                     analysis/04_score/01_collect/results/main/models.csv
                     analysis/04_score/02_aggregate/a_unweighted/results/main/metrics_summary.csv
                     (resolved by searching for the one child of 02_aggregate with
                     results under this combination)
                     analysis/03_models/**/results/main/run_cost.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every figure is a deterministic statistic of stored per-cell
                     scores. No resampling is used: the clustered standard errors are
                     computed in closed form, which is why there is nothing to seed.
                     Project seed 20260822 unused.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-26
```

**What it establishes.** Two things. The leaderboard, assembled from the stored scores and
the stored run costs, which is the file phase C adds candidates to and the one the plan
requires never to be typed. And the answer to the question batch 4 left open and batch 5
made this batch's reason for existing: **whether a paired per-cell comparison on 371 cells
can separate two models at all.**

**Why paired, and why four ways.** Batch 4 measured the split-to-split standard error of the
reference's own CRPS at 5.65, a quarter of its mean, and observed that no plausible model
difference clears that. But that variation is mostly the difficulty of the period, common to
both models, and it cancels cell by cell. What is left is what this node measures, and it
measures it four ways because the easy answer is the wrong one:

- the per-cell standard error, which assumes 371 independent observations. They are not
  independent — three lead times of the same forecast and neighbouring months of the same
  province move together — so this figure flatters the comparison and is reported as the
  optimistic bound rather than as the answer;
- the same standard error clustered by province and by split, which allows arbitrary
  correlation inside a cluster. With sixteen provinces and eight splits this is a small
  number of clusters, so it is indicative rather than exact;
- the comparison at the split level, over eight paired numbers, which needs no independence
  assumption inside a split at all;
- **the noise floor**: the identical paired statistic computed between two repeats of the
  reference against itself. Because the reference is unseeded, two of its repeats differ by
  its sampler and by nothing else, so the largest paired difference among its own repeats is
  a difference this evaluation demonstrably cannot attribute to a model. It is the
  comparison's resolution, computed in the same units as the comparison, on the same cells.

**No significance test is reported and none is implied.** The plan settled before any number
existed that statistical significance is not attainable here and is not to be suggested
(§4b, human-set). What is reported is the spread and a plain statement of what it can
distinguish; "we cannot separate these two" is one of the answers.

alternatives-considered: a paired bootstrap over provinces would give a confidence interval
without the closed-form clustering assumption and was not run — it would introduce
randomness into a node that currently has none, and with sixteen clusters it would be
resampling the same small set. It is the obvious extension if the clustered figures turn out
to be load-bearing, and it is recorded here as not run rather than not considered. A
Diebold-Mariano test was rejected: it is a significance test, and the plan forbids implying
significance. Comparing against each reference repeat separately *instead of* against their
mean was rejected in favour of doing both — the mean is the denominator the conclusion uses
and the per-repeat comparisons are what calibrate it.

agency: agent-autonomous. That the comparison must be paired rather than unpaired is batch
4's finding (agent-autonomous, recorded there); computing it, and computing the noise floor
from the reference's own repeats rather than assuming a resolution, is this batch's.

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

Regenerated on `main` after the promotion, from the promoted candidate's scores. The sweep
combinations do not reach this node: batch 9 stops at `02_aggregate`, because a conclusion
per sibling is the phase-D deliverable and producing nine of them here would report the
stability answer before the manifest that makes it honest has been frozen.

**What moved.** The candidate's paired difference against the reference fell from **4.002**
CRPS to **1.599**, and its split-clustered standard error is **1.551**, so the difference
is **1.03 standard errors** -- against 3.62 for the batch-8 configuration. The comparison
that batch 8 could resolve, this one cannot: on the development backtest our candidate and
the field's own model are not distinguishable. It wins 41 % of cells and 2 of 8 splits.

alternatives-considered: none new; the node's own choices are batch 7's.

agency: agent-autonomous.

## Batch 10 — the family comparison, under `family_boosted`

```
result:              family_boosted/leaderboard.csv
                     family_boosted/paired_vs_reference.csv
                     family_boosted/paired_summary.csv
                     family_boosted/paired_by_split.csv
                     family_boosted/reference_repeat_noise.csv
                     family_boosted/comparison_notes.json
script:              scripts/compare_models.py
                     sha256:6d6748b30ef2c185f6742f1e7586f3f85f4c5614f4dd6b200b94c97e2d8ae9d2
invocation:          bash analysis/04_score/03_compare/run.sh
                     with COMBO=family_boosted and COMBO_BASE=main
inputs:              01_collect/results/family_boosted/metrics_cell.csv
                     02_aggregate/a_unweighted/results/family_boosted/*.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; a deterministic comparison of stored scores.
commit:              6cb1163
instructions-commit: cf97b81
produced:            2026-08-28
```

**Why this node runs for a combination that is not `main`, when the batch-9 sweep stopped at
`02_aggregate`.** The reason batch 9 stopped there stands: a `conclusion.json` per sibling
is the phase-D deliverable and producing one before the manifest is frozen would report the
stability answer early. This node produces no conclusion — it produces the **leaderboard**,
which phase C requires to be maintained by a script from the stored outputs and never typed,
and the paired comparison that says what the leaderboard can resolve. Candidate 2 does not
appear on `main`'s leaderboard, because it is a sibling family and does not run there, so
without this the project would have a candidate whose score had never been put beside the
reference's by the node that exists to do it. The root's `conclude.py` was **not** run for
this combination.

**What it establishes.** Nine leaderboard rows, of which `boosted` is first at mean CRPS
**20.771** — ahead of the reference's 22.098, candidate 1's 23.698, climatology's 24.337 and
persistence's 24.879. The paired difference against the reference is **−1.327** with a
split-clustered standard error of **1.110**, against a noise floor of 0.565: the first
margin in this project on the right side of zero, and the first to clear the floor.

**It still does not separate the two models.** 1.20 standard errors is not a distinction,
and the plan forbids implying that it is. What has changed since batch 9 is the sign of the
point estimate, not the resolution of the comparison.

alternatives-considered: running the root's `conclude.py` under this combination so that
candidate 2 has a `conclusion.json` (rejected — that is the phase-D artifact and its
production before the manifest is frozen is what the freeze discipline exists to prevent);
leaving candidate 2 unscored at this node and reading its leaderboard position out of the
fork sweep's table (rejected — the sweep's table is copied from `02_aggregate` and carries
no paired comparison, so the question of what the margin can resolve would have gone
unanswered for the only model of ours that has ever led).
agency: agent-autonomous

---

## Batch 11 — `main` after the promotion, and the ensemble's own combination

```
result:              main/comparison_notes.json
                     main/fig_accuracy_and_spread.csv
                     main/fig_accuracy_and_spread.png
                     main/fig_accuracy_and_spread_preaggregation.csv
                     main/fig_crps_by_location.csv
                     main/fig_crps_by_location.png
                     main/fig_crps_by_location_preaggregation.csv
                     main/fig_paired_vs_reference.csv
                     main/fig_paired_vs_reference.png
                     main/fig_paired_vs_reference_preaggregation.csv
                     main/leaderboard.csv
                     main/paired_by_split.csv
                     main/paired_summary.csv
                     main/paired_vs_reference.csv
                     main/reference_repeat_noise.csv
                     family_ensemble/comparison_notes.json
                     family_ensemble/fig_accuracy_and_spread.csv
                     family_ensemble/fig_accuracy_and_spread.png
                     family_ensemble/fig_accuracy_and_spread_preaggregation.csv
                     family_ensemble/fig_crps_by_location.csv
                     family_ensemble/fig_crps_by_location.png
                     family_ensemble/fig_crps_by_location_preaggregation.csv
                     family_ensemble/fig_paired_vs_reference.csv
                     family_ensemble/fig_paired_vs_reference.png
                     family_ensemble/fig_paired_vs_reference_preaggregation.csv
                     family_ensemble/leaderboard.csv
                     family_ensemble/paired_by_split.csv
                     family_ensemble/paired_summary.csv
                     family_ensemble/paired_vs_reference.csv
                     family_ensemble/reference_repeat_noise.csv
script:              scripts/compare_models.py
                     sha256:6d6748b30ef2c185f6742f1e7586f3f85f4c5614f4dd6b200b94c97e2d8ae9d2
invocation:          bash analysis/04_score/03_compare/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-28
```

**What it establishes.** The project's reported comparison, and the first one that goes our
way. On `main`: the ensemble at mean CRPS **18.817** against the reference's 22.098, a paired
per-cell difference of **−3.282** with a split-clustered standard error of **1.726**, winning
43 % of individual cells. That is 1.90 standard errors and nearly six times the 0.565 CRPS
noise floor the reference's own unseeded repeats occupy — a margin large enough to be
attributable to a model, and short of separating the two. The leaderboard under `main` now
carries eight rows rather than nine, for the reason in the record at `01_collect`.

**The win rate and the mean point in different directions, and that is the finding under
them.** The pool wins only 43 % of cells while being 3.282 CRPS better on average, so what it
buys is not being right more often — it is being much less wrong where it is wrong. A pool is
a hedge, and this is what a hedge looks like in a paired comparison.

alternatives-considered: reporting the comparison against the reference's best repeat rather
than its four-repeat mean (rejected in batch 7 and unchanged: the mean is the denominator that
does not move with an external model's sampler, and the repeats are reported beside it).
agency: agent-autonomous

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/leaderboard.csv
                     results/$COMBO/paired_vs_reference.csv
                     results/$COMBO/paired_summary.csv
                     results/$COMBO/paired_by_split.csv
                     results/$COMBO/reference_repeat_noise.csv
                     results/$COMBO/comparison_notes.json
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 13, and
                     COMBO_BASE=main
combinations:        aggregate_caseWeighted, aggregate_populationWeighted, popColumn_backCast, provinces_mergeVientiane, provinces_reportingOnly, retrain_everySplit, trainingWindow_from2004
inputs:              unchanged in kind; each combination's own inputs are recorded in the
                     specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/04_score/03_compare
produced:            2026-08-29
```

**What it establishes.** The leaderboard and the paired comparison under each row. **A caveat belongs on the two scoring rows**: everything this script computes — the paired difference, the clustered standard errors, the split-level comparison and the noise floor — is computed from the unweighted per-cell file, while the leaderboard's `mean_crps` comes from whichever aggregation child ran. So under `aggregate_populationWeighted` and `aggregate_caseWeighted` the headline is weighted and the spread beside it is not. That is recorded here, in `04_score/02_aggregate/claim.md` and in batch 13's report, and assigned to batch 14; it is not a defect in these files, it is a limit on how they may be read.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`. `/validate invariants` accepts that form only
for combinations the stability manifest names, and its `combos` check keeps that set closed.

agency: agent-autonomous.
information: agent-retrieved.


---

## Batch 22 — the two baseline-fork combinations

```
result:              results/$COMBO/leaderboard.csv · paired_summary.csv ·
                     comparison_notes.json and the split-level files beside them
combinations:        climatology_frozenWindow, persistence_negBinomialFloor
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 22, and
                     COMBO_BASE=main
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; the step is arithmetic on the collected per-cell scores
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-29
```

**What it establishes.** Under `persistence_negBinomialFloor` the paired difference between
the reported pool and the reference is **−2.664 CRPS with a split-clustered standard error of
1.351** — 1.97 standard errors, which is *more* than the main path's 1.90 even though the pool
scores worse there. The gap narrowed and its spread narrowed further. It still does not
separate the two models and is not reported as though it did.

The same file records that the **persistence baseline itself** beats the reference on this
row: −1.400 CRPS, standard error 1.424, 0.98 standard errors, cell win rate 0.518.

**The known gap is unchanged and does not bite here.** This step computes its paired spread
from the unweighted per-cell file while the leaderboard mean follows the weighting fork; both
batch-22 rows are unweighted, so the two agree on them. Batch 14 still owns the fix.

alternatives-considered: none at this node.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.

---

## Batch 14 — the paired comparison follows the weighting fork, and the twelve candidate and family combinations

```
result:              results/$COMBO/leaderboard.csv · paired_vs_reference.csv ·
                     paired_summary.csv · paired_by_split.csv ·
                     reference_repeat_noise.csv · comparison_notes.json
                     and the three figures beside them
combinations:        main, aggregate_caseWeighted, aggregate_populationWeighted,
                     family_hierNB, family_boosted, weighting_crpsWeighted,
                     autoregressive_lag3, covariates_lagged, covariates_rich,
                     features_richCalendar, fitTime_refitAtPredict,
                     head_quantileEnsemble, observation_negBinomial,
                     observation_zeroInflated, population_covariate, population_ignored,
                     yearVariance_shared
script:              scripts/compare_models.py
                     sha256:f75ea678438f4a8b28dc98c2a235386b1a8534258dae06955f268c5d641de83e
invocation:          bash analysis/04_score/03_compare/run.sh, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 14 and
                     COMBO_BASE=main; on `main`, the step alone with neither set
inputs:              01_collect/results/$COMBO/metrics_cell.csv · models.csv
                     the one child of 02_aggregate with results under this combination:
                     its metrics_summary.csv and, where it is a weighted child, its
                     weights.csv
                     analysis/03_models/**/results/$COMBO/run_cost.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; the step is arithmetic on the collected per-cell scores
commit:              87440bc (the script), 3fb1280 (the combinations)
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-30
```

**What changed in the script.** The caveat batch 13 recorded here and batch 22 repeated is
closed. Everything this node computes — the paired difference, the three standard errors,
the split-level comparison and the noise floor — is now taken under the weighting the fork
at `02_aggregate` chose, read from that child's own `weights.csv` rather than recomputed.
The leaderboard always followed the fork, because it is that child's summary; the paired
figures did not, so a weighted row reported a weighted CRPS with an unweighted spread
against it and nothing in the file said which was which. Every file this node writes now
carries a `weighting` column, and `comparison_notes.json` a `weighting` field.

**The unweighted case is its own code path**, for the reason
`04_score/scripts/lib/aggregate.py` gives one node up: weighting by a vector of ones and
taking a mean are the same number in arithmetic and not always the same float, and these
are the figures the project reports. Verified on `main` before anything else in this batch
ran — every existing value in `paired_summary.csv`, `paired_by_split.csv`,
`reference_repeat_noise.csv` and `fig_paired_vs_reference.csv` is unchanged, and the only
difference is the added column.

**Within a split the cells carry their weights; across splits the eight numbers count
equally.** The split-level comparison exists as the figure that assumes nothing about
independence inside a split, and weighting the splits by their totals would collapse it
into the cell-level statistic it is reported beside.

**What it establishes on the two weighting rows.** Under case weighting the pool's paired
difference against the reference is **−26.732 with a split-clustered standard error of
9.321** against a noise floor of 5.502 — 2.87 standard errors, the largest margin in this
project. Under population weighting, −8.478 ± 3.693 against a floor of 0.835, or 2.30.
Both are larger than `main`'s 1.90, and both were previously reported as `main`'s own
−3.282 ± 1.726, which is what the defect amounted to: the same comparison copied under
three headline means. The noise floor grows with the weighting because the reference's own
sampler is re-weighted along with everything else, which is what keeps the two comparable.

**What it establishes on the twelve candidate and two family rows.** The eleven forks
inside the two member families move the paired difference between 1.85 and 1.99 standard
errors around `main`'s 1.90. The pool's own weighting fork takes it to **0.48** — the
CRPS-fitted pool is 22.838 against the reference's 22.098, and the comparison stops
resolving anything at all. `family_hierNB` is 1.03 and `family_boosted` 1.20, both
reproducing what batches 9 and 10 measured for those models when they were the main path.

alternatives-considered: weighting the split-level statistic across splits as well as
within them (rejected above, and recorded in the script's own docstring); leaving
`win_rate_cells` weighted (rejected — it is a count of cells, its name says so, and a
weighted version of it would be a different quantity reported under an unchanged name);
recomputing the weights here from the analysis dataset rather than reading the aggregation
child's `weights.csv` (rejected — a second place that knew what a cell is worth is a second
place that can be wrong about it, which is the argument `aggregate.py` was created on).

agency: agent-autonomous. The defect was found by batch 13 reading its own output and
recorded in three places before this batch existed; the fix, and the choice of which
statistics follow the weighting, are this batch's.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.

## Batch 18 correction — "the eleven forks" are eleven combinations over eight forks

Appended rather than edited into the batch-14 section above, because a provenance record
that quietly changes what it said is worth less than one that is wrong in a visible way.

**What the batch-14 section says.** "What it establishes on the twelve candidate and two
family rows. The eleven forks inside the two member families move the paired difference
between 1.85 and 1.99 standard errors around `main`'s 1.90."

**What is true.** The two member families hold **eight** forks between them —
`a_hierNB/{01_observation, 02_covariates, 03_population, 04_fitTime, 05_autoregressive,
06_yearVariance}` and `b_boosted/{01_features, 02_head}`. Those eight forks have **eleven**
non-main children between them, which is where the eleven comes from: it is a count of
perturbed *combinations*, one per non-main child, and the twelfth candidate row is
`c_ensemble/01_weighting`, which is not inside a member. Both numbers are in
`analysis/05_stability/results/sensitivity_by_fork.csv`: eight rows have `owner` in
`{a_hierNB, b_boosted}`, and their `rows` column sums to eleven.

**Nothing computed changes.** The range 1.85 to 1.99 is over the eleven combinations and is
correct as stated; only the noun is wrong. No figure in `leaderboard.csv`,
`paired_summary.csv` or `comparison_notes.json` is affected, and none was recomputed.

**Where it came from, and how far it spread.** Batch 14's report carries a table whose
column is a row count and whose label reads "the eleven forks inside the member families";
the label was then copied into `readme-at-start.md`, `analysis/05_stability/claim.md`, claim
C3 of the collection, and this record. Batch 18's `/validate outsider` run found it by
counting the rows of `sensitivity_by_fork.csv` rather than reading any of them. The live
records are corrected; the batch reports and the plan's §4b keep what they said, because
they are accounts of what was established at the time and rewriting them would hide that
this happened.

agency: agent-autonomous. The error and the correction are both the agent's; the outsider
check that surfaced it is the method's.
information: agent-retrieved — the counts are read from `sensitivity_by_fork.csv`.

## Batch 18 correction — the batch-14 commit `9993d37` is not in the history; read `87440bc`

Appended rather than edited in place, because a provenance record that silently changes an
address it once gave is worth less than one that shows the address went bad.

The sections above named **`9993d37`** as batch 14's "before the run" commit. That commit is
not an ancestor of `HEAD` and is on no branch: batch 14's history was rewritten after it was
made, and the commit that survived is **`87440bc`** — same subject, same author timestamp,
and **the same tree**, `f473a16ee75d23f4483d3d101b18119cd224b6d7`. So the *state* those
sections describe is exactly right and only the address was dead.

**Their `commit:` lines have therefore been corrected in place**, from `9993d37` to
`87440bc`, and this section is the record that it happened. Appending alone was not enough:
a provenance record exists so a reader can check out what it names, and one that keeps a
dead hash and a footnote saying to read a different one has not been repaired. Nothing else
in those sections is touched, and no result was recomputed — the two commits have the same
tree, so the state they describe is byte-identical either way.

It looked fine for eight days for two compounding reasons, both now closed in
`AI-internal/useful-scripts/check_invariants.py`. The check tested `git cat-file -e`, which
answers whether an object is in the store — and an orphaned object stays in the store of the
tree that orphaned it, and is copied wholesale by a *local* `git clone`, which hardlinks the
object directory. It would have vanished on the first push, which is batch 19. The check now
requires ancestry of `HEAD`. And the pattern was anchored to a `commit:` line carrying one
bare hash, so a line like `commit: 9993d37 (the script), 3fb1280 (the combinations)` was
skipped entirely — a record that annotated its hashes was the one the check never read. It
now takes every hash on every `commit:` line.

Found by batch 18's `/validate outsider` run, which walked the headline result's chain from
`conclusion.json` back to the archived dataset and tested each link rather than reading it.

agency: agent-autonomous.
information: agent-retrieved — `git merge-base --is-ancestor`, `git rev-parse <c>^{tree}`.
