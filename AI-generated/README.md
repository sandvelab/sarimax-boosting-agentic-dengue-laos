# AI-generated

Derived documents. Most of what will be here is produced by a recorded recipe and can be
rebuilt, so it can also be deleted without loss — and should be, when its source goes away.
`batch-reports/` is the exception: it is an account of what happened during one batch, and
no re-run produces the same report twice, so it is never pruned.

**Never hand-edit anything here.** An edit is lost on the next run and is wrong in the
meantime. If a derived document is wrong, its source is wrong.

## Currently here

- `batch-reports/` — one report per executed batch, never pruned; see its own `README.md`.
- `validation/` — what `/validate cleanroom`, `/validate outsider` and `/release check` found,
  one dated folder or file per run; measurements of a commit on a machine at a time, so never
  pruned either. See its own `README.md`.
- `hierarchical-report/` — the linked drill-down over the claim tree (Rule 8). Gitignored except
  for `provenance.md`, the append-only record of each build; rebuilt by `/hierarchical-report`.
- `repro-report/` — the reproducibility report (the closing step) and the `inventory.json` it is
  written from, produced by `AI-internal/useful-scripts/repro_inventory.py`. See its own
  `README.md`.
