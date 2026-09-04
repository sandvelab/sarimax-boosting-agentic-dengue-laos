# Clean-room check — 2026-09-04, batch 31

`/validate cleanroom`, run on the tree batch 30 repaired: build the environment from
nothing, run the analysis, and **report the differences** rather than announcing success.

**`analysis/run.sh` exited 0.** A clean checkout of this repository ran the whole analysis —
both datasets, all 64 combinations, every figure and both distributions — to the end, for the
first time in the project. Batch 18's run was cut off by its session, batch 25's exited 1 at
the freeze check with phase E never reached, and batch 27's exited 1 at the last script in
the tree.

The short statement of what this run establishes:

- **Every model this project wrote reproduced its CRPS exactly, on both halves.** 192
  model-combination scores, none moved.
- **The phase-E answer's counts reproduce**: 26 of 32 beat the reference, 27 of 32 beat both
  required baselines, the reported model ranks 18th, and its CRPS is identical to the last
  digit. What moved is downstream of the unseeded reference and nothing else.
- **Batch 30's fix carried the run past the point that stopped batch 27**, and by the margin
  that decided it: 32 frozen figures drifted, 0 pairings moved, and the largest drift landed
  **outside** the noise band. The alternative batch 30 considered and rejected — widening the
  tolerance to the band — would have failed this run.
- **Batch 24's freeze check and batch 26's recorded selection both held from cold**, each for
  the third time and each on a fresh draw that disagreed with the record.
- **The environment matched the lockfile exactly**, which is batch 27's own repair verified
  from cold.
- **One reported figure reproduced while what it counts did not**, and that is the finding of
  this run that is not about reproduction succeeding.

## How it was run

`git clone` of the repository at `c94e85f` into a scratch directory, `environment/chapenv`
built from `environment/lock.txt`, then `bash analysis/run.sh` from cold, on the host, with
Docker available so the containerised reference model can run. The clone carried **4 366
tracked files** and no `.holdout_opened`, so the seal released and phase E was allowed to run.

The harness is `AI-internal/useful-scripts/run_cleanroom.sh`, unchanged from batch 27.

The run was launched detached from the session, **under `caffeinate -ims`**. Both mattered.
The session's own wait process was killed three times while the analysis ran on untouched;
and where batch 27 recorded 81 335 s of wall clock across a host that slept — a figure it
correctly refused to read as compute — this run's **41 677 s (694 min) is a measurement**.

## The environment, and batch 27's repair

`environment/install-chap.sh` printed:

```
matches environment/lock.txt exactly (174 packages)
```

Batch 27's run printed `DOES NOT MATCH` at the same commit against an environment that
matched exactly, because `uv pip freeze` colours its output when the invoking shell asks and
that session had `FORCE_COLOR=3`. Batch 27 routed both uses through a `freeze()` helper that
sets `NO_COLOR` and strips surviving escapes.

From cold, on a session that also had colour forced, the check now reports the truth:
**0 lines carrying ANSI colour, 174 packages installed against 174 in the lockfile, none in
one and not the other** (`26-09-04_cleanroomHoldoutReproduction.json`, `environment`). The
fix is verified rather than asserted.

## What reproduced

`26-09-04_cleanroom_comparison.json`, by `cleanroom_compare.py`.

| | |
|---|---|
| tracked files | 4 366 |
| came back byte-identical | **2 248** |
| differ in something computed | 2 118 |
| differ only in the repository path | 0 |
| untracked in the clone | 5 |

The 5 untracked are the same `member_selection.json` files batch 27 found: five setup
combinations that have not been re-run since batch 14 added the file, so the archive never
received it. A record that was never written, not a value that moved.

### The models

`26-09-04_cleanroomHoldoutReproduction.json`. Per model, per combination, from each
`conclusion.json`'s `crps_by_model`:

| model | development identical | moved | holdout identical | moved |
|---|---|---|---|---|
| persistence | 32 | **0** | 32 | **0** |
| climatology | 32 | **0** | 32 | **0** |
| ensemble (reported) | 27 | **0** | 27 | **0** |
| hier_nb | 4 | **0** | 4 | **0** |
| boosted | 1 | **0** | 1 | **0** |
| **reference** (unseeded) | 0 | **32** | 0 | **32** |

**192 model-combination scores and not one of ours moved by a bit**, on a machine that built
the environment from a lockfile and the models' own environments from their `uv.lock` files.
The reported pool returns 18.816872064690028 on development and 76.73108261979166 on the
holdout, digit for digit.

### The phase-E answer

