# Develop a spatio-temporal dengue forecasting model for Laos, veridically

The plan this repository exists to execute. It is written to be run by an agent that has
none of the conversation behind it in context: everything needed to start is either here or
in `Archive/case-source-material/`.

**Source material** — read before batch 1, and re-read the relevant part when a batch touches it:

- [[chapOrientation]] — the platform, the dataset, the evaluation command, and what was *not* verified
- [[reproAgenticAiManuscript]] — the manuscript this analysis is the worked case for; its
  *proposed comprehensive agentic AI setup* section specifies the claim tree, and its Appendix
  specifies what the case must demonstrate
- [[tenSimpleRules2013]] — the original rules the manuscript updates
- [[trustAgenticProposal]] — why an autonomously developed forecasting method on a real case
  is the interesting test, and what counts as an honest assessment of one
- [[trustAgenticSupplementary]] — §S2 model families worth trying, §S3 the provenance-and-agency
  schema, §S4 the veridical-robustness protocol

---

## 1. The aim

**Develop, as autonomously as the setup allows, a spatio-temporal model that forecasts
monthly dengue case counts across the provinces of Laos, and make it perform decently under
Chap's own standard evaluation.**

The dataset is `chap_LAO_admin1_monthly.csv` from
`https://github.com/dhis2/climate-health-data/tree/main/lao`: monthly dengue counts per
admin-1 province, 1998–2010, with rainfall, mean temperature, mean relative humidity and a
population figure. The evaluation is Chap's standard cross-validated backtest, run through
`chap eval`. The headline number is **mean CRPS across regions and across test splits**.

Two things are being produced at once, and neither is subordinate to the other:

1. **A forecasting model, with a defensible score.** A real result, developed the way the
   method would actually be developed.
2. **The complete veridical record of how it came about** — every execution, every
   environment, every judgment call and the alternatives to it, and how far the conclusion
   survives them. This record is what the manuscript reports on.

The second is the reason the first is being done. A model that scores well but whose
development is not reconstructable is a failed run of this project.

## 2. What "decently" means

CRPS has no absolute scale, so the criterion is comparative. The reference is a specific,
already-integrated Chap model: **`https://github.com/chap-models/chapkit_ewars_model`** — the
WHO EWARS-csd early-warning model for dengue. The aim is a model whose mean CRPS is:

- **below both required baselines** — persistence (next month = last observed month) and
  seasonal climatology (next month = mean of that calendar month in the training window);
- **and below `chapkit_ewars_model`**, both on the cross-validated backtest over the
  development dataset **and** on the held-out final year (§3).

**The aim is to conclude, and the conclusion will be an uncertain call.** One year of
holdout is roughly 216 province-months and twelve years of development data give a handful
of meaningful splits; nothing here will reach statistical significance, and no attempt should
be made to dress it up as though it had. What is reported is the comparison, its per-region
and per-split spread, and a plain statement of how much that spread can distinguish. An
honest "we cannot separate these two" is a conclusion.

**The comparison is a spread, not a point, on both datasets.** The stability work of phase D
produces a distribution of development results over the reasonable alternatives to each
judgment call, and **that same enumerated set is carried forward to the held-out year**, so
the final validation also yields a spread rather than a single number. The question is then
not "did our best configuration beat EWARS on one number" but "across the analyses that all
looked reasonable, how often and by how much did it, and on development and holdout alike".
That is the veridical form of the question and it is the one worth answering.

Report the mean CRPS with the per-region and per-split values behind it, and report
calibration (interval coverage) alongside. **A model that wins on mean CRPS while being
badly calibrated has not won**, and saying so is more useful than hiding it.

If, after the model-development phase, no candidate beats the baselines or EWARS, that is
the result. Report it plainly, with what was tried and what it cost. A negative result here
is a perfectly good outcome for the manuscript and a dishonest positive one is not.

**If `chapkit_ewars_model` turns out not to be runnable on this dataset, stop and bring it
back to me.** Report what blocked it, in detail — that is itself a finding about the
platform's model library, and a useful one. Then we reconsider §2 together and may well
choose a different method as the reference. The intent behind naming EWARS is that the model
should be **competitive against something real that the field already uses**, not that it be
competitive against that model specifically; a practical obstacle is a reason to change the
reference, not a reason to lower the aim. Do not pick the replacement on your own initiative,
and do not quietly fall back to the two required baselines as though they were the criterion.

*Settled 2026-08-23, in dialogue, from the batch-1 report §3.2. The reference model, the
requirement to beat it on both datasets, the refusal to imply significance, and the fallback
route are **human-set**; see §4b for what within this section the agent proposed.*

## 3. Non-negotiables

These override anything else in this plan. They are here because they are the specific ways
this particular project could go quietly wrong.

**The final year is removed from the data before any work begins, and touched once.** The
dataset runs 1998-01 to 2010-12. **2010 is cut off and set aside**; everything — model
development, tuning, selection, comparison, the whole of Chap's standard cross-validated
backtest — happens on the **development dataset, 1998-01 to 2009-12**, and until the final
validation of phase E nothing is ever pointed at anything but that file. At the end, in a
single batch, the holdout is opened and the final candidate, the baselines and
`chapkit_ewars_model` are validated against the held-out year.

This is stronger than splitting the backtest, because the held-out year is not merely
excluded from a metric — it is not in the file. An agent cannot leak what it cannot open.

Three consequences, all of them binding:

- **The holdout file is sealed.** During development, do not read its case values, plot
  them, characterise them, or reason about them. Batch 3 may confirm it is complete and
  well-formed — row counts, provinces present, no missing months — and nothing further.
- **If the holdout has to be opened a second time, record that it happened and why.** A
  holdout consulted three times is a development set, and calling it otherwise makes the
  headline number a lie.
- **The perturbation set run on the holdout is frozen before the holdout is opened.** §2 asks
  for a spread on the held-out year as well as on development, which means the holdout is
  opened once but evaluated many times — and that is only honest if *what* gets evaluated was
  fixed in advance. So phase D commits a perturbation manifest, phase E runs exactly that
  manifest, and **nothing is added, dropped, re-tuned or re-run after a holdout number has
  been seen.** A spread computed from a set chosen after looking is not a spread, it is
  selection with extra steps.
- **One year is a thin holdout**, roughly 216 province-months. Report the validation number
  with its per-region and per-split values and an honest statement of how much it can
  distinguish. Do not read a small difference between two candidates as a ranking.

**No number reaches a claim except through a file.** `chap eval` writes NetCDF; `chap
export-metrics` writes CSV. Every reported figure is read from one of those by a script, not
from terminal output by you. This is `AGENTS.md` §1 and it is the single most likely way this
project ends up dishonest.

**Every judgment call is a node or a logged decision, never silent.** Covariate set, lag
structure, model family, how population is used, how the zero-heavy early years are handled,
transformation of the target, horizon — each is either an alternatives node in the tree with
its rejected siblings intact, or an explicitly logged decision with its basis. See
[[trustAgenticSupplementary]] §S3 for the schema and §S4 for the protocol.

**Agency is recorded on every decision**: `human-set`, `agent-on-human-assessment`, or
`agent-autonomous`; and for information gathering, `agent-retrieved` or `human-pointed`. The
default here is `agent-autonomous` — that is the point of the exercise — so the entries that
matter are the exceptions. Do not flatter your own contribution, and do not flatter mine.

**Failures are kept.** Models that did not work, installs that did not build, approaches
abandoned: they stay in the record with what went wrong. The negative space is a deliverable,
not clutter.

**Chap runs locally, from a pinned version.** Not against a hosted service. An analysis whose
result depends on a remote service's current state cannot be reproduced from a clean
environment, which would defeat the whole project. If a local install turns out to be
genuinely impossible, stop and report it rather than silently switching — that finding is
itself worth having.

## 4. Decisions already made

Settled here so that execution does not reopen them. Where a decision turns out to be wrong,
say so and propose the change; do not quietly take a different one.

| | Decision |
|---|---|
| **Project seed** | `20260822`. Every component seed derives from it. |
| **Target** | `disease_cases` (reported dengue), monthly, admin-1, Laos. |
| **Development data** | 1998-01 to 2009-12. The only file development ever sees. |
| **Held-out data** | 2010-01 to 2010-12, sealed until the final validation (§3). |
| **Metric** | Mean CRPS across regions × splits, from Chap's own evaluation. Secondary: interval coverage, MAE. |
| **Required baselines** | Persistence and seasonal climatology, implemented as Chap-compatible models so they traverse the identical evaluation path. A baseline evaluated a different way is not a comparison. |
| **Reference model** | `https://github.com/chap-models/chapkit_ewars_model`, at its own default configuration. The target to beat on development and on holdout (§2). Not a candidate of ours and not tuned by us. *(human-set, 2026-08-23)* |
| **Stability on the holdout** | The phase-D perturbation manifest is frozen and re-run on the held-out year, so the final validation reports a spread over reasonable analyses rather than one number (§2, §3). *(human-set, 2026-08-23)* |
| **Model service framework** | `chapkit` (`github.com/dhis2-chap/chapkit`) may be used to build our own models against the Chap contract. Permitted, not mandated; whichever route is taken is a logged decision with its basis. *(human-set, 2026-08-23)* |
| **Where Chap runs** | Locally, version pinned by commit and recorded in the environment. |
| **Tracking level** | Full (`AGENTS.md` §6). This project is *about* tracking; the usual argument for a lighter touch does not apply. |
| **Data** | Pinned by repository commit hash, copied into `Archive/` unmodified, marked `(IS_SHADOW)`, with `provenance.md`. Public and redistributable. |
| **Scope of the tree** | The whole analysis, from data acquisition to reported score, is in `analysis/`. Nothing important happens outside it. |
| **Sibling datasets** | `tha` and `vnm` are **not** part of the headline analysis. They are an optional external check in phase E, and only if the budget survives that far. |
| **Git remote** | Do **not** create one. The release batch prepares the repository and stops for me. |

## 4b. Decisions settled during execution

§4 is what was fixed before the project started. This section accumulates what gets settled
while it runs, and **it is not an appendix to the plan but part of the result**. The purpose
of this project is the human's; how to carry it out is resolved in dialogue, and a record
that showed only the outcome of that dialogue and not its shape would misrepresent how the
work was actually done.

So each entry carries its agency honestly, in the vocabulary of `AGENTS.md` §4 — **human-set**
where the human decided, **agent-on-human-assessment** where the agent proposed and the human
chose, **agent-autonomous** where the agent decided alone and the human did not object. Do not
flatter either contribution. Where an entry changed the plan's text, the commit that made the
change carries the reasoning, and `Archive/plan-as-delivered/` holds the plan as it stood
before any of this.

### 2026-08-23 — settling §2, after the batch-1 report

| Decision | Basis | Agency |
|---|---|---|
| The reference is `chapkit_ewars_model`, at its own configuration, to be beaten on the development backtest **and** on the held-out year | Named directly by the human, replacing §2's unoperationalised "within reach of the best already-integrated Chap model". | human-set |
| Statistical significance is not attainable here and is not to be implied; the aim is to conclude, and to report the call as uncertain | The human's, and stated before any number exists — which is what makes it credible. A project that discovers its result is inconclusive and only then decides inconclusiveness is acceptable has decided nothing. | human-set |
| The stability spread is carried forward from development to the held-out year, so the final validation reports a distribution rather than a point | The human's. It is the substantive methodological addition of this round: it makes the holdout answer the veridical question rather than only the predictive one. | human-set |
| `chapkit` may be used to build our own models against the Chap contract | The human's; permitted, not mandated. | human-set |
| If EWARS cannot be run: stop, report what blocked it, and reconsider the reference together — a practical obstacle changes the reference, not the aim | The human's, correcting the agent's initial fallback to the two required baselines, which would have lowered the aim rather than preserved it. | human-set |
| The holdout perturbation manifest is frozen before the holdout is opened; nothing is added, dropped, re-tuned or re-run after a holdout number is seen | Proposed by the agent as the condition under which "spread on the holdout" stays honest, since the holdout is now opened once but evaluated many times. Accepted. | agent-on-human-assessment |
| Forks are of two kinds: those that change the data or the evaluation re-score every model including the reference; those internal to our candidates move only ours | Proposed by the agent. A comparison in which one side moved and the other did not is not a comparison. Accepted. | agent-on-human-assessment |
| The root's computed conclusion is a **skill score against the reference**, `1 − CRPS_ours / CRPS_ewars`, per analysis, with raw CRPS and coverage reported beside it | Proposed by the agent with the reasoning that raw CRPS is not comparable between development and holdout, so a raw dev→holdout gap confounds the agent inflating its own performance with 2010 being a harder year; a relative score controls for year difficulty and puts both spreads on one axis. The human chose it. | agent-on-human-assessment |
| `chapkit_ewars_model` is pinned by commit, and vendored if the URL cannot carry a ref | Agent's, unopposed. `chap eval --model-name <URL>` fetches at run time, so an unpinned reference would make the headline comparison depend on another repository's current state — the objection §3 already makes against running Chap as a hosted service, applied to the reference model. | agent-autonomous |
| If the budget will not carry the manifest twice, cut **forks run on both datasets** — never the full set on development and a subset on holdout | Agent's, unopposed. A holdout spread computed over a different set than the development spread is not comparable to it, so the asymmetric cut destroys exactly what the manifest exists to produce. | agent-autonomous |
| The plan as delivered is archived under `Archive/plan-as-delivered/`, and how it changes is a reported result | The human's, on the reasoning that how much of the original design survives the process, and what had to change, is evidence about how far an agentic system can be handed a plan and left to run it. | human-set |

### 2026-08-23 — settled by batch 2, from the installed platform

| Decision | Basis | Agency |
|---|---|---|
| Phase E runs Chap's own path: `chap eval` on the full file, with `n_periods + (n_splits−1)·stride = 12` so the evaluated span is exactly 2010. The script-computed-CRPS fallback batch 3 was told to prepare is dropped | Batch 2 established that the evaluated span is `n_periods + (n_splits−1)·stride` and always ends at the last period of the file, so the arrangement §7's batch 3 called *preferred* is available. The plan reserved the choice to whichever route turned out to be configurable. | agent-autonomous |
| Phase E reads the **archived original** rather than concatenating the two split files | Answers the open question batch 1 raised at its §3.3. Concatenating would also demonstrate the partition was lossless, but the partition can be verified where it is made, and reading the original keeps the number of files that must agree at one. | agent-autonomous |
| This project never implements CRPS. Aggregation level is ours; the score is always chap-core's `CRPSMetric` | Batch 2 found that per-region and per-split values are recoverable through chap-core's own metric API, so the case the plan allowed for — a hand-computed metric, flagged loudly — does not arise. A metric we computed ourselves is the one we could most easily bend without it being visible. | agent-autonomous |

### 2026-08-23 — settled by batch 3, from the data

