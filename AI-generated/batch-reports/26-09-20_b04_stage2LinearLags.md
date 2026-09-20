Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 4)

# Batch 4 — stage-2 contract and first candidate

## 1. What this batch did

Built `analysis/04_stage2`, an **alternatives** node (its children are competing stage-2
model families, per AGENTS.md §2) with `a_linearLags` as the first, and so far only, child —
automatically the main path. `/validate invariants` passes except the expected mid-batch
`git` finding.

**The contract.** Stage 1's exact fit spec (SARIMAX(1,1,1)×(1,0,0,12), raw `disease_cases`)
is factored into `analysis/scripts/lib/stage1_model.py` so stage 2 can obtain stage 1's
*in-sample* residuals, which `02_stage1` never persisted — without touching that batch's
closed script or results (AGENTS.md §1: never edit a file you produced). Before trusting the
re-derivation, `a_linearLags`'s own script compares its independently re-fitted out-of-sample
forecast against `02_stage1`'s stored `per_cell_scores.csv`, cell for cell: **408/408 cells
verified, max|Δmean| = 0.0, max|Δse| = 0.0** — bit-identical, not merely close. The script
raises rather than proceeds if this check ever fails.

**a_linearLags.** A plain OLS on stage 1's lag-12 in-sample residual and cyclical calendar
month (sin/cos of month-of-year), added additively to stage 1's forecast mean; sigma left
unchanged from stage 1. Scored on the identical 371 cells stage 1 and the baselines score:
**mean CRPS 26.26 — 0.78% *worse* than stage 1 alone (26.05)**. Interval coverage at nominal
90%: 82.7% (stage 1 alone) vs. 83.3% (two-stage) — essentially unchanged, and both already
under the nominal level, a property of stage 1's raw-scale Gaussian CRPS on zero-heavy series
that this candidate neither introduces nor fixes. 40 of 408 cells (9.8%) had stage 2 abstain
(correction forced to 0) for lack of a usable lag-12 residual or too few valid training rows;
recorded per-cell, not absorbed into the score.

**This batch's honest answer, so far**: the first stage-2 candidate does not earn its place.
That is a result, not a failure (plan §2) — it does not settle whether *some* stage-2 family
would, which is what batches 5–7 continue to test.

## 2. Judgment calls logged, with agency

- **Lag-12 only, not lag-1, as stage 2's residual input**: lag-1 residual is available at
  forecast time for the first of each split's 3 test months but not the second or third — it
  would depend on an actual the forecaster has not yet observed at that point, a leakage risk
  once multi-step. Lag-12 always falls inside the training window regardless of which of the
  3 test months is being predicted, so it was used instead of a lag that only works for part
  of the horizon. `agent-autonomous`.
- **Sigma unchanged from stage 1**: stage 2 corrects the mean only; characterising the spread
  of its own correction's error would need a further nested split within an already-small
  per-province-per-split training window. Interval coverage is reported beside CRPS
  specifically so an overconfidence problem from this default would surface rather than be
  assumed away — it did not move meaningfully in this candidate's case. `agent-autonomous`.
- **Abstain rather than guess**: a province/split with fewer than 12 valid training rows (3×
  the 4 regression parameters), or a specific test month whose lag-12 residual is itself
  missing, gets a forced correction of 0, flagged per-cell as `stage2_abstained` rather than
  silently degrading or being dropped from the count. `agent-autonomous`.
- **Verification-by-reproduction rather than by import**: `02_stage1`'s script was not
  imported or modified; its exact model spec was independently re-implemented in a shared
  library and checked against its stored output. This costs an extra 136 SARIMAX refits but
  keeps `02_stage1` a closed record while still guaranteeing the two agree. `agent-autonomous`.
- **Nominal coverage level fixed at 90%**: a conventional default, not tuned to this data or
  explored as a fork — plan §2 asks for coverage to be reported beside CRPS, not for a
  specific level to be optimised. `agent-autonomous`.

## 3. A bug caught by running the script, fixed before committing

`compare_to_stage1.py`'s first run crashed on `TypeError: Object of type bool is not JSON
serializable` — a numpy boolean from a comparison expression, not a plain Python `bool`, sat
in the summary dict. Fixed with an explicit `bool(...)` cast and re-run before anything was
committed; the failed run produced no result file, so there was nothing to have quietly
absorbed. Not a silent patch: recorded here and in the "After" commit message.

## 4. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass except `git`
(clean after this batch's final commit). Every provenance sha256 was computed from the actual
file on disk and checked before committing, matching batch 3's discipline (not batch 2's
first attempt).

## 5. A stray observation, out of this batch's scope

`analysis/claim.md` (root)'s aim paragraph still names "the prior project's externally
reported reference" as something stage 2 is established against — flagged already by batch 3
as leftover phrasing from before plan §4b settled that this project cites no external
reference at all. Still not touched; still not this batch's job.

## 6. What batches 5–7 inherit

One stage-2 candidate exists (`a_linearLags`, main path by default) and it does not beat
stage 1 alone. The contract (`lib/stage1_model.py`, the verification-by-reproduction pattern,
the additive-mean/unchanged-sigma combination, per-cell abstention) is reusable machinery —
a further alternatives child needs only its own residual-prediction model, not a rebuilt
contract. Batches 5–7's job (ledger row 5–7): add at least one tree-based stage-2 candidate
and at least one non-tree/structural one (Bayesian or linear-with-structure), decide which
family — if any — sits on the main path on development evidence with the rejected families
kept runnable, and log what stage 2 is allowed to see (lags, covariates, population) as
forks rather than a single silent choice repeated across candidates.
