# Provenance — the training window cut to the second half of the record

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_training_window.py
                     sha256:b12525e80e8a1d3dadee07db43409e56ea07dbd1f6ac13364937e4ebf1cefc2c
invocation:          "$PYTHON" scripts/apply_training_window.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=trainingWindow_from2004.)
inputs:              the analysis dataset produced by whichever child of 01_population ran
                     in this combination — resolved by search, not by name, and its
                     sha256 recorded in results/$COMBO/setup_spec.json as `input_sha256`
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage is a predicate on a date column.
commit:              40b6936
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/02_trainingWindow/b_from2004
produced:            2026-08-29
```

**What it establishes.** Half the record is removed: 2 592 rows in, 1 296 out, 2004-01 to
2009-12, with 1 296 rows dropped and the latest dropped period 2003-12
(`results/$COMBO/setup_spec.json`). The evaluated span begins 2008-01, so nothing inside it
was touched, and the script asserts that rather than assuming it — `evaluated_span_untouched`
is a field, and a cut that reached into the evaluated span would stop the run instead of
producing two children scored on different cells.

**Why the cut is at the midpoint.** The fork exists because the zero rate falls monotonically
across the period. A cut chosen by that zero rate — the first year below some share of zeros —
would let the alternative be tuned by the quantity it is meant to probe, and a perturbation
that can be tuned measures the tuner. The calendar midpoint is arbitrary in the one way that
matters: it is stated as a rule anybody can restate, and it was fixed before the row ran.

alternatives-considered: **a zero-rate threshold** — rejected above. **2003-01**, which
batch 5's sibling docstring named in passing before this child existed, was not chosen: it is
not the midpoint of anything and the reference to it was a stale note, corrected in this batch.
**Several cuts as several children** — a fork with four training windows would measure the
shape of the dependence rather than its existence, and was rejected on the manifest's
arithmetic: every additional child of a `02_setup` fork is a twenty-minute row, of which
seventeen minutes are re-running the reference model, for a curve phase D does not need to
report a distribution.

agency: agent-autonomous. That the zero rate falls, and that it is either transmission or
reporting, was established from the data by batch 3. The cut point, the rule that fixes it and
the comparability check are the agent's.
information: agent-retrieved — the evaluated span is read from the stored scheme file, not
recalled.


---

## Batch 23 — the digest batch 16's switch left behind

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_training_window.py
                     sha256:0f586bf854de0a75614f90fb2940bb52d4c25c005de24b1dd3fa3d85d019764d
invocation:          unchanged: "$PYTHON" scripts/apply_training_window.py, from the node
                     directory via run.sh, with COMBO set by the driver where a
                     combination is being run
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              895a9f8
instructions-commit: cf97b81
node:                analysis/02_setup/02_trainingWindow/b_from2004
produced:            2026-08-31; recorded 2026-09-01
```

**What changed in the script.** The evaluated span the fork checks itself against stopped being
`development_evaluated_span` and became `scheme[combos.span_key()]`, so a holdout row checks
that it has not truncated into the year it is scored on rather than into 2008–2009. The
window rule — keep from 2004 — is unchanged, and on development the key resolves to the
constant it replaced.

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

---

## 2026-09-04 — batch 20 — the scheme file becomes a property of the dataset

```
script:              analysis/02_setup/02_trainingWindow/b_from2004/scripts/apply_training_window.py
                     sha256:243044e0dcb37f1c28efab4a47322147bec1f4b60b848490ae9501c9b027b6ac
commit:              bfbc096
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
```

**What changed.** The repository-relative path of the backtest-scheme file was a module
constant here, repeated in six setup scripts. Which scheme file answers is now a property of
the dataset the combination faces, read through `analysis/scripts/lib/combos.py`
(`scheme_path`, `scheme_file`) — the same place the source file and the scheme key were
already decided. Batch 20's external check runs on sibling calendars whose spans are
recorded in a different file, so the constant could not stay one; and a constant repeated in
six places is the shape this project has had to correct four times.

**What it changed in the results: nothing.** The script was re-run under a combination it
had already produced and returned every file byte-identical. The specification's
`eval_flags_source` still names the file it read, now via `combos.scheme_path()` rather than
via the constant, and for every Lao combination that is the same string it was.

**What has run under this version.** The Lao combination it was re-run under to check that,
and batch 20's four external rows for the scripts on the main path.
