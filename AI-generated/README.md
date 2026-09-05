# AI-generated

Derived documents. Most of what is here is produced by a recorded recipe and can be rebuilt,
so it can also be deleted without loss — and should be, when its source goes away.

| Path | Produced by | Rebuild with | Regenerable |
|---|---|---|---|
| `hierarchical-report/` | `build_hierarchical_report.py` from `analysis/` | `/hierarchical-report` | yes |
| `repro-report/` | `repro_inventory.py` over the tree, the claims and the provenance, with the narrative written from it | `/repro-report` | inventory yes; the narrative is written and dated |
| `release/` | `release_scan.py` and `release_manifest.py` over the tree and the git history | `/release` | yes, and the scan's history half takes minutes |
| `batch-reports/` | `/do`, one per executed batch of the plan | — | **no** |
| `chap-reconnaissance/` | `AI-internal/reconnaissance/` against the pinned `chap-core` | re-run the script | yes |
| `method-reconnaissance/` | `AI-internal/reconnaissance/` against the pinned reference model and the model library | re-run the scripts | recipe yes, numbers **no** |
| `vertical-slice/` | `AI-internal/vertical-slice/` against the development file | — | superseded: the tree reproduces it |
| `validation/` | `/validate cleanroom` and `/validate outsider`, and targeted checks written for one defect | re-run the check | recipe yes, findings **no** |
| `determinism-checks/` | `AI-internal/useful-scripts/verify_model_determinism.sh` | re-run the script | yes, ~3 min |
| `candidate-forks/` | `AI-internal/useful-scripts/candidate_fork_sweep.py` and `family_leaderboard.py` against the tree | re-run the sweep, or rebuild the table | every round but the first yes; **round 1 no** |
| `plan-drift/` | `AI-internal/useful-scripts/plan_drift.py` against the delivered and live plans | re-run the script | yes, seconds |

**`batch-reports/` is the exception and should not be pruned with the rest.** Each report is
an account of what happened during one batch — what was established, what went wrong, what
was decided and by whom. Re-running a batch produces a *different* report rather than the
same one, so there is no recipe that rebuilds these. They sit here because `/do` generates
them, not because they are disposable.

**Never hand-edit anything here.** An edit is lost on the next run and is wrong in the
meantime. If a derived document is wrong, its source is wrong.

## Currently here

- `batch-reports/` — one report per executed batch, and **what each one established is
  listed in that folder's own `README.md`**, a paragraph per batch. A second list here would
  have to be extended by every batch, and was not: it stopped at batch 17 while the ledger
  reached 24. Batch 21's report is on the branch `greedy` and is deliberately not copied
  here.
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
- `validation/` — what the checks on the method found, one file per run: `/validate
  cleanroom` and `/validate outsider`, and since batch 24 a check written for one defect —
  the frozen phase-E set, put to eleven situations to see whether it defends itself. Each
  reports its differences rather than announcing success.
- `determinism-checks/` — Rule 6 verified by running each of our models twice and diffing.
- `repro-report/` — the closing report (Rule 10): what was produced, what is tracked and how,
  the veridical section, the agency record, and what does not hold. Its §5 is the section to
  read first and is longer than its §1. Every count comes from `repro_inventory.json` beside
  it rather than from prose, because a closing report that quotes a figure nobody can
  recompute is the failure the report itself is about.
- `release/` — Rule 10's safety scan and assembly as files: credentials in the working tree
  and in every blob the history holds, what each archived dataset says about its own licence,
  and every item Rule 10 names checked against what git tracks. **The release is the
  repository**, so assembly is a verification and not a copy.
- `plan-drift/` — how far the live plan has moved from the plan as delivered, measured
  rather than described: section-by-section survival, the ledger's growth, §4b's decisions
  tallied by agency — 169 when batch 18 measured it and **247** when batch 19 remeasured it at the
  end — and the plan's commit history. Phase E asks for this as a
  reported result, because it is the project's only direct evidence on how far an
  agentic system can be handed a research plan and left to run it. Regenerable, and the
  figures are a function of the commit it is run at.
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
