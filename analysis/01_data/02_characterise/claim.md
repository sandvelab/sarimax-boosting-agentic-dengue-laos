# Claim

What is in the development period: how complete is it per province and per year, how are dengue counts distributed, what seasonality do they show, and how do the climate covariates behave? Which of its features are analytic problems that phase D must perturb rather than preprocessing details?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The development period is a small, zero-heavy, strongly seasonal panel.** 2 592 rows over
18 provinces and 144 months, 77 031 reported cases in total. 8.1% of target cells are
missing and 56.3% of the observed ones are zero. Cases peak in July–September at roughly
fourteen times the February trough.
→ `results/dev_overview.json`, `results/seasonality_by_month.csv`, `results/fig_cases_seasonality.png`

**The headline metric is a mean over 16 provinces, not 18.** Vientiane (LA-VI) reports
nothing in the whole development period and is dropped by chap-core's own region filter.
Xaisomboun (LA-XN) reports through 2005-12 and then stops, so it survives the filter — which
looks only at the training period — and still contributes no evaluable cell. Under the fixed
scheme the metric averages 371 cells, not the nominal 408.
→ `results/evaluable_cells_by_province.csv`, `results/backtest_scheme_chosen.json`, `results/fig_completeness.png`

**The burden spans four orders of magnitude across provinces**, and six provinces report
zero in more than 85% of their observed months. An unweighted mean CRPS gives each of them
the same weight as the capital, so the headline number can be moved by provinces where the
answer is almost always zero. This is a property of the plan's chosen metric, established
before any model exists.
→ `results/cases_by_province.csv`, `results/fig_province_burden.png`

**Climate leads dengue, consistently in sign and loosely in size.** Rainfall associates most
strongly at a lag of one month, temperature at two to three, humidity at nought to one; each
is positive in 16 or 17 of the 17 provinces, with a min–max band across provinces roughly
0.0 to 0.7. The negative values at lags five and six are the far side of the annual cycle.
→ `results/lag_correlation.csv`, `results/fig_covariate_lag_correlation.png`

**The backtest scheme is fixed and does not move again.** Development: `n_periods 3`,
`n_splits 8`, `stride 3`, `n_retrain 1`, evaluating 2008-01 to 2009-12 from a training set
ending 2007-12. Phase E: `n_periods 3`, `n_splits 4`, `stride 3` on the full file, evaluating
exactly 2010.
→ `results/backtest_scheme_chosen.json`, `results/backtest_scheme_candidates.csv`, `results/split_schedule.csv`

**Two of the schema's statements do not describe the file.** `population` is a single 2020
snapshot repeated across all thirteen years — confirmed, one distinct value per province.
`rainfall`, declared as a monthly total in millimetres, is a mean daily rate: read as
declared it puts a province's year at 50–78 mm, read as mm/day at 1 518–2 383 mm.
→ `results/population_static_check.csv`, `results/covariate_units_check.json`