| Decision | Basis | Agency |
|---|---|---|
| The backtest scheme is `n_periods 3`, `n_splits 8`, `stride 3`, `n_retrain 1` on development, and `3, 4, 3` on the full file in phase E. It does not move again | Seven candidates were run and costed against the data. `stride 3` because overlapping splits break the balance batch 2's metric identity depends on; `n_splits 8` because four splits make the development estimate a statement about a single dengue season and twelve leave the one training fit ending 2006-12 while predicting through 2009. | agent-autonomous |
| `n_periods = 3` is not a free choice | It follows from the human's selection of `chapkit_ewars_model` as the reference: chap-core forces `n_periods=3` for EWARS and the chapkit service declares `prediction_periods: 3`, so a different horizon would mean the central comparison never happens. | agent-on-human-assessment |
| The headline mean is over **16 provinces and 371 cells**, not 18 and 408, and this is reported rather than corrected | Vientiane never reports and is dropped by Chap's own region filter; Xaisomboun survives the filter, which looks only at the training period, and still contributes no evaluable cell. This is what §2's metric computes on this dataset, and changing it would be changing the success criterion, which is not the agent's. | agent-autonomous |
| Data acquisition is not a node in the claim tree; the fetch script lives in `AI-internal/data-acquisition/` and its record beside the data in `Archive/lao-dataset/provenance.md` | The tree analyses dengue in Laos and starts from the archived file. A node writing into `Archive/` would also break the read-only rule. Same split batch 2 made for reconnaissance. | agent-autonomous |
| `(IS_SHADOW)` is recorded in `Archive/lao-dataset/README.md` and `provenance.md` rather than in the data files | The marker inserts a line into the document; inserting a line into a CSV edits imported data and breaks the checksums that make the import verifiable. The convention is written for text documents and the repository now holds data. | agent-autonomous |
| Where the holdout's 24 missing target cells fall was not examined | §3 permits row counts, provinces present and missing months, "and nothing further"; their positions are a pattern in the target. Phase E will need them and phase E can have them. | agent-autonomous |
| Node scripts run under `environment/chapenv`, and `node.py` generates `run.sh` accordingly | The generator emitted `../.venv/bin/python`, which resolves to nothing below the first level of the tree and named the repository's own machinery rather than the pinned analysis environment. A node's declared environment and its generated main script now agree. Rule 4 makes this a methodological change. | agent-autonomous |

### 2026-08-23 — settled by batch 4, from the reference model

| Decision | Basis | Agency |
|---|---|---|
| The reference is pinned by **image digest** `sha256:abd8098f…` rather than by a `@<commit>` model URL or a local build | The published image's `org.opencontainers.image.revision` label is the source commit `a4c2fa42`, so the digest pins bytes and provenance together. A local build would have pinned our layer and left its own `chapkit-r-inla:latest` base floating, which is weaker than what §4b's original decision assumed. | agent-autonomous |
| Batch 4's reference run is reconnaissance; **the reported reference score is produced from a node inside the tree** | A result produced outside the tree does not exist, and the tree does not exist until batch 7. At 149 seconds per backtest the duplicated compute costs nothing worth weakening the rule for. | agent-autonomous |
| The reference's **unseeded stochasticity is measured and reported, not worked around** — four identical runs, sd 0.196 CRPS, 2.1 % range | `scripts/predict.R` calls `inla.posterior.sample` and `rnbinom` and never `set.seed`, and the service exposes no seed. Rule 6 cannot be satisfied for the model the success criterion names, so the honest move is to quantify the gap: any margin against the reference under about 0.4 CRPS is inside its own re-run noise. | agent-autonomous |
| The unpaired split-level standard error (5.65 CRPS, 26 % of the mean) is recorded as a property of the *dataset*, and phase C must compute the **paired** per-cell difference rather than lean on it | Split-to-split variation is common to both models and cancels in a paired comparison, so the unpaired figure is the right answer to "how variable is forecasting difficulty here" and the wrong answer to "how small a model difference can we detect". Recording both prevents the crude number being quoted later as the comparison's sensitivity. | agent-autonomous |
| Candidates are implemented as `MLproject` models with a `uv_env`, native Python; `chapkit` stays permitted but unused | No candidate on batch 4's shortlist needs a persistent service, and the `uv_env` route needs neither Docker nor an image build. This exercises the human's §4 permission by declining it, with a reason. | agent-autonomous |
| Spatio-temporal GNNs are **ruled out as a family**; the superensemble is ruled out as an *integration* but retained as an ensemble of our own candidates; the mechanistic thermal backbone is ruled out as a backbone and retained as a covariate-transform fork | Each against the data rather than against the budget: 16 nodes and 144 periods is not a graph-learning problem; the one integrated superensemble needs covariates the Lao file does not have and is the sole failure in the library sweep; and the Lao temperature range sits on the rising limb of the suitability curve, where a mechanistic transform is nearly monotone in temperature. | agent-autonomous |
| Whether our candidates **refit at predict time**, as the reference does, is a fork rather than a convention | The reference's `train.R` is a placeholder and its INLA fit runs in `predict.R`, so despite `n_retrain 1` it refits at every split. A candidate that fits only in `train` would be compared against a reference that refits eight times, which is a difference in what is compared rather than in model quality. | agent-autonomous |

### 2026-08-26 — settled by batch 5, from the design

| Decision | Basis | Agency |
|---|---|---|
| The two kinds of fork become a property of the tree's shape: every fork under `02_setup` re-scores every model, every fork under `03_models/03_candidate` moves only ours | §4b's rule was a convention that had to be applied correctly each time it came up. Placed in the tree it is checkable, and a fork in the wrong subtree is visible as a misplacement rather than left as an oversight. | agent-autonomous |
| A third case is recorded beside §4b's two: the **scoring fork**, which re-scores every model without re-running any of them | Re-weighting the headline mean re-aggregates stored per-cell scores. It is §4b's first kind by semantics and a different thing by cost, which is what matters when the manifest is costed. | agent-autonomous |
| The combination is an environment variable `COMBO`, defaulting to `main`, and every node reads and writes under `results/$COMBO/` | It makes the main path combination `main`, so `analysis/run.sh` and the stability run are the same code. A separate stability pipeline would be a second implementation of the analysis and the two would drift. | agent-autonomous |
| Models are re-run only when a fork upstream of them moved; the reuse is a column in the manifest | Re-running the emulated reference under a fork that cannot affect it buys nothing. Putting the reuse in the file rather than in the driver's control flow keeps which numbers were computed and which inherited on the face of the record. | agent-autonomous |
| **The forecast horizon is removed from phase D's fork list** | It is forced by the human's choice of reference model — chap-core forces `n_periods=3` for EWARS and the chapkit service declares `prediction_periods: 3` — so a combination at another horizon has no reference to be compared against, and the root's conclusion is a ratio to the reference. A fork whose conclusion is uncomputable is not a fork. | agent-on-human-assessment |
| Population becomes two forks: what the **column** contains (setup) and how **our model uses it** (candidate) | They move different sets of models. Batch 3's single entry would have put a candidate-internal choice into the subtree that re-scores the reference. | agent-autonomous |
| The reference is re-scored **four times** wherever it is re-scored at all, on development and on the holdout alike | It is unseeded and the conclusion divides by it; an unaveraged denominator carries the ~2 % wobble batch 4 measured, which is the size of the fork effects the manifest exists to detect. | agent-autonomous |
| Tier 2 of the manifest — the pairs — is selected by a rule written before tier 1 runs and applied by a script | Choosing which pairs to explore after seeing tier 1's numbers is selection with extra steps, which is the objection §3 makes to an unfrozen holdout manifest, applied one level down. | agent-autonomous |
| Phase C ends when the leaderboard's best moves by less than **0.4 CRPS** in a batch | The reference's own re-run spread, so the smallest movement that means anything. A stopping rule fixed before any leaderboard exists is the only kind that cannot be adjusted to suit the leaderboard. | agent-autonomous |
| Alternatives children are lettered `a_`, `b_`, `c_`; sub-analyses children keep `NN_` | `AGENTS.md` §8 numbers node directories "in the order the parent runs them", which is the ordered case. Alternatives are unordered and mutually exclusive, and the manuscript's own worked skeleton letters them. Batch 7 makes §8 say so, as a methodological change under Rule 4. | agent-autonomous |
| `06_holdout` is not created until batch 16 | A node that reads the sealed file must not be runnable while the seal is on. After batch 16, re-running `analysis/run.sh` re-reads the holdout; that is reproduction of a reported result rather than a second look, and it is recorded once in batch 16. | agent-autonomous |
| Batch 7 additionally builds `02_setup`, `04_score` and the reference node | Whether a paired per-cell comparison on 371 cells can separate two models is batch 4's first open question and the most expensive one to discover late. It needs only the reference and one trivial model, both of which batch 7 has. | agent-autonomous |
| The §9 budget is expressed in implementation effort, and phase C is cut to four batches with an evidence-based stopping rule | Batch 4 measured a full backtest at one to three minutes, so evaluation is not what binds. Batches allocated on a schedule rather than on evidence are the expansion-without-decision `AGENTS.md` §6 names. | agent-autonomous |

### 2026-08-26 — settled by batch 7, from the tree running

| Decision | Basis | Agency |
|---|---|---|
| **The development backtest resolves differences of about 4 CRPS, and nothing below 0.57 CRPS can be attributed to a model at all** | Measured, not assumed. The paired per-cell comparison is two to four times tighter than batch 4's unpaired figure of 5.68, giving a standard error of 1.3 to 3.0 depending on how the correlation between cells is treated — but both baselines sit 2.2 to 2.8 CRPS from the reference and neither difference clears two standard errors on any reading. The floor comes from the unseeded reference compared against its own repeats, which is a difference of exactly zero contaminated only by its sampler. This is what §2's instruction to report the call as uncertain will mean in practice. | agent-autonomous |
| Phase C's 0.4 CRPS stopping rule is **left where batch 5 fixed it**, although the measured floor is 0.57 | A stopping rule adjusted after seeing a number is not a stopping rule. The difference is small and the rule is if anything slightly too permissive, which is the safe direction. | agent-autonomous |
| **Calibration and lead-time structure are reported beside CRPS in phase C, not after it** | They separate these three models where the headline mean does not: the reference's per-province 10–90 coverage never falls below 0.542 while our baselines reach 0.042, and at one month's lead a persistence baseline is level with the reference (16.43 against 16.54) while losing badly at three. A candidate selected on mean CRPS alone would be selected on the least discriminating thing measured. | agent-autonomous |
| Each fork gets **only its main-path child** until the code that runs a sibling exists | Batch 5's design and this plan's batch-7 paragraph differ; the narrower reading was taken because a sibling that exists but cannot run would pass `/validate invariants` and advertise an alternative nobody can execute. | agent-autonomous |
| A stage finds its input by **searching for the one child of the previous fork with results under this combination**, never by naming a child | It is what lets the stability driver swap a child without any downstream script changing. Batch 5's file contract needs the mechanism and does not name it. | agent-autonomous |
| Every model of ours reaches `chap eval` through **one shared script** | "No candidate is compared on a metric computed a different way" is a constraint this plan states for phase C, and it is cheapest to enforce structurally rather than by care. | agent-autonomous |
| `install-chap.sh` **installs from `lock.txt`** rather than resolving afresh and writing it | Rule 3. A rebuild three days after the environment was pinned resolved a different package set while the lockfile sat unchanged in git; `environment/Dockerfile` had always installed from the lockfile, so the image and the local environment would have drifted apart silently. Found by accident during the clean-room check. | agent-autonomous |
| The reference's run costs from batch 7 are an **upper bound**, not a measurement, and batch 12 re-measures them | The machine was heavily loaded by unrelated processes during part of the run. A contaminated figure would otherwise go into the manifest costing. | agent-autonomous |
| **The headline weighting fork is not to be cut from the manifest** without an explicit decision | The reference is beaten by both baselines in the two provinces carrying the most evaluated cases and wins nearly everywhere else, so a population- or case-weighted mean moves weight toward where it does worst. Batch 5 costed this fork as the cheapest in the project; batch 7 gives the first evidence that it may be among the most informative. | agent-autonomous |

### 2026-08-27 — settled by batch 8, from the first candidate

| Decision | Basis | Agency |
|---|---|---|
| **Model configuration reaches an `MLproject` model through a file assembled from the forks**, not through a file checked in beside the model | Open since batch 2. The route is chap-core's own — `--model-configuration-yaml` → `ModelConfiguration` → `model_configuration_for_run.yaml` → the `{model_config}` placeholder in the entry points. Assembling the file from whichever child of each fork ran means the forks are the only record of what the model is; a checked-in file would be a fifth record and the one that actually ran. | agent-autonomous |
| The project seed is derived per component as **BLAKE2b of `"<project seed>:<component>"`**, read from the settings table in `readme-at-start.md` | Rule 6 asks for one seed derived downward. Reading it rather than copying it means there is no second number that could disagree; BLAKE2b rather than Python's `hash`, which is salted per process. The candidate is the first component in the project that draws at all. | agent-autonomous |
| The candidate's default covariate set is **rainfall and mean temperature at a two-month lag** | It is the reference family's own published configuration for this country: `laos_eval_config.yaml` in `chap-models/ewars_plus_template`. Taking the same pair at the same lag makes the first configuration a comparable one rather than a differently-tuned one. | agent-on-human-assessment; the configuration was `agent-retrieved` |
| **No autoregressive term on lagged counts in candidate 1's defaults**, although a lag of three is available at every horizon | None of the four forks batch 5 placed covers it, and adding a structural term outside them would be exactly the silent judgment call this project exists to make visible. It is proposed to batch 9 as a fifth fork instead — which is the visible way to add it. | agent-autonomous |
| **The reference is not re-run when a batch only adds a model of ours** | It is unseeded, so re-running replaces the four repeats with a different draw and moves the denominator of every conclusion. What makes the comparison paired is that every model was scored on the same 371 cells of the same dataset, checked by comparing `dataset_sha256` across the specs — not that every model ran on the same day. | agent-autonomous |
| **The backtest's resolution is a property of the pair being compared, not of the dataset alone** | Batch 7 measured ~4 CRPS using the two baselines. The candidate's paired difference against the reference has a clustered standard error of 1.11, less than half of persistence's 2.99, because the two models are structurally alike and fail on the same cells. A candidate built to be unlike the reference is harder to distinguish from it, not easier — which bears on how phase C's remaining candidates are chosen. | agent-autonomous |
| Phase C's 0.4 CRPS stopping rule is **applied as written and not adjusted**: it governs whether a further *candidate* batch is added | Batch 8 moved the best of our models by zero. Batch 9 is candidate 1's internal forks rather than a further candidate, so it proceeds; batch 10's admissibility depends on what batch 9 moves. Whether "the leaderboard's best" was meant as the best of ours or the best candidate is put to the human in the batch-8 report rather than settled here. | agent-autonomous |

### 2026-08-27 — settled by batch 9, from the fork sweep

