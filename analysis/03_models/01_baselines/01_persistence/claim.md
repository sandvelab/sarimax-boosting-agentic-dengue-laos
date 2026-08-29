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

**The fork moves the leaderboard row by 4.181 CRPS, and it moves it the wrong way for the
main path.** The parametric construction — a negative binomial about the last observation,
mean floored at 0.2, dispersion fitted from the last five observations — scores **20.698**
against the non-parametric main path's **24.879**, and beats the reference model where the
main path is 2.781 CRPS behind it. How uncertainty is wrapped around a point forecast is
worth more here than every choice about the dataset that batch 13 measured.

**The main path's reasoning was sound and its conclusion was wrong.** Batch 6 chose the
non-parametric form because it estimates nothing and needs no arbitrary floor, and because
52 % of observed months are zero. That is true; the parametric form needs *two* arbitrary
constants on this data, not one, since the maximum-likelihood dispersion does not exist for
an all-zero window and has to be bounded. It wins anyway. A construction that estimates
nothing also cannot learn that this province's counts are stickier than that one's, and on a
series where provincial burdens differ by four orders of magnitude that is what the fitted
dispersion buys.

**The fork is not promoted, and the reason is that phase C is closed.** Batch 11 closed model
development, and the phase-D manifest was frozen and committed before any of it ran; moving a
main path on the strength of a stability row would make the reported analysis a function of
the stability run, which is the ordering the whole design forbids. What this row does is
report that the reported analysis sits on the worse of two published constructions, which is
a more useful thing for the manuscript than a better number would have been.
