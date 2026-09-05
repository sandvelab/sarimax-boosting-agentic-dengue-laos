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

## `26-09-02_cleanroom_comparison.json`

```
result:              26-09-02_cleanroom_comparison.json
script:              AI-internal/useful-scripts/cleanroom_compare.py
                     sha256:33010dd1c969900db39ef0ca95c6972ef96d61c6a99c4cc104708d67e9832c48
invocation:          .venv/bin/python cleanroom_compare.py
                     (from the clean-room directory holding the clone)
harness:             AI-internal/useful-scripts/run_cleanroom.sh
                     sha256:846911b2bf9dc8d8bb5a89164542979bf8b349557dddc7de69d910db55c8105f
                     bash run_cleanroom.sh — clones the repository at HEAD into a scratch
                     directory, builds environment/chapenv from environment/lock.txt, runs
                     analysis/run.sh from cold, and records git's own diff. Both files are
                     byte-identical to the versions batch 18 ran, verified by digest before
                     this run started, so this is the same check and not a new one.
inputs:              a git clone of this repository at ae0f62d, and the same repository's
                     working tree as the archive to compare against
environment:         the clone's own environment/chapenv — CPython 3.13.0, chap-core 2.1.0,
                     installed from environment/lock.txt and reported by install-chap.sh as
                     matching it exactly (174 packages). The comparison script itself runs
                     under .venv, standard library only.
seeds:               none in the comparison. The run it compares is seeded per component
                     except the reference model, which is unseeded and is the reason
                     anything moved at all.
commit:              ae0f62d
instructions-commit: ae0f62d
node:                not a node — a check on the method, like the determinism checks
produced:            2026-09-02, batch 25
```

**What it establishes.** That of 4 306 tracked files 3 458 came back identical; that on the
reported main path the ensemble, persistence and climatology mean CRPS are identical to the
last digit while the unseeded reference moved +0.285 CRPS; and that the reported skill score
therefore moved +0.0109, with `beats_reference` and `beats_all_baselines` still true.

**What it does not establish, and the field that says so.**
`rows_of_the_stability_manifest_reached` lists **32**, which is the whole development set —
batch 18's listed 8. But `conclusions` shows `main__holdout` with no moved fields, and **that
is not a reproduction**: the run exited 1 before the phase-E half, so those files are the
clone's committed copies and were never rewritten. Read the holdout half of this file as
absent rather than as verified. Why the run stopped is in
`26-09-02_cleanroomTier2Drift.json`.

agency: agent-autonomous.
information: agent-retrieved.

## `26-09-02_cleanroomTier2Drift.json`

```
result:              26-09-02_cleanroomTier2Drift.json
script:              AI-internal/useful-scripts/cleanroom_tier2_drift.py
                     sha256:3d98ea7e47493d565b2be298c0ff373ef987acf860a24c227277d240ce15deeb
invocation:          .venv/bin/python AI-internal/useful-scripts/cleanroom_tier2_drift.py
                     --archive . --cleanroom <clean-room>/repo
                     --out AI-generated/validation/26-09-02_cleanroomTier2Drift.json
under test:          analysis/05_stability/scripts/plan_manifest.py::select_tier2
                     sha256:ffb398e840ef13434e6531a9cacb7f04a94f07a6002c426e4b32942222a8fa23
                     and the rule it applies, results/tier2_rule.md, whose own sha256 is
                     recorded in results/manifest_notes.json by the batch that fixed it
inputs:              this repository's own analysis/05_stability/results/ as the archive,
                     and the clean-room clone's, both written by the same scripts at the
                     same commit. The clone's copies are preserved in
                     26-09-02_cleanroom-artefacts/ because the clone itself was discarded.
environment:         .venv (CPython 3.13.7, standard library only). It reads files; it runs
                     no analysis.
seeds:               none.
commit:              ae0f62d
instructions-commit: ae0f62d
node:                not a node — a check on the method
produced:            2026-09-02, batch 25
```

**What it establishes.** Three things, each from files both runs wrote.

**Ninety-six model-combination scores and not one of ours moved**: persistence and
climatology identical in all 32 combinations, the reported ensemble in all 27 it appears in,
`hier_nb` in 4 and `boosted` in 1, with zero moved between them. The unseeded reference moved
in 26 of 32 and is identical only in the 6 that inherit it rather than re-run it.

