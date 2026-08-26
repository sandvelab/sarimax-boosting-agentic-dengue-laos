# Claim

How should the static population figure enter the analysis dataset? The file carries one population number per province for the whole 1998-2010 record, which is wrong by a decade of growth at both ends.

## Children

kind: alternatives
main-path: a_static

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The population column is **constant within every province** across the whole development
period — verified in `a_static/results/main/setup_spec.json` rather than assumed, since it
is the premise the fork rests on. The main path takes it unchanged. The sibling that
back-casts a per-year series is not built yet.
