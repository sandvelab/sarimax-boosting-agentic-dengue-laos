# Claim

Which model family should our candidate be? Each child is one family — one possible answer to the same question of what forecast our model makes — so exactly one of them is ever the reported model, and the others are re-run in the stability work rather than discarded.

## Children

kind: alternatives
main-path: a_hierNB

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**One family exists so far, and it is the main path by default rather than by comparison.**
`a_hierNB` scores a development mean CRPS of **26.100** over the 371 evaluated cells
(`04_score/03_compare/results/main/leaderboard.csv`), which is last of the four models the
project has scored. The switch this node performs is therefore not yet a choice: `b_boosted`
and `c_ensemble` are batches 10 and 11, and until they exist the node records that the
family question has one answer available and no comparison behind it.
