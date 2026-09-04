# Provenance — the external check's four rows

```
result:              results/run_status_external.csv
                     results/external_cost_planned_vs_actual.json
                     results/logs/main__vnm.log
                     results/logs/main__vnmFinal.log
                     results/logs/main__tha.log
                     results/logs/main__thaFinal.log
                     and, under each node's results/<combination>/ for the four
                     combinations main__vnm, main__vnmFinal, main__tha, main__thaFinal:
                     the setup chain's four stage specifications and assembled dataset,
                     both baselines' evaluations, the reference model's four repeats, the
                     pool's evaluation and members, the per-cell scores, the leaderboard,
                     the paired summaries, the three comparison figures and conclusion.json
script:              scripts/run_external.py
                     sha256:aeb1a2988dc9e5e6dfe704c1a7250087afe73a45a8e687b56d618dcd0c6d238d
                     analysis/05_stability/scripts/lib/driver.py
                     (builds every step list and executes it; the same library the 32
                     perturbation rows and the held-out year go through)
invocation:          "$PYTHON" scripts/run_external.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              results/manifest_external.csv
                     analysis/01_data/03_siblings/results/{THA,VNM}_{development,full}_*.csv
                     analysis/01_data/03_siblings/results/backtest_scheme_external.json
                     every script the reported analysis runs, unchanged — each row's log
                     names the exact command of every step, and each model's own
                     model_spec.json hashes the model files it was evaluated from
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0.
                     The reference model is the pinned amd64 chapkit image
                     ghcr.io/chap-models/chapkit_ewars_model@sha256:abd8098f… running
                     under emulation; Docker must be up.
seeds:               unchanged. Each model of ours derives its component seed from the
                     project seed 20260822 and the component's name, and no part of that
                     derivation is the dataset. The reference is unseeded and is run four
                     times on each of the four datasets, as it is on both Lao arrangements.
commit:              bfbc096
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                analysis/06_external
produced:            2026-09-04
alternatives-considered: a second implementation of the pipeline at this node, which would
                     have avoided moving the step-list construction out of run_manifest.py
                     and would have made the check measure the code rather than the model.
                     Rejected on the same argument every model in this project reaches
                     `chap eval` through one function.
                     Also considered and not run: evaluating candidate 1 and candidate 2
                     separately on each sibling dataset, which would make the pool's
                     independent reconstruction available there. Not run because the check
                     the plan asks for is the reported model unchanged; the absence is
                     recorded in results/pool_reconstruction_external.json.
agency:              agent-autonomous
```

**What it establishes.** Recorded in `run_status_external.csv` — which row ran, for how long,
and where its log is — and in `external_cost_planned_vs_actual.json`, the estimate against
the clock, per row and in total.

**Why no row is skipped on a second invocation.** There is no seal here. Plan §3's seal
protects the Lao 2010, because the model was developed against Lao 1998–2009; nothing was
developed on these four files. A row that is skipped because it already ran is what stopped
`analysis/run.sh` reproducing phase E from a clean checkout in batch 18, and that shape is
not reintroduced at a node where it would protect nothing. The cost is that the reference
model is unseeded, so a re-run redraws every denominator — which is why the report puts the
reference's own re-run spread beside every figure that divides by it.
