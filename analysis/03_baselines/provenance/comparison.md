result: results/comparison.json
script: scripts/comparison.py
        sha256:dfa9fdf8d910526f062a5e87a220b51680059ac66512f6be1048a02fa23f83e9
invocation: ../../environment/env/bin/python scripts/comparison.py
inputs: ../02_stage1/results/per_cell_scores.csv  sha256:a7132066292f8bbd93c13a74478dabaa164a13ac31d24dfd04bc2b533937ecce
         01_persistence/results/per_cell_scores.csv  sha256:06b0f45ea4380d3741e0ccae4d518dd834183e5652e690e942040e1a5f2922b8
         02_climatology/results/per_cell_scores.csv  sha256:00069fe14ee8cc1bde5987d3d891b4f4b31a7c2d975235670836185506c52cf1
environment: environment/ (project main)
         lock.txt sha256:1d10c3af0cce41440634defbe5b77b0fa30243333df2fd9493015ba2e197278a
seeds: none — reads three already-produced result files and computes means; no fitting, no
        randomness.
commit: (see this batch's After commit for 03_baselines)
instructions-commit: 595c32d
node: analysis/03_baselines
produced: 2026-09-20
alternatives-considered: the script asserts the three (province, split, month) cell sets are
  identical before comparing means, rather than assuming it from equal counts (371 each) --
  a silent set mismatch under equal counts is exactly the kind of thing that would make a
  comparison look honest while not being apples-to-apples. It was not, so the comparison
  ran unmodified.
agency: agent-autonomous
