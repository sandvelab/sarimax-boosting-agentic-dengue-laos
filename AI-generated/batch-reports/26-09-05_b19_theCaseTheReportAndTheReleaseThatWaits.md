# Batch 19 — the case, the report, and the release that waits

Generated from [[26-08-22_dengueForecastingCase]] — iteration 19

**State: done — produced.** The case write-up, the reproducibility report, the hierarchical
report, the plan's drift remeasured, `/validate cleanroom` to completion with the external
check in the tree, `/validate outsider`, and `/release` scanned and assembled. **The push is
not in this batch**, and the reason is the batch's most useful finding rather than an
omission: the outsider check found a defect in forty committed files, and **a release must not
claim more than its checks support**.

**`analysis/run.sh` exited 0 from a clean checkout in 14.87 hours**, this time with
`analysis/06_external` in the tree — which is exactly what the reproducibility report, written
hours earlier, had named as the one thing the previous verification did not cover. **207 of
207 scores from models this project wrote came back identical; 340 of 345 reference scores did
not.**

**And the run withdrew one of batch 20's claims.** "All three drops are larger than the two
reference bands together" came back **false for Laos and false for Thailand**. Laos had been
flagged as fragile hours before, by the outsider check. **Thailand had not, and failed the
other way** — its band is the tightest in the project, and what moved was the drop itself.

---

## 1. What was produced

| deliverable | where |
|---|---|
| the case write-up | `Human-AI-collaboration/manuscript/26-09-05_illustratingCase.md` |
| its provenance sidecar | `…_illustratingCase_sidecar.md` |
| the reproducibility report | `AI-generated/repro-report/26-09-05_reproducibilityReport.md` |
| what the repository contains, counted | `AI-generated/repro-report/repro_inventory.json` |
| the hierarchical report | rebuilt — 69 combinations, 1 387 pages |
| the plan's drift, at the end | `AI-generated/plan-drift/26-09-05_planDrift.md` |
| the clean-room record | `AI-generated/validation/26-09-05_cleanroom.md` |
| the outsider record | `AI-generated/validation/26-09-05_outsider.md` |
| the release record | `AI-generated/release/26-09-05_release.md` |

Six new claims — **C42–C47 were batch 20's; C48 is this batch's**, and it is the one the
outsider check forced.

## 2. The case write-up

The document that could be lifted into the manuscript's *An illustrating case* section, and
supplying what that paper's Appendix supplies for the case this one replaces: the worked
claim-tree skeleton in dengue terms, the seventeen perturbation forks in four families, and
the judgment about where this setup was more trouble than it was worth.

