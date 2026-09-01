# The frozen phase-E set, made to defend itself

Batch 24. Not a `/validate` run: a check written for one defect, and kept because the thing
it checks is the artefact the whole holdout spread rests on.

Figures from `26-09-01_freezeDefence.json`, written by
`AI-internal/useful-scripts/check_freeze_defence.py`; the record is in `provenance.md`.

## What was wrong

The plan's §3 makes one file carry the honesty of the held-out year: `manifest_holdout.csv`
fixes *what* gets evaluated on 2010 before 2010 is opened, so that the spread reported from
it is a measurement rather than a selection.

`freeze_holdout_manifest.py`, which writes that file, is the last step of the development
half of `analysis/05_stability/run.sh`. So every run of `analysis/run.sh` re-derived the
frozen set from whatever the development manifest said at that moment. It came back
byte-identical because the tree had not changed — not because anything made it. Earlier in
the same block, `plan_manifest.py` re-derives the *development* manifest from the tree by
design, and the
development manifest may legitimately grow: §3 as clarified on 2026-09-01 binds the frozen
holdout manifest and nothing else, while `/validate invariants`'s `combos` check *requires*
every non-main child in the tree to have a development row. A fork child added after the
opening was therefore one run of `analysis/run.sh` away from entering the frozen set, with no
batch and no decision behind it. Batch 18's outsider check added one and watched thirty-three
rows become **thirty-four**.

## The two defences

**The script refuses.** If `manifest_holdout.csv` exists, it is authoritative: the set the
tree would produce now is derived and compared, neither it nor `holdout_freeze.json` is
written, and the comparison goes to `results/holdout_freeze_check.json`. A development row
with no frozen twin is reported as *unpaired* and never added; a frozen row the tree no
longer carries, or one whose structural columns moved, is fatal; a frozen row whose numbers
moved is recorded, because the reference model is unseeded and moves them on any re-run. If
the file is missing and the year has already been opened, the set is restored from git rather
than re-derived.

**The invariant checks the file**, whatever wrote it. `check_invariants.check_freeze`: the
frozen manifest must still hash to what `holdout_freeze.json` recorded for it, the row count
must agree, and — the claim `holdout_freeze.json`'s own `commit_note` makes and nothing
checked — **no file under `analysis/results/*__holdout/` may exist at the commit that added
the frozen set**. That commit is the entire evidence that the set predates the opening.

## What was put to them

Eleven situations, on throwaway copies built from the live files. Four of them corrupt the
frozen manifest, which is why none of them runs against the live tree.

| Scenario | What it is | Exit | Outcome |
|---|---|---|---|
| `intact` | this repository | 0 | 33 rows, nothing written to the frozen files |
| `added` | a fork child discovered after the opening | 0 | **33 rows**, one row reported unpaired |
| `dropped` | a frozen row the tree no longer carries | 1 | fatal; frozen file untouched |
| `restructured` | a frozen row's fork child renamed | 1 | fatal; frozen file untouched |
| `conclusion_drift` | a development conclusion that moved | 0 | reported; the frozen pairing stands |
| `missing_after_opening` | the frozen file deleted after the year was opened | 1 | refuses; says to restore it from git |
| `refreeze_from_cold` | the frozen file deleted with no trace of an opening | 0 | **byte-identical** to the manifest frozen in batch 15 |
| `invariant_intact` | this repository | — | no findings |
| `invariant_rewritten` | a frozen manifest that no longer matches its digest | — | 2 findings |
| `invariant_row_count` | a row count the record disagrees with | — | 1 finding |
| `invariant_late_freeze` | holdout results present at the commit that added the set | — | 1 finding |

All eleven behaved as specified.

Two carry the weight. **`added`** is batch 18's defect reproduced, and it is the one the fix
exists for. **`refreeze_from_cold`** is the regression test rather than a defence: the script
was restructured, and a refactor that changed the set would have changed the reported result,
so the freeze path was made to run from cold and its output compared byte for byte against
what batch 15 froze.

## What the superseded version did

The same eleven, run against the version this replaces: **six of the seven script scenarios
fail, and every one of them exits 0.** The frozen set grew to 34 rows, shrank to 32, was
rewritten with a renamed fork child, had its frozen development pairing replaced by drifted
numbers, and was re-derived from scratch after the year had been opened. Nothing printed a
warning in any of them.

The drift case is worth naming on its own, because batch 18 did not: under the superseded
script, a clean-room run of `analysis/run.sh` would have rewritten the *frozen* development
conclusions with the clean room's own re-drawn reference numbers — the pairing §3 exists to
fix, quietly refitted by the run that was supposed to verify it. Batch 25 is that run.

## A second hole, closed by the same change

`holdout_freeze.json` records `frozen_on`, and it was written from `date.today()` on every
invocation. Batch 16 found and fixed exactly this in the field beside it, `frozen_at_commit`,
and left the date. Run today, the superseded script rewrote **2026-08-31 → 2026-09-01**, with
the other eighteen keys identical. The date the phase-E set was frozen was being overwritten
by every run of the analysis. It is written once now, because the file carrying it is.

## What this does not establish

That the frozen set is the *right* set. It is thirty-three rows chosen in batch 12 by a rule
fixed before tier 1 ran, and nothing here inspects that choice. What is checked is that the
set has not moved since, and that it could not have been chosen after the year was opened —
shape, again, and not content.

Nor does it establish anything about the eight of thirty-two stability rows the clean-room run
reached. Both distributions remain unverified from cold and the phase-E half has still never
run from a clean checkout. That is batch 25.
