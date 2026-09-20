Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 6)

# Batch 6 — Bayesian stage-2 candidate

## 1. What this batch did

Added `analysis/04_stage2/c_bayesianRidge` as a third **alternatives** child alongside batch
4's `a_linearLags` and batch 5's `b_gradientBoosting`. `04_stage2/run.sh` still calls only
`a_linearLags` — `c_bayesianRidge` is a not-taken sibling, run by the stability node like
every other rejected alternative. `/validate invariants` passes except the expected mid-batch
`git` finding.

**The candidate.** `sklearn.linear_model.BayesianRidge` — a closed-form Bayesian linear
regression (Gaussian prior on coefficients, precision hyperparameters set by evidence
maximisation, no MCMC) — trained on **the identical minimal input** the other two candidates
use: stage 1's lag-12 in-sample residual and cyclical calendar month. No new dependency:
`scikit-learn` was already pinned by batch 5. Same additive-to-the-mean combination, same
per-cell abstention contract (`MIN_TRAIN_ROWS = 12`), same verification-by-reproduction against
`02_stage1`'s stored forecast (408/408 cells, bit-identical, `lib/stage1_model.py`, unchanged
since batch 4).

**Two things this candidate does differently from its siblings**, both logged judgment calls
(§3): features are standardised before fitting (BayesianRidge's shared-precision prior needs
comparable feature scales, which the raw lag-12 residual and the bounded sin/cos features are
not), and — unlike `a_linearLags`/`b_gradientBoosting`, which left stage 1's sigma unchanged
for lack of a principled alternative — this candidate's own posterior predictive variance is
combined with stage 1's forecast variance into the final interval
(`final_se = sqrt(stage1_se² + stage2_se²)`, independence assumed). This is a genuine
calibration attempt, the first among the three candidates.

**Result.** Scored on the identical 371 cells every prior candidate scores: **mean CRPS
28.07 — 7.73% worse than stage 1 alone (26.05), worse than both `a_linearLags` (26.26,
-0.78%) and `b_gradientBoosting` (27.68, -6.25%).** Interval coverage at nominal 90%: 86.8% —
the best-calibrated of the three (stage 1 alone 82.7%, `a_linearLags` 83.3%,
`b_gradientBoosting` 82.2%). The two results are connected, not contradictory: combining a
real second-stage variance with stage 1's widens the interval, which buys calibration but
costs CRPS, and here the cost dominates. 40 of 408 cells (9.8%) abstained — the same threshold
and the same cells as both siblings, since the threshold and underlying data are identical.
`analysis/04_stage2/c_bayesianRidge/results/all_candidates_comparison.json` holds all three
candidates side by side, produced here specifically so batch 7's main-path decision has one
file to read rather than three to hand-collate.

**This batch's honest answer**: three stage-2 candidates — a plain point-estimator, a
tree-based point-estimator, and a genuinely calibrated Bayesian model — all lose to stage 1
alone on the identical minimal input, and the ranking from best to worst tracks a
CRPS/calibration trade-off rather than any one family being obviously "more correct." This is
consistent with the minimal input (one lag, one seasonal signal) simply not carrying enough
residual structure for any of these families to exploit profitably — not yet evidence that no
richer input could help, which is explicitly batch 7's question.

## 2. Judgment calls logged, with agency

- **BayesianRidge over a hierarchical/partial-pooling model (e.g. PyMC)**: answers the plan's
  calibration question via a real posterior without a heavy MCMC dependency, appropriate for
  per-province-per-split fits on as few as ~24 rows where MCMC asymptotics are the wrong tool
  anyway; no new environment pin needed. `agent-autonomous`.
- **Inputs kept identical to both siblings, not extended**: isolates the third model-family
  comparison from the input-set question, deferred to batch 7 by design (same reasoning batch
  5 recorded). `agent-autonomous`.
- **Feature standardisation before fitting** (training-window mean/std only, un-standardised
  after): necessary because `BayesianRidge` places one shared-precision prior across all
  coefficients, which implicitly assumes comparable feature scales — the raw lag-12 residual
  and the bounded sin/cos features are not comparable without this. Not a hyperparameter
  search; a precondition for the model to regularise sensibly. `agent-autonomous`.
- **Calibration via combined variance, not left unchanged**: `final_se = sqrt(stage1_se² +
  stage2_se²)`, independence assumed between stage 1's forecast uncertainty and stage 2's
  posterior predictive uncertainty — the first candidate with its own predictive variance to
  use, so the first candidate where this was possible rather than deferred. `agent-autonomous`.
- **Determinism verified, not assumed**: `BayesianRidge` has no `random_state` and no random
  initialisation, but this is checked (two independent fits on identical data, confirmed
  bit-identical mean and std) rather than taken on faith, same discipline as both siblings.
  `agent-autonomous`.
- **Same `MIN_TRAIN_ROWS = 12` abstention threshold as both siblings**: kept for comparability
  rather than re-tuned per family. `agent-autonomous`.

## 3. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass except `git`
(clean after this batch's final commits, aside from the pre-existing, out-of-scope untracked
`.idea/`). Every provenance sha256 computed from the actual file on disk and checked before
committing.

## 4. What batch 7 inherits

Three stage-2 candidates exist, all negative, all on the same minimal input: `a_linearLags`
(26.26, still the default main path as the least-bad of the three), `b_gradientBoosting`
(27.68), `c_bayesianRidge` (28.07, best-calibrated). The plan's central question — does *some*
stage-2 family earn its place — is not yet answered on a richer input. Batch 7's job (ledger
row 7): decide which family, if any, sits on the main path on development evidence, with the
rejected families kept runnable, and log what stage 2 is allowed to see (more lags, covariates,
population) as forks rather than the single minimal input all three candidates have used.
