# Claim

Over what weighting is the headline mean taken? The provinces differ in burden by four orders of magnitude, so an unweighted mean over cells and a mean weighted by population or by cases are three different summaries of the same per-cell file.

## Children

kind: alternatives
main-path: a_unweighted

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The headline figures under the unweighted mean, and the four resolutions beside it. The
per-province file is where the aggregate's weakness shows: mean CRPS per province spans four
orders of magnitude, from 0.01 in Phongsaly to 84 in Vientiane Capital, so the unweighted
mean over cells is very nearly a statement about the largest few provinces.

The population-weighted and case-weighted siblings are not built yet. They cost seconds when
they are, because re-weighting re-runs no model.
