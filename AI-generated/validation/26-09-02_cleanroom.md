# Clean-room check — 2026-09-02, batch 25

`/validate cleanroom`, run to finish what batch 18 could not: build the environment from
nothing, run the analysis, and **report the differences** rather than announcing success.

**It did not reach the end, and this time that is a finding rather than an interruption.**
`analysis/run.sh` ran for **3 h 48 m (13 669 s)** and **exited 1** at the freeze check, with
the whole development half behind it and the phase-E half still ahead. It stopped because
the check batch 24 built refused to let it continue, and the check was right.

The short statement of what this run establishes:

- **Every model this project wrote reproduced its CRPS exactly**, in every combination it
  appears in — not just on the reported main path, which is as far as batch 18 got.
- **The development manifest cannot be re-derived from a clean checkout.** Its tier-2
  selection is computed at run time from skill scores that divide by an unseeded model, and
  a second draw selects **six of eight pairs differently**.
- **The noise band that phase D's headline is measured against nearly doubled**, and the
  headline count went from **six of seventeen forks to three**.

## How it was run

`git clone` of the repository at `ae0f62d` into a scratch directory, `environment/chapenv`
built from `environment/lock.txt`, then `bash analysis/run.sh` from cold, on the host, with
Docker available so the containerised reference model can run. The harness is
`AI-internal/useful-scripts/run_cleanroom.sh` and the comparison `cleanroom_compare.py`, both
unchanged from batch 18 and verified by digest before the run, so this is the same check and
not a new one.

**The comparison is git's.** The clone's index is the archived result, so after the run every
difference is a modified tracked file. Of **4 306 tracked files, 3 458 came back identical**,
848 differ and 93 are untracked.

The run was launched detached from the session that started it. Batch 18's clean-room died
because its session was cut off, and an unfinished check is the one failure mode this batch
existed to remove.

## What the environment did

`environment/install-chap.sh` built `chapenv` from the lockfile and reported **"matches
environment/lock.txt exactly (174 packages)"**, giving `chap 2.1.0` on CPython 3.13.0 — the
second independent confirmation of the mechanism batch 7 repaired.

## Every model this project wrote reproduces; the reference does not

The strongest result here, and it is stronger than batch 18's because it covers the whole
development set rather than the main path alone. Per combination and per model, from
`26-09-02_cleanroomTier2Drift.json`:

| model | combinations identical | combinations moved |
|---|---|---|
| persistence | 32 | **0** |
| climatology | 32 | **0** |
| ensemble (the reported model) | 27 | **0** |
| hier_nb | 4 | **0** |
| boosted | 1 | **0** |
| **reference** (unseeded) | 6 | **26** |

**Ninety-six model-combination scores, and not one of ours moved by a bit.** The six
combinations where the reference is identical are the ones that inherit it rather than
re-run it.

On the reported main path the reference moved from **22.098446493261456** to
**22.383841657008084** (+0.285 CRPS), and everything downstream moved because of that and
nothing else:

| | archived | clean-room | moved by |
|---|---|---|---|
| ensemble mean CRPS | 18.816872064690028 | 18.816872064690028 | **identical** |
| reference mean CRPS | 22.098446493261456 | 22.383841657008084 | +0.285 |
| skill score | +0.14849796928359138 | +0.15935466516317520 | **+0.0109** |
| resolvable difference floor | 0.565277280323451 | 1.1673769919137462 | **+0.602** |

`beats_reference` and `beats_all_baselines` remain true. The reported conclusion reproduces
in the only sense available to it: the part that can be identical is identical, and the part
that cannot is the external model the conclusion divides by.

## Why the run stopped: a frozen set with an unreproducible derivation

`analysis/05_stability/results/manifest.csv` is re-derived from the tree on every run, by
design — `/validate invariants`'s `combos` check requires it to match the tree. Twenty-four
of its rows are tier 1, planned from the tree alone. The other eight are **tier 2**, and they
are not planned from the tree. They are **selected from tier 1's own results** by
`tier2_rule.md`: rank every tier-1 row by how far its skill score sits from the main path's,
take the top two `setup` rows, the top two model rows and the top `scoring` row, and pair the
groups.

