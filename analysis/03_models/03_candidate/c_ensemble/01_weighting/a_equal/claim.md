# Claim

Every member carries the same weight. The pool is told nothing about how well its members did, so no member's weight can be a selection made on data the backtest will later score.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**On the main path, at weight 0.25 each** (`results/main/model_option_spec.json`,
`../../results/main/pool_check.json`). The pool it produces scores 18.817, ahead of the
minimum-CRPS sibling's 22.838 and of all four of its own members.

**The premise registered here before the run was half wrong, and the wrong half is the
finding.** It predicted that an equal pool would score worse than its best member, because
half its mass sits on the two required baselines and they are the two worst-scoring models
of ours. The pool beat its best member by 1.954 CRPS. The prediction reasoned about where
the forecasts sit and not about how wide they are, and CRPS is a function of both: every
member except candidate 2 under-covers its 10–90 interval, and pooling widens.

The other half held exactly as stated: the pool's 10–90 coverage, 0.863, is above the
largest of its members' (0.825), so it is wider than any member and over-covers where one
member already did.
