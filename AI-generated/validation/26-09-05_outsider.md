# Outsider check — 2026-09-05, batch 19

`/validate outsider`, the second run in this repository. Batch 18 ran the first, before the
held-out year had been opened and before three of the four fixes that followed from it. This
one runs on the tree as it will be released.

Two agents, each given a throwaway `git clone` at `922506b` and nothing else — no
conversation history, no summary, no hint about what was known to be weak. Each was told to
work only inside its own clone, to run nothing costing more than about five minutes, and to
report where following the instructions was hard. The clones are disposable and nothing
either agent did reaches the record.

**Two tasks, chosen to exercise the halves batch 18's tasks exercised, on what has changed
since.**

- **A — write into the tree.** *"Add a new alternative to the analysis: an aggregation of the
  headline mean that trims the highest- and lowest-scoring province before averaging. Take it
  as far as the repository's own instructions say it should be taken."*
- **B — trace a reported number to the command that produced it.** *"The repository reports
  that its model, run unchanged on Vietnam, scores worse on the final year than the reference
  model does. Establish, from the repository alone, what that number is; which file it is
  read from; which script wrote that file; what command produced it, in what environment,
  from what inputs, at what commit. Verify as much of that chain as you can execute."* Then:
  *"state what the project's own evaluation can and cannot distinguish on that dataset, and
  whether the summary documents agree with the files underneath them."*

**Agent A did not finish.** It was terminated by an account spend limit partway through
writing its new node — `You've hit your monthly spend limit … your session limit resets
2:30am (Europe/Oslo)`. What it had produced was inside its own clone and is discarded. **The
write-into-the-tree half of this check therefore did not run**, and that is recorded here
rather than quietly omitted: batch 18's equivalent task is what found the contradiction
between the plan's freeze rule and the `combos` invariant, so the half that did not run is
not the cheap half.

**Agent B finished, and it is the most productive check this project has run.** It verified
twenty-one links of the chain, re-executed most of them under a *different* interpreter and
different pandas and numpy majors than the pinned ones, and returned findings in three
categories. Every one below was re-verified against the files before anything was changed.

---

## What it verified

The chain from the reported number to the archived bytes holds, and most of it holds under
execution rather than under reading.

`external_vs_laos.json` → `report_external.py` (digest matches, re-ran byte-identical) →
`conclusion.json` → `conclude.py` (re-ran byte-identical) → the compare and aggregate outputs
(re-ran byte-identical) → `metrics_cell.csv`, from which it **independently recomputed** the
mean CRPS, the skill score, the paired difference, the split-clustered standard error and the
coverage, and reproduced all of them to fifteen digits → `model_spec.json`, whose six model
file digests, configuration digest and dataset digest all match → the sibling cut, whose
checksum manifest verifies → `Archive/sibling-datasets/`, whose manifest verifies and whose
`chap_VNM_admin1_monthly.csv` carries **the same digest** as the file the model was evaluated
on, byte for byte.

It also **re-derived the component seed** — `int(blake2b("20260822:analysis/03_models/03_candidate/c_ensemble", digest_size=8), 16) % 2**32` = `1648567750` — matching what the model spec records.

**One numeric link could not be executed**: `eval.nc` is HDF5 and reading it needs `chap_core`,
which is in the gitignored pinned environment. Everything downstream of it was recomputed.

**A stronger result than the record claims.** Four scripts of the reported analysis re-ran
byte-identically under system CPython with pandas 2.3.0 and numpy 2.3.0 rather than the
pinned versions. That is worth knowing and it cuts both ways: the pins are, for these steps,
currently untested.

## Findings that changed the repository

### 1. Two arithmetic errors of the agent's, in five places each

**"A factor of 215."** The ratio of the reference model's re-run spread on Vietnam's
development backtest to Thailand's. The two endpoints, both verified against
`reference_repeat_noise.csv`, are `7.082205159391536` and `0.032397735197368424`. The ratio
is **218.6**. 215 is not derivable from either the exact or the rounded values; it came from
a mistyped intermediate.

**"Thirty-five times its band."** `0.08563434091782274 / 0.002365941278000961` = **36.19**.

Both are corrected in the eight living documents — `readme-at-start.md`, the two `claim.md`
files, the claim collection, the case write-up and its sidecar, the reproducibility report,
the batch-reports index and the plan. The batch-20 report and the task-log entries keep what
they said, as records of what was stated at the time; this file is where the correction lives.

### 2. The resolution yardstick had been applied to one number out of six

The project's success criterion says every comparison is reported "with a plain statement of
what that spread can distinguish", and sets its own line: 1.03 standard errors is where
"cannot separate" arrived in practice during development. That yardstick appears against
exactly one figure in the whole repository — the development headline, at 1.90.

Computed for all six analyses from the stored conclusions:

| analysis | skill | paired difference / split-clustered SE |
|---|---|---|
| Laos, development | +0.1485 | 1.90 |
| Laos, **held-out year** | **+0.0868** | **0.94** |
| Vietnam, development | +0.0852 | 3.62 |
| Vietnam, **final year** | **−0.0862** | **0.97** |
| Thailand, development | +0.0856 | 1.45 |
| Thailand, **final year** | **+0.0197** | **0.49** |

**Five of the six are on the wrong side of the project's own line, including the held-out
result it reports as beating the reference and the Vietnamese row it reports as a loss.**
Every one of those sentences was true and unaccompanied. The agent's summary layer had also
dropped the column that carries the answer: `external_conclusions.csv` holds
`standard_errors_from_reference`, and neither `external_vs_laos.json` nor the figure's data
file — the two files the summaries actually cite — carries it through.

Recorded as **claim C48**, as a table in the case write-up, and in the reproducibility
report's §5.