| Decision | Basis | Agency |
|---|---|---|
| **One-at-a-time fork effects do not add, and two of nine reverse sign** | Measured. Three forks worth 2.115, 1.870 and 0.648 CRPS when each was taken alone from the batch-8 configuration delivered **2.402** together, not 4.632; re-measured from the promoted configuration, the hurdle is worth 0.601 rather than 2.115, the per-province annual variance 0.051 rather than 1.870, and dropping the climate covariates changes sign. This is the most important thing batch 9 found and it bears directly on phase D: **tier 1 of the manifest measures a quantity that does not compose**, so the distribution of conclusions it produces describes each fork's effect from one place in the space and not in general. Tier 2's pairs were designed to catch exactly this, and they now have evidence behind them rather than a precaution. | agent-autonomous |
| The promotion rule — **a fork moves only if its best child beats the main path by more than the 0.57 CRPS floor**, takes that fork's best child, and the promoted combination is then run; backed off if it is worse than the best single fork by more than the floor | Fixed after the sweep's numbers existed and **committed before the promoted combination was run**, so it cannot have been fitted to what it decided. The threshold is batch 7's measured floor rather than a position in the ranking, which is what keeps it from being a rule fitted to the sweep. | agent-autonomous |
| The rule is **applied once**, not iterated to a fixpoint | The second sweep, taken around the promoted path, has two children outside the floor — `b_refitAtPredict` at 0.873 and `b_rich` at 0.821 — so applying the rule again would move two more forks, and again after that. Iterating is greedy coordinate descent on development CRPS, which is precisely the failure §8's phase C warns about and which one held-out year cannot diagnose. Stopping after one application is a decision with a cost, and the cost is stated: roughly 0.9 CRPS left on the table. Whether phase C should iterate is put to the human rather than settled here. | agent-autonomous |
| **The width defect and the autoregressive term became forks, not model changes** | Batch 8 proposed both. A structural change made inside the model would have been the silent judgment call this project exists to make visible; as forks, each has a claim, a premise computed before it ran, a score, and a sibling that stays in the tree. That the autoregressive term turned out to be worth nothing is a finding the fork produced and a quiet change would have buried. | agent-autonomous |
| A combination **inherits what it did not move**, through `COMBO_BASE`, and every inheritance is recorded in the file that reports it | Batch 5's design named the reuse and left it to batch 12's manifest column. A candidate-internal fork changes nothing the reference or the baselines face, and the reference is unseeded — re-running it would replace its four repeats with a different draw and move the denominator of every comparison for reasons unrelated to the fork. `analysis/run.sh` sets no base, so the reported analysis inherits nothing. | agent-autonomous |
| The fork sweep is a **phase-C selection aid** and stops at `04_score/02_aggregate` | A `conclusion.json` per sibling is the phase-D deliverable. Producing nine of them in batch 9 would report the stability answer before the manifest that makes it honest has been frozen, which is the freeze discipline §3 exists to protect. The driver therefore lives in `AI-internal/` and writes every number into the tree through the tree's own scripts, keeping only the cross-combination table outside it. | agent-autonomous |
| The convergence tolerance was **not relaxed**, although the promoted fit runs to its 200-round cap | A criterion adjusted after seeing a run is a criterion adjusted to pass. The parameters are stable to six figures long before the cap; the flag says `converged: false`, and the record says why. | agent-autonomous |
| Phase C's 0.4 CRPS stopping rule **does not stop the phase**: batch 9 moved the best of our models by **2.402** CRPS | Applied as written. Batch 10 is admissible on the evidence the rule asks for. The ambiguity batch 8 raised — whether "the leaderboard's best" means the best of ours or the best model on the board — is still open and still the human's. | agent-autonomous |

### 2026-08-27 — settled by the human, on batch 9's open question

| Decision | Basis | Agency |
|---|---|---|
| **Phase C does not iterate the promotion rule on the main path.** Batch 9's decision to apply it once stands, and the reported analysis is the one that stopped | The human's reading of batch 9 §13: iterating is greedy optimisation on development CRPS, which is the failure this plan exists to watch for, and one held-out year cannot diagnose it. The 0.9 CRPS left on the table is accepted as the price of not selecting that hard | human-set |
| **The iterated path is run anyway, on a branch named `greedy` that is never merged**, as batch 21 | "It could be interesting to see where this would have taken us." What stopping cost is then a measured quantity rather than an estimate from one sweep, and the branch is the only place in the project where selection is deliberately pushed to a fixpoint — which makes it evidence about the method rather than a result about Laos | human-set |


### 2026-08-28 — settled by batch 10, from the second candidate

| Decision | Basis | Agency |
|---|---|---|
| **A model of ours beats the reference on development for the first time**: gradient-boosted trees at mean CRPS **20.771** against 22.098, ahead of each of the reference's four unseeded repeats individually, and the first margin in the project to clear the 0.565 CRPS floor | Measured. The paired difference is −1.327 with a split-clustered standard error of 1.110 — 1.20 standard errors, where batch 9's candidate was 1.03 on the other side. **This does not separate the two models and is not reported as though it did**; what changed is the sign of the point estimate, not the resolution of the comparison. It also repairs the failure batch 9 could not: Salavan, which carried the largest single piece of candidate 1's gap, goes from 55.09 to 35.44 — because a tree that separates two provinces gives them different widths as a by-product of giving them different means, which a constant log-scale width cannot do | agent-autonomous |
| **The family fork is not promoted in batch 10**, although candidate 2 leads candidate 1 by 2.927 CRPS — five times the floor | Batch 5's design assigns the family main path to batch 11, after `c_ensemble` exists. Promoting here would pre-empt a choice that must be made again one batch later. What batch 9's rule would decide on today's evidence is recorded in the batch-10 report §9, so batch 11 cannot decide otherwise without saying why | agent-autonomous |
| **The probabilistic head is where the family fails, and the reason was written down before the model ran** | The fork child computed its premise before anything was fitted and registered a prediction: every ladder level below the target's 56.3 % zero share cannot move off zero, because at those levels the majority of residuals sit exactly on the pinball loss's kink. Eight levels were named; **seven are flat at zero across the whole file** and the eighth is flat in the one province that never reports a zero, whose observed median is 109 cases. A script compares the two afterwards and writes the comparison to a file, so the confirmation is an artifact and not a reading. **This is the shape of veridical work the manuscript argues for, and it cost about twenty lines** | agent-autonomous |
| The quantile head's failure is **kept, not repaired** | The repair is a hurdle over the ladder — the construction candidate 1's `01_observation` fork already promoted — and would be a third child of `02_head` rather than a change to this one. A fork child rebuilt until it worked would leave the tree with no record that the plain construction does not. §3's "failures are kept", applied where it costs something | agent-autonomous |
| **The two heads fail in opposite directions**, and reporting either number alone would mislead | The ladder has the project's closest interval coverage — 0.798 against nominal 0.80 — and its worst point forecast, MAE 33.020, because a median pinned at zero is far below the outcome wherever a province reports steadily. §2's "a model that wins on mean CRPS while being badly calibrated has not won", arriving with the halves swapped | agent-autonomous |
| **scikit-learn enters the project**, in one model's environment, pinned exactly by the lockfile beside it; and the fitted ensembles are stored as JSON this project's own code can walk | Gradient boosting is binning, split finding, shrinkage and a stopping rule — not two functions, so the argument that hand-wrote candidate 1's fitter points the other way. Rule 5 then forbids pickling the result, so the trees are written out as arrays and read back by a second prediction path; because a second path can disagree, every fit checks it against scikit-learn's own prediction and fails if they differ. Batch 21's finding — that a rule selecting on development CRPS cannot see whether the model it selects can be inspected — is the direct ancestor of this | agent-autonomous |
| The boosting hyper-parameters are a **logged decision, not forks**; the round count is chosen by a **time-ordered** early-stopping split | §3 permits a judgment call to be a node *or* a logged decision. Forks here would enumerate a tuning grid whose siblings all re-run in phase D and again on the holdout, to answer a question about tuning rather than about a choice an analyst would plausibly make differently. The stopping split is by month because a rule scored on rows interleaved with the training rows is choosing a model for a different problem than the backtest poses | agent-autonomous |
| **Two of the three comparison figures would have dropped a series silently** on the fifth model, and the invariant checks could not have seen it | All three built their colour maps by zipping the models present against a four-entry list, and `zip` stops at the shorter argument. The figure would still have existed, with its plotted values beside it, and looked wrong only to someone counting series. Fixed at the cause — one shared palette keyed on the model's own name, so a model keeps its colour across combinations and two figures stay comparable. **It bears on §5 of `AGENTS.md`: what a deterministic check can see is not everything** | agent-autonomous |

### 2026-08-28 — settled by batch 11, from the ensemble and the family fork

| Decision | Basis | Agency |
|---|---|---|
| **The reported conclusion is positive.** The main path is a linear opinion pool over the two candidate families and the two required baselines, at mean CRPS **18.817** against the reference's 22.098 — skill **+0.1485**, ahead of both required baselines, ahead of each of the reference's four repeats individually, and better in six of the eight splits | Measured. The paired difference is −3.282 with a split-clustered standard error of 1.726: **1.90 standard errors, which does not separate the two models**, and is not reported as though it did. What changed against batch 10 is that the margin is now nearly six times the 0.565 CRPS floor rather than twice it | agent-autonomous |
| **The family fork moves to `c_ensemble`**, by a rule written after the family leaderboard existed and committed before the promoted family was run under `main` | `AI-generated/candidate-forks/family_rule.md`: batch 9's 0.57 CRPS threshold unchanged, each family compared at its own main path, plus one clause an internal fork does not need — a family that wins on mean CRPS while being badly calibrated has not won, checked at the 10–90 level because the 25–75 level is bounded below by the target's 56 % zero share. The pool beats candidate 1 by 4.881 CRPS and its 10–90 coverage is closer to nominal, so the calibration veto does not fire | agent-autonomous |
| Candidate 1's `results/main/` are **removed** and it is re-run under `family_hierNB`, where its per-cell scores are **identical** | They described a main path that no longer exists, and `04_score` discovers models by the `model_spec.json` they wrote, so leaving them would have put a row on the reported leaderboard that `analysis/run.sh` does not produce. Batch 9's precedent for demoted fork children, applied one level up. Git holds them at commit `4cdfd16` | agent-autonomous |
| **Estimating the pool's weights costs 4.021 CRPS**, and that is the batch's most useful result | The sibling fork fits the weights to minimise the pool's own CRPS on a year held back inside the training frame, and finds the exact minimiser there — 14.227 against 17.026 at equal weights. It puts 0.953 of the pool on the member that was best on that year, which is the **worst** of the three non-baseline members on the period the backtest scores. One year of held-back data does not say which member will be best on the next two. This is the plan's phase-C warning — fitting the available data rather than the data-generating process — happening inside the tree with both sides in one table, and it is a stronger argument for the equal pool than the equal pool's own score | agent-autonomous |
| **A prediction registered before the run was wrong, and it is kept where it was written** | `a_equal` predicted that an equally weighted pool would score worse than its best member, because half its mass sits on the two required baselines. It beat its best member by 1.954 CRPS. The prediction reasoned about where the forecasts sit and not about how wide they are; every member but candidate 2 under-covers, and pooling widens. Its other two clauses held. **Two batches running, the registered prediction has been the most informative artifact in the batch, and in this one it was informative by being false** | agent-autonomous |
| The winning model is the **most over-dispersed** in the project, and the innocent explanation was measured and rejected | 10–90 coverage 0.863 against nominal 0.80 — conservative, and second-closest to nominal of the six models — but 25–75 coverage 0.749 against 0.50. A count target that is 56 % zeros gives a model with a large atom at zero a degenerate central interval, which would inflate that figure for free; the share of cells where each model's own quartiles coincide is therefore measured, and the pool is at 0.240 against 0.412 to 0.547 for three of its four members. It over-covers while being *less* exposed to the artefact, so the over-dispersion is real. §2's "a model that wins on mean CRPS while being badly calibrated has not won", reported rather than buried | agent-autonomous |
| **The pool contains no member code**: each member runs through its own Chap entry points, read out of the member's own `MLproject`, and its configuration is assembled under the running combination by that member family's own scripts | One copy of every member's code, at the node that owns it, and a pool that follows a phase-D perturbation: a combination that moves candidate 1's observation fork moves the pool's candidate-1 member with it. `AGENTS.md` §2 sanctions a node running its siblings' scripts — it is how the stability node executes the paths not taken. The cost, paid explicitly, is that the pool's environment is the union of its members' | agent-autonomous |
| The pool is **verified by a second path**: rebuilt from its members' own stored evaluations and scored with chap-core's own CRPS, it gives 18.801 against the 18.817 it scored | A model that beats every model in it needs more than one route to the claim. The residual 0.016 is the sampling error of the pool's own allocation, and the members' scores by that second path reproduce their leaderboard rows exactly, so the models inside the pool are the models on the leaderboard. Members are matched to evaluations by **configuration hash**, never by combination name | agent-autonomous |
| **The assembler lift batch 10 scheduled for batch 11 is deferred to batches 13–14**, and the deferral is recorded in four places | Lifting the shared part of the three candidates' configuration assemblers into `03_models/scripts/lib/` changes two scripts' sha256, and those hashes are in the provenance record of every combination they configured — thirteen — whose results would then name a script that never produced them. Batches 13–14 re-run every combination in the frozen manifest, which is when regenerating those records costs nothing extra | agent-autonomous |
| **Phase C is closed although its stopping rule permits another candidate batch** | The rule makes a further batch admissible, not required: batch 11 moved the best of ours by 1.954 CRPS against the 0.4 threshold. Closing is the judgment that the stability answer is worth more than a better score — this plan's own words — and that another round of selection on development CRPS is the failure phase C warns about. Two candidate targets that were *not* built are named in the batch report §12, both of them deliberately: a width fork on the pool would have been a repair fitted to the calibration number it repairs, and a candidates-only pool would answer how much of the win is persistence | agent-autonomous |
| `verify_model_determinism.sh` names **every** candidate by its own node path | It named candidate 1 by the family node, which was correct only while candidate 1 was the main path: after the promotion it would have run the pool twice and reported it `identical` under the name `hier_nb`. Batch 10 fixed the same shape of error for candidate 2 alone; this generalises it. The list has now been edited twice for one reason, which is the argument for discovering the leaves if a fourth family arrives | agent-autonomous |
| **A model node was reading a scoring node, and the check found it** | The first version of the equal-weight fork child read `04_score`'s leaderboard for its premise — a circular dependency invisible under `main`, where an earlier run's leaderboard was on disk, and fatal the moment the node ran under a combination whose scoring chain had not. The premise now reads only the shape of the tree and the numbers about members are measured afterwards. Two batches running, the thing that went wrong was caught by a deterministic check rather than by reading the code, which is `AGENTS.md` §5 working | agent-autonomous |

### 2026-08-27 — settled by batch 21, from the greedy branch

*(Produced on branch `greedy`, which is never merged. The report is
`AI-generated/batch-reports/26-08-27_b21_greedyBranch.md` **on that branch**; every number
below is read from a file there.)*

| Decision | Basis | Agency |
|---|---|---|
| **Iterating the rule reaches a fixpoint in three rounds at 21.275 mean CRPS**, past the reference's 22.098 and past each of its four repeats individually — and changes nothing the project can conclude | The paired difference against the reference is −0.823 CRPS with a split-clustered standard error of 1.602: half a standard error, where batch 9's candidate was 1.03 on the other side. The main line's "we cannot separate these two" survives the counterfactual with the sign of the point estimate reversed, which is the strongest available evidence that stopping cost the project nothing it reports. The third round's sweep found the best remaining move worth 0.150 CRPS, so the branch stopped at a fixpoint rather than at its round cap | agent-autonomous |
| **The cost of iterating is paid in the record, not in the score.** The first fork the rule moved (`04_fitTime` → `b_refitAtPredict`) is the one under which the model has no stored fitted object at all | On the branch, `a_hierNB/results/main/fitted_model.json` is a 520-byte stub where the main line's carries seventeen annual variances, two blocks of coefficients and an EM history. A rule that selects on development CRPS cannot see whether the model it selects can be inspected. This is an argument for the main line's decision that the score alone does not give | agent-autonomous |
| **A second demonstration that one-at-a-time fork effects do not compose, with the sign reversed** | The lagged-count term is worth −0.075 around batch 8's configuration, +0.353 around batch 9's, and +0.582 once the model refits inside `predict` — it and the refit are complements, and no one-at-a-time sweep can see a complement. With batch 9's finding that three forks overstated their combined worth, **tier 2 of the phase-D manifest now has two independent demonstrations behind it** and batch 12 must not cut it | agent-autonomous |
| The branch's model does **not** join the phase-D manifest, and the holdout is not opened on it | The project has one opening and it belongs to the frozen manifest. Whether the greedy model should be carried into phase E is the human's, not settled here | agent-autonomous |
| **`verify_model_determinism.sh` was reporting `differs` unconditionally, and was repaired.** Both passes now run under one scratch combination name; pass 1's outputs are copied aside and compared with what pass 2 writes over them | Batch 9 added a `scored_under_combo` column to `models.csv` and the check ran its two passes under combinations named `…_1` and `…_2`, so it was comparing a field whose value is the pass's own scratch name — `identical` at `509d458`, `differs` at `dec4116` and every run since, whatever the models did. **Rule 6's only instrument was stuck on red**, which is the failure `AGENTS.md` §5 guards against arriving in the guard itself. The repair exempts nothing from the comparison, which is why it is a fix and not an adjustment to pass; the alternative of dropping the one column was rejected because an exemption list is where a second exemption can later be added unnoticed. Re-run, the check reports `identical` for all three models. Batch 9's report carries a dated correction: what it claims in words — identical per-cell scores and fitted objects — held throughout, and only its citation of the status word did not | agent-on-human-assessment |


