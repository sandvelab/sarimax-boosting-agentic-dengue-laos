result: results/development.csv · results/holdout.csv · results/holdout_completeness.json · results/partition_summary.json
script: scripts/partition.py
        sha256:8968678ead42ac57154e085c5286ec56566446755eb2a9c38ba7611817351029
invocation: ../../../environment/env/bin/python scripts/partition.py
inputs: ../../../Archive/lao-dataset/chap_LAO_admin1_monthly.csv  sha256:19488aa1fc4d961ae1a6aeb75b874789576877664fce47713628f497a06fff56
environment: environment/ (project main)
seeds: none — deterministic partition, no randomness
commit: 9db4b71
instructions-commit: 595c32d
node: analysis/01_data/01_prepare
produced: 2026-09-20
alternatives-considered: splitting by row index rather than by `time_period` string
  comparison; rejected because the source file is a complete 18×156 grid (verified by
  `02_characterise`) so the two give the same partition here, but the string comparison is
  the one that stays correct if a future data refresh adds or reorders rows. Writing the
  holdout file at all, rather than only the development one, was itself a judgment call —
  needed so phase E can read it without re-deriving the partition, and safe under the
  non-negotiable because nothing downstream of this script opens it before phase E.
agency: agent-autonomous
