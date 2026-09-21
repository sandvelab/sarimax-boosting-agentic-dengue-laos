result: results/comparison.json · results/all_candidates_comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:9601d5fe2dac7523bfa50550c83658abd65b510d2edfc8a73d8d19e1f2467281
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv  sha256:ae660b8fe9c1fa89ee266bf42ac2aac5ef710bea2dd9bffa92fb8f0c42b715aa
         ../h_levelOnlyBoosting/results/comparison.json  sha256:47657629c39f5bc1848c0d0afa4b228a5f3639e41ebe30d4f5158c178885f84e
         (the parent this candidate is one axis -- the bound -- away from)
         ../{a_linearLags,b_gradientBoosting,c_bayesianRidge,d_linearClimate,e_pooledRandomForest,f_oosErrorRidge,g_oosErrorBoosting,i_boundedBoosting}/results/comparison.json
         (the side-by-side table; each sibling's own provenance hashes its file; i's is
         sha256:2a14aba839db8f3f989728125cf2240f63c24aa3e54c002bdad375f099963778)
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none drawn.
commit: 7fce55c
instructions-commit: 595c32d
node: analysis/04_stage2/j_levelOnlyBoundedBoosting
produced: 2026-09-21
what it reports: as its siblings' compare scripts, plus all ten stage-2 candidates side by
        side, the subset clearing both of plan §2's bars, and the **pre-registered main-path
        rule applied** (plan §4b, 2026-09-21, written before this node's result was seen):
        among g, h, i, j the lowest development mean CRPS with coverage >= stage 1's; a tie
        within 0.1 CRPS broken by more splits improved, then by fewer changes from g. Outcome
        recorded in results/all_candidates_comparison.json: j (24.288) and h (24.351) tie on
        the first criterion and on splits improved (6 of 8); h is the simpler -> main path h.
alternatives-considered:
  - A rule without the tie band (strict lowest CRPS): would have picked j on a 0.06 CRPS
    difference on 371 cells, a difference no perturbation in the stability run would call
    meaningful (the seed alone moves the margin by 0.1 points); the band was written into the
    rule for that reason, before the result.
  - A rule preferring more splits improved first: would have picked i (7 of 8) at a higher
    CRPS; plan §2 makes mean CRPS the primary criterion.
agency: agent-autonomous (the rule's content and its application); annotating a main path now
        is human-set.
