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


---

## Batch 22 — the two baseline rows

```
result:              results/run_status.csv
                     results/logs/climatology_frozenWindow.log
                     results/logs/persistence_negBinomialFloor.log
script:              scripts/run_manifest.py — unchanged by this batch
invocation:          environment/chapenv/bin/python \
                       analysis/05_stability/scripts/run_manifest.py --batch 22
inputs:              results/manifest.csv (rows 9 and 10), and the tree, through
                     scripts/lib/inventory.py
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none at this node; each model carries its own
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** Both rows ran, at 137 s (`climatology_frozenWindow`) and 156 s
(`persistence_negBinomialFloor`) against the manifest's estimates of 100.7 s and 103.6 s —
1.36 and 1.51 times the plan, the same over-run direction and rough size the setup rows
showed, and for the same reason: the cost model sums each row's parts as measured under
`main`, and under these rows the pool's members are rebuilt rather than reused.

**The first attempt failed at the first step of both rows**, with `ModuleNotFoundError: No
module named 'chap_eval'` — the two new runners resolved the shared library one level too
high in the tree. Nothing was written and the failure is in `run_status.csv`'s history
through the commit that fixed it (`d8f93ca`); the run recorded here is the second.

alternatives-considered: none at this node; the step list for a `baseline` row is what
`steps_for` derives from the manifest, unchanged since batch 12.

agency: agent-autonomous.
information: agent-retrieved — the timings are read from results/run_status.csv.

---

## Batch 14 — the fourteen candidate and family rows, and the running family's own fork

```
result:              results/run_status.csv
                     results/logs/family_hierNB.log
                     results/logs/family_boosted.log
                     results/logs/weighting_crpsWeighted.log
                     results/logs/autoregressive_lag3.log
                     results/logs/covariates_lagged.log
                     results/logs/covariates_rich.log
                     results/logs/features_richCalendar.log
                     results/logs/fitTime_refitAtPredict.log
                     results/logs/head_quantileEnsemble.log
                     results/logs/observation_negBinomial.log
                     results/logs/observation_zeroInflated.log
                     results/logs/population_covariate.log
                     results/logs/population_ignored.log
                     results/logs/yearVariance_shared.log
                     results/logs/aggregate_caseWeighted.log
                     results/logs/aggregate_populationWeighted.log
                     and, per row, everything the tree's own steps write under that
                     combination
combinations:        family_hierNB, family_boosted, weighting_crpsWeighted,
                     autoregressive_lag3, covariates_lagged, covariates_rich,
                     features_richCalendar, fitTime_refitAtPredict,
                     head_quantileEnsemble, observation_negBinomial,
                     observation_zeroInflated, population_covariate, population_ignored,
                     yearVariance_shared; and aggregate_caseWeighted and
                     aggregate_populationWeighted re-run under the corrected 03_compare
script:              scripts/run_manifest.py
                     sha256:0f6378b3f440dfd09abb7a9898aa97cb33a5a94021e08c2bd63ec0b3830b06a9
invocation:          environment/chapenv/bin/python analysis/05_stability/scripts/run_manifest.py --batch 14
                     then ... --only weighting_crpsWeighted after the driver was fixed
inputs:              results/manifest.csv; the tree's own run.sh files and node scripts
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none of its own; each step seeds itself from the project seed
commit:              3fb1280
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-30
```

**What it establishes.** Thirteen of the fourteen rows ran on the first attempt, in 1 123
seconds against 1 224 planned. `weighting_crpsWeighted` failed at its second step in two
seconds, was fixed, and ran in 172.

**The failure, kept.** The driver ran the moved fork child and then the family's `run.sh`.
An alternatives parent runs every fork below it at its main path — that is what the
relationship means — so on the one row whose moved fork belongs to the family that is
*running*, `c_ensemble/run.sh` ran `01_weighting/a_equal` after the driver had already run
`b_crpsWeighted`, and the assembler refused two children of one fork. The refusal is the
design working; the driver was what was wrong.

A row moving the running family's own fork now takes that family's forks itself — the moved
child where one moved, the main one otherwise — and then runs the family's **own scripts**,
read out of its `run.sh` under the `# Own scripts` marker `node.py` writes. It is the
treatment `02_setup` already has one kind up, where the driver calls `assemble_setup.py`
rather than `02_setup/run.sh`. Reading the list rather than carrying it is the same choice
`inventory.py` made about forks: a list kept here is a second copy of a file that is free to
change without it.

**This is the fourth fork-blind step in the project and the first found by running.** The
other three — `prepare_members.py`'s member discovery, `01_collect`'s inheritance, and this
batch's `ensure_configuration` — were found by planning or by reading output. All four have
the same origin: a step written when every fork had exactly one child that did anything.