### 2026-08-29 — settled by batch 12, from the manifest

| Decision | Basis | Agency |
|---|---|---|
| **The fork inventory is computed from the tree, not listed.** `05_stability/scripts/lib/inventory.py` walks `analysis/` for alternatives nodes | Batch 5 wrote the inventory by hand and counted ten forks. The tree has **seventeen**: phase C added five while building the candidates, and the two baseline forks were never on the list although this plan's phase D names one of them. The same omission would recur the next time a fork was added. `/validate invariants` now fails when the manifest and the tree disagree, so a fork added later is in the manifest or the check says so | agent-autonomous |
| **The nine children this tree named in prose are created as nodes**, scaffolded and unbuilt | `/perturb` says to prefer making a judgment call an alternatives node so the path not taken survives. Four `02_setup` forks, the scoring fork and both baseline forks had exactly one child each, so seven of the ten judgment calls phase D exists to perturb were sentences in a `claim.md` rather than paths in the tree. They are now nodes with claims; batch 13 and batch 22 write their scripts, and the driver's `--dry-run` prints the step list each has to satisfy | agent-autonomous |
| **The two baseline forks moved kind.** They re-run our reported model as well as their own leaderboard row | Batch 11's pool takes both required baselines as members, so how persistence wraps uncertainty around its point is now a choice inside the model this project reports. Batch 5 costed that fork as moving one row. Nothing about the fork changed; what changed is what depends on it — and the same promotion is why the manifest gained a whole kind of row rather than two cheap ones | agent-autonomous |
| **The manifest is 24 tier-1 rows, not batch 5's 20**, and its arithmetic is a script's rather than a report's | Seventeen forks with 23 non-main children, plus the main path. Batch 5's figure was stated as 20 and its own components sum to 17, which is the argument for computing it | agent-autonomous |
| **Tier 2's rule is written out and hashed before tier 1 runs**: rank tier-1 rows by \|Δ skill\| from the main path; take the top two `setup` rows, the top two rows of the three kinds that move our model, and the top scoring row; every cross-group pair is a tier-2 combination — 2×2 + 2×1 + 2×1 = **8** | Batch 5 fixed "the two setup forks and the two candidate forks, crossed: 8", whose arithmetic only closes under the cross-group reading. That reading is fixed here, with the count it was chosen to preserve. The rule's sha256 is in `manifest_notes.json` so that it cannot be edited into a different rule after the numbers are in. Batches 9 and 21 each demonstrated that one-at-a-time fork effects do not compose, so tier 2 is not cut | agent-autonomous |
| **Compute is not what binds, by a factor of four**, and the manifest says what does | Tier 1 costs 124 minutes on development and 75 on the holdout against a 12-hour budget, so nothing is cut and the cut order is recorded against the day something is. **89 of those 124 minutes are the reference model** — five setup rows at four unseeded repeats each, through an amd64 image under emulation, for the one model this plan forbids perturbing. Every model of ours across all of tier 1 costs 21 minutes together | agent-autonomous |
| The budget is **12 wall-clock hours for the manifest run twice**, set by the agent | No compute budget had ever been fixed in figures; §9 and `readme-at-start.md` say only that compute does not bind. Twelve hours is roughly one unattended overnight run on this machine and is four times the estimate, so it constrains nothing now and is a number the human can move. Raised in batch 12's report rather than left implicit | agent-autonomous |
| **Every cost in the manifest is measured, including the pipeline's own steps** | Batch 5's cost table was arithmetic on two measured backtests and labelled an estimate, with batch 12 named as the batch that replaces it. The model terms are now each model's own `run_cost.json`; the setup, scoring and conclusion steps are timed by `measure_step_costs.py`, which re-runs them under `COMBO=main` and checks with git that they leave the tree byte-identical — a step that is not idempotent cannot be timed this way and the check is what says so | agent-autonomous |
| **Twelve tier-1 rows have results on disk that their row would replace**, and this is recorded rather than discovered in batch 14 | `observation_negBinomial` meant "our model is candidate 1 with a plain negative binomial" in phase C and means "our model is the pool, whose candidate-1 member has a plain negative binomial" now. Same name, different analysis. Which is which is not guessed: `01_collect` writes a `models.csv` naming every model it scored, and the planner compares that against what the row would produce. Batch 14 removes them before re-running, as batch 11 removed candidate 1's `results/main/`, with git as the witness | agent-autonomous |
| **Two defects block twelve built rows**, found by planning rather than by running | `prepare_members.py` runs *every* member fork's main-path child when it assembles a configuration, so a combination that has already run a sibling of one of them gives the assembler two children of one fork and it fails by design. And `conclude.py` resolves our reported model from `claim.md`'s `main-path` field, which does not move with the combination, so every family row would report `candidate_exists: false`. Both are fixed in batch 14 alongside the assembler lift batch 11 deferred there, which is the batch that re-runs those rows anyway | agent-autonomous |
| **The driver is written and is deliberately not in `run.sh` yet** | Nine children have no scripts and twelve built rows are blocked, so calling it from `analysis/run.sh` today would write a dozen failed combinations into the tree on every run. It joins `run.sh` in batch 15, when every row can run — which is what makes `analysis/run.sh` reproduce the stability result as well as the main one. Recorded in the node's `claim.md`, in a comment in `run.sh` itself and here, rather than in nobody's notes | agent-autonomous |
| **A new invariant: the combination space is closed.** `/validate invariants` gains a `combos` check | Every `results/<name>/` directory must be a combination the manifest names, and the manifest's tier-1 rows must agree exactly with the tree's non-main children. It found something on its first run — `family_ensemble`, a real combination with no manifest row — and the fix was to make the manifest complete rather than to exempt the directory. Provenance records may now name an artefact by its combination-invariant path, `results/$COMBO/eval.nc`, which is what the record of a combination-parameterised step actually says; the placeholder only satisfies files whose combination the manifest names, so the two checks close over each other | agent-autonomous |
| **Batch 22 is appended**: the two baseline forks' children, built and run | Batch 13 already has seven children to write and five twenty-minute setup rows to run. The baseline children are two new Chap-contract models and they move the reported model, so they are not a footnote on somebody else's batch. The ledger is executed top to bottom and the number is an identifier — batch 21 already broke the number-equals-position property | agent-autonomous |

### 2026-08-29 — settled by batch 13, from the first rows to run

| Decision | Basis | Agency |
|---|---|---|
| **The five `02_setup` forks do not move the conclusion; the one scoring fork moves it four times as much as any of them** | Skill spans +0.1266 to +0.1861 around the main path's +0.1485 across the five dataset choices, every gap smaller than the reference's own 0.57 CRPS re-run spread. Re-weighting the same per-cell file, re-running nothing, gives +0.2288 and +0.2320. The cheapest row in the manifest at thirteen seconds is the one the conclusion is most sensitive to, and the twenty-minute rows are the ones it is not | agent-autonomous |
| **Under case weighting, persistence beats the model this project reports** — 86.598 against 88.484 — and the pool's 10–90 coverage falls from 0.863 to 0.701 | The pool is too wide on the quiet months that dominate the unweighted mean and too narrow on the outbreak months that dominate this one; no single weighting shows that. It does not overturn the headline, which is defined against Chap's own unweighted mean, and §2's rule that a badly calibrated winner has not won is why it is reported beside the score. It is the most useful thing tier 1 has produced | agent-autonomous |
| **Three of the five setup rows move the reference rather than our model** | Removing the two unevaluable provinces costs the reference 1.05 CRPS and our pool 0.03; merging Vientiane costs it 0.84 against our 0.19. EWARS pools across provinces while fitting and our pool's members largely do not, so a setup choice that looks like data hygiene is, for this comparison, a change to the opponent. Invisible in a headline that reports only our own score, and an argument for the ratio §4b already fixed | agent-autonomous |
| **The reference model crashes about once in a hundred jobs**, and each repeat is now retried up to three times | `Prediction script did not create output file`: the R process exits without writing. A setup row asks for 36 jobs and `retrain_everySplit` for 64, so rows failed about a third of the time for reasons that say nothing about the row. Legitimate only because the model is unseeded — every repeat is already a draw, so a retry replaces a crash and not an unfavourable number — and `attempts_per_repeat` records the count. Both re-run rows needed one attempt per repeat. This is a finding about the platform's model library of the kind §2 asks to be reported | agent-autonomous |
| **A failed re-run of the reference left a results directory that looked complete**, and the node now clears it first | Three repeats from the new run, one from the old, and the previous run's `model_spec.json` beside them: a per-cell reference mean spanning two commits, which nothing downstream could detect. The most dangerous thing this batch found, because it produces a wrong number no check was looking for | agent-autonomous |
| **`conclude.py` reported a required baseline as the project's model** on both scoring rows | It resolved our model by globbing under `results/$COMBO/` only, and a combination that re-runs no model of ours has none, so it fell through to "best-scoring model of ours" — persistence, under case weighting. The fix falls back to `COMBO_BASE` only when no child of the family fork produced a spec under the combination, so batch 14's separate family-row defect is untouched. Found by reading the output, not by a check | agent-autonomous |
| **The tier-2 rule is not applied until every tier-1 row has been attempted.** `tier2_rule.md` is unchanged and its sha256 is unchanged | Applied after batch 13 the rule would have filled group A and half of group S, selected two pairs instead of eight, and recorded a shortfall that is an artefact of the running order — and batch 15 would then have got a different tier 2 with nothing to say which was frozen. What changed is when a rule about the ranking of tier 1 may read a tier 1, which is why the rule's hash did not have to move | agent-autonomous |
| **Batch 12's cost model predicts the total to 2 % and every individual row wrongly** | Planned 6 041 s against 5 901 s actual, with row ratios from 0.577 to 1.851 and all five setup rows costed identically at 1 202.9 s. The model summed each row's parts as measured under `main` and could not know that a row changes how much work a part does — `retrain_everySplit` makes the reference run sixteen jobs a repeat instead of two. **The cut order within a kind is ranked on a constant.** Nothing was cut, so nothing rests on it; it is recorded because it could not have been relied on | agent-autonomous |
| **The archived population column does not have the level its schema claims** | It sums to 4 961 076; the national total at the schema's stated 2020 reference was 7 346 533, and the nearest year is 1995. The third statement in that schema found not to describe the file, after the row count and the rainfall unit. The back-cast anchors where the schema says anyway, because under a log offset the anchor is a constant the intercept absorbs, so the two anchors are the same analysis and using our own inference instead would trade a recorded discrepancy for a silent correction | agent-autonomous |
| The population back-cast uses a **national** series, so it probes a trend and not a provincial differential | The provincial censuses of 1995, 2005 and 2015 have no pinnable machine-readable release, and an input transcribed by hand from a PDF is the manual step Rule 2 exists to keep out. The World Bank series can be fetched, checksummed and re-obtained; the loss is stated where it bites rather than buried in the archive | agent-autonomous |
| The three children of the weighting fork share **one** implementation, and `a_unweighted` was moved onto it | The fork's whole content is the weight, so three copies of one aggregation is the drift `chap_eval.py` was created to prevent, one node over. The unweighted case is kept as its own code path inside the library because weighting by ones and taking a mean are the same number in arithmetic and not always the same float; re-run, `results/main/` is byte-identical, which is the check that no reported number moved | agent-autonomous |
| **`node.py rebuild` will re-add the stability driver to `run.sh` every time it is run there** | Adding a script to the node meant regenerating `run.sh`, and the generator lists `scripts/` alphabetically — which put `run_manifest.py` back into the file batch 12 deliberately kept it out of, and reordered the rest out of dependency order. The block now carries a warning saying what to do when it happens again | agent-autonomous |

### 2026-08-29 — settled by batch 22, from the two baseline forks

