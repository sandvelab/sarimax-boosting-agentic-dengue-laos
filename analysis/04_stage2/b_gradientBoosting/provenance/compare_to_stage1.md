result: results/comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:4a538e98dc3da01f4c5b6b14635fc11483a191b0204a5ccca0838ff1ab8e3a27
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv (this node's own, produced by 01_stage2_gradient_boosting.py)  sha256:c5d6610e5947d8f8f79fca85895922d0a513afe8676ca4ef8cfb57608a192b4a
environment: environment/ (project main, re-pinned this batch for scikit-learn)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none — a deterministic re-aggregation of two already-produced files, no fitting.
commit: (see this batch's commit for 04_stage2/b_gradientBoosting)
instructions-commit: 595c32d
node: analysis/04_stage2/b_gradientBoosting
produced: 2026-09-20
alternatives-considered: nominal interval coverage is reported at 90% (two-sided Gaussian,
  z≈1.6449), matching a_linearLags for comparability — a conventional default, not tuned to
  this data.
agency: agent-autonomous
