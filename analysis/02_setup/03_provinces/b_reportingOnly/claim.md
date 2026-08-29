# Claim

Remove the two provinces that cannot be evaluated before the dataset reaches the platform, so they are absent from training as well as from scoring. Vientiane province never reports and Xaisomboun stops in 2005; the main path leaves both in the training frame and lets the platform drop them later.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**LA-VI and LA-XN are removed**, leaving 16 provinces and 2 304 rows, and the same **371** evaluable cells (`results/provinces_reportingOnly/setup_spec.json`). The pair is derived from the rule — no non-missing `disease_cases` inside the evaluated span — rather than named, so a province that went silent for another reason would be caught by the rule instead of missed by a constant.

**The skill score rises to +0.1861, and almost none of that is us.** Our pool moves 18.817 to 18.843; the reference moves 22.098 to **23.150**. Taking two unevaluable provinces out of the training frame costs the reference more than a standard error and costs us nothing measurable — presumably because it pools across provinces while fitting. This is the clearest case in tier 1 of a setup choice moving *the comparison* rather than either model, and it is invisible in a headline that reports only our own score.
