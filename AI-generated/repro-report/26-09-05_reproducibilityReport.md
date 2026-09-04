# Reproducibility report — 2026-09-05

`/repro-report`. What this project produced, what is tracked and how, what the veridical
work established, who decided what, and — the section a critical reader should read first —
what does not hold.

Every count below is read from `repro_inventory.json` beside this file, written by
`AI-internal/useful-scripts/repro_inventory.py` at commit `922506bb8`. Nothing here was
counted by eye. Figures about the analysis itself are read from the claim collection, whose
47 claims each name the stored result grounding them.

---

## 1. What was produced

**A forecasting model with a defensible score**, and the record of how it came about. The
two are not ranked: a model whose development cannot be reconstructed is a failed run of
this project, and it is stated that way in the project's own first file.

The analysis is a tree of **71 nodes** — analytical aims written as questions — of which
**17 are alternatives forks** carrying **40 children**, so **23 paths are in the repository
and not on the main path**. Nine nodes decompose into sub-analyses. `analysis/run.sh`
reproduces the whole of it: the reported result, the distribution around it on both
datasets, and the external check.

The reported model is a **linear opinion pool** over two candidate families of ours and both
required baselines, equally weighted.

| | development backtest | held-out year |
|---|---|---|
| mean CRPS, ours | **18.817** | **76.731** |
| mean CRPS, reference (WHO EWARS-csd) | 22.098 | 84.026 |
| skill score | **+0.1485** | **+0.0868** |
| beats both required baselines | yes | yes |
| 10–90 coverage against a nominal 0.80 | 0.863 | 0.755 |
| cells the mean is over | 371 | 192 |

**And it is one member of a distribution rather than a number.** Thirty-two analyses that
all looked reasonable were fixed before either dataset was scored. On development the skill
score runs **−0.0724 to +0.2320** and the reported analysis sits thirteenth of thirty-two; on
the held-out year it runs **−0.5038 to +0.2026**, more than twice as wide, and the reported
analysis sits eighteenth.

**Run unchanged on two other countries**, the model beats the reference on both development
backtests and on one of the two final years, and beats both baselines on all six analyses.
The development-to-final-year drop replicates in all three countries.

**Everything the tree produced is on disk**: 3 845 result files, 2.61 GB, across 69
combination directories — 1 466 CSVs, 1 402 JSON documents, 241 NetCDF evaluations, 220
figures, 175 model configurations and 309 run logs. The smallest combination holds 25 files
and the largest 79.

**And it is navigable.** `AI-generated/hierarchical-report/` is 1 387 linked pages: the tree,
then for each of the 69 scored combinations the national mean, that mean by province, each
province month by month, and the per-cell scores everything above is an average of. Every
number on it is displayed from the file the analysis wrote; nothing on it recomputes an
aggregate, so the report cannot disagree with the analysis.

## 2. What is tracked, and how

The chain runs **sentence → claim → result → provenance record → script → commit →
environment**, and each link is a file rather than an inference.

**Sentence → claim.** The case write-up is written from the claim collection and carries a
provenance sidecar mapping every passage to the claims it rests on — or, where it rests on
none, to what kind of statement it is instead: *design*, grounded in the plan and
`AGENTS.md`; *record*, grounded in the batch reports; or *judgment*, which is the agent's
opinion and is labelled as such.

**Claim → result.** **47 claims**, with **107 grounding paths between them, all 107 of which
resolve** to files that exist. Two claims are `agent-on-human-assessment` and forty-five are
`agent-autonomous`.

**Result → provenance record.** **84 records covering 240 recorded runs**, naming **271
sha256 digests** across **78 distinct scripts**. A record is a running account rather than a
snapshot: when a script changes, a section is appended saying what changed and what has run
under the new version, and earlier sections keep the version they describe. `/validate
invariants` fails if a record does not name its file's *current* digest — a check added
after twenty records, the headline result's included, were found describing versions that no
longer existed.

**Script → commit.** **143 commits**, of which 69 touch `analysis/` and **6 touch the
instruction files**. The instructions are versioned as part of the method: two runs of this
repository under different instructions are two different methods, and every provenance
record names the instruction commit in force as well as the code commit.

**Commit → environment.** One pinned environment, **174 packages** in
`environment/lock.txt`, built by a script that reports any difference between what it built
and that file. **No node needs an override**, so there is one environment to build rather
than a tree of them. Each of our models additionally carries its own lockfile inside its
model directory, and every run records whether the lockfile the platform built from is the
one shipped.

**The parts that are checked rather than asserted.**

- **`/validate invariants`** — ten deterministic checks: the tree's semantics; a provenance
  record for every result; every digest current; every plot's data and script beside it;
  every stochastic script seeded; every claim resolving; the combination space closed
  against three planned manifests; the frozen phase-E set still the set that was frozen; the
  working tree clean; and no value looking transcribed between steps by hand. It runs at the
  end of every analysis and before every commit.
