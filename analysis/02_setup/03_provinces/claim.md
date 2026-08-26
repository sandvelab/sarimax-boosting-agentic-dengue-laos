# Claim

Which provinces belong in the analysis at all? One province reports nothing across the whole record and a second stops reporting partway through, and what the headline mean is a mean over depends on the answer.

## Children

kind: alternatives
main-path: a_chapFilter

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

18 provinces go to the platform; **16 contribute 371 evaluable cells**. One province
(LA-VI, Vientiane) never reports and the platform's region filter drops it; one (LA-XN,
Xaisomboun) survives the filter and has no observation inside the evaluated span, so it
contributes nothing. The figure is recomputed here from the dataset and the stored scheme
(`a_chapFilter/results/main/setup_spec.json`) and agrees with batch 3's and with what the
evaluation produced.

Unlike the other three forks, this one's siblings change *what is evaluated*, so raw CRPS is
not comparable across them. That is survivable only because the project's reported
conclusion is a ratio to the reference computed on whatever cell set the child produced.
