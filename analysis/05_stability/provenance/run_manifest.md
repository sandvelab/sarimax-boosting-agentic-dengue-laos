# Provenance — the combination driver

```
result:              results/run_status.csv
                     results/logs/main.log
script:              scripts/run_manifest.py
                     sha256:eeaace3c5730c4b924d6d7be7628fee4b2361b85eb9b71a82b41094b1c857260
                     scripts/lib/inventory.py
                     sha256:71e0687ad3227b07cd569ba167ad3c63fd7cfd9b1636f798a545de72e8c59667
invocation:          "$PYTHON" scripts/run_manifest.py --only main
                     (from the repository root. Not called from run.sh yet — see the
                     comment at the foot of 05_stability/run.sh, and §5 of batch 12's
                     report. Batches 13, 22 and 14 call it with --batch.)
inputs:              analysis/05_stability/results/manifest.csv
                     analysis/**/claim.md — the tree, for each fork's main-path child
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none of its own. Every model it invokes seeds itself from the project
                     seed through analysis/scripts/lib/project_seed.py.
commit:              26dca49
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** One row of the manifest has been run through the driver — `main`,
whose only step is `conclude.py`, because the main path is the analysis that has already
run. `conclusion.json` came back byte-identical, which is the smallest possible end-to-end
exercise of the driver and the one available before any child is built. Everything else in
`run_status.csv` records why it did not run.

**What the driver is.** It calls the tree's own scripts with `COMBO` set, exactly as
`AGENTS.md` §2 specifies a stability node does. There is no second implementation of the
analysis here and there must not be one. What the driver contributes is the **order**: both
assemblers in this project resolve a fork by finding the one child of it with results under
this combination and fail if they find two, so a combination may not run a parent's
`run.sh` after running a moved sibling. The driver substitutes the moved child for the main
one and runs the rest of the fork's siblings at their main paths, which is the same shape
`AI-internal/useful-scripts/candidate_fork_sweep.py` used for phase C.

**Its dry run is the specification of the children that do not exist.** `--dry-run` prints
the ordered step list for every row including the unbuilt ones, so batch 13 and batch 22
have the contract each new child has to satisfy written out by the driver that will call
it, rather than by a batch report.

**Rows that cannot run are recorded, not skipped silently.** An unbuilt child, a
pending tier-2 slot and a failed step each land in `run_status.csv` with the reason. A
driver that stopped at the first unbuilt row would leave the shape of what is missing in
nobody's notes, which is the absence `AGENTS.md` §4 forbids.

alternatives-considered: driving the manifest from a single re-entrant call to
`analysis/run.sh` per combination — rejected, because the root's `run.sh` runs every fork's
main child and the assemblers would then see two children of the moved fork. Teaching each
assembler to prefer a non-main child when it finds two — rejected as the wrong place for
the knowledge: which child a combination takes is the manifest's business, and an assembler
that silently picked between two would make a combination's contents depend on what
happened to be on disk. Re-running the reference model on candidate rows so that every row
is self-contained — rejected because it is unseeded, and a fresh draw would move the
denominator of every comparison for reasons unrelated to the fork.

agency: agent-autonomous.

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/logs/aggregate_caseWeighted.log
                     results/$COMBO/logs/aggregate_populationWeighted.log
                     results/$COMBO/logs/popColumn_backCast.log
                     results/$COMBO/logs/provinces_mergeVientiane.log
                     results/$COMBO/logs/provinces_reportingOnly.log
                     results/$COMBO/logs/retrain_everySplit.log
                     results/$COMBO/logs/trainingWindow_from2004.log
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
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** The driver's transcript for each row: the step list it ran, each step's own output, and the failures. `provinces_reportingOnly.log` and `retrain_everySplit.log` are the third attempt at those rows; the two earlier failures are described in the reference node's record and in batch 13's report, and the logs themselves were overwritten by the successful run, which is what `run_status.csv` exists to date.

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
