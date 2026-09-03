# Clean-room check — 2026-09-03, batch 27

`/validate cleanroom`, run on the tree batch 26 repaired: build the environment from
nothing, run the analysis, and **report the differences** rather than announcing success.

**The phase-E half ran from a clean checkout for the first time.** Batch 18's run was cut
off by its session; batch 25's exited 1 at the freeze check with the whole development half
behind it and phase E never reached. This run went through the freeze check, opened the
holdout, scored all 32 held-out analyses, wrote the distribution and the figures — and then
**exited 1 at the last script in the tree**, `pair_holdout_development.py`.

So `analysis/run.sh` still does not run to completion from a clean checkout. What stopped it
this time is one assertion in one arithmetic step, and it is the third instance of a defect
family this project has now met three times.

The short statement of what this run establishes:

- **Every model this project wrote reproduced its CRPS exactly on both halves.** 192
  model-combination scores — 96 development, 96 holdout — and not one moved.
- **The phase-E answer reproduces.** `beats_the_reference` 26 of 32, `beats_both_required_baselines`
  27 of 32, 17 rows inside the noise band, and the same five forks above it by name: all
  identical to the archive.
- **Batch 26's fix did the job it was built for.** The tier-1 order would have moved four
  positions and the tier-2 rule would have chosen six different pairs. Both were reported and
  neither was acted on; the recorded selection ran.
- **Batch 24's freeze check passed from cold**: *the frozen set is intact*.
- **The environment matched the lockfile**, though the check said otherwise for a reason of
  its own.

## How it was run

`git clone` of the repository at `80276f3` into a scratch directory, `environment/chapenv`
built from `environment/lock.txt`, then `bash analysis/run.sh` from cold, on the host, with
Docker available so the containerised reference model can run. The clone carried **4 329
tracked files** and no `.holdout_opened`, so the seal released and phase E was allowed to run.

The harness is `AI-internal/useful-scripts/run_cleanroom.sh` and the comparison
`cleanroom_compare.py`; both were **verified by digest against batch 25's provenance record
before the run started** — `846911b2…` and `33010dd1…` — so this is the same check run
further, not a new one. `cleanroom_tier2_drift.py` (`3d98ea7e…`) was verified the same way.

The run was launched detached from the session that started it. That mattered: the session's
own wait process was killed twice during the run and the analysis was untouched by it.

