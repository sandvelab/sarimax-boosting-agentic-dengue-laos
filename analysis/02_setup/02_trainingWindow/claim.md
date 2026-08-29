# Claim

How much of the record should models be allowed to learn from, given that the share of zero-valued months falls monotonically across the period and the early years may describe a different reporting regime?

## Children

kind: alternatives
main-path: a_from1998

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The sibling is built and run.** Starting at 2004-01, the calendar midpoint, discards half the record and costs **0.0219 of skill** (+0.1266 against the main path's +0.1485) while leaving the 371 evaluated cells identical — the comparability the paragraph below predicts, checked by the sibling rather than assumed. See `b_from2004/claim.md`.

All 2 592 rows reach the models: no year is discarded on the main path. Because chap-core
lays its splits out backwards from the last period of the file, a sibling that truncates the
early years would change what the models learn from and leave the 371 evaluated cells
identical — which is what makes this fork's children directly comparable.
