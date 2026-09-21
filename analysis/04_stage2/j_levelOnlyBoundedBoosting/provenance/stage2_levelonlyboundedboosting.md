result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/01_stage2_levelonlyboundedboosting.py
        sha256:19dcb458e1cc1adc9e7f4f6ff18d11958056011ad1fc47b6b7f66b863cbd45e8
        ../../scripts/lib/stage2_perturb.py  (the verified parametrised pipeline)
        sha256:b5371bb823a6e8b9b821db11ee9f6c11d1d2d02b46752619c31b491980b0241a
        ../../scripts/lib/stage2_oos.py
        sha256:d6f12d8cf9643eab708ed9fc175b372f562dcd9578da4efd19ec7ccf603e0074
        ../../scripts/lib/residual_features.py
        sha256:cbe025691c5e58b415720849ca3e30964f24c96f921764d638a9ccd8149bec2c
        ../../scripts/lib/backtest.py
        sha256:bb036170c3e82031614c3fa2e7c9454ee98dad17ff7b3a387397d0addbf5f405
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/project_seed.py
        sha256:8cf8c777a92e0d43663854423c4a6854675ea150613d42b5d08f69de14b18a5b
invocation: ../../../environment/env/bin/python scripts/01_stage2_levelonlyboundedboosting.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (verification reference only)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: as h_levelOnlyBoosting: component seed 3256270425, real randomness pinned via random_state.
verification: derived stage-1 forecast vs 02_stage1's stored per_cell_scores.csv: 408/408
        cells, max|Δmean| = 0.0, max|Δse| = 0.0 (results/conclusion.json).
commit: 7fce55c
instructions-commit: 595c32d
node: analysis/04_stage2/j_levelOnlyBoundedBoosting
produced: 2026-09-21
configuration: Stage2Config(features="level_only", bounded_correction=True, bound_floor=10.0)
        -- h's input and i's bound together; not a row of the v1 manifest, so this is the one
        of the three whose result was unknown when the main-path rule was written.
alternatives-considered: the two single-axis siblings h and i, which this node combines;
        nothing else differs from them.
agency: agent-autonomous (the configuration); exploring further is human-set.
