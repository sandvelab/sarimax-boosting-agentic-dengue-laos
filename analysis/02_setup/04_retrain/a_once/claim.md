# Claim

Refit once, at chap-core's default n-retrain 1: a single fit on the training period, with an expanding historic window handed to predict at every split.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

`n_retrain = 1` is written into the stage specification and reaches `chap eval` from there (`results/main/setup_spec.json`).
