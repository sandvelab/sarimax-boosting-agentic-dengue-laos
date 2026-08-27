# Claim

How does the province population enter the model? The file's population figure is one constant per province, and it can serve as a denominator the model forecasts a rate against, as an ordinary covariate, or not at all.

## Children

kind: alternatives
main-path: a_offset

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**How population enters our model does not matter here.** All three children score within
**0.18** CRPS of each other, well inside the 0.57 floor: the offset (the main path,
23.698), dropping population entirely (23.723) and estimating its coefficient (23.876)
(`round2_promoted/fork_leaderboard.csv`).

The reason is visible in the fits. The pooled province effect widens from sigma 1.27 with
the offset to **1.87** with population dropped, and narrows to **0.94** with the
coefficient estimated: the intercept and the population term are explaining the same thing,
and the column is constant within a province so an intercept can stand in for it exactly.

**The premise the offset rests on is nevertheless false.** Across provinces, log mean
reported cases rises **1.74** per unit of log population, where an offset asserts 1.00. It
costs nothing on this backtest because a per-province intercept absorbs the difference --
and it would cost something for a province the model had never seen, which this backtest
never asks about.