**Verified against the whole dry run.** The step lists of all 33 rows before and after the
change differ in exactly one row and by exactly the four commands above.

**Two rows the failed attempt touched.** It wrote a `model_option_spec.json` for
`a_equal` under `weighting_crpsWeighted`, which is the sibling's choice under a combination
that does not take it; it was removed before the re-run, and the re-run wrote the
combination fresh.

alternatives-considered: hard-coding each family's own scripts in the driver (rejected — it
is a second copy of `run.sh`, and the same objection the driver's own docstring makes to a
second implementation of the analysis); having the family's `run.sh` skip a fork whose
sibling already ran (rejected — `run.sh` is a short list of shell lines by `AGENTS.md` §2
and putting resolution logic in it would make every node's main script conditional on the
combination).

agency: agent-autonomous.

---

## Batch 14 — tier 2: the eight pairs

```
result:              results/run_status.csv
                     results/logs/provinces_reportingOnly__family_hierNB.log
                     results/logs/provinces_reportingOnly__weighting_crpsWeighted.log
                     results/logs/provinces_mergeVientiane__family_hierNB.log
                     results/logs/provinces_mergeVientiane__weighting_crpsWeighted.log
                     results/logs/provinces_reportingOnly__aggregate_caseWeighted.log
                     results/logs/provinces_mergeVientiane__aggregate_caseWeighted.log
                     results/logs/family_hierNB__aggregate_caseWeighted.log
                     results/logs/weighting_crpsWeighted__aggregate_caseWeighted.log
                     and, per row, everything the tree's own steps write under that
                     combination
script:              scripts/run_manifest.py
                     sha256:0f6378b3f440dfd09abb7a9898aa97cb33a5a94021e08c2bd63ec0b3830b06a9
invocation:          environment/chapenv/bin/python analysis/05_stability/scripts/run_manifest.py --tier 2
inputs:              results/manifest.csv, with its eight tier-2 rows resolved by
                     plan_manifest.py from results/tier2_rule.md and results/conclusions.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none of its own
commit:              ba3cf8d
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** All eight pairs ran on the first attempt, in **5 703 seconds**
against 6 047 planned — 5.7 % under, and the same total-accurate, row-inaccurate pattern
batches 12 and 13 recorded. Six of the eight move a `02_setup` fork and therefore re-run the
reference at four repeats under emulation, which is where 87 % of the time went; the two that
do not took 38 and 97 seconds.

**Two of the eight are the first rows to use the driver's own-scripts path**, because their
moved fork belongs to the family that runs. Neither needed anything further.

**No row was retried.** Batch 13 gave the reference node three attempts per repeat after
measuring an intermittent crash at about one job in a hundred; across the twenty-four
reference evaluations these eight rows asked for, `attempts_per_repeat` is 1 throughout.

agency: agent-autonomous.
information: agent-retrieved.

---

## The phase-E half (batch 16)

```
result:              results/run_status_holdout.csv
                     results/logs/aggregate_caseWeighted__holdout.log
                     results/logs/aggregate_populationWeighted__holdout.log
                     results/logs/autoregressive_lag3__holdout.log
                     results/logs/climatology_frozenWindow__holdout.log
                     results/logs/covariates_lagged__holdout.log
                     results/logs/covariates_rich__holdout.log
                     results/logs/family_boosted__holdout.log
                     results/logs/family_hierNB__aggregate_caseWeighted__holdout.log
                     results/logs/family_hierNB__holdout.log
                     results/logs/features_richCalendar__holdout.log
                     results/logs/fitTime_refitAtPredict__holdout.log
                     results/logs/head_quantileEnsemble__holdout.log
                     results/logs/main__holdout.log
                     results/logs/observation_negBinomial__holdout.log
                     results/logs/observation_zeroInflated__holdout.log
                     results/logs/persistence_negBinomialFloor__holdout.log
                     results/logs/popColumn_backCast__holdout.log
                     results/logs/population_covariate__holdout.log
                     results/logs/population_ignored__holdout.log
                     results/logs/provinces_mergeVientiane__aggregate_caseWeighted__holdout.log
                     results/logs/provinces_mergeVientiane__family_hierNB__holdout.log
                     results/logs/provinces_mergeVientiane__holdout.log
                     results/logs/provinces_mergeVientiane__weighting_crpsWeighted__holdout.log
                     results/logs/provinces_reportingOnly__aggregate_caseWeighted__holdout.log
                     results/logs/provinces_reportingOnly__family_hierNB__holdout.log
                     results/logs/provinces_reportingOnly__holdout.log
                     results/logs/provinces_reportingOnly__weighting_crpsWeighted__holdout.log
                     results/logs/retrain_everySplit__holdout.log
                     results/logs/trainingWindow_from2004__holdout.log
                     results/logs/weighting_crpsWeighted__aggregate_caseWeighted__holdout.log
                     results/logs/weighting_crpsWeighted__holdout.log
                     results/logs/yearVariance_shared__holdout.log