**The tier-2 selection is not reproducible.** `tier2_rule.md` ranks tier-1 rows by distance
in skill score from the main path, and skill divides by the reference. Groups S and A both
selected differently on a second draw, changing **six of the eight pairs**. The rule's own
deciding margins say it was never stable: group S was decided by **0.001002** of skill and
group A by **0.003211**, against a reference noise band of 0.043084 — and both flipped, while
group M's margin of 0.093547 did not.

**The band nearly doubled**, 0.021778 → 0.043084 (ratio 1.978), taking the phase-D headline
from **6 of 17 forks above it to 3**. The three that crossed did not move; the band did.

**The self-check that makes the tier-2 half readable.**
`tier2.reimplementation_reproduces_the_archived_selection` is **true**: applying this file's
copy of the rule to the archived conclusions returns exactly the eight pairs in
`manifest_holdout.csv`. The rule lives in a node script run under the pinned environment and
this is repository machinery run under `.venv`, so it is reimplemented here rather than
imported, and a reimplementation that had drifted would make the rest of the block
meaningless. If that field is ever false, nothing else under `tier2` should be believed.

agency: agent-autonomous.
information: agent-retrieved.

## `26-09-03_cleanroom_comparison.json`

```
result:              26-09-03_cleanroom_comparison.json
script:              AI-internal/useful-scripts/cleanroom_compare.py
                     sha256:33010dd1c969900db39ef0ca95c6972ef96d61c6a99c4cc104708d67e9832c48
invocation:          .venv/bin/python cleanroom_compare.py
                     (from the clean-room directory holding the clone, with FORCE_COLOR and
                     COLORTERM unset so git's output is not coloured)
harness:             AI-internal/useful-scripts/run_cleanroom.sh
                     sha256:846911b2bf9dc8d8bb5a89164542979bf8b349557dddc7de69d910db55c8105f
                     bash run_cleanroom.sh — clones the repository at HEAD into a scratch
                     directory, builds environment/chapenv from environment/lock.txt, runs
                     analysis/run.sh from cold, and records git's own diff. Both files are
                     byte-identical to the versions batch 18 and batch 25 ran, verified by
                     digest before this run started, so this is the same check run further.
inputs:              a git clone of this repository at 80276f3, and the same repository's
                     working tree as the archive to compare against
environment:         the clone's own environment/chapenv — CPython 3.13.0, chap-core 2.1.0,
                     installed from environment/lock.txt. install-chap.sh reported
                     "DOES NOT MATCH", which is a defect in that check and not in the
                     environment: see 26-09-03_cleanroomHoldoutReproduction.json, which
                     establishes the 174 packages are identical as sets. The comparison
                     script itself runs under .venv, standard library only.
seeds:               none in the comparison. The run it compares is seeded per component
                     except the reference model, which is unseeded and is the reason
                     anything moved at all.
commit:              80276f3
instructions-commit: 80276f3
node:                not a node — a check on the method
produced:            2026-09-03, batch 27
```

**What it establishes.** That of 4 329 tracked files 2 224 came back identical, 2 105 differ
and 5 are untracked; that on **both** reported paths the ensemble, persistence and
climatology CRPS are identical to the last digit while the unseeded reference moved
(+0.157361 on development, −0.227290 on the holdout); and that `beats_reference` and
`beats_all_baselines` are unchanged on both.

**What it does not establish.** `conclusions` covers `main` and `main__holdout`, and this
time **both were genuinely re-run** — unlike batch 25's, where the holdout half had to be
read as absent. But `analysis/run.sh` exited 1 at `pair_holdout_development.py`, so
`holdout_vs_development.csv`, `holdout_vs_development.json` and `fork_sensitivity_both.csv`
are the clone's committed copies and were never rewritten. This file reports them as
unchanged; that reading would be wrong, and why is in
`26-09-03_cleanroomHoldoutReproduction.json`.

agency: agent-autonomous.
information: agent-retrieved.

## `26-09-03_cleanroomTier2Drift.json`

