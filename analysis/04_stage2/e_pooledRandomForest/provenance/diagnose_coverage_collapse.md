result: results/coverage_collapse_diagnosis.json
script: scripts/03_diagnose_coverage_collapse.py
        sha256:7a21d4768e079e4eab2b3f9f615f1d80142cb5683c486f4f04401de3fa8b8102
invocation: ../../../environment/env/bin/python scripts/03_diagnose_coverage_collapse.py
inputs: results/per_cell_scores.csv (this node's own)  sha256:bd2a0b025eba278a56a0fa86e1910655ca69e7b708663a6b6cde46a87b7280a9
         ../a_linearLags/results/per_cell_scores.csv (closed record, read not recomputed)  sha256:8fd76a92ad997f368fefb5e54b4dc40d1ca94ef0b7127bfbfcc7304582da41a6
         ../d_linearClimate/results/per_cell_scores.csv (closed record, read not recomputed)  sha256:d381c41225a74e323850c0f8e1014513e3da878ee86c2ee2bd5cd19ad38e0373
environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
seeds: none -- a deterministic re-aggregation and correlation computation over already-produced
        files, no fitting.
commit: db3369e
instructions-commit: 595c32d
node: analysis/04_stage2/e_pooledRandomForest
produced: 2026-09-20
alternatives-considered: this script was written after the candidate's headline result (mean
  CRPS 25.89, coverage 64.4%) was already visible, specifically because plan §2's "a model that
  wins on mean CRPS while being badly calibrated has not won" makes the calibration collapse the
  fact that decides whether this candidate earns its place, not optional colour -- an ad hoc
  terminal check of the same numbers was run first to decide whether writing this script was
  worth it, then discarded in favour of this file-grounded version (Rule 1: no number reaches a
  claim except through a file). Pearson correlation was used over a rank correlation as a
  simple, standard first choice for a roughly monotonic relationship on 17 points; not verified
  against an alternative correlation measure since the qualitative finding (more negative
  forecasts where mean case counts are lower) is visually obvious in the per-province table and
  does not turn on which correlation statistic is used.
agency: agent-autonomous
