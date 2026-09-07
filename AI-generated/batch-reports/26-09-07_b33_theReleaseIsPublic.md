# Batch 33 — the release is public, and the scan that authorises it is of the tree that went out

Generated from [[26-08-22_dengueForecastingCase]] — iteration 33

**State: done — produced.** `github.com/sandvelab/veridical-agentic-dengue-laos` exists, is
public, and holds the repository: `main` at `8690d0a`, and batch 21's `greedy` at `6bfeecf`
beside it, unmerged. The last row of the ledger is closed and every row in it is closed.

**What a reader gets is the whole tree, not a distribution of it.** 4 854 tracked files;
`analysis/` entire, with **23 paths not taken across 17 forks and an entry point for every
one**; the claim collection, the manuscript and its provenance sidecar; every provenance
record; the environment specifications at all three layers; the instruction files and the
skills, because they determine how the analysis was produced; the hierarchical and
reproducibility reports; and a root script that rebuilds it.

**The batch's one substantive finding is about its own record.** The scan and manifest batch
33 had committed as the authority for this push carried `scanned_at_commit: 4bbe766a4` — batch
32's head — while the provenance section written beside them names `f4c1b7c`. Both statements
are true of the moment they describe and the pair reads as one that is not: the tree that was
scanned contained neither licence file nor the `Licence` section of `README.md`, which are the
release's own legal statement and the reason the licence question was reopened at all. Both
scripts were re-run at `5da6e3875`, the commit pushed, and come back clean.

**The release rests on the clean-room run of 2026-09-05 and says so on the remote**, rather
than implying a check of the pushed commit: 14.87 h, exit 0, 207 of 207 scores from models this
project wrote identical. The human settled on 2026-09-06 that batch 32's rewrite does not
invalidate it, and why.

---

## 1. What was pushed, and when

| | commit | duration | |
|---|---|---|---|
| repository created | — | — | public, `sandvelab/veridical-agentic-dengue-laos` |
| `main` | `8690d0a` | **95.98 s** | 4 854 tracked files; the default branch |
| `greedy` | `6bfeecf` | **9.31 s** | 3 commits, never merged, no reported result on it |

Measured beforehand by bundling: **176.70 MiB** for `main` alone, **185.41 MiB** with `greedy`
— the counterfactual costs **8.70 MiB**. The largest tracked file is 41.8 MB, a Thai NetCDF
evaluation from the external check, inside GitHub's 50 MB advisory threshold and well inside
its 100 MB limit; nothing was rejected and no warning was returned.

`greedy` stays a branch. It is the counterfactual to batch 9's promotion rule — the rule
iterated to a fixpoint — and Rule 4 says the paths not taken stay in the tree and runnable, so
leaving it unpushed would have left ledger row 21 pointing at a report no reader could open.
Merging it would have made the release claim more than its checks support: `main` is the tree
the clean-room run of 2026-09-05 verified, and three commits no run has covered would not be.

## 2. A scan is only ever true of the tree it read

This sentence is the one batch 33 had already written, to justify re-running batch 19's scan
rather than pushing on it. Applied one commit further along it says something the batch had not
yet done.

The artefacts committed at `f4c1b7c` record:

```
scanned_at_commit:  4bbe766a4          checked_at_commit:  4bbe766a4
```

and the provenance section committed in the same commit records:

```
inputs:  … at commit f4c1b7c
commit:  f4c1b7c
```

Neither is false. The scripts ran while `4bbe766a4` was HEAD and their output was committed in
`f4c1b7c`. But the pair reads as a scan of `f4c1b7c`, and `f4c1b7c` is the commit that
*introduced* `LICENSE` and `LICENSE-CODE` — so the tree the scan actually read did not contain
the licences, and two further commits (the release folder's own re-run record, the ledger row
and the task log) landed after that.

Re-run at `5da6e3875`, both come back clean, and every field that moved is a count of what was
read:

| | at `4bbe766a4` | at `5da6e3875` |
|---|---|---|
| tracked files | 4 852 | **4 854** |
| history blobs | 9 289 | **9 318** |
| credential hits, working tree | 0 | **0** |
| credential hits, history | 0 | **0** |
| credential files by name | 0 | **0** |
| home-directory path, in source files | 0 | **0** |
| Rule 10 items present | 8 of 8 | **8 of 8** |
| paths not taken, with an entry point | 23 of 23 | **23 of 23** |

The two files are `LICENSE` and `LICENSE-CODE`; the 29 blobs are those two and the 27 versions
of files the four batch-33 commits touched. The home-directory path stands at 3 965 occurrences
in 348 files in both scans — 341 `.log`, 4 `.json`, 2 `.txt`, 1 `.csv`, **and no source file** —
which is the shape the human's decision of 2026-09-05 was made about.

