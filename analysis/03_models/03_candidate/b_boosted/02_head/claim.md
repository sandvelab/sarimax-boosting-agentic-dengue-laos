# Claim

Where does the spread of the forecast come from? A boosted tree returns one number per cell, so the predictive distribution has to be constructed around it, and this is the choice of how.

## Children

kind: alternatives
main-path: a_negBinomial

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The fork does not move the model, and the two heads fail in opposite directions.** The
negative binomial scores **20.771** and the quantile ladder **20.960**, a difference of
0.189 CRPS — well inside the 0.565 floor, so the main path stays at `a_negBinomial`.

**On the metric the project reports beside CRPS, the ladder is the better head.** Its
10–90 coverage is **0.798** against a nominal 0.80 — the closest any model in the project
has come — where the negative binomial over-covers at 0.825. But its point forecast is the
worst of any model of ours: **MAE 33.020** against 26.953, because the lower half of its
distribution is pinned at zero and its median is therefore far below the outcome in every
province that reports steadily. A head that is well calibrated on average and wrong in the
middle is not the better head, and this is the plan's "a model that wins on mean CRPS while
being badly calibrated has not won", arriving with the two halves swapped.

**Why the ladder's lower half is pinned at zero was predicted before it ran and then
measured.** 56.3 % of the observed counts are exactly zero, so every quantile level below
that share begins at the marginal quantile — zero — and meets a residual of exactly zero at
the majority of rows, which is the kink of the pinball loss and says nothing about
direction. The prediction registered eight of the fifteen levels as stranded; **seven are
flat at zero across the whole file** and the eighth, 0.50, is flat in Vientiane Capital,
whose observed median is 109 cases and which never reports a zero at all
(`../results/head_quantileEnsemble/head_premise_check.json`). The bottom 40 % of every
forecast this head makes is a point mass at zero.

**This is where batch 4 said the family would fail, and it is where the family fails.** The
repair — a model for whether the month reports at all, with the ladder fitted only to the
months that do — is the construction candidate 1's `01_observation` fork calls a hurdle. It
would be a third child of this fork, not a change to this one.
