Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 8)

# Batch 8 — climate-covariate stage-2 candidate

## 1. What this batch did

Batch 7 closed phase C with an open question left explicitly for the human: move to phase D
(stability) with `a_linearLags` frozen as the stage-2 default, or spend a further batch trying
richer stage-2 inputs — climate covariates above all — since a stage-2 family with climate
might change the central finding rather than just its stability. The human chose to explore
richer inputs first.

**Built `analysis/04_stage2/d_linearClimate`**, a fourth stage-2 alternative: `a_linearLags`'s
exact OLS family (lag-12 in-sample residual, cyclical calendar month) with three columns added
— `rainfall`, `mean_temperature`, `mean_relative_humidity` — all already present in
`development.csv` (no new data acquisition). The climate columns are taken at **lag 12**, not
contemporaneously, for the same leakage reason `a_linearLags` fixed the residual lag: a real
1–3-month-ahead deployment does not know next quarter's rainfall, but the value from 12 months
before any test month in this backtest scheme is always inside the training window. This keeps
the same family as the main path deliberately, so the result is attributable to the input, not
to also changing the model — the model-family axis was already explored by
`b_gradientBoosting` and `c_bayesianRidge` on the minimal input.

**Result: worse, not better.** Mean CRPS **26.85** over the same 371 cells — worse than stage 1
alone (26.05, +3.05%) and worse than `a_linearLags` on the minimal input (26.26, +2.25%).
Coverage is essentially unchanged (83.0% vs. `a_linearLags`'s 83.3%, both against nominal 90%).
`a_linearLags` remains `04_stage2`'s main path. The updated development-data ranking, best to
worst:

| Model | Mean CRPS | vs. stage 1 alone |
|---|---|---|
| Stage 1 alone (`02_stage1`) | 26.05 | — |
| `a_linearLags` | 26.26 | +0.78% |
| `d_linearClimate` | 26.85 | +3.05% |
| Seasonal climatology (`03_baselines/02_climatology`) | 26.91 | +3.20% |
| `b_gradientBoosting` | 27.68 | +6.25% |
| `c_bayesianRidge` | 28.07 | +7.73% |
| Persistence (`03_baselines/01_persistence`) | 28.32 | +8.72% |

No stage-2 family or input tried so far beats stage 1 alone. `04_stage2/claim.md` and the root
`analysis/claim.md` are updated with this candidate's result and its bearing on the still-open
climate question (see §5).

**Plan updated to reflect the human's choice**, before any modelling (`/do` step 5, backed up
to `/tmp/claude_backups/` first): inserted as ledger row 8, with the reason and its agency
recorded in the plan's own §4b; the stability phase (formerly rows 8–10) and everything after
it renumbered to rows 9–16.

## 2. Judgment calls logged, with agency

- **Lag-12 climate, not contemporaneous**: the leakage-safety argument is identical to
  `a_linearLags`'s own lag-12 residual choice, applied to a new input. Recorded in the node's
  own provenance record and `claim.md` as a deliberate, conservative choice — it forgoes the
  current season's anomaly, which a genuine short-range climate forecast (not present in this
  dataset) would capture. `agent-autonomous`.
- **Same family (OLS) as `a_linearLags`, not a new one**: deliberate, to isolate the
  input-richness axis from the model-family axis already covered by batches 5–6. Trying a new
  family and a new input in the same candidate would have confounded the two, and a future
  candidate crossing them (e.g. gradient boosting given the same climate input) remains a
  single, clean addition to the tree. `agent-autonomous`.
- **Population still not tried**: kept as `04_stage2/claim.md`'s existing deprioritisation
  (near-constant within a province relative to month-to-month case variation) rather than
  bundled into this candidate. `agent-autonomous`, carried over from batch 7.
- **`MIN_TRAIN_ROWS` raised from 12 to 21**: the parameter count rose from 4 to 7 (three new
  climate coefficients); kept the same "≥3× parameters" rule `a_linearLags` used rather than
  picking a new threshold. `agent-autonomous`.

## 3. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass (`tree`,
`provenance`, `hashes`, `plots`, `seeds`, `claims`, `combos`, `freeze`, `crossing`, `pool`)
except `git`, which failed only mid-batch on the expected uncommitted provenance/claim edits
and passed once those were committed. The re-derived stage-1 forecast was verified bit-for-bit
against `02_stage1`'s stored `per_cell_scores.csv` (408/408 cells, max|Δ|=0.0) before the
script trusted its own residuals, exactly as `a_linearLags` does.

## 4. Self-caught issue

The first draft of the root `analysis/claim.md` ranking line inserted `d_linearClimate` in the
wrong sorted position relative to seasonal climatology (26.85 vs. 26.91 — climate is actually
*better* than climatology despite being worse than stage 1 and `a_linearLags`). Caught on
re-reading the sentence before committing, not by a separate audit; corrected to the right
numeric order.

## 5. What batch 9 inherits

Phase C is closed again, this time with four stage-2 candidates tried and all four losing to
stage 1 alone. The climate-covariate question is narrowed, not closed: this batch rules out
lag-12 climate added to a *linear* correction, not climate added to a non-linear family
(`b_gradientBoosting` or `c_bayesianRidge`'s families, given the same climate input, are an
untried cell of the family × input grid) and not a genuinely forward climate signal (this
dataset has none to try). Population and cross-province pooling remain untried, as they were
after batch 7.

Nothing in this batch's own record recommends spending further batches on this grid before
moving to phase D — the informativeness/cost trade-off batch 7 raised has, if anything, gotten
less favourable (four families now tried and lost, not three) — but batch 8 does not make that
call unilaterally either; `04_stage2/claim.md` remains the place a future batch or the human
would look to decide whether to keep exploring inputs or move to stability. Batch 9 is expected
to start phase D (stability, ledger rows 9–11) unless redirected: enumerate the judgment calls
made across batches 1–8 as a perturbation manifest, cost it, freeze the development manifest,
and run it.
