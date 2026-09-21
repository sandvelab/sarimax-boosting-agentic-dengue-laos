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
