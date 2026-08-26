# validation

What `/validate` produced, one file per run, named `YY-MM-DD_<check>.md`.

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

`/validate outsider` has not been run in this repository yet. It is batch 18's.
