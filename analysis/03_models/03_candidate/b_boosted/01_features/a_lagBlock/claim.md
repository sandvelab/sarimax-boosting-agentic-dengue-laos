# Claim

A block of lags and nothing else: the climate columns at the lags a three-month forecast can see, the province's own recent counts at the lags it can see, and the province's size. Time and place enter only through what they imply about those numbers.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Eighteen features: three climate columns at lags 0, 1, 2 and 3; the province's own counts
at lags 3, 4, 5, 6 and 12; and log population
(`results/family_boosted/model_option_spec.json`). No column is standardised and none is
dropped for being missing. 209 of the 2 012 fitted rows have at least one lag that falls
before the record begins, and the boosters carry those as a missing-value direction learned
at each split rather than discarding the rows — which is where this family differs from
candidate 1, whose fit drops them.
