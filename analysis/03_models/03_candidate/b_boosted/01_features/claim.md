# Claim

Which features does the booster see? Trees cannot extrapolate a trend or interpolate a cycle, so what a boosted model knows about time and place is exactly what the feature matrix says, and this is the choice of how much to say.

## Children

kind: alternatives
main-path: a_lagBlock

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The fork does not move the model.** The lag block alone scores **20.771** and the rich
calendar **20.375**, a difference of 0.396 CRPS — inside the 0.565 floor the reference's own
re-runs occupy, so by the rule batch 9 fixed the main path stays at `a_lagBlock`
(`AI-generated/candidate-forks/boosted_round1/fork_leaderboard.csv`).

**What the richer set buys is not accuracy but width.** Its point forecast is worse — MAE
28.251 against 26.953 — and its intervals are wider: 10–90 coverage 0.857 against 0.825,
further from nominal on the over-covering side. A boosted model given the province as an
identifier and a year index fits the training years more closely and forecasts a period it
cannot extrapolate into with correspondingly less confidence, which is what the two
numbers together say.

**So the twelve-month lag was enough.** `a_lagBlock` has no month, no year and no province
identifier, and describing all three explicitly moved the score by less than the evaluation
can resolve. On this dataset a tree given last year's count in the same province has
already been told what the calendar would tell it.