script:              scripts/run_manifest.py
                     sha256:48bd1c5b04e0abb468e914e1b197df9feef96de3b136f422b5b04b72ed6a68ca
invocation:          "$PYTHON" scripts/run_manifest.py --dataset holdout
                     (from 05_stability/, via run.sh)
inputs:              analysis/05_stability/results/manifest_holdout.csv
                     analysis/05_stability/results/run_status_holdout.csv (its own record
                     of what has already run, read to refuse re-running it)
                     the tree's own run.sh files and node scripts, unchanged
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               component seeds reach the models through their own configuration; the
                     driver adds none. The reference model is unseeded and is re-scored four
                     times on the holdout as on development, which is why the conclusion
                     divides by their per-cell mean.
commit:              609e1be (the run), 895a9f8 (the code and the main row)
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: run the holdout set with a second driver written for it. Rejected
                     for the reason this script exists: a holdout row that ran different
                     code would not measure what phase E is for. Every command is the one
                     its development twin issued, and the dataset reaches the steps through
                     the combination name.
agency:              agent-autonomous for the mechanism; human-set for the constraint it
                     works under (plan §3).
```

**What it establishes.** The 32 rows of the frozen set that have a development twin ran on
the held-out year, none failed, and the whole set took **2.39 h** against the 2.07 h it was
frozen at. The thirty-third row, `family_ensemble__holdout`, is not run: it is the main path
under a second name and development did not run it either, so there is nothing for it to be
reported beside. The absence is in `run_status_holdout.csv` with that reason.

**A holdout row that has run is not run again.** Plan §3, enforced rather than remembered:
the driver reads its own status file and skips every row recorded as `ran`. This was found
by running the manifest without it, which began re-running `main__holdout` — and since the
reference is unseeded, a second pass would have replaced the denominator of every number
already reported with a different draw. It was stopped at the persistence baseline and those
files restored; the reference was never reached.


---

## Batch 23 — the digest of the two-condition seal

```
result:              no analysis result; the change is to the seal that decides whether a
                     holdout row runs. results/run_status_holdout.csv is unchanged by it,
                     and results/.holdout_opened is not a result — it is gitignored and is
                     a property of one working tree.
script:              scripts/run_manifest.py
                     sha256:df5b87ea4635ce3ff3ad8a79e182039d81f261983df2702d232795827f60dc0c
invocation:          unchanged: "$PYTHON" scripts/run_manifest.py --tier 1 | --tier 2 |
                     --dataset holdout, from 05_stability/, via run.sh
inputs:              unchanged from the section(s) above
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               unchanged from the section(s) above
commit:              ae565fd (the seal), ad7e64f (the marker moved to the node root)
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31; recorded 2026-09-01
```

**What changed in the script.** The holdout seal had rested on `run_status_holdout.csv`
alone, which is versioned — so it sealed every clone of the repository and not only the copy
that opened the year. Batch 18's clean-room run found all thirty-two rows skipped in a fresh
checkout, `collect_conclusions.py --dataset holdout` re-reading the committed conclusions,
and the phase-E half of `analysis/run.sh` reproducing its outputs byte-identically while
running none of the analysis behind them. The seal now takes two conditions and needs both:
the row recorded as `ran` in the versioned file, so forcing a re-run by deleting a row still
shows in git, and a gitignored `.holdout_opened`, written by the driver after the first
invocation in which a holdout row actually ran, saying that *this* tree opened the year. The
marker sits at the node root rather than under `results/`, at `ad7e64f`, because `results/`
is where results go and a seal is not one.

**What ran on it, which is nothing, and why that is the record.** No row of either manifest
has been executed by this version. Plan §3 forbids re-running the frozen set, and the
development set was not re-run either. What is verified is that the seal *releases*: the
driver plans all thirty-two rows in a fresh clone. What is not verified is that they then
produce the archived numbers there, and that is batch 25's, stated as plainly in
`AI-generated/validation/26-09-01_cleanroom.md`. This section exists so that the gap has an
address: a reader who finds the driver's digest recorded here and the phase-E rows recorded
under `609e1be` can see that the two are different versions without having to diff anything.

alternatives-considered: re-running one holdout row to make the digest and the results agree.
Rejected — it is exactly what §3 forbids, and for the reason §3 gives: the reference is
unseeded, so a second pass replaces the denominator of every reported number with a different
draw. A record that says which version ran is worth more than a number that has been redrawn
to suit it.

agency: agent-autonomous for the mechanism; human-set for the constraint it works under
(plan §3).
information: agent-retrieved — the digest is computed from the file and the two changes read
from the diffs at `ae565fd` and `ad7e64f`.
