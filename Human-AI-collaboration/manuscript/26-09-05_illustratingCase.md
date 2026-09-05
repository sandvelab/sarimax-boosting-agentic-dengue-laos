# An illustrating case: forecasting dengue in Laos, veridically

Generated from [[26-08-22_dengueForecastingCase]] — iteration 19

*Written for the manuscript's* An illustrating case *section, and supplying what that
paper's Appendix supplies for a case: the worked claim-tree skeleton, the perturbation
families, and the judgment about where the setup was more trouble than it was worth. Every
figure traces to a claim in `Human-AI-collaboration/claims/claims.md`; the mapping is in
`26-09-05_illustratingCase_sidecar.md`.*

---

## The case, and why this one

An agentic system was given a real forecasting problem and a research plan, and asked to
produce two things at once: a model with a defensible score, and the complete record of how
it came about. The problem is **monthly dengue case counts across the eighteen admin-1
provinces of Laos, 1998–2010**, from the CHAP harmonized dataset, with rainfall, mean
temperature, relative humidity and a population figure as covariates. The evaluation is the
platform's own cross-validated backtest, and the model to beat is the field's own: WHO
EWARS-csd, at its published default configuration, pinned by image digest and never tuned.

Four things made this case worth the apparatus rather than merely compatible with it.

**The data are public and redistributable**, so the release is about secrets rather than
permissions.

**The evaluation is somebody else's.** The metric, the splitter and the region filter are the
platform's, so the analysis cannot quietly define its own success. The headline is mean CRPS
across regions and splits, which scores a distribution rather than a point.

**A published model exists to be measured against**, so "did it work" has an answer that is
not self-referential.

**And the answer is sensitive to choices that all look reasonable.** That is what makes the
veridical machinery report something rather than perform. Seventeen judgment calls were
identified and carried as forks in the analysis tree, and the spread of conclusions across
them is wider than the margin the project reports.

One decision shaped everything else and is worth stating first. **The final year was cut out
of the data before any work began.** 2010 went into a separate file; development, tuning,
selection and the whole backtest happened on 1998–2009, and nothing was pointed at anything
else until the final validation. This is stronger than holding a year out of a metric,
because the held-out year is not in the file the agent can open. An agent cannot leak what it
cannot read.

## What the analysis did

The archived source was cut into a development period and a sealed holdout, and the cut was
verified rather than asserted: 2 592 and 216 data lines against the source's 2 808, no line
in both, the sorted union byte-identical to the source, and each part an order-preserving
subsequence of it.

The evaluation scheme was fixed before any model ran and never moved: **three-month horizons,
eight splits, stride three, refitted once**, evaluating 2008-01 to 2009-12 from a training
set ending 2007-12. A horizon changed midway makes every earlier number incomparable, so it
was fixed early and treated as immovable.

Three things the data turned out to be were established from the file and not from its
documentation.

- **The headline mean is over 16 provinces and 371 cells, not the 18 provinces the file
  contains.** The platform's own region filter rejects one province that reports nothing at
  all, and a second contributes no evaluable cell because it stops reporting in 2005.
- **The target is mostly zeros and the record gets less complete as it goes on**: 56.3 % of
  observed province-months in the development period are exactly zero, and the missing share
  rises across the period.
- **Three statements in the dataset's own schema do not describe the file it ships with.**
  The declared row count is the count of rows with an observed target rather than the row
  count; the rainfall column, declared a monthly total in millimetres, is a mean daily rate;
  and the boundary file it names had been renamed. Two of the three are the harmonisation's
  rather than this file's — the sibling country files carry them too.

Three models of ours and one external model were scored on identical ground: a **persistence**
baseline and a **seasonal climatology** baseline, both required by the plan and both
implemented as platform-compatible models so they traverse the same evaluation path; our
candidate; and the reference. A baseline evaluated a different way is not a comparison.

## The result

**On the development backtest the reported model beats the reference model and both required
baselines**: mean CRPS **18.817** against the reference's **22.098**, a skill score of
**+0.1485**, ahead of each of the reference's four repeats individually and better in six of
the eight splits.

**The margin is not large enough to separate the two models, and the project says so rather
than rounding it up.** The paired difference is 3.282 CRPS per cell against a
split-clustered standard error of 1.726 — **1.90 standard errors**, which is the largest
margin the project achieved and still short of a separation. "We cannot separate these two"
is a conclusion, and it is the one reported.

