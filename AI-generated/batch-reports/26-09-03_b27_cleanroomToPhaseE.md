# Batch 27 — the clean-room reaches phase E, and stops at the last script

Generated from [[26-08-22_dengueForecastingCase]] — iteration 27

**State: blocked.** `/validate cleanroom` was to be run to completion and was not.
`analysis/run.sh` got through the freeze check that stopped batch 25, opened the holdout,
scored all 32 held-out analyses, wrote the distribution and the figures — and **exited 1 at
`pair_holdout_development.py`, the last script in the tree.**

What is missing and what would unblock it is in §7. The batch establishes a great deal that
no previous run could, including the single strongest reproduction statement this project has
made, and it did not do the one thing it was for.

The run was launched detached from the session. That earned its keep: the session's wait
process was killed twice while the analysis ran on untouched.

---

## 1. What the run establishes

`AI-generated/validation/26-09-03_cleanroom.md`, with figures in
`26-09-03_cleanroom_comparison.json`, `26-09-03_cleanroomTier2Drift.json` and
`26-09-03_cleanroomHoldoutReproduction.json`.

The harness and both comparison scripts were **verified by digest against batch 25's
provenance record before the run started**, so this is the same check run further.

**Every model this project wrote reproduced its CRPS exactly, on both halves.**

| model | development identical | moved | holdout identical | moved |
|---|---|---|---|---|
| persistence | 32 | **0** | 32 | **0** |
| climatology | 32 | **0** | 32 | **0** |
| ensemble (reported) | 27 | **0** | 27 | **0** |
| hier_nb | 4 | **0** | 4 | **0** |
| boosted | 1 | **0** | 1 | **0** |
| **reference** (unseeded) | 0 | **32** | 0 | **32** |

**192 model-combination scores and not one of ours moved by a bit.** Batch 18 could say this
of the reported development path; batch 25 of the whole development set; this run says it of
the held-out year as well, which no clean-room run had reached.

Of 4 329 tracked files, **2 224 came back identical**.

## 2. Phase E, from a clean checkout for the first time

The half the project's own release claim depends on, and it holds:

| field | archived | clean-room | |
|---|---|---|---|
| CRPS of the reported model | 76.73108261979166 | 76.73108261979166 | **identical** |
| beats the reference | 26 of 32 | 26 of 32 | **identical** |
| beats both required baselines | 27 of 32 | 27 of 32 | **identical** |
| rows inside the reference noise band | 17 | 17 | **identical** |
| forks above the band | 5 | 5 | **identical**, same five by name |
| skill score | 0.086820 | 0.084343 | −0.002477 |
| reference CRPS | 84.026202 | 83.798911 | −0.227290 |
| reference noise band | 0.014023 | 0.013410 | −0.000613 |

Everything that moved is downstream of the unseeded reference and nothing else.

**The holdout's noise band is steady where the development band is not** — 4 % across two
draws, against a factor of two on development. The figure phase E is measured against is not
the unstable one.

## 3. Batch 26 and batch 24 both worked, under the conditions that defeated their predecessor

`manifest_selection_check.json`, written after tier 1 re-ran from cold:

- the tier-1 order **would** have moved four positions;
- the tier-2 rule **would** have chosen **six different pairs**;
- verdict: *the rule would now choose 6 different pair(s); the recorded ones stand.*

Reported, not acted on. The run went on to tier 2 and ran all eight recorded pairs. This is
precisely what killed batch 25, arriving a third time on a third draw of the reference, and
passing through. `holdout_freeze_check.json` then reported *the frozen set is intact* — 33
rows, `manifest_holdout.csv` still `fc9d1a16…`.

**One qualification to batch 26's report.** `manifest.csv` is **not** byte-identical from a
cold checkout. All 32 rows differ, in the two cost columns only — `est_seconds_dev` and
`est_seconds_holdout` are measured wall-clock durations. Rank order, names, node paths, skill
values and all eight pairs are identical. Batch 26's claim was true of the tree it was tested
in, where the timings were not re-measured; a file carrying durations cannot be byte-stable
from cold.

