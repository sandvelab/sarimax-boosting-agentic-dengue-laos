Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 14)

# Batch 14 — stage 1 fixed and documented; a third stage-2 iteration; the main path annotated

## 1. What this batch did

After phase D the human set three things (plan §4b, 2026-09-21): stage 1 is not repaired —
it stays the per-province SARIMAX as specified, and its weaknesses are documented instead;
stage 2 is explored further; and one stage-2 configuration is annotated as the main path
now, before the holdout manifest is frozen. This batch did the three, and re-planned the
development stability manifest around the new main path.

**Stage 1's weaknesses, in one place.** `05_residualStructure/scripts/03_stage1_weaknesses.py`
reads the diagnostics and stage 1's own results and writes `results/stage1_weaknesses.json`:
six weaknesses, each with its evidence, its effect on the forecasts, whether a stage 2 can
address it, and the stage-1 fork not taken. In brief: (1) coverage below nominal because the
standardised error is heavy-tailed — median |z| 0.3, one percent of cells beyond 23 — so that
rescaling sigma to nominal coverage costs CRPS 26.05 → 35.65 and no additive stage 2 can help;
(2) negative means in 4% of cells; (3) a standard error that does not grow with the level, so
the same standardised correction is 130–190 cases in Savannakhet and under one in
Xiangkhouang; (4) systematic multi-step bias by level and season, which is what the batch-10
stage 2 learns; (5) the 2008–09 reporting-regime breaks, unpredictable from a province's own
history; (6) a first-default specification whose own score moves between 23.99 and 29.15 under
alternative orders and windows. `02_stage1/claim.md` carries the prose.

**Three stage-2 configurations as nodes.** The two stage-2 changes the v1 stability run scored
best, and their combination, built through the parametrised pipeline batch 12 verified against
`g` (each node's content is its configuration, its verification against `02_stage1` — 408 of
408 cells, exact — and its answer):

| Candidate | Change from `g_oosErrorBoosting` | Mean CRPS | vs stage 1 (26.05) | Coverage (stage 1: 82.7%) | Splits improved |
|---|---|---|---|---|---|
| `h_levelOnlyBoosting` | input: horizon, month, forecast level only | 24.35 | −6.53% | 85.2% | 6 of 8 |
| `i_boundedBoosting` | correction bounded at max(stage-1 mean, 10) | 24.53 | −5.85% | 85.7% | 7 of 8 |
| `j_levelOnlyBoundedBoosting` | both | 24.29 | −6.78% | 85.2% | 6 of 8 |

All three clear both of plan §2's bars. The minimal input is the larger gain and on its own
removes most of the Savannakhet loss (+8 CRPS-units summed under `h`, against +211 under `g`):
it was the recent-residual and reporting-level features, not the level, that drove the large
Savannakhet corrections. The bound adds −2.52% on the full input and only −0.26% on the
minimal one; the two gains overlap. Vientiane Capital's loss persists in every configuration.
By horizon, `h` improves all three (19.02 / 24.03 / 30.00 against stage 1's 19.47 / 25.60 /
33.08), where `g` had lost at one month ahead.

**The main path, annotated now by a pre-registered rule.** Before `j`'s result was seen the
rule was written into the plan: among `g`, `h`, `i`, `j`, the lowest development mean CRPS with
coverage not worse than stage 1's; a tie within 0.1 CRPS broken by more splits improved, then
by the simpler configuration. `j` (24.29) and `h` (24.35) tie, both improve 6 of 8 splits, and
`h` is the simpler: **`h_levelOnlyBoosting` is `04_stage2`'s main path** (own commit, reversible).
The rule and its application are in `j_levelOnlyBoundedBoosting/results/all_candidates_comparison.json`.
This is the third round of selection on the same 371 development cells; the sealed 2010
holdout, opened once across a manifest frozen beforehand, is the guard.

**The stability manifest, re-planned around `h` (v2).** The v1 manifest was built around `g`.
Its rows and results are kept, marked superseded, so the batch-13 report stays a true record
of `g`'s stability; v2 adds a `main@h` gate row, the nine not-taken siblings as tier 1, and 26
tier-2 rows around `h` (suffixed `@h`): the same stage-1, window, scheme, target, combination,
hyperparameter, seed and error-construction perturbations as v1, with the feature rows turned
around — adding back to the minimal input the groups `h` dropped — and the bound tried without
its floor. Batch 15 runs it.

## 2. Judgment calls logged, with agency

- **Stage 1 not repaired; weaknesses documented**: `human-set`. The documentation's content
  and wording: `agent-autonomous`; its numbers are read from result files.
- **Which three stage-2 configurations**: `agent-autonomous`, the two best v1 rows and their
  combination; exploring further is `human-set`.
- **The main-path rule** (its criteria and the 0.1 tie band): `agent-autonomous`, written
  before `j`'s result; annotating now is `human-set`. A strict lowest-CRPS rule would have
  picked `j` on a 0.06 difference smaller than the seed's own effect.
- **Reusing the verified pipeline for the new nodes** instead of re-implementing it:
  `agent-autonomous`.
- **v1 manifest superseded, not edited**: `agent-autonomous`; a change of main path after
  phase D is the cost of exploring further, and it is paid by a v2 run, not by rewriting v1.

## 3. Checks run

`/validate invariants`: all pass except `git` (pre-existing untracked `.idea/`). Stage-1
verification 408/408 in all three new nodes. `combos` confirms the v2 tier-1 rows match the
tree's nine not-taken alternatives.

## 4. What batch 15 inherits

A main path annotated by rule, a v2 manifest frozen around it (26 planned rows, the gate, nine
siblings, five not run, 29 superseded), and the runner adapted to it. Batch 15 runs v2 and
reports its distribution beside v1's; batch 16 freezes the holdout manifest. The line-ending
item (row 19) stands.
