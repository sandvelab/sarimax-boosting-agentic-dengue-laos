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

If `chapkit_ewars_model` turns out not to be runnable on this dataset, do not substitute a
different reference on your own initiative: report what blocked it — that is itself a finding
about the platform's model library — and fall back to the two required baselines as the
criterion, saying so explicitly wherever the result is reported.

*Settled 2026-08-23 in response to the batch-1 report §3.2; agency: **human-set**.*

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
that is intended.

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
| 2 | A | Reconnaissance — Chap: install it, learn the model contract, learn the evaluation | open | |
| 3 | A | Reconnaissance — data: acquire, characterise, and fix the split scheme | open | |
| 4 | A | Reconnaissance — methods: candidate model families, and run `chapkit_ewars_model` to get the reference score | open | |
| 5 | A | Bootstrap: turn phases C–E into concrete batches | open | |
| 6 | B | Vertical slice: one trivial model, end to end, first CRPS number | open | |
| 7 | B | Erect the claim tree and route the vertical slice through it | open | |
| — | C | *Model development — batches written by batch 5* | | |
| — | D | *Stability and veridical work — batches written by batch 5* | | |
| — | E | *Closing: claims, report, validation, release — batches written by batch 5* | | |

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

**Batch 7 — erect the tree.** Build the claim tree from batch 5's design with `/node`, and
route the vertical slice through it so that `analysis/run.sh` reproduces the batch-6 result
end to end. Add the second baseline (seasonal climatology). Run `/validate invariants` and
`/validate cleanroom`: the clean-room check is worth its cost *now*, while the tree is small
and a failure is diagnosable.

From here on, everything happens inside the tree. A result produced outside it does not exist.

### Phase C — model development

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

### Phase D — stability and the veridical record

**What must be true when the phase ends.** The judgment calls are enumerated and costed
(`/perturb plan`); the ones within budget have been run (`/perturb run`); and the result is a
**distribution of conclusions over reasonable analyses**, not a single number
(`/perturb report`). What was not run is recorded as a decision, with the reason, not left as
an absence.

**The forks that are almost certainly worth having** — confirm against what batches 3 and 4
actually found:

- how `population` is used: offset, rate, or ignored (its staticness across thirteen years is
  a real problem, not a technicality)
- the covariate set and the lag structure applied to the climate variables
- the handling of the zero-heavy early period, and of provinces with very few cases
- the transformation of the target, and the observation model for the counts
- the forecast horizon
- the model family itself — the top candidates as siblings under one fork

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
  holdout number has been seen** (§3).
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

---

## 9. Budget

Rough, and to be revised by batch 5 once the cost of a `chap eval` run is actually known.
The purpose is to make the trade-offs of `AGENTS.md` §6 decisions rather than drift.

| Phase | Batches | Note |
|---|---|---|
| A — orientation and bootstrap | 5 | Fixed. |
| B — vertical slice and tree | 2 | Fixed. |
| C — model development | ~6–10 | The elastic one. Stop when the leaderboard stops moving, not when the shortlist is exhausted. |
| D — stability | ~4–6 | Cut here first if the budget binds, and record the cut. |
| E — closing | ~4 | Not compressible. A project that ran out of budget before the closing phase has produced nothing this plan wanted. |

**If the budget binds, protect phase E before phase C.** A well-recorded mediocre model is
worth more here than an excellent undocumented one — the manuscript is about the record.

## 10. Left to me, not to you

Bring these to me rather than deciding them:

- Creating a git remote, and the owner and repository name.
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