| Decision | Basis | Agency |
|---|---|---|
| **The reported analysis stands on the worse of two published constructions of a required baseline, by 4.181 CRPS, and the fork is not promoted** | The parametric persistence construction scores 20.698 against the main path's 24.879 and beats the reference model at 22.098 (paired −1.400 ± 1.424, 0.98 standard errors). Batch 6's reasoning for rejecting it was sound — an arbitrary floor doing visible work in the 52 % of months that report zero — and it understated the problem, because the maximum-likelihood dispersion does not exist for an all-zero window and needs a second arbitrary constant, a bound, which binds for six of seventeen provinces. It wins anyway. It is **not promoted**: phase C closed at batch 11 and the manifest was frozen before this row ran, so moving a main path on a stability row would make the reported analysis a function of the stability run — the ordering the whole design exists to prevent. Reopening phase C for it is the human's | agent-autonomous |
| **A better member is a worse pool**, and this is the second independent demonstration that the pool's win comes from disagreement rather than member quality | With the sharper persistence member every summary of the pool's inputs improves — best member 20.771 → 20.698, mean of the members' means 23.421 → 22.376 — and the pool scores 0.617 CRPS worse, its margin over its own best member falling from 1.954 to 1.264. A linear pool's spread is the mean of its members' spreads plus the spread between their means; a sharper, better-centred member narrows it, and it lost more from being narrower than it gained. Its 10–90 coverage falls from 0.863 to **0.817**, the closest to nominal the reported model has been — better calibrated on the row where it scores worse. Batch 11's result that fitting the weights costs 4.021 CRPS is the same fact from the other side | agent-autonomous |
| **The shape of a baseline's predictive distribution matters here and the window it is estimated over does not** | Two forks of the same kind on the two required baselines, an order of magnitude apart: the persistence construction is worth 4.181 CRPS and freezing the climatology's estimation window 0.532, which is inside the 0.565 floor. The frozen table forecasts two dengue seasons it never saw, on a series whose reporting improved throughout, and the difference does not clear the noise — the node's own claim had argued before the run that it would | agent-autonomous |
| **Every constant in the alternative construction is the source's**, including a five-observation window that is five weeks there and five months here | Floor 0.2, window five, maximum likelihood, and one distribution at every horizon, all from the KIT baseline for the German COVID-19 Forecast Hub, re-read for the horizon rule. A stability alternative whose constants the agent chose could be tuned against the path taken, which is the one thing a perturbation must not permit. The transplant is recorded where it bites rather than repaired by picking a different number | agent-autonomous |
| The alternative's dispersion is re-estimated at **predict** time, so the fork moves *where* the spread is estimated as well as its form | The source re-estimates from the last five observations available at forecast time, and the sibling construction already takes its anchor from the historic frame, so a frozen dispersion beside a moving mean is a hybrid neither published construction describes. The confound is stated rather than hidden, and the fork next door isolates the window question on its own | agent-autonomous |
| **Two more fork-blind globs, and this is now the fourth instance** | `prepare_members.py` discovered pool members by globbing for `MLproject`, so the two new contracts would have made the reported model a **six-member pool containing two persistence baselines and two climatologies** — silently, at equal weights, under every combination including `main`. And `01_collect` inherited from `COMBO_BASE` per node rather than per fork, so a baseline row would have carried the sibling construction over from `main` and put two persistence rows on one leaderboard. Both now resolve the fork the way `04_score` already did. Both leave every existing result byte-identical, verified by re-running and comparing. The origin is the same each time: a step that discovers things from the tree, written when every fork had one child that did anything | agent-autonomous |
| Two contract directories rather than one with a construction switch, accepting a duplicated table build in the climatology pair | A Chap contract directory is copied whole into chap-core's run directory, so a library shared between two children does not travel with either model; and a switch would re-hash a model that produced six committed combinations' results, which is batch 11's objection to the assembler lift. The fork stays a path in the tree rather than becoming a configuration option | agent-autonomous |
| **Moving fitting into `predict` costs the record rather than the score — the third instance** | The dispersion this model forecast with was re-estimated at every split and chap-core does not surface a model's stdout, so those estimates are in no file; `fitted_model.json` holds the training-frame fit, which is the fallback and not the parameters behind the forecasts. Batch 4 found the reference has no stored fit at all and batch 21 found the same for `04_fitTime/b_refitAtPredict`. Closing it needs a place for a model to write per-split diagnostics that outlives the run directory, in the shared `chap_eval.py`, which batch 14 already touches | agent-autonomous |
| **Storage, not compute, is the number to watch before phase E** | The planner's own measurement: every combination on disk holds **660.2 MB** against its projection of 584.7 MB for the whole of tier 1 on development and 1 169.4 MB across both datasets (`manifest_notes.json["storage"]`). The development projection is already exceeded because the disk carries the fourteen phase-C combinations as well as the manifest's rows, and only one of those was budgeted — the projection is not wrong, the budget was drawn around the wrong set. Compute remains four times inside its budget. Nothing is deleted and the criticality tables say what would go first | agent-autonomous |
| `verify_model_determinism.sh` names all seven models by their **leaf** nodes | The two baselines were named by their fork nodes, which was correct only while each fork had one built child: with two, the check would have run whichever construction is on the main path, called it `persistence`, and left the other unchecked. Batch 11's rule for the candidates, applied where a second built child makes it bite. The list has now been edited three times for one reason; discovering the leaves instead needs a naming rule the check does not have, because the leaves of a fork score under the *same* leaderboard name | agent-autonomous |

### 2026-08-29 — settled by the human, on batch 22's storage question

| Decision | Basis | Agency |
|---|---|---|
| **Storage is not a constraint on this project.** A few gigabytes for the whole repository is fine, and no batch is to plan, cut or rank around disk | The human's, in response to batch 22 raising 660.2 MB on disk against a 1 169.4 MB projection for tier 1 across both datasets as the number to watch. It settles the second half of `AGENTS.md` §6's reproducibility-against-storage trade-off the way the first half was already settled: neither compute nor storage binds here, so `/annotate-criticality` keeps annotating and nothing is pruned | human-set |


### 2026-08-31 — settled by batch 14, from the completed development manifest

| Decision | Basis | Agency |
|---|---|---|
| **The choice of model family moves the reported conclusion twenty-seven times more than any choice inside a family** | Swapping the pool for candidate 1 costs 0.2209 of skill, for candidate 2 0.0884; the eleven forks inside those families move it by at most 0.0081, and their whole span in CRPS — 18.638 to 18.933 — is about half the reference's own 0.57 re-run spread. The mechanism is the pool: phase C's own sweeps record candidate 1's observation model as a 0.601 CRPS swing to candidate 1 alone and the same fork as a 0.102 swing to the pool, because three of four members did not move — and candidate 2's quantile head makes candidate 2 worse while making the pool better, so the damping is not simple scaling. Phase C spent batches 8, 9 and 10 selecting among analyses this evaluation cannot separate, and batch 21 spent a branch iterating that selection. The ratio, not the score, is what phase D has to say to the manuscript | agent-autonomous |
| **The one candidate-internal fork that is not inside a member is the second-largest move in the set** | Fitting the pool's weights on a year held back inside the training frame costs 0.1820 of skill and takes the reported model to 22.838 CRPS, behind the reference, with its paired comparison falling to 0.48 standard errors. Batch 11 measured the same fork as 4.021 CRPS and called it that batch's most useful result; read on the skill scale the whole set is read on, it is second only to replacing the pool | agent-autonomous |
| **The pairs are not the sum of their parts, and the largest interaction exceeds both main effects behind it** | The province filter is worth +0.0376 alone and case weighting +0.0835 alone; together they come to +0.0177 against an additive +0.1211, an interaction of −0.1033. Both work by re-weighting what the mean is over, so taking both does not do it twice. It is the third demonstration that fork effects do not compose — batches 9 and 21 were the first two — and the first on the reported conclusion. It is computed by `collect_conclusions.py` into `conclusions.csv` rather than in a report, because arithmetic that looks too simple to need a file is exactly where §1 fails | agent-autonomous |
| **Case weighting is the one condition under which a required baseline beats the reported model**, in every combination it appears in | Five of the 32 rows, all five case-weighted. Batch 13 reported it from one row; with five it is a property of the weighting rather than of an analysis. The reported model is over-dispersed on the quiet months that dominate the unweighted mean and under-dispersed on the outbreak months that dominate this one, and 10–90 coverage across the set runs from 0.458 to 0.920 against a nominal 0.80 while the skill score stays positive on 27 of 32 | agent-autonomous |
| **A fourth fork-blind step, and the first found by running rather than by planning** | The driver ran the family's `run.sh` after the moved child, and an alternatives parent runs every fork below it at the main path — so the one row whose fork belongs to the family that runs had both children of it under one combination. A row like that now takes the family's forks itself and runs the family's **own scripts**, read out of its `run.sh` under the `# Own scripts` marker rather than listed in the driver. All four instances have one origin: a step that discovers something from the tree, written when every fork had exactly one child that did anything | agent-autonomous |
| **A member family's fork is run only where the combination cannot already resolve it**, from `COMBO` or `COMBO_BASE` | The alternative would re-run every fork of every member family on every candidate row and record a combination as having taken choices it inherited. The consequence is that batch 22's two rows record their inherited choices under their own names and this batch's twelve record them as inherited; the configurations are identical, so no number moves, and the earlier rows are not re-run for bookkeeping | agent-autonomous |
| **The two weighting rows had been reporting the main path's paired spread**, and are re-run | `03_compare` computed its paired difference, its standard errors and its noise floor unweighted while the leaderboard beside it followed the fork, so both rows carried `main`'s −3.282 ± 1.726 against a 0.565 floor under a re-weighted mean. Under their own weighting the pool separates from the reference further than anywhere else in the project: 2.87 and 2.30 standard errors against `main`'s 1.90, with the noise floor growing alongside because the reference's own sampler is re-weighted too | agent-autonomous |
| **Tier 2's setup dimension is one fork asked twice**, and the rule is not adjusted for it | Ranking by \|Δ skill\| put both group-S slots on children of `03_provinces`, so tier 2 crosses the province filter with the model choices and says nothing about the training window, the population column or the retraining frequency. No pair joins two children of one fork — pairs are drawn from different groups — so the rule holds. It was fixed and hashed before any of this was knowable, and changing it now is what the freeze exists to prevent | agent-autonomous |
| **The per-split diagnostics gap stays open**, against batch 22's expectation of this batch | Its premise was that batch 14 touches `chap_eval.py`; the lift was of the assemblers. A model can only write per-split diagnostics from inside its own contract directory, which re-hashes the model, the pool's membership and the reported model's configuration — so closing it forces a re-run of the reported analysis and of the frozen manifest, between the manifest freezing and the holdout opening. Deferred with the reason rather than done quietly | agent-autonomous |
| **Batch 12's cost model is confirmed a second time: right on the total, wrong on every row** | Tier 1's fourteen rows came to 1 293 s against 1 224 planned and tier 2's eight to 5 703 against 6 047 — 6 % either way — with per-row ratios from 0.52 to 1.91. Batch 13 measured the same pattern. Nothing rests on it because nothing was cut, and phase D has used about 3.2 of its 12 budgeted hours on development | agent-autonomous |
| **The repository is 1.1 GB and the disk holds 10 GB**, and the whole difference is disposable | `analysis/**/work/` — chap-core's per-split run directories, a `.venv` per model per combination — is 8.8 GB, gitignored since batch 7, cleared by each node before it runs and read by nothing afterwards. The tracked repository is inside the human's "a few gigabytes", and phase E's holdout backtest is four splits rather than eight, so it stays there | agent-autonomous |

### 2026-08-31 — settled by batch 15, from the reported distribution

| Decision | Basis | Agency |
|---|---|---|
| **The scale on which "does the conclusion move" is answered is measured, not chosen: the reference model's own re-run spread in skill, 0.0218** | The reference is unseeded and was scored four times, and `03_compare` scores our model against each repeat separately — so the spread of those four is how far the reported conclusion moves when nothing about the analysis changes. Picking a threshold instead would have been a silent judgment call inside the node whose job is to make judgment calls visible. It is the skill-space twin of the 0.565 CRPS floor and comes from the same four repeats; the CRPS floor could not have been used, because the conclusion is a ratio and the weighting fork makes CRPS non-comparable across six of the 32 rows | agent-autonomous |
| **Six of the seventeen forks move the conclusion further than that band and eleven do not**, and nine of the eleven are the candidate-internal forks phase C selected among | Family 0.2209, pool weighting 0.1820, headline mean weighting 0.0835, province filter 0.0376, persistence construction 0.0279, training window 0.0219 — the last of which clears the band by one part in two hundred and is reported as the borderline case it is. This is the plan's "most valuable single output", and what it says is that a system free to spend effort spent almost all of phase C below the resolution of its own evaluation | agent-autonomous |
| **The reported analysis is the thirteenth of thirty-two, not the middle of the range**, and the failures are structured | Twelve reasonable analyses conclude a better skill score and nineteen a worse one. The five rows the reference wins are exactly the five that replace our model or refit its weights; the five a required baseline wins are exactly the five that weight the headline mean by cases. No choice about the data, the evaluation, the scoring or the baselines takes our model below the reference on any row | agent-autonomous |
| **Mean CRPS is summarised within a weighting and never across one** | 18.55–23.70 unweighted, 28.58 population-weighted, 88.48–112.26 case-weighted. A re-weighted mean is over a different set of weights and one axis would report a spread that is an artefact of the unit. Which group a row is in is read from its own fork columns, never from the size of the number. It is the first time the project's reason for reporting a ratio rather than a CRPS has been load-bearing | agent-autonomous |
| **`run_manifest.py` joins `run.sh`, and `analysis/run.sh` becomes about four hours rather than twenty minutes** | Every row can now run, so batch 12's reason for holding it out is gone, and the distribution is a reported result — `run.sh` is what reproduces reported results. The question that had to be answered first was whether re-planning moves the frozen manifest, since `run.sh` re-plans on every run: it does not, and `manifest.csv` came back byte-identical against a completed tier 1. The node's order now runs plan → tier 1 → collect → plan → tier 2 → collect, so the frozen pair rule can select from a tier 1 that exists even on a cold run | agent-on-human-assessment |
| **The phase-E set is frozen with its development pairing, row by row**, under `__holdout` names | Thirty-three rows at an estimated 2.07 h. Freezing which analyses run and assembling the development half of the comparison afterwards would leave the comparison selectable after the fact even though neither half was. The rename is not cosmetic: a holdout row writes under `analysis/results/<combination>/` and would otherwise overwrite the result it is to be compared against. `check_invariants`' `combos` check now reads both manifests, so the combination space stays closed over the larger set of names | agent-autonomous |
| **`plan_manifest.py`'s documented `--freeze-check` flag does not exist and could not work as described** | The script writes `tier2_rule.md` and its sha256 from the same in-script constant on every run, so comparing them can only succeed. What evidences the freeze is git — batch 12's commit of the rule before any tier-1 row ran — which is stronger. The check the flag describes is now enforced by `freeze_holdout_manifest.py`, against the hash in the existing notes. The docstring is left standing and the finding recorded, because correcting it means editing the script whose output is the frozen manifest | agent-autonomous |
| **The completed development manifest took 3.66 hours, not the 3.2 batch 14 reported** | Summed from `run_status.csv`, which is the file that records it, over all 32 rows including the two that failed first time. `readme-at-start.md` is corrected; batch 14's report is an output and is not edited. The conclusion the figure supported — that compute does not bind — is unchanged and slightly stronger. Over the rows the manifest costed, planned and actual agree at 7 469 s, a ratio of 1.00, with per-row ratios from 0.52 to 1.91 | agent-autonomous |

### 2026-08-31 — settled by batch 16, from the opened holdout

