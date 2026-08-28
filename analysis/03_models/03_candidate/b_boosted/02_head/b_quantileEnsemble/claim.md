# Claim

A ladder of quantile boosters, each fitted to a different quantile of the same target, and the forecast drawn from the distribution they trace out. The width is learned per cell rather than derived from the level.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Fifteen boosters, 1 302 trees, and a lower half that does not exist
(`../../results/head_quantileEnsemble/head_premise_check.json`).

**Seven of the fifteen levels are flat at zero across the whole file** — the largest count
any of them returns anywhere is 0.3 — and the eighth, 0.50, is flat in Vientiane Capital,
where the observed median is 109 cases. Seven of those eight took a single boosting round
before their loss on the held-back months stopped improving, and 0.50 and 0.60 ran to the
400-round cap without settling. The registered prediction named eight levels; seven met the
test as stated and the eighth met it in the province the prediction was about.

The head scores **20.960** mean CRPS — 0.189 worse than the sibling, inside the floor — with
the project's closest interval coverage (0.798 against nominal 0.80) and its worst point
forecast (MAE 33.020). Fitting the ladder was also the most expensive thing in the batch at
75 seconds against 52.

**The ladder crossed on 1 408 of 2 012 training rows**, repaired by cumulative maximum
before anything was drawn, with a largest repair of 2.49 on the log1p scale
(`../../results/head_quantileEnsemble/fitted_model.json`). Fifteen boosters fitted without
reference to each other do not produce fifteen ordered quantiles, and the size of the
disagreement is recorded rather than only the fact of the repair.
