# Claim

One booster for the mean and a negative-binomial distribution around it, its dispersion estimated by maximum likelihood on the training fit. The width is a function of the level and of nothing else.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

One booster and one dispersion. The fitted dispersion is **0.313**
(`../../results/family_boosted/head_premise_check.json`), covering a dataset whose
variance-to-mean ratio runs from 2.9 to 842.4 across the eighteen provinces — so a single
shared number is being asked to span more than two orders of magnitude, which is what the
premise recorded before the fit.

It nevertheless produces the best-calibrated model of ours so far: 10–90 coverage 0.825
against a nominal 0.80. The reason the shared dispersion does not hurt as it did in
candidate 1 is that the width here is `mu + mu^2/phi` around a mean the trees place per
cell, so a province the trees separate gets a different width by getting a different mean.
Candidate 1's width was constant on the log scale and could not do that.
