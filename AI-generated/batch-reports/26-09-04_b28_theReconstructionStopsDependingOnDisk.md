# Batch 28 — the pool's second path stops depending on what is on disk

Generated from [[26-08-22_dengueForecastingCase]] — iteration 28

**State: done — produced.** `check_pool.py` matched each pool member to a stored evaluation
by globbing sibling result directories and taking the first hit, so **which** evaluation it
named — and **whether it found one at all** — recorded the order in which batches happened to
run. The tie-break is now a rule over the combination names, and the last step of
`05_stability/run.sh` settles every pool row once the whole manifest has run, which is the
first moment at which a member's own separate evaluation exists.

**The headline holdout row's reconstruction is done, and it agrees.** Its archived copy said
the reconstruction was impossible. Rebuilt from its members' own stored evaluations of 2010
the pool scores **76.646 against the 76.731 it scored**, a residual of **0.085** over 192
cells — the same relative size as the 0.016 over 371 development cells. **The pool beats its
best member on the held-out year by 4.767 CRPS**, and the prediction registered before any of
it ran is false in both of its halves there, where on development one half held.

**Nothing computed moved.** All 51 `pool_check.json` files were rewritten: 43 changed in the
name of an evaluation and in one added field, four gained the reconstruction they had been
run too early to have, four gained a member match. **No number that existed before is
different, no row lost anything, and every `mean_crps_as_run` is unchanged** — computed key
by key against `HEAD`'s own copies, not read off a diff.

---

## 1. The defect, stated against the data

`matching_evaluation` pairs each member of the pool with a stored evaluation of that member
run **on its own**, through its own node — the file that makes the reconstruction a second
path rather than a restatement of the pool's own forecast. It matched on the member's
`configuration_sha256`, the dataset's hash and the backtest flags, which is right and is
unchanged: a member evaluated under a different configuration is a different model.

Those three fields usually admit **more than one** run. The same model, on the same data,
sits under every combination that left it alone. The script globbed them and took `found[0]`:

| | archived | today, unmodified |
|---|---|---|
| `main`, the persistence member | `main` | `climatology_frozenWindow` |
| `main__holdout`, `mean_crps_rebuilt` | `null` | **76.646** |
| `main__holdout`, `not_done_because` | *"no stored evaluation of ['hier_nb', 'boosted']"* | `null` |

Both lines are the same defect at two strengths. The first is a name; the second is whether
the check happened at all. Batch 16 ran the holdout's main row before the holdout's family
rows, so at that moment candidate 1 and candidate 2 had no separate evaluation on 2010 — and
the file recorded that as a property of the pool.

**It is not a property of the pool. It is a property of the clock.** Batch 26 found it while
fixing something else, verified it pre-dated that batch by re-running `HEAD`'s own copy, and
left it here rather than repairing the tie-break in passing.

## 2. Why a tie-break alone would not have been enough

The rule had to answer a second question the first one hides: **when** a member's separate
evaluation exists.

Our two candidate families are evaluated on their own only under the family fork's own
combination — `family_hierNB`, `family_boosted` — because the main path runs the pool. Those
are **stability rows**. So on a run of `analysis/run.sh` from nothing, the main path's pool is
checked in `03_models`, hours before `05_stability` produces the runs it needs. A rule that is
deterministic given a set of directories still gives a different answer from a cold checkout
than from this repository, where every directory exists. Batch 31's clean-room run shows it
happening: 13 `pool_check.json` files came back changed, `main` among them.

So the repair is in two parts, and needs both.

## 3. The rule

`check_pool.py` now names, among the evaluations that match on configuration, dataset and
flags:

1. **this combination's own run of the member**, where there is one;
2. otherwise the run that **moved the fewest forks among the combinations this one implies**,
   ties broken by name.

"Implies" is `combos.implies`, added beside the `__holdout` suffix in
`analysis/scripts/lib/combos.py`, which is where a combination's name is read and now also
where it is split into the forks it moved: every fork the candidate moves is one this
combination moves too, **family tokens aside**, on the same dataset. The exception for the
family fork is the whole reason a lookup is needed at all.

Fewest forks is the member's own canonical run — `main` for a baseline the pool did not
perturb, `family_hierNB` for candidate 1, `provinces_reportingOnly__holdout` for a baseline
under a combination that moved the province filter and the weighting. Both clauses are
functions of two names, so the answer does not move when an unrelated combination is run, and
each file records which clause chose it in a `chosen_by` field beside the evaluation.

**What is deliberately not recorded in those files is the list of candidates the rule chose
from.** That list *is* a function of what is on disk, and writing it into 51 artefacts would
have put the dependence straight back into the files this change exists to free of it. It is
written once, after every row has run, into `05_stability/results/pool_reconstruction.json`.

