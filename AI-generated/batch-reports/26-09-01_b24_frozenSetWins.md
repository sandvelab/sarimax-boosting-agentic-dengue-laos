# Batch 24 — the frozen set wins over the recomputation

Generated from [[26-08-22_dengueForecastingCase]] — iteration 24

**State: done — produced.** The script that writes the frozen phase-E set no longer rewrites
it, a new invariant checks the file rather than the script that wrote it, and eleven
situations were put to the two of them on throwaway copies. Nothing in the reported analysis
moves: `manifest_holdout.csv` and `holdout_freeze.json` are byte-identical to what batch 15
froze and batch 16 ran, which is the point.

Batch 18 scheduled this batch, at its §6: *"`freeze_holdout_manifest.py`'s recomputation of
the frozen set."* It was deferred because the defect was not reachable while phase E was
closed and the fix needs someone who can re-freeze and check byte-identity afterwards.

---

## 1. The defect, stated exactly

One file carries the honesty of the held-out year. Plan §3 makes the holdout spread a
measurement rather than a selection by fixing *what* gets evaluated on 2010 **before** 2010 is
opened, and `analysis/05_stability/results/manifest_holdout.csv` is that fixing. Everything
phase E reports rests on it: thirty-three rows, thirty-two of them with a development twin
frozen beside them.

`freeze_holdout_manifest.py` writes that file, and it is the **last step of the development
half of `05_stability/run.sh`** — which batch 15 put into `analysis/run.sh`. So every run of
the analysis re-derived the frozen set from whatever the development manifest said at that
moment.

It returned byte-identical every time. Not because anything made it: because the tree had not
changed. And the tree is allowed to change. Earlier in the same block, `plan_manifest.py`
re-derives the **development** manifest from the tree by design, and §3 as
clarified on 2026-09-01 binds the frozen holdout manifest **and nothing else** — while
`/validate invariants`'s `combos` check *requires* every non-main child in the tree to have a
development row. A fork child added after the opening was therefore one run of
`analysis/run.sh` away from entering the frozen set, with no batch and no decision behind it.
Batch 18's outsider check added one and watched thirty-three rows become **thirty-four**.

That is the shape of failure batch 18 named in its own §7 and found five times: a statement
about the repository that was **true as prose and false as behaviour**. The prose was in
`run.sh` itself — *"batch 15 established that both come back byte-identical, so the set this
runs is the one fixed before the year was opened"* — and it was an observation about one
moment offered as a guarantee.

## 2. What the script does now

The frozen file is authoritative. The script has two modes, chosen by whether it exists.

**It does not exist** — the freeze, batch 15's path, unchanged except for one new refusal
(§3 below).

**It exists** — a verification. The set the tree would produce now is derived by the same
function that would have written it, `manifest_holdout.csv` and `holdout_freeze.json` are not
written at all, and the comparison goes to `results/holdout_freeze_check.json`.

What a difference does is not uniform, because the plan does not make it uniform:

| Difference | What happens | Why |
|---|---|---|
| a development row with no frozen twin | reported **unpaired**, never added | §3 as clarified on 2026-09-01. The freeze binds this manifest, not the tree; an alternative found after the opening is carried in the tree and in the development manifest, has no holdout twin, and never joins the 32 |
| a frozen row the tree no longer carries | **fatal**, non-zero exit | the frozen set names an analysis this repository can no longer run, so it can no longer be reproduced |
| a frozen row whose structure moved | **fatal** | the columns that say *what analysis runs* — fork, child, what it re-runs, what it inherits — are the set |
| a frozen row whose numbers moved | reported, not fatal | the reference model is unseeded; batch 18's clean-room run moved the development skill score by 0.0065 with nothing wrong |

The last row is a decision with a cost, and the cost is stated: a development conclusion that
genuinely should not have moved will be recorded rather than raised. The alternative fails
batch 25 on its own honest re-draw, which is worse — a check that a correct clean-room run
cannot pass is a check that will be weakened the first time it fires.

## 3. A refusal that was not there at all

If the frozen file is **missing** and the year has already been opened — `run_status_holdout.csv`
records a row as `ran`, or any `analysis/results/*__holdout/` directory exists — the script
refuses outright and says to restore the file from git.

Under the version this replaces, deleting the frozen manifest and running `analysis/run.sh`
silently re-derived the whole set after the numbers had been seen. That is §3's central
prohibition, and the file is versioned precisely so that restoring it is the available move.

