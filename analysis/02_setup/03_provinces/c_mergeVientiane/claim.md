# Claim

Aggregate Vientiane province into Vientiane Capital, which lies geographically inside it, so the province that never reports is not a hole in the map but part of its neighbour. This changes what the headline mean is a mean over, which is why the project's conclusion is a ratio rather than a raw score.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

LA-VI is folded into LA-VT: **2 448 rows, 17 provinces**, and again the same **371** cells (`results/provinces_mergeVientiane/setup_spec.json`). Batch 12 asked whether this child could be scored at all, since it changes what the metric averages over. It can: it changes the *content* of the capital's 24 cells, not the number of cells, because the province it absorbs contributed none.

The merged unit's population is 1 308 736 against the capital's 960 194, and the geodesic areas put **78.1 %** of the merged polygon in the province (`results/provinces_mergeVientiane/merge_weights.csv`), so the merged climate is largely the province's — in 1998-01 rainfall goes from 0.075 to 0.251 mm/day and mean temperature from 24.13 to 22.64 degrees.

Skill rises to **+0.1714**, again mostly by moving the reference (22.098 to 22.937) rather than us (18.817 to 19.006).
