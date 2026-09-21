Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 15)

# Batch 15 — the stability set re-run around the annotated main path (v2)

## 1. What this batch did

Batch 14 annotated `h_levelOnlyBoosting` as `04_stage2`'s main path and re-planned the
development perturbation manifest around it: 26 tier-2 rows suffixed `@h`, the nine not-taken
siblings as tier 1, five tier-3 alternatives not run, and v1's 29 rows kept as superseded.
This batch ran that manifest with the verified runner, reported its distribution beside v1's,
and put six claims into the collection. Every figure below is read from files under
`06_stability/results/`: `run_summary_v2.json`, `conclusions_v2.csv`, `distribution_v2.json`,
`perturbation_effects_v2.csv`, `province_stability_v2.csv`, `horizon_stability_v2.csv` and
`version_comparison_v2.csv`.

**The run.** The runner refused to start until `manifest.csv` hashed to the frozen v2 digest
and the tree's main path matched the one the manifest was frozen for. Its gate row `main@h`
then reproduced `h_levelOnlyBoosting`'s stored per-cell scores on all 408 rows with 0
mismatched values, and only after that did the 26 perturbations run: 1,537 s of the 3,600 s
ceiling, the true rolling refit alone 774 s. The budget line fell below every row. v1's run
log, conclusions and report are untouched; v2 writes `_v2` files beside them, so the batch-13
report and claims C2–C7 keep their grounds.

**Two checks that came free.** Two rows change nothing binding (a higher minimum-training-row
threshold, a higher modelability threshold) and reproduce `main@h`'s 24.3508 exactly. Four rows
are, by construction, the same configuration as a v1 row — the main path itself is v1's
level-only row, and the three "add features back" rows land on v1's three "drop features"
rows — and each reproduces the v1 two-stage mean CRPS to the last digit. The rolling-refit row
carries the same caveat as in v1: three origins per split whose refit returned non-finite
predictions contributed no training row.

## 2. The distribution

The central comparison is stage 1 alone against the two-stage ensemble, on the same cells,
inside each combination. The main path (`h_levelOnlyBoosting`) scores −6.53% with coverage
82.7% → 85.2%.

| Across the 26 perturbations | Margin vs. stage 1 alone |
|---|---|
| Minimum (largest gain) | −10.41% (airline stage 1) |
| 10th percentile | −7.28% |
| Lower quartile | −6.53% |
| Median | −5.91% |
| Upper quartile | −4.90% |
| 90th percentile | −3.16% |
| Maximum (smallest gain) | −1.06% (no-differencing stage 1; the 2002 window start is −1.06% too) |
| Two-stage beats stage 1 on CRPS | 26 of 26 |
| Coverage not worse than stage 1 | 26 of 26 |
| Sign flips | 0 |
| Splits improved | 6 of 8 in 21 rows, 4 of 8 in 5 rows |

**The sign is stable; the size is not.** Eight perturbations move the margin by more than two
percentage points from the main path's:

| Group | n | Range | Rows moving the size |
|---|---|---|---|
| Stage 1 specification | 3 | −10.4% to −1.1% | airline (0,1,1)(0,1,1,12): stage 1 alone 29.15, corrected 26.11, larger; stationarity enforced: 26.80 → 24.08, larger; **no differencing (1,0,1)(1,0,0,12): 24.93 → 24.67, smaller** |
| Training window, scheme, data | 4 | −7.6% to −1.1% | rolling 72-month window: 23.99 → 23.17 (−3.4%), smaller; 2002 window start: 27.37 → 27.08 (−1.1%), smaller |
| Stage 2 target and combination rule | 7 | −6.9% to −3.5% | one model per horizon (−3.5%), smaller |
| Stage 2 features | 3 | −5.8% to −3.3% | recent-residual and cross-province features added back (−3.3%), smaller |
| Stage 2 family hyperparameters and seed | 5 | −6.5% to −4.8% | none |
| How the training errors are made | 4 | −6.5% to −3.0% | true rolling refit (−3.0%), smaller |

Three readings follow. First, as in v1, the stage-2 family's tuning does not matter: depth,
tree count, learning rate, leaf size and an alternative seed stay within two points, and so do
the winsorisation bound, the bound without its floor, clipping, the standardisation and the
warm-up. Second, what does matter is stage 1 and the construction of the training errors. A
weaker stage 1 leaves more to correct and the correction recovers most of it; the rolling
refit, the honest version of the fixed-parameter shortcut, gives −2.99% while still improving
coverage and 4 of 8 splits. Third, and new in this round, **a better stage 1 leaves little to
correct**: the no-differencing SARIMAX alone scores 24.93, better than the main path's stage 1
(26.05) and within 0.6 CRPS of the two-stage main path (24.35). Under it the correction is
worth −1.06%. Part of the second stage's development margin is therefore a repair of stage 1's
differencing choice. Stage 1 stays as specified by the human's decision after phase D, and
this is recorded against its documented weaknesses rather than acted on.