### 3. Two resolution yardsticks that disagree, and only one reported

Vietnam's development row is **3.62 standard errors** from the reference *and* has a margin
of 4.905 CRPS sitting **inside** the reference's own 7.082 re-run spread — which is driven
entirely by one repeat of four landing 12 % above the others. A paired standard error asks
whether a difference is large relative to how it varies across splits; a re-run spread asks
whether it is large relative to how much the comparator moves against itself. On this row
they answer oppositely. The record reported the second only, and nothing in it noticed the
two were different quantities. Both are now reported.

The same conflation has a milder form: "the reference's own re-run spread, in skill" means
max−min of *our skill against each repeat* in phase D (0.0218 on Lao development) and *CRPS
spread ÷ reference mean CRPS* in the external check (0.0256 on the same repeats). Prose calls
both by the same name.

### 4. The Laos band clause is draw-dependent and was stated without its dependence

"All three drops are larger than the two reference bands taken together" clears by 0.0588 for
Thailand and 0.0418 for Vietnam, and by **0.0207** for Laos. This project has drawn the Lao
development band four times, at 0.0218, 0.0431, 0.0349 and **0.0483** — and on the largest the
band sum is 0.0637 against a drop of 0.0617, so the clause is false. The human settled on
2026-09-03 that the phase-D fork count is to be stated *together with* the draw-dependence of
its band; the same standard had not been applied here. C42's scope now carries it.

### 5. Three gaps in the provenance chain

- **`analysis/05_stability/scripts/lib/driver.py` was named as a script of record with no
  `sha256:`** — the only one. The `hashes` invariant checks files that *have* a digest, so it
  passed: the library that builds and executes every step of every combination was the one
  un-pinned script in the record. **Fixed.**
- **`report_external.md` carried a sentence git contradicts.** It said the script was carried
  by batch 20's closing commit; `git log` returns only `bfbc096`, the commit named one line
  above. **Fixed.**
- **`Archive/sibling-datasets/provenance.md` names `analysis/06_external/01_ingest` twice**,
  a node that does not exist — the node is `analysis/01_data/03_siblings`. The file is under
  `Archive/`, which is never edited, so the correction is appended as a section rather than
  applied in place.

### 6. A recorded premise that contradicts the model it describes, in 40 of 47 combinations

The largest finding, and the one carried forward rather than fixed here.

`01_weighting/a_equal/scripts/choose_weighting.py` states what the pool will contain, so that
the prediction it registers can say what share of the pool the required baselines carry. It
builds that statement from `MODELS.glob("**/scripts/*/MLproject")` — the **unfiltered**
version of the glob `prepare_members.py` uses. Batch 22 added a second child to each baseline
fork and fixed `prepare_members.py`; this script was not fixed.

So since batch 22 it has recorded a **six-member pool at 1/6 each, with 2/3 of its mass on
required baselines**. The pool that ran is **four members at 1/4, with half its mass on
baselines**, and the run log prints both statements two lines apart. Counted across the
`a_equal` specs: **40 say six and 7 say four**, the seven being those written before batch 22.
The reported development row and the reported held-out row therefore disagree about the shape
of the same model.

**No score moves.** `user_option_values`, the field that reaches the model configuration, is
unaffected, and the agent verified this by re-running the script and diffing. What is wrong is
the registered prediction's premise — and the fact that re-running one main-path step of the
reported analysis rewrites a committed file **for a reason that has nothing to do with the
unseeded reference**, which is the qualification the record gives for everything that does not
reproduce.

It is the **fifth instance** of the fork-blindness this project has found five times, and the
second instance of a recorded premise being derived rather than recorded.

**Why it is not fixed in this batch.** The clean-room run in flight was launched before this
was known and will re-run `choose_weighting.py` for every combination from cold, which
supplies the independent confirmation each of the previous four fixes was built against —
batch 26 against batch 25's data, batch 30 against batch 27's, batch 28 against batch 31's.
Fixing it while that evidence is still being gathered would throw the evidence away. It is
**batch 32** in the ledger.

### 7. Two more, recorded and not acted on

- **`beats_all_baselines` has no uncertainty attached anywhere in the project.**
  `compare_models.py` pairs every model against the reference only, so the strongest-sounding
  results — the model beats both required baselines on all six analyses — are comparisons of
  two means with no spread. The margins are 15 to 21 CRPS against a 0.5 noise floor on the
  row where it matters most, so this very probably changes no conclusion, and "very probably"
  is doing work a computed spread would not have needed to do.
- **`models.csv` records the pooled reference as `n_samples 4000`** where the evaluation is a
  mean of four repeat *scores*. Nothing computes from the field; it is misleading to read.

---

## What this check cost, and what it says about the method

About twenty-five minutes of wall-clock for the agent that finished, and one agent lost to an
account limit. It found **two wrong numbers, one systematic reporting omission across five of
six reported analyses, one conflation of two different yardsticks, three provenance gaps and
one defect in forty committed files** — none of which `/validate invariants` could see, and
none of which any amount of re-reading by the party that wrote them would have found.

Batch 18 concluded that these checks verify shape and never content. This run is the sharpest
demonstration of that yet: every finding above is a statement that is **true on the page and
false, incomplete or unaccompanied when executed**. The invariant checker passed throughout,
before and after.

**And the half that did not run is the half that wrote into the tree.** Batch 18's equivalent
task found the ambiguity that made the plan's freeze rule and the tree's own invariant
contradict each other. Whether the tree is still writable by an outsider following the
instructions is, after this run, unestablished.

---

**Agency:** agent-autonomous. That `/validate outsider` runs before release is the plan's
(phase E); the tasks, the verification of every finding and the decision to carry finding 6
forward rather than fix it are the agent's.