**Below that sits a floor that has nothing to do with either model.** The reference cannot be
seeded: it draws from a posterior and exposes no seed. Four repeats of the same model on the
same data score 21.820, 21.917, 22.272 and 22.385, so **nothing below about 0.57 CRPS on this
dataset can be attributed to a model at all**. The project's own margin is about six times
that floor; most of the choices it agonised over are below it.

**The reported model is a linear opinion pool** over four members: two candidate families of
ours and both required baselines, equally weighted. It beats every model that goes into it —
18.817 against its best member's 20.771 and its members' mean of 23.421 — with half its
weight on baselines that individually lose to the reference. Two results about it are worth
more than the score:

- **Fitting the pool's weights costs far more than it buys.** Weights chosen by minimising
  the pool's CRPS on a validation period held back inside the training frame score 22.838
  against equal weights' 18.817 — **4.021 CRPS worse**, and worse than the reference. The
  obvious refinement is the worst decision available at that fork.
- **The family the project built first never beat the reference.** A hierarchical
  negative-binomial GLM scores 23.698 against 22.098. The second family, gradient-boosted
  trees with a probabilistic head, scores 20.771 and beats the reference on its own. Neither
  fact would be in the record if only the winner had been kept.

**Calibration is reported beside the score and not under it**, because a badly calibrated
CRPS winner has not won. The reported model is the most over-dispersed in the project:
10–90 interval coverage 0.863 against a nominal 0.80. On this dataset the 25–75 figures are
not a clean reading of calibration and the 10–90 figures are, because 56 % of observed
province-months are exactly zero and a model that puts more than a quarter of its mass on
zero covers the lower quartile trivially.

**Both required baselines lose to the reference, so beating the baselines is not the bar that
binds.** Persistence scores 24.879 and climatology 24.337 against 22.098. The plan's success
criterion has two clauses and only one of them is difficult.

## The stability result, which is the larger one

**The conclusion this project reports is one member of a distribution over thirty-two
analyses that all looked reasonable, and the set was fixed before any of them ran.** Across
it the skill score runs from **−0.0724 to +0.2320** around the reported +0.1485, which sits
**thirteenth of thirty-two**.

Five things that distribution says, none of which a single-path analysis could have said.

**The failures are structured rather than scattered.** Our model beats the reference on 27 of
the 32 and both baselines on 27. The five where the reference wins are exactly the five that
replace our model or refit its weights; the five where a baseline wins are exactly the five
that weight the headline mean by cases.

**The model family is what the conclusion is sensitive to; the choices inside a family are
not.** Swapping the pool for the first candidate costs 0.2209 of skill. The eight forks
*inside* the two member families move it by at most 0.0081 and span 18.638 to 18.933 mean
CRPS over the eleven combinations they perturb — about half the reference's own re-run
spread. Phase C spent three of its four batches choosing among those eight.

**The cheapest analysis in the manifest is the one the conclusion is most sensitive to among
the choices that leave our model alone.** Re-weighting the headline mean re-runs no model at
all — thirteen seconds against twenty minutes — and moves the reported skill by 0.0835, four
times as far as any of the five setup forks that re-run every model on the leaderboard.

**Under one reasonable weighting a required baseline beats the model this project reports**,
in every combination where that weighting appears. Weighting provinces by cases makes
persistence the winner; the reported unweighted mean is a choice, and a defensible
alternative reverses the ranking.

**Fork effects do not compose, so a one-at-a-time stability report cannot be added up.**
Across the eight pairs the interaction runs from −0.1033 to +0.0424, and the largest is
bigger than either main effect behind it: the province filter and case weighting each improve
the reported skill alone and almost exactly cancel together.

And one caution about the stability report's own headline. **Six of the seventeen judgment
calls move the conclusion further than the reference model moves on its own** — but the
yardstick is a draw, not a constant. It is a maximum minus a minimum over four repeats of an
unseeded model, and across this project's runs it has come out at 0.0218, 0.0431, 0.0349 and
0.0483 of skill, on which the same file reads six, three, three and three of seventeen. Three
forks cross the line on some draws and not others; the band moved, not the forks. Only the
model family, the pool's weighting and the headline-mean weighting are clear of it every
time. The count is reported as the headline together with the draw-dependence of the band it
is measured against.

## The held-out year

The holdout was opened once, in a single batch, and the set of analyses run on it was frozen
before it was opened — **thirty-two rows, each a development row under a holdout name, with
its development conclusion frozen beside it**, committed at a point in history where no
holdout result existed. That freeze is what makes the second spread a measurement rather
than a selection.

