# Claim

Does the model do its fitting in train or in predict? Chap fits once and then predicts at every split, so a model that refits inside predict sees each split's expanded history while one that does not sees only the training period.

## Children

kind: alternatives
main-path: a_trainOnly

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_
