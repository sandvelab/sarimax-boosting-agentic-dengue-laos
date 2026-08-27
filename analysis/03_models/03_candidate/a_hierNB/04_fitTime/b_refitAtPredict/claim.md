# Claim

The model is refitted inside every predict call, on the whole expanding historic window Chap hands it, so that a forecast late in the backtest is made by a model that has seen the years between. This is what the reference model does.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**22.825** mean CRPS, the best combination in the second sweep and **0.873** better
     than the main path, at **108** seconds against 36. It recovers the 21 months of history a
     train-time fit discards by the last split -- the history the reference model has been
     using all along. It leaves no single fitted object: the fit happens once per split inside
     chap-core's untracked run directories, and `train` writes a stub that says so.
