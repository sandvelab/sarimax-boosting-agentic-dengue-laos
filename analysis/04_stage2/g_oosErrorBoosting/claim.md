# Claim

Same target and features as f_oosErrorRidge (stage 1's h-step out-of-sample error, pooled across provinces on the standardised-error scale), fitted with shallow gradient-boosted trees instead of a ridge regression: does a non-linear family find structure the linear one misses, and does either earn its place against stage 1 alone?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Yes to both.** On identical training rows and features, shallow gradient-boosted trees
score mean CRPS **25.16** against stage 1 alone's 26.05 (**−3.41%**) and against
`f_oosErrorRidge`'s 25.63, with 90% coverage **improved** to 85.7% (stage 1: 82.7%; ridge:
84.6%) — the best of the seven stage-2 candidates on both criteria (`results/conclusion.json`,
`results/comparison.json`, `results/all_candidates_comparison.json`). Determinism verified by
a second run, byte-identical.

Decomposition: stage 1 26.05 → clipped 25.91 → corrected, unclipped 25.30 → corrected and
clipped 25.16; the correction alone against the clipped stage 1 is −2.87%. Unlike the ridge,
the gain is entirely at h=2 and h=3 (25.60 → 24.17; 33.08 → 31.69) and h=1 is slightly worse
(19.47 → 19.63). It improves 5 of 8 splits (by 1.5–10.4%; splits 0, 2 and 5 are worse by
0.7–6.7%) and 56.6% of cells. Gains: Khammouane (−280 CRPS-units), Salavan (−275), Bokeo
(−131), Champasak (−41), Attapeu (−22). Losses: Savannakhet (+211, the same se-inflation
mechanism as the ridge's), Vientiane Capital (+127: the level shrinkage was wrong in the
genuine late-2009 surge, when forecasts of 455–467 met actuals of 521–527) and Luang Prabang
(+93). Feature importances (`results/feature_importances.csv`, mean over splits): forecast
level 0.31, last residual 0.12, last-three residuals 0.09, trailing zero fraction 0.08,
trailing incidence 0.08, level × horizon 0.07, July 0.06, cross-province mean 0.06.

**The non-linear family finds more than the linear one** (−3.41% vs −1.64%), consistent with
interactions between the level effect and the month/horizon that a ridge cannot represent;
but the extra gain is concentrated in three provinces and three horizons-by-split cells,
and the family's hyperparameters were fixed rather than searched, so how much of the
difference is robust is a stability-phase question. This candidate is promoted to
`04_stage2`'s main path on the development evidence (agent-autonomous, reversible with
`/node promote`), with `f_oosErrorRidge` the runner-up the stability node runs as the
not-taken linear sibling.
