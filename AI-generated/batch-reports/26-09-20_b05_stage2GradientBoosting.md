Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 5)

# Batch 5 — tree-based stage-2 candidate

## 1. What this batch did

Re-pinned the project environment to add `scikit-learn` (Rule 3: declarative spec, resolved
lockfile, verified clean rebuild — see §2 below), then added `analysis/04_stage2/b_gradientBoosting`
as a second **alternatives** child alongside batch 4's `a_linearLags`, per AGENTS.md §2
(stage-2 model families compete under `04_stage2`, exactly one is the main path). `04_stage2/run.sh`
still calls only `a_linearLags` — `b_gradientBoosting` is a not-taken sibling, run by the
stability node like every other rejected alternative. `/validate invariants` passes except
the expected mid-batch `git` finding.

**The candidate.** A `sklearn.ensemble.GradientBoostingRegressor`, regularised for the very
small per-province-per-split training windows here (`n_estimators=50`, `max_depth=2`,
`learning_rate=0.05` — far short of scikit-learn's defaults, which have more capacity than
the ~12–40 available training rows can support without memorising them), trained on **the
identical minimal input `a_linearLags` uses**: stage 1's lag-12 in-sample residual and
cyclical calendar month (sin/cos of month-of-year). Same additive-to-the-mean combination,
sigma left unchanged from stage 1, same per-cell abstention contract, same
verification-by-reproduction against `02_stage1`'s stored forecast (408/408 cells,
bit-identical, `lib/stage1_model.py`, unchanged from batch 4) — all reused machinery, not
rebuilt.

**Result.** Scored on the identical 371 cells stage 1, the baselines, and `a_linearLags` all
score: **mean CRPS 27.68 — 6.25% worse than stage 1 alone (26.05), and worse than
`a_linearLags`'s 26.26 too.** Interval coverage at nominal 90%: 82.7% (stage 1 alone) vs.
82.2% (this candidate) — essentially unchanged, not overconfident, not better calibrated
either. 40 of 408 cells (9.8%) abstained under the same `MIN_TRAIN_ROWS = 12` threshold as
`a_linearLags` — the same cells, since the threshold and the underlying data are identical.

**This batch's honest answer**: a second stage-2 candidate does not earn its place, and more
model capacity made the correction *worse*, not better, given the same minimal input. That is
consistent with a genuinely weak or noisy residual signal at this input specification, not
(yet) evidence that no stage-2 family could help — batch 6 still owes a non-tree, non-linear
candidate, and batch 7 the input-set exploration this batch deliberately deferred.

## 2. Environment re-pin: scikit-learn

`environment/environment.yml` and `install-env.sh` gained `scikit-learn`;
`RESOLVE=1 bash environment/install-env.sh` re-resolved and wrote a new `lock.txt` (18
packages, `scikit-learn==1.9.1`); a second, plain `bash environment/install-env.sh` rebuilt
`env/` from that lockfile from scratch and confirmed it matches exactly — the same two-pass
verification batch 2 first established. `environment/README.md`'s dependency table and
verification log updated. Two commits (`Before`/`After: batch 5, environment`), separate from
the node's own before/after commits, since this is project-main-environment machinery, not a
node result.

## 3. Judgment calls logged, with agency

- **Inputs kept identical to `a_linearLags`, not extended (e.g. with lag-1)**: a deliberate
  choice to isolate the model-family comparison (linear vs. tree) from the input-set question.
  Changing both at once would leave it unclear which change caused any difference in score —
  the input-set exploration is its own named fork later in the ledger (batch 7). `agent-autonomous`.
- **Regularised gradient-boosting hyperparameters, not a search**: `max_depth=2`,
  `n_estimators=50`, `learning_rate=0.05` — a first, defensible default sized to the training
  data available, in the same spirit as stage 1's fixed SARIMAX order. `agent-autonomous`.
- **Sigma unchanged from stage 1, for direct comparability with `a_linearLags`**: same
  reasoning as batch 4 (a nested split to characterise the correction's own error would need
  more data than these windows have), and the same interval-coverage safeguard is in place to
  catch overconfidence if this default ever produces it. `agent-autonomous`.
- **Determinism verified, not assumed**: the fit configuration (`subsample=1.0`,
  `max_features=None`) draws no real randomness, but this is checked rather than taken on
  faith — the script fits the same data twice with two different `random_state` values on the
  first eligible province/split and confirms bit-identical predictions, raising if they ever
  disagreed. A seeded `random_state` (`lib/project_seed.py`, component `"04_stage2/b_gradientBoosting"`)
  is still recorded, for defensiveness against a future configuration change that would
  introduce real randomness. `agent-autonomous`.
- **Same `MIN_TRAIN_ROWS = 12` abstention threshold as `a_linearLags`**: kept for
  comparability rather than re-tuned per family. `agent-autonomous`.

## 4. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass except `git`
(clean after this batch's final commits). Every provenance sha256 computed from the actual
file on disk and checked before committing, including the re-pinned `lock.txt`.

## 5. Also fixed this batch: a stale line in the root claim

`analysis/claim.md`'s top aim paragraph still named "the prior project's externally reported
reference" as something stage 2 is established against, three batches after plan §4b settled
that this project cites no external reference at all (flagged by batch 3, left untouched by
batch 4). Fixed visibly here, not silently: the paragraph now states the internal-only
comparison directly, with a pointer to §4b.

## 6. What batches 6–7 inherit

Two stage-2 candidates exist, both negative, both on the same minimal input:
`a_linearLags` (26.26, still the default main path as the less-bad of the two) and
`b_gradientBoosting` (27.68). The environment now has `scikit-learn` pinned, so a further
tree-based or ensemble variant costs nothing further to pin. Batch 6's job (ledger row 6):
add a non-tree, non-linear candidate (Bayesian or linear-with-structure). Batch 7's job
(ledger row 7): decide which family — if any — sits on the main path on development evidence,
with the rejected families kept runnable, and log what stage 2 is allowed to see (lags,
covariates, population) as forks rather than the single minimal input all candidates have
used so far.
