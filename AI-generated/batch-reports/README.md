# Batch reports

One report per executed batch of
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`. The plan is run one
batch per invocation of `/do`; each batch writes its report here and links it from the plan's
batch ledger.

Named `YY-MM-DD_bNN_camelCaseName.md`, where `NN` is the batch number. **A report is never
overwritten.** If a batch is redone, the new report is a new file and both stay.

Every batch ends in exactly one of three states, stated at the top of its report:

- **done — produced** — it created or changed something in the analysis, and the report says
  what and where;
- **done — expanded** — it produced no analysis output but replaced itself with more concrete
  batches, and the report says what made those possible;
- **blocked** — it could not proceed, and the report says exactly what is missing and what
  would unblock it.

These reports are the project's own running account of itself, so they are not regenerable
in the way the rest of `AI-generated/` is: they record what happened at a point in time, and
re-running a batch produces a different report rather than the same one.

## Currently here

- `26-08-23_b01_orientAndSetUp.md` — batch 1, phase A: orientation and repository set-up.
- `26-08-23_b02_chapSetup.md` — batch 2, phase A: installing and pinning `chap-core`, the
  model contract, and what `chap eval` actually computes.
- `26-08-23_b03_dataCharacterisation.md` — batch 3, phase A: pinning the Lao data, cutting
  off the held-out year, describing the development period, and fixing the backtest scheme.
- `26-08-23_b04_methodSurvey.md` — batch 4, phase A: running the reference model to get the
  score the project is measured against, and ranking the candidate model families against
  what the data will carry.
- `26-08-26_b05_bootstrapPlan.md` — batch 5, phase A: the claim-tree design, the fork
  inventory and the perturbation manifest, and the concrete batches for phases C, D and E.
- `26-08-26_b06_verticalSlice.md` — batch 6, phase B: the persistence baseline implemented
  against the Chap contract and run end to end on the development file, exercising every
  link in the chain once and giving the project its first CRPS from a model of its own.
- `26-08-26_b07_erectTheTree.md` — batch 7, phase B: the claim tree built from batch 5's
  design, the vertical slice routed through it and reproduced exactly, the seasonal
  climatology baseline and the reference model added as nodes, and the paired per-cell
  comparison that measures what the evaluation can and cannot resolve.
- `26-08-27_b08_candidateContract.md` — batch 8, phase C: the candidate subtree and its four
  configuration forks, the route model configuration takes into an `MLproject` model, the
  project seed's derivation into component seeds, and candidate 1 — a hierarchical
  negative-binomial GLM with the best point forecast in the project and the worst CRPS.

- `26-08-27_b09_candidateForks.md` — batch 9, phase C: every remaining child of candidate 1's
  forks built and run, two new forks for the structural choices batch 8 declined to make
  silently, three forks promoted by a rule committed before the combination it chose was run,
  and the finding that one-at-a-time fork effects do not add — three forks worth 4.632 CRPS
  separately delivered 2.402 together, and two of nine children reversed sign.
- `26-08-28_b10_boostedCandidate.md` — batch 10, phase C: candidate 2, gradient-boosted trees
  with a probabilistic head, and its two forks. The first model of ours to beat the reference
  on development — 20.771 against 22.098, ahead of each of its four repeats individually — and
  the first whose intervals are too wide rather than too narrow. Neither internal fork moved,
  and the family fork is left to batch 11 by batch 5's design. Its methodological centre is a
  prediction the head fork registered before it ran and a script that measured it afterwards:
  seven of eight named quantile levels flat at zero, the eighth flat in the one province that
  never reports one.
- `26-08-28_b11_ensembleCandidate.md` — batch 11, phase C and its close: candidate 3, a linear
  opinion pool over the two candidate families and both required baselines, holding no member
  code of its own — each member runs through its own Chap entry points. It scores **18.817**
  against the reference's 22.098, the family fork is promoted to it, and the project's
  reported conclusion turns positive for the first time at skill **+0.148**. Its two most
  useful results are both negative: a prediction registered before the run — that an equal
  pool would score worse than its best member — was **wrong** by 1.954 CRPS, and fitting the
  pool's weights on a year held back inside the training frame **cost 4.021 CRPS**, because
  the member that was best on that year is the worst on the years the backtest scores.
- `26-08-29_b12_perturbationManifest.md` — batch 12, phase D: the stability node, the
  perturbation manifest written and committed before any of it runs, the nine paths not
  taken created as nodes, and a new `combos` invariant that closes the combination space.
  Seventeen forks where batch 5 counted ten; 124 development minutes against a 12-hour
  budget, 89 of them re-running the reference model.
- `26-08-29_b13_setupAndScoringRows.md` — batch 13, phase D: the seven setup and scoring
  children built and their rows run, so 8 of the 24 tier-1 combinations have conclusions, plus
  the external population series `b_backCast` needed, archived from the World Bank. **The five
  `02_setup` forks move the conclusion less than the reference's own re-run noise; the single
  scoring fork moves it four times as much**, from re-weighting a stored file and re-running no
  model — and under case weighting the persistence baseline beats the reported pool while its
  coverage inverts. Three of the five setup rows move the score by moving the *reference*
  rather than our model. Where batch 12 found two defects by planning, this one found three by
  running: `conclude.py` naming a baseline as the project's model, an intermittent crash in the
  reference at about one job in a hundred, and a failed re-run leaving a results directory that
  looked complete while spanning two commits.
- `26-08-29_b22_baselineForkRows.md` — batch 22, phase D: the two baseline forks' children
  built and their rows run, so 10 of the 24 tier-1 combinations have conclusions and no child
  the tree names is unbuilt. **They are the extremes of the set**: freezing the climatology's
  estimation window moves the conclusion by 0.0025 of skill, and the persistence construction
  by −0.0279, the largest move of any row and the first downward one that clears the noise.
  The alternative persistence construction scores **4.181 CRPS better** than the main path's
  and beats the reference model, so the reported analysis stands on the worse of two published
  constructions of a required baseline — and **the pool that contains it is better off for
  that**, which with batch 11's weight-fitting result is the second demonstration that this
  pool's win comes from its members disagreeing rather than from their quality. Two more
  fork-blind globs found by building the rows: one would have made the reported model a
  six-member pool with two copies of each baseline, silently, under `main`.
- `26-08-30_b14_candidateAndFamilyRows.md` — batch 14, phase D: the twelve candidate rows, the
  two family rows and all eight tier-2 pairs, so **32 of the manifest's 33 rows have
  conclusions** and the development set is complete. **The model family is what the conclusion
  is sensitive to and the choices inside a family are not**: swapping the reported pool for
  candidate 1 costs 0.2209 of skill, while the eleven forks phase C spent three batches
  selecting among span 18.638 to 18.933 CRPS — about half the reference's own re-run noise.
  The one exception is the pool's own weighting fork, worth 0.1820. **Tier 2 shows the forks do
  not compose**: its largest interaction, −0.1033, is bigger than either main effect behind it,
  because the province filter and case weighting each improve the reported skill alone and
  almost exactly cancel together. Three defects fixed as planned and a fourth found by running
  into it — all four the same fork-blindness — plus the assembler lift batches 10 and 11 both
  deferred here, and the discovery that batch 13's two weighting rows had been reporting the
  main path's own paired spread under a re-weighted mean.
- `26-08-31_b15_perturbationReport.md` — batch 15, phase D and its close: `/perturb report`.
  The thirty-two analyses become the phase-D result — skill **−0.0724 to +0.2320** around a
  reported +0.1485 that sits **thirteenth of thirty-two** — and the plan's "most valuable
  single output" becomes one file and one figure: **six of the seventeen judgment calls move
  the conclusion further than the reference model moves on its own, and eleven do not**,
  against a band of 0.0218 measured from the reference's four unseeded repeats rather than
  chosen. Nine of the eleven below the band are the candidate-internal forks phase C spent
  three batches selecting among. The driver joins `analysis/run.sh`, which is now about four
  hours and reproduces the distribution as well as the reported result — safe because
  re-planning returns the frozen manifest byte-identical. The phase-E set is frozen at 33
  rows and 2.07 h with each row's development conclusion beside it, and the first twelve
  claims are written. Two smaller findings kept: `plan_manifest.py` documents a
  `--freeze-check` flag that does not exist and could not work as described, and the
  completed development manifest took 3.66 hours rather than the 3.2 batch 14 reported.
- `26-08-31_b16_holdout.md` — batch 16, phase E: the held-out year opened once, and the
  thirty-two analyses frozen before it was opened run against it. The reported pool scores
  **76.731** against the reference model's **84.026** — skill **+0.0868** where development
  read **+0.1485** — and still beats the reference and both required baselines. The finding
  is the distribution around it: **−0.5038 to +0.2026**, more than twice as wide as
  development's, with **28 of 32 analyses worse** on the year they had not seen and a rank
  correlation of only **+0.396** between the two orderings. The fork ranking transfers better
  (+0.679, 14 of 17 agreeing) but reorders at the top: the **province filter goes from 0.0376
  to 0.2696**, the largest fork effect in the project, and the analysis behind it — ranked
  fourth on development and highest of every analysis that does not re-weight the headline
  mean — is twenty-ninth on 2010, because the fork moves the **reference model** from 84.03
  to 64.72 while our pool moves 0.17. The holdout is reached by one switch keyed on the
  `__holdout` suffix, in `analysis/scripts/lib/combos.py` and nowhere else; the seal is opened
  by a script at `01_data/01_partition` that reassembles the archive from the two parts beside
  it and verifies it byte for byte. Three things kept: the driver began re-running the main
  holdout row before a guard was added, the freeze script was overwriting the commit that
  evidences its own freeze, and a figure title had been carrying a number nothing computed.
- `26-08-31_b17_claimsAndReport.md` — batch 17, phase E: the claim collection completed and
  the hierarchical report built. **Eighteen claims added, C22–C39, for 39 in total** — the
  phase-A, -B and -C half the file had been missing, since batches 15 and 16 had written only
  about the perturbation set and the held-out year: the development headline (**+0.1485**,
  18.817 against 22.098) and the fact that its margin — 3.282 CRPS against a split-clustered
  standard error of 1.726 — cannot separate the two models; the reference's own **0.565** CRPS
  re-run floor; what pooling bought (**1.954** over the best member, against a premise
  registered before the run that said it would not) and what fitting the pool's weights cost
  (**4.021**); the family that never beat the reference; three statements in the dataset's own
  schema that do not describe the file; and the byte-identical re-runs of all seven models we
  wrote. **The report is 1 175 pages** — the tree above, and four levels below it running
  national mean → province → month → per-cell score, for each of the 65 scored combinations on
  both datasets, with every number displayed from the file the analysis wrote rather than
  recomputed. Each node page now also carries the claims resting on it. Two things kept: the
  report was listing a `uv`-built virtual environment as **6 117 of one node's scripts**, fixed
  by asking git what the repository versions rather than by carrying a skip list; and it
  crashed sorting a province whose mean is empty because it contributes no evaluable cell.
  One discipline point, which changed what several claims say: **a claim states the figures a
  file holds and never a ratio between two of them that no file computes.**