## 4. The second part: settling every row once the set has run

`05_stability/scripts/reconstruct_pools.py` is the last step of that node's `run.sh`. For
every combination with a pool it asks `check_pool`'s **own** rule — imported, never restated —
which evaluations should be named, and where the file on disk names others it re-runs
`check_pool.py` as a subprocess with `COMBO` set, exactly as `c_ensemble/run.sh` runs it.

It is the shape this node already has twice. `plan_manifest.py` and `collect_conclusions.py`
each appear twice in the same `run.sh`, because a first pass cannot know what has not run
yet; this is a third instance of the same argument, one node further out.

**It costs nothing when nothing has moved.** The first invocation rewrote 49 files in 2 min
28 s. The second rewrote none, took 1.2 s, and returned a byte-identical
`pool_reconstruction.json`.

## 5. What the rewrite changed, measured

`AI-internal/useful-scripts/pool_check_rewrite.py` flattens both versions of every file to
their leaves and classifies each differing key. → `26-09-04_poolCheckRewrite.json`.

| | |
|---|---|
| files | 51 |
| changed in the name of an evaluation and the added field only | **43** |
| gained the full reconstruction | **4** |
| gained a member match, still short of a reconstruction | 4 |
| **numeric changes to values that existed before** | **0** |
| rows that lost anything | 0 |

The four that gained a reconstruction are all held-out rows, and all four are rows batch 16
ran before the family rows existed:

| combination | as run | rebuilt | residual |
|---|---|---|---|
| `main__holdout` | 76.731 | 76.646 | −0.085 |
| `climatology_frozenWindow__holdout` | 76.731 | 76.646 | −0.085 |
| `persistence_negBinomialFloor__holdout` | 77.504 | 77.414 | −0.090 |
| `weighting_crpsWeighted__holdout` | 77.746 | 77.610 | −0.136 |

The first two rows are identical to the digit, as their leaderboard rows already were: the
climatology construction fork changes nothing on the held-out year, where both rows score
76.73108261979166 and skill +0.08681957547474661. The reconstruction agreeing with that is a
cross-check on the rule and not a new finding, and this record does not offer a cause for the
fork's two constructions coinciding on the phase-E backtest, because nothing here measured
one.

The four that gained a member match are the province-filter rows, where candidate 1's
separate run exists under `provinces_*__family_hierNB` and candidate 2's does not: their
`members_without_a_matching_stored_evaluation` goes from two names to one, and the
reconstruction is still not done.

### The sweep, put to the states it exists for

This repository is not in the state the sweep is built for — every combination has run here —
so the states are made, one file at a time, and restored after each
(`26-09-04_reconstructionSweepDefence.json`):

| state | what should happen | |
|---|---|---|
| the record batch 16 left on `main__holdout`, restored from `96f1205` | rewritten to 76.646 | pass |
| a file that is already right | not re-run, not touched | pass |
| a file that is missing entirely | produced, same reconstruction | pass |
| `covariates_rich`, which no order of execution could reconstruct | left saying so, still naming candidate 1 as the member it lacks | pass |

Every file ends at its committed digest and `analysis/` is left clean by git's own account,
which the check verifies and exits non-zero without.

## 6. What the headline holdout row now says

| | development | held-out year |
|---|---|---|
| pool, as run | 18.817 | 76.731 |
| pool, rebuilt from the members' own evaluations | 18.801 | **76.646** |
| residual | −0.016 | **−0.085** |
| cells | 371 | 192 |
| best member | candidate 2, 20.771 | climatology, **81.498** |
| pool beats its best member by | 1.954 | **4.767** |
| pool 10–90 coverage | 0.863 | 0.755 |
| largest member 10–90 coverage | 0.825 | **0.854** |

**The registered prediction fails on 2010 in both halves, where on development it failed in
one.** `01_weighting/a_equal` wrote down, before anything was fitted, that an equal pool with
half its mass on the two required baselines would score worse than its best member — false on
both datasets — and that its 10–90 coverage would be at least its largest member's, which held
on development and does not hold here. Pooling still widens against the mean of the members;
on this year the widest member is wider than the pool.

The holdout member scores are new to the record and worth reading beside the leaderboard:
climatology 81.498, candidate 2 81.679, candidate 1 84.707, **persistence 128.052**. The
required baseline that is worst by a factor of 1.6 carries a quarter of the reported model's
weight, and the pool still beats every member by 4.767 CRPS.

## 7. What can be reconstructed at all, and what cannot

**Eleven of the 51 pool rows. Forty cannot, and no order of execution would help.** A row
that moves a fork *inside* one of the members — the nine candidate-internal forks, the
population column, the training window — has no separate run of that member under the
configuration the pool gave it, because this tree evaluates a member on its own only under
the family fork's own combination. That is a property of the frozen manifest, and
`pool_reconstruction.json` names the rows and the reason, so the absence is a recorded
decision rather than a gap a reader has to infer.

