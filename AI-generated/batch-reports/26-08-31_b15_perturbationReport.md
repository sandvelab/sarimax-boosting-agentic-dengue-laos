# Batch 15 — `/perturb report`: the distribution, and the frozen holdout set

Generated from [[26-08-22_dengueForecastingCase]] — iteration 15

**Phase D · Status: done — produced · Executed 2026-08-31**

---

Phase D's thirty-two analyses become the phase-D result; the driver joins
`analysis/run.sh`; and the set phase E runs on the held-out year is frozen and committed
before the year is opened. Phase D is complete.

**The conclusion survives the perturbation set, and the reported number is not the middle of
what it survives across.** Skill runs **−0.0724 to +0.2320** around the reported **+0.1485**,
which sits **thirteenth of thirty-two**. Our model beats the reference on **27** and both
required baselines on **27**, and the failures are structured rather than scattered: the five
rows the reference wins are exactly the five that replace our model or refit its weights, and
the five a required baseline wins are exactly the five that weight the headline mean by cases.

**Six of the seventeen judgment calls move the conclusion further than the reference model
moves on its own; eleven do not.** The yardstick is measured rather than chosen. The
reference is unseeded and was scored four times, and our model's skill score against those
four repeats spans **0.0218** — how far the reported conclusion moves when nothing changes
but the reference's sampler. Above that band: the model family (0.2209), the pool's own
weighting (0.1820), the weighting of the headline mean (0.0835), the province filter
(0.0376), the persistence construction (0.0279) and the training window (0.0219, which is
the band itself to within 0.0001). Below it: everything else, **including nine of the eleven
candidate-internal forks phase C spent three batches selecting among**.

**The frozen manifest, re-planned against a completed tier 1, came back byte-identical.**
That is what made it safe to put `run_manifest.py` into `run.sh`, which re-plans on every
run — and it is what makes `analysis/run.sh` reproduce the stability result rather than only
the reported one, at about four hours rather than twenty minutes.

---

## 1. What ran

| | |
|---|---|
| New scripts | five at `05_stability`: the report, three figures, the freeze |
| Models re-run | **none.** Every number here is arithmetic on stored conclusions |
| Rows re-run | none. The manifest ran in batches 13, 22 and 14 and is not re-run to report it |
| Scripts re-run | `plan_manifest.py` (byte-identical manifest), `compare_planned_cost.py` (stale since batch 14) |
| Claims added | **12**, the first entries in the collection |
| Invariant checks changed | one, extended: `combos` now reads both manifests |

Nothing in this batch touches a model, and that is deliberate. The perturbation set is the
evidence; re-running any of it to report it would replace the unseeded reference's four
repeats with a different draw and move the denominator of every number in the report.

## 2. The distribution

`results/distribution.json`, from `results/distribution_rows.csv`, from each combination's
own `conclusion.json`.

| | |
|---|---|
| Analyses with a conclusion | **32** of the manifest's 33 |
| The row without one | `family_ensemble` — the main path's own choice under its own name, which perturbs nothing |
| Skill score | **−0.0724 to +0.2320**, median **+0.1469** |
| The reported analysis | **+0.1485**, rank **13 of 32** — 12 conclude better, 19 worse |
| Beats the reference | **27** of 32 |
| Beats both required baselines | **27** of 32 |
| 10–90 coverage | **0.458 to 0.920**, nominal 0.80 |
| Cut for budget | nothing |

**Mean CRPS is reported within a weighting and never across one**, and the report enforces
it by reading each row's weighting off its own fork columns rather than from the size of the
number: **18.55–23.70** unweighted over 26 rows, **28.58** population-weighted, **88.48–112.26**
case-weighted over 5. A re-weighted mean is over a different set of weights; putting those on
one axis would report a spread that is an artefact of the unit. The skill score is a ratio
and is comparable across all thirty-two, which is the reason `readme-at-start.md` gives for
reporting a ratio in the first place — and it is the first time in the project that the
reason has actually been load-bearing.

