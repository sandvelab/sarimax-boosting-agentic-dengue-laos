# Claim

How far does the project's conclusion survive the reasonable alternatives the main path did not take? The node enumerates every judgment call the tree carries as a fork, costs the analyses that take them instead, and runs that set so the reported result is a distribution over analyses that all looked defensible rather than the one that was run.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The tree carries **17 forks**, not the ten batch 5 counted by hand: phase C added five while
building the candidates, and two baseline forks were never on the hand-written list although
the plan's phase D names one of them. `results/forks.csv` is read from the tree, so the next
fork anyone adds is in the manifest without anyone remembering to add it — and
`/validate invariants` fails if it is not.

The manifest is **24 tier-1 combinations**, one per path not taken, plus **8 tier-2 pairs**
selected by a rule fixed and hashed before tier 1 ran, plus one combination that already
exists and perturbs nothing. Tier 1 costs **124 minutes on development and 75 on the
holdout**, against a 12-hour budget, so **nothing is cut** and the cut order is recorded
against the day something is (`results/manifest_notes.json`).

**Compute is not what binds, and it is not close.** Of the 124 development minutes, **89 are
the reference model** — five setup rows at four unseeded repeats each, through an amd64
image under emulation, for a model the plan forbids perturbing. Every model of ours, on
every combination in tier 1, costs 21 minutes together.

What binds is that **nine of the 24 rows have no scripts**: the tree named those children in
prose and did not carry them until this batch created them. And twelve of the fifteen that
do have scripts hold results produced around a main path that has since moved, so their
directories describe a different analysis from the one their manifest row now names.

No conclusion is stated here yet. `results/conclusions.csv` has 1 of 33 rows and says why
the other 32 are empty, which is the honest state of a manifest that has been written and
not yet run.
