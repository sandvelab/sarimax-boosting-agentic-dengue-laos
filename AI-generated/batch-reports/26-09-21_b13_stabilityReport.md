Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 13)

# Batch 13 — the stability report

## 1. What this batch did

Phase D closes. The frozen development perturbation set was run in batch 12; this batch
reports the distribution of the central conclusion across it, as the plan asks: not the best
row, not a headline with a robustness footnote, but which choices the conclusion is
insensitive to and which it turns on. A script (`06_stability/scripts/05_report_distribution.py`)
reads the collected conclusions and every combination's per-cell file and writes
`distribution.json`, `perturbation_effects.csv`, `province_stability.csv` and
`horizon_stability.csv`; every figure below is read from those files. Seven claims (C1–C7)
enter the claim collection, each scoped to the development backtest.

## 2. The distribution

The central comparison is stage 1 alone against the two-stage ensemble, on the same cells,
inside each combination. The main path (`g_oosErrorBoosting`) scores −3.41% with coverage
82.7% → 85.7%.

| Across the 29 perturbations | Margin vs. stage 1 alone |
|---|---|
| Minimum (largest gain) | −10.64% (airline stage 1) |
| 10th percentile | −6.66% |
| Lower quartile | −4.19% |
| Median | −3.32% |
| Upper quartile | −2.41% |
| 90th percentile | −1.63% |
| Maximum (smallest gain) | −0.70% (true rolling refit of the in-window errors) |
| Two-stage beats stage 1 on CRPS | 29 of 29 |
| Coverage not worse than stage 1 | 29 of 29 |
| Sign flips | 0 |

**The sign is stable; the size is not.** Nine perturbations move the margin by more than two
percentage points from the main path's:

| Group | n | Range | Rows moving the size |
|---|---|---|---|
| Stage 1 specification | 3 | −10.6% to −3.4% | airline (0,1,1)(0,1,1,12): stage 1 alone 29.15, corrected 26.05; stationarity enforced: 26.81 → 24.55 |
| Training window, scheme, data | 4 | −7.2% to −0.9% | Chap's default scheme (7 splits, stride 1): 35.00 → 32.50, larger; 2002 window start: 27.37 → 27.12, smaller |
| Stage 2 target and combination rule | 7 | −5.8% to −1.6% | bounded correction (−5.8%), larger |
| Stage 2 features | 4 | −6.5% to −3.3% | level-only (−6.5%), no cross-province term (−5.8%), climate anomalies added (−5.8%): all larger |
| Stage 2 family hyperparameters and seed | 7 | −4.2% to −1.6% | none |
| How the training errors are made | 4 | −3.7% to −0.7% | true rolling refit (−0.7%), smaller |

Two readings follow. First, the stage-2 family's tuning does not matter: depth, tree count,
learning rate, leaf size, an alternative seed and the ridge penalty all stay within two points.
Second, what does matter is stage 1 and the construction of the training errors. A weaker
stage 1 leaves more to correct and the correction recovers most of it. The rolling refit is
the honest version of the main path's fixed-parameter shortcut for the in-window errors, and
under it the margin falls to −0.70% while still improving coverage (82.7% → 85.7%) and 4 of 8
splits; a reader who weights that row most should read the development margin as under one
percent. Split-level agreement across the set: 5 or more of 8 splits improved in 22 rows, 4 in
6 rows, 3 in one (the rolling 72-month window).

**The gain is concentrated, and the concentration is stable.** Over the 30 combinations run
(main and 29 perturbations), four provinces improve in every one — Khammouane (median summed
CRPS change −276), Salavan (−273), Bokeo (−131), Xiangkhouang (−26) — and five improve in at
most 20%: Savannakhet (median +207), Vientiane Capital (+127), Luang Prabang (+77), Xayaboury
(+9), Oudomxay (+6, never improved). The two largest losses persist under every perturbation
of the stage-2 configuration; only a different stage 1 or a rolling window turns them around
(Savannakhet's best is −134 under one such row). By horizon: two and three months ahead
improve in every combination, one month ahead in 47%.

**Rows that beat the main path.** Four stage-2 simplifications score better on development
data than the configuration that was frozen: level-only features, the bounded correction,
dropping the cross-province term, adding climate anomalies. None was promoted. The main path
was frozen before the run so that this report is a measurement; changing it now would make
the holdout evaluate a configuration chosen on the development test cells twice over. If a
change is wanted it belongs before the holdout manifest is frozen in batch 14, as a
pre-registered decision, and this batch does not make it.

**What the statement does not cover.** The five tier-3 alternatives were not run, above all a
negative-binomial or zero-truncated predictive family at stage 1: batch 10 showed the
coverage deficit is a heavy tail of reporting-regime cells that no rescaling of a Gaussian
repairs, and only a change of family could. The four configurations in which the ensemble
loses are the early siblings trained on the in-sample one-step residual (white); the pooled
random forest wins on CRPS with coverage collapsed to 64.4%.

## 3. Judgment calls logged, with agency

- **Two percentage points as the "moves the size" threshold**: `agent-autonomous`; a reporting
  device that separates tuning noise from choices that change the magnitude, recorded in the
  script and the output.
- **Not promoting a better-scoring perturbation**: `agent-autonomous`, per plan §3.
- **Seven claims now, the rest in phase F**: `agent-autonomous`.
- **Reading the rolling-refit row as the conservative margin**: an interpretation offered in
  the claim's scope, `agent-autonomous`; the human may weight it differently.

## 4. Checks run

`/validate invariants`: all checks pass except `git`, which fails only on the pre-existing
untracked `.idea/`; `claims` confirms every grounds path resolves. `claims.py audit` clean.

## 5. What batch 14 inherits

Phase D is closed with a sign-stable, size-unstable development finding and a concentrated
gain. Batch 14 freezes the holdout manifest — the development rows under holdout names — before
the 2010 file is opened, and this is the last moment at which the main path or the manifest
can change with a recorded reason. Two questions are the human's: whether to pre-register a
stage-2 simplification that scored better on development data (level-only features or the
bounded correction), and whether to build the predictive-family fork before or after the
holdout.