The evidence deliberately does **not** consult `.holdout_opened`, which is gitignored and says
only that *this working tree* ran the year. That is the right question for the driver's re-run
seal and the wrong one here: a fresh clone that has run nothing still carries results computed
from a set that was frozen, and re-deriving it there would be as wrong as doing it in the tree
that opened the year. Batch 18 got caught by the mirror image of this — a seal that used the
versioned condition alone and so sealed every clone — and the two conditions are not
interchangeable.

## 4. The file is now checked, not only the script that writes it

`check_invariants.py` gains **`freeze`**. The refusal above lives in one script; this holds
whatever wrote the file.

- The frozen manifest must still hash to what `holdout_freeze.json` recorded for it, and the
  row count must agree.
- **No file under `analysis/results/*__holdout/` may exist at the commit that added the frozen
  set.** That is the claim `holdout_freeze.json`'s own `commit_note` makes — it is the entire
  evidence that the set predates the opening — and nothing checked it. It is checkable against
  git in one command.
- If `holdout_freeze_check.json` is present it must be about the file that is here, and must
  not be carrying a fatal difference.

The other digests `holdout_freeze.json` carries — `conclusions.csv`, `distribution.json`, the
development `manifest.csv` — are deliberately **not** checked. They are context recorded at
the freeze, not the frozen artefact, and the development half may legitimately be re-run.

## 5. Eleven situations, and what the old version did with them

`AI-internal/useful-scripts/check_freeze_defence.py`, seven scenarios to the script and four
to the invariant, on throwaway copies built from the live files. Four of them corrupt the
frozen manifest, which is why none runs against the live tree.
→ `AI-generated/validation/26-09-01_freezeDefence.json`, written up in
`26-09-01_freezeDefence.md`.

**All eleven behaved as specified.** Two carry the weight.

**`added`** is batch 18's defect reproduced. A fork child discovered after the opening appears
as a new development row; the frozen set stays at **33 rows** and the row is reported as
unpaired.

**`refreeze_from_cold`** is a regression test rather than a defence. The script was
restructured, and a refactor that changed the set would have changed the reported result — so
the frozen file is deleted along with every trace of the year having been opened, the freeze
path runs from cold, and what comes back is **byte-identical to the manifest frozen in batch
15**.

Run against the superseded version, **six of the seven script scenarios fail and every one of
them exits 0**:

| Scenario | Superseded version | Now |
|---|---|---|
| `added` | frozen set grows to **34 rows** | 33 rows, one unpaired |
| `dropped` | frozen set shrinks to **32 rows** | fatal, exit 1 |
| `restructured` | frozen set rewritten with the renamed child | fatal, exit 1 |
| `conclusion_drift` | frozen pairing replaced by the drifted numbers | reported, pairing stands |
| `missing_after_opening` | set re-derived from scratch | refuses, exit 1 |
| `intact` | `holdout_freeze.json` rewritten | nothing written |
| `refreeze_from_cold` | byte-identical | byte-identical |

The `conclusion_drift` row is the one batch 18 did not name and it is the one that would have
fired next: under the superseded script, **batch 25's clean-room run of `analysis/run.sh`
would have rewritten the frozen development pairing with the clean room's own re-drawn
reference numbers** — the pairing §3 exists to fix, quietly refitted by the run that was
supposed to verify it.

## 6. A second hole, closed by the same change

`holdout_freeze.json` records `frozen_on`, and it was written from `date.today()` on every
invocation. Run today against the superseded script, it rewrote **2026-08-31 → 2026-09-01**;
the other eighteen keys were identical.

Batch 16 found and fixed exactly this in the field beside it, `frozen_at_commit`, and left the
date. So the date on which the phase-E set was frozen — half of the evidence that it was
frozen before the year was opened — was being overwritten by every run of the analysis, in a
file whose own note explains why that must not happen to the field above it. It is written
once now, because the file carrying it is.

The pattern is worth stating plainly: **batch 16 fixed one field of a record that a script
recomputes, and left the recomputation.** The durable fix was never the field.

## 7. What did not happen

**Nothing was re-run.** No analysis, no model, no combination. `freeze_holdout_manifest.py`
was executed twice, and both times it read four files and wrote one. The frozen manifest and
`holdout_freeze.json` are byte-for-byte what they were at the start of this batch, which
`/validate invariants`'s new `freeze` check now asserts on every run.

