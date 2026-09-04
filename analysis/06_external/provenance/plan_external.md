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

---

## 2026-09-04 — batch 20 — the plan is recorded, not recomputed

```
result:              results/manifest_external.csv (now read and verified, not rewritten)
                     results/external_plan.json (unchanged)
                     results/external_plan_check.json (new)
script:              scripts/plan_external.py
                     sha256:e169d8cbd5dccc4e484ed718efb76109c96fe6f9a0ef431630e09bb16c46c2ac
commit:              a715ffc
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
```

**What changed, and why it had to.** The estimate divides a **measured wall-clock duration**
— the seconds the held-out `main` row took, read from
`05_stability/results/run_status_holdout.csv` — and `05_stability/run.sh` rewrites that
measurement every time it runs, which on `analysis/run.sh` is the step immediately before
this node. A planning script that recomputed itself would come back from a clean checkout
with a different estimate, and the claim that the plan was committed before the rows ran
would be a claim about a file that had since been rewritten.

Fourth instance of the family batches 24, 26 and 30 addressed, and it is caught here before
a clean-room run found it rather than after. The split is theirs: the **rows** come from the
tree and the sibling scheme, so a disagreement means the record describes an analysis this
tree cannot produce and is **fatal before anything is written**; the **estimate** is a
measurement, so a drift is written into `external_plan_check.json` and the run carries on.

**What it changed in the results: nothing.** The manifest and `external_plan.json` are the
files committed at `bfbc096`, byte for byte. The new file reports zero drift against this
tree, which is what a tree whose stability half has not re-run should say.

**The defence.** Four situations, in
`AI-generated/validation/26-09-04_externalPlanDefence.json`, all passing: the record as
committed; the cost unit changed by the size batch 31's clean-room run changed it, giving
four reported drifts and a byte-identical manifest; a structural field moved, giving exit 1
and nothing written; and no record at all, giving the plan written.