## 4. Why it stopped, and why that is a third instance rather than a new problem

`pair_holdout_development.py` takes each holdout row's development figure from the frozen
`manifest_holdout.csv` — correctly. It then asserts that each frozen figure still equals what
`conclusions.csv` says **today**, to `1e-9`, a tolerance its comment calls "not a tolerance
for drift".

**That assertion cannot hold on any tree whose development half has been re-run**, because
the development skill score divides by the unseeded reference. It passes only where it is not
needed.

Two facts about what it stopped on:

- **32 rows drifted; 0 rows had their pairing move.** Every frozen row still has a
  development twin of the same name and `manifest_holdout.csv` is byte-identical to the
  archive's. Its message — *"The pairing this compares on is no longer the pairing that was
  frozen"* — is not what the data shows.
- **Every drift is inside the noise band this run measured for itself**: largest −0.025673
  against 0.034944.

And the tree contradicts itself. `holdout_freeze_check.json`, written minutes earlier by
batch 24's machinery, reports the *same* drift on the *same* 32 rows under the heading
`drift_under_an_unchanged_set` and concludes **the frozen set is intact**. One script reports
this drift by design; the next treats it as fatal.

So the family is now three: batch 24 found a frozen artefact recomputed at run time, batch 26
a recorded selection re-derived at run time, and this is **a recorded figure re-asserted
against a recomputed one.** The fix has the same shape as the other two.

## 5. Two smaller findings

**The environment check reported a mismatch that was not one.** `install-chap.sh` printed
`DOES NOT MATCH environment/lock.txt` where batch 25 reported an exact match at the same
commit. The environment was the lockfile's — 174 packages, identical as sets. `uv pip freeze`
colours its output when the invoking shell asks, and the session that launched this run had
`FORCE_COLOR=3`; every line failed the byte diff on its colour wrapper, and `sort` misordered
the wrapped names on top of that. The same `uv pip freeze` **writes `lock.txt`** on the
`RESOLVE=1` branch, so a lockfile produced from such a shell would not install.

This one **was fixed in this batch**: both uses go through a `freeze()` helper that sets
`NO_COLOR` and strips surviving escapes, verified by running the comparison against the live
`chapenv` with `FORCE_COLOR=3` and `CLICOLOR_FORCE=1` deliberately set — *matches
environment/lock.txt exactly (174 packages)*. It is fixed and the phase-E defect is not,
because this one is reporting machinery outside the analysis tree whose repair cannot change
a result and takes seconds to verify, where `pair_holdout_development.py` writes a reported
phase-E result and needs a defence of its own.

**Five files the archive does not have.** The clean-room wrote 50 `member_selection.json`
files; the archive has 45. The five setup combinations concerned have not been re-run since
batch 14 added the file, so the archive never received it. Nothing computed differs — a
record that was never written rather than a value that moved.

## 6. What was decided, and by whom

| Decision | Agency |
|---|---|
| The batch is **blocked**, not "done — produced": it established more than any previous clean-room run and did not run one to completion, and batch 19 rests on its word | agent-autonomous |
| `install-chap.sh` **is** fixed here; `pair_holdout_development.py` is **not**, and the line between them is stated rather than left to look arbitrary | agent-autonomous |
| The clean-room's own outputs are copied into the repository before the 18 GB clone is discarded, so batch 30 can build its defence against the data that stopped this run | agent-autonomous |
| `cleanroom_holdout_reproduction.py` is written rather than the numbers read out of the transcript, so the holdout table, the phase-E headline and the environment comparison all come from an executed file (AGENTS.md §1) | agent-autonomous |
| The 81 335 s elapsed and the `ratio 8.814` holdout cost line are reported as contaminated by the host sleeping, not as findings | agent-autonomous |
| Batch 26's "byte-identical `manifest.csv`" is qualified rather than left standing | agent-autonomous |
| Whether the development noise band should stay a max-minus-min over four draws — **still open**, now with a third draw | **carried to the human** |

## 7. What is missing, and what would unblock this batch