**The gain is concentrated, and reaches one month ahead now.** Over the 27 combinations run,
five provinces improve in every one — Khammouane (median summed CRPS change −337), Salavan
(−284), Bokeo (−145), Xiangkhouang (−27), Xekong (−2) — and Champasak in 25. Oudomxay never
improves (+6); Phongsaly, Luang Prabang (+57) and Vientiane Capital (+195) improve in at most
10%; Savannakhet (+22) in 4 of 27, under the airline stage 1 (−248), the rolling window, the
bound without floor and the tighter winsorisation. The Vientiane Capital and Luang Prabang
losses turn around only under the airline stage 1 or, for Vientiane Capital, the full feature
set with climate anomalies. By horizon: three months ahead improves in every combination, two
in 26, one month ahead in 23 of 27 — against 47% around `g`. The four that lose at one month
are the per-horizon fit, the rolling window, the added-back recent and cross-province
features, and the no-differencing stage 1.

## 3. Beside v1

| | v1 (around `g_oosErrorBoosting`) | v2 (around `h_levelOnlyBoosting`) |
|---|---|---|
| Main path margin | −3.41% | −6.53% |
| Perturbations run | 29 | 26 |
| Sign flips | 0 | 0 |
| Range | −10.64% to −0.70% | −10.41% to −1.06% |
| Median | −3.32% | −5.91% |
| Rows moving the size | 9 | 8 |
| Conservative reading (rolling refit) | −0.70% | −2.99% |
| One month ahead improved | 47% | 85% |

Twenty-two perturbations are shared by name. Twenty of them have a larger margin around `h`
than around `g` (median shift −2.3 points, the largest −5.0 for no winsorisation); the two
exceptions are stage-1 changes, the airline specification (−10.64% → −10.41%) and no
differencing (−3.36% → −1.06%). Which rows move the size also shifts: Chap's default scheme
did in v1 and does not in v2; the per-horizon fit, the rolling window and the no-differencing
stage 1 do in v2 and did not in v1. In words: around the minimal-input stage 2 the margin is
larger and more uniform across the stage-2 choices, and more exposed to stage 1's
specification.

**Rows that beat the main path.** Winsorisation at 5 (−6.92%), the bound without its floor
(−6.78%) and no winsorisation (−6.57%) score better on development data than `h`. All three
lie within the alternative seed's own distance from the main path (−6.19%), and none is
promoted: the main path is the pre-registered configuration the holdout will evaluate, and
this report is a measurement of it.

**What the statement does not cover.** The five tier-3 alternatives are unchanged and
uncovered, above all a count or heavier-tailed predictive family at stage 1. The four
configurations in which the ensemble loses remain the early siblings trained on the in-sample
one-step residual; the pooled random forest still wins on CRPS with coverage collapsed to 64.4%.

## 4. Judgment calls logged, with agency

- **Versioned outputs beside v1's rather than overwriting**: `agent-autonomous`. v1's files are
  the record the batch-13 report and claims C2–C7 cite.
- **Keeping the four configuration-identical rows in the run**: `agent-autonomous`. They are
  what the manifest planned around `h`, and their exact reproduction of v1 is recorded as a
  determinism check rather than discarded as redundancy.
- **Two percentage points as the "moves the size" threshold, unchanged**: `agent-autonomous`;
  the same threshold keeps the two versions comparable, and it is a column in the output.
- **Not promoting a better-scoring perturbation**: `agent-autonomous`, per plan §3.
- **Recording the no-differencing result against stage 1's weaknesses instead of reopening
  stage 1**: the decision not to repair stage 1 is `human-set` (plan §4b, 2026-09-21); the
  recording is `agent-autonomous`, and the finding is flagged for the human.
- **Six claims now (C8–C13), the rest in phase F**: `agent-autonomous`.

## 5. Checks run

`/validate invariants`: all checks pass except `git`, which fails only on the pre-existing
untracked `.idea/`. `claims.py audit`: every pointer resolves. The runner's gate: 408 of 408
rows, 0 mismatches. Reproduction checks against v1: 4 of 4 identical.

## 6. What batch 16 inherits

A main path whose development margin is sign-stable across 26 alternatives and whose size
turns on stage 1 and on the training-error construction, with v1 and v2 side by side in
`version_comparison_v2.csv`. Batch 16 freezes the holdout manifest from v2 before the 2010 file
is opened; that is the last moment at which the main path or the set can change with a
recorded reason. Two things are the human's: whether the no-differencing finding changes the
decision not to repair stage 1 (it is the one stage-1 row whose stage 1 alone comes close to
the two-stage main path), and whether any of the three better-scoring stage-2 rows should be
pre-registered instead of `h`. The line-ending item (row 19) stands.
