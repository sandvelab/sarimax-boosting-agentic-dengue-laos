# Provenance — the external check reported beside Laos

```
result:              results/external_conclusions.csv
                     results/external_vs_laos.json
                     results/pool_reconstruction_external.json
script:              scripts/report_external.py
                     sha256:a84f5cd864955530bcb56f282d2d65567a4bf89eab646712a7b9d32dc7b16054
invocation:          "$PYTHON" scripts/report_external.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              results/manifest_external.csv
                     analysis/results/main/conclusion.json
                     analysis/results/main__holdout/conclusion.json
                     analysis/results/main__{vnm,vnmFinal,tha,thaFinal}/conclusion.json
                     analysis/04_score/03_compare/results/<combination>/comparison_notes.json
                     analysis/03_models/03_candidate/c_ensemble/results/<combination>/pool_check.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. This reads stored conclusions and arranges them.
commit:              bfbc096 — the tree the four rows ran from. The script
                     itself is carried by batch 20's closing commit, which
                     changed nothing under analysis/ that had already run.
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                analysis/06_external
produced:            2026-09-04
alternatives-considered: reporting raw CRPS across the three countries, which is not
                     comparable — Thailand's mean monthly case count is about half
                     Vietnam's and about four times Laos's, so a raw gap between countries
                     would be mostly a gap between epidemics. The skill score against a
                     reference that faced the same data is the same control the project
                     already uses between its development period and its held-out year.
                     Also considered: calling three countries a sample and putting a
                     confidence statement on the drop. Not done; the file says so.
agency:              agent-autonomous
```

**What it establishes.** The reported model's skill score, raw CRPS, coverage and margin on
six analyses — Laos's two, which are read from the same `conclusion.json` the headline is
read from and are not recomputed here, and the four external ones — with each figure's own
band beside it: the largest paired difference between two of the reference model's four
unseeded repeats on that dataset, divided by its mean CRPS.

**What it deliberately does not establish.** Three countries from one harmonisation are not
a sample, and the two sibling analyses were not held out from anything — no model was
developed on them, so there was nothing to hold them out from. What they can say is whether
the development-to-final-year drop measured on Laos is a thing that happens repeatedly or a
thing that happened once. The file states that limit in its own text rather than leaving it
to a reader.

**The pool's second path is absent here, on purpose.** `check_pool.py` rebuilds a pool from
its members' own separate evaluations, and a member is evaluated separately only under the
family fork's own combination — a perturbation row. This check moves no fork, so no such row
exists on these datasets and no order of execution would produce one. That is a different
thing from the ordering defect batch 28 removed, and
`results/pool_reconstruction_external.json` says which it is, what it would have cost to
have, and why it was not bought.
