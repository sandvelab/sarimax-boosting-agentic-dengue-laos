# Claim

Both changes at once -- the minimal input of h_levelOnlyBoosting and the bounded correction of i_boundedBoosting -- on the same target, pooling and family: is the combination better than either alone, and does it earn its place?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Better than either alone on mean CRPS, by a little; the two gains overlap rather than add.**
Mean CRPS **24.29** against stage 1 alone's 26.05 (**−6.78%**), against `h_levelOnlyBoosting`'s
24.35 (−0.26%) and `i_boundedBoosting`'s 24.53; coverage 85.2% (as h), 6 of 8 splits improved
(as h), 55.8% of cells (`results/conclusion.json`, `results/comparison.json`). Stage 1 verified
cell for cell against `02_stage1` (408/408).

The bound adds −0.26% on top of the minimal input, against −2.52% on top of the full input
(`i` vs `g`): once the recent-residual and reporting-level features are gone, the large
Savannakhet corrections the bound existed to limit are mostly gone too (Savannakhet −17 here,
+8 under h, +25 under i, +211 under g). Vientiane Capital's loss (+198) is untouched by
either change. By horizon 18.89 / 23.98 / 29.99.

**Not the main path, by the pre-registered rule** (plan §4b): `j` and `h` are within 0.1 CRPS
of each other (24.29 vs 24.35) and improve the same number of splits (6 of 8), and the rule
then prefers the configuration with fewer changes from `g`, which is `h`. This candidate is
the best-scoring configuration on development data and is recorded as such; it is run as a
not-taken alternative by the stability node and will be evaluated on the holdout as a row of
the frozen manifest, not as the main path.
`results/all_candidates_comparison.json` holds all ten candidates side by side, the rule and
its application.
