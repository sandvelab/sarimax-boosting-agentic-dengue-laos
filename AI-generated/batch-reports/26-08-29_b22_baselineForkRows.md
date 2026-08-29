# Batch 22 — `/perturb run`: the two baseline forks' children

Generated from [[26-08-22_dengueForecastingCase]] — iteration 22

**Phase D · Status: done — produced · Executed 2026-08-29**

---

The last two tier-1 rows that needed a model built before they could run. Both baseline forks
now carry two children, ten of the manifest's twenty-four tier-1 combinations have
conclusions, and the manifest's planner reports **zero unbuilt children** for the first time.

**The two rows are the extremes of the stability set.** Freezing the climatology's estimation
window is worth **0.532 CRPS** to that baseline and **0.0025 of skill** to the reported model
— the smallest move of any row run. Wrapping the persistence point in a fitted negative
binomial rather than in the empirical distribution of past changes is worth **4.181 CRPS** to
that baseline and **−0.0279 of skill** to the reported model — the largest, and the first
that is downward by more than the reference's own re-run noise.

**The reported analysis stands on the worse of two published constructions of a baseline the
plan requires.** The parametric persistence baseline scores **20.698** against the main path's
24.879, and **beats the reference model** at 22.098. Batch 6's reasoning for rejecting it was
sound and its conclusion was wrong.

**And the pool that contains it is better off for that.** With the sharper member the pool's
own contribution shrinks: its margin over its best member falls from 1.954 to 1.264 CRPS and
it scores 0.617 worse. A linear opinion pool profits from its members disagreeing, and batch
11's finding that fitting the weights costs 4.021 CRPS is the same fact from the other side.

**Two defects, both the same shape**, found by building the rows rather than by running them:
a glob that ignores the tree's forks. Neither was reachable until a fork had two built
children, and one of them would have silently changed the reported model.

## 1. What ran

| combination | kind | skill | Δ vs main | our CRPS | that baseline's CRPS | seconds |
|---|---|---|---|---|---|---|
| `persistence_negBinomialFloor` | baseline | **+0.1206** | **−0.0279** | 19.434 | **20.698** (was 24.879) | 157 |
| **`main`** | — | **+0.1485** | — | 18.817 | 24.879 / 24.337 | — |
| `climatology_frozenWindow` | baseline | +0.1460 | −0.0025 | 18.872 | 24.869 (was 24.337) | 137 |

From `analysis/05_stability/results/conclusions.csv` and `run_status.csv`. The reference is
inherited from `main` at 22.098 on both rows — a fork inside one of our models cannot move it,
and re-running an unseeded model would replace its four repeats with a different draw.

**Both rows sit below the main path.** After batch 13, six of seven perturbations improved the
reported skill, and the honest reading was that a conservative main path and a systematically
flattering set of alternatives look identical from there. Two rows below it is the first
evidence for the first reading. It is two rows, and the fourteen candidate rows are what would
settle it.

## 2. The persistence fork: the main path took the worse construction

| | `a_empiricalChange` (main) | `b_negBinomialFloor` |
|---|---|---|
| mean CRPS | 24.879 | **20.698** |
| MAE | 29.073 | 25.604 |
| 10–90 coverage (nominal 0.80) | 0.666 | **0.720** |
| 25–75 coverage (nominal 0.50) | 0.491 | 0.550 |
| paired vs reference | +2.781 ± 2.985 | **−1.400 ± 1.424** |
| cell win rate vs reference | 0.469 | 0.518 |

From `04_score/03_compare/results/*/leaderboard.csv` and `paired_summary.csv`. The gap is
4.181 CRPS — **more than seven times the 0.565 floor** below which nothing on this dataset can
be attributed to a model — and it goes the same way on every secondary: better point forecast,
better tails, better central interval.

**A required baseline beats the reference model.** 20.698 against 22.098, paired difference
−1.400 with a split-clustered standard error of 1.424: **0.98 standard errors**, which does
not separate them and is not reported as though it did. But the point estimate says that a
model whose entire content is "next month is like last month, with a fitted spread" is ahead
of the WHO EWARS-csd model on this dataset. That is a finding about the reference and about
the problem, not about this node.

**Why the main path's reasoning was sound and its conclusion was wrong.** Batch 6 chose the
non-parametric construction because it estimates nothing and needs no arbitrary floor, on a
target where 56 % of observed months are zero. Both halves of that are true. What it could
not weigh is that estimating nothing also means never learning that Champasak's counts are
stickier than Phongsaly's — and on a dataset where provincial burdens differ by four orders of
magnitude, a per-province fitted dispersion is worth more than the floor costs. The fitted
dispersions span **0.01 to 1000** across seventeen provinces
(`b_negBinomialFloor/results/*/fitted_model.json`); a construction with no parameters gives
them all the same shape.

