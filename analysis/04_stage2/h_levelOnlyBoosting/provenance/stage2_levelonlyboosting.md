result: results/per_cell_scores.csv · results/conclusion.json
script: scripts/01_stage2_levelonlyboosting.py
        sha256:7e83a784a709d7cd3e9c6e12dc45224d8c5985edbdfbc71f0f1c6bbcb1322021
        ../../scripts/lib/stage2_perturb.py  (the verified parametrised pipeline; see 06_stability/provenance/run_combinations.md)
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
invocation: ../../../environment/env/bin/python scripts/01_stage2_levelonlyboosting.py
inputs: ../../01_data/01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
         ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         (verification reference only: the derived stage-1 forecast must match it cell for cell)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: project 20260920; component seed 3256270425 = component_seed("04_stage2/g_oosErrorBoosting"),
        deliberately the main path's own seed (Stage2Config default) so the difference from g
        is the configuration alone. Real randomness (subsample=0.8), pinned via random_state.
        Determinism of the pipeline was demonstrated in batch 12 (its `main` configuration
        reproduces g's 408 rows value for value) and is not re-demonstrated per candidate.
verification: derived stage-1 forecast vs 02_stage1's stored per_cell_scores.csv: 408/408
        cells, max|Δmean| = 0.0, max|Δse| = 0.0 (results/conclusion.json).
commit: 7fce55c
instructions-commit: 595c32d
node: analysis/04_stage2/h_levelOnlyBoosting
produced: 2026-09-21
configuration: Stage2Config(features="level_only"); everything else the main path's
        (Stage1Config(), SchemeConfig(), the other Stage2Config defaults). Equal by
        construction to 06_stability's v1 row `stage2=g_level_month_horizon_only`, whose
        conclusion (24.351, -6.53%) this node reproduces.
alternatives-considered:
  - Re-implementing the pipeline in this node, as candidates a-g did: rejected -- the
    parametrised pipeline was verified against g in batch 12, and reusing it is the point of
    having verified it; the node's own content is its configuration, its verification against
    02_stage1, and its answer.
  - A level-only set without the month indicators (horizon and level alone): not built; a
    perturbation for the v2 manifest.
  - Keeping the recent-residual features and dropping only the incidence/cross-province ones
    (or the reverse): those are `stage2=g_no_incidence_terms` (-3.32%) and
    `stage2=g_no_cross_province` (-5.84%) in the v1 stability run; both worse than level-only.
agency: agent-autonomous (the configuration); the decision to explore stage 2 further is
        human-set (plan §4b, 2026-09-21).
information: agent-retrieved -- the choice of the level-only input follows this project's own
        diagnostics (05_residualStructure/results/predictability.json) and stability run.
