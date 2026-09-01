# Clean-room check — 2026-09-01, batch 18

`/validate cleanroom`: build the environment from nothing, run the analysis, and **report the
differences** rather than announcing success.

The first clean-room run since the tree grew a stability node and a phase E, and the first
that could reach the reference model at all — batch 7's ran inside a container and could
not, because the reference is distributed as a container itself.

**This run was interrupted and did not finish.** It reached the whole of the reported main
path and 8 of the 32 stability rows before the session that started it was cut off. What it
established up to that point is below, and what remains unverified is stated as plainly:
completing it is **batch 25**. An interrupted check that reports itself as complete would be
worth less than no check.

## How it was run, and why not in a container

A `git clone` of the repository at `ad7e64f` into a scratch directory, the analysis
environment built from `environment/lock.txt`, then `bash analysis/run.sh` from cold.

**The comparison is git's.** The clone's index is the archived result, so after the run every
difference is a modified tracked file and `git status` is the difference report. There is no
second copy of the results to keep in step, and nothing to decide about what to compare
against.

Batch 7 ran the check inside `environment/Dockerfile` and recorded that the reference model
could not run there, because it starts a container of its own and there is no daemon inside
one. Since the reported conclusion is a **ratio to that model**, a container-only clean-room
can never reproduce it. This one therefore runs on the host with Docker available, and pays
for it by not proving that the analysis is independent of the host — the two checks verify
different halves, and `environment/Dockerfile` still builds.

The harness is `AI-internal/useful-scripts/run_cleanroom.sh` and the comparison
`cleanroom_compare.py`; both are versioned so the next run is the same run.

## What the environment did

`environment/install-chap.sh` built `chapenv` from the lockfile and reported **"matches
environment/lock.txt exactly (174 packages)"**, giving `chap 2.1.0` on CPython 3.13.0. This
is the mechanism batch 7 had to repair — the installer used to resolve afresh and *write*
the lockfile rather than install from it — and it has now been exercised on a machine with
no prior state.

## The seal, which is why this check earned its cost before it ran

**A fresh clone skipped all 32 phase-E rows.** The seal that plan §3 requires rested on
`results/run_status_holdout.csv`, which is versioned — so it shipped with every copy of the
repository and sealed copies that had never opened the year. `collect_conclusions.py
--dataset holdout` then re-read the committed conclusions and the phase-E half of
`analysis/run.sh` reproduced `holdout_distribution.json` **byte-identically while running
none of the analysis behind it**. A false reproduction indistinguishable from a true one.

`run_manifest.py`'s docstring, `05_stability/run.sh` and `readme-at-start.md` all asserted
the opposite in so many words — *"From a clean checkout that file does not exist and the
whole set runs"*. Only an actual clean run could tell the two apart.

The seal now takes two conditions and needs both: the row recorded as `ran` in the versioned
status file, so forcing a re-run by deleting a row still shows in git; and a gitignored
`.holdout_opened` at the stability node's root, so the flag says whether *this working tree*
opened the year. Verified in both directions before this run started, and this run's own log
records `no .holdout_opened: the seal releases, phase E will run`.

## The differences, on what completed

Of **4 284 tracked files, 3 994 came back byte-identical**. Everything under `01_data` and
`02_setup` reproduced exactly, as it did in batch 7.

### Our models reproduce to the last digit; the reference cannot

This is the whole finding of the run, and it is clean.

| model | archived mean CRPS | clean-room | |
|---|---|---|---|
| persistence | 24.879338288409706 | 24.879338288409706 | identical |
| climatology | 24.336908636118597 | 24.336908636118597 | identical |
| **ensemble** (reported) | **18.816872064690028** | **18.816872064690028** | **identical** |
| reference (mean of 4) | 22.098446493261456 | 22.269520428571430 | **+0.171074** |

Every model this project wrote reproduced its mean CRPS exactly, on a fresh clone, a freshly
built environment and no prior state — which is what the determinism checks claimed and this
is the independent confirmation of it. Sixteen of the twenty-six fields in
`conclusion.json` are unchanged, including `crps_ours`, both of our coverage figures, the
cell and location counts and every boolean.

