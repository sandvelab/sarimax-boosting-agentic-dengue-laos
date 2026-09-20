# Claim

What structure is there in stage 1's out-of-sample forecast errors on the development backtest — by horizon, calendar month, province scale, spread calibration and cross-province synchrony — and how much of it is predictable from information available at forecast time, i.e. can a stage 2 do better than chance at all?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Batch 10.** All figures from `results/error_structure.json`, `results/test_cells.csv`,
`results/insample_residual_acf.csv` and `results/predictability.{csv,json}`, on `02_stage1`'s
371 scored development test cells.

1. **The in-sample one-step residual every earlier candidate trained on is essentially
   white.** On the final split's training window its mean autocorrelation across provinces
   is within ±0.06 at every lag 1–12 (lag 12: 0.004), with at most 3 of 17 provinces beyond
   two standard errors at any lag. A stage 2 trained on it had nothing to learn — which is
   what candidates a–e found.

2. **The out-of-sample h-step error a stage 2 must correct is not white, but its structure
   is skewed and concentrated.** Median error is near zero at every horizon while the mean
   is positive (+2.6 at h=2, +7.3 at h=3): stage 1 over-predicts in two thirds of cells
   (share of positive errors 0.33/0.32/0.38 by horizon) and under-predicts by a large amount
   in a few. By calendar month the sign is systematic: 55% of June and July errors are
   positive (June median +1.8, mean +30.9 on a mean actual of 48.7), against 13–23% positive
   in January–April and 29–32% in November–December. Five provinces carry three quarters of
   the CRPS (SV 19%, VT 16%, SL 13%, KH 11%, BK 10%), and three of them are reporting-regime
   breaks in the test years: Savannakhet averaged 166 cases/month in the 2000–2007 training
   window and 8 in 2008–09; Bokeo went from 0.7 to 39, Salavan from 4.0 to 61 (the raw data:
   Bokeo 1 case in 2007, 218 in 2008, 709 in 2009). Those cells give standardised errors
   |z| up to 164 and are the whole coverage deficit.

3. **The coverage deficit cannot be fixed by scaling sigma.** 90% coverage is 87.1/82.1/79.0%
   by horizon. The multiplier that would put the 90th percentile of |z| at nominal is
   1.22/1.91/2.44 — but applying even that oracle factor (fixed on the scored cells) raises
   mean CRPS from 26.05 to 35.65 while reaching 89.5% coverage, because the median |z| is only
   0.27–0.34: most cells are already over-covered and pay for the tail. Worse, the in-window
   errors a leakage-safe stage 2 could estimate a factor from are *over*-covered (93–94%;
   factor 0.62–0.75, also over the last 24 origins), so an honest spread correction would
   shrink the intervals. The heavy tail is a predictive-family problem (Gaussian on counts),
   not a spread-scale problem, and belongs to stage 1's specification. Clipping stage 1's
   mean at zero (4.0% of cells are negative) needs nothing estimated and lowers mean CRPS to
   25.91.

4. **What co-varies with the error, at forecast time.** Strongest: stage 1's own forecast
   level relative to the province's residual scale (Spearman −0.27 with z, Pearson −0.40 with
   winsorised z; and Spearman +0.65 between |z| and level — the se does not grow with the
   level as a count's variance does). Then the calendar (cos of month −0.21), the last
   residual at the origin (+0.20 Spearman, near zero Pearson: a rank signal), horizon, the
   trailing-12-month incidence anomaly (−0.12) and the cross-province mean (−0.09). Climate
   anomalies at lags 1–3, contemporaneous or 3-month means, are all |ρ| ≤ 0.05 for
   temperature and humidity and −0.04 for rainfall. Cross-province synchrony of the
   standardised error is modest: mean pairwise correlation 0.10, 14.5% of variance explained
   by the test-month mean, first component 27%.

5. **Predictability better than chance, cross-validated on the test cells** (leave-one-split-
   out, target z winsorised at ±3, chance = 95th percentile of the same model on a permuted
   target, 30 permutations): of 56 feature-set × family configurations, 10 beat chance on
   skill and only **2 lower mean CRPS** — both the forecast-level features with a ridge
   (−0.84% and −0.80%, coverage 84.4%). The earlier candidates' input (lag-12 residual and
   calendar) never beats chance in any family (skill −0.19 to −0.08). Rich feature sets fit
   with trees or weakly regularised ridge lose badly in CRPS even with positive skill on z,
   because a z-scale gain in many small cells is paid for in a few large-se cells. This is an
   exploratory estimate on ~325 training cells per fold from other years' test errors; the
   candidates built from it (`04_stage2/f_oosErrorRidge`, `g_oosErrorBoosting`) train inside
   each split's own window on ~5,000 rows and do better than this test suggests.

**Answer to the claim**: there is predictable structure in stage 1's out-of-sample errors —
a level-dependent over-prediction, a calendar bias in the multi-step forecast, a horizon
effect, and a weak recent-residual signal — but it is modest, and the dominant errors
(reporting-regime breaks in 2008–09) are not predictable from the province's own history.
Climate at short lags carries no usable signal here, and the interval-coverage deficit is
not a spread-scale problem that a stage 2 can fix without losing CRPS.
