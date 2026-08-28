# Claim

…a weighted combination of the models this project already has: the two candidate families and the two required baselines, pooled into one predictive distribution rather than chosen between. The node's one child is the choice of weights; the node itself assembles the members, sends the pooled model through the same chap eval path as every other model, and so asks whether combining beats selecting.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**Mean CRPS 18.817 over the same 371 cells, at 63 seconds for the eight-split backtest**
(`results/main/run_cost.json`) — the project's best score and the first model of ours to
beat the reference model, whose development mean is 22.098
(`analysis/04_score/03_compare/results/main/leaderboard.csv`). The skill score against the
reference is **+0.1485** and the paired difference is **−3.282** with a split-clustered
standard error of **1.726**, which is 1.90 standard errors: the pool is ahead of the
reference by nearly six times the 0.565 CRPS floor the reference's own re-runs occupy, and
still short of separating the two.

**The pool beats every model in it, by 1.954 CRPS over its best member.** That was
predicted not to happen: `01_weighting/a_equal` registered, before the model ran, that an
equal pool putting half its mass on the two required baselines would score *worse* than
its best member and better than their mean. The second half held and the first did not
(`results/main/pool_check.json`). What the prediction left out is that CRPS rewards
calibration as well as location, and the members are individually under-dispersed —
10–90 coverage 0.650 to 0.825 against a nominal 0.80 — so the spread the pool adds by
disagreeing with itself is spread the members were missing.

**The mechanism is verified by a second path, not asserted.** The pool rebuilt from the
members' own stored evaluations — the files produced when each was run on its own, through
its own node — and scored with chap-core's own CRPS gives **18.801** against the 18.817 the
model scored, a difference of 0.016, which is the sampling error of the pool's own
allocation. The members' scores computed by that second path reproduce their leaderboard
rows exactly, so the models inside the pool are the models on the leaderboard.

**It is the most over-dispersed model in the project, and that is the cost of the win.**
10–90 coverage 0.863 against nominal 0.80, and 25–75 coverage 0.749 against nominal 0.50.
The obvious innocent explanation — that a count distribution with a 56 % zero share has a
degenerate central interval — was measured and does not hold here: the pool's 25–75
interval is a single point in 24 % of cells against 41 % to 55 % for three of its four
members, so it over-covers while being *less* exposed to the artefact than they are. A
linear opinion pool is over-dispersed even when every member is calibrated, and this is
that, plainly.
