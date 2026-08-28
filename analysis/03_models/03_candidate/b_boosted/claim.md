# Claim

…gradient-boosted trees with a probabilistic head: the conditional distribution of a province-month's count built in two pieces, a boosted-tree fit for where the count sits and a separately estimated head for how wide the distribution around it is. The node's two children are the choices that shape it; the node itself assembles them into one model configuration and sends the model through the same chap eval path as every other model in the project.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_
