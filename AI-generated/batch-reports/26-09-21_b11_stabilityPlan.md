Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 11)

# Batch 11 — the stability plan

## 1. What this batch did

Phase D opens. Batch 10 left a stage 2 that earns its place on the development backtest by a
modest margin (`g_oosErrorBoosting`, mean CRPS 25.16 against stage 1 alone's 26.05, coverage
85.7% against 82.7%), concentrated in four provinces and the later splits. Whether that margin
survives reasonable alternative ways of building either stage is the question phase D exists
to answer, and this batch is the `/perturb plan` step: enumerate the judgment calls, cost them
from measurement, rank them, and freeze the set before any of it is run.

**The node.** `analysis/06_stability`, a sub-analysis of the root numbered after
`05_residualStructure`. The invariant checker's manifest paths, inherited from the prior
project as `05_stability`, were moved to `06_stability` in their own commit, since a change to
the machinery is a methodological change.

**Cost, measured.** `01_measure_run_costs.py` re-ran stage 1 and every stage-2 candidate under
the pinned environment and timed each: the whole existing model tree re-runs in 87 seconds
(stage 1 7.7 s; the per-province candidates 7–10 s; `f_oosErrorRidge` 16 s;
`g_oosErrorBoosting` 22 s). Every re-run reproduced its committed outputs byte for byte, which
is the first whole-tree determinism check this project has had. Compute is therefore not the
binding constraint on stability work; development effort per perturbation is. The compute
budget is set provisionally at one hour of wall-clock, and at the measured costs it excludes
nothing planned.

**The manifest.** `02_plan_manifest.py` wrote `results/manifest.csv` (40 rows) and froze it
(`results/manifest_freeze.json`, sha256 recorded with the planning commit):

- **Tier 1, 6 rows, derived from the tree**: the six not-taken `04_stage2` siblings, already
  run. The invariant checker refuses a manifest whose tier-1 rows disagree with the tree.
- **Tier 2, 29 rows, all planned, ranked by expected informativeness** (estimated 24 minutes
  in total). The top of the ranking: a correction bounded relative to the forecast level (the
  refinement batch 10's Savannakhet diagnosis motivates); the airline specification
  (0,1,1)(0,1,1,12) for stage 1; standardising the stage-2 target by the province's residual
  scale instead of stage 1's se; a rolling 72-month training window that forgets the 2003
  epidemic and the pre-2008 reporting regime. Then the level-only feature set, a
  no-differencing stage 1, a true rolling refit for the in-window errors (the one
  approximation in the new candidates' construction, 15 minutes), the per-horizon fit, Chap's
  default scheme (7 splits, stride 1, horizon 3), the winsorisation bound at 2, 5 and none, an
  alternative seed, the climate anomalies added back, a 2002 window start, four boosting
  configurations, two ridge penalties, clipping off, two feature ablations, two warm-ups and
  two thresholds. Every row names the node, the parameter, the main-path and alternative
  values, and the basis for calling the alternative reasonable.
- **Tier 3, 5 rows, not run, each with its reason**: a log1p stage 1 and a negative-binomial or
  truncated-normal predictive family (both need a verified extension of the CRPS metric; the
  family fork is the most consequential one not run, since the coverage deficit is a heavy
  tail a Gaussian cannot carry), a multiplicative combination rule (undefined where stage 1's
  mean is near zero), an ENSO covariate (a data acquisition and governance call), and
  Chap-native evaluation (decided against in plan §4).

**The run design, fixed now so batch 12 does not improvise it** (`results/manifest_summary.json`):
tier 1 by calling each sibling's `run.sh`; tier 2 by a combination runner in this node that
recomputes stage 1 and the main-path stage 2 under one combination's settings and writes
`results/<combination>/`, trusted only after its `main` combination reproduces
`g_oosErrorBoosting`'s stored per-cell scores byte for byte. Per combination the recorded
conclusion is stage 1's and the two-stage ensemble's mean CRPS and coverage and the sign of
their difference; batch 13 reports the distribution of those, not the best one.

## 2. Judgment calls logged, with agency

- **Numbering the stability node `06`** and moving the checker's paths: `agent-autonomous`.
- **A one-hour provisional compute budget**: `agent-autonomous`; plan §4 left it to phase D,
  and the measured costs make it non-binding. The human may revise it.
- **Splitting ledger row 11–13 into plan / run / report**: `agent-autonomous`; the run cannot
  start before the manifest is frozen and the runner verified.
- **The informativeness ranking** and each row's basis: `agent-autonomous`, written into the
  manifest itself so the ranking is on record before the results are.
- **Tier 3 not run**: `agent-autonomous` for the listing; whether to build the predictive-
  family fork is left to the human, flagged as the most consequential absence.

## 3. Checks run

`/validate invariants`: `tree`, `provenance`, `hashes`, `seeds`, `claims`, `combos`, `freeze`,
`crossing`, `pool` pass; `git` fails only on the pre-existing untracked `.idea/`. The `combos`
check now has a manifest to test and confirms the tier-1 rows match the tree's six not-taken
alternatives. Whole-tree re-run: 8 nodes, all exit 0, all outputs byte-identical.

## 4. What batch 12 inherits

A frozen development manifest of 29 planned perturbations plus 6 siblings, a measured cost per
run, a stated budget that binds nothing, and a run design with a verification gate. Batch 12
builds the combination runner and runs the set; a change to the frozen manifest between now
and then is a recorded decision in the plan's §4b, not an edit.