**The five and the five.** The rows where the reference wins are `family_hierNB`,
`weighting_crpsWeighted` and the three pairs built from them. The rows where a required
baseline wins are the five case-weighted ones. Those two sets do not overlap and neither is
a scatter: **no choice about the data, the evaluation, the scoring or the baselines takes
our model below the reference on any row.** What takes it below the reference is replacing
it or refitting its weights.

## 3. The yardstick, which is measured rather than chosen

"Does the conclusion move" needs a scale to be answered on. Choosing one — a tenth of the
main path, say, or two standard errors — would be a judgment call made silently inside the
node whose whole job is to stop judgment calls being made silently.

So it is measured. `03_compare` already scores our model against **each of the reference's
four repeats** separately as well as against their mean, because the reference is unseeded.
Those four skill scores are 0.1376, 0.1415, 0.1551, 0.1594 — a span of **0.0218**. That is
how far the reported conclusion moves when nothing about the analysis changes at all.

It is the skill-space twin of the **0.565 CRPS** floor the project has quoted since batch 7,
and it comes from the same four repeats. The CRPS floor could not have been used here: the
conclusion is in skill, and the weighting fork makes CRPS non-comparable across six of the
thirty-two rows. Both are carried in `distribution.json`.

A fork inside the band has **not been shown to move the conclusion**, which is weaker than
having been shown not to, and the report says so rather than the other thing.

## 4. Which judgment calls the conclusion is sensitive to

`results/sensitivity_by_fork.csv`, and `results/fig_fork_sensitivity.png`. One row per fork,
the largest absolute move across the tier-1 rows that take one of its children.

| Rank | Fork | Kind | Largest move | |
|---:|---|---|---:|---|
| 1 | `03_models/03_candidate` | family | **0.2209** | which model family is ours |
| 2 | `.../c_ensemble/01_weighting` | candidate | **0.1820** | how the pool weights its members |
| 3 | `04_score/02_aggregate` | scoring | **0.0835** | how the headline mean is weighted |
| 4 | `02_setup/03_provinces` | setup | **0.0376** | which provinces are in the analysis |
| 5 | `.../01_baselines/01_persistence` | baseline | **0.0279** | how persistence wraps its uncertainty |
| 6 | `02_setup/02_trainingWindow` | setup | **0.0219** | how much of the record is learned from |
| | *— the reference's own re-run noise, 0.0218 —* | | | |
| 7 | `02_setup/04_retrain` | setup | 0.0166 | how often a model is refitted |
| 8 | `02_setup/01_population` | setup | 0.0138 | what the population column contains |
| 9 | `.../a_hierNB/02_covariates` | candidate | 0.0081 | the covariate set and lags |
| 10 | `.../a_hierNB/04_fitTime` | candidate | 0.0057 | fitting in train or in predict |
| 11 | `.../a_hierNB/01_observation` | candidate | 0.0052 | the observation model for the counts |
| 12 | `.../02_climatology` | baseline | 0.0025 | the seasonal estimation window |
| 13 | `.../a_hierNB/03_population` | candidate | 0.0020 | how population enters our model |
| 14 | `.../b_boosted/02_head` | candidate | 0.0018 | the probabilistic head |
| 15 | `.../a_hierNB/06_yearVariance` | candidate | 0.0011 | how the year variance is pooled |
| 16 | `.../b_boosted/01_features` | candidate | 0.0002 | the boosted feature block |
| 17 | `.../a_hierNB/05_autoregressive` | candidate | 0.0002 | an autoregressive term |

**The training window is the borderline case and is reported as one.** At 0.021875 against a
band of 0.021778 it clears by one part in two hundred, which is not a distinction anybody
should lean on. It is above the line because the line is where it is, not because the
evidence separates it; the figure and the file both carry the number rather than the verdict.

