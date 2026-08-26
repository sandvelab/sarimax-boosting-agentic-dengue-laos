# Claim

Wrap the point in the empirical distribution of past h-step changes within the same province, each change entered with its negation so the predictive median stays on the last observation, truncated at zero.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Mean CRPS **24.879** over 371 cells in 16 provinces, 28 seconds for the eight-split backtest (`results/main/run_cost.json`). Identical to batch 6's vertical-slice figure to the last digit, and byte-identical across two independent runs.