**The floor is the first of two arbitrary constants, not the only one.** On this dataset the
maximum-likelihood dispersion frequently does not exist: with an all-zero window and every
mean at the floor, the log-likelihood rises monotonically as the dispersion goes to zero,
where the distribution becomes a point mass at zero. The estimator therefore needs bounds,
`[0.01, 1000]`, and they bind for **six of the seventeen reporting provinces** — five at the
lower bound, one at the upper. The second constant does its work in exactly the provinces
where the first one does. **It wins anyway**, which is the finding rather than a caveat.

**Every constant is the source's.** Floor 0.2, window of five observations, dispersion by
maximum likelihood, and the same distribution at every horizon: all from the KIT baseline for
the German COVID-19 Forecast Hub, which batch 6 read and recorded as the construction not
taken, and which was re-read on 2026-08-29 for the horizon rule. A stability alternative whose
constants we chose could have been tuned against the path taken, which is the one thing a
perturbation must not permit.

**The fork is not promoted.** Phase C closed at batch 11 and the manifest was frozen and
committed before any of it ran; moving a main path on the strength of a stability row would
make the reported analysis a function of the stability run, which is the ordering the whole
design exists to prevent. What this row does instead is put the fact in the record.

## 3. The climatology fork: two years of data are worth nothing measurable

| | `a_expandingWindow` (main) | `b_frozenWindow` |
|---|---|---|
| mean CRPS | 24.337 | 24.869 |
| 10–90 coverage | 0.650 | 0.639 |
| 25–75 coverage | 0.542 | 0.520 |

0.532 CRPS, **inside** the 0.565 floor. The training frame ends 2007-12 and the evaluation
runs through 2009-12, so the frozen table forecasts two dengue seasons it has never seen, on a
series whose reporting improved throughout — and the difference does not clear the noise. The
node's own claim argued before the run that the choice mattered *because* of that gap. It
does not, and that is the answer.

Set beside its sibling, the pair says something neither row says alone: **on this dataset the
shape of a baseline's predictive distribution matters and the window it is estimated over does
not.** Two forks of the same kind, on the two baselines the plan requires, an order of
magnitude apart in what they are worth.

## 4. A better member is a worse pool

Batch 11 put both required baselines inside the reported model, so a baseline fork now moves
the pool as well as its own leaderboard row. Under `persistence_negBinomialFloor` every
summary of the pool's inputs improves and its output gets worse.

| | `main` | `persistence_negBinomialFloor` |
|---|---|---|
| best member CRPS | 20.771 | **20.698** |
| mean of the members' means | 23.421 | **22.376** |
| pool CRPS | **18.817** | 19.434 |
| pool's margin over its best member | **1.954** | 1.264 |
| pool 10–90 coverage (nominal 0.80) | 0.863 | **0.817** |
| pool 25–75 coverage (nominal 0.50) | 0.749 | **0.674** |

From `03_candidate/c_ensemble/results/*/pool_check.json`.

A linear opinion pool's spread is the mean of its members' spreads plus the spread *between*
their means, and its advantage comes from covering the outcome where the members disagree.
Replacing a wide, badly-centred member with a sharper, better-centred one narrows the pool,
and here it lost more from being narrower than it gained from the member being better. **The
pool is better calibrated on the row where it scores worse** — 0.817 against a nominal 0.80,
the closest to nominal the reported model has been.

Batch 11 found that fitting the weights to the members' quality costs 4.021 CRPS. This is the
same fact reached the other way: **both routes to a pool that respects member quality make it
worse.** Two independent demonstrations that this pool's win comes from disagreement, not from
its members being good.

The independent check survives the swap: rebuilt from the members' own stored evaluations, the
pool gives 19.455 against the 19.434 it scored — a residual of 0.021, the size of the pool's
own allocation sampling error and the same as `main`'s 0.016.

## 5. Two defects, both a glob that ignores the tree

Neither was reachable before a fork had two built children, and neither would have failed
loudly.

