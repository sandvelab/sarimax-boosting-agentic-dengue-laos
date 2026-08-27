# Claim

…a hierarchical negative-binomial GLM: monthly province counts as negative-binomial draws around a log-linear mean built from a population offset, a shared annual seasonality and lagged climate covariates, with province and province-year effects pooled toward a common level. The node's six children are the choices that shape it; the node itself assembles those choices into one model configuration and sends the model through the same chap eval path as every other model in the project.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**Mean CRPS 26.100 over 371 cells in 16 provinces, at 43 seconds for the eight-split
backtest** (`results/main/run_cost.json`) — the worst of the four models scored so far, and
worse than both required baselines.

**The same model has the best point forecast in the project.** Mean absolute error **27.106**
against the reference's 28.902, climatology's 30.620 and persistence's 29.073, and the best
interval coverage of any model of ours: **0.720** at 10–90 and **0.590** at 25–75, against
nominal 0.80 and 0.50. The centre of the forecast is right and its width is wrong, which is a
different repair from the one a model with a bad centre needs.

**The width is wrong locally, not on average.** Two provinces carry 2.4 of the 4.0 CRPS gap
to the reference (`04_score/02_aggregate/a_unweighted/results/main/crps_by_location.csv`): in
Vientiane Capital the 10–90 interval covers **every** outcome, and in Salavan it covers
**0.125**. The province-year variance is a single number shared by all provinces, so on the
log scale it is a constant multiplicative width — too much where the burden is largest and
too little where the epidemic years are sharpest.

The fit itself: between-province spread sigma **2.06** on the log-incidence scale,
between-year spread within a province sigma **1.47**, negative-binomial dispersion **0.83**,
converged in 24 EM rounds on 1 978 usable rows over 17 provinces and 168 province-years
(`results/main/fitted_model.json`).
