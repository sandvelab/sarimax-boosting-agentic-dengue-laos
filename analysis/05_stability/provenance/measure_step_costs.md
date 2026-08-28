# Provenance — what the pipeline's own steps cost

```
result:              results/step_costs.json
script:              scripts/measure_step_costs.py
                     sha256:8ecc2882b399bc5bbd597b9ebc56d76d594357e6a7774b1d59735f3eb0d0bf52
invocation:          "$PYTHON" scripts/measure_step_costs.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Batch 12 additionally ran it with
                     --check-clean, which verifies that the three timed steps leave the
                     working tree byte-identical.)
inputs:              none read. The measurement is made by running three steps of the
                     main path under COMBO=main and timing them:
                       analysis/02_setup/run.sh
                       analysis/04_score/run.sh
                       analysis/scripts/conclude.py
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Nothing here draws.
commit:              26dca49
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-29
```

**What it establishes.** The three durations the manifest's cost column needs and no
model's `run_cost.json` carries: the setup chain that assembles the dataset, the scoring
chain that turns evaluations into a leaderboard, and the root's conclusion. Measured at
about 1.0–1.6 s, 10–13 s and 0.3 s on this machine; the file carries the run's own figures
rather than a range.

**Why a re-run is a legitimate measurement.** All three steps recompute files that already
exist, from inputs that have not changed, and leave them byte-identical — checked with
`--check-clean`, which fails if git reports anything under `analysis/` modified. A step
that is not idempotent cannot be timed this way, and the check is what says so rather than
an assumption in a comment.

**What is deliberately not timed.** `03_models`. Re-running it re-runs the reference model,
which is unseeded, and would replace its four repeats with a different draw — moving the
denominator of every comparison in the project for the sake of a stopwatch. Its cost is
read from each model's own `run_cost.json` instead, which is a measurement of the run that
produced the numbers rather than of a run made to be measured.

**The figures move between runs and the row set does not.** These are wall-clock
measurements on a shared laptop and they vary by a few tens of percent. So re-running this
node changes `step_costs.json` and the cost columns of `manifest.csv`, and changes nothing
about which combinations the manifest contains, how they are ranked, or what the tier-2
rule says. A cost estimate that is stable to the digit across re-measurement would be
asserting something it cannot know.

alternatives-considered: timing the steps under a scratch combination, which would have
avoided touching `main`'s files at all — rejected because it would leave a combination in
the tree that no manifest row names and no analysis wanted, which is exactly what this
batch's new `combos` invariant exists to forbid. Not measuring at all and carrying batch
5's arithmetic estimate forward — rejected because batch 5 labelled its own table an
estimate and named batch 12 as the batch that replaces it with measurements. Caching the
file and re-measuring only on request — rejected because a cached duration is a duration
from a machine nobody can identify.

agency: agent-autonomous.
