# AI-generated

Derived documents. Most of what is here is produced by a recorded recipe and can be rebuilt,
so it can also be deleted without loss — and should be, when its source goes away.

| Path | Produced by | Rebuild with | Regenerable |
|---|---|---|---|
| `hierarchical-report/` | `build_hierarchical_report.py` from `analysis/` | `/hierarchical-report` | yes |
| `reproducibility-report/` | the final text, claims, tree and provenance | `/repro-report` | yes |
| `batch-reports/` | `/do`, one per executed batch of the plan | — | **no** |
| `chap-reconnaissance/` | `AI-internal/reconnaissance/` against the pinned `chap-core` | re-run the script | yes |
| `method-reconnaissance/` | `AI-internal/reconnaissance/` against the pinned reference model and the model library | re-run the scripts | recipe yes, numbers **no** |
| `vertical-slice/` | `AI-internal/vertical-slice/` against the development file | — | superseded: the tree reproduces it |
| `validation/` | `/validate cleanroom` and `/validate outsider` | re-run the check | recipe yes, findings **no** |
| `determinism-checks/` | `AI-internal/useful-scripts/verify_model_determinism.sh` | re-run the script | yes, ~3 min |
| `candidate-forks/` | `AI-internal/useful-scripts/candidate_fork_sweep.py` against the tree | re-run the sweep | the later round yes; **round 1 no** |

**`batch-reports/` is the exception and should not be pruned with the rest.** Each report is
an account of what happened during one batch — what was established, what went wrong, what
was decided and by whom. Re-running a batch produces a *different* report rather than the
same one, so there is no recipe that rebuilds these. They sit here because `/do` generates
them, not because they are disposable.

**Never hand-edit anything here.** An edit is lost on the next run and is wrong in the
meantime. If a derived document is wrong, its source is wrong.

## Currently here

- `batch-reports/` — one report per executed batch. Batches 1 (orientation and set-up),
  2 (Chap reconnaissance), 3 (the data), 4 (methods), 5 (the bootstrap), 6 (the
  vertical slice), 7 (erecting the tree), 8 (the candidate contract and candidate 1) and
  9 (candidate 1's forks, swept and promoted).
- `candidate-forks/` — what every alternative to candidate 1's configuration scores on the
  development data, and the rule by which three forks were promoted in batch 9. Every number
  is copied from a file inside the tree. **Round 1's table is not regenerable** — the tree's
  results behind it were replaced by round 2 — and it is the record the promotion was
  decided from. This is a phase-C selection aid; the phase-D stability result is batch 12's
  and lives in the tree.
- `validation/` — what `/validate` found, one file per run. Batch 7's clean-room check is
  the first, and it reports its differences rather than announcing success.
- `determinism-checks/` — Rule 6 verified by running each of our models twice and diffing.
- `chap-reconnaissance/` — what the installed Chap platform is and does, captured to files
  in batch 2 so the report could quote them. Regenerable, and safe to prune once the claim
  tree supersedes it. None of its numbers is a result of this project.
- `method-reconnaissance/` — what the reference model scores, costs and varies by on this
  dataset, and what else Chap's model library holds, captured in batch 4. The *recipe* is
  regenerable; the numbers are not, because the reference model is unseeded. Its evaluation
  `.nc` is therefore kept rather than treated as an intermediate. None of its numbers is yet
  a result of this project — the reported reference score comes from a node in the tree.

- `vertical-slice/` — what the first model of our own scored, end to end, on the real
  development file at the fixed scheme, captured in batch 6. **None of its numbers is a
  reported result**, and it is now **superseded**: batch 7 moved the model into
  `analysis/03_models/01_baselines/01_persistence/a_empiricalChange/` and reproduced its mean
  CRPS from there to the last digit. Kept because it is the record of the batch that
  exercised the chain before there was a tree to run it in; `run_vertical_slice.sh` points at
  a directory that has since moved, and batch 6 is reproducible from the commit its
  provenance records name.

Neither the hierarchical report nor the reproducibility report exists yet; both are phase-E
deliverables.