The reference model is **unseeded**, and its four repeats went from
{21.917, 22.272, 22.385, 21.820} to {22.436, 22.473, 22.024, 22.145}. Everything that moved
in `conclusion.json` moved because of that and nothing else.

### What that does to the reported conclusion

| | archived | clean-room | moved by |
|---|---|---|---|
| skill score | +0.14849796928359138 | +0.15503918797693150 | **+0.0065** |
| paired mean difference | −3.281574428571429 | −3.452648363881401 | −0.171 CRPS |
| resolvable difference floor | 0.565277280323451 | 0.449080592991914 | −0.116 CRPS |

**The reported conclusion reproduces to within 0.0065 of skill, and the 0.171 CRPS behind
that is a quarter of the floor below which this project already declines to attribute
anything to a model.** `beats_reference` and `beats_all_baselines` are both still true. The
answer to "does this reproduce" is therefore yes, in the only sense available: the part that
can be identical is identical, and the part that cannot is inside the noise band the project
measured for exactly this purpose.

It is worth saying what the third row means, because it is easy to miss. **The noise floor is
itself a random variable.** 0.565 was one draw of the largest paired difference between two
repeats of an unseeded model; this run drew 0.449. Every statement of the form "nothing below
0.57 CRPS can be attributed to a model" is a statement about one sample of four repeats, and
a second sample of four moved it by 0.12.

### A file the archive does not have

The clean-room produced **four `member_selection.json` files that are untracked** — the
repository has that file for 45 of `c_ensemble`'s 51 combinations and not for
`popColumn_backCast`, `provinces_mergeVientiane`, `provinces_reportingOnly`,
`trainingWindow_from2004`, `retrain_everySplit` or the never-run `family_ensemble`.

Those five are batch 13's `02_setup` rows, run before `prepare_members.py` was given the fix
that writes it. So **five reported combinations carry results produced by a version of the
pipeline that did not write one of its current outputs**, and re-running the analysis today
produces artefacts the archive lacks. Nothing about their *scores* is in question — those
files record which member each pool selected, not what it scored. But "the archive is what
`run.sh` produces" is not quite true, and only a clean run says so. Folded into batch 25.

### The 290 files that differ, and why most of it is not a difference

The remaining differences are `eval.nc`, `eval*.log` and `run_cost.json` under every model,
for every combination the run reached. NetCDF carries creation metadata, the logs carry
absolute paths and per-split timings, and `run_cost.json` is a duration. **None of these is a
score**, and every score derived from them — `metrics_cell.csv`, `metrics_summary.csv`,
`crps_by_location.csv` — is identical wherever the model is one of ours.

This is a weakness in what the comparison can say cheaply, not a finding: a byte comparison
of a NetCDF file cannot distinguish a changed forecast from a changed timestamp, so the
derived CSVs are what carry the answer. Recorded so the next run does not rediscover it.

## What is not verified, and is batch 25's

The run reached 8 of the 32 development rows — `main`, both scoring rows, and five of the
`02_setup` rows — and never reached tier 2 or the phase-E half at all. So:

- **The distribution of 32 analyses is not verified from cold**, on either dataset.
- **The phase-E half has never been run from a clean checkout at all.** The seal defect above
  is why: until this batch, it could not be. The fix is verified to *release* the seal — the
  driver plans all 32 rows in a fresh clone — but the rows themselves have not been executed
  there.
- `analysis/run.sh`'s six-hour end-to-end claim is unverified past the first ninety minutes.

That is the honest state, and it means **`readme-at-start.md`'s "what has to stay true" #1 is
currently supported for the reported result and not for the two distributions around it.**
Batch 25 runs the check to completion; `/release` in batch 19 must not claim more than this
document supports until it has.

## Files

| file | what it holds |
|---|---|
| `26-09-01_cleanroom_comparison.json` | every figure quoted above, written by `cleanroom_compare.py` |
| `AI-internal/useful-scripts/run_cleanroom.sh` | the harness: clone, build, run, diff |
| `AI-internal/useful-scripts/cleanroom_compare.py` | the comparison, and the file it writes |
