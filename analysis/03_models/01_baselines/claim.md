# Claim

How well does the problem's own inertia forecast it? Two baselines the plan requires: what the series did last, and what the series usually does in this calendar month.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Both baselines the plan's §4 requires are implemented against the Chap contract and
evaluated through the identical path. **Seasonal climatology scores 24.337 mean CRPS and
persistence 24.879**, over the same 371 cells
(`04_score/02_aggregate/a_unweighted/results/main/metrics_summary.csv`).

The two are 0.54 CRPS apart, which is at the edge of what this evaluation can resolve — the
reference's own re-runs move by up to 0.57 — so the honest reading is that **knowing the
season and knowing the last observation are worth about the same here**, not that one
baseline is better. Their calibration differs more than their score does: climatology's
central interval is too wide (0.542 against a nominal 0.50) where persistence's is almost
exact (0.491), and both have tails far too thin (0.650 and 0.666 against 0.80).

Both contain no randomness, and that is verified rather than asserted: two independent runs
of each produced identical per-cell scores and identical fitted models
(`AI-generated/determinism-checks/model_determinism.json`).

**Batch 22 ran both baselines' alternative constructions, and they are the two extremes of
the stability set so far.** Wrapping the persistence point in a fitted negative binomial
rather than in the empirical distribution of past changes is worth **4.181 CRPS** (24.879 →
20.698) and takes the baseline past the reference model; freezing the climatology's estimation
window is worth **0.532 CRPS** (24.337 → 24.869), inside the noise floor. The better
persistence construction reaches the reported model too, because the pool takes both baselines
as members — and makes it **worse**, 18.817 → 19.434.

So the honest reading of "knowing the season and knowing the last observation are worth about
the same here" is narrower than it looked: it is true of the two constructions the main path
happens to run, and knowing the last observation is worth considerably more when its
uncertainty is wrapped the other published way.
