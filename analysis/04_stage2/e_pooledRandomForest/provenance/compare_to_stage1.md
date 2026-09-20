result: results/comparison.json · results/all_candidates_comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:71f12c050bb4385cf46bb2fa30a4ec39a5dd0c93005b8d981312c9ceef5f1c78
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv (this node's own, produced by 01_stage2_pooled_random_forest.py)  sha256:bd2a0b025eba278a56a0fa86e1910655ca69e7b708663a6b6cde46a87b7280a9
         ../a_linearLags/results/comparison.json (closed record, read not recomputed)  sha256:ab1875cc37adb87600acbf848d32df803ebb358fc5de3efb1b0562bdccfd87ec
         ../b_gradientBoosting/results/comparison.json (closed record, read not recomputed)  sha256:b3adea2993af5871859a396a7975c5346483a2e03d26cd647cdc4f7c4f9a96dd
         ../c_bayesianRidge/results/comparison.json (closed record, read not recomputed)  sha256:3ec97961d573dc214b1e73671e4b9fa7fba643a22dfc9100a88ae0ee7a34c3ac
         ../d_linearClimate/results/comparison.json (closed record, read not recomputed)  sha256:905d7e02ea97ac4e2d95f9d7782225cac70682ef622fa7e27b34bbefdd67fbdb
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none -- a deterministic re-aggregation of already-produced files, no fitting.
commit: db3369e
instructions-commit: 595c32d
node: analysis/04_stage2/e_pooledRandomForest
produced: 2026-09-20
alternatives-considered: nominal interval coverage reported at 90% (two-sided Gaussian,
  z≈1.6449), the same convention as every sibling candidate. The "vs_d_linearClimate" block
  isolates this candidate's actual question -- does pooling help, holding the input fixed --
  the same pattern d_linearClimate used to isolate its own question against a_linearLags.
agency: agent-autonomous