```
result:              26-09-03_cleanroomTier2Drift.json
script:              AI-internal/useful-scripts/cleanroom_tier2_drift.py
                     sha256:3d98ea7e47493d565b2be298c0ff373ef987acf860a24c227277d240ce15deeb
invocation:          .venv/bin/python AI-internal/useful-scripts/cleanroom_tier2_drift.py
                     --archive . --cleanroom <clean-room>/repo
                     --out AI-generated/validation/26-09-03_cleanroomTier2Drift.json
under test:          analysis/05_stability/scripts/plan_manifest.py::select_tier2
                     and results/tier2_rule.md, whose sha256 is recorded in
                     results/manifest_notes.json
inputs:              this repository's own analysis/05_stability/results/ as the archive,
                     and the clean-room clone's. The clone's copies are preserved in
                     26-09-03_cleanroom-artefacts/ because the clone was discarded.
environment:         .venv (CPython 3.13.7, standard library only). It reads files.
seeds:               none.
commit:              80276f3
instructions-commit: 80276f3
node:                not a node — a check on the method
produced:            2026-09-03, batch 27
```

**What it establishes.** The development-half per-model table — persistence and climatology
identical in all 32 combinations, the reported ensemble in all 27 it appears in, `hier_nb` in
4 and `boosted` in 1, zero moved; the unseeded reference moved in all 32. That the tier-2
rule, applied to this run's own conclusions, would again choose **six different pairs** and
change groups S and A. And a **third** draw of the development noise band: 0.021778 archived,
0.034944 here, taking the headline from 6 forks of 17 to 3 — the same 3 batch 25 found.

Its self-check `tier2.reimplementation_reproduces_the_archived_selection` is **true**.

agency: agent-autonomous.
information: agent-retrieved.

## `26-09-03_cleanroomHoldoutReproduction.json`

```
result:              26-09-03_cleanroomHoldoutReproduction.json
script:              AI-internal/useful-scripts/cleanroom_holdout_reproduction.py
                     sha256:08c2e588f8eb19261c55c614db15c8b43656d867f5ed29ce6a4c38d841e1693c
invocation:          .venv/bin/python \
                       AI-internal/useful-scripts/cleanroom_holdout_reproduction.py \
                       --archive . --cleanroom <clean-room>/repo \
                       --artefacts AI-generated/validation/26-09-03_cleanroom-artefacts \
                       --out AI-generated/validation/26-09-03_cleanroomHoldoutReproduction.json
under test:          analysis/05_stability/scripts/pair_holdout_development.py
                     sha256:a7595ccfb60db109db366f9685b612ae6c6a9666f959ef261b44e1f08c72ece3
                     — the script whose assertion stopped analysis/run.sh
inputs:              both trees' analysis/results/*/conclusion.json and
                     analysis/05_stability/results/; and, for the environment section,
                     26-09-03_cleanroom-artefacts/freeze_raw.txt and lock.txt, which are the
                     clone's own files preserved before it was discarded
environment:         .venv (CPython 3.13.7, standard library only). It reads files; it runs
                     no analysis.
seeds:               none.
commit:              80276f3
instructions-commit: 80276f3
node:                not a node — a check on the method
produced:            2026-09-03, batch 27
```

**What it establishes.** Three things, new to this batch.

**Both halves reproduce.** 96 development and 96 holdout scores from models this project
wrote — persistence 32, climatology 32, ensemble 27, `hier_nb` 4, `boosted` 1 on each half —
and **0 moved**. The unseeded reference moved in all 32 combinations of both. This is the
first statement of it for the held-out year, which no clean-room run had reached before.

**The phase-E answer reproduces on the fields it reports.** `beats_the_reference` 26 of 32,
`beats_both_required_baselines` 27 of 32, 17 rows inside the noise band, and 5 forks above
the band — the same five by name — all identical. The four fields that moved are the skill
score, the reference CRPS, the rank within the distribution and the band itself, and each is
downstream of the unseeded reference. The holdout band is nearly steady across draws
(0.014023 → 0.013410) where the development band is not.

**Why the run stopped, stated against the data rather than the message.**
`pair_holdout_development.py` raised on **32 drifted rows**; the number of rows whose
*pairing* moved is **0**, and `manifest_holdout.csv` is byte-identical between the two trees.
Every drift is inside the noise band this run measured for itself — largest −0.025673 against
0.034944. The script's message says the pairing has changed; the pairing has not.

**The environment section** answers the question `install-chap.sh` meant to ask: 174 lines
came back colour-wrapped, and the package sets are identical once the escapes are stripped.
The mismatch was the check's output, not the environment. Fixed in `install-chap.sh` in this
batch.

agency: agent-autonomous.
information: agent-retrieved.

---

