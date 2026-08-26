# Claim

What forecast does each model make on that common ground? The node holds every model the project scores — our baselines, our candidates and the external reference — so that all of them traverse the identical evaluation path.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Three models have run on the common ground, all through the same `chap eval` path: the two
baselines the plan requires and the external reference. Their scores are computed at
`04_score`, not here.

What this node establishes about *how* they were run: a model of ours reaches the platform
through exactly one piece of code (`scripts/lib/chap_eval.py`), which reads the dataset and
every backtest flag from `02_setup` and hashes the model's own files into its spec before
the run. So the constraint the plan states for phase C — that no candidate is compared on a
metric computed a different way — holds structurally rather than by care.

**A native model of ours costs about 28 seconds for a full eight-split backtest; the
emulated reference costs about 268 seconds per repeat**, four repeats to a combination
(`*/results/main/run_cost.json`). Implementation effort, not evaluation, is what binds this
project, which is what batch 4 concluded from one measurement and what two more confirm.
