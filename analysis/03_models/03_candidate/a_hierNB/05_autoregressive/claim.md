# Claim

Does the model see the recent case history, or only the calendar and the weather? A seasonal regression forecasts the average year; the last observed count is what would tell it whether this year is one of the bad ones.

## Children

kind: alternatives
main-path: a_none

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The recent case history carries nothing this model can use.** `b_lag3` scores **23.345**
against the main path's 23.698, a gain of 0.353 that is inside the 0.57 CRPS floor; around
the batch-8 configuration the same child was worth **−0.075**. Neither number is
attributable.

**The premise says why, and it was computed before the child was run.** Within a province,
log1p counts correlate **0.701** at three months' lag and **0.758** at twelve. Three months
is the shortest lag one model can use at all three of Chap's forecast horizons, and at that
distance the lagged count is mostly telling the model what month of the year it is --
which the seasonal harmonics already say. Batch 7's finding that a persistence baseline is
level with the reference at *one* month's lead does not survive the trip to three.

The node's other purpose is served whatever it scored: the term batch 8 declined to add is
now a child with a claim, a premise and a number, rather than a paragraph in a report.
