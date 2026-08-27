# Claim

As a fixed offset, log population: the model forecasts an incidence rate and multiplies it back up by the province's size, so the fit never has to learn how large a province is.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The offset can be taken: population is positive in every province, and the largest is
**23.8 times** the smallest (`results/main/model_option_spec.json`). That ratio is also the
reason the choice matters — a model that had to learn each province's size from its counts
would spend a parameter per province on something the file already says.