Across the eleven the residual runs **0.016 to 0.136 CRPS**, largest on the held-out rows
where every score is about four times the size. It is the sampling error of the pool's own
allocation: the members' draws are the same draws, but the pool takes a seeded subsample of
each member's thousand and the reconstruction takes a different one.

Making the other forty reconstructable would mean evaluating each perturbed member on its own
as well — a second evaluation per candidate-internal row. That is not in the frozen manifest
and §3 does not allow adding to it, so it is recorded as the alternative not taken rather
than done.

## 8. Why this does not reopen the holdout

`readme-at-start.md`'s first non-negotiable, as the human clarified it on 2026-09-01, binds
`manifest_holdout.csv`: nothing added, dropped, re-tuned or re-run in the frozen set after a
holdout number has been seen. That file is untouched. No model was re-fitted, no evaluation
recomputed, no reported score moved, and the set is still 32. What ran is a **check**, over
evaluations produced in batch 16, that reads them and writes its own file — the standing this
project already gives a clean-room re-run of the whole phase-E half, which batches 25, 27 and
31 each performed. The reading is recorded in the plan's §4b rather than assumed, as batch 26
recorded its own.

## 9. What was decided, and by whom

| Decision | Agency |
|---|---|
| The headline holdout row's reconstruction is **done and reported**, not left saying it was impossible | agent-autonomous |
| The tie-break becomes a rule over combination names; `combos.implies` lives beside the `__holdout` suffix rather than at the node that first needed it | agent-autonomous |
| A sweep at `05_stability` settles every pool row once the whole set has run, because the rule alone is deterministic only given a set of directories | agent-autonomous |
| The list of candidate evaluations is **not** written into the 51 files, and is written once into `pool_reconstruction.json` | agent-autonomous |
| Re-running a check over the held-out year's stored evaluations does not touch §3, and the reading is written down | agent-autonomous, inside the human-set §3 |
| The forty rows that cannot be reconstructed stay that way, with the reason recorded, rather than the manifest growing a member evaluation per row | agent-autonomous, inside the human-set §3 |

## 10. What this batch says about the method

Batch 24 named the family: **a value that records history must not be derived at run time.**
Batch 26 added the second half: **a derivation over the filesystem is a claim about when it
ran.** This one adds the third, and it is the reason the fix needed two parts rather than one:

**Making the derivation deterministic is not the same as making it right.** The rule alone
would have been a function of the combination names and the tree — deterministic, auditable,
and still giving one answer from a cold checkout and another from this repository, because
what it ranges over is produced by the run it sits inside. A check that depends on its own
position in the run has to be moved to where its inputs exist, or it is not a check but a
report on progress.

And the thing itself is worth saying plainly. **For five batches the record said the second
path behind this project's headline held-out result could not be run.** Nothing looked wrong:
the file was written by a script, the reason it gave was true when it was written, and every
number in it was right. It took a re-run, in a different order, to see it.

## 11. Files

**Changed**

- `analysis/03_models/03_candidate/c_ensemble/scripts/check_pool.py` — the matcher is a rule;
  `stored_evaluations` split out so the sweep can use it; the docstring says where the
  reconstruction is settled and why; one scoring pass per member instead of two.
- `analysis/scripts/lib/combos.py` — `tokens()` and `implies()`.
- `analysis/05_stability/run.sh` — the sweep, last, with the reason.
- `analysis/03_models/03_candidate/c_ensemble/results/*/pool_check.json` — all 51.
- `analysis/03_models/03_candidate/c_ensemble/claim.md`, `analysis/05_stability/claim.md`,
  `analysis/05_stability/criticality.md`.
- `AI-generated/validation/README.md`, `provenance.md`.

**New**

- `analysis/05_stability/scripts/reconstruct_pools.py` and its provenance record.
- `analysis/05_stability/results/pool_reconstruction.json`.
- `AI-internal/useful-scripts/pool_check_rewrite.py` and
  `AI-generated/validation/26-09-04_poolCheckRewrite.json`.
- `AI-internal/useful-scripts/check_reconstruction_defence.py` and
  `AI-generated/validation/26-09-04_reconstructionSweepDefence.json`.
- Claims **C40** and **C41**.

**Provenance**: a section appended to `c_ensemble/provenance/check_pool.md`; a new record at
`05_stability/provenance/reconstruct_pools.md`; a section appended to
`AI-generated/validation/provenance.md`.

## 12. What is left

**Batch 20**, then **batch 19**. Nothing here changes either: no reported score moved, and the
two claims added are new statements about the held-out year rather than revisions of old ones.