**Three readings.** The two largest are the model family and the pool's own weighting, and
between the family bar and the largest fork *inside* a family there is a factor of
twenty-seven. The third largest **re-runs no model at all** — thirteen seconds of
re-aggregating a stored file, against twenty minutes for a setup row that re-runs everything
on the leaderboard. And nine of the eleven forks below the line are the candidate-internal
ones: **phase C's three batches of selection happened almost entirely inside the noise.**

## 5. The pairs still do not compose

`results/fig_pair_interaction.png`. Nothing in this section is new — batch 14 established it
— but it is what the figure is for and it is what the claim rests on.

None of the eight pairs sits on the diagonal, and the largest departure, **−0.1033**, is
larger than either main effect behind it: the province filter is worth +0.0376 alone, case
weighting +0.0835, and together they come to **+0.0177** against an additive +0.1211. Both
work by re-weighting what the mean is over, and taking both does not do it twice.

The departure is **not a general property of the set**. The two pairs that put case weighting
on a setup fork fall furthest below the diagonal; the other six sit within +0.042 to −0.018.
The interaction is concentrated where two forks reach the same mechanism, which is a more
useful statement for the manuscript than "forks interact".

## 6. Putting the driver into `run.sh`, and the question that had to be answered first

`run_manifest.py` was written in batch 12 and deliberately kept out of `run.sh` through
batches 13, 22 and 14, because rows with no scripts and rows whose defects made them report
the wrong thing would have been written into the tree every time anyone ran the analysis.
Every row can now run, so the reason is gone.

But `05_stability/run.sh` **re-plans the manifest on every run**, and the manifest is the
frozen artefact whose commit date is the evidence that the perturbation set was not chosen
after the numbers were in. So before the driver could join the file, one question had to be
answered by running rather than by reading: does re-planning move it?

**It does not.** `manifest.csv` came back **byte-identical** — same 33 rows, same ranks, same
eight tier-2 pairs — now that every row has been attempted and the frozen pair rule reads a
complete tier 1. The only field that changed anywhere is `manifest_notes.json`'s
`on_disk_now_results_mb`, 681.0 → 1126.3, which is a measurement of the disk and not a plan.

The node's script order is now the phase's own, and the two repeated steps are what make it
reproducible from nothing rather than from the results already on disk:

```
measure_step_costs  →  plan_manifest  →  run_manifest --tier 1  →  collect_conclusions
                    →  plan_manifest  →  run_manifest --tier 2  →  collect_conclusions
                    →  compare_planned_cost  →  report_distribution  →  three figures
                    →  freeze_holdout_manifest
```

On a cold run the first planning pass can only leave eight unresolved tier-2 slots, because
`tier2_rule.md` selects the pairs from tier 1's conclusions and tier 1 has not run. The
second pass, after tier 1 has run and been collected, fills them by the same rule. Both
passes are the same script and the same rule; what differs is that the second has a tier 1
to read.

**The cost of this is real and is recorded**: `analysis/run.sh` is now about four hours
rather than about twenty minutes, and most of that is the reference model's four unseeded
repeats through an amd64 image under emulation. `readme-at-start.md` says so, and the
property the plan asks for — `analysis/run.sh` reproduces the reported result — is now the
stronger property that it reproduces the reported result *and* the distribution around it.

## 7. The frozen phase-E set

`results/manifest_holdout.csv` and `results/holdout_freeze.json`, written by
`freeze_holdout_manifest.py`.

**Thirty-three rows**, one per development row, at an estimated **2.07 h** against a 12-hour
budget of which development spent 3.66. Nothing is cut. Each row is its development
combination with `__holdout` appended, because a holdout row writes under
`analysis/results/<combination>/` and reusing the development names would overwrite the very
results the holdout is to be reported against.

**The pairing is frozen with the set.** Every row carries the development skill score, CRPS,
reference CRPS, coverage and model it is to be reported beside. Freezing which analyses run
and then assembling the development half of the comparison afterwards would leave the
comparison selectable after the fact even though neither half was — and the plan asks for
development and holdout spreads to be read on one axis.

