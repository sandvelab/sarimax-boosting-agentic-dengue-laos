# Claim

Population does not enter the model at all: a province's level is carried entirely by its own pooled intercept, which is estimated from its record rather than from its size.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**23.723** mean CRPS, 0.025 from the main path -- two orders of magnitude inside the
     resolvable floor. Dropping the population column changes nothing this backtest can
     measure, because the column is constant within a province and the pooled intercept
     absorbs it exactly: the province spread widens to sigma **1.87** from 1.27.
