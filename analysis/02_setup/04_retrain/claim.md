# Claim

How often is a model refitted across the backtest? Chap's n-retrain governs whether one fit serves all splits or each split gets its own.

## Children

kind: alternatives
main-path: a_once

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

`n_retrain = 1` reaches `chap eval` from a file rather than from a constant in each model's
runner, so two models cannot disagree about it silently. The flag governs how often
chap-core calls `train`; it does not stop a model that fits inside `predict` from refitting
at every split, which is what the reference model does. That distinction is recorded because
one flag can otherwise look as though it had made all the models comparable in this respect.
