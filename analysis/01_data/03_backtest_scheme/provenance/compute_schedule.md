result: results/split_schedule.csv · results/schedule_summary.json
script: scripts/compute_schedule.py
        sha256:f6c39a6d1f8a4a0f8405eed56da335916264a32c0f227ebbf21a6e291e2967bf
        ../../../scripts/lib/backtest.py
        sha256:bb036170c3e82031614c3fa2e7c9454ee98dad17ff7b3a387397d0addbf5f405
invocation: ../../../environment/env/bin/python scripts/compute_schedule.py
inputs: ../01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
environment: environment/ (project main)
seeds: none — deterministic
commit: 9d9590f
instructions-commit: 595c32d
node: analysis/01_data/03_backtest_scheme
produced: 2026-09-20
alternatives-considered: n_periods=3/n_splits=8/stride=3 is not derived here but taken from
  the plan §4b decision to reuse the prior project's scheme for comparability. What this
  script settles is only the resolution of that scheme to concrete month windows and the
  Chap-matching convention that the evaluated span ends at the file's last period — verified
  by hand against the prior project's own reported figures (evaluated span 2008-01 to
  2009-12, first split's training window ending 2007-12) before trusting the code.
agency: agent-autonomous
