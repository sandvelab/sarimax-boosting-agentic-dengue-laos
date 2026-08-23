# AI-generated

Derived documents. Most of what is here is produced by a recorded recipe and can be rebuilt,
so it can also be deleted without loss — and should be, when its source goes away.

| Path | Produced by | Rebuild with | Regenerable |
|---|---|---|---|
| `hierarchical-report/` | `build_hierarchical_report.py` from `analysis/` | `/hierarchical-report` | yes |
| `reproducibility-report/` | the final text, claims, tree and provenance | `/repro-report` | yes |
| `batch-reports/` | `/do`, one per executed batch of the plan | — | **no** |
| `chap-reconnaissance/` | `AI-internal/reconnaissance/` against the pinned `chap-core` | re-run the script | yes |

**`batch-reports/` is the exception and should not be pruned with the rest.** Each report is
an account of what happened during one batch — what was established, what went wrong, what
was decided and by whom. Re-running a batch produces a *different* report rather than the
same one, so there is no recipe that rebuilds these. They sit here because `/do` generates
them, not because they are disposable.

**Never hand-edit anything here.** An edit is lost on the next run and is wrong in the
meantime. If a derived document is wrong, its source is wrong.

## Currently here

- `batch-reports/` — one report per executed batch. Batches 1 (orientation and set-up) and
  2 (Chap reconnaissance).
- `chap-reconnaissance/` — what the installed Chap platform is and does, captured to files
  in batch 2 so the report could quote them. Regenerable, and safe to prune once the claim
  tree supersedes it. None of its numbers is a result of this project.

Neither the hierarchical report nor the reproducibility report exists yet; both are phase-E
deliverables.
