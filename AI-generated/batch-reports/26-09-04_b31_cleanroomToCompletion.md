# Batch 31 — the clean-room runs to the end

Generated from [[26-08-22_dengueForecastingCase]] — iteration 31

**State: done — produced.** `analysis/run.sh` ran from a clean checkout to **exit 0**. Both
datasets, all 64 combinations, both distributions, every figure, and the last script in the
tree. This is what batches 18, 25 and 27 were each for, and it is the first time it has
happened.

`AI-generated/validation/26-09-04_cleanroom.md` is the check. Its figures are in four JSONs
beside it and the run's own outputs are preserved in `26-09-04_cleanroom-artefacts/`.

The claim that has been withheld since batch 18 can now be made: **`analysis/run.sh`
reproduces this analysis from nothing.** With one qualification that is a property of the
analysis rather than of the run, and which the check states in full: the reference model is
an unseeded container, so every figure that divides by it is a draw, and this run drew a
different one.

---

## 1. What the run establishes

**Every model this project wrote reproduced its CRPS exactly, on both halves.** 192
model-combination scores — 96 development, 96 holdout — and not one moved. The reported pool
returns 18.816872064690028 on development and 76.73108261979166 on the held-out year, digit
for digit, from an environment built from a lockfile on a machine with none of the project's
state.

**The phase-E answer's counts reproduce.** 26 of 32 beat the reference, 27 of 32 beat both
required baselines, the reported model ranks 18th of 32. Of 4 366 tracked files, **2 248 came
back byte-identical**, and no file differed only in the repository path.

**The environment matched the lockfile exactly** — 174 packages, zero lines carrying colour.
That is batch 27's own repair to `install-chap.sh`, verified from cold on a session that had
colour forced, where batch 27's run reported a mismatch that was not one.

**41 677 s, and it is a measurement.** The run was launched detached and under `caffeinate
-ims`, so the host could not sleep. Batch 27's 81 335 s was wall clock across a sleeping
machine and that batch correctly refused to read it as compute. This one can be read.

## 2. Batch 30's fix carried the run past the point that stopped batch 27 — by the margin that decided it

```
32 frozen development figure(s) have drifted, largest +0.051016 …
The frozen figures stand and are what this comparison uses.
```

32 frozen figures drifted, **0 pairings moved**, `manifest_holdout.csv` byte-identical, and
the run continued. That is the split batch 30 built: a drifted figure is reported, a moved
pairing is fatal.

What this run adds is the case batch 30 could not have: **the largest drift, +0.051016, is
outside the development noise band this run measured for itself, 0.048273.** Batch 27's
drift was inside its own band.

Batch 30 recorded considering and rejecting the obvious alternative — widen the tolerance to
the width of the band — on the grounds that the band is itself a draw of the same unseeded
model, and *"a check whose threshold is redrawn on every run is not a check"*. **Had it taken
that option, this run would have exited 1**, on a difference that is not a defect, in a tree
where nothing had moved. The reasoning was recorded as principle; this run turned it into a
consequence.

Batch 24's freeze check and batch 26's recorded selection also held, each for the third time
and each against a fresh draw that disagreed with the record: the tier-1 order *would* have
moved three positions and the tier-2 rule *would* have chosen six different pairs. Reported,
not acted on, and the eight recorded pairs ran.

## 3. The three files no clean-room run had ever compared

Batch 27 exited 1 **at** `pair_holdout_development.py`. The three files that script writes
were therefore carried unchanged out of the clone's index, and batch 27's comparison reported
them **identical** — a reading that was wrong in exactly the way batch 25's holdout half had
to be read as absent. *A file that was never written cannot have reproduced.*

This run wrote them, so they were compared for the first time
(`26-09-04_cleanroomPhaseEAnswer.json`, from a script written for the purpose):

| file | cells or scalars identical | what moved |
|---|---|---|
| `holdout_vs_development.csv` | 544 of 640 | three columns, all the reference on the holdout side |
| `holdout_vs_development.json` | 56 of 80 | 14 reference-derived; 10 structural, 4 of them the drift-reporting block itself |
| `fork_sensitivity_both.csv` | 129 of 221 | every numeric column; only `fork`, `stage`, `kind`, `owner` held |