**The pool would have grown to six members, silently, under every combination including
`main`.** `prepare_members.py` discovered membership by globbing `03_models/**/scripts/*/MLproject`
and taking every contract directory it found. That is correct while each baseline fork has one
built child; with two, the reported model becomes a six-member pool containing **two**
persistence baselines and **two** climatologies, at equal weights, with the doubled models
carrying half the pool. Membership now resolves every alternatives fork above a contract to
the child this combination takes — by the same `resolve_glob` lookup `04_score` uses, so there
is one rule and not two that can disagree. The family fork is the one exception, because
pooling *its* children is what the node is for. A doubled member name is now a hard failure.
Re-run under `main`, `members.json` is **byte-identical**.

The record of the resolution went into a **new file beside** `members.json` rather than into
it, and the reason is a real cost of a good design: the pool's configuration carries
`members.json`'s sha256 and the model refuses to run when the two disagree, so a line of prose
added there re-hashes the reported model's configuration and forces the headline analysis to
be re-run in order to say it.

**The leaderboard would have carried two persistence baselines.** `01_collect` inherits a
model node with no results under the running combination from `COMBO_BASE`. A baseline row
runs `b_negBinomialFloor` and not `a_empiricalChange`, so the sibling would have arrived from
`main` — one leaderboard, two persistence rows, one of them produced by the very analysis the
row is defined against, and `conclusion.json` comparing against two baselines where the plan
requires one. Inheritance is now per fork rather than per node. Re-run with the change,
`metrics_cell.csv` and `models.csv` are **byte-identical** under `main`,
`weighting_crpsWeighted` and `provinces_reportingOnly`.

**It will change what batch 14's family rows collect**, because a family row runs `a_hierNB`
and not `c_ensemble` and the pool is therefore no longer inherited onto its leaderboard. That
is correct and it is adjacent to the `conclude.py` family-row defect batch 14 already owns.
Flagged rather than assumed.

**Both defects have the same shape as batch 12's two**, and the same origin: a step that
discovers things from the tree by globbing, written when every fork had exactly one child that
did anything. That is now four instances. The tree's own structure is what the globs should
have been reading, and from this batch two of them do.

## 6. What went wrong, kept

**Both rows failed at their first step, and nothing was written.** The two new runners
resolved the shared `chap_eval` library with `NODE.parents[3]`, which is `analysis/` from a
fork child rather than `03_models/`. Both were written from their siblings, which sit one
level shallower and use `parents[2]`, without re-counting. `ModuleNotFoundError`, 23 seconds
and 0 seconds. The fix is its own commit so the failure is in the history rather than smoothed
out of it, and it is the argument for the dry run: `--dry-run` prints the step list a child
has to satisfy and cannot tell you the child imports from the wrong place.

**A gap in the record I did not close.** The dispersion the parametric baseline actually
forecast with was re-estimated inside `predict` at every split, and chap-core does not surface
a model's stdout, so those per-split estimates are in no file. `fitted_model.json` holds the
training-frame fit — what the model knew at fitting time, and the fallback — not the
parameters behind the forecasts. **This is the third time in this project that moving fitting
into `predict` has cost the record rather than the score**: batch 4 found the reference has no
stored fit at all, batch 21 found the same for `04_fitTime/b_refitAtPredict`. Closing it needs
somewhere for a model to write per-split diagnostics that outlives chap-core's run directory,
which is a change to the shared `chap_eval.py`. Left to batch 14, which touches that file and
re-runs everything it configured.

## 7. Decisions taken in this batch

Full table in the plan's §4b, dated 2026-08-29 (batch 22). The four worth arguing with:

| Decision | Basis |
|---|---|
| The parametric construction's constants are the source's, unchanged, including a five-observation window that is five *weeks* there and five *months* here | An alternative whose constants we chose could be tuned against the path taken. The transplant is recorded where it bites rather than repaired by picking a different number |
| The dispersion is re-estimated at predict time, so this fork moves *where* the spread is estimated as well as its form | The source re-estimates from the last five observations available at forecast time, and the sibling already takes its anchor from the historic frame; a frozen dispersion beside a moving mean is a hybrid neither published construction describes. The confound is stated, and the fork next door isolates the window question on its own |
| Two contract directories rather than one with a switch, accepting the duplicated table build in the climatology pair | A Chap contract directory is copied whole into the run directory, so a shared library outside it does not travel with the model; and a switch would re-hash a model that produced six committed combinations' results, which is batch 11's objection to the assembler lift |
| Both new models score under the *existing* leaderboard names, `persistence` and `climatology` | A second name would put two baselines on a board where the plan's §4 requires one, and would make every cross-combination comparison of that row a comparison of two differently-named things. Which construction produced it is in `models.csv`'s `node` column |

## 8. Compliance for this batch

