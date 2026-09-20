result: results/comparison.json · results/all_candidates_comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:8978ebc8ad3094618c4fc16d4efe81e32f9c68d1bfa69588a31911eb74443857
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv  sha256:d03eaf3c6ca59b7a0b951cb3dd4c38fdbc1eea3dabe894c5e3d0d7198012732c
         ../a_linearLags/results/comparison.json  sha256:ab1875cc37adb87600acbf848d32df803ebb358fc5de3efb1b0562bdccfd87ec
         ../b_gradientBoosting/results/comparison.json  sha256:b3adea2993af5871859a396a7975c5346483a2e03d26cd647cdc4f7c4f9a96dd
         ../c_bayesianRidge/results/comparison.json  sha256:3ec97961d573dc214b1e73671e4b9fa7fba643a22dfc9100a88ae0ee7a34c3ac
         ../d_linearClimate/results/comparison.json  sha256:905d7e02ea97ac4e2d95f9d7782225cac70682ef622fa7e27b34bbefdd67fbdb
         ../e_pooledRandomForest/results/comparison.json  sha256:5f2485a6d337fdd3b6f130b73045ab78ac8d7cc89e2922f557c3f28f677d49c3
         ../f_oosErrorRidge/results/comparison.json  sha256:04bc491bee9512b98017735a0961b0bc5cbd189c9cb462efe242da4ddc3fbc3f
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: 90add4c
instructions-commit: 595c32d
node: analysis/04_stage2/g_oosErrorBoosting
produced: 2026-09-20
what it reports: as f_oosErrorRidge's compare script (headline pair, combination-rule
        decomposition, by horizon, by split, by province), plus all seven stage-2 candidates
        side by side with a ranking by mean CRPS and the subset that beats stage 1 on CRPS with
        90% coverage within five points of stage 1's.
alternatives-considered: as f_oosErrorRidge/provenance/compare_to_stage1.md. The
        "coverage within five points" criterion is a reporting convenience for the side-by-side
        table, not plan §2's definition of calibration -- §2 asks that coverage be reported
        beside CRPS and that a CRPS win under broken calibration not count; the threshold is
        chosen so that e_pooledRandomForest (64.4%) fails it and every per-province candidate
        (82-87%) passes, matching the judgment batch 9 already recorded in prose.
agency: agent-autonomous