Written through Rule 9's two steps — results → claims → text — with a sidecar mapping every
passage to the claims it rests on, or, where it rests on none, to what kind of statement it is
instead: **design** (grounded in the plan and `AGENTS.md`), **record** (grounded in the batch
reports) or **judgment** (the agent's opinion, labelled). `/claims check-text` flagged 51
sentences; every one carrying a figure was checked by hand and is in the sidecar.

**The judgment section names three things as not worth their cost**: the hierarchical report
at the depth it reached, criticality annotation applied against a storage constraint that
never arrived, and the two-step writing process on short documents. It also names one
structural regret — the alternatives-and-sub-analyses tree records the *outcome* of a search
and loses its order, which is why the counterfactual had to run on a branch outside the tree.

## 3. The reproducibility report, and why its §5 is longer than its §1

`/repro-report` says section 5 is not optional and is the section a critical reader will
value most. It lists ten things, **four of them found while writing the report**.

Every count in it comes from `repro_inventory.py` rather than from prose, and writing that
script caught two things the report would otherwise have got wrong. Walking
`AI-internal/useful-scripts/` for script files counted **15 078 files and 6 094 813 lines** —
because `/validate cleanroom` clones the whole repository into a subdirectory of it. The count
now comes from `git ls-files`, which knows what belongs to the project where the filesystem
does not. The same walk counted the claim collection's own **fenced example block** as a
48th claim with a broken grounding pointer.

## 4. The clean-room, and the claim it withdrew

`analysis/run.sh` from a clean checkout at `6d6ad7c`: **exit 0, 53 514 s, 891 min**.

**What reproduced.** The reported pool returns 18.816872064690028 and 76.73108261979166,
digit for digit. Across every leaderboard, **207 of 207 scores from our models are identical
and none moved**; 340 of 345 reference scores moved. 2 511 of 4 790 tracked files came back
byte-identical.

**All four recorded-decision defences held from cold**, each against a fresh draw that
disagreed with the record — which is the only condition under which passing means anything.
The fourth was **batch 20's external plan on its first cold test**: the cost unit moved from
2.2568 to 2.1505 seconds per cell, so a plan that recomputed itself would have come back with
four different estimates, and the claim that it was committed before the rows ran would have
been a claim about a file that had since been rewritten. It verified instead and reported the
drift. **That defect was found by asking what the next clean-room run would do; this is the
run that would have found it.**

**And it withdrew a claim.**

| country | archived drop | clean-room | clears the two bands? |
|---|---|---|---|
| Laos | −0.0617 | −0.0786 | True → **False** |
| Vietnam | −0.1714 | −0.1419 | True → True |
| Thailand | −0.0659 | −0.0345 | True → **False** |

The Lao fragility was predicted and C42's scope had been amended to say so before the run
landed. **Thailand was not predicted and failed differently**: its band is the tightest in the
project, a two-hundredth of Vietnam's, so its clause looked the safest. What moved was the
**drop**, from −0.0659 to −0.0345, because the reference happened to do worse on Thailand's
2010 on that draw. The direction, the ordering and the sign of the Vietnamese loss survive
both draws; the quantification against the reference's own noise does not, and it is withdrawn
in C42, the write-up, the node's `claim.md`, `readme-at-start.md` and the sidecar.

**The elapsed time is not a property of the analysis.** The agent ran the external check, two
outsider sessions, a release scan over 8 875 blobs and a report build on the same host while
an emulated amd64 container was the bottleneck. Measured: **7 rows in the first nine hours, 17
in the hour after the agent went quiet.** Recorded, because 14.87 h against batch 31's 11.6 h
would otherwise read as the external check's cost, and the external check is 1.4 h of it.

## 5. The outsider check, which found more than any other check in this project

Two agents on throwaway clones. **One was killed by an account spend limit**, and it was the
one asked to *write into the tree* — the task that in batch 18 found the plan's freeze rule
and the `combos` invariant contradicting each other. **That half of the check did not run**,
and it is recorded as not run.

The one that finished traced a reported number through **twenty-one links**, re-executed most
of them, and independently recomputed the mean CRPS, skill score, paired difference,
split-clustered standard error and coverage from the per-cell scores, reproducing all of them
to fifteen digits. It found:

**Two arithmetic errors of the agent's**, each in five places: the reference-spread ratio is
**218.6, not 215**, and Thailand is **36.2×** its band, not 35.

**The resolution yardstick had been applied to one number out of six.** The project's own line
for "cannot separate" is 1.03 standard errors. Computed for all six analyses:

| analysis | skill | SE from the reference |
|---|---|---|
| Laos, development | +0.1485 | 1.90 |
| **Laos, held-out year** | **+0.0868** | **0.94** |
| Vietnam, development | +0.0852 | 3.62 |
| **Vietnam, final year** | **−0.0862** | **0.97** |
| Thailand, development | +0.0856 | 1.45 |
| **Thailand, final year** | **+0.0197** | **0.49** |

**Five of six are below the project's own line, including the held-out headline it reports as
beating the reference.** The summary layer had also dropped the column that answers the
question: `external_conclusions.csv` carries `standard_errors_from_reference`, and neither of
the two files the summaries cite carries it through. Now **C48**, a table in the write-up, and
an entry in the report's §5.

**Two yardsticks that disagree.** Vietnam's development row is 3.62 standard errors from the
reference *and* inside the reference's own re-run spread. Nothing in the project had noticed
they were different quantities.

**Three provenance gaps**, two fixed: `driver.py` was the one script of record named without a
digest — the library that builds and executes every step of every combination; a sentence in
`report_external.md` that git contradicts; and a stale node path in an archived record, which
is appended as a correction because `Archive/` is never edited.

**And the one that stops the release.** `choose_weighting.py` builds its statement of what the
pool will contain from an **unfiltered** glob — the version `prepare_members.py` was fixed away
from in batch 22. Since then it has recorded a **six-member pool at 1/6 each with two-thirds of
its mass on required baselines**, where **four members at 1/4** ran; the run log prints both
statements two lines apart. **40 of 47 combinations say six, 7 say four.** No score moves —
the field that reaches the model configuration is unaffected — but the registered prediction is
written on a premise the file contradicts, and re-running one main-path step rewrites a
committed file **for a reason that is not the unseeded reference**. Fifth instance of the
fork-blindness family.

## 6. The release: scanned, assembled, not pushed

**No credential** in 4 840 tracked files or in 8 875 history blobs, across ten patterns, with
every blob streamed by hash so a credential removed in a later commit would still be found.

**Data permission cleared, and it had to be asked.** Two archived directories had no licence
statement and they hold the human's own unpublished documents — the manuscript, the proposal,
its supplement and the plan as delivered. The human set a standard Creative Commons licence on
2026-09-05; both provenance files record it, and all five archived directories now carry a
statement.

**The home-directory path, 3 965 occurrences, splits in two.** 3 927 are in run logs recording
commands that genuinely contained absolute paths; rewriting them would edit produced files,
invalidate 31 checksum manifests and 113 recorded digests, and make the next clean-room report
348 spurious differences. They stay, as a recorded decision. **Two were in source code and are
fixed**: `run_cleanroom.sh` and `cleanroom_compare.py` each named this machine's repository
path as a constant, so the harness a reader would most want to re-run only ran here. **No
tracked script carries the path.**

**Everything Rule 10 asks for is present and tracked**, and the **23 paths not taken across 17
forks all have an entry point** — counted, because an alternative nobody can run is a directory
and not a path.

**Feasibility remeasured, because both figures had grown**: `.git` is **189 MB** against the
131 MB batch 16 recorded, and the largest tracked file is **41.8 MB**, one of the external
check's Thai evaluations. Inside GitHub's limits.

## 7. The ten rules

| Rule | This batch |
|---|---|
| 1 — track results | Provenance for the inventory, the scan, the manifest, the clean-room and the plan drift; `driver.py`'s missing digest supplied |
| 2 — no manual manipulation | Nothing edited by hand. The archived record's stale path is appended as a correction, not applied in place |
| 3 — environment | Rebuilt from `lock.txt` from nothing by the clean-room, reporting *matches exactly, 174 packages* |
| 4 — version control | Nine commits; no change to `AGENTS.md`, `CLAUDE.md` or `.claude/` |
| 5 — intermediates | The clean-room's artefacts preserved before its 20 GB clone was discarded |
| 6 — seeds | Verified from cold: our models bit-identical, the reference unseeded and moving |
| 7 — plots | 220 figures, 220 with their plotted values |
| 8 — hierarchical report | Rebuilt, 69 combinations, 1 387 pages |
| 9 — claims | **C48 added**; C42 and C44 corrected |
| 10 — release | Scanned, assembled, **not pushed** |
| `/validate invariants` | Passes, all ten |

## 8. What is not done, and where it went

**Batch 32** — the `choose_weighting.py` premise. Its defence is built against the clean-room
run's own output, as batches 26, 30 and 28 each were against the run that preceded them. That
is why it was not fixed here: fixing it while the confirming evidence was still being gathered
would have thrown the evidence away.

**Batch 33** — create the remote and push. Both human answers are recorded, so batch 32 is its
only remaining blocker.

**The write-into-the-tree half of the outsider check**, lost to an account limit. Whether an
outsider following these instructions can still add an alternative is, after this batch,
unestablished.

## 9. For the human

- **The project has its case write-up, its reproducibility report, and a clean-room run that
  covers the whole tree.** What was missing at the start of this batch is no longer missing.
- **The most useful thing this batch produced is a withdrawn claim and a table of standard
  errors.** Both make the project's results weaker and more honest: five of six reported
  analyses cannot separate the model from the reference by the project's own line, and a
  clause about the drop that was true on one draw is false on the next.
- **The release is one batch away**, and the thing between it and the push is a defect the
  release would otherwise have shipped while claiming its checks supported it.
