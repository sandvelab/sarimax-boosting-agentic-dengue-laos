result: results/comparison.json
script: scripts/02_compare_to_stage1.py
        sha256:df774293953e0d5eecdccc403c8a2637e250afac25c45236ba854199c2a6c62b
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
invocation: ../../../environment/env/bin/python scripts/02_compare_to_stage1.py
inputs: ../../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         results/per_cell_scores.csv (this node's own, produced by 01_stage2_linear_lags.py)  sha256:8fd76a92ad997f368fefb5e54b4dc40d1ca94ef0b7127bfbfcc7304582da41a6
environment: environment/ (project main)
         lock.txt sha256:1d10c3af0cce41440634defbe5b77b0fa30243333df2fd9493015ba2e197278a
seeds: none — a deterministic re-aggregation of two already-produced files, no fitting.
commit: fe845c3
instructions-commit: 595c32d
node: analysis/04_stage2/a_linearLags
produced: 2026-09-20
alternatives-considered: nominal interval coverage is reported at 90% (two-sided Gaussian,
  z≈1.6449) — a conventional default, not tuned to this data; not itself explored as a fork
  since plan §2 asks for coverage to be reported beside CRPS, not for a specific level to be
  optimised.
agency: agent-autonomous

---
section appended 2026-09-23 (batch 20, at the outsider test's finding) — **the environment
changed after this record was written, and the record had not caught up.**

environment: environment/ (project main)
         lock.txt sha256:2ed8d10ee004b65ae2076e055d090f487018731cdf02723fa48431c8cfd8bc01
         changed at fa71b3b (batch 5, 2026-09-20): scikit-learn 1.9.1 and its dependencies added
         for the tree-based stage-2 candidate; every package this node's scripts import is at the
         same version in both lockfiles. The section above names the batch-2 lockfile
         (sha256:1d10c3af…), which is the one this result was produced under.
re-run: not re-run at fa71b3b. The result was reproduced byte for byte under the current lockfile
         by the clean-room run of 2026-09-22 (a fresh clone, the environment built from
         lock.txt; `AI-generated/validation/2026-09-22_cleanroom-artefacts/`), and again by the
         release-time run of 2026-09-23.
why-it-was-missed: `/validate invariants`' hashes check verified the digests in `script:` blocks
         and not the lockfile digest in the `environment:` block; it now verifies both (batch 20).
agency: agent-autonomous.
