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
  candidate 1 costs 0.2209 of skill, while the eight forks phase C spent three batches
  selecting among span 18.638 to 18.933 CRPS over their eleven combinations — about half the reference's own re-run noise.
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

- `26-09-01_b18_validationAndDrift.md` — batch 18, phase E: the two checks that had never
  been run here. `/validate cleanroom` found, **before executing a line**, that the holdout
  seal was versioned and therefore sealed every clone — a fresh checkout skipped all 32
  phase-E rows and reproduced their outputs byte-identically while running none of the
  analysis. On what it then ran, **every model this project wrote reproduced its mean CRPS to
  the last digit** and the unseeded reference moved the headline skill by 0.0065; the run was
  **interrupted at 8 of 32 rows**, so the distributions are unverified from cold and batch 25
  finishes it. `/validate outsider`, run for the first time, found three wrong counts — one in
  claim C3 — and six provenance records naming a commit orphaned by a history rewrite, which
  would have vanished on the first push. The plan's drift is measured: **89.1% of the
  delivered lines survive** while the document is five times its delivered length, and 145 of
  169 recorded decisions were the agent's alone.

- `26-09-01_b23_provenanceHashes.md` — batch 23, phase E: the `hashes` invariant, and the
  twenty appended provenance sections that make it pass. A record must name the **current**
  digest of every file it gives a sha256 for. Batch 18 estimated sixteen stale records by
  scanning `script:` lines; the check reads the whole block and finds **twenty**, the four it
  adds being records that name the shared evaluation library `chap_eval.py`, which changed
  twice after they were written. Nineteen of the twenty are one failure repeated: **a batch
  appends its section when it runs the script, changes the script again later in the same
  batch, and does not append again** — including the record of the headline result, which
  named a version of `conclude.py` that had not existed since batch 16 ran it thirty-two
  times to produce phase E. Two things verified rather than argued: the development stability
  figures were re-drawn after batch 16's refactor and came back byte-identical, PNG and CSV;
  and the reported development conclusion was **not** re-run, resting instead on batch 18's
  clean-room rebuild, because where re-running would have meant re-running an analysis this
  batch did not.

- `26-09-01_b24_frozenSetWins.md` — batch 24, phase E: the frozen phase-E set stops being
  rebuilt. `freeze_holdout_manifest.py` is the last step of the development half of
  `05_stability/run.sh`, so every run of `analysis/run.sh` re-derived the set that plan §3
  freezes; it came back byte-identical because the tree had not changed, and batch 18 added
  one fork child and got **34 rows**. The file is now authoritative — verified, never
  rewritten; a development row with no frozen twin is reported unpaired; once the year has
  been opened the set is restored from git rather than re-derived. A new `freeze` invariant
  checks the file rather than the script that wrote it, including the claim
  `holdout_freeze.json` makes about its own commit. Eleven situations were put to the two of
  them and all eleven behaved as specified; against the superseded script **six of seven fail
  and every one exits 0**, including the one batch 25 would have hit — a clean-room run
  rewriting the frozen development pairing with its own re-drawn reference numbers.


- `26-09-02_b25_cleanroomStoppedByItsOwnCheck.md` — batch 25, phase E, and **blocked**:
  `/validate cleanroom` was to run to completion and did not. It ran 3 h 48 m, completed all
  32 development rows, and **exited 1** at the freeze check. The development manifest's eight
  tier-2 rows are not planned from the tree but *selected* from tier-1 skill scores, which
  divide by the unseeded reference; a second draw re-selected **six of the eight pairs**, and
  batch 24's freeze defence correctly refused to rewrite the frozen set — the scenario batch
  24 predicted this run would be the first to hit. So the frozen phase-E set is a **decision**
  the record has been presenting as a **derivation**, and `analysis/run.sh` does not run to
  the end from a clean checkout. What it did verify is stronger than batch 18's: **96
  model-combination scores and not one of ours moved**, while the unseeded reference moved in
  26 of 32 and carried the headline skill by +0.0109. Two further findings: the reference
  noise band nearly doubled on a second draw (0.0218 → 0.0431), taking phase D's headline
  from **six of seventeen forks to three** with none of the three having moved; and the
  drifted selection immediately crashed on a combination the archived tier 2 never chose,
  where the CRPS-weighted pool correctly falls back to equal weights and `check_pool.py` asks
  for a validation block that was never written. Added batches 26 (record the selection
  rather than re-deriving it) and 27 (the clean-room, again).

