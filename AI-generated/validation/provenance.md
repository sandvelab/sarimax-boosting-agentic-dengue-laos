# Provenance — validation

One section per file a check on the method produced that is more than a document — from
`/validate`, or from a targeted check written for one defect. Append; never overwrite.

## `26-09-01_cleanroom_comparison.json`

```
result:              26-09-01_cleanroom_comparison.json
script:              AI-internal/useful-scripts/cleanroom_compare.py
                     sha256:33010dd1c969900db39ef0ca95c6972ef96d61c6a99c4cc104708d67e9832c48
invocation:          .venv/bin/python cleanroom_compare.py
                     (from the clean-room directory holding the clone)
harness:             AI-internal/useful-scripts/run_cleanroom.sh
                     sha256:846911b2bf9dc8d8bb5a89164542979bf8b349557dddc7de69d910db55c8105f
                     bash run_cleanroom.sh — clones the repository at HEAD into a scratch
                     directory, builds environment/chapenv from environment/lock.txt, runs
                     analysis/run.sh from cold, and records git's own diff
inputs:              a git clone of this repository at ad7e64f, and the same repository's
                     working tree as the archive to compare against
environment:         the clone's own environment/chapenv — CPython 3.13.0, chap-core 2.1.0,
                     installed from environment/lock.txt and reported by install-chap.sh as
                     matching it exactly (174 packages). The comparison script itself runs
                     under .venv, standard library only.
seeds:               none in the comparison. The run it compares is seeded per component
                     except the reference model, which is unseeded and is the reason
                     anything moved at all.
commit:              8908d17
instructions-commit: 8908d17
node:                not a node — a check on the method, like the determinism checks
produced:            2026-09-01, batch 18
```

**What it establishes.** That every model this project wrote reproduces its mean CRPS to the
last digit from a fresh clone and a freshly built environment; that the reference model does
not and cannot, being unseeded; and that the reported skill score therefore reproduces to
within 0.0065, the 0.171 CRPS behind it being a quarter of the floor below which this project
already declines to attribute anything to a model.

**What it does not establish, and the field that says so.**
`rows_of_the_stability_manifest_reached` lists **8** of the 32. The run was interrupted, so
neither distribution is verified from cold and the phase-E half has never been executed from
a clean checkout. Completing it is batch 25. A reader should take this file as covering the
reported main path and nothing beyond it.

**Why the comparison is git's own diff.** The clone's index is the archived result, so there
is no second copy of 1.6 GB of results to keep in step and nothing to decide about what to
compare against. The cost is that a byte comparison cannot distinguish a changed forecast
from a changed timestamp inside a NetCDF file, which is why the derived CSVs rather than the
`.nc` files carry the answer.

agency: agent-autonomous.
information: agent-retrieved.

## `26-09-01_freezeDefence.json`

```
result:              26-09-01_freezeDefence.json
script:              AI-internal/useful-scripts/check_freeze_defence.py
                     sha256:cc0ab8bd0b359c7436adf78f2e60c81979e0e7609caac5e39bbc776cb6f1b7d0
invocation:          .venv/bin/python AI-internal/useful-scripts/check_freeze_defence.py
                     --root .
under test:          analysis/05_stability/scripts/freeze_holdout_manifest.py
                     sha256:8bc160edcac6f70b0e28327d09f1cee76a10e30520d3e8ac881ca8cc4c9e59b2
                     AI-internal/useful-scripts/check_invariants.py::check_freeze
                     sha256:7c9aa339861505bbc9eaa3cbd4689232e6cc78f0d86740c62122c2a73c9e9a83
inputs:              throwaway copies of analysis/05_stability/results/, built from the live
                     files and mutated per scenario, plus two fixture git repositories.
                     Nothing is written to the live tree.
environment:         the script itself runs under .venv (CPython 3.13.7, standard library
                     only); the node script it exercises is invoked under
                     environment/chapenv, because a node's scripts are part of the pinned
                     analysis whatever they import
seeds:               none.
commit:              595c32d
instructions-commit: 595c32d
node:                not a node — a check on the method, like the determinism checks
produced:            2026-09-01, batch 24
```

**What it establishes.** That the frozen phase-E set defends itself, in eleven situations of
which four corrupt the frozen manifest and so cannot be put to the live tree. Seven go to the
node script and four to the `freeze` invariant, and all eleven behave as specified.

**The two that carry the weight.** `added` is batch 18's defect, reproduced: a fork child
discovered after the opening appears as a new development row, and under the superseded
script the frozen set became **34 rows**. It is now 33 rows and one row reported as unpaired.
`refreeze_from_cold` deletes the frozen file with no trace of the year ever having been
opened, which is batch 15's own path, and the manifest comes back **byte-identical** to the
one frozen in batch 15 — the evidence that restructuring the script did not restructure the
set it produces.

**What it says about the version it replaced.** Run against the superseded script, six of the
seven scenarios fail and **every one of them exits 0**: the frozen set silently grew to 34
rows, silently shrank to 32, was silently rewritten with a renamed fork child, had its frozen
development pairing silently replaced by drifted numbers, and was re-derived from scratch
after the year had been opened. That last is the one a clean-room run would have hit.

alternatives-considered: **testing against the live tree with a backup and a restore** —
rejected: four scenarios write a broken frozen set, and a restore that failed would leave the
project's central §3 artefact wrong on disk. **Folding these into
`check_invariants.py`** — rejected, because that file asserts things about the repository as
it is, and this one asks what happens to repositories that are not this one.

agency: agent-autonomous.
information: agent-retrieved.
