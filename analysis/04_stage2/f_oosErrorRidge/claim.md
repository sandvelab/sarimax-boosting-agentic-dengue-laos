# Claim

Does a stage 2 that predicts stage 1's h-step out-of-sample forecast error -- rather than its in-sample one-step residual -- from forecast-time features (horizon, target month, stage 1's own forecast level, recent residuals, their cross-province mean, trailing incidence and reporting level), pooled across provinces on the standardised-error scale with a ridge regression, earn its place against stage 1 alone?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Yes, on the development backtest — the first candidate to clear both of plan §2's bars,
by a modest and unevenly distributed margin.** Mean CRPS **25.63** against stage 1 alone's
26.05 (**−1.64%**) over the same 371 cells, with 90% interval coverage **improved** from 82.7%
to 84.6% (`results/conclusion.json`, `results/comparison.json`).

The combination rule decomposed (`comparison.json`, `combination_rule_decomposition`): stage
1 26.05 → clipped at zero 25.91 (−0.56%) → corrected, unclipped 25.68 (−1.43%) → corrected
and clipped 25.63. The correction alone, measured against the clipped stage 1, is −1.09%. The
gain grows with horizon (h=1: 19.47 → 19.34; h=2: 25.60 → 25.25; h=3: 33.08 → 32.29), as a
correction of multi-step error should. It is not uniform: the candidate improves 4 of 8
splits (the four latest, 2008Q4–2009Q4, by 1.7–15.6%; the four earliest are worse by
1.7–9.0%) and 56.6% of cells. By province the gains sit in Salavan (−149 CRPS-units summed),
Khammouane (−140), Bokeo (−107) and Champasak (−61); the losses in Savannakhet (+232) and
Vientiane Capital (+79). The Savannakhet loss is mechanical and understood: its stage-1 se
(200–414) is tens of times its 2008–09 case level, so a standardised correction of +0.4–0.6
becomes 130–190 cases; a correction bounded relative to the forecast level is the refinement
this points to, logged in the provenance as untried.

What the ridge learned is stable across all eight splits (`results/ridge_coefficients.csv`,
standardised features): the forecast level relative to the province's residual scale has the
largest coefficient (−0.19 to −0.22: a high forecast is shrunk), then the calendar (June–
September positive, peaking in July at +0.09 to +0.12; November–April negative), the horizon
(h=3 positive), the last residual (+0.06 to +0.07), the trailing zero fraction (−0.09 to
−0.14) and a small positive trailing-incidence term. Mean |zhat| is 0.27 standard errors.

Whether the margin survives reasonable alternative choices — stage 1's specification, the
ridge penalty, the winsorisation bound, the feature set, clipping — is the stability
phase's question, and this development score was reached after diagnostics that looked at
the same test cells (plan §4b), so it is a development number, not an independent one.
