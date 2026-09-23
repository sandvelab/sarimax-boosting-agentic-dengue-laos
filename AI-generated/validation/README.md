# validation

What `/validate cleanroom`, `/validate outsider` and `/release check` found, one dated folder or
file per run. Not
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
- `2026-09-23_release-scan/` — the release safety scan (batch 20), written by
  `AI-internal/useful-scripts/release_scan.sh`: `summary.json` with the counts and the one
  automatic verdict, `secrets_tracked.txt` and `secrets_history.txt` (secret-shaped strings at
  HEAD and in every line ever added), `credential_filenames_history.txt`, `secret_words_prose.txt`
  (mentions, for reading), `data_permission.md` (every imported data file with its folder's
  governance statement), `identifying_tracked.txt` and `git_identities.txt`, and `size.txt`.

The clean-room clone itself, and the logs it writes while running, are gitignored — they are
about 20 GB of working directories inside the repository being checked. Only the findings are
kept.
