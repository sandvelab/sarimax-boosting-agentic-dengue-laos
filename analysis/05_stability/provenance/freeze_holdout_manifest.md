# Provenance — the frozen phase-E set

```
result:              results/manifest_holdout.csv
                     results/holdout_freeze.json
script:              scripts/freeze_holdout_manifest.py
                     sha256:ca92a098f7ee5708190b4934ffea286737968fc73e0955cc466a6739823584cf
invocation:          "$PYTHON" scripts/freeze_holdout_manifest.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/05_stability/results/manifest.csv
                     analysis/05_stability/results/conclusions.csv
                     analysis/05_stability/results/manifest_notes.json
                     analysis/05_stability/results/tier2_rule.md
                     analysis/05_stability/results/distribution.json
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              9ad6578
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** The deliverable the plan's §3 makes phase E depend on: the exact
set of analyses to be run on the held-out year, committed **before** the year is opened.
Thirty-three rows — the development manifest's own rows under `__holdout` names — at an
estimated **2.07 h**, against a 12 h budget for both datasets of which development spent
3.66 h. Nothing is cut.

**The pairing is frozen with the set.** Each row carries the development skill score, CRPS,
reference CRPS, coverage and model it is to be reported beside. Freezing which analyses run
and then assembling the development half of the comparison afterwards would leave the
comparison selectable after the fact even though neither half was, and the plan asks for
development and holdout spreads to be read on one axis.

**The rows are renamed and that is a decision, not bookkeeping.** A holdout row writes under
`analysis/results/<combination>/`, so reusing the development names would overwrite the
results the holdout is to be reported against. Every row is its development name with
`__holdout` appended. `check_invariants.check_combos` now reads both manifests, so a holdout
directory is planned exactly as a development one is and one nobody planned still fails.

**What the freeze refuses.** The script will not write a set whose development half is
unfinished: every row must have a conclusion or a reason that is not "waiting for a batch",
every tier-2 slot must be resolved, and `tier2_rule.md` must still hash to what
`manifest_notes.json` recorded before tier 1 ran. A holdout set frozen around the rows that
happened to finish would be chosen by the running order.

**What is deliberately left open.** How `02_setup` is pointed at the full file rather than
at the development file does not exist yet and is batch 16's implementation.
`holdout_freeze.json["left_to_batch_16"]` records the constraint it works under: it may not
change the rows, the scheme, the models or the pairing.

alternatives-considered: **freezing only tier 1 and running tier 2 on the holdout only if
the budget allowed** — rejected: tier 2 is where this project measured that fork effects do
not compose, so a holdout half without it would be a spread computed under an assumption
development has already falsified, and at 2.07 h against 12 there is no budget argument for
it. **Recording the freeze as a git tag rather than a file** — rejected, because a tag is
not readable by the checks or by a reader with the tree in front of them; the commit that
adds this file is the evidence, and the file says so.

agency: agent-autonomous, inside a constraint that is human-set — the plan's §3 fixes that a
holdout manifest exists and is frozen before the holdout opens. What is in it is the
agent's.
information: agent-retrieved — every value read from the files named above.
