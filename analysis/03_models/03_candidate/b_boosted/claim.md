# Claim

…gradient-boosted trees with a probabilistic head: the conditional distribution of a province-month's count built in two pieces, a boosted-tree fit for where the count sits and a separately estimated head for how wide the distribution around it is. The node's two children are the choices that shape it; the node itself assembles them into one model configuration and sends the model through the same chap eval path as every other model in the project.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**Mean CRPS 20.771 over the same 371 cells, at 52 seconds for the eight-split backtest**
(`results/family_boosted/run_cost.json`) — the best score in the project, ahead of the
reference model's 22.098 and of candidate 1's 23.698
(`analysis/04_score/03_compare/results/family_boosted/leaderboard.csv`). The paired
difference against the reference is **−1.327** with a split-clustered standard error of
**1.110**: 1.20 standard errors, on the other side of zero from candidate 1's 1.03. It
also clears the 0.565 CRPS floor the reference's own unseeded re-runs occupy, which
candidate 1's margin never did.

**It is the first model of ours whose intervals are not too narrow.** 10–90 coverage
**0.825** against a nominal 0.80, and 25–75 coverage 0.693 against 0.50 — over-covering
rather than under-covering, where every previous model of ours was under. The two-part
construction candidate 1 needed to repair half of its width defect is not needed here: a
tree that separates Salavan from Vientiane Capital gives them different widths as a
by-product of giving them different means.

**It repairs the failure candidate 1 could not.** Salavan, which carried the largest single
piece of candidate 1's gap to the reference at 55.09 mean CRPS, scores **35.44** here
against the reference's 38.44 (`analysis/04_score/02_aggregate/a_unweighted/results/
family_boosted/crps_by_location.csv`). In Vientiane Capital, the highest-burden province,
it is **72.97** against the reference's 92.81.

**The lead-time pattern is the reverse of candidate 1's.** By horizon the candidate is
18.36 / 19.25 / **24.69** against the reference's 16.54 / 21.97 / 27.79: it loses the
one-month lead and wins both of the others, where candidate 1 lost the one-month lead
heavily and only drew level at three months. The reference refits inside `predict`; this
model does not, and one month ahead is where that costs most.

The fit itself: 71 boosting rounds chosen on the 316 rows from 2006-05 onward, 71 trees
over 18 features, negative-binomial dispersion **0.313**, fitted on 2 012 of 2 040 rows —
including the 209 rows whose twelve-month lag falls before the record begins, which the
trees carry as a missing-value direction rather than dropping
(`results/family_boosted/fitted_model.json`).

**Neither of the two forks moved.** The richer feature set is worth 0.396 CRPS and the
quantile head costs 0.189, both inside the 0.565 floor, so batch 9's promotion rule leaves
both at their defaults (`AI-generated/candidate-forks/boosted_round1/fork_sweep.json`).
