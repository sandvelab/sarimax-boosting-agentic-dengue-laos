# Claim

Weight the headline mean by the cases actually observed in each cell, so the summary is dominated by the province-months where dengue was happening. A province reporting four cases in twelve years then stops carrying the same weight as the capital.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Weighted by the cases actually observed, the pool scores **88.484** against the reference's **115.216** — skill **+0.2320**, the highest in tier 1. **The number beside it is the result.** Persistence scores **86.598**: on the months when dengue was happening, the simplest baseline in the project forecasts better than the model this project reports.

The calibration inverts too. Our pool is over-dispersed everywhere else — 10-90 coverage 0.863 against nominal 0.80 — and here it is **0.701**, under-dispersed. It is too wide on the quiet months that dominate the unweighted mean and too narrow on the outbreak months that dominate this one.

**137 of 371 cells carry zero weight.** The effective sample falls to **65**, the top decile of cells carries 62.3 % of the weight, and 240 province-by-split groups have no weighted mean at all and are reported missing rather than zero (`results/aggregate_caseWeighted/weighting_notes.json`). This is the opposite blind spot to the unweighted mean's, not a correction of it.