- **220 figures, and 220 of them have their plotted values beside them.**
- **Determinism, measured.** Every model this project wrote returns byte-identical per-cell
  scores, model listing and fitted object when run again.
- **The clean-room.** `analysis/run.sh` has been run from a fresh clone with the environment
  built from nothing, and its output compared against the archive.

## 3. The veridical section

**What was varied.** Seventeen judgment calls, computed from the tree rather than listed by
hand, in four families: the data every model faces (5 forks), which models are compared and
how the baselines are constructed (3), the models' own internals (8), and how the answer is
scored (1). The manifest is two tiers — every fork alone, then eight pairs selected by a rule
fixed in advance — giving **32 analyses**, run on development and again on the held-out year,
plus **4 external rows** on the sibling countries.

**On what basis each choice was made.** Every fork's `claim.md` states its question and each
child states what it assumes. Where a choice was taken by the agent it is
`agent-autonomous`; where the human set it, it is `human-set`; and §4b of the plan logs 247
such decisions with their basis.

**How stable the conclusion was.** Not very, and the useful part is the structure of the
instability.

- The **model family** is what the conclusion is sensitive to and the choices *inside* a
  family are not. Swapping the pool for the first candidate costs 0.2209 of skill; the eight
  forks inside the two member families move it by at most 0.0081.
- The **cheapest analysis in the manifest** — re-weighting the headline mean, which re-runs
  no model — is the most consequential of the choices that leave our model alone, at 0.0835.
- Under one reasonable weighting, **a required baseline beats the model this project
  reports**, in every combination where that weighting appears.
- **Fork effects do not compose.** The largest pairwise interaction is bigger than either
  main effect behind it.
- **Development ranking is a weak guide to held-out ranking**: rank correlation +0.396 across
  the 32 analyses. The analysis that ranked highest on development among those that change
  the data or the models is twenty-ninth of thirty-two on the held-out year.
- **The drop from development to the final year replicates on two other countries**, so it is
  not about 2010 in particular.
- **What the evaluation can resolve is a property of the country.** The reference model's own
  unseeded re-run spread is 0.032 CRPS on Thailand's development backtest, 0.565 on Laos's
  and 7.082 on Vietnam's — a factor of 215 — and on Vietnam our own margin falls inside it.

**What was left unexplored, and why.** Nothing was cut for budget: the development manifest
cost 3.66 hours, the held-out half 2.39 and the external check 1.81, against budgets of 12
and 6 hours. Three things are named as not done and are absences by decision rather than by
oversight: **the reference model was never perturbed** (the plan forbids tuning the target);
**Thailand's twenty-two years outside the Lao calendar were not spent**, which is what would
separate "the final year is hard" from "a four-split backtest is noisier than an eight-split
one"; and **the pool's independent reconstruction is unavailable on the external datasets**,
because a member is evaluated separately only under a perturbation row and the external check
moves no fork. Each is recorded in a file with what it would have cost.

## 4. The agency record

From the plan's §4b, parsed by `AI-internal/useful-scripts/plan_drift.py`: **247 decisions
across 36 settling occasions.**

| agency | decisions | share |
|---|---|---|
| `agent-autonomous` | 211 | **85.4 %** |
| `human-set` | 17 | 6.9 % |
| `agent-on-human-assessment` | 9 | 3.6 % |

**This is not a claim that the agent did 85 % of the thinking.** The default in this project
is `agent-autonomous` by design, so the entries that carry information are the exceptions,
and the seventeen `human-set` decisions are the ones that determine what the project is: the
success criterion, the reference model to beat, the seal on the held-out year, the storage
budget, the target venue, the repository name, the instruction that the perturbation set
stops at thirty-two, and the delegation of the judgment about where the setup was more
trouble than it was worth. The agent decided far more things; the human decided which things
there were to decide.

**Seven of the thirty-six occasions were opened by the human** rather than by a batch, and
fourteen decisions were taken at them.

The provenance records tell the same story one level down: **209 of them are
`agent-autonomous`** and the rest are compound — *agent-autonomous for running it, human-set
for the constraint it works under* — which is the honest shape of the collaboration and is
also, as §5 notes, more than the vocabulary can count.

**Where the record is explicit that the agent decided alone**: the whole analysis design, the
model families, every fork and its children, the perturbation manifest and its cut order, the
claim collection, the release assembly, and the judgment in the case write-up about where
this apparatus was not worth its cost. The human read that judgment afterwards; recording it
as jointly held on that basis would overstate their part, and the plan says so.

## 5. What does not hold

The section a critical reader should value most. A reproducibility report that reports only
success is an advertisement.

