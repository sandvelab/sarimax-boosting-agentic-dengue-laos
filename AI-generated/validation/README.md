# validation

What `/validate cleanroom` and `/validate outsider` found, one dated folder per run. Not
regenerable in the sense the rest of `AI-generated/` is: a clean-room run is a measurement of a
particular commit on a particular machine at a particular time, and re-running it produces a new
finding, not the same one.

## Currently here

- `2026-09-22_cleanroom-artefacts/` — the first clean-room run (batch 19): `summary.json` with
  the counts, `differences.txt` listing every result that differed, `clone_invariants.txt` with
  the clone's own `/validate invariants` output, and `console.log`.
- `2026-09-23_outsider-test.md` — the first outsider test (batch 19): a fresh agent given only
  the repository and asked to follow its instructions, with every point at which it guessed or
  hit a false statement.

The clean-room clone itself, and the logs it writes while running, are gitignored — they are
about 20 GB of working directories inside the repository being checked. Only the findings are
kept.
