result: results/conclusions.csv
script: scripts/04_collect_conclusions.py
        sha256:29e7384066b4fcc31e4e4fb7b5aead7d367ebafa93e1aea79b5363575aac87bc
invocation: ../../environment/env/bin/python scripts/04_collect_conclusions.py
inputs: results/manifest.csv  sha256:ba01a061bfbe0a4f3e636d4a747b2a3bffe8d2cd1f673342af790fb2bdc9340b
         results/$COMBO/conclusion.json for every planned tier-2 combination (this node's own
         output from 03_run_combinations.py)
         ../04_stage2/g_oosErrorBoosting/results/comparison.json  sha256:6171532fa1366810df902264329f1a7b112397fd2ebdce935c7538b79c03e38f
         (the main-path reference row)
         ../04_stage2/{a_linearLags,b_gradientBoosting,c_bayesianRidge,d_linearClimate,e_pooledRandomForest,f_oosErrorRidge}/results/comparison.json
         (tier 1; each sibling's own provenance hashes its file)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: edc5158  (2b5256c's version built the tier-1 path wrongly -- `analysis/` twice -- and
        failed before writing; fixed in edc5158 and run once)
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-21
what it records: one row per manifest row plus the main path -- 41 rows, 36 run (main, 6
        siblings, 29 perturbations), 5 tier-3 not run with reasons -- carrying stage-1 and
        two-stage mean CRPS and coverage, the sign of the difference, splits and cells improved.
        Nothing is computed here beyond copying; the distribution report (batch 13) is written
        from this file.
alternatives-considered: recomputing the tier-1 figures from the siblings' per-cell files
        rather than copying their comparison.json -- rejected, the siblings' own scripts are
        the record of those numbers and this node should read, not re-derive, them.
agency: agent-autonomous

---
section appended at commit ba79a02 (batch 15): **script changed and run for manifest v2**.
script: scripts/04_collect_conclusions.py
        sha256:9b5c3e8c33dd6b2f3bd8788326053d9f9acec55aedc47b3fbb5736aaecb4d97f
change: (was 29e73840…) the version, main path and row tag are read from
        results/manifest_freeze.json and results/manifest_summary.json instead of naming
        g_oosErrorBoosting in code; the main-path row is copied from that node's own
        comparison.json; a version after the first writes conclusions_v<N>.csv beside v1's
        conclusions.csv, which is left as it was; the tier-0 gate row is skipped (the main row
        is written from the tree's file) and rows the manifest marks superseded are not
        repeated. Nothing is computed beyond copying, as before.
result: results/conclusions_v2.csv  sha256:27916dca54ddc7a7277cd3f5b6cda6465b9ed45681b0aa842e76ff5003123045
invocation: ../../environment/env/bin/python scripts/04_collect_conclusions.py
inputs: results/manifest.csv  sha256:d2c5e813e7215eb908787049546e0e8346c3311ea7b6d6b3ca6fd43c53834ac0
         results/manifest_freeze.json  sha256:a6e1efa271432a42694d4c106aa366a6641a5c52d3ac41d345c3101aeff15d95
         results/manifest_summary.json  sha256:f9427e68414ca876758e57e37b242cc5a8bbcb268f4742fa1f6283ff673acf02
         results/$COMBO/conclusion.json for the 26 planned `@h` rows (this node's own output
         from 03_run_combinations.py, section above)
         ../04_stage2/h_levelOnlyBoosting/results/comparison.json  sha256:47657629c39f5bc1848c0d0afa4b228a5f3639e41ebe30d4f5158c178885f84e
         (the main-path reference row)
         ../04_stage2/{a_linearLags,b_gradientBoosting,c_bayesianRidge,d_linearClimate,e_pooledRandomForest,f_oosErrorRidge,g_oosErrorBoosting,i_boundedBoosting,j_levelOnlyBoundedBoosting}/results/comparison.json
         (tier 1, nine siblings; each sibling's own provenance hashes its file)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: ba79a02
instructions-commit: 595c32d
node: analysis/06_stability
produced: 2026-09-22
what it records: 41 rows, 36 run (main@h, 9 siblings, 26 perturbations), 5 tier-3 not run
        with reasons; the two-stage ensemble beats stage 1 on CRPS in 32 of the 36 and does so
        with coverage not worse in 31 (the four losses are siblings a-d; the CRPS win with worse
        coverage is e_pooledRandomForest), the same four-and-one as in v1.
alternatives-considered (this section): including the 29 superseded v1 rows in this table with
        their v1 numbers -- rejected; they are v1's rows and stay in conclusions.csv, and the
        cross-version comparison is 05_report_distribution.py's job, done by file.
agency: agent-autonomous