**Skill score divides by the unseeded reference.** So the ranking that selects tier 2 is a
ranking of numbers that do not reproduce, and on this run it selected differently:

| group | archived selection | clean-room selection |
|---|---|---|
| S (setup) | `provinces_reportingOnly`, **`provinces_mergeVientiane`** | `provinces_reportingOnly`, **`trainingWindow_from2004`** |
| M (model) | `family_hierNB`, `weighting_crpsWeighted` | `family_hierNB`, `weighting_crpsWeighted` — unchanged |
| A (scoring) | **`aggregate_caseWeighted`** | **`aggregate_populationWeighted`** |

Two of the five selected rows changed, and because the groups are paired, **six of the eight
tier-2 pairs changed**.

**The margins say this was never stable.** The rule's own deciding margin is how far the last
row admitted to a group sits above the first row excluded:

| group | archived margin | flipped? |
|---|---|---|
| S | **0.001002** | yes |
| A | **0.003211** | yes |
| M | 0.093547 | no |

The reference's own noise band on this run is **0.043084** of skill. Group S was decided by a
margin **one forty-third** of that band and group A by one thirteenth; both flipped. Group M
was decided by a margin **twice the band**, and it did not. The selection is reproducible
exactly where it was decided by a real difference, and a coin toss everywhere else.

The freeze check then did what batch 24 built it to do. `manifest_holdout.csv` is intact —
33 rows, hashing to `fc9d1a16…` as `holdout_freeze.json` records — and the script **refused
to rewrite it**, reporting `9 difference(s) the frozen set cannot absorb`: six frozen rows
the tree no longer carries, and three whose `rank` moved. `set -e` did the rest.

**This is the check working, not failing.** Under the version batch 24 replaced, this run
would have silently rewritten the frozen phase-E pairing with the clean room's own re-drawn
numbers — which batch 24 named as the scenario batch 25 would hit, and it hit it.

## What the frozen set is, and what it is not

Worth stating precisely, because it is easy to read this as worse than it is.

**The phase-E results are not in question.** `manifest_holdout.csv` was frozen in batch 15,
committed before 2010 was opened, and batch 16 ran exactly it. That the *set* was recorded is
what §3 requires, and it was.

**What is not reproducible is the derivation of that set.** The record says these eight pairs
were chosen by a rule from tier 1's conclusions; a reader who re-runs the analysis gets a
different eight and cannot arrive at the frozen set from the inputs. The eight pairs are a
*decision*, correctly recorded, and the project has been treating them as a *derivation*. It
is the same distinction batch 24 drew for `frozen_on` and for the manifest itself: **a value
that records history must not be derived at run time, because a derivation is a claim about
the present.** Batch 24 fixed that for the holdout manifest and left it standing one file
away, in the development manifest the holdout manifest is derived from.

## The band is a random variable, and this run shows what that costs

Batch 18 noted the resolvable-difference floor moved 0.565 → 0.449 between two samples and
warned that the project quotes it as a constant. This run makes the point sharper, because
the same statistic now runs the other way and further:

| | archived | clean-room |
|---|---|---|
| skill against the four repeats | 0.1376, 0.1415, 0.1551, 0.1594 | 0.1448, 0.1512, 0.1521, 0.1879 |
| **skill band** (max − min) | **0.021778** | **0.043084** |
| CRPS floor | 0.565 | 1.167 |
| **forks moving more than the band** | **6 of 17** | **3 of 17** |

The band is a **max minus a min over four draws**, which is about the least stable statistic
that could have been chosen for the job. One high draw (0.1879) doubled it.

And the consequence lands on phase D's headline. Three forks crossed from above the band to
below it — `analysis/02_setup/02_trainingWindow`, `analysis/02_setup/03_provinces`,
`analysis/03_models/01_baselines/01_persistence` — and **not one of them moved.** Their
largest effects are 0.021875 → 0.037047, 0.037553 → 0.041809 and 0.027933 → 0.027576. The
yardstick moved.