**What no scan can cover, stated rather than closed.** The commit that records a scan is
necessarily a child of the commit it scanned; a scan of its own commit does not exist. The gap
is enumerable and it is enumerated in `AI-generated/release/provenance.md`: between `5da6e3875`
and what `main` now points at, the only changes are the two JSON artefacts, that provenance
section, a paragraph in the release folder's `README.md`, this report, and the plan and
task-log entries that close the batch. No file under `analysis/`, `environment/`, `Archive/` or
`Human-AI-collaboration/` moves, so nothing the scan looks for could have entered.

## 3. What GitHub reports about the licence, which is not what the repository says

The repository's licence is unambiguous in prose: `LICENSE` names CC BY 4.0, states the scope
document by document, and links the canonical legalcode; `LICENSE-CODE` carries the MIT text in
full; `README.md` has a `Licence` section saying which applies where.

**GitHub's API returns `licenseInfo: null` for the repository**, and no licence appears in the
sidebar. Its detector matches a licence by reproducing the licence's own text, and `LICENSE`
links the CC BY legalcode rather than reproducing its seven thousand words, while `LICENSE-CODE`
is not a filename the detector looks at. So an automated consumer — and a reader who reads the
sidebar rather than the file — sees a repository with no licence, which is the state Rule 10
was reopened to fix.

This is recorded and not acted on. The licence choice and its wording are human-set, the two
remedies both change what the human decided (paste the full legalcode into `LICENSE`, or make
the MIT file the one GitHub reads and demote the CC statement), and the prose is legally
sufficient as it stands — CC's own recommended practice is a notice naming the licence and
linking it. It is the human's to settle, and it is the only thing this batch found that a
reader could trip over.

## 4. What is on the remote, against what Rule 10 asks for

`release_manifest.py` checks the eight items `/release` names against what git tracks, at the
pushed commit:

- data, or accessioned references where redistribution is not permitted — **ok**
- all scripts, and `analysis/` entire, alternatives included — **ok**
- the environment specifications at all three layers — **ok**
- the claim collection and the manuscript's provenance sidecar — **ok**
- the provenance records — **ok**
- the instruction files and skills — **ok**
- the hierarchical report and the reproducibility report — **ok**
- a root script that rebuilds everything — **ok**

And the thing the release exists to make possible: **23 paths not taken, across 17 forks, each
with an entry point**. Publishing them is what changes a reader's question from *does this
analysis run* to *was this a reasonable analysis among the ones that were tried*, and it is the
part of this release that nothing else in the project substitutes for.

## 5. What remains, and is not the agent's

`/release` asks for a **citable, versioned snapshot with a persistent identifier** — a
repository host is where work lives, not an archive. Linking the repository to Zenodo (or an
equivalent), cutting a release tag, and citing the resulting DOI in the manuscript needs an
account the agent does not have. It is the one step of Rule 10 the push does not complete, and
it is recorded as outstanding rather than as done.

The licence-detection question of §3 is the other open item, and it is a decision rather than
a defect.

## 6. Decisions

| Decision | Basis | Agency |
|---|---|---|
| Push without a further `/validate cleanroom`; the release rests on the run of 2026-09-05 and says so | Batch 32's rewrite is provably score-free — 47 byte-identical configurations, a second pass reproducing 102 documents byte for byte — so a further 15 h would confirm deterministic functions of the checkout | human-set, 2026-09-06 |
| The repository is created public | Rule 10 is public access, and the release is assembled for it | human-set, 2026-09-06 |
| CC BY 4.0 for the record, MIT for the scripts | The release is both a record and a program; Creative Commons advises against CC for software | human-set, 2026-09-06 |
| `greedy` is published beside `main` and stays unmerged | Rule 4 keeps the paths not taken runnable; `main` is the tree the clean-room run verified | human-set, 2026-09-06 |
| Push proceeds now, both branches | Asked and answered at the start of this batch's final step, as §10 of the plan requires | human-set, 2026-09-07 |
| Re-run the scan and manifest at the pushed commit before pushing | The committed pair named a commit whose tree it had not read, and the difference is the licence files. Five minutes against a release authorised by a scan of an ancestor | agent-autonomous |
| State the scan's uncoverable gap rather than chase it | A scan of its own recording commit cannot exist; the regress is infinite and the residue is enumerable | agent-autonomous |
| Report GitHub's licence detection rather than change the licence files | Both remedies alter a human-set decision, and the prose is sufficient as it stands | agent-autonomous |

Information gathering: agent-retrieved throughout — the two artefacts, the field-by-field
comparison against the copies committed at `f4c1b7c`, the remote's own state after the push,
and the bundle measurements.

## 7. Checks

`/validate invariants` passes, all eleven — `tree`, `provenance`, `hashes`, `plots`, `seeds`,
`claims`, `combos`, `freeze`, `git`, `crossing`, `pool` — before the push and after the batch's
last commit.

`/validate cleanroom` was not run again, by the human's decision of 2026-09-06 recorded in §4b
of the plan; the release rests on the run of 2026-09-05 and both the reproducibility report and
this report name that run rather than implying a check of the pushed commit.

`/validate outsider` last ran on 2026-09-05 and produced batch 32's work; nothing in the
instructions has changed since.
