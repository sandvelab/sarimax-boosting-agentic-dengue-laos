# Provenance — validation

One section per file `/validate` produced that is more than a document. Append; never
overwrite.

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