**What the freeze refuses.** The script will not write a set whose development half is
unfinished: every row must have a conclusion or a reason that is not "waiting for a batch",
every tier-2 slot must be resolved, and `tier2_rule.md` must still hash to what
`manifest_notes.json` recorded before tier 1 ran. A holdout set frozen around the rows that
happened to finish would be a set chosen by the running order.

**What is deliberately left open.** How `02_setup` is pointed at the full file rather than at
the development file does not exist yet; it is batch 16's implementation.
`holdout_freeze.json` records the constraint it works under — it may not change the rows, the
scheme, the models or the pairing — so that a change would be visible rather than convenient.

**And `check_invariants`' `combos` check now reads both manifests.** A holdout directory is
planned exactly as a development one is, and one nobody planned still fails. That is an
extension of the check, not a relaxation: the combination space is still closed, over a
larger set of names.

## 8. Cost, corrected

`compare_planned_cost.py` had been stale since batch 14, describing nine rows when
twenty-three had run. Re-run:

| | |
|---|---|
| Planned, over the rows the manifest costed | **7 469 s** |
| Actual, same rows | **7 469 s** — ratio **1.00** |
| Worst row | `weighting_crpsWeighted` at **1.91** |
| Whole development set, all 32 rows | **13 172 s = 3.66 h** |

**A cost model right to three significant figures in total and wrong by a factor of two on
individual rows is a cost model whose rank order carries no information** — and the rank
order is what the cut order would have been drawn on. Nothing was cut, so nothing rests on
it. What rests on it is the next project that builds a manifest this way and does cut.

**A correction to a figure, not to a conclusion.** Batch 14's report and
`readme-at-start.md` put the completed development manifest at "about 3.2 hours". Summed from
`run_status.csv`, which is the file that records it, it is **3.66 hours**. The readme now
says 3.66; batch 14's report is an output and is not edited. Nothing else moves — the budget
was 12 hours and the finding was that compute does not bind, which is more true at 3.66 than
at 3.2.

## 9. What went wrong, kept

**`plan_manifest.py` documents a `--freeze-check` flag that does not exist**, and could not
work as documented if it did. The docstring says it "refuses to [fill the tier-2 slots] if
the rule's text has changed since the hash was recorded" — but the script writes both
`tier2_rule.md` and its sha256 from the same in-script constant on every run, so the two can
only ever agree. There is no flag in its argument parser, and there never was one.

What actually evidences the freeze is git: batch 12's commit of `tier2_rule.md`, before any
tier-1 row ran. That is stronger than the flag would have been. And the check the flag
describes **is** enforced now, by `freeze_holdout_manifest.py`, which compares the rule's
current text against the hash in the *existing* notes before anything overwrites them, and
refuses to freeze a holdout set if they disagree.

The docstring is left standing and the finding recorded in
`provenance/plan_manifest.md`, because correcting it means editing the script whose output is
the frozen manifest, and this batch's whole argument for touching that script at all was that
re-running it changes nothing. A promise in a comment that nothing enforces is worth more in
the record than tidied away.

**No models were re-run in this batch and no row was re-run to report it** — which is the
right outcome and also the reason there is nothing else in this section. The two failures
this phase produced are in batches 13 and 14's reports, where they happened.

