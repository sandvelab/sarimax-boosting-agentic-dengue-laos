result: results/comparison.json · results/all_candidates_comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:cc803c993b97a0fd0c1e649fe18e325dd36817d5eb7ab62ce94137ef3b99c185
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv (this node's own, produced by 01_stage2_linear_climate.py)  sha256:d381c41225a74e323850c0f8e1014513e3da878ee86c2ee2bd5cd19ad38e0373
         ../a_linearLags/results/comparison.json (closed record, read not recomputed)  sha256:ab1875cc37adb87600acbf848d32df803ebb358fc5de3efb1b0562bdccfd87ec
         ../b_gradientBoosting/results/comparison.json (closed record, read not recomputed)  sha256:b3adea2993af5871859a396a7975c5346483a2e03d26cd647cdc4f7c4f9a96dd
         ../c_bayesianRidge/results/comparison.json (closed record, read not recomputed)  sha256:3ec97961d573dc214b1e73671e4b9fa7fba643a22dfc9100a88ae0ee7a34c3ac
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none -- a deterministic re-aggregation of already-produced files, no fitting.
commit: 8c414b7
instructions-commit: 595c32d
node: analysis/04_stage2/d_linearClimate
produced: 2026-09-20
alternatives-considered: nominal interval coverage reported at 90% (two-sided Gaussian,
  z≈1.6449), the same convention as every sibling candidate, for comparability -- not tuned to
  this data. The "vs_a_linearLags" block was added beyond the sibling scripts' pattern because
  this candidate's actual question is "does climate help over a_linearLags's minimal input",
  not only "does it beat stage 1 alone" -- both are reported so neither comparison is buried.
agency: agent-autonomous
