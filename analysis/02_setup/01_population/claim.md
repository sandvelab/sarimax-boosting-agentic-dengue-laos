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

**The sibling is built and run.** Back-casting the snapshot to a per-year series with the archived national population series moves the conclusion from +0.1485 to **+0.1347**, and establishes that the archived column does not have the level its schema claims: it sums to 4.96 million against a 2020 national total of 7.35 million, matching the country's population around **1995**. See `b_backCast/claim.md`.

The population column is **constant within every province** across the whole development
period — verified in `a_static/results/main/setup_spec.json` rather than assumed, since it
is the premise the fork rests on. The main path takes it unchanged. The sibling that
back-casts a per-year series is not built yet.
