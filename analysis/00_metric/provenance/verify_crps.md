result: results/verification.json
script: scripts/verify_crps.py
        sha256:ede42223ccfb7c89baf79fc8f23486bf736a5dad380a20003b45b72b217ca33e
        ../../scripts/lib/crps.py
        sha256:90f29c8379d42e50bba1fa9b129c3617fff8d112d650217f82197fd4446b278e
        ../../scripts/lib/project_seed.py
        sha256:8cf8c777a92e0d43663854423c4a6854675ea150613d42b5d08f69de14b18a5b
invocation: ../../environment/env/bin/python scripts/verify_crps.py
inputs: readme-at-start.md (project seed only)
environment: environment/ (project main)
seeds: project 20260920; component 1607043955 (blake2b("20260920:00_metric-verify_crps"))
commit: b83b280 (script iterated twice after the run first executed -- see the commit
        message; this digest and commit are the version that actually produced the archived
        result)
instructions-commit: 595c32d
node: analysis/00_metric
produced: 2026-09-20
alternatives-considered: comparing only against `properscoring.crps_gaussian` (the exact
  check) was rejected as insufficient on its own, because that function implements the same
  closed form and a shared conceptual error in both would not be caught -- the Monte-Carlo
  check against `crps_ensemble`, a general empirical estimator that assumes nothing about
  the forecast distribution's shape, is the independent leg. Ensemble sizes were capped at
  4,000 rather than the originally planned 100,000 after the first run at 10,000 consumed
  ~3.5 GB and the 100,000 run was OOM-killed -- `properscoring.crps_ensemble` falls back to
  an O(n²) pairwise-difference implementation without `numba` installed. Adding `numba` (a
  compiler-toolchain dependency) to pin a one-off verification's sample size was judged not
  worth it; the smaller, relative-tolerance version still catches a real defect (which would
  produce relative error of order 1, not the 0.01-0.04 observed from Monte-Carlo noise
  alone).
agency: agent-autonomous