| Decision | Basis | Agency |
|---|---|---|
| **The holdout is reached by one switch, in `analysis/scripts/lib/combos.py`, keyed on the `__holdout` suffix the frozen manifest already names its rows with** | Three things differ on the phase-E side and nothing else does: the file the setup chain starts from, the backtest scheme, and the span the province and training-window forks call "evaluated". Six setup scripts and `conclude.py` needed all three. Putting the answer in each of them is the fork-blindness this project has now corrected six times; putting it in one place makes "the holdout row runs the same analysis" a checkable property rather than a claim. Deriving it from the combination name also means the driver sets one variable, `COMBO`, exactly as for every other row, so no second switch can be set inconsistently with it | agent-autonomous |
| **`01_data/01_partition` opens the seal, by reassembling the archive from the two parts beside it** | The alternative was to point `02_setup` at `Archive/lao-dataset/` for holdout rows. Rejected twice over: the archive is `(IS_SHADOW)` material and a setup stage reaching into it would put the read outside the tree where no node's provenance covers it; and the licence to read the whole record belongs to this node *because* this is where the proof lives that development and holdout partition the source exactly, which is what makes putting them back together legitimate rather than a second import. The assembled file is byte-identical to the archive and the check is on hashes, so no case value of 2010 is read by the script that opens it | agent-autonomous |
| **The tree gained no `06_holdout` node**, although `analysis/README.md` had reserved one | The holdout is not a second question. It is the stability question — how far the conclusion survives a differently-but-equally-reasonably conducted analysis — asked of a second year, over the identical set of analyses, against the identical yardstick, with the frozen manifest and freeze record already at `05_stability`. A node whose claim restated that node's and whose scripts were that node's under other names would make the tree larger and not clearer. The headline holdout number is where the headline development number is: at the root, written by the same `conclude.py` | agent-autonomous |
| **A holdout row that has run is not run again, enforced by the driver rather than remembered** | Plan §3's second half. Found by running the manifest without it, which began re-running `main__holdout`; the reference is unseeded, so a second pass would have replaced the denominator of every number already reported with a different draw. It got as far as the persistence baseline, those files were restored from the previous commit, and the reference was never reached. From a clean checkout there is no status file and the whole set runs, so `analysis/run.sh` still reproduces phase E from nothing | agent-autonomous |
| **The thirty-third frozen row is not run, because its development twin was not** | `family_ensemble__holdout` is the main path under a second name and development did not run it either. The rule is read off the frozen manifest's own column — a holdout row with no development conclusion has nothing to be reported beside — rather than off the row's kind, and the absence is in `run_status_holdout.csv` with its reason. The freeze's own cost estimate excluded it, which is what says the intent was already this | agent-autonomous |
| **Each dataset's forks are judged against that dataset's own noise band** | 0.0218 on development, 0.0140 on the holdout, each the spread of our skill score against the four repeats of the unseeded reference on that year. Importing one band into the other would let one analysis decide what counts as a move in another, which is the judgment call this whole node exists to avoid making silently | agent-autonomous |
| **The gap is reported plainly and is not explained away: +0.1485 to +0.0868, and a spread that more than doubles** | The plan asks for exactly this. What the numbers say is that the model still beats the reference and both baselines on a year it had never seen, that 2010 was about four times harder for every model in the comparison, and that the *distribution* is where the damage is: −0.5038 to +0.2026 against −0.0724 to +0.2320, with 28 of 32 analyses worse and the rank correlation between the two only +0.396 | agent-autonomous |
| **The largest effect on the holdout is a fork that moves the reference model, not ours** | Under `provinces_reportingOnly` our pool goes 76.73 → 76.56, inside the noise, while the reference goes 84.03 → 64.72. That row ranks fourth of thirty-two on development (+0.1861), highest of every analysis that does not re-weight the headline mean, and twenty-ninth on the holdout (−0.1828), with its case-weighted pair worst of all at −0.5038. Reading it as our model being sensitive to the province filter would be wrong, and the per-model CRPS in each row's own `conclusion.json` is what says so | agent-autonomous |
| **`freeze_holdout_manifest.py`'s `frozen_at_commit` is read from git rather than recomputed** | It recorded HEAD at write time, so every later run overwrote the evidence the field exists to carry; running the script once after the holdout turned batch 15's `f3904c5` into batch 16's own commit. It now reads the commit that *adds* `manifest_holdout.csv` — 937fd5c — which cannot be overwritten by running the script again. Safe to change because `manifest_holdout.csv` itself comes back byte-identical after the whole set has run, checked before the change and after | agent-autonomous |
| **The two ranked figures moved into `scripts/lib/`, with one-screen runners as the steps** | `/validate invariants` requires a plotting script named for each figure, and one script writing two figures under a `--dataset` flag has no such name. The fix is the shape this project already uses for `chap eval`: the drawing in a library, the steps as runners. The alternative was to weaken the check, which is forbidden. The development figures' titles now count their own bars instead of stating "Six of seventeen", which is the transcription §1 is about and had been sitting in a title since batch 15 | agent-autonomous |

### 2026-08-31 — settled by batch 17, from the collection and the report

| Decision | Basis | Agency |
|---|---|---|
| **A claim states the figures a file holds, never a ratio between two of them that no file computes** — *superseded the same day by the human; see the entry below* | `readme-at-start.md` says the pool sits 1.90 standard errors from the reference. The paired difference and its standard error are both stored; the ratio is not, so asserting it in a claim would write a number computed in the agent's context into the record — the failure `AGENTS.md` §1 describes, and one that looks like nothing on the page. C23 gives both stored figures instead. The same rule shaped C29 and C31. The alternative, a script at `04_score/03_compare` that divides and stores, is a change to the analysis and phase E forbids re-running anything, so it is the human's to allow | agent-autonomous |
| **The report's within-result levels are built for every scored combination, not only for the main path** | The project's finding is that the reported analysis is one member of a distribution. A report that let a reader descend only that member would contradict it in its own structure. 65 combinations, 1 105 pages below the tree, against about a tenth of that for `main` and `main__holdout` alone | agent-autonomous |
| **The report displays stored numbers and computes none** | Every level reads the file the analysis wrote — `metrics_summary.csv`, `crps_by_location.csv`, `metrics_cell.csv`, `conclusion.json`. A report that re-derived its own means could disagree with the analysis about a number and look right doing it. The cost is that it can show only what was stored: there is no per-split, per-province breakdown below the province page, because the aggregation node writes none. That is the diagnostics gap batches 22, 14, 15 and 16 left open, seen from the display end | agent-autonomous |
| **What the report lists is decided by git, not by a skip list** | The first build showed `c_ensemble`'s scripts as 6 117 files, of which 11 are the node's; the rest is the virtual environment `uv` builds inside the model's contract directory. The builder now asks `git ls-files --others --ignored --exclude-standard --directory` and shows nothing the repository declines to version, so what is not part of the method cannot appear in the report, and the two cannot drift apart | agent-autonomous |
| **`.gitignore` ignores the report's contents rather than its directory** | So that `AI-generated/hierarchical-report/provenance.md` can be tracked while the 18 MB of generated HTML is not. A record of a build that is itself untracked records nothing. The folder's `README.md` stays generated, because a hand-kept description of a generated folder goes stale silently | agent-autonomous |
| **A province with no evaluable cell sorts last and prints as an em dash** | `crps_by_location.csv` carries an empty mean for Xaisomboun rather than a zero, which is correct — it contributes nothing to the metric and a zero would be a score. The first build crashed sorting on it. Reading the blank as zero would have put a perfect-looking province at the top of every table | agent-autonomous |

### 2026-08-31 — settled by the human, on batch 17's question

| Decision | Basis | Agency |
|---|---|---|
| **A claim may state what follows trivially from the figures it cites — a ratio, a ranking, a difference — and may not state anything that needed a step nobody ran** | Batch 17 had drawn the line at "no file computes it, so no claim states it", which would have kept the paired margin as 3.282 CRPS against a standard error of 1.726 and never as the 1.90 standard errors that quotient makes it. The human's line is where the arithmetic stops being legible from the claim itself: a reader can check a quotient of two cited figures at a glance, and cannot check a number that stands for a computation nobody ran. Only the second is the transcription §1 forbids. C23 now states all three figures and is `agent-on-human-assessment`; the rule is in `Human-AI-collaboration/claims/README.md`, where a future session writing claims will meet it, and in `readme-at-start.md` | human-set |

### 2026-08-31 — settled by the human, on batch 16's two open questions

| Decision | Basis | Agency |
|---|---|---|
| **The agent writes the judgment about where this setup was more trouble than it was worth, and the human comments and edits afterwards** | Phase E requires the case write-up to say it, and the manuscript's Appendix asks for it by name. Batch 16 asked whether the judgment should be the human's; it is the agent's, offered back for comment. **What that makes it is `agent-autonomous`, and batch 19 must label it so** — the delegation is the human's decision and the verdict is not, and this project reports its own agency as a result, so recording the verdict as jointly held because the human read it afterwards would overstate their part. If an edit changes what a sentence says rather than how it says it, that sentence becomes `agent-on-human-assessment` and the change is logged here | human-set |
| **`analysis/run.sh` is not split; the stability and phase-E runs stay inside it** | The agent's recommendation, taken. Both distributions are reported results and `run.sh` is what reproduces reported results, so a `run.sh` that reproduced the headline number but not the spread around it would reproduce the weaker half of what this project claims. The cost is accepted with the decision: the whole run is about six hours, most of it the unseeded reference model's four repeats through an emulated amd64 image on each of two datasets, and `/validate cleanroom` in batch 18 is therefore a six-hour check rather than a twenty-minute one | agent-on-human-assessment |

### 2026-08-31 — settled by the human, closing phase E's open decisions

| Decision | Basis | Agency |
|---|---|---|
| **Batch 20 runs; the optional external check is not cut** | The same model, unchanged, on `tha` and `vnm`. It is the only thing in this plan that bears on batch 16's largest open question — whether the holdout spread is about 2010 or about one-year backtests — which this project cannot answer from inside itself, having one held-out year and four splits. Compute was never the constraint | human-set |
| **Batch 20 runs before batch 19, so the order is 18, 20, 19** | Batch 19 writes the case study and does the release. An external check that lands after the write-up is a result the write-up cannot use, and after the release is a result nobody reads. The ledger's numbering is an identifier and not a position, which batch 22 already established | agent-autonomous |
| **A git remote is created after all, at `github.com/sandvelab/`** | This reverses §10's standing position that no remote is to be created and that `/release` stops. The owner is the human's; the repository name was delegated, and is **`veridical-agentic-dengue-laos`** — the method and the case, without the local folder's misspelling. It is created and pushed as the last step of batch 19's `/release`, after the secrets and data-permission scan, `/validate cleanroom`, `/validate outsider` and both generated reports, because a release that pushes before its own scan has not run its scan. The agent asks before the push itself | human-set |
| **The manuscript's target venue is *PLoS Computational Biology*** | The obvious precedent: the manuscript this case serves updates Sandve et al., *PLoS Comput Biol* 9(10): e1003285 (2013). It had been recorded as not fixed in the source material | human-set |
| **What `/validate outsider` finds in the instruction files is fixed by the agent and logged, not brought back for approval first** | The findings are what an outsider misunderstands, and fixing them is a methodological change under Rule 4 — so each one is committed in those terms, with what it changed and why. The human reads the log rather than the proposal | human-set |

### 2026-08-31 — settled by batch 18, from the clean-room and outsider checks

| Decision | Basis | Agency |
|---|---|---|
| **The holdout seal takes two conditions and needs both** | The seal rested on `run_status_holdout.csv`, which is versioned — so it sealed every clone of the repository, not just the copy that opened the year. In a fresh clone all thirty-two rows were skipped and the phase-E half of `analysis/run.sh` reproduced its outputs byte-identically while running none of the analysis behind them. The versioned file stays as the evidence, so deleting a row to force a re-run still shows in git; a gitignored `.holdout_opened` at the node root says whether *this working tree* opened the year. §3's rule is unchanged and only where the flag lives has moved | agent-autonomous |
| **The wrong counts are corrected in the live records and left standing in the batch reports and in this section** | Three of them: "eleven forks" for eight forks and their eleven combinations, "nine of the eleven" below the noise band for eight, and a per-row cost ratio rounded up from 0.514 to 0.52. The claim collection is what batch 19 writes the manuscript from and had to be right. The batch reports and §4b are accounts of what was established at the time, and correcting them in place would hide that the project carried a wrong noun through four batches — which is itself a result about this method | agent-autonomous |
| **`check_invariants.py` requires ancestry, and reads every hash on a `commit:` line** | Six records named a commit that is not an ancestor of HEAD, orphaned by a history rewrite in batch 14. `git cat-file -e` passed it because the object is still in the store, and a *local* clone hardlinks the object directory so every clone passed too — it would have vanished on batch 19's push. The anchored pattern separately skipped `conclude.md` entirely, for annotating its two hashes, so the headline result's record was the one the check never read | agent-autonomous |
| **The root `README.md` stops restating project state** | It described batch 1 through the whole of phases B, C and D, and its build command never worked. The durable fix is not a fresher copy of the state but no copy: `readme-at-start.md` answers that question, and a second document answering it goes stale silently, which is exactly what happened | agent-autonomous |
| **The provenance hash gap and the recomputed freeze become batches 23 and 24 rather than edits here** | Both are real and neither is reachable today: the tree cannot grow while phase E is closed, and the sixteen stale hashes need appended sections describing runs this batch did not do. Plan §5 says a batch running long splits the remainder rather than pushing on. The alternative — adding the hash invariant now — leaves a failing check, which is worse than a scheduled one | agent-autonomous |
| **The outsider check is two agents on two tasks, not one** | One writing into the tree and one tracing the headline result back to the archived data. They failed in disjoint places: the first found the machinery defects, the second found the wrong numbers and the broken commit link. A single agent would have produced one of those two lists | agent-autonomous |

## 5. How this plan is executed

**One batch per invocation.** `/do 26-08-22_dengueForecastingCase` runs the **next open batch**
in the ledger below and then stops and reports. Batch *N* is iteration *N* for the purposes
of `/do`: the batch's report is written to `AI-generated/batch-reports/` as
`YY-MM-DD_bNN_camelCaseName.md`, linked under `## Batch ledger` here, and the previous
report is never overwritten.

**A batch is sized to finish inside one session with room to spare.** If a batch is running
long, stop, write the report with what was established, and **split the remainder into new
batches** rather than pushing on and losing the record when the context ends. A batch that
ran out of context without a report is the one genuinely unrecoverable failure mode here.

**Every batch ends in exactly one of three states**, recorded in the ledger:

- **Done — produced** — it created or changed something in the analysis. The report says what,
  and where.
- **Done — expanded** — it produced no analysis output but replaced itself with more concrete
  batches. This is a legitimate and expected outcome, especially early. The report says what
  was learned that made the new batches possible.
- **Blocked** — it could not proceed. The report says exactly what is missing and what would
  unblock it. Then stop; do not silently take the next batch instead.

**Batches added by a batch are appended to the ledger** with a one-line aim each, in the phase
they belong to. The ledger is the live plan; this document is edited as the project runs, and
that is intended. **The ledger is executed top to bottom and a batch's number is an
identifier, not a position** — batch 21 runs on a branch and batch 22 was added between 13 and
14, so neither sits where its number would put it.

**At the end of every batch, without being asked**: `/track-result` for anything produced,
`/commit-run after`, `/validate invariants`. If invariants fail, fix the cause before the
batch is marked done. Never weaken a check to make it pass.

**The early batches genuinely do not know what the later ones are.** Batches 1–5 are
reconnaissance and bootstrapping; batch 5's entire job is to replace the sketched phases C–E
with concrete batches now that the ground is known. Phases C, D and E below are therefore
written as *aims and constraints*, not as steps — they say what has to be true when the phase
is finished, and batch 5 decides how.

---

## 6. Batch ledger

Status values: `open` · `done — produced` · `done — expanded` · `blocked`. Update this table
at the end of every batch, and append newly created batches to it.

