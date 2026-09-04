# Provenance — the external check's manifest, planned before it ran

```
result:              results/manifest_external.csv
                     results/external_plan.json
script:              scripts/plan_external.py
                     sha256:5ee8eb6b93b73c3ed836b5a352ad1d84943619e9a6e4ec76cd651723213465e4
invocation:          "$PYTHON" scripts/plan_external.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/01_data/03_siblings/results/backtest_scheme_external.json
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     analysis/05_stability/results/run_status.csv
                     analysis/05_stability/results/run_status_holdout.csv
                     (the last two for the measured cost per evaluated cell; the estimate
                     is built from this project's own runs and not from a guess)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Planning reads sizes and writes a table.
commit:              bfbc096
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                analysis/06_external
produced:            2026-09-04
alternatives-considered: running the four rows without a manifest, which for four rows
                     costs nothing to do and loses two things. `/validate invariants`'s
                     `combos` check closes the combination space, and a directory it has to
                     be told to excuse is a check that has stopped meaning anything; and
                     `AGENTS.md` §6 asks for the cost of each unit, the ranking and where
                     the line fell, which an estimate written after the clock stopped
                     cannot supply.
agency:              agent-autonomous. That batch 20 runs at all, and before batch 19, is
                     human-set (plan §4b, 2026-08-31); the budget, the unit and the cut
                     order are the agent's.
```

**What it establishes.** Four rows — Vietnam and Thailand, each in the development and the
final-year arrangement — estimated at **3.14 hours** in total against a **six-hour budget**,
so **nothing was cut** and the cut order was never exercised. The order is recorded anyway:
whole country pairs from the bottom, Thailand before Vietnam, because what the check measures
is the drop between a country's two arrangements and half a country measures nothing.

**Where the estimate comes from.** The unit is seconds per evaluated cell, taken from the
holdout `main` row — the one Lao row that ran this same pipeline on a dataset where nothing
had run before. The development `main` row runs `conclude.py` alone and costs nothing, so it
cannot be the unit; that is exactly the kind of substitution that would have made the
estimate meaningless while looking like a measurement.