| field | archived | clean-room | |
|---|---|---|---|
| CRPS of the reported model | 76.73108261979166 | 76.73108261979166 | **identical** |
| rank within the distribution | 18 | 18 | **identical** |
| beats the reference | 26 of 32 | 26 of 32 | **identical** |
| beats both required baselines | 27 of 32 | 27 of 32 | **identical** |
| skill score | 0.086820 | 0.076510 | −0.010310 |
| reference CRPS | 84.026202 | 83.088163 | −0.938039 |
| reference noise band | 0.014023 | 0.050443 | ×3.6 |
| rows inside the noise band | 17 | 22 | +5 |
| forks above the band | 5 | 2 | −3 |

Everything that moved is the reference model or a figure computed from it. Everything the
phase-E answer states as a count or a ranking held.

## The holdout noise band is not the steady one

Batch 27 reported the held-out band at 0.013410 against the archive's 0.014023 and drew a
conclusion from it: *"The holdout's noise band is steady where the development band is not —
4 % across two draws, against a factor of two on development. The figure phase E is measured
against is not the unstable one."*

**A third draw gives 0.050443** — 3.6 times the archived value, and wider than any of the
four development draws. That statement was true of the two draws it had and does not
generalise; the held-out band is a max minus a min over four repeats of an unseeded model,
exactly as the development band is, and it moves for the same reason. It is corrected here
rather than left standing.

The two bands, every draw this project has taken:

| | batch 15 | batch 25 | batch 27 | batch 31 |
|---|---|---|---|---|
| development | 0.021778 | 0.043084 | 0.034944 | **0.048273** |
| forks above it (of 17) | 6 | 3 | 3 | **3** |
| holdout | 0.014023 | — | 0.013410 | **0.050443** |

The human settled on 2026-09-03 that the count stands as the headline, stated together with
the draw-dependence of the band it is measured against. Nothing here reopens that; it adds
the fourth development draw, and it removes the exemption batch 27 had granted the holdout.

## The three checks that stopped earlier runs

### Batch 30's, at the last script — passed, and by the margin that mattered

```
32 frozen development figure(s) have drifted, largest +0.051016 on
provinces_reportingOnly__weighting_crpsWeighted. The frozen figures stand and are
what this comparison uses.
```

- **32 frozen figures drifted; 0 pairings moved.** Every frozen row still has a development
  twin of that name, and `manifest_holdout.csv` is byte-identical to the archive's.
- The drift runs −0.045837 to **+0.051016**.
- The development noise band this run measured for itself is **0.048273**.

So **the largest drift is outside the band**, where batch 27's was inside its own. Batch 30
recorded rejecting a widened tolerance on the grounds that the band is itself a draw and *"a
check whose threshold is redrawn on every run is not a check"*. Had it taken that option
instead, this run would have exited 1 — on a difference that is not a defect, in a tree where
nothing had moved. The categorical split is what let the run finish, and this is the first
run in a position to show it.

### Batch 24's, at the freeze — passed

`holdout_freeze_check.json`: *the frozen set is intact*, 33 recomputed rows, 0 unpaired
development rows, 32 rows whose numbers drifted, and `manifest_holdout.csv` still
`fc9d1a16…`. This is where **batch 25** exited 1.

### Batch 26's, at the selection — passed

`manifest_selection_check.json`, after tier 1 re-ran from cold:

- the tier-1 order **would** have moved three positions;
- the tier-2 rule **would** have chosen **six different pairs**;
- verdict: *the rule would now choose 6 different pair(s); the recorded ones stand.*

Reported, not acted on; the run went on to execute the eight recorded pairs. Three clean-room
runs have now put three independent draws to this check and it has absorbed all three.

`cleanroom_tier2_drift.py` confirms the rule itself has not drifted:
`reimplementation_reproduces_the_archived_selection: true`.

## The three files no clean-room run had ever compared

Batch 27 exited 1 *at* `pair_holdout_development.py`, so the three files it writes were
carried unchanged out of the clone's index and batch 27's comparison reported them
**identical** — a reading that was wrong in the same way batch 25's holdout half had to be
read as absent. A file that was never written cannot have reproduced. This run wrote them.

`26-09-04_cleanroomPhaseEAnswer.json`, by `cleanroom_phase_e_answer.py`.

**`holdout_vs_development.csv` — 544 of 640 cells identical.** Three columns moved, all of
them the reference on the held-out side: `holdout_crps_reference`, `holdout_skill_score`,
`skill_holdout_minus_development`. **Every development column held**, including
`development_skill_score` and `development_crps_reference`, which are read from the freeze —
batch 30's fix, doing visibly what it was built to do.