- `26-09-02_b26_theSelectionIsRecorded.md` — batch 26, phase E, `done — produced`: the
  development manifest's **tier-1 order and tier-2 pairing become recorded decisions**
  instead of derivations. Both came from numbers that do not reproduce — the order breaks
  ties on measured wall-clock cost, the pairing ranks on a skill score that divides by the
  unseeded reference — which is why batch 25's clean-room run exited 1. Membership still
  comes from the tree, so `combos` keeps working and a late alternative is appended and
  reported; a recorded row the tree cannot produce is fatal. Five situations put to it, one
  driven by **the clean-room run's own `conclusions.csv`**: the rule chooses its six
  different pairs and the recorded eight stand. `check_pool.py` now branches on what the
  weighting did rather than what the combination asked for, which is how batch 25 lost a row
  to `KeyError: 'validation'`. **Nothing reported moves** — the manifest, its notes and all
  51 `pool_check.json` files are byte-identical. A third and larger defect was found and
  left standing as batch 28: `matching_evaluation` depends on which combinations exist on
  disk, so re-running the **unmodified** script changes 18 of 51 pool checks, and
  `main__holdout`'s archived copy calls its reconstruction impossible where it now returns
  76.646 against a reported 76.731 — with no number inside the eighteen moving.

- `26-09-03_b27_cleanroomToPhaseE.md` — batch 27, phase E, `blocked`: the clean-room run
  reached **phase E from a clean checkout for the first time**, opened the holdout, scored
  all 32 held-out analyses — and exited 1 at `pair_holdout_development.py`, the last script
  in the tree. **192 model-combination scores and not one of ours moved by a bit**, on both
  halves; the unseeded reference moved everything downstream of it. The phase-E headline CRPS
  reproduced to all 14 digits. `install-chap.sh`'s colour-corrupted lockfile comparison was
  fixed here; the script that stopped the run was left for batch 30, with the reason stated.
  Added batches 30 and 31.

- `26-09-03_b30_theFrozenFigureIsReported.md` — batch 30, phase E, `done — produced`: the
  check that stopped batch 27 now **separates a drifted figure from a moved pairing**. A
  frozen `development_skill_score` that no longer equals today's table is reported against
  the band that dataset's own repeats of the reference define; a frozen row whose development
  twin the table no longer concludes is fatal and stops the run before anything is written.
  The tolerance was deliberately not widened to the band, because the band is itself a draw.
  A **fourth instance of batch 24's family was found three lines away and fixed**:
  `development_beats_reference` was read from today's `conclusions.csv`, and on batch 27's
  clean-room numbers one row flips and the reported development count reads 28 rather than
  27; it now derives from the frozen CRPS columns, reproducing the archive on all 32 rows.
  `development_beats_all_baselines` cannot be — the baselines' CRPS was never frozen — and
  the output names it as the one re-derived development figure. Five situations put to it,
  one driven by **the clean-room run's own `conclusions.csv` and `distribution.json`**: exit
  0, 32 drifted figures, 0 moved pairings, largest move 0.025673 inside a band of 0.034944.
  **Nothing reported moves** — both output CSVs byte-identical, and `manifest_holdout.csv`
  untouched.

- `26-09-04_b31_cleanroomToCompletion.md` — batch 31, phase E, `done — produced`: **the
  clean-room run reached the end.** `analysis/run.sh` exited **0** from a clean checkout for
  the first time in the project — both datasets, all 64 combinations, both distributions, the
  last script in the tree, 41 677 s on a host held awake so the figure is a measurement.
  **192 model-combination scores from our models and none moved**; the phase-E counts
  reproduce exactly. Batch 30's categorical split is vindicated by the margin and not merely
  by the run finishing: the largest frozen-figure drift was **+0.051016 against a band of
  0.048273**, *outside* it, so the widened-tolerance alternative batch 30 rejected would have
  failed this run. Batch 27's claim that the holdout noise band is steady does not survive a
  third draw. And the finding that is not about reproduction succeeding: **`14 of 17 forks
  agree` came back byte-identical while the forks mattering on both datasets went from four
  to one**, so batch 19 reports such agreement by identity and not only by count. Added no
  batches; 28, 20 and 19 remain.

- `26-09-04_b28_theReconstructionStopsDependingOnDisk.md` — batch 28, phase E,
  `done — produced`: **the pool's second path stops recording the clock.** `check_pool.py`
  matched each pool member to a stored evaluation by globbing sibling directories and taking
  the first hit, so which evaluation it named — and whether it found one at all — depended on
  which combinations existed when it ran. The tie-break is now a rule over the combination
  names, and the last step of `05_stability/run.sh` settles every pool row once the whole set
  has run, because the rule alone would still have given one answer from a cold checkout and
  another from here. **The held-out headline row's reconstruction, called impossible for five
  batches, is reported: 76.646 rebuilt against 76.731 as run, and the pool beats its best
  member on 2010 by 4.767 CRPS.** All 51 files rewritten, 43 in naming only, **no number that
  existed before moved**. Eleven of the 51 pool rows can be reconstructed and forty cannot,
  for a reason that is a property of the frozen manifest. Added no batches; 20 and 19 remain.
