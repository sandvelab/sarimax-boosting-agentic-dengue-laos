# validation

What the checks on the method produced, one file per run, named `YY-MM-DD_<check>.md`.
Mostly `/validate`; batch 24 added a targeted check written for one defect, which belongs
here for the same reason.

These are records of checks on the **method**, not analysis results: they say whether the
repository does what it claims, and they belong here rather than in `analysis/` for the same
reason `check_invariants.py` lives in `AI-internal/`.

`/validate invariants` is deterministic code run at the end of every batch and its outcome
is recorded in that batch's report rather than here. `/validate cleanroom` and
`/validate outsider` produce enough to be worth their own document, and that is what is
here.

## Currently

- `26-08-26_cleanroom.md` — batch 7. The `environment/` Docker layer builds for the first
  time; `01_data` and `02_setup` reproduce byte-identically and both baselines reproduce
  their per-cell scores exactly. Two small differences reported rather than waved away, and
  one defect found on the way: `install-chap.sh` was writing `lock.txt` rather than
  installing from it.
- `26-08-31_outsider.md` — batch 18, and the first outsider run here. Two fresh agents with
  no context, one writing into the tree and one tracing the headline result back to the
  archived data. Six defects, three wrong counts — one of them in the claim collection — and
  a provenance record naming a commit that is not in the history and would have vanished on
  the first push. What was fixed, what was deferred to batches 23 and 24, and the two
  questions carried to the human are all in it.
- `26-09-01_cleanroom.md` — batch 18, and the first clean-room run that could reach the
  reference model, batch 7's having run inside a container where it cannot. **Interrupted at
  8 of 32 stability rows**, and it says so: what it verified is the reported main path, where
  every model this project wrote reproduces its mean CRPS to the last digit and the unseeded
  reference moves the headline skill score by 0.0065. The two distributions are unverified
  from cold and the phase-E half has never run from a clean checkout; that is batch 25.
  Its figures are in `26-09-01_cleanroom_comparison.json`, with `provenance.md` beside it.
- `26-09-02_cleanroom.md` — batch 25, and the run that finished the development half and
  was **stopped by the project's own freeze check**. `analysis/run.sh` exited 1 after 3 h 48 m:
  the development manifest's tier-2 rows are *selected* from tier-1 skill scores, which divide
  by the unseeded reference, and a second draw re-selected six of the eight pairs — so the
  frozen phase-E set has a derivation a clean checkout cannot reproduce. What it did verify is
  stronger than batch 18's: **96 model-combination scores and not one of ours moved**, while
  the reference moved in 26 of 32. It also found the noise band nearly doubled, taking phase
  D's headline from six of seventeen forks to three. Figures in
  `26-09-02_cleanroom_comparison.json` and `26-09-02_cleanroomTier2Drift.json`; the run's own
  outputs in `26-09-02_cleanroom-artefacts/`.
- `26-09-01_freezeDefence.md` — batch 24, and not a `/validate` run: eleven situations put
  to the two defences of the frozen phase-E set, on throwaway copies. The set stops being
  rebuilt on every run of `analysis/run.sh`, and the file is now checked as well as the
  script that writes it. Its figures are in `26-09-01_freezeDefence.json`.
- `26-09-02_selectionDefence.json` — batch 26, and like `26-09-01_freezeDefence` not a
  `/validate` run: five situations put to the recorded tier-1 order and tier-2 pairing that
  replaced `plan_manifest.py`'s re-derivation. One of them is driven by the clean-room run's
  own `conclusions.csv` — the data that made batch 25 exit 1 — and the recorded pairs stand
  while the rule, reported beside them, would choose six different ones. All five pass.