## 26-09-03_pairingDefence.json

Five situations put to the frozen-pairing check that batch 30 rebuilt in
`analysis/05_stability/scripts/pair_holdout_development.py`, one of them driven by the
clean-room run's own outputs — the data that stopped batch 27 at the last script in the tree.

```
produced-by:  AI-internal/useful-scripts/check_pairing_defence.py
              sha256:3336fefeed8e432260182931d36c50edf0f7a2f38ee72111e6537a89c392bde8
invocation:   .venv/bin/python AI-internal/useful-scripts/check_pairing_defence.py --root .
inputs:       analysis/05_stability/results/ (the archived tree, restored from git after
              every scenario)
              AI-generated/validation/26-09-03_cleanroom-artefacts/conclusions.csv
              AI-generated/validation/26-09-03_cleanroom-artefacts/distribution.json
environment:  .venv (repository machinery); the node script under test is invoked under
              environment/chapenv, per AGENTS.md §8
commit:       78fd76a
produced:     2026-09-03
```

**All five pass.** The one that matters is `drifted_frozen_figures`, which swaps in the
clean-room run's `conclusions.csv` **and its own `distribution.json`** rather than a
synthetic perturbation — both from the same run, because the band the drift is measured
against has to be the one that run drew for itself (0.034944) and not batch 15's (0.021778).
Against that input the fixed script **exits 0**, reports **32 drifted figures and 0 moved
pairings**, records the largest move as **0.025673 inside a band of 0.034944**, and compares
on the frozen figures — verified by hashing the `development_skill_score` column of the
output table before and after.

`pairing_moved` removes a development twin from the table and confirms the run **exits 1 and
writes nothing**: `holdout_vs_development.json` is byte-identical after the attempt. This is
the case the old message claimed and the data never showed.
`beats_reference_comes_from_the_freeze` inverts `beats_reference` on every development row
and confirms the output does not move — the regression test for the second defect this batch
found. `twin_without_a_conclusion` blanks one twin's skill score and confirms it is reported
rather than fatal, and `the_output_is_stable` confirms two runs on the archived tree produce
byte-identical files.

Each scenario restores from git unconditionally, so the tree is as it was found; nothing
touches `manifest_holdout.csv`.

agency: agent-autonomous.
information: agent-retrieved.

---

## 26-09-04_cleanroom.md, 26-09-04_cleanroom_comparison.json, 26-09-04_cleanroom-artefacts/

`/validate cleanroom` on the tree batch 30 repaired: the repository cloned at `c94e85f`, the
analysis environment built from `environment/lock.txt`, and `bash analysis/run.sh` from cold.
**It exited 0** — the first clean-room run in this project to reach the end of the tree.

```
produced-by:  AI-internal/useful-scripts/run_cleanroom.sh
              sha256:846911b2bf9dc8d8bb5a89164542979bf8b349557dddc7de69d910db55c8105f
              AI-internal/useful-scripts/cleanroom_compare.py
              sha256:33010dd1c969900db39ef0ca95c6972ef96d61c6a99c4cc104708d67e9832c48
invocation:   nohup caffeinate -ims bash AI-internal/useful-scripts/run_cleanroom.sh
              .venv/bin/python AI-internal/useful-scripts/cleanroom_compare.py
inputs:       the repository at commit c94e85f (git clone of the working tree)
              environment/lock.txt (174 packages)
              Docker, for the reference model's amd64 chapkit image under emulation
environment:  environment/chapenv built from the lockfile inside the clone, for the analysis;
              .venv for the comparison, per AGENTS.md §8
commit:       c94e85f
produced:     2026-09-04
seeds:        the project seed as the tree derives it; the reference model is unseeded
```

Both scripts are **byte-identical to the versions batch 27 verified** — `846911b2…` and
`33010dd1…` — so this is the same check run further rather than a new one.

`analysis/run.sh` exited **0** after **41 677 s** (694 min). The run was detached from the
session and held awake with `caffeinate -ims`; the session's wait process was killed three
times and the analysis was untouched. Batch 27's 81 335 s was wall clock across a sleeping
host and was not readable as compute. This figure is.

Of 4 366 tracked files, **2 248 came back byte-identical**, 2 118 differ in something
computed, **0** differ only in the repository path, and 5 are untracked in the clone — the
same five `member_selection.json` files batch 27 found, for five setup combinations not
re-run since batch 14 added the file.