## 10. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| The yardstick for "moves the conclusion" is the reference's own re-run spread in skill, 0.0218 | Measured from `paired_summary.csv`; choosing a threshold would have been a silent judgment call inside the node that exists to prevent them | agent-autonomous |
| Mean CRPS is summarised within a weighting and never across one | A re-weighted mean is over different weights; one axis would report an artefact of the unit | agent-autonomous |
| The distribution is reported as min / median / max with the per-row table beside it, not as quartiles | Thirty-two rows drawn from a manifest are not a sample of a population, and a quartile invites reading them as one | agent-autonomous |
| Holdout rows are named `<combination>__holdout` | A holdout row must not overwrite the development result it is to be compared against | agent-autonomous |
| The development conclusion is frozen into the holdout manifest row by row | Otherwise the comparison is selectable after the fact even though neither half is | agent-autonomous |
| `run_manifest.py` joins `run.sh`, and `analysis/run.sh` becomes a four-hour reproduction | The plan's batch 15; every row can now run | agent-on-human-assessment |
| The `combos` invariant reads both manifests | The frozen holdout set is a plan, and a directory it names is planned | agent-autonomous |
| Nothing is re-run to produce this report | The reference is unseeded; re-running would move the denominator of every number reported | agent-autonomous |

## 11. Compliance for this batch

| Rule | This batch |
|---|---|
| 1 — track results | Five new provenance records at `05_stability`; two existing ones appended to for the two scripts re-run |
| 2 — no manual manipulation | Nothing edited in place. `manifest.csv` was regenerated by its own script and came back byte-identical |
| 3 — pinned environment | Unchanged. Every script ran under `environment/chapenv/bin/python` |
| 4 — version control | `/commit-run before` at `9ad6578` for the scripts, `after` for the results and records |
| 5 — intermediates | `distribution_rows.csv` is the per-analysis table the summary is computed from, and is stored beside it |
| 6 — seeds | Nothing here draws randomness; every script's docstring says so and `/validate invariants` checks it |
| 7 — plots | Three figures, each with its plotted values, two with pre-aggregation files, all three with their scripts and provenance records. `fig_skill_distribution` has no pre-aggregation file and its record says why: each point is one stored conclusion, not a summary of several |
| 8 — hierarchical report | Not this batch; batch 17 |
| 9 — claims | **Twelve claims added**, the first in the collection — the stability claim itself and eleven under it. `claims.py audit` resolves every pointer |
| 10 — release | Not this batch; batch 19 |

## 12. What is still unknown

- **The holdout.** Every number in this report is development. The set that will be run
  against 2010 is frozen and the year has not been opened.
- **Whether the distribution transfers.** If the holdout spread is much worse than this one,
  that gap is the most interesting result the project has, and the plan says to report it
  plainly rather than explain it away.
- **The per-split diagnostics gap** batch 22 opened and batch 14 declined to close stays
  open, and now stays open permanently for development: closing it would mean re-running the
  reported analysis after the manifest has been frozen. It can still be closed on the holdout
  side if the human wants it, since batch 16 has not run.
- **What `analysis/run.sh` costs from cold has not been measured.** The four-hour figure is
  the sum of what the rows took when they ran, not a clean-room measurement.
  `/validate cleanroom` in batch 18 is where that gets a number.

## 13. For the human

- **Phase D is complete and the seal is intact.** The distribution is reported, the fork
  ranking is the plan's "most valuable single output" and is in one file and one figure, and
  the phase-E set is frozen and committed. Batch 16 opens the holdout, once, and runs exactly
  what is in `manifest_holdout.csv`.
- **The headline for the manuscript is the ranking, not the spread.** That the conclusion
  survives 27 of 32 reasonable analyses is a good result and a slightly boring one. That
  **six of seventeen judgment calls matter and eleven do not, and that the eleven are almost
  exactly the ones three batches of phase C were spent on**, is the finding — a direct
  measurement of effort spent below the resolution of the evaluation, by a system that was
  free to spend it.
- **`analysis/run.sh` is now four hours.** If you would rather it stayed twenty minutes and
  the stability run were invoked separately, say so and I will split it; the argument for the
  current shape is that the distribution is a reported result and `run.sh` is what reproduces
  reported results.
- **One correction, small**: the completed development manifest took 3.66 hours, not the 3.2
  batch 14 reported. The readme is updated; the conclusion it supported is unchanged.