**The freeze path was not deleted**, although the set is frozen and this project never freezes
again. It is the path a reader implementing this method runs, and it is what
`refreeze_from_cold` exercises; a script that cannot demonstrate how the set was produced
leaves a set with an assertion behind it rather than a derivation.

**The defect was not urgent and is fixed anyway.** The human settled on 2026-09-01 that the
perturbation set stays at 32 and nothing further is added, so the tree does not grow again
before release and the defect was unreachable in practice. It is fixed for the reader
implementing the method, which is what this repository is for.

## 8. What was decided, and by whom

| Decision | Agency |
|---|---|
| The frozen file is authoritative: once it exists the script verifies and never writes to it | agent-autonomous, inside a human-set constraint (plan §3) |
| A development row with no frozen twin is reported unpaired, not fatal — the tree may grow, the frozen set may not | agent-autonomous, following the human's clarification of 2026-09-01 |
| A drifted development conclusion is reported and not fatal, because the reference is unseeded and batch 25 must be able to pass | agent-autonomous |
| The set is not re-derived at all once a holdout number has been seen; the file is restored from git | agent-autonomous |
| The evidence for "the year has been opened" is the versioned record and the results on disk, never the gitignored `.holdout_opened` | agent-autonomous |
| `check_freeze` also checks the claim `holdout_freeze.json` makes about its own commit, which nothing checked | agent-autonomous |
| The freeze path is kept although this project will never freeze again | agent-autonomous |

## 9. What this batch says about the method

Batch 18's summary was that `/validate invariants` **verifies shape and never content**. This
batch is a third thing, and it is the one that took a check on the method to find: a script
that re-derives a frozen artefact is not caught by either. The shape was right — the file
existed, its rows were planned, `combos` passed. The content was right — the bytes never
changed. What was wrong was that neither of those was *load-bearing*: they held because the
input happened not to have moved, and every check in the repository confirmed the outcome
while nothing looked at the mechanism.

The general form is worth naming, because this project has now hit it three times. Batch 16
found `frozen_at_commit` recomputed and fixed the field. Batch 18 found the whole manifest
recomputed and scheduled this batch. Both are the same thing: **a value that records history
must not be derived at run time, because a derivation is a claim about the present.** The
`frozen_on` field survived both diagnoses, sitting one line above the field batch 16 repaired.

And the fix has a cost that should be stated rather than discovered later. `analysis/run.sh`
can now fail in a way it could not before: a tree that has moved under the frozen set stops
the run instead of quietly bringing the set along. That is the intended trade — but it means
the release run has a new way to fail, and batch 25 is the first thing to discover it.

## 10. Files

**Changed**

- `analysis/05_stability/scripts/freeze_holdout_manifest.py` — two modes; the derivation is
  one function used both to freeze and to check the freeze.
- `analysis/05_stability/run.sh` — the comment that asserted byte-identity as a guarantee now
  says what enforces it.
- `AI-internal/useful-scripts/check_invariants.py` — the `freeze` check.
- `AI-internal/useful-scripts/README.md`, `.claude/commands/validate.md` — the new check and
  the new script. **An instructions change under Rule 4.**

**Added**

- `AI-internal/useful-scripts/check_freeze_defence.py` — the eleven situations.
- `analysis/05_stability/results/holdout_freeze_check.json` — what the tree would freeze now,
  against what is frozen. Written on every run of `analysis/run.sh`.
- `AI-generated/validation/26-09-01_freezeDefence.md` and `.json`.

**Unchanged, and checked to be so**

- `analysis/05_stability/results/manifest_holdout.csv` — `fc9d1a169065…`, as batch 15 froze it.
- `analysis/05_stability/results/holdout_freeze.json` — `frozen_on: 2026-08-31`,
  `frozen_at_commit: 937fd5c`.

**Records appended** — `analysis/05_stability/provenance/freeze_holdout_manifest.md`,
`AI-generated/validation/provenance.md`, `analysis/05_stability/claim.md`,
`analysis/05_stability/criticality.md`.

`/validate invariants`: all ten checks pass, `freeze` included.

## 11. What is left

**Batch 25** — `/validate cleanroom` to completion. Batch 18's reached 8 of 32 development
rows; both distributions are unverified from cold and the phase-E half has never run from a
clean checkout. It is also the first run that will exercise this batch's fix end to end.

**Batch 20** — the external check on `tha` and `vnm`.

**Batch 19** — the case write-up, the reproducibility report, the release. Last, because a
release must not claim more than its own checks support.

Nothing is carried to the human.
