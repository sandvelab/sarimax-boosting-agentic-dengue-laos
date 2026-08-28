# Claim

How much weight does each member of the pool carry? Every member is a model that was fitted and evaluated on this dataset already, and the two answers differ in whether the pool is told anything about how well they did.

## Children

kind: alternatives
main-path: a_equal

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The fork does not move, and the reason is the most useful thing in the batch.** Equal
weights score **18.817**; the minimum-CRPS weights score **22.838**
(`AI-generated/candidate-forks/ensemble_round1/fork_leaderboard.csv`). Estimating the
weights costs **4.021 CRPS** — seven times the 0.565 floor, in the wrong direction — so
batch 9's promotion rule leaves `a_equal` on the main path, as it would have even if the
gap had been a tenth the size.

**What estimating them did.** On the validation year held back inside the training frame,
the pooled CRPS at the fitted weights is 14.227 against 17.026 at equal weights: fitting
looked worth 2.799 CRPS where it was fitted. It put 0.953 of the pool on candidate 1,
which was the best member on that year at CRPS 14.253. On the evaluated period candidate 1
is the *worst* of the three non-baseline members at 23.698, and the pool it dominates
scores 22.838 — 2.067 worse than the best member it was supposed to be selecting.

So the fork measures one thing cleanly: **on this dataset, one year of held-back data
cannot tell which member will be best on the next two.** That is the failure the plan's
phase C names — fitting the available data rather than the data-generating process — with
the two sides of it in one table, and the model that estimates nothing is the one that
survives it.
