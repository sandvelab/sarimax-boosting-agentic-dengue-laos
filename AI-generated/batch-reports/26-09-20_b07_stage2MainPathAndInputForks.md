Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 7)

# Batch 7 — stage-2 main-path decision and input-space forks

## 1. What this batch did

No new modelling. This batch closes out phase C (ledger rows 3–7) by making the two decisions
that row 7 owes: which of the three built stage-2 candidates sits on `04_stage2`'s main path,
and an explicit accounting of what stage 2 was and was not allowed to see.

**Main-path decision.** `a_linearLags` is `04_stage2`'s main path — already reflected in its
`claim.md` and `run.sh` since batch 6, formalised here: it is the least-bad of the three
candidates (mean CRPS 26.26 vs. stage 1 alone's 26.05, -0.78%), not a candidate judged to earn
its place. `b_gradientBoosting` (27.68) and `c_bayesianRidge` (28.07) remain runnable siblings,
per AGENTS.md §2's alternatives discipline.

**The central comparison, answered as of this batch** (`analysis/claim.md`): no stage-2 family
tried so far beats stage 1 alone. The honest development-data ranking, best to worst:

| Model | Mean CRPS | vs. stage 1 alone |
|---|---|---|
| Stage 1 alone (`02_stage1`) | 26.05 | — |
| `a_linearLags` | 26.26 | +0.78% |
| Seasonal climatology (`03_baselines/02_climatology`) | 26.91 | +3.20% |
| `b_gradientBoosting` | 27.68 | +6.25% |
| `c_bayesianRidge` | 28.07 | +7.73% |
| Persistence (`03_baselines/01_persistence`) | 28.32 | +8.72% |

Stage 1 alone is currently the best model built in this project, on this backtest.

**Input-space forks, logged explicitly** (`analysis/04_stage2/claim.md`, plan §3's requirement
that "what stage 2 sees as input... is either an alternatives node... or an explicitly logged
decision with its basis"). All three candidates share one input set — stage 1's lag-12
in-sample residual and cyclical calendar month, fixed once in batch 4's leakage analysis and
reused unexamined by batches 5 and 6. Surveyed what else exists rather than guessing:

- `analysis/01_data/01_prepare/results/development.csv` already carries `rainfall`,
  `mean_temperature`, `mean_relative_humidity` and `population` per province-month, alongside
  `disease_cases` — no new data acquisition needed to try any of them. **None were used by any
  candidate.** Climate covariates in particular are flagged as the most plausible untried route
  to a stage-2 model that actually earns its place, since dengue transmission has a known
  climate dependence that stage 1 (SARIMAX on raw counts) does not see at all.
- `Archive/lao-population/` holds only a country-level World Bank total, coarser than the
  per-province column already in the working dataset — not a source of anything new.
- Additional residual lags beyond lag-12 (e.g. lag-1 restricted to a split's first test month,
  where it is genuinely available) were not tried.
- Pooling across provinces (a shared or partially-pooled coefficient, as opposed to each of the
  three candidates' fully independent per-province fits) was not tried, and is named as a
  distinct kind of fork from a raw input feature.

None of these was run in this batch: each would cost roughly what batches 4–6 individually
cost (a fresh node, a contract-verification check against stage 1's stored forecast, its own
provenance record), not a cheap addition, and three families have already been tried and lost
on the same minimal input. Whether to spend further batches exploring richer inputs, versus
moving to the stability phase (rows 8–10) with `a_linearLags` frozen as the default stage-2
configuration, is left open for the human rather than decided by this batch — see §5.

## 2. Self-caught issue

`analysis/claim.md`'s `Children` section carried `main-path: (none yet)` since batch 1 — the
root node is `kind: sub-analyses`, for which `node.py`'s own convention (confirmed by reading
`AI-internal/useful-scripts/node.py` and by `01_data/claim.md`'s own `main-path: -`) is `-`,
not a placeholder string; `main-path` only has meaning for an `alternatives` node.
Corrected to `-` in this batch. No downstream node reads this field, so nothing depended on
the stale value; caught while editing the same file for batch 7's answer, not by a separate
audit.

## 3. Judgment calls logged, with agency

- **"Main path" among three losing candidates means least-bad, not adopted**: recorded
  explicitly in `04_stage2/claim.md` so a future reader does not mistake the `run.sh` default
  for an endorsement. `agent-autonomous`.
- **Climate covariates and pooling flagged but not run**: a cost/informativeness call
  (AGENTS.md §6) — each untried fork costs roughly a full batch, and the more useful next
  decision is whether to spend further batches on richer stage-2 inputs at all, which this
  batch treats as the human's call rather than making it unilaterally. `agent-autonomous` for
  the survey and the logging; the continue-vs-move-to-phase-D choice itself is left to the
  human, unmade.
- **`main-path: (none yet)` → `-`**: a small documentation-consistency fix, made visibly and
  reported here rather than silently. `agent-autonomous`.

## 4. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass except `git`
(clean after this batch's commit, aside from the pre-existing, out-of-scope untracked
`.idea/`). `AI-internal/useful-scripts/node.py tree` confirms `04_stage2`'s main path is
`a_linearLags` and both siblings are marked not-taken.

## 5. What batch 8 inherits

Phase C is closed. Stage 1 alone (mean CRPS 26.05) is the best model this project has built;
no stage-2 family tried on the minimal input earns its place. Two paths are open and neither
is decided here:

1. **Move to phase D (stability, ledger rows 8–10)** with the tree as it stands: enumerate the
   judgment calls accrued so far (stage 1's order/spec, stage 2's family and its minimal
   input, the combination rule, sigma-unchanged vs. own-posterior-variance, training window,
   zero-handling, the abstention threshold) as a perturbation manifest, cost it, freeze it, run
   it, and report the distribution rather than the single number.
2. **Spend one or more further batches on richer stage-2 inputs** (climate covariates above
   all) before moving to phase D, on the reasoning that phase D perturbs judgment calls already
   made rather than searching for ones not yet tried, and a stage-2 family given climate
   covariates might change the central finding rather than just its stability.

Whichever is chosen, `04_stage2/claim.md`'s fork log is the record of what was and wasn't
tried, so the choice is between two named options rather than a decision made on an unspoken
default.