The clone was 18 GB and has been discarded. `26-09-04_cleanroom-artefacts/` holds what the
run wrote, with a README, so the findings can be re-checked without re-running from cold.

agency: agent-autonomous.
information: agent-retrieved.

---

## 26-09-04_cleanroomTier2Drift.json

Whether the tier-2 selection rule, applied to this run's own tier-1 conclusions, chooses the
recorded eight pairs — and what the reference model's four repeats did to the development
noise band.

```
produced-by:  AI-internal/useful-scripts/cleanroom_tier2_drift.py
              sha256:3d98ea7e47493d565b2be298c0ff373ef987acf860a24c227277d240ce15deeb
invocation:   .venv/bin/python AI-internal/useful-scripts/cleanroom_tier2_drift.py \
                  --archive . --cleanroom AI-internal/useful-scripts/repo \
                  --out AI-generated/validation/26-09-04_cleanroomTier2Drift.json
inputs:       analysis/05_stability/results/ (the archive)
              the clean-room clone's analysis/05_stability/results/
environment:  .venv (repository machinery)
commit:       c94e85f
produced:     2026-09-04
```

Byte-identical to the version batch 27 verified (`3d98ea7e…`).
`reimplementation_reproduces_the_archived_selection: true`, so the rest of the block is
readable. The rule **would** now choose **six different pairs** and the tier-1 order **would**
move three positions; batch 26's machinery reported both and the recorded selection ran. That
is the third independent draw this check has absorbed.

The development noise band is **0.048273** against batch 15's 0.021778, and **3** of 17 forks
clear it against 6. Four draws now read 0.021778, 0.043084, 0.034944, 0.048273 and 6, 3, 3, 3.

agency: agent-autonomous.
information: agent-retrieved.

---

## 26-09-04_cleanroomHoldoutReproduction.json

Per model and per combination, on both halves: whether the CRPS came back identical. Plus the
phase-E headline archived beside the clean-room's, the environment comparison, and the
comparison against the frozen development figures.

```
produced-by:  AI-internal/useful-scripts/cleanroom_holdout_reproduction.py
              sha256:1f8fb33606534854b770b7cc1cd1e349a99eef38db97310135368a2d5364a13a
invocation:   .venv/bin/python AI-internal/useful-scripts/cleanroom_holdout_reproduction.py \
                  --archive . --cleanroom AI-internal/useful-scripts/repo \
                  --out AI-generated/validation/26-09-04_cleanroomHoldoutReproduction.json \
                  --artefacts AI-generated/validation/26-09-04_cleanroom-artefacts
inputs:       analysis/results/*/conclusion.json in both trees
              analysis/05_stability/results/{manifest_holdout,conclusions}.csv, both trees
              26-09-04_cleanroom-artefacts/{freeze_raw.txt,lock.txt,install_env.log}
environment:  .venv (repository machinery)
commit:       c94e85f
produced:     2026-09-04
```

**The script was changed in this batch** and the digest above is the changed version.
Two things in it described batch 27 rather than the run it is pointed at: `environment_check`
hardcoded `install_chap_sh_reported: "DOES NOT MATCH environment/lock.txt"`, which batch 27's
own fix to `install-chap.sh` has since made false; and the payload key `why_the_run_stopped`,
with `rows_it_stopped_on` inside it, named a failure on a run that exits 0. The environment
block now reads the reported line out of `install_env.log`, and the key is
`the_frozen_figure_comparison` with `rows_whose_frozen_figure_drifted`. No arithmetic changed.

**192 model-combination scores from models this project wrote — 96 development, 96 holdout —
and 0 moved.** The unseeded reference moved in all 32 combinations on both halves, for each
of its four repeats and their mean.

Environment: `matches environment/lock.txt exactly (174 packages)`, **0 lines carrying ANSI
colour**, sets identical, nothing in one and not the other. Batch 27's repair verified from
cold.

Phase E: CRPS of the reported model, its rank, `beats_the_reference` (26 of 32) and
`beats_both_required_baselines` (27 of 32) all **identical**. The skill score, the reference
CRPS, the noise band, the rows inside it and the forks above it all moved with the reference.
The held-out band is **0.050443** against the archive's 0.014023, which contradicts batch 27's
report of a steady held-out band across two draws.

