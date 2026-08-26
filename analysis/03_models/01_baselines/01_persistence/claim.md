# Claim

How well does the last observed count forecast the next three months? A persistence forecast is a point, and CRPS scores a distribution, so the baseline is only defined once a predictive distribution is wrapped around that point — and how to wrap it is the question this node forks on.

## Children

kind: alternatives
main-path: a_empiricalChange

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The persistence baseline scores **24.879 mean CRPS** over 371 cells, with 10-90 coverage
0.666 and 25-75 coverage 0.491. Run from this node on the assembled dataset, it reproduces
batch 6's vertical-slice figure to the last digit, which is the check that the tree added no
arithmetic of its own between the platform and the number.

The main path wraps the point forecast in the empirical distribution of past h-step changes.
The sibling — a negative binomial with a floor on its mean — is documented in the model's own
README and built when the stability manifest needs it.