**The reported model beats the reference and both baselines on the held-out year too**: skill
**+0.0868**, 76.731 against 84.026 over 192 cells. Raw CRPS is about four times the
development period's for every model in the comparison, which is what the ratio exists to
control for.

The interesting results are the ones that did not hold.

**The distribution is more than twice as wide on the held-out year**: −0.5038 to +0.2026,
against −0.0724 to +0.2320 on development. Same thirty-two analyses, same yardstick, one year
they had not seen.

**Twenty-eight of the thirty-two scored worse**, median 0.056 of skill.

**Ranking the analyses on the development set is a weak guide to how they rank on a year they
have not seen.** The rank correlation is **+0.396**. The fork ranking transfers better, at
+0.679, with 14 of 17 forks agreeing on whether they matter — but the identity of the forks
that matter on *both* datasets is not stable across re-runs of the same analysis, so that
count is reported with its names beside it rather than on its own.

**The analysis the development set ranked highest among those that change the data or the
models is twenty-ninth of thirty-two on the held-out year.** It ranked fourth on development
at +0.1861 and scores −0.1828 on 2010; its case-weighted pair is worst of all at −0.5038.
And the fork behind it moves the *reference*, not our model: our pool goes 76.73 → 76.56
while the reference goes 84.03 → 64.72. A system optimising freely against a development set
would have taken that row.

**The province filter is the largest single judgment call in the project on the held-out
year**, at 0.2696 of skill, having been fourth at 0.0376 on development. **The pool's own
weighting collapses from 0.1820 to 0.0121** and falls below the band.

**The over-dispersion does not survive the change of year**: 10–90 coverage 0.863 on
development, 0.755 on 2010, and across the frozen set coverage runs 0.458 to 0.920 on
development and 0.210 to 0.854 on the held-out year. Calibration moves much further across
the perturbation set than the score does.

## The external check

The reported model was then run, unchanged, on the Thai and Vietnamese files of the same
harmonisation, cut onto the same calendar and evaluated in the same two arrangements. This is
the only thing in the design that could say whether the development-to-final-year drop is
about 2010 in particular.

**It replicates.** Thailand +0.0856 → +0.0197; Vietnam +0.0852 → **−0.0862**; against Laos's
+0.1485 → +0.0868. All three drops are larger than the two reference bands they are measured
against, taken together — on the draw that is archived. **That clause does not survive a
re-run**: running the whole analysis again from a clean checkout returned it false for Laos
and false for Thailand, true only for Vietnam. Laos was the fragile one and was flagged as
such; Thailand, whose band is the tightest in the project, failed the other way, its drop
halving because the reference happened to do worse on Thailand's 2010. What survives both
draws is the direction in all three countries, the ordering, and the sign of the Vietnamese
loss. What does not is the quantification against the reference's own noise, and it is
withdrawn rather than restated.
Three countries of one harmonisation are not a sample and no confidence statement is made
from them — but the drop is a thing that happens repeatedly rather than a thing that happened
once.

**The country the model was developed on is the country it scores highest on.** Its Lao
development skill is 1.74 times either sibling's, and the two siblings — which have nothing
to do with each other — agree to **0.0004** while sitting **0.063** below Laos, about the size
of the whole held-out drop. The design cannot attribute that gap to development alone,
because nothing here varies development while holding the country fixed, and the claim says
so. But it is the most direct measurement the project has of what optimising against one
dataset bought on that dataset.

**And one finding is about the evaluation rather than the model.** The reference's own
unseeded re-run spread is **0.032 CRPS on Thailand's development backtest, 0.565 on Laos's
and 7.082 on Vietnam's** — a factor of 219 on one model at one configuration. Vietnam's
+0.0852 margin falls *inside* its own noise floor, so on that dataset the comparison this
project is built on cannot be made at all; Thailand's near-identical +0.0856 is thirty-five
times its band. A resolution measured on one dataset says nothing about another, and this
project had been quoting one number as though it were a property of the method.

**The over-dispersion travels and grows**: 10–90 coverage 0.941 and 0.967 on the sibling
development backtests against 0.863 on Laos's.

## What the evaluation can separate, on all six analyses

The margin the evaluation cannot separate is the usual case here rather than the exception,
and saying so of every analysis rather than of one is a correction this project made to
itself at the end.

