result: results/comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:7c66ab874d3b495322ee0e7f92c76c6ef26a7d0c40fce367a6fc2248ea4f0888
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv  sha256:ea7254d95b7778d1e0bc547663e461eabedb347dbbd69226a2ff11e1a441c826
         ../g_oosErrorBoosting/results/comparison.json  sha256:6171532fa1366810df902264329f1a7b112397fd2ebdce935c7538b79c03e38f
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: 7fce55c
instructions-commit: 595c32d
node: analysis/04_stage2/i_boundedBoosting
produced: 2026-09-21
what it reports: as h_levelOnlyBoosting/provenance/compare_to_stage1.md (same script text).
agency: agent-autonomous