**The reference model cannot be reproduced, and every reported ratio divides by it.** WHO
EWARS-csd draws from a posterior and exposes no seed. It is run four times on every dataset
and the per-cell mean is used, with the spread carried rather than hidden — but the headline
skill score is a draw, not a constant. Our models are bit-identical on re-run; the
denominator is not. **Every figure in this project that divides by the reference carries that
qualification, and the clean-room runs have measured the same yardstick at 0.0218, 0.0431,
0.0349 and 0.0483 of skill on the same dataset.**

**One reported figure reproduced byte-identically while what it counts changed completely.**
A clean-room run returned *14 of 17 forks agree on whether the fork matters* — the same
number — while the set of forks mattering on *both* datasets went from four to one, the two
sets sharing a single member. Every check in this repository compares values, so every one of
them called that field reproduced. **This is the sharpest available statement of what
structural checking cannot do**: a number can be right and its noun wrong, and nothing here
looks at nouns.

**The structural checks verify shape, never content.** A provenance record can name the wrong
script; a claim can point at a result that does not support it. One thing crossed that line —
a record's digest is now checked against the file rather than merely being present — and the
rest of it is where it was.

**The clean-room verification is one step behind the tree.** The run that took
`analysis/run.sh` to completion from a clean checkout was made before the external check node
existed. Its shared code was verified byte-identical on the live tree before anything ran,
but the node's own scripts have not been through a cold run at the time this section was
written. Whether that gap is closed is stated in the release record beside this file.

**The plan-drift measurement overwrites its own data files.** The script writes to fixed
filenames, so re-running it at the end of the project replaced the figures the batch-18
narrative quotes. That narrative is still an accurate account of what the measurement said
then — its numbers are in its own text and in git history — but the JSON beside it now
answers for a later commit. This is a Rule 5 failure in the project's own machinery, found
while writing this report, and it is reported rather than repaired: repairing it means
changing where a script writes on the last batch, for values that are recoverable from git.

**The agency vocabulary drifted past what counts it.** `AGENTS.md` names three values. §4b
now holds ten entries whose agency field is something else — compound labels like
*agent-autonomous, inside the human-set §3*, and two reading *carried to the human*. Every
one of them is more informative than the three-value vocabulary allows, and every one falls
out of the counts in §4, which are therefore over 247 entries rather than 257. The right fix
is a richer vocabulary; it was not applied at the end of the project.

**Nothing here reaches statistical significance and nothing pretends to.** The largest margin
the project achieved is 1.90 standard errors. The held-out year is roughly 216
province-months through four splits. Three countries of one harmonisation are not a sample,
and the two sibling countries were not held out from anything because nothing was developed
on them.

**The development-arrangement gap between Laos and the two sibling countries is not
attributable to optimisation alone.** It is the project's most direct measurement of what
developing against one dataset bought on that dataset, and the three countries also differ in
province count, burden and reporting system. Nothing in the design varies development while
holding the country fixed, and nothing can be built here that does.

**Four separate places recorded a decision by re-deriving it at run time** from numbers that
do not reproduce — the frozen phase-E manifest, the tier-1 order and tier-2 selection, a
frozen development figure, and the external check's own cost estimate. Three were found by a
clean-room run exiting non-zero and one by asking what the next one would do. The pattern is
the single most persistent defect class in this repository, and its recurrence after each fix
is itself a finding: **a rule that a value recording a decision must not be derived at run
time was learned four times and not generalised in time to prevent the fourth.**

**The counterfactual does not fit the tree.** Iterating the promotion rule to a fixpoint had
to be run on a git branch outside the analysis, because the alternatives-and-sub-analyses
structure records the outcome of a search as a set of static siblings and has no shape for
the search itself.

**One node's results are not combination-scoped in the way the invariant assumes**, and the
check derives its exemption from where the manifests are rather than naming the nodes. That
is the correct form of the fix and it is still an exemption; a third planning node would
inherit it silently.

---

## How to reproduce this

```bash
git clone <repository>
cd <repository>
bash environment/install-chap.sh          # builds environment/chapenv from lock.txt
bash analysis/run.sh                      # about 13 hours; Docker must be running
.venv/bin/python AI-internal/useful-scripts/check_invariants.py
```

`analysis/run.sh` reproduces the reported result, the distribution around it on both
datasets, and the external check. Most of the wall-clock is the reference model's unseeded
repeats through an emulated amd64 image on six datasets. The held-out year runs from a clean
checkout by design: the seal that stops it being re-run in *this* working tree is deliberately
not versioned, because a versioned seal seals every clone and turns a reproduction into a
description of one.

**Agency:** agent-autonomous. That this report exists is Rule 10's; its content, its
inventory script and the judgments in §5 are the agent's.
