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
| `candidate-forks/` | `AI-internal/useful-scripts/candidate_fork_sweep.py` and `family_leaderboard.py` against the tree | re-run the sweep, or rebuild the table | every round but the first yes; **round 1 no** |

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
  vertical slice), 7 (erecting the tree), 8 (the candidate contract and candidate 1),
  9 (candidate 1's forks, swept and promoted), 10 (candidate 2, gradient-boosted trees with
  a probabilistic head), 11 (candidate 3, the ensemble, and the close of phase C) and
  12 (the perturbation manifest, and the opening of phase D), 13, 22 and 14 (the
  perturbation rows), 15 (the distribution, and the frozen holdout set), 16 (the holdout,
  opened once) and 17 (the claim collection completed, and this report).
  Batch 21's report is on the branch `greedy` and is deliberately not copied here.
- `candidate-forks/` — what every alternative to a candidate's configuration scores on the
  development data, what each candidate *family* scores at its own main path, and the two
  rules by which forks and families are promoted. Every number is copied from a file inside
  the tree. **Round 1's table is not regenerable** — the tree's results behind it were
  replaced by round 2 — and it is the record candidate 1's promotion was decided from;
  `boosted_round1/`, `ensemble_round1/` and `families/` are regenerable, because nothing
  under them has been replaced. This is a phase-C selection aid; the phase-D stability result
  lives in the tree, at `analysis/05_stability/results/conclusions.csv`. These tables have
  one further use since batch 12: the manifest reads each fork child's measured effect from
  them as the prior that **orders** its rows, and only from a sweep whose recorded base
  configuration still matches the family's current one.
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

- `hierarchical-report/` — the linked drill-down over the claim tree, built in batch 17.
  The tree supplies the upper levels; below them are four more, one page per scored
  combination: the national mean each model is reported at, that mean by province, each
  province by month, and the per-cell scores every mean above is an average of. 1 175 pages
  over 65 combinations, and every number on them is displayed from the file the analysis
  wrote rather than recomputed. **Its contents are gitignored and its `provenance.md` is
  not**, because a record of a build that is itself untracked records nothing.

The reproducibility report does not exist yet; it is batch 19's.