| Rule | What was done |
|---|---|
| 1 — track results | Two new provenance records and eleven appended sections, each naming its script sha256, inputs, environment, commit, alternatives-considered and agency. Every figure in this report is read from `conclusions.csv`, `run_status.csv`, `leaderboard.csv`, `paired_summary.csv`, `pool_check.json`, `fitted_model.json` or `manifest.csv` |
| 2 — no manual manipulation | No file produced by this batch was edited. The two rows were re-run after the import fix, never patched |
| 3 — pinned environments | Two new model environments, each pinned by a `pyproject.toml` and a `uv.lock` that travel with the model. Both resolve to the **same six packages at the same versions** as their siblings', verified by diffing the lockfiles — the negative binomial is implemented from its own pmf rather than pulled in from scipy, which is what keeps that true and keeps the pool's environment where it was |
| 4 — version control | Three commits: the children and the two fixes; the import-path repair; the results and records. This report and the plan are the fourth |
| 5 — intermediates | Every stage of both rows stored, plus one artefact that did not exist before: `member_selection.json` under every combination the pool has run since |
| 6 — seeds | Neither new model contains randomness — a deterministic grid search and a quantile function at fixed levels — and this is verified rather than asserted. `verify_model_determinism.sh` now names all **seven** models by their own leaf nodes; the two baselines had been named by their fork nodes, which would have checked one construction, called it `persistence`, and left the other unchecked. Batch 11's rule, applied where a second built child makes it bite |
| 7 — plots | The three figures were drawn under both rows by the existing scripts, with plotted values beside them. No new figure: the distribution of conclusions is batch 15's and it has ten of twenty-four rows |
| 8 — hierarchical report | Not due |
| 9 — claims | Answers written into both new children, both parent forks, `01_baselines`, `c_ensemble` and `05_stability`. `/claims add` is batch 17's |
| 10 — release | Not due |
| `/annotate-criticality` | Appended at `03_models` and `05_stability`, with sizes **measured** rather than projected. `manifest_notes.json` puts every combination on disk at **660.2 MB** against a projected 584.7 MB for the whole of tier 1 on development and 1 169.4 MB across both datasets — so storage, not compute, is the number to watch before phase E |
| `/validate invariants` | All invariants hold |

## 9. What is still unknown

1. **Whether the main path is conservative or the alternatives flatter it.** Both new rows are
   below it, which is the first evidence either way, and two rows are not enough. The
   fourteen candidate rows are the ones that move our own model.
2. **What the better persistence baseline would do inside a pool that was allowed to notice
   it.** Nothing here says whether a pool fitted to *these* members would have done better —
   only that the equal pool does worse. Batch 11's `b_crpsWeighted` row, which batch 14 runs,
   is the closest the frozen manifest comes to asking.
3. **Whether the fork should have been the main path.** It is not the agent's call: phase C is
   closed and the manifest was frozen before the row ran. It is the human's, and §12 asks it.
4. **Whether the same is true of the holdout.** The frozen manifest carries both rows to 2010,
   so the question will be answered there rather than argued.

## 10. For the human

- **The model we report is built on the worse of two published constructions of a baseline
  your plan requires, by 4.181 CRPS.** The better construction beats the reference model on
  the point estimate. Nothing in the reported conclusion changes — the pool is still ahead of
  everything, on every row — but that sentence belongs beside the headline.
- **The pool got worse when a member got better**, and I think this is the most interesting
  thing phase D has produced about the model itself. It says the reported model's advantage is
  a property of its members disagreeing rather than of their quality, and it is the second
  independent demonstration of that after batch 11's weight-fitting result.
- **One decision I deliberately did not take.** Promoting `b_negBinomialFloor` onto the main
  path would improve the persistence row and make the pool worse, and it would also make the
  reported analysis a function of the stability run, which is the ordering the design forbids.
  If you want it promoted, that is a phase-C reopening and it is yours; it would invalidate
  the frozen manifest and everything already run against it.
- **A defect that would have changed the reported model without failing.** Adding the two
  contract directories would have made the pool a six-member pool under `main`, with two
  copies of each baseline. It was caught by reading the discovery code before running, not by
  any check. `/validate invariants` would still have passed.
- **Storage, not compute, is the thing to watch.** 660.2 MB on disk for the combinations run
  so far, against the planner's own projection of 584.7 MB for all of tier 1 on development
  and 1 169.4 MB across both datasets — the disk is filling from the phase-C combinations as
  well as the manifest's, and only one of those was budgeted. Compute is still four times
  inside its budget. Nothing is deleted and the criticality tables say what would go first.