| # | Phase | Aim | Status | Report |
|---|---|---|---|---|
| 1 | A | Orient: read the source material, fix project settings, set up the repository | done — produced | [[26-08-23_b01_orientAndSetUp]] |
| 2 | A | Reconnaissance — Chap: install it, learn the model contract, learn the evaluation | done — produced | [[26-08-23_b02_chapSetup]] |
| 3 | A | Reconnaissance — data: acquire, characterise, and fix the split scheme | done — produced | [[26-08-23_b03_dataCharacterisation]] |
| 4 | A | Reconnaissance — methods: candidate model families, and run `chapkit_ewars_model` to get the reference score | done — produced | [[26-08-23_b04_methodSurvey]] |
| 5 | A | Bootstrap: turn phases C–E into concrete batches | done — expanded | [[26-08-26_b05_bootstrapPlan]] |
| 6 | B | Vertical slice: one trivial model, end to end, first CRPS number | done — produced | [[26-08-26_b06_verticalSlice]] |
| 7 | B | Erect the claim tree, route the vertical slice through it, add the reference | done — produced | [[26-08-26_b07_erectTheTree]] |
| 8 | C | The candidate contract, and candidate 1 (hierarchical NB GLM) at its defaults | done — produced | [[26-08-27_b08_candidateContract]] |
| 9 | C | Candidate 1's internal forks, plus a proposed fifth on an autoregressive term, and the width defect batch 8 diagnosed; promote the main path | done — produced | [[26-08-27_b09_candidateForks]] |
| 10 | C | Candidate 2: gradient-boosted trees with a probabilistic head | done — produced | [[26-08-28_b10_boostedCandidate]] |
| 11 | C | Candidate 3: the ensemble; close phase C | done — produced | [[26-08-28_b11_ensembleCandidate]] |
| 12 | D | `/perturb plan`: the stability node, the driver, the frozen development manifest | done — produced | [[26-08-29_b12_perturbationManifest]] |
| 13 | D | `/perturb run`: build the seven setup and scoring children, archive the population series `b_backCast` needs, and run those rows | done — produced | [[26-08-29_b13_setupAndScoringRows]] |
| 22 | D | `/perturb run`: build and run the two baseline forks' children, which move the pool as well as their own leaderboard row | done — produced | [[26-08-29_b22_baselineForkRows]] |
| 14 | D | `/perturb run`: fix the two defects blocking the candidate rows **and the third, that `03_compare` computes its paired spread unweighted while the leaderboard mean follows the weighting fork**, lift the shared assembler, re-run the twelve candidate rows and the two family rows, then tier 2 | done — produced | [[26-08-30_b14_candidateAndFamilyRows]] |
| 15 | D | `/perturb report`; put the driver into `run.sh`; freeze and commit the holdout manifest | done — produced | [[26-08-31_b15_perturbationReport]] |
| 16 | E | The holdout, opened once, on the frozen manifest | done — produced | [[26-08-31_b16_holdout]] |
| 17 | E | Claims and the hierarchical report | done — produced | [[26-08-31_b17_claimsAndReport]] |
| 18 | E | Clean-room and outsider validation; the plan's own drift | open | |
| 19 | E | The case write-up, the reproducibility report, the release | open | |
| 20 | E | The external check on `tha` and `vnm` — **confirmed, not cut; runs before batch 19** | open | |
| 21 | C, on branch `greedy` | The counterfactual: iterate batch 9's promotion rule to a fixpoint on a branch, and measure what stopping once cost | done — produced | `26-08-27_b21_greedyBranch.md`, on branch `greedy` |
| 23 | E | The provenance records' script hashes: the invariant that a script's current sha256 must appear in its own record, and the sixteen appended sections that make it pass — including `conclude.py`, whose newest section predates batch 16 changing it | open | |
| 24 | E | The frozen phase-E manifest is recomputed on every run of `analysis/run.sh`, so a tree that grew a fork child would silently grow the frozen set; make the freeze win over the recomputation | open | |

---

## 7. Phase A — orientation and bootstrap

### Batch 1 — orient and set up

Read all five source documents. Then:

- Fill in `readme-at-start.md` from §4 above: seed, main environment, tracking level `full`,
  compute budget (§9), data governance. Leave the split point marked as *fixed in batch 3*.
  Replace the bracketed template text; do not leave a template describing a real project.
- Initialise git if it is not already, with the standard `.gitignore`. No remote (§4).
- Create `.venv` and record the Python version.
- Create `AI-generated/batch-reports/` with its README.
- Write the batch-1 report: what the project is, in your own words, and anything in the
  source material that looks inconsistent or that you did not understand. **That list is
  valuable** — it is the first evidence about whether the instructions work for someone
  arriving cold, which is a question the manuscript asks directly.

No analysis, no data, no Chap. Just a repository that knows what it is.

### Batch 2 — reconnaissance: Chap

The largest unknown, and the one everything else waits on. From [[chapOrientation]] §2 and §5
and the live documentation:

- Install `chap-core` locally, from a pinned version. Record exactly what was needed —
  including whatever went wrong, which is the part a reader will want.
- Establish the **model contract**: what a Chap-compatible model must implement, in what
  language, how it declares covariates and configuration, and how it is pointed at by
  `chap eval`. Read `minimalist_example_r` and at least one model from
  `github.com/chap-models` as worked examples of the contract rather than relying on the
  prose description alone.
- Establish whether `chap eval` accepts a **local model directory** or only a URL. This
  determines whether development can happen locally at all, so settle it early.
- Establish the **exact form of the reported CRPS**: over what it is computed, how it is
  aggregated, and whether per-region and per-split values are recoverable from the `.nc` or
  only the aggregate from `export-metrics`. §2 of this plan is not operational until this is
  answered. If per-region and per-split values are *not* recoverable, say so and propose how
  to obtain them; do not substitute a hand-computed CRPS without flagging it loudly, since a
  metric you computed yourself is exactly the metric you could be gaming.
- Run the documented example end to end, on whatever data the documentation uses, to confirm
  the install works before pointing it at the real dataset.

Output: `chapSetup.md` under `AI-generated/batch-reports/` — the install recipe, the contract,
the evaluation semantics, and a list of what is still unknown. Environment changes go through
`/pin-environment`.

### Batch 3 — reconnaissance: the data

- Download the three Lao files at a pinned commit into `Archive/`, unmodified, `(IS_SHADOW)`,
  with `provenance.md` recording the repository, the commit and the date.
- **Cut the data in two, first, before anything else looks at it.** A script reads the
  pinned original and writes two files: the **development dataset**, 1998-01 to 2009-12, and
  the **holdout**, 2010-01 to 2010-12. The script is a node in the tree like anything else,
  and it is the only thing in the project that reads the full file. Verify that the two
  partition the original exactly — every row in one or the other, none in both, none lost.
  Then confirm the holdout is complete and well-formed (row count, provinces present, no
  missing months) and **stop looking at it**: its case values are sealed until phase E (§3).
- Characterise **the development dataset only**, with a script whose output is stored: rows,
  provinces, time span, completeness per province and per year, the distribution of
  `disease_cases` (expect many zeros in the early years), seasonality, and how the climate
  covariates behave.
- **Resolve the row-count discrepancy** flagged in [[chapOrientation]] §4: the schema says
  2575 rows, the CSV has 2808. Establish which is right from the data itself and record the
  answer.
- Get the data into whatever form `chap eval` expects, and confirm the conversion is lossless
  against the original.
- **Fix the backtest scheme** used on the development dataset throughout: `n-periods` (the
  horizon), `n-splits`, and `stride`. Justify each against the data — twelve years of monthly
  data at admin-1 constrains how many splits are meaningful — and write the scheme into
  `readme-at-start.md`. It does not move after this batch, because a horizon changed midway
  makes every earlier number incomparable.
- **Establish how the final validation will be run**, now rather than in phase E, since it
  may constrain the backtest scheme. The preferred route is Chap's own: `chap eval` on the
  *full* dataset with `n-splits` and `stride` chosen so that every evaluated period falls
  inside 2010 and no training window extends past 2009-12 for the first of them — the same
  command, the same CRPS, the same data isolation as development. Establish in batch 2
  whether that is configurable. If it is not, the fallback is Chap's predict path plus a
  CRPS computed by script, and that script must first be **validated by reproducing a
  Chap-reported CRPS on a development split to within tolerance** — a metric you compute
  yourself is exactly the metric you could be gaming, and the only defence is showing it
  agrees with the platform's where both can be had. Record which route will be used.
- Note every data problem you find. Missing months, implausible zeros, provinces with almost
  no cases, the static population figure. Each is a candidate alternatives node in phase D,
  and this is where the list is built.

Output: `dataCharacterisation.md` plus the stored characterisation results and plots (with
their data, per Rule 7).

### Batch 4 — reconnaissance: methods

- Read [[trustAgenticSupplementary]] §S2 first: it names the families worth considering —
  Bayesian hierarchical spatio-temporal models (INLA and similar), gradient-boosted trees on
  engineered climate-lag features, spatio-temporal GNNs over administrative units,
  probabilistic superensembles combining a mechanistic climate-driven prior with a data-driven
  residual learner, and fine-tuned time-series foundation models. It also names the
  knowledge-informed option: temperature-suitability curves for vector transmission as an
  informative prior or a mechanistic backbone whose residuals are learned.
- Then survey what exists: models in `github.com/chap-models`, and the published
  spatio-temporal dengue-forecasting literature. **Getting
  `https://github.com/chap-models/chapkit_ewars_model` to run on the development dataset is
  this batch's most important single task** — §2 makes it the model to beat, so the project
  has no criterion until its score exists. If it will not run, establish precisely what
  blocks it and report that; §2 says what happens then. Note also what other integrated models
  could be run, and whether any has already been run on Lao data.
- Assess each family against the actual constraints: 13 years, monthly, ~18 provinces,
  ~2,800 rows, three climate covariates, zero-heavy counts, and a *probabilistic* forecast
  requirement. Several of the families above will not survive contact with a dataset this
  small, and saying which and why is a genuine finding.
- Produce a **ranked shortlist**: what to try, in what order, with the reason and a rough
  cost for each, and what was ruled out and why.

Output: `methodSurvey.md`. Sources are cited; nothing about "the literature" is asserted from
memory (`AGENTS.md` §7).

### Batch 5 — bootstrap

The batch that makes the rest of the plan concrete. With the install working, the data
characterised, the metric understood and the shortlist ranked:

- Write the **claim tree design**: the root question, the sub-analysis decomposition, and the
  alternatives forks — which judgment calls become forks, which children each fork gets, and
  which is the initial main path. Check it against the three properties the manuscript
  requires of a tree that a stability run can walk ([[reproAgenticAiManuscript]], Appendix,
  *What a PCS stability analysis requires of the tree*): a shared output contract per fork, a
  script-computed conclusion at the root, and a pre-enumerated perturbation set with a budget.
  A fork whose children produce differently-shaped output has been placed too low — move it up.
  **The root's computed conclusion is fixed** (§4b): a skill score against the reference,
  `1 − CRPS_ours / CRPS_ewars`, computed per analysis by a script from the stored evaluation
  outputs, with raw mean CRPS and interval coverage reported beside it. Design the fork output
  contract so that this is computable at the root for every combination the manifest names.
- Write **concrete batches for phases C, D and E** into the ledger, each with an aim, an
  expected output, and a rough cost. Aim for batches that finish comfortably within a session.
- Revise anything in phases C–E below that reconnaissance showed to be wrong, and say what
  changed and why.

Output: `bootstrapPlan.md`, plus the ledger rewritten. This batch is `done — expanded` by
construction: it produces no analysis.

---

## 8. Phases B–E — what has to be true

Phase B is concrete. C, D and E state what the phase must achieve; batch 5 turns them into
batches.

### Phase B — make it run at all

**Batch 6 — vertical slice.** One trivial model (persistence is the natural choice, and it is
a required baseline anyway) implemented against the Chap contract, run through `chap eval` on
the development dataset, producing a real mean CRPS with its per-region and per-split values. Nothing clever. The point is that every link in the chain —
data → model → evaluation → metric → stored file — has been exercised once.

Until this exists, nothing about the modelling is real, and any effort spent on model design
before it is effort spent on assumptions.

The model writes the contract files batch 5's design specifies — the combination-scoped
`results/$COMBO/` layout and the per-stage schemas — even though only one child of each fork
exists yet. A contract first exercised when it has to carry alternatives is a contract first
tested in phase D.

**Batch 7 — erect the tree.** Build the claim tree from batch 5's design with `/node`, and
route the vertical slice through it so that `analysis/run.sh` reproduces the batch-6 result
end to end. Add the second baseline (seasonal climatology). Run `/validate invariants` and
`/validate cleanroom`: the clean-room check is worth its cost *now*, while the tree is small
and a failure is diagnosable.

Build `02_setup` and `04_score` with one child per fork, and add the reference node
`03_models/02_reference` running `chapkit_ewars_model` inside the tree. That gives the
**paired per-cell comparison** its first real test: batch 4 established what the *unpaired*
split-level spread is and argued the paired one is far tighter, and until two models have been
scored on the same 371 cells nobody knows whether the comparison can separate anything. It is
the cheapest thing in the project to check and the most expensive to discover late — if the
answer is that it cannot, phase C's design changes rather than phase D finding out.

Batch 7 also settles two things left open since batch 2: whether the Docker layer of
`environment/` builds, and the wording of `AGENTS.md` §8 on node naming, where alternatives
children are lettered and sub-analyses children numbered. Both are commits that say what they
change about the method.

From here on, everything happens inside the tree. A result produced outside it does not exist.

### Phase C — model development

**Batches 8–11** in the ledger. The claim tree they build into, and the fork inventory they
populate, are designed in [[26-08-26_b05_bootstrapPlan]].

**What must be true when the phase ends.** Several candidates from batch 4's shortlist have
been implemented against the Chap contract, evaluated on the **development dataset only**, and
recorded — each as a node, each with its provenance, each with its intermediates and its
plots-with-data. One candidate is the main path. The holdout year has not been opened.

**Constraints.**

- Every candidate is evaluated through the same `chap eval` path as the baselines. No
  candidate is compared on a metric computed a different way.
- A leaderboard file is maintained by a script from the stored evaluation outputs — never
  typed. It carries the candidate, its configuration, its development mean CRPS, its
  calibration, and its compute cost. `chapkit_ewars_model` and both baselines sit on it as
  fixed reference rows from the moment they can be run.
- Candidates that failed stay in the record, with what went wrong. A family abandoned because
  it could not be made to produce calibrated probabilistic output is a finding.
- Each round decides what to do next from what the last round showed, and says so. A round
  that reports only a number and no reasoning has hidden the interesting part.
- Watch for the specific failure the proposal names ([[trustAgenticProposal]], *Why this
  research is needed*): fitting the available data rather than the data-generating process,
  and brittleness to the chosen metric. Selecting hard on development CRPS across many
  candidates is precisely how that happens, which is what the held-out year exists to catch.
  Every rejected sibling stays in the tree and is re-run in phase D and on the holdout, so the
  cost of each selection is measured rather than argued about.
- **The phase ends on evidence, not on a batch count.** It stops when the leaderboard's best
  moves by less than **0.4 CRPS** in a batch — the reference's own re-run spread, and therefore
  the smallest movement that means anything. Adding a further candidate batch requires that
  the last one moved it by more.

### Phase D — stability and the veridical record

**Batches 12–15** in the ledger.

**What must be true when the phase ends.** The judgment calls are enumerated and costed
(`/perturb plan`); the ones within budget have been run (`/perturb run`); and the result is a
**distribution of conclusions over reasonable analyses**, not a single number
(`/perturb report`). What was not run is recorded as a decision, with the reason, not left as
an absence.

**The forks**, confirmed against what batches 3 and 4 found and placed in the tree by batch 5.
Ten were listed here; **the tree carries seventeen**, and batch 12 replaced the list with a
script that reads them off the tree (`analysis/05_stability/results/forks.csv`). Five were
added by phase C while building the candidates, and two — the baseline forks, one of which
this section names below — were never on the hand-written list. The four groups:

*Under `02_setup`, and so re-scoring every model including the reference* — what the
`population` column contains, given that it is a single 2020 snapshot applied to thirteen
years; how much of the record models may learn from, given that the zero rate falls
monotonically across it; which provinces belong in the analysis at all; and how often a model
is refitted across the backtest.

*Under `04_score`, re-scoring every model without re-running any* — the weighting of the
headline mean, over provinces whose burdens differ by four orders of magnitude.

*Under `03_models/03_candidate`, and so moving only ours* — the model family itself, with the
top candidates as siblings under one fork; the observation model for the counts; the covariate
set and the lag structure; how population enters our model; and whether our model does its
fitting in `train` or, as the reference does, in `predict`.

*Under `03_models/01_baselines`, and so moving one leaderboard row **and our reported
model*** — how uncertainty is wrapped around a point baseline, and which window estimates
the seasonal distribution. Batch 6 found two published constructions for the first that
disagree, and the choice sets the calibration of one of the two numbers §2's criterion is
defined against, so it is a fork rather than an implementation detail. **Batch 11 changed
what these forks reach**: the reported model is a pool that takes both required baselines as
members, so a fork on how persistence wraps its uncertainty is now a choice inside the model
this project reports as well as a choice about a baseline.

