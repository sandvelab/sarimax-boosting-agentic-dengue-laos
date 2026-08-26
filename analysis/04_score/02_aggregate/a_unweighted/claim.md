# Claim

Take the plain unweighted mean over evaluable cells, which is what Chap's own evaluation reports and what the project's success criterion is defined against.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The headline row per model and the four resolutions beside it, all `groupby` aggregations of one per-cell file. Mean CRPS per province spans **0.01 to 84** across the 16 provinces (`results/main/crps_by_location.csv`), which is the measurement behind the warning that an unweighted mean over cells is close to a statement about the largest few provinces.