So the sentence *"six of the seventeen judgment calls move the conclusion further than the
reference model moves on its own, and eleven do not"* — batch 15's headline, carried into
`readme-at-start.md` and the claim collection — **reads "three and fourteen" on a second draw
of the same unseeded model.** The three that survive are `family`, `weighting` and
`aggregate`, and those three are well clear of the band on both draws.

## The row that crashed, and what it says about the pairs that did not

The drifted selection ran seven of its eight pairs and **crashed on the eighth**,
`trainingWindow_from2004__weighting_crpsWeighted`, at `check_pool.py`:

```
validation = fitted["weighting"]["validation"]
KeyError: 'validation'
```

The pipeline was right and the check was wrong. `run_ensemble.py` has a deliberate fallback,
and it fired and recorded itself:

> `"fell_back": true`, `"fell_back_because": "holding back 12 months would leave 36 to refit
> the members on, below the 60 this model requires"`, `"method": "equal"`

With the training window starting in 2004 there is not enough history to hold back a
validation block, so the CRPS-weighted pool correctly becomes an equally-weighted one.
`check_pool.py` then branches on the **configured** choice, `stage["choice"] ==
"b_crpsWeighted"`, rather than on what the weighting actually did, and reaches for a
validation block that was never written. This is the fork-blindness family batch 14 found
four times: a script keyed on the configuration instead of the outcome.

Two things follow, and the second is the more interesting.

**The defect was unreachable until the selection drifted.** It sits in a combination the
archived tier 2 never chose, and one run of a differently-drawn ranking found it.

**That pair is degenerate anyway.** `trainingWindow_from2004__weighting_crpsWeighted` is
supposed to perturb the weighting fork under a shortened training window, and under that
window the weighting fork **cannot take effect** — the crps-weighted child silently becomes
the equal-weighted one. Had it run, it would have been a duplicate of the training-window row
wearing another row's name. That is a property of the pair, not of this run, and it is worth
knowing about a selection rule that can choose it.

## What is verified, and what is still not

**Verified from cold, and new here:**

- the environment builds from the lockfile and matches it exactly;
- all 32 development analyses run, and 31 produce a conclusion;
- every model this project wrote returns identical CRPS in every combination;
- the reported development conclusion, to within the unseeded reference's own re-draw;
- batch 24's freeze defence, exercised in anger for the first time.

**Still not verified, and now for a stated reason rather than an interruption:**

- **The phase-E half has still never run from a clean checkout.** Batch 18 could not reach it
  because the seal sealed clones; this run could not reach it because the run aborts before
  it. The holdout figures in `26-09-02_cleanroom_comparison.json` show `main__holdout` as
  unchanged, and that means **nothing** — those files are the clone's committed copies,
  untouched. Read them as absent, not as reproduced.
- **`analysis/run.sh` does not currently run to completion from a clean checkout**, which is
  `readme-at-start.md`'s first "what has to stay true" and is the property `/release` would
  claim.
- The archive is still not quite what `run.sh` produces: the five `member_selection.json`
  files batch 18 predicted are confirmed missing from the archive and written by the run.

**`/release` must not claim that `analysis/run.sh` reproduces this analysis from nothing.**
It reproduces the development half and stops. That is the honest statement until the
development manifest stops being re-derived.

## Files

| file | what it holds |
|---|---|
| `26-09-02_cleanroom_comparison.json` | the file-by-file comparison and the `conclusion.json` diff, by `cleanroom_compare.py` |
| `26-09-02_cleanroomTier2Drift.json` | the per-model reproduction table, the tier-2 selection both ways with its deciding margins, and the band, by `cleanroom_tier2_drift.py` |
| `26-09-02_cleanroom-artefacts/` | what the run itself wrote, copied out of the clone before it was discarded |
| `AI-internal/useful-scripts/run_cleanroom.sh` | the harness — unchanged from batch 18 |
| `AI-internal/useful-scripts/cleanroom_compare.py` | the comparison — unchanged from batch 18 |
| `AI-internal/useful-scripts/cleanroom_tier2_drift.py` | why the run stopped; new in this batch |