**The forecast horizon is not among them.** It is forced by the reference model, so a
combination at another horizon has no reference to be compared against and the root's
conclusion — a ratio to the reference — is uncomputable there. It is the one item of this list
that reconnaissance removed rather than refined.

**Also required**: a stated answer to whether the headline conclusion moves when a reasonable
alternative is taken at each fork, and which forks it is most sensitive to. That answer is the
most valuable single output of this project for the manuscript, and it is worth more than a
better CRPS.

**And the deliverable phase E depends on**: a **frozen perturbation manifest** — the exact set
of analyses to be re-run on the held-out year, committed before the holdout is opened (§3).
It names each fork, the children to be taken, the resulting combinations, and the estimated
cost of running the set twice: once on development, once on holdout. If the budget will not
carry the whole set to the holdout, cut the manifest here and record the cut; do not discover
the problem in phase E with the holdout already open.

**What reporting the distribution found.** The conclusion survives, and the reported number
is not the middle of what it survives across: skill runs **−0.0724 to +0.2320** around
+0.1485, which sits **thirteenth of thirty-two**. The plan's "stated answer to whether the
headline conclusion moves at each fork" is `analysis/05_stability/results/sensitivity_by_fork.csv`
and it is this: **six of the seventeen forks move the conclusion further than the reference
model moves on its own, and eleven do not** — the yardstick being the 0.0218 spread of our
model's skill score against the reference's four unseeded repeats, measured rather than
chosen. Above the band: the model family, the pool's weighting, the weighting of the headline
mean, the province filter, the persistence construction, and the training window by one part
in two hundred. Below it: **nine of the eleven candidate-internal forks phase C spent three
batches selecting among**. That ratio, and not the spread, is what phase D has to say. Batch
15's report has all of it, and the phase-E set is frozen in
`analysis/05_stability/results/manifest_holdout.csv`.

**What running the candidate and family rows found, and what tier 2 found.** The
development manifest is complete: **32 of its 33 rows have a conclusion**, the 33rd being the
main path's own choice under its own name. The reported skill spans **−0.0724 to +0.2320**
around +0.1485, our model beats the reference on 27 of the 32 and both required baselines on
27, and 10–90 coverage runs from 0.458 to 0.920 against a nominal 0.80. **The choice of model
family moves the conclusion twenty-seven times further than any choice inside a family**: the
eleven forks phase C spent three batches selecting among span 18.638 to 18.933 CRPS, about
half the reference's own re-run noise, while swapping the pool for candidate 1 costs 0.2209
of skill. The exception is the pool's own weighting fork, worth 0.1820 and the second-largest
move in the set. **Tier 2 shows the forks do not compose**: the largest interaction, −0.1033,
is bigger than either main effect behind it — the province filter and case weighting each
improve the reported skill alone and almost exactly cancel together — so a one-at-a-time
stability report would have been wrong about that pair by two thirds of the whole main-path
score. Batch 14's report has all of it.

**What running the two baseline rows found.** They are the extremes of the set. Freezing the
climatology's estimation window moves the reported conclusion by 0.0025 of skill, the smallest
move of any row; wrapping the persistence point in a fitted negative binomial rather than in
the empirical distribution of past changes moves it by −0.0279, the largest, and downward.
That construction — the one this section's fork exists to compare, and the one batch 6
rejected — scores 4.181 CRPS better than the main path's and **beats the reference model**.
So the reported analysis stands on the worse of two published constructions of a baseline §4
requires, and it is not promoted, because phase C is closed and the manifest was frozen before
the row ran. **The pool that contains it is better off for that**: with the sharper member its
margin over its own best member falls from 1.954 to 1.264 CRPS, which with batch 11's
weight-fitting result is the second independent demonstration that this pool's win comes from
its members disagreeing rather than from their quality. Batch 22's report has all of it.

**What running the first seven rows found.** The five `02_setup` forks move the conclusion
less than the reference model's own re-run noise, and the single `04_score` fork moves it four
times as much as any of them — from re-weighting a stored file and re-running no model. Three
of the five setup rows move the score by moving *the reference* rather than our model, which a
headline reporting only our own score would hide entirely. Under case weighting the required
persistence baseline beats the model this project reports, and our pool's interval coverage
inverts from over-dispersed to under-dispersed. The batch also measured an intermittent crash
in the reference — about one job in a hundred — which is a finding about the platform's model
library rather than about any row. Batch 13's report has all of it.

**What planning the manifest found, before running any of it.** Nine of the twenty-four
tier-1 rows were sentences in a `claim.md` rather than paths in the tree, and are now nodes;
after batch 22 the planner reports **none** unbuilt.
Twelve of the fifteen that had scripts hold results produced around a main path that has since
moved, so their directories describe a different analysis from the one their row now names.
Two code defects — the pool's member assembler and the root's resolution of which model is
ours — would have made every family row and every candidate row report the wrong thing. None
of that is visible from a fork list, and all of it is cheaper to find here than in batch 14.

**Which forks apply to the reference and the baselines.** `chapkit_ewars_model` is an external
reference at its own default configuration and is not perturbed as a model. But forks that
change the *data* or the *evaluation* — the split scheme, the handling of the zero-heavy
period, how population enters the dataset — change what every model is scored on, so every
model on the leaderboard is re-scored under those. Forks internal to our own candidates move
only our candidates. Record which fork is which kind when the manifest is written; a
comparison where one side moved and the other did not is not a comparison.

If the budget forces a cut, cut here — but cut *explicitly*, recording where the line fell and
what was below it. See [[reproAgenticAiManuscript]], *Trade-offs*.

### Phase E — closing

**Batches 16–19 in the ledger, with 20 optional.**

**What must be true when the phase ends.**

- **The final validation has happened, once**: the holdout year opened in a single batch, and
  the frozen phase-D manifest run on it — the final candidate, both baselines and
  `chapkit_ewars_model`, across every combination the manifest names — by the route batch 3
  established, producing the numbers that are reported. Report them beside the development
  numbers for the same models and the same combinations, so that development spread and
  holdout spread are read together. **If the holdout numbers are much worse than the
  development numbers, that gap is the most interesting result the project has** — it is the
  direct measurement of how much an autonomously optimising agent inflated its own
  performance, and it is precisely what the manuscript and the proposal are asking about.
  Report it plainly and do not explain it away. **Nothing is re-run or re-tuned after a
  holdout number has been seen** (§3). The reference is re-scored four times on the holdout as
  it is on development: it is unseeded, the conclusion divides by it, and an unaveraged
  denominator would put the reference's own re-run noise on every number reported.
- **`analysis/run.sh` reproduces the reported result from a clean environment** — verified by
  `/validate cleanroom`, not asserted.
- **Every claim is in `Human-AI-collaboration/claims/claims.md`**, each bound to a stored
  result: the headline claim about forecast performance, the stability claim about how far it
  survives the alternatives, the negative claims about what did not work, and the supporting
  claims under each.
- **`/validate outsider` has been run** on a fresh agent with no context, and what it
  misunderstood has been recorded and fixed. Run it late enough that there is something real
  to reproduce, and early enough that fixing the instructions is still cheap.
- **The hierarchical report** (`/hierarchical-report`) is built, with the tree supplying its
  upper levels and each node's within-result detail below that — national → province → month,
  down to the values.
- **The reproducibility report** (`/repro-report`) exists.
- **The plan's own drift is reported**: a short section, generated from the diff between
  `Archive/plan-as-delivered/` and the live plan and from that file's commit history, saying
  how much of the original design survived, what had to change, and — using §4b's agency
  column — how much of the change was the human's and how much the agent's. This is evidence
  about how far an agentic system can be handed a research plan and left to run it, which is
  a question the proposal asks directly and which no other part of this project answers.
- **The case write-up** exists: a short document that could be lifted into the manuscript's
  *An illustrating case* section — what the analysis did, what the main results are, what was
  achieved, and what the challenges and limitations were. **This case replaces the genomic
  region-set co-occurrence analysis** that the archived manuscript's Appendix still specifies;
  the archived copy stays stale by design, since `Archive/` is never edited. The write-up
  therefore also has to supply what that Appendix supplied for the old case: the worked
  claim-tree skeleton and the perturbation families, in dengue terms. *(human-set,
  2026-08-23, settling batch-1 report §3.1)* Write it through the two-step
  process of Rule 9: results → claims → text. Include, specifically, **where this setup was
  more trouble than it was worth**, which the manuscript's Appendix asks for by name and
  which nobody else is in a position to report.
- **`/release`** has assembled the repository, and stopped before creating any remote (§4).

**Optional, only if the budget survives**: run the final model unchanged on `tha` and `vnm`
and report what happens. It is a real external check and costs little once everything works.
It is optional because the project is complete without it.

### The counterfactual — the greedy branch (batch 21)

**Batch 21 in the ledger. It runs on a git branch named `greedy` and is never merged.**

Batch 9 applied its promotion rule once and stopped, on the grounds that iterating it is
greedy coordinate descent on development CRPS — the failure this phase warns about — and
that one held-out year cannot diagnose it. The cost of stopping was stated rather than
hidden: two children sit outside the 0.57 CRPS floor from the promoted path. This batch
pays that cost out on a branch, so that what stopping bought and what it cost are both
measured instead of one being argued.

**What must be true when it is finished.**

- The branch `greedy` exists, branched from the main line at the commit that closed batch 9,
  and **nothing from it is merged into `main`** — no tree state, no result, and not the batch
  report either, whose every citation is a file on that branch. What crosses to `main` is this
  ledger row and the §4b entry recording what the branch settled. The reported analysis is the
  one on `main`.
- The iteration rule was **written and committed before the first round it decided was run**,
  as batch 9's was, and it is batch 9's rule with the single-application clause removed.
- Every round is a full sweep of every non-main child around the branch's current main path,
  a promotion, and a scored run of the promoted combination — through the tree's own scripts,
  under the same `COMBO`/`COMBO_BASE` mechanism, with the reference inherited and never
  re-run.
- The iteration ran to a **fixpoint** — a round in which no fork's best child clears the
  floor — or to a stated round cap, and which of the two it was is recorded.
- The branch's `analysis/run.sh` reproduces the greedy model, and its `conclusion.json` is
  computed by the same script as the main line's.
- The report says what the fixpoint scores, **how many rounds of selection produced it**, and
  what that implies for the holdout: a model chosen by *k* rounds of coordinate descent on
  development CRPS has had more opportunity to fit the development period than one chosen by
  a single application of the same rule, and the difference between the two is the size of
  the effect phase E is set up to detect.

**Constraints.**

- **The holdout is not opened on this branch.** It is not opened on any branch. The
  counterfactual is about how far development CRPS can be driven, not about what that costs
  out of sample — that question belongs to phase E and to the manifest, and answering it here
  would spend the one opening the project has.
- The greedy path's numbers are **not reported results of this project**. They are evidence
  about the method, and they enter the manuscript, if at all, as such.
- *(human-set, 2026-08-27: "note that it could be interesting to see where this would have
  taken us".)*

---

## 9. Budget

Nineteen batches, plus one optional. The purpose is to make the trade-offs of `AGENTS.md` §6
decisions rather than drift.

**The unit is implementation effort, not evaluation runs.** Batch 4 measured a full
eight-split backtest at 149 seconds for the reference through the emulated amd64 image and 56
seconds for a native `uv_env` model, so the whole phase-D manifest is a few hours of compute
and the binding constraint is the work of building models, not of running them.

| Phase | Batches | Note |
|---|---|---|
| A — orientation and bootstrap | 5 (1–5) | Done. |
| B — vertical slice and tree | 2 (6–7) | Fixed. |
| C — model development | 4 (8–11) | Three candidates and their internal forks. Extended only by the stopping rule in §8: the last batch must have moved the leaderboard by more than 0.4 CRPS. |
| D — stability | 4 (12–15) | Cut *within* the phase if the budget binds — the manifest's tier 2 goes first — and record the cut. |
| E — closing | 4 (16–19) | Not compressible. A project that ran out of budget before the closing phase has produced nothing this plan wanted. |
| Optional | 1 (20) | The external check on `tha` and `vnm`. Was first to be cut; **confirmed on 2026-08-31 and not cut**, and moved ahead of batch 19 so the case study can use it. |
| Counterfactual | 1 (21) | The greedy branch. Off the main path, on branch `greedy`; it produces no reported result and does not extend phase C. |

**If the budget binds, protect phase E before phase C.** A well-recorded mediocre model is
worth more here than an excellent undocumented one — the manuscript is about the record.

## 10. Left to me, not to you

Bring these to me rather than deciding them:

- Creating a git remote, and the owner and repository name. **Settled 2026-08-31**: `github.com/sandvelab/veridical-agentic-dengue-laos`, pushed as the last step of batch 19's `/release` and not before its scan. The agent still asks before the push.
- Anything that would spend real money.
- Abandoning the local Chap install in favour of a hosted service (§3).
- Any change to §2's success criterion or §3's non-negotiables. (§2 was settled on
  2026-08-23 and is now fixed; substituting a different reference model if EWARS cannot be
  run is explicitly *not* yours to decide — §2 says what to do instead.)

Everything else is yours to decide, and the record of how you decided it is a deliverable.

## Batch ledger — reports

*(One link per completed batch, added by `/do`. Never overwritten.)*

### Batch 1 — orient and set up

- [[26-08-23_b01_orientAndSetUp]]

### Batch 2 — reconnaissance: Chap

- [[26-08-23_b02_chapSetup]]

### Batch 3 — reconnaissance: the data

- [[26-08-23_b03_dataCharacterisation]]

### Batch 4 — reconnaissance: methods

- [[26-08-23_b04_methodSurvey]]

### Batch 5 — bootstrap

- [[26-08-26_b05_bootstrapPlan]]

### Batch 6 — vertical slice

- [[26-08-26_b06_verticalSlice]]

### Batch 7 — erect the tree

- [[26-08-26_b07_erectTheTree]]

### Batch 8 — the candidate contract, and candidate 1

- [[26-08-27_b08_candidateContract]]

### Batch 9 — candidate 1's forks, swept and promoted

- [[26-08-27_b09_candidateForks]]

### Batch 10 — candidate 2: gradient-boosted trees with a probabilistic head

- [[26-08-28_b10_boostedCandidate]]

### Batch 11 — candidate 3: the ensemble, and the close of phase C

- [[26-08-28_b11_ensembleCandidate]]

### Batch 12 — `/perturb plan`: the perturbation manifest

- [[26-08-29_b12_perturbationManifest]]

### Batch 13 — `/perturb run`: the setup and scoring rows

- [[26-08-29_b13_setupAndScoringRows]]

### Batch 22 — `/perturb run`: the two baseline forks' children

- [[26-08-29_b22_baselineForkRows]]

### Batch 14 — `/perturb run`: the candidate and family rows, and tier 2

- [[26-08-30_b14_candidateAndFamilyRows]]

### Batch 15 — `/perturb report`: the distribution, and the frozen holdout set

- [[26-08-31_b15_perturbationReport]]

### Batch 16 — the holdout, opened once, on the frozen manifest

- [[26-08-31_b16_holdout]]

### Batch 17 — the claim collection completed, and the report that descends to the values

- [[26-08-31_b17_claimsAndReport]]

### Batch 21 — the greedy branch

- `AI-generated/batch-reports/26-08-27_b21_greedyBranch.md`, **on branch `greedy` only**.
  It is not copied here, because every file it cites lives on that branch and a report
  whose links resolve to nothing is worse than a pointer. What it settled is in §4b.