The frozen-figure comparison: **32 drifted, 0 pairings moved**, `manifest_holdout.csv`
identical, largest move **+0.051016** against a band of 0.048273 —
`all_within_the_development_noise_band: false`.

agency: agent-autonomous.
information: agent-retrieved.

---

## 26-09-04_cleanroomPhaseEAnswer.json

The three files `pair_holdout_development.py` writes, archived beside the clean-room's,
classified field by field. Batch 27 exited 1 at that script, so those three were carried
unchanged out of the clone's index and its comparison reported them identical; a file that
was never written cannot have reproduced. This is the first run in which they exist to
compare.

```
produced-by:  AI-internal/useful-scripts/cleanroom_phase_e_answer.py
              sha256:9b41d408c741ec642e24f69529cc9cbb30b123eff4a4a15bc6c2d8a7324ac89e
invocation:   .venv/bin/python AI-internal/useful-scripts/cleanroom_phase_e_answer.py \
                  --archive . \
                  --artefacts AI-generated/validation/26-09-04_cleanroom-artefacts \
                  --out AI-generated/validation/26-09-04_cleanroomPhaseEAnswer.json
inputs:       analysis/05_stability/results/{holdout_vs_development.json,
              holdout_vs_development.csv,fork_sensitivity_both.csv}
              the same three in 26-09-04_cleanroom-artefacts/
environment:  .venv (repository machinery)
commit:       c94e85f
produced:     2026-09-04
```

Written in this batch. Each scalar is classified as **reference-derived** or **structural**
by a field path listed in the script rather than by a heuristic, so a field added later is
classified deliberately.

`holdout_vs_development.csv`: **544 of 640 cells identical**, same 32 rows by name. Three
columns moved — `holdout_crps_reference`, `holdout_skill_score`,
`skill_holdout_minus_development` — and **every development column held**, including the two
batch 30 made read from the freeze. `development_beats_all_baselines`, which batch 30 named
as re-derived and therefore able to move, did not move on this draw.

`holdout_vs_development.json`: 56 of 80 scalars identical, 14 reference-derived moved, 10
structural — four of which are the `frozen_pairing_verified` block reporting the drift, which
is what it exists to do.

`fork_sensitivity_both.csv`: 129 of 221 cells identical; only `fork`, `stage`, `kind` and
`owner` held, because every numeric column is measured against a band that moved.

**The finding**: `agreeing_on_whether_the_fork_matters` came back **identical at 14**, while
`matter_on_both` went from four forks to one and the two sets share only `family`. A reported
number reproduced exactly and does not mean the same thing in the two runs. Every check this
project has compares values, so all of them call that field reproduced.

agency: agent-autonomous.
information: agent-retrieved.

---

## `26-09-04_poolCheckRewrite.json` — what batch 28's rewrite of the pool checks changed

```
result:       AI-generated/validation/26-09-04_poolCheckRewrite.json
script:       AI-internal/useful-scripts/pool_check_rewrite.py
              sha256:dd1a43760f823b059141848bd0d6f2e31c2250aa937b5a1ebdd1689a0a063330
invocation:   .venv/bin/python AI-internal/useful-scripts/pool_check_rewrite.py
inputs:       analysis/03_models/03_candidate/c_ensemble/results/*/pool_check.json,
              each against its own version at HEAD, read with `git show`
environment:  .venv (repository machinery)
commit:       9a0f8e7
produced:     2026-09-04
```

Batch 28 replaced the tie-break by which `check_pool.py` names the stored evaluation each
pool member is compared against, and rewrote all 51 `pool_check.json` files. The claim that
follows — that nothing computed moved — is a comparison of two versions of every file, so it
is computed rather than read off a diff: both versions are flattened to their leaves and
every differing key is classified as a **naming** change, the added **annotation**, a
**reconstruction** that appeared, or a **numeric** change to a value that existed before.

**43 files changed in naming and annotation only. Four gained the reconstruction they had
been run too early to have** — `main__holdout`, `climatology_frozenWindow__holdout`,
`persistence_negBinomialFloor__holdout`, `weighting_crpsWeighted__holdout`. Four gained a
member match without gaining a reconstruction. **No number that existed before moved, no row
lost anything, and every `mean_crps_as_run` is unchanged.** The script exits 1 if either of
the last two is false.

agency: agent-autonomous.
information: agent-retrieved.

---

## `26-09-04_reconstructionSweepDefence.json` — four states put to batch 28's sweep

