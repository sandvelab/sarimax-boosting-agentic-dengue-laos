# Provenance — the training window, the whole development period

```
result:              results/main/analysis_dataset.csv
                     results/main/setup_spec.json
script:              scripts/apply_training_window.py
                     sha256:47606787c0b389db49c2171836f140cc1f9af9f47e3952bf9e98d47876882f57
invocation:          "$PYTHON" scripts/apply_training_window.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/02_setup/01_population/a_static/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     (resolved by searching for the one child of 01_population with
                     results under this combination, never by naming a child)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. A row filter on a period string; project seed 20260822 unused.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/02_setup/02_trainingWindow/a_from1998
produced:            2026-08-26
```

**What it establishes.** All 2 592 rows, 1998-01 to 2009-12, reach the models. Nothing is
discarded, so this stage too is the identity on the main path.

**Why the fork is clean.** Batch 2 established that chap-core lays its splits out backwards
from the last period of the file, so truncating early years changes what the models learn
from and leaves the evaluated cells identical. That is what makes a training-window fork
comparable across its children: both sides are scored on the same 371 cells. A fork that
moved the evaluated set would not be, and the province fork below is exactly that case,
handled differently.

alternatives-considered: starting at 2003, after the most zero-heavy years, is the sibling
(`b_from2003`, built in phase D). Starting at a *per-province* first-report date was
considered and rejected: it makes the training window a property of the province, so the
models would be learning from panels of different lengths and the fork would confound the
window with the province set. Down-weighting rather than dropping the early years was also
rejected — it is a model-internal choice, not a property of the dataset every model faces.

agency: agent-autonomous. The monotone decline in the zero rate is batch 3's finding from
the data; that the main path keeps everything, on the grounds that discarding years is the
choice that assumes more, is the agent's.