| analysis | skill | paired difference / split-clustered SE | separated? |
|---|---|---|---|
| Laos, development | +0.1485 | **1.90** | the largest margin the project has, and still short |
| Laos, held-out year | +0.0868 | **0.94** | **no** |
| Vietnam, development | +0.0852 | 3.62 | yes on this yardstick, no on the other |
| Vietnam, final year | −0.0862 | **0.97** | **no** |
| Thailand, development | +0.0856 | 1.45 | no |
| Thailand, final year | +0.0197 | **0.49** | **no** |

The project's own line for "cannot separate arriving in practice" is 1.03 standard errors,
set when a candidate landed there during development. **Five of the six analyses are on the
wrong side of it — including the held-out result reported as beating the reference, and
including the Vietnamese final year reported as a loss.** Neither of those two sentences is
wrong; both were, until this table, unaccompanied.

**Two yardsticks, and they disagree.** Vietnam's development row is 3.62 standard errors from
the reference and simultaneously inside the reference's own re-run spread, because that
spread is driven by one repeat of four sitting 12 % above the others. A paired standard error
asks whether the difference is large relative to how it varies across splits; a re-run spread
asks whether it is large relative to how much the comparator moves against itself. On this
row they give opposite answers, and both are reported.

**And there is no equivalent test against the baselines.** `beats_all_baselines` is a
comparison of two means with no standard error attached, anywhere in the project. The margins
are large — 15 to 21 CRPS on the Vietnamese final year against a 0.5 noise floor — but the
project computed a paired spread only against the reference, so the strongest-sounding of its
results is the one with the least uncertainty attached to it.

---

## The claim tree, worked

The analysis is a tree of **claims** — analytical aims, written as questions — rather than a
pipeline of steps. Each node holds its question, its scripts, its results, its provenance
records, and one entry point. Children stand in one of two relationships, and the
relationship is a property of the whole set of children rather than of individual edges:
**alternatives**, which are competing answers to the parent's question and of which exactly
one is on the main path; and **sub-analyses**, which are parts of one approach and all of
which run.

```
analysis/                 "Can a spatio-temporal model of Lao dengue beat a persistence and a
│                          seasonal-climatology baseline on mean CRPS — and how far does that
│                          answer survive the reasonable alternatives?"   [sub-analyses]
├── 01_data/              "What does the dataset contain, and on what part may development
│   │                      happen?"                                        [sub-analyses]
│   ├── 01_partition/     "Does the source partition exactly into 1998–2009 and 2010?"
│   ├── 02_characterise/  "What is in the development period, and which of its features are
│   │                      analytic problems rather than preprocessing details?"
│   └── 03_siblings/      "What do the Thai and Vietnamese files contain, and on what
│                          arrangement can the model be checked on them?"
├── 02_setup/             "What dataset and evaluation setting does every model face in
│   │                      common?"                                        [sub-analyses]
│   ├── 01_population/    "How should the static population figure enter?"  [alternatives]
│   │   ├── a_static/     "…unchanged, one constant per province"           ← main path
│   │   └── b_backCast/   "…as a per-year series back-cast from it"
│   ├── 02_trainingWindow/"How much of the record may models learn from?"   [alternatives]
│   │   ├── a_from1998/   "…all of it"                                      ← main path
│   │   └── b_from2004/   "…the second half only"
│   ├── 03_provinces/     "Which provinces belong in the analysis at all?"  [alternatives]
│   │   ├── a_chapFilter/ "…leave it to the platform's region filter"       ← main path
│   │   ├── b_reportingOnly/ "…drop the two that cannot be evaluated"
│   │   └── c_mergeVientiane/ "…merge the silent province into its neighbour"
│   └── 04_retrain/       "How often is a model refitted across the backtest?" [alternatives]
│       ├── a_once/       "…once, at the platform's default"                ← main path
│       └── b_everySplit/ "…at every split"
├── 03_models/            "What forecast does each model make on that common ground?"
│   ├── 01_baselines/     "How well does the problem's own inertia forecast it?"
│   │   ├── 01_persistence/  "How is a point forecast turned into a distribution?"
│   │   │   ├── a_empiricalChange/  ← main path        └── b_negBinomialFloor/
│   │   └── 02_climatology/  "From what window is the seasonal average estimated?"
│   │       ├── a_expandingWindow/  ← main path        └── b_frozenWindow/
│   ├── 02_reference/     "What does the field's own model score here?"
│   └── 03_candidate/     "Which model family should our candidate be?"     [alternatives]
│       ├── a_hierNB/     "…a hierarchical negative-binomial GLM"   (6 forks below it)
│       ├── b_boosted/    "…gradient-boosted trees with a probabilistic head"  (2 forks)
│       └── c_ensemble/   "…a linear opinion pool over the families and the
│                          baselines"  (1 fork)                             ← main path
├── 04_score/             "What do the per-cell scores say?"                [sub-analyses]
│   ├── 01_collect/       "…collected from every model's evaluation"
│   ├── 02_aggregate/     "How is the headline mean formed?"                [alternatives]
│   │   ├── a_unweighted/ ← main path   ├── b_populationWeighted/   └── c_caseWeighted/
│   └── 03_compare/       "What can the comparison distinguish?"
├── 05_stability/         "How far does the answer survive the alternatives, on both
│                          datasets?"
└── 06_external/          "Does the model hold on two other countries, and does the drop
                           replicate?"
```