```
result:       AI-generated/validation/26-09-04_reconstructionSweepDefence.json
script:       AI-internal/useful-scripts/check_reconstruction_defence.py
              sha256:e13175b8e2794295fe937fc2b035ae0e40f267952ee8780b1e1f137bf412dab2
invocation:   .venv/bin/python AI-internal/useful-scripts/check_reconstruction_defence.py
inputs:       analysis/03_models/03_candidate/c_ensemble/results/{main,main__holdout,
              covariates_rich}/pool_check.json, and each of their versions at commit
              96f1205 — the last commit before batch 28 rewrote them
environment:  .venv (repository machinery); it drives
              analysis/05_stability/scripts/reconstruct_pools.py under environment/
commit:       b47f6f2
produced:     2026-09-04
```

`reconstruct_pools.py` exists so that a `pool_check.json` written before its members had been
evaluated separately does not stay that way — a claim about conditions this repository is not
in, since every combination has run here. So the repository is put into them, one file at a
time: **the record batch 16 left** on the headline holdout row, restored from `96f1205`; **a
file that is already right**; **a file that is missing entirely**; and **a row no order of
execution could reconstruct**, `covariates_rich`, which moves a fork inside candidate 1.

All four pass. The early record is rewritten to 76.646; the correct file is neither re-run
nor touched; the missing file is produced with the same reconstruction; and the row that
cannot be reconstructed is left saying so, still naming candidate 1 as the member it lacks,
rather than reaching into another combination's directory. Every file is restored to its
committed digest and `analysis/` is left clean by git's own account, which the check verifies
and exits non-zero without.

agency: agent-autonomous.
information: agent-retrieved.

## `26-09-04_externalPlanDefence.json` — four situations put to the external plan's record

```
result:       AI-generated/validation/26-09-04_externalPlanDefence.json
script:       AI-internal/useful-scripts/check_external_plan_defence.py
              sha256:67c9f1289daa6cb7edda7bc85a35baa76e9392a0a3db8fe382bc737ba4c1992d
invocation:   .venv/bin/python AI-internal/useful-scripts/check_external_plan_defence.py
inputs:       analysis/06_external/results/manifest_external.csv
              analysis/06_external/results/external_plan.json
              analysis/05_stability/results/run_status_holdout.csv
              each restored from HEAD after every scenario
environment:  .venv (repository machinery); it drives
              analysis/06_external/scripts/plan_external.py under environment/
commit:       a715ffc
produced:     2026-09-04
```

Batch 20's external plan carries an estimate built from a **measured wall-clock duration** —
the seconds the held-out `main` row took — and `05_stability/run.sh` rewrites that
measurement on every run, one step before this node. A planning script that recomputed itself
would therefore come back different from a clean checkout, and the claim that the plan was
committed before the rows ran would be a claim about a file that had since been rewritten.
Fourth instance of the family batches 24, 26 and 30 addressed.

The split is theirs: **rows are structural and a disagreement is fatal; the estimate is a
measurement and a drift is reported**. Four situations, all passing — the record as
committed (nothing rewritten, no drift); the cost unit changed by the size and direction
batch 31's clean-room run changed it (exit 0, four estimates reported as drifted, manifest
byte-identical); a structural field moved (exit 1, nothing written, the message naming
`main__tha.cells`); and no record at all (the plan written, and from this tree identical to
the record — from a tree whose stability half had re-run it would not be, which is the whole
reason the record exists). Every file is restored from git after each scenario and the
harness refuses to start against an uncommitted one.

agency: agent-autonomous.
information: agent-retrieved.

---

## `26-09-05_cleanroom.md` and `26-09-05_cleanroom-artefacts/` — the run with 06_external in it

