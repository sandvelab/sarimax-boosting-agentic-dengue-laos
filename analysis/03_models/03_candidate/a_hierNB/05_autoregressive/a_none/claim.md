# Claim

No autoregressive term. The forecast for a province-month is built from the calendar, the climate and the province's own level and annual effect, and nothing about how the current epidemic is going.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The main path.** The information it declines to use, measured rather than argued:
     within a province, log1p counts correlate **0.701** at three months and **0.758** at
     twelve. The seasonal harmonics already carry the twelve-month structure, so at the only
     lag a three-month forecast can use, the lagged count is largely redundant.
