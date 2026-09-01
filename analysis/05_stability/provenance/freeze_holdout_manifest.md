# Provenance — the frozen phase-E set

```
result:              results/manifest_holdout.csv
                     results/holdout_freeze.json
script:              scripts/freeze_holdout_manifest.py
                     sha256:ca92a098f7ee5708190b4934ffea286737968fc73e0955cc466a6739823584cf
invocation:          "$PYTHON" scripts/freeze_holdout_manifest.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/05_stability/results/manifest.csv
                     analysis/05_stability/results/conclusions.csv
                     analysis/05_stability/results/manifest_notes.json
                     analysis/05_stability/results/tier2_rule.md
                     analysis/05_stability/results/distribution.json
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              9ad6578
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** The deliverable the plan's §3 makes phase E depend on: the exact
set of analyses to be run on the held-out year, committed **before** the year is opened.
Thirty-three rows — the development manifest's own rows under `__holdout` names — at an
estimated **2.07 h**, against a 12 h budget for both datasets of which development spent
3.66 h. Nothing is cut.

**The pairing is frozen with the set.** Each row carries the development skill score, CRPS,
reference CRPS, coverage and model it is to be reported beside. Freezing which analyses run
and then assembling the development half of the comparison afterwards would leave the
comparison selectable after the fact even though neither half was, and the plan asks for
development and holdout spreads to be read on one axis.

**The rows are renamed and that is a decision, not bookkeeping.** A holdout row writes under
`analysis/results/<combination>/`, so reusing the development names would overwrite the
results the holdout is to be reported against. Every row is its development name with
`__holdout` appended. `check_invariants.check_combos` now reads both manifests, so a holdout
directory is planned exactly as a development one is and one nobody planned still fails.

**What the freeze refuses.** The script will not write a set whose development half is
unfinished: every row must have a conclusion or a reason that is not "waiting for a batch",
every tier-2 slot must be resolved, and `tier2_rule.md` must still hash to what
`manifest_notes.json` recorded before tier 1 ran. A holdout set frozen around the rows that
happened to finish would be chosen by the running order.

**What is deliberately left open.** How `02_setup` is pointed at the full file rather than
at the development file does not exist yet and is batch 16's implementation.
`holdout_freeze.json["left_to_batch_16"]` records the constraint it works under: it may not
change the rows, the scheme, the models or the pairing.

alternatives-considered: **freezing only tier 1 and running tier 2 on the holdout only if
the budget allowed** — rejected: tier 2 is where this project measured that fork effects do
not compose, so a holdout half without it would be a spread computed under an assumption
development has already falsified, and at 2.07 h against 12 there is no budget argument for
it. **Recording the freeze as a git tag rather than a file** — rejected, because a tag is
not readable by the checks or by a reader with the tree in front of them; the commit that
adds this file is the evidence, and the file says so.

agency: agent-autonomous, inside a constraint that is human-set — the plan's §3 fixes that a
holdout manifest exists and is frozen before the holdout opens. What is in it is the
agent's.
information: agent-retrieved — every value read from the files named above.

---

## Correction (batch 16): `frozen_at_commit` is read from git, not recomputed

The field recorded HEAD at the moment the file was written, so every later run of this
script overwrote the evidence it exists to carry. Batch 16 ran the script once after the
holdout and watched `f3904c5` become that run's own commit. It now reads the commit that
*adds* `results/manifest_holdout.csv` — **937fd5c**, batch 15's — from `git log
--diff-filter=A`, which cannot be overwritten by running the script again. Before the
manifest is committed at all there is no such commit and the field is HEAD, which is then
the commit the freeze was computed at, and the note beside it says so.

The correction changes `holdout_freeze.json` and nothing else: `manifest_holdout.csv` comes
back byte-identical after the whole holdout set has run, which is the property that makes
editing this script safe at all. It was checked before the change and again after.

`f3904c5` was one commit before `937fd5c` and both predate any file under
`analysis/results/*__holdout/`, the first of which appears at `895a9f8`. So the earlier
value was not misleading about the seal; it was simply a value that a re-run would destroy.


---

## Batch 23 — the digest of that correction

```
result:              results/holdout_freeze.json
                     results/manifest_holdout.csv (unchanged by the correction)
script:              scripts/freeze_holdout_manifest.py
                     sha256:7726bef9e8d35b0965c341f04e55cfe25c4093c763d03fd9aa12c4fe13d8cb4b
invocation:          "$PYTHON" scripts/freeze_holdout_manifest.py
                     (from 05_stability/, via run.sh)
inputs:              results/manifest.csv, results/conclusions.csv, results/tier2_rule.md,
                     and git, for the commit that adds results/manifest_holdout.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              48edaea
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31; recorded 2026-09-01
```

The section above describes the correction and this one carries its digest, which that
section did not: it is prose with no `script:` block, so the record went on naming
`ca92a098…`, the version whose `frozen_at_commit` recorded HEAD. The current version reads
that field from `git log --diff-filter=A` and the field now holds **937fd5c**.

This is the record where a stale digest would have cost the most per byte. The field exists
to evidence that the phase-E set predates the year being opened; a reader checking that claim
reaches for this record, and it named a script that could not have produced the value they
are looking at.

alternatives-considered: none new — the correction's own alternatives are in the section
above.

agency: agent-autonomous.
information: agent-retrieved — the digest is computed from the file and the change read from
the diff at `48edaea`.


---

## Batch 24 — the freeze wins over the recomputation

```
result:              results/holdout_freeze_check.json
                     results/manifest_holdout.csv (unchanged, and now unchangeable here)
                     results/holdout_freeze.json (unchanged, and now written once)
script:              scripts/freeze_holdout_manifest.py
                     sha256:8bc160edcac6f70b0e28327d09f1cee76a10e30520d3e8ac881ca8cc4c9e59b2
invocation:          "$PYTHON" scripts/freeze_holdout_manifest.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/05_stability/results/manifest.csv
                     analysis/05_stability/results/conclusions.csv
                     analysis/05_stability/results/manifest_holdout.csv
                     analysis/05_stability/results/holdout_freeze.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              595c32d
instructions-commit: 595c32d
node:                analysis/05_stability
produced:            2026-09-01
```

**What it establishes.** That this script no longer rebuilds the set it exists to fix. It is
the last step of the development half of `run.sh`, so every run of `analysis/run.sh`
re-derived the frozen manifest from
whatever the development manifest said at that moment; it returned the same bytes because
the tree had not changed, not because anything made it. `plan_manifest.py`, five lines above,
re-derives the development manifest by design, and since the clarification of 2026-09-01 that
manifest may legitimately grow — so a fork child added after the opening was one run of
`analysis/run.sh` away from entering the frozen set with no batch and no decision behind it.
Batch 18 added one and watched thirty-three rows become **thirty-four**.

The frozen file is now authoritative and the script has two modes. If it does not exist this
is the freeze, as it was in batch 15. If it exists this is a verification: the set the tree
would produce now is derived and compared, `manifest_holdout.csv` and `holdout_freeze.json`
are not written at all, and the comparison goes to `results/holdout_freeze_check.json`.

**What a difference does, and why it is not uniform.** A development row with no frozen twin
is reported as **unpaired** and never added — that is plan §3 as clarified on 2026-09-01,
which binds this manifest and not the tree. A frozen row the tree no longer carries, or one
whose structural columns moved, is **fatal**: the frozen set can no longer be reproduced, and
the run stops rather than the file being adjusted. A frozen row whose *numbers* moved is
recorded and not fatal, because the reference model is unseeded and batch 18's clean-room run
moved the development skill score by 0.0065 with nothing wrong.

**A second hole, not previously reported, closed by the same change.** `holdout_freeze.json`
carries `frozen_on`, and it was written from `date.today()` on every invocation. Batch 16
found and fixed the same failure in `frozen_at_commit` and left the date beside it: run today,
the superseded script rewrote **2026-08-31 → 2026-09-01**, and the other eighteen keys were
identical. The date the phase-E set was frozen was being overwritten by every run of the
analysis. It is now written once, because the file carrying it is.

**What was checked, and how.** `AI-internal/useful-scripts/check_freeze_defence.py` puts
eleven situations to the two defences on throwaway copies — four of them corrupt the frozen
manifest, which is why none runs against the live tree. All eleven behave as specified
(`AI-generated/validation/26-09-01_freezeDefence.json`). Two matter most: **`added`** produces
a 34-row frozen set under the superseded script and a 33-row one plus an unpaired row under
this one; and **`refreeze_from_cold`**, which deletes the frozen file with no trace of the
opening and gets back a manifest **byte-identical** to the one frozen in batch 15 — the
evidence that restructuring the script did not restructure the set. Run against the
superseded version, six of the seven script scenarios fail and every one of them exits 0.

alternatives-considered: **failing on an added development row rather than reporting it
unpaired** — rejected, because `/validate invariants`'s `combos` check requires every non-main
child in the tree to have a development row, so failing would make the two rules contradict
each other, which is the ambiguity batch 18's outsider check hit and the human settled on
2026-09-01 in favour of the narrow reading. **Failing on a drifted development conclusion** —
rejected: the reference is unseeded, so a clean-room run of `analysis/run.sh` would fail on
its own honest re-draw, and batch 25 is that run. **Deleting the freeze path entirely, since
the set is frozen and never freezes again** — rejected, because it is the path a reader
implementing this method runs, and a script that cannot demonstrate how the set was produced
is a set with an assertion behind it rather than a derivation.

agency: agent-autonomous, inside a constraint that is human-set — plan §3 fixes that the
holdout manifest is frozen before the year opens, and the 2026-09-01 clarification fixes what
that binds. Which failures are fatal and which are reported is the agent's.
information: agent-retrieved — every value read from the files named above, and the
superseded script's behaviour from running it.