```
result:       AI-generated/validation/26-09-05_cleanroom.md
              AI-generated/validation/26-09-05_cleanroom-artefacts/   (35 files)
              AI-generated/validation/26-09-05_cleanroomPhaseEAnswer.json
harness:      AI-internal/useful-scripts/run_cleanroom.sh
comparison:   AI-internal/useful-scripts/cleanroom_compare.py
              sha256:27e0ab124e6657c6321e66bd3cffdbd53422f37e79e75985a08561e9e35d40ce
              AI-internal/useful-scripts/cleanroom_phase_e_answer.py
invocation:   nohup caffeinate -ims bash AI-internal/useful-scripts/run_cleanroom.sh
              then .venv/bin/python AI-internal/useful-scripts/cleanroom_compare.py
inputs:       a git clone of the repository at commit 6d6ad7c, with environment/chapenv
              built from environment/lock.txt by environment/install-chap.sh
environment:  the clone's own environment/ (CPython 3.13.0, chap-core==2.1.0, 174 packages),
              built from nothing; Docker for the pinned amd64 reference image
seeds:        unchanged. Our models derive their component seeds from the project seed; the
              reference is unseeded and is what moved.
commit:       1e0f6f7
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:         not a node — a check on the method
produced:     2026-09-05
exit status:  0, after 53 514 s (891 min)
agency:       agent-autonomous
```

**What it establishes.** The reported pool returns 18.816872064690028 on development and
76.73108261979166 on the held-out year, digit for digit, from a checkout that built its own
environment. Across the tree's leaderboards, **207 of 207 scores from models this project
wrote are identical** and 340 of 345 reference scores are not. 2 511 of 4 790 tracked files
came back byte-identical.

**Why the elapsed time is not a property of the analysis.** The agent ran the external check,
two outsider agent sessions, a release scan over 8 875 git blobs and a hierarchical-report
build on the same host while an emulated amd64 container was the run's bottleneck. Measured:
7 rows in the first nine hours, 17 in the hour after the agent went quiet. Batch 31's
comparable figure is 11.6 h for a tree without the external check.

**The scratch clone is gitignored rather than deleted by hand**, since batch 19. It was
removed after the artefacts were copied out.

---

## `26-08-31_outsider.md` and `26-09-05_outsider.md` — the two outsider checks

**Written on 2026-09-05, batch 19**, when `/log-tasks` found that neither outsider record had
a section here. Batch 18's has been in the repository since 2026-08-31 without one; this
covers both, and says so rather than backdating.

```
result:              AI-generated/validation/26-08-31_outsider.md   (batch 18)
                     AI-generated/validation/26-09-05_outsider.md   (batch 19)
script:              none. An outsider check is not a script — it is agent sessions given a
                     clone and a task, which is why it finds what deterministic code cannot.
invocation:          two throwaway `git clone`s per run, each handed to a fresh agent with
                     no conversation history and one task. Batch 18 at commit ad7e64f;
                     batch 19 at 922506b. The tasks are quoted verbatim in each record.
inputs:              the repository at the commit named, and nothing else — no summary, no
                     hint about what was known to be weak. That is the whole method: an
                     outsider has what a reader would have.
environment:         each agent's own; the clones built nothing beyond what their task
                     needed. Batch 19's agent re-ran four analysis scripts under system
                     CPython with pandas 2.3.0 and numpy 2.3.0 rather than the pinned
                     versions, and reported that they came back byte-identical.
seeds:               none, and this is the entry's honest limit — see below.
commit:              ad7e64f (batch 18), 922506b (batch 19)
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/) for batch 19
node:                not a node — a check on the method
produced:            2026-08-31 and 2026-09-05
alternatives-considered: asking an agent whether the instructions are clear. Rejected in
                     `AGENTS.md` §5 and by both runs' results: a system asked whether
                     instructions are clear says yes, and a system asked to follow them
                     fails visibly at the ambiguous step.
agency:              agent-autonomous for the tasks and for verifying every finding before
                     acting on it; that the check runs before release is the plan's.
```

**This is the one record in the repository that cannot promise reproduction.** Re-running an
outsider check at the same commit with the same task will not return the same findings: the
agents are not seeded, they are not the same agents, and what they happen to look at is not
determined. What the record fixes is the **conditions** — the commit, the task, what the agent
was and was not given — so that a reader can judge whether the check was fair, and can run
another one.

**What each run cost and found** is in the documents themselves. Batch 18: six defects, three
wrong numbers and one broken link in the headline result's chain. Batch 19: two wrong numbers,
one systematic omission across five of six reported analyses, two yardsticks that disagree,
three provenance gaps and one defect in forty committed files. `/validate invariants` passed
before and after both.

**Batch 19's run is incomplete and the record says so.** One of its two agents was killed by
an account spend limit, and it was the one asked to write into the tree — the half that in
batch 18 produced the finding about the freeze rule. Whether an outsider can still add an
alternative to this tree is unestablished.

**agency:** agent-autonomous.
