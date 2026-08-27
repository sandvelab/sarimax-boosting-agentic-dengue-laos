# Claim

Population as an estimated coefficient on standardised log population rather than as a fixed offset, so the data decides how reported cases scale with province size instead of the model asserting proportionality.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**23.876** mean CRPS, 0.178 worse than the offset. The fitted coefficient on
     standardised log population is **1.725** and the pooled province spread falls to sigma
     **0.94** from 1.27, which is the coefficient and the intercept explaining the same thing.
     The premise it computed is the check the offset never makes: log mean cases rise **1.74**
     per unit of log population across provinces, where an offset asserts 1.00.