**Every development column of `holdout_vs_development.csv` held** — including
`development_skill_score` and `development_crps_reference`, which batch 30 made read from the
freeze. The fix is visible in the output, not only in the code.

It also held `development_beats_all_baselines`, the one development figure batch 30 named as
re-derived rather than frozen and therefore able to move. It did not move on this draw. The
caveat batch 30 wrote into the output file stands as written: one draw not moving a field is
not a guarantee about the field.

## 4. The finding that is not about reproduction succeeding

The phase-E answer reports how far the stability finding transfers as **"14 of 17 forks agree
on whether the fork matters"**. That field came back **identical**. What it counts did not.

| | archived | clean-room |
|---|---|---|
| matter on both datasets | `aggregate`, `family`, `provinces`, `trainingWindow` | `family` |
| matter on development only | `persistence`, `weighting` | `aggregate`, `weighting` |
| matter on the holdout only | `covariates` | `provinces` |

Four forks matter on both in the archive and **one** does here; the two sets share only
`family`. The count is preserved because forks moved out of "both" into the single-dataset
lists in matching numbers, and a count cannot see that. The rank correlations underneath
moved too — analyses 0.395747 → 0.368985, forks 0.678922 → 0.789216.

A reader quoting "14 of 17" from the reproduced file would be quoting a number that
reproduced exactly and means something different in each run. Batch 18 wrote that these
checks *"verify shape and never content — a number can be right and its noun wrong, and
nothing here looks at nouns."* This is that sentence with a worked example under it, and the
example is a figure the project reports.

## 5. Batch 27's holdout-band claim does not survive a third draw

Batch 27 reported: *"The holdout's noise band is steady where the development band is not — 4
% across two draws. The figure phase E is measured against is not the unstable one."*

This draw gives **0.050443** against the archive's 0.014023 — 3.6×, and wider than any of the
four development draws.

| | batch 15 | batch 25 | batch 27 | batch 31 |
|---|---|---|---|---|
| development band | 0.021778 | 0.043084 | 0.034944 | **0.048273** |
| forks above it (of 17) | 6 | 3 | 3 | **3** |
| holdout band | 0.014023 | — | 0.013410 | **0.050443** |

The statement was true of the two draws it had and does not generalise; the held-out band is
a max minus a min over four repeats of an unseeded model, exactly as the development band is.
It is corrected in the check rather than left standing, and `readme-at-start.md` carried it
too.

This does not reopen the noise-band question. The human settled on 2026-09-03 that the count
stands as the headline, stated with the draw-dependence of the band. This batch adds a fourth
development draw agreeing with the second and third, and removes an exemption batch 27 had
granted the holdout.

## 6. Cost, measured rather than estimated

| | rows | planned | actual | ratio |
|---|---|---|---|---|
| development | 24 | 7 470 s | 9 882 s | **1.32** |
| development, less one row | 23 | 7 393 s | 6 671 s | **0.90** |
| holdout | 32 | 7 468 s | 7 394 s | **0.99** |

The holdout's **0.99** replaces batch 27's `ratio 8.814`, which that batch flagged as
contaminated and refused to report. The same rows, on a host held awake, come in at 0.99
against an estimate frozen before any of them ran — and phase E's estimates were the first in
this project that were predictions rather than measurements of runs already made.

**One row is 37× its archived duration and nothing else is.** `yearVariance_shared`: 3 210.7 s
against 85.6 s, its ensemble step 1 508 s against 62 s, 188.4 s per split against 7.7 —
producing **CRPS 18.840, identical**, from the same seed and the same four members. Every
other row on both halves is within about a factor of two of its archived time. It was the
last development row, not the first, so it is not a cold environment build. The record does
not say what happened and it is reported as an unexplained timing outlier rather than given a
cause it cannot support.

## 7. What was decided, and by whom