`analysis/run.sh` calls each child in order and then its own script, which states the
conclusion as a computed file. `03_candidate/run.sh` is one line: it calls `c_ensemble`. The
other two families sit beside it, complete and runnable, untouched by the main path — and
`05_stability` is what runs them.

Three properties make this shape carry a stability analysis rather than merely tolerate one,
and each is a design obligation.

**A shared output contract per fork.** Every child of an alternatives node produces output of
the same shape, because downstream nodes consume any of them interchangeably. Where an
alternative would change what is produced, the fork has been placed too low and belongs at a
parent whose output is common to both.

**A computed conclusion.** The reported answer is produced by a script at the root, from
files, so it can be recomputed once per combination and the results compared. Nothing states
a number that was not read from a file a script wrote.

**An enumerated perturbation set with a budget.** Which forks are varied and over which
children is stated in advance, because the combination count is multiplicative. The stability
node holds that enumeration, runs what the budget allows, and records what it did not run.

## The perturbation families, in dengue terms

Seventeen forks, computed from the tree rather than listed by hand, in four families.

**The data every model faces** — five forks. How the static population figure enters; how much
of the record models may learn from; which provinces belong in the analysis; how often a
model is refitted. These move every model on the leaderboard together, so a choice taken
differently re-scores the whole comparison rather than one side of it.

**The models being compared** — three forks. Which family our candidate is; and, for each
required baseline, how it is constructed — how a persistence point forecast is turned into a
distribution, and from what window a seasonal climatology is estimated. The baseline forks
became candidate forks when the reported model turned out to be a pool with both baselines as
members: a choice about how persistence wraps its uncertainty now moves our reported model as
well as the persistence row.

**The models' own internals** — eight forks. The observation model, covariate set and lag,
how population enters, when the model is fitted, whether an autoregressive term is included,
how year-to-year variance is pooled; and for the boosted family, its feature construction and
its probabilistic head. **These are where phase C spent three of its four batches, and they
are eight of the eleven forks whose effect is below the noise floor.**

**How the answer is scored** — one fork. Whether the headline mean over provinces is
unweighted, population-weighted or case-weighted. It re-runs no model and is the third-largest
effect in the project.

The manifest is two tiers: every fork taken alone, then eight pairs selected by a rule fixed
in advance — 24 one-at-a-time combinations and 8 pairs, 32 analyses, run on development and
again on the held-out year.

---

## What the case demonstrates

**The apparatus is affordable, and compute was never what bound it.** The whole development
manifest — twenty-four one-at-a-time analyses and eight pairs — ran in 3.66 hours, and most of
that is the reference model's unseeded repeats through an emulated container for the one model
the plan forbids perturbing. The held-out half took 2.39 hours and the external check 1.81.
What was scarce was the work of building models and of keeping the record honest, not the work
of running them.

**The negative space is worth publishing.** The three results a reader is most likely to use —
that fitting the pool's weights costs 4.021 CRPS, that the first family never beat the
reference, and that a required baseline wins under a defensible weighting — are all things a
paper reporting only its winner would not contain. They are in the tree, runnable, with their
scripts.

**The checks caught real problems, and they caught them where memory would not have.** The
invariant checker found twenty provenance records naming script versions that no longer
existed, including the record of the headline result. The clean-room run found that the seal
on the held-out year sealed every clone of the repository as well, so a fresh checkout
reproduced phase E's outputs *without running the analysis behind them*. The outsider test
found the plan's freeze rule and the tree's own invariant contradicting each other, an
ambiguity nobody in the project had noticed. Four separate places recorded a decision by
re-deriving it at run time from numbers that do not reproduce, and each was found by a check
rather than by review.

