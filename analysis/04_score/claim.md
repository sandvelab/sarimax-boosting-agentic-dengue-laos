# Claim

What does each model score, and how do they compare, at every resolution the platform allows? Scores are collected once at the platform's finest resolution and everything reported is an aggregation of that one file.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The leaderboard for this combination, from best to worst mean CRPS: the reference at
**22.098**, seasonal climatology at **24.337**, persistence at **24.879**
(`03_compare/results/main/leaderboard.csv`). Every figure is an aggregation of one per-cell
file, and that file is written from chap-core's own registered metrics.

The node's substantive answer is not the ordering but **what the ordering can support**, and
that is at `03_compare`.