| Decision | Agency |
|---|---|
| The batch is **done — produced**: the run reached exit 0, which is the thing it was for | agent-autonomous |
| The run is held awake with `caffeinate`, so the elapsed time is a measurement rather than the uninterpretable figure batch 27 had to discard | agent-autonomous |
| Batch 27's "the holdout band is steady" is **corrected** in the check and in `readme-at-start.md`, rather than left standing beside a third draw that contradicts it | agent-autonomous |
| The fork-agreement finding is reported as the run's substantive result, above the reproduction it also establishes — a preserved number whose meaning moved is worth more to this project's argument than another file that matched | agent-autonomous |
| `cleanroom_phase_e_answer.py` is written rather than the three files eyeballed, so the comparison is an executed file (`AGENTS.md` §1) | agent-autonomous |
| `cleanroom_holdout_reproduction.py`'s stale nouns are fixed — it hardcoded batch 27's `DOES NOT MATCH` and called its output `why_the_run_stopped` on a run that did not stop | agent-autonomous |
| The `yearVariance_shared` timing outlier is reported without a cause, since the record does not support one | agent-autonomous |
| Nothing is carried to the human | — |

## 8. What this batch says about the method

Four clean-room runs, and each found something the one before it could not:

- **Batch 18** reached 8 of 32 development rows and reproduced the reported main path.
- **Batch 25** completed the development half and was stopped by a recorded selection being
  re-derived.
- **Batch 27** reached the last script and was stopped by a recorded figure being re-asserted.
- **Batch 31** got to the end, and the only defect left to find was in a script that had run
  successfully three times: `cleanroom_holdout_reproduction.py`, whose output called this run
  *"the assertion that stopped analysis/run.sh"* on a run that did not stop.

The defect family batch 24 opened — an artefact recorded once and then recomputed at run time
— is closed at four members, all four found by running the whole thing from nothing and none
by reading the code. Two code reviews and an outsider test found none of them.

But the sharper thing this run produced is not a defect at all. **A reported figure came back
byte-identical while the sets it counts changed almost completely.** Every check this project
has — invariants, the freeze check, the selection check, byte comparison of results — would
report that field as reproduced, because every one of them compares values. The project has
written down twice that its checks verify shape and never content; this is the first time the
gap has been demonstrated on a number the analysis actually reports, and the demonstration
came free, from a run whose purpose was to confirm that things match.

The practical consequence for batch 19 is small and specific: where the write-up reports
agreement between the two datasets, it should report *which* forks agree and not only how
many.

## 9. What is next

**Batch 28** — `check_pool.py`'s member matching depends on which combinations exist on disk.
Untouched here.

Then **20** (the external check on `tha` and `vnm`) and **19** (write-up, reproducibility
report, release).

**Batch 19 may now state that `analysis/run.sh` reproduces this analysis from a clean
checkout**, and must state it with the qualification this run measured: our models are
bit-identical, the unseeded reference is not, and the figures that divide by it are draws.

## 10. Files

**Added**

- `AI-internal/useful-scripts/cleanroom_phase_e_answer.py` — the three phase-E answer files,
  archived beside a clean-room run's, classified into reference-derived and structural.
- `AI-generated/validation/26-09-04_cleanroom.md` — the check.
- `AI-generated/validation/26-09-04_cleanroom_comparison.json` — by `cleanroom_compare.py`.
- `AI-generated/validation/26-09-04_cleanroomTier2Drift.json` — by `cleanroom_tier2_drift.py`.
- `AI-generated/validation/26-09-04_cleanroomHoldoutReproduction.json` — by
  `cleanroom_holdout_reproduction.py`.
- `AI-generated/validation/26-09-04_cleanroomPhaseEAnswer.json` — by the new script.
- `AI-generated/validation/26-09-04_cleanroom-artefacts/` — what the run wrote, with a README.

**Changed**

- `AI-internal/useful-scripts/cleanroom_holdout_reproduction.py` — the environment block reads
  what `install-chap.sh` reported instead of hardcoding batch 27's mismatch; the keys that
  called a drift comparison "why the run stopped" are renamed for a run that did not stop.

**Unchanged, and checked to be so**

- `analysis/` — nothing in the analysis was run, edited or re-run by this batch. The
  clean-room ran in a throwaway clone, now discarded.
- `analysis/05_stability/results/manifest_holdout.csv` — `fc9d1a16…`, as batch 15 froze it.

**Records appended** — `AI-generated/validation/provenance.md`, four sections.
