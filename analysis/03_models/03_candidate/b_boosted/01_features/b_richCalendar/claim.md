# Claim

The same lag block, plus what the calendar and the map say directly: the month as a pair of harmonics, a year index, the province as an identifier, and rolling summaries of the province's own recent history.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Twenty-seven features: the sibling's eighteen, plus two harmonic pairs of the month, a year
index, the province as an identifier, and rolling means of the count over 3, 6 and 12
months ending at the third lag (`results/features_richCalendar/model_option_spec.json`).

**It scores 20.375 against the sibling's 20.771** — better by 0.396 CRPS, which is inside
the resolvable floor and so does not move the fork. Its point forecast is worse (MAE 28.251
against 26.953) and its intervals wider (10–90 coverage 0.857 against 0.825), which is the
signature of a model that has fitted the training years more closely and is less certain
about a period it cannot extrapolate into. Both costs registered before the run — sixteen
extra cuts from the province identifier, and a year index every forecast month falls beyond
— are consistent with what happened, and neither is separable from the other by this run.
