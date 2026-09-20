result: results/province_summary.csv · results/modelability_summary.json
script: scripts/characterise.py
        sha256:939b2743fd78e3e03bfbc213ac88cbf1b10ba1d256c6954656ca1003f10d83c4
invocation: ../../../environment/env/bin/python scripts/characterise.py
inputs: ../01_prepare/results/development.csv  sha256:138c568c84e33bc7c94fe10f1e4d6bef4f339469dd81ec49b8180be18bf2033f
environment: environment/ (project main)
seeds: none — deterministic
commit: cf15184
instructions-commit: 595c32d
node: analysis/01_data/02_characterise
produced: 2026-09-20
alternatives-considered: a modelability threshold of 36 or 48 months was also reasonable;
  24 (two full seasonal cycles) was chosen as the minimum a SARIMAX with a 12-month seasonal
  term needs to estimate anything, not as the point past which more data stops mattering. No
  province's inclusion/exclusion changes between 24 and 48 here — LA-VI has zero present
  months and every other province has well over 96 — so the choice is not load-bearing for
  this dataset, but is recorded rather than left as an unstated default.
agency: agent-autonomous