**And it took four attempts to make the root script run from a clean checkout.** Each got one
step further than the last, and each stop was a genuine defect: a recorded selection being
re-decided, a recorded figure being re-asserted, a check that could pass only on a tree that
had not been re-run. `analysis/run.sh` reproduces this analysis from nothing — and the
qualification belongs in the same breath: every model this project wrote returns identical
scores, and the reference model is an unseeded container, so every figure that divides by it
is a draw.

## Where this setup was more trouble than it was worth

*This judgment is the agent's. It was delegated deliberately, and recording it as jointly
held because a human read it afterwards would overstate their part.*

**The tracking that paid for itself.** Provenance records, the versioned instructions, stored
intermediates, plot data, seeds, the claim collection, the invariant checks and the clean-room
run. Each is cheap to produce and each caught something. The invariant checker in particular
is the best value in the whole apparatus: a few hundred lines of deterministic code that has
no attention budget to lose and that found, repeatedly, rules honoured for twenty steps and
dropped at the twenty-first.

**The tracking that was more trouble than it was worth, honestly.**

*The hierarchical report, at the size it reached.* Thirteen hundred and eighty-seven linked
pages descending from the national mean to per-cell scores, for sixty-nine scored
combinations. It is generated in seconds and it is genuinely complete, and I do not believe
anyone will ever read below its third level. The rule it satisfies is worth keeping; the depth
it was taken to was a decision nobody made deliberately, and it is the clearest instance in
this project of the failure mode the manuscript names — expansion without decision, because
each request is individually cheap.

*Criticality annotation.* It was applied faithfully to every stored artefact and its purpose
is to make later pruning targeted. Nothing was ever pruned, because storage turned out not to
be a constraint. The annotations are a cost paid against a contingency that did not arrive,
and on a project of this size the honest advice is to defer them until something is actually
scarce.

*The two-step writing process, on short documents.* Results → claims → text is the right
discipline for the manuscript and it is overhead on a batch report. This project wrote
thirty-one batch reports; requiring each of them to route through the claim collection would
have doubled their cost and improved none of them, and the rule was correctly applied only to
the documents that are the deliverable.

**The parts that were expensive and still worth it, which is a different category.** The
stability work cost four batches of construction and about eight hours of compute, and it is
the reason this write-up has anything to say beyond a score. Freezing the held-out set before
opening the year cost two batches of machinery — a manifest that verifies rather than rebuilds
itself, a seal with two conditions because one file could not carry both — and without it the
second spread would have been selection with extra steps.

**The one structural regret.** The alternatives-and-sub-analyses tree is a good fit for this
problem and a bad fit for the way an agent actually explores. Phase C's real history is a
search: build a family, sweep its forks, promote what wins, try another family. The tree
records the *outcome* of that search as a static set of siblings and loses its order. The
counterfactual branch — iterating the promotion rule to a fixpoint instead of applying it
once — had to be run on a git branch outside the tree because the tree has no shape for "what
this rule would have done if it had kept going". That is a real limitation of the structure
and not of this project's use of it.

## Limitations

**Nothing here reaches statistical significance and nothing pretends to.** The largest margin
the project achieved is 1.90 standard errors, on a backtest whose resolution is a property of
the pair being compared rather than of the dataset — and five of the six analyses, the
held-out headline among them, are below the project's own 1.03 line for the case where two
models cannot be separated.

**One held-out year, four splits.** Roughly 216 province-months. The external check gives two
more countries but not more years.

**The reference model is unseeded**, so every reported ratio is a draw. Our models are
bit-identical on re-run; the denominator is not.

**Three countries of one harmonisation are not a sample**, and the two sibling countries were
not held out from anything, because nothing was developed on them.

**The development-arrangement gap between Laos and the siblings is not attributable to
optimisation alone.** The three countries differ in province count, burden and reporting
system, and nothing in the design varies development while holding the country fixed.

**And the structural checks verify shape, never content.** A provenance record can name the
wrong script; a claim can point at a result that does not support it. One reported figure in
this project reproduced byte-identically across two runs while the sets it counts went from
four members to one — every check compares values, so every one of them called it reproduced.
Structural checking narrows where a human must look. It does not remove the need to look.
