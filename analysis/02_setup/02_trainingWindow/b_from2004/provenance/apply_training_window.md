# Provenance — the training window cut to the second half of the record

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_training_window.py
                     sha256:b12525e80e8a1d3dadee07db43409e56ea07dbd1f6ac13364937e4ebf1cefc2c
invocation:          "$PYTHON" scripts/apply_training_window.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=trainingWindow_from2004.)
inputs:              the analysis dataset produced by whichever child of 01_population ran
                     in this combination — resolved by search, not by name, and its
                     sha256 recorded in results/$COMBO/setup_spec.json as `input_sha256`
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage is a predicate on a date column.
commit:              40b6936
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/02_trainingWindow/b_from2004
produced:            2026-08-29
```

**What it establishes.** Half the record is removed: 2 592 rows in, 1 296 out, 2004-01 to
2009-12, with 1 296 rows dropped and the latest dropped period 2003-12
(`results/$COMBO/setup_spec.json`). The evaluated span begins 2008-01, so nothing inside it
was touched, and the script asserts that rather than assuming it — `evaluated_span_untouched`
is a field, and a cut that reached into the evaluated span would stop the run instead of
producing two children scored on different cells.

**Why the cut is at the midpoint.** The fork exists because the zero rate falls monotonically
across the period. A cut chosen by that zero rate — the first year below some share of zeros —
would let the alternative be tuned by the quantity it is meant to probe, and a perturbation
that can be tuned measures the tuner. The calendar midpoint is arbitrary in the one way that
matters: it is stated as a rule anybody can restate, and it was fixed before the row ran.

alternatives-considered: **a zero-rate threshold** — rejected above. **2003-01**, which
batch 5's sibling docstring named in passing before this child existed, was not chosen: it is
not the midpoint of anything and the reference to it was a stale note, corrected in this batch.
**Several cuts as several children** — a fork with four training windows would measure the
shape of the dependence rather than its existence, and was rejected on the manifest's
arithmetic: every additional child of a `02_setup` fork is a twenty-minute row, of which
seventeen minutes are re-running the reference model, for a curve phase D does not need to
report a distribution.

agency: agent-autonomous. That the zero rate falls, and that it is either transmission or
reporting, was established from the data by batch 3. The cut point, the rule that fixes it and
the comparability check are the agent's.
information: agent-retrieved — the evaluated span is read from the stored scheme file, not
recalled.