It also held `development_beats_all_baselines`, the one development figure batch 30 named as
re-derived from today's table rather than read from the freeze, and which a re-run can
therefore move. On this draw it did not move. The caveat batch 30 wrote into the output file
stands unchanged: it is a field that *can* move, and one draw not moving it is not a
guarantee.

**`holdout_vs_development.json` — 56 of 80 scalars identical.** Fourteen reference-derived
scalars moved. Ten structural fields moved, and four of those are the
`frozen_pairing_verified` block itself reporting the drift, which is the block existing to do
exactly that.

**`fork_sensitivity_both.csv` — 129 of 221 cells identical.** Only `fork`, `stage`, `kind`
and `owner` held: every numeric column and every "does this fork matter" verdict is measured
against a band that moved.

## One number reproduced; what it counts did not

The phase-E answer reports how far the stability finding transfers from development to the
held-out year as **"14 of 17 forks agree on whether the fork matters"**.

That field came back **identical: 14 both times.** The sets behind it did not.

| | archived | clean-room |
|---|---|---|
| matter on both | `aggregate`, `family`, `provinces`, `trainingWindow` | `family` |
| matter on development only | `persistence`, `weighting` | `aggregate`, `weighting` |
| matter on the holdout only | `covariates` | `provinces` |

Four forks matter on both datasets in the archive; **one** does in the clean-room, and the
two sets share only `family`. The agreement count is preserved because forks moved out of
"both" and into the single-dataset lists in matching numbers, and the count cannot see the
difference.

A reader quoting "14 of 17" from the reproduced file would be quoting a figure that
reproduced exactly and that means something different in each run. The rank correlations
beneath it moved as well — analyses 0.395747 → 0.368985, forks 0.678922 → 0.789216 — so the
underlying ordering is visibly not the same one.

This is batch 18's line arriving with a worked example. *These checks verify shape and never
content; a number can be right and its noun wrong, and nothing here looks at nouns.* Here a
number is right, its noun has changed under it, and byte-comparison of that field reports
success.

## Cost, measured rather than estimated

The first clean-room timing this project can read as compute, because the host was held
awake.

| | rows | planned | actual | ratio |
|---|---|---|---|---|
| development | 24 | 7 470 s | 9 882 s | **1.32** |
| development, less one row | 23 | 7 393 s | 6 671 s | **0.90** |
| holdout | 32 | 7 468 s | 7 394 s | **0.99** |

The holdout half's 0.99 replaces batch 27's `ratio 8.814`, which that batch flagged as
contaminated by the sleeping host and refused to report as a finding. It was right to: the
same rows, awake, come in at 0.99 against the estimate frozen before any of them ran.

**One row is 37 times its archived duration and nothing else is.** `yearVariance_shared` took
3 210.7 s against 85.6 s in the archive; inside it, the ensemble step took 1 508 s against 62
s, 188.4 s per split against 7.7. It produced **CRPS 18.840, identical**, from the same seed
and the same four members. Every other row in both halves is within about a factor of two of
its archived time. The record does not say what happened — it was the last development row,
not the first, so it is not a cold environment build — and it is reported as an unexplained
timing outlier rather than given a cause it cannot support.

## What this run does not establish

- **It is one draw.** The reference model is an unseeded container and every figure that
  divides by it is a sample. This run says our models are deterministic and the counts held;
  it cannot say the counts hold on the next draw, and the fork-agreement finding above is a
  direct demonstration that some of them do not mean the same thing when they do.
- **It verifies shape, not content.** A comparison that says 2 248 files came back identical
  says nothing about whether the analysis is right.
- **The five missing `member_selection.json` files are still missing** from the archive, as
  they were for batch 27. Nothing computed differs.
- **`check_pool.py`'s member matching still depends on which combinations exist on disk** —
  batch 28, open, and untouched here.

## Files

- `26-09-04_cleanroom_comparison.json` — `cleanroom_compare.py`
- `26-09-04_cleanroomTier2Drift.json` — `cleanroom_tier2_drift.py`
- `26-09-04_cleanroomHoldoutReproduction.json` — `cleanroom_holdout_reproduction.py`
- `26-09-04_cleanroomPhaseEAnswer.json` — `cleanroom_phase_e_answer.py`, new in this batch
- `26-09-04_cleanroom-artefacts/` — what the run wrote, with a README

The clone was 18 GB and has been discarded. The artefacts are what the findings above rest
on, so they can be re-checked without re-running the analysis from cold.