**Missing:** `analysis/run.sh` does not run to completion from a clean checkout. It exits 1 at
the last script. And because that script did not run, `holdout_vs_development.csv`,
`holdout_vs_development.json` and `fork_sensitivity_both.csv` are unverified from cold — the
comparison reports them unchanged, and that reading would be wrong for the same reason batch
25's holdout half had to be read as absent.

**What would unblock it** is one change, the same shape as batch 24's and batch 26's:

**Batch 30 — the frozen development figure stops being re-asserted.** The frozen
`development_skill_score` in `manifest_holdout.csv` is a record of what was true at the
freeze; `conclusions.csv` is what the tree computes today, and the two cannot agree on a tree
that has been re-run. The comparison should keep using the frozen figure — it already does —
and **report** the disagreement rather than dying on it, in the file it already writes for
the purpose (`frozen_pairing_verified`). What must stay fatal is a pairing that genuinely
moved: a frozen row with no development twin of that name, which this run had **zero** of.
The defence should be built against this run's own `conclusions.csv`, preserved in
`26-09-03_cleanroom-artefacts/`, exactly as batch 26 built its defence against batch 25's.

**Batch 31 — `/validate cleanroom` to completion**, on the fixed tree. What this batch was
for, and what batch 27 was for before it.

Then **20** (the external check on `tha` and `vnm`) and **19** (write-up, reproducibility
report, release). **Batch 19 must not claim that `analysis/run.sh` reproduces this analysis
from nothing** until a run gets past the last script. It now reproduces both halves' numbers,
which is more than could be said before, and it still does not finish.

**The question carried to the human is unchanged and has one more data point.** The
development noise band is a max minus a min over four draws of an unseeded model, and three
draws now give 0.021778, 0.043084 and 0.034944 — a factor of two apart. The headline "N of 17
forks move the conclusion further than the reference moves on its own" reads 6, 3, 3. What is
stable is *which* forks clear it — `family`, `weighting` and `aggregate` on all three draws —
and stating the finding that way rather than as a count may be the cheapest resolution. It is
still not the agent's to take.

## 8. What this batch says about the method

Batch 18: `/validate invariants` verifies shape and never content. Batch 24: a script that
re-derives a frozen artefact is caught by neither. Batch 25: that defect was not rare, and
only a cold run of the whole thing finds it. This batch adds the obvious next step and it is
worth saying plainly: **the family has three members and each was found one file further
downstream than the last, by the same method — running the whole thing from nothing.** Two
code reviews and an outsider test found none of them.

The sharper point is about self-contradiction as a signal. `holdout_freeze_check.json` and
`pair_holdout_development.py` looked at the same 32 drifted rows minutes apart and reached
opposite verdicts, and both files are in the same node, written by the same project, four
batches apart. Nothing checks that a tree agrees with itself about what is fatal. The
information needed to predict this run's failure was sitting in the file written immediately
before it.

## 9. Files

**Added**

- `AI-internal/useful-scripts/cleanroom_holdout_reproduction.py` — both halves per model, the
  phase-E headline archived beside the clean-room's, the environment question, and the rows
  the run stopped on.
- `AI-generated/validation/26-09-03_cleanroom.md` — the check.
- `AI-generated/validation/26-09-03_cleanroom_comparison.json` — by `cleanroom_compare.py`.
- `AI-generated/validation/26-09-03_cleanroomTier2Drift.json` — by `cleanroom_tier2_drift.py`.
- `AI-generated/validation/26-09-03_cleanroomHoldoutReproduction.json` — by the new script.
- `AI-generated/validation/26-09-03_cleanroom-artefacts/` — what the run wrote, with a README.

**Changed**

- `environment/install-chap.sh` — the `freeze()` helper, so the lockfile comparison and the
  lockfile itself are not corrupted by a colour-forcing shell.

**Unchanged, and checked to be so**

- `analysis/` — nothing in the analysis was run, edited or re-run by this batch. The
  clean-room ran in a throwaway clone, now discarded.
- `analysis/05_stability/results/manifest_holdout.csv` — `fc9d1a16…`, as batch 15 froze it.

**Records appended** — `AI-generated/validation/provenance.md`, three sections.
