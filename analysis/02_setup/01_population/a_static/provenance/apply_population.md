# Provenance — the population column, taken as the archive supplies it

```
result:              results/main/analysis_dataset.csv
                     results/main/setup_spec.json
script:              scripts/apply_population.py
                     sha256:8e70f8cc37d08e0aac52262de8f4769aa4741c424f9283cc8fb097b0b647e83e
invocation:          "$PYTHON" scripts/apply_population.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so the combination
                     is `main` and results go to results/main/.)
inputs:              analysis/01_data/01_partition/results/development_1998-01_2009-12.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage is the identity on the data and the diagnostic is a
                     count of distinct values; project seed 20260822 has no surface here.
commit:              959f63c
instructions-commit: cf97b81 (AGENTS.md §8 now states the node-naming rule, and
                     check_invariants enforces it; node.py no longer treats a
                     subdirectory of scripts/ as a callable step)
node:                analysis/02_setup/01_population/a_static
produced:            2026-08-26
```

**What it establishes.** The population column is constant within every province across the
whole development period — checked here rather than assumed, because the whole reason this
node is a fork is that a constant is the wrong shape for a decade of a growing population.
The stage passes the dataset through unchanged, so the file it writes is the archived
development file byte for byte.

**Why the transformation is the identity and the node still exists.** A fork whose main path
does nothing is not a redundant fork: it is the place where "we used the column as supplied"
stops being an unexamined default and becomes a recorded choice with a sibling that would do
otherwise. The sibling (`b_backcast`, a per-year series back-cast from a published growth
rate) is not implemented yet; it is built when the stability manifest needs it, in phase D.

alternatives-considered: the back-cast series is the alternative and it is the sibling this
node's parent exists to hold. A third option — dropping the population column entirely, so
that no model can use it — was rejected because it removes a covariate from the reference
model as well, and the reference is run at its own configuration, not at one we choose for
it. A fourth — normalising the column to a rate here rather than letting each model decide —
was rejected because how population enters a model is a candidate-internal question and
belongs in the subtree that moves only our own models.

agency: agent-autonomous. That the population figure is static and therefore a problem was
established by batch 3 from the data; that the main path takes it unchanged is the agent's,
on the reasoning that it is the reading with the fewest of our fingerprints on it.
information: agent-retrieved — the column's behaviour is read from the file, not recalled.

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
node:                analysis/02_setup/01_population/a_static
produced:            2026-08-29
```

**What it establishes.** Ran under the six rows that did not move this fork.

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

## Batch 23 — the digest batch 16's switch left behind

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_population.py
                     sha256:71742dbce933ba0819f264951e2c016d74110e4e4ed0ae3a5ac022f1f47a6a87
invocation:          unchanged: "$PYTHON" scripts/apply_population.py, from the node
                     directory via run.sh, with COMBO set by the driver where a
                     combination is being run
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              895a9f8
instructions-commit: cf97b81
node:                analysis/02_setup/01_population/a_static
produced:            2026-08-31; recorded 2026-09-01
```

**What changed in the script.** The hard-coded development file became `combos.source_dataset(ROOT)`, so the stage
reads whichever of the two files `01_partition` wrote that this combination is evaluated on.
On every development combination that is the same file it had been reading, so this node's
`setup_spec.json` came back byte-identical under all of them; what the change bought is the
holdout rows, which this node then ran.

**What ran on it.** Every development combination this node takes part in was re-derived at
`895a9f8` and this node's specifications came back byte-identical — the fields that moved
are the assembled ones at `02_setup`, which gained `evaluated_on`, `source_dataset`,
`identical_to_source_dataset` and a scheme key on each `eval_flags_source` entry. The
holdout combinations of the frozen phase-E set then ran on this version and nothing else
has.

**Why the record did not say so.** Batch 16 changed the script and ran it, and appended no
section anywhere in `02_setup`. Nothing looked wrong: the development numbers had not moved,
which is exactly the case in which a stale digest is invisible. The `hashes` invariant this
batch added is what makes it visible, and it found the same omission at twenty records.

alternatives-considered: writing one section at `02_setup` covering the whole fork chain
rather than one per node. Rejected because a provenance record belongs to the node whose
script it describes, and a reader checking `apply_provinces.py` would have to know to look
one level up — which is the kind of indirection that makes a record go unread. Correcting
the earlier sections' digests in place was rejected on the standing rule: those sections
describe runs that happened under that version, and the version they name is right.

agency: agent-autonomous.
information: agent-retrieved — the digest is computed from the file and the commit read from
`git log`; what moved in the specs is read from batch 16's report and from the diff.