**On the elapsed time.** The harness recorded **81 335 s** between starting and finishing
`analysis/run.sh`. That is wall clock and the host slept for a large part of it, so it is not
a measure of compute. The development half — start to the freeze check — took about **4 h
20 m**, against batch 25's 3 h 48 m for the same work. The `holdout: planned 7 468 s vs
actual 65 818 s (ratio 8.814)` line the run printed is contaminated by the same sleep and
should not be read as a cost finding.

## What the environment did, and a check that reported the wrong thing

`environment/install-chap.sh` printed **`DOES NOT MATCH environment/lock.txt`**, where batch
25 had reported an exact match at the same commit.

**The environment was the lockfile's.** 174 packages, the same names at the same versions,
verified against the preserved freeze output in
`26-09-03_cleanroomHoldoutReproduction.json`. What differed was the check's own output.

`uv pip freeze` colours its output when the invoking shell asks it to, and the session that
launched this run had `FORCE_COLOR=3` set. Every package name came back wrapped:

```
lock.txt   aiosqlite==0.22.1
freeze     \033[1maiosqlite\033[0m==0.22.1
```

so all 174 lines failed the byte diff, and `sort` ordered the wrapped names differently as
well — leaving 8 packages out of position even after the escapes are removed. The line the
check corrupts is the one that means *the environment is not what the repository says it is,
and the run that follows would be unrecordable*, in the script's own words.

Two things follow. The comparison is sensitive to the terminal environment of whoever invokes
it. And the **same `uv pip freeze` writes `lock.txt`** on the `RESOLVE=1` branch, so a
lockfile produced from a colour-forcing shell would carry escape codes and would not install.
`environment/lock.txt` is clean and was not written by this run.

Fixed in `install-chap.sh`: both uses go through one `freeze()` helper that sets `NO_COLOR`
and strips any escapes that survive. Verified by running the comparison against the live
`chapenv` with `FORCE_COLOR=3` and `CLICOLOR_FORCE=1` deliberately set — *matches
environment/lock.txt exactly (174 packages)*.

## Both halves reproduce, and the reference does not

The strongest result here, and it is stronger than batch 25's because it covers the year that
had never been run from cold. Per model and per combination, from
`26-09-03_cleanroomHoldoutReproduction.json`:

| model | development identical | moved | holdout identical | moved |
|---|---|---|---|---|
| persistence | 32 | **0** | 32 | **0** |
| climatology | 32 | **0** | 32 | **0** |
| ensemble (the reported model) | 27 | **0** | 27 | **0** |
| hier_nb | 4 | **0** | 4 | **0** |
| boosted | 1 | **0** | 1 | **0** |
| **reference** (unseeded) | 0 | **32** | 0 | **32** |

**192 model-combination scores from models this project wrote, and not one moved by a bit.**
The reference moved in every combination on both halves.

On the two reported paths, everything that moved is downstream of the reference and nothing
else:

| | archived | clean-room | moved by |
|---|---|---|---|
| **development** ensemble CRPS | 18.816872064690028 | 18.816872064690028 | **identical** |
| development reference CRPS | 22.098446493261456 | 22.255807673854445 | +0.157361 |
| development skill | 0.14849796928359138 | 0.15451857149198822 | +0.006021 |
| **holdout** ensemble CRPS | 76.73108261979166 | 76.73108261979166 | **identical** |
| holdout reference CRPS | 84.02620178776041 | 83.79891141666666 | −0.227290 |
| holdout skill | 0.08681957547474661 | 0.08434272805445153 | −0.002477 |

`beats_reference` and `beats_all_baselines` are unchanged on both.

Of 4 329 tracked files, **2 224 came back identical**, 2 105 differ and 5 are untracked.
More files differ than in batch 25's run (848) because phase E ran, which touches every
combination a second time.

## Phase E, opened from cold

The half that had never been checked. From `holdout_distribution.json`, archived beside the
clean-room's:

| field | archived | clean-room | |
|---|---|---|---|
| CRPS of the reported model | 76.73108261979166 | 76.73108261979166 | **identical** |
| beats the reference | 26 of 32 | 26 of 32 | **identical** |
| beats both required baselines | 27 of 32 | 27 of 32 | **identical** |
| rows inside the reference noise band | 17 | 17 | **identical** |
| forks above the band | 5 | 5 | **identical**, and the same five by name |
| skill score | 0.086820 | 0.084343 | −0.002477 |
| reference CRPS | 84.026202 | 83.798911 | −0.227290 |
| reference noise band | 0.014023 | 0.013410 | −0.000613 |
| rank within the distribution | 18 of 32 | 16 of 32 | 2 places |

The five forks above the band are `02_setup/02_trainingWindow`, `02_setup/03_provinces`,
`03_models/03_candidate`, `03_models/03_candidate/a_hierNB/02_covariates` and
`04_score/02_aggregate` — the same list on both runs.

**The holdout's noise band is far steadier than the development one.** 0.014023 against
0.013410, a 4 % difference, where the development band moved by a factor of two between
batch 15 and batch 25. Whatever the right treatment of the development band turns out to be,
the phase-E figure it is measured against is not the unstable part.

## The development band, on a third draw

Batch 25 raised the development band as a question for the human. This run is a third
independent draw of it and does not settle it:

| | batch 15 (archived) | batch 25 | batch 27 |
|---|---|---|---|
| skill band (max − min over four repeats) | 0.021778 | 0.043084 | **0.034944** |
| forks moving more than the band, of 17 | **6** | **3** | **3** |
| which ones | +3 more | family, weighting, aggregate | family, weighting, aggregate |

Three draws, three values spanning a factor of two, and a headline count that reads 6 or 3
depending which. The **identity** of the forks that clear the band is stable — `family`,
`weighting` and `aggregate` on every draw — while the count is not. That is a sharper way to
state the finding than the count is, and it is the human's question to settle.

## Batch 26 and batch 24, both exercised from cold

Batch 26's mechanism met exactly the conditions that defeated its predecessor.

`manifest_selection_check.json`, written after tier 1 re-ran:

- the tier-1 order **would** have moved four positions — `provinces_reportingOnly` 5→6,
  `popColumn_backCast` 6→5, `provinces_mergeVientiane` 7→8, `retrain_everySplit` 8→7;
- the tier-2 rule **would** have chosen **six different pairs**;
- verdict: *the rule would now choose 6 different pair(s); the recorded ones stand.*

Both were reported and neither was acted on. `manifest.csv` carries the recorded eight pairs
and the run went on to tier 2. This is batch 25's failure, arriving a third time on a third
draw of the reference, and passing through.

`holdout_freeze_check.json`, immediately after: *the frozen set is intact*. 33 rows,
`manifest_holdout.csv` still `fc9d1a16…`, no fatal differences, no unpaired development rows,
and **32 rows whose numbers drifted, recorded and not absorbed.**

**`manifest.csv` is not byte-identical from a cold checkout**, and cannot be. All 32 rows
differ, in the two cost columns only — `est_seconds_dev` and `est_seconds_holdout` are
measured wall-clock durations summed from each model's `run_cost.json`. Rank order, names,
node paths, skill values, statuses and all eight pairs are identical. Batch 26's report says
these files come back byte-identical; that was true of the tree it was tested in, where the
timings were not re-measured.

## Why the run stopped

`analysis/scripts/conclude.py` and everything before it succeeded. The failure is in
`analysis/05_stability/scripts/pair_holdout_development.py`, the last script in the tree,
which produces the phase-E comparison:

> the development half has moved since the phase-E set was frozen … **The pairing this
> compares on is no longer the pairing that was frozen.**

The script takes each holdout row's development figure from the **frozen**
`manifest_holdout.csv` — which is correct, and is what the comparison is built on. Separately
it asserts that each frozen figure still equals what `conclusions.csv` says **today**, to
`1e-9`, a tolerance its own comment describes as "not a tolerance for drift: it is float
formatting through a CSV".

**That assertion cannot hold on any tree whose development half has been re-run**, because
the development skill score divides by the unseeded reference. It passes only on a tree that
has not been re-run since the freeze — that is, only where it is not needed.

Two facts about what it stopped on, from
`26-09-03_cleanroomHoldoutReproduction.json`:

- **32 rows drifted; 0 rows had their pairing move.** Every frozen row still has a
  development twin of the same name, and `manifest_holdout.csv` is byte-identical to the
  archive's. The message's claim that the pairing has changed is not what the data shows.
- **Every drift is inside the noise band this run measured for itself.** The largest is
  −0.025673 (`provinces_reportingOnly__weighting_crpsWeighted`, frozen 0.046500, today
  0.020827) against a band of 0.034944.

And the tree contradicts itself about it. `holdout_freeze_check.json`, written minutes
earlier by batch 24's machinery, reports the *same* drift on the *same* 32 rows under the
heading `drift_under_an_unchanged_set` and calls the verdict **the frozen set is intact**.
One script reports the drift by design; the next treats it as fatal.

This is the third member of a family: batch 24 found a frozen artefact recomputed at run
time, batch 26 found a recorded selection re-derived at run time, and this is a recorded
figure re-asserted against a recomputed one. The fix has the same shape as the other two —
report the drift, do not die on it — and it is left to batch 30 rather than made here, for
the reason batch 25 gave when it found batch 26's defect: the change alters what a node
produces, it needs a defence of its own, and a batch that is blocked stops.

## Five files the archive does not have

The clean-room produced 5 untracked files: `member_selection.json` under
`03_models/03_candidate/c_ensemble/results/` for `popColumn_backCast`,
`provinces_mergeVientiane`, `provinces_reportingOnly`, `retrain_everySplit` and
`trainingWindow_from2004`. The archive has 45 of these files; the clean-room wrote 50.

They are not gitignored. Those five setup combinations were last run before the shared
assembler was lifted in batch 14, and have not been re-run since, so the archive simply never
received a file the current `run_ensemble.py` writes. Nothing computed differs — it is a
record that was never written rather than a value that moved. One copy is preserved in the
artefacts.

## What this run does not establish

- **That `analysis/run.sh` runs to completion from a clean checkout.** It does not; it exits 1
  at the last script. Batch 19 must not claim otherwise until a run gets past it.
- **`holdout_vs_development.csv`, `holdout_vs_development.json` and
  `fork_sensitivity_both.csv` were not regenerated**, because the script that writes them is
  the one that stopped. They are the clone's committed copies and are unverified from cold,
  exactly as batch 25's holdout half was. The comparison reports them as unchanged and that
  reading would be wrong.

## Files

- `26-09-03_cleanroom_comparison.json` — `cleanroom_compare.py`: the file classification and
  the two reported conclusions.
- `26-09-03_cleanroomTier2Drift.json` — `cleanroom_tier2_drift.py`: the development-half
  per-model table, the tier-2 selection both ways, the band.
- `26-09-03_cleanroomHoldoutReproduction.json` — `cleanroom_holdout_reproduction.py`, new in
  this batch: both halves per model, the phase-E headline archived beside the clean-room's,
  the environment question, and the rows the run stopped on.
- `26-09-03_cleanroom-artefacts/` — what the run wrote, copied out before the 18 GB clone was
  discarded, with a README.
