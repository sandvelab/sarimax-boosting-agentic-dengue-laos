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

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 13, and
                     COMBO_BASE=main
combinations:        aggregate_caseWeighted, aggregate_populationWeighted, popColumn_backCast, provinces_mergeVientiane, provinces_reportingOnly, retrain_everySplit, trainingWindow_from2004
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/02_trainingWindow/a_from1998
produced:            2026-08-29
```

**What it establishes.** Ran under the rows that did not move this fork.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`, because one script produces the same artefact
under every combination from the same invocation — the combination is a parameter, and each
file records its own in a `combo` field. `/validate invariants` accepts that form only for
combinations the stability manifest names, and its `combos` check is what keeps that set
closed, so the two checks close over each other rather than either being weakened.

alternatives-considered: a section per combination, as batches 10 and 11 wrote for the family
rows — rejected here because seven near-identical sections at twenty-odd nodes is 150 sections
that say the same sentence, and the placeholder exists precisely so that a parameterised step
is recorded once. Where a combination made this node do something *different*, that is in the
paragraph above rather than in a section of its own.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.


---

## Batch 23 — a docstring correction that was never recorded

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_training_window.py
                     sha256:b20a62abc97fb3d155cb561d892cdfd9ff04fddad6464d76727af8f8e23f9ba2
invocation:          unchanged: "$PYTHON" scripts/apply_training_window.py, from the node
                     directory via run.sh
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              40b6936
instructions-commit: cf97b81
node:                analysis/02_setup/02_trainingWindow/a_from1998
produced:            2026-08-29; recorded 2026-09-01
```

**What changed in the script, and what did not.** The docstring said the sibling starts at
2003. It starts at 2004, the calendar midpoint of the period, which is what batch 13 built
it as. One sentence, no executable line, and **no output of this node moved** — this stage
is the identity on the data and writes the same bytes before and after.

Recorded anyway, and the reason is the point of the check that found it. A record whose
digest does not match its script cannot be read as evidence that the script has not changed
underneath it, whatever the change turns out to have been; the reader cannot tell a corrected
docstring from a moved threshold without doing the diff themselves. This node is the main
path of its fork, so this is the version behind every development and holdout combination in
the project.

alternatives-considered: leaving a docstring-only change unrecorded, on the grounds that
nothing computed moved. Rejected — the check that would then be needed is one that judges
whether a diff matters, and there is no such check. The obligation is that the record names
the file that is there.

agency: agent-autonomous.
information: agent-retrieved — the digest is computed from the file and the change read from
the diff at `40b6936`.
