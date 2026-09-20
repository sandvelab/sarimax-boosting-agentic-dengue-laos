result: results/comparison.json · results/all_candidates_comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:060965ccaf493f68aea4bb713f697f4d3bf9c2cc28c8b8356b96c74f6fd32ffe
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv (this node's own, produced by 01_stage2_bayesian_ridge.py)  sha256:5606e76b0098ddd97e79e14689e3b3644598df3a68b198e3500807fa28f0e606
         ../a_linearLags/results/comparison.json (that node's own closed record, read not
         recomputed)  sha256:ab1875cc37adb87600acbf848d32df803ebb358fc5de3efb1b0562bdccfd87ec
         ../b_gradientBoosting/results/comparison.json (likewise)  sha256:b3adea2993af5871859a396a7975c5346483a2e03d26cd647cdc4f7c4f9a96dd
environment: environment/ (project main, unchanged this batch)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none — a deterministic re-aggregation of already-produced files, no fitting.
commit: (see this batch's close-out commit for the hash)
instructions-commit: 595c32d
node: analysis/04_stage2/c_bayesianRidge
produced: 2026-09-20
alternatives-considered: nominal interval coverage reported at 90% (two-sided Gaussian,
  z≈1.6449), matching both sibling candidates for comparability — a conventional default, not
  tuned to this data. `all_candidates_comparison.json` was added beyond the sibling
  candidates' own comparison scripts specifically to give batch 7's main-path decision a
  single file-grounded, three-way comparison to read from, rather than requiring that batch to
  recompute or hand-collate three separate files.
agency: agent-autonomous
