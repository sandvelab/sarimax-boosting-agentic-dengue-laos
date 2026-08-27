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

**Refitting inside `predict` is worth more than any other unmoved fork, and it is the one
place our model was handicapped against the reference.** `b_refitAtPredict` scores
**22.825** mean CRPS from the promoted main path against 23.698 -- a gain of **0.873**,
outside the 0.57 floor, and the closest any model of ours has come to the reference's
22.098 (`round2_promoted/fork_leaderboard.csv`).

The asymmetry it measures is real: `chapkit_ewars_model` fits inside its own predict
endpoint, so at every split of the backtest it has been using history our train-time fit
discards -- **21 months** of it by the last split.

It costs **108 seconds** against 36, which is eight fits instead of one, and it leaves no
single fitted object for the record, since the fit happens once per split inside chap-core's
untracked run directories.

**It was not promoted**, because around the batch-8 configuration -- the sweep the
promotion rule was applied to -- it was worth 0.408 and inside the floor.
