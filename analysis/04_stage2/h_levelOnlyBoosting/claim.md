# Claim

The same target, pooling and family as g_oosErrorBoosting, with stage 2 allowed to see only the horizon, the target month and stage 1's own forecast level relative to the province's residual scale -- the minimal input the diagnostics singled out: does the minimal model earn its place, and does it match or beat the full-feature one?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Yes, and it beats the full-feature model.** Mean CRPS **24.35** against stage 1 alone's
26.05 (**−6.53%**) and against `g_oosErrorBoosting`'s 25.16 (−3.23% on the identical target,
pooling and family), with 90% coverage 85.2% (stage 1: 82.7%; g: 85.7%), 6 of 8 splits
improved (g: 5) and 55.5% of cells (`results/conclusion.json`, `results/comparison.json`).
Stage 1's forecast verified cell for cell against `02_stage1` (408/408, max |Δ| = 0).

The minimal input — horizon, target month, and stage 1's forecast level relative to the
province's residual scale — does everything the full set did and more. By horizon: 19.02 /
24.03 / 30.00 against g's 19.63 / 24.17 / 31.69 and stage 1's 19.47 / 25.60 / 33.08, so the
one-month-ahead loss g had is gone. By province the pattern is g's, sharper: Khammouane −344
(g: −280) and Salavan −304 (−275) CRPS-units summed; Savannakhet now +8 (g: +211) — the
recent-residual and reporting-level features, not the level, were what drove the large
Savannakhet corrections — while Vientiane Capital is worse at +195 (g: +127), the level
shrinkage still wrong in the genuine late-2009 surge.

**Annotated as `04_stage2`'s main path (batch 14)**, by the rule written in the plan's §4b
before `j_levelOnlyBoundedBoosting`'s result was seen: lowest development mean CRPS with
coverage not worse than stage 1's, a tie within 0.1 CRPS broken by more splits improved, then
by the simpler configuration. `j` (24.29) and `h` (24.35) tie on the first criterion and on
splits improved (6 of 8); `h` is the simpler. This is the third round of selection on the
same 371 development cells; the sealed 2010 holdout evaluates it once, across a manifest
frozen beforehand.
