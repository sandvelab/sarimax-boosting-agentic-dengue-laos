Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 3)

# Batch 3 — required baselines

## 1. What this batch did

Built `analysis/03_baselines`, a sub-analyses node with two children — `01_persistence` and
`02_climatology` — plus its own comparison script run after both. Every result is
file-grounded, provenance recorded, and `/validate invariants` passes except the expected
mid-batch `git` finding.

**01_persistence.** Next-month-equals-last-observed, held flat across each split's whole test
window (a genuine multi-step persistence forecast, never re-anchored on truth the model
would not have). Scored through the same native CRPS pipeline as stage 1, on the identical
371 cells: **mean CRPS 28.32**, no fit failures (0/408).

**02_climatology.** Next month equals the mean of that calendar month across the training
window; scored the same way: **mean CRPS 26.91**, no fit failures (0/408).

**03_baselines (comparison).** Reads all three nodes' `per_cell_scores.csv` — stage 1,
persistence, climatology — asserts their (province, split, month) cell sets are identical
before comparing (they are: 371 cells each), and reports stage 1's percentage CRPS reduction
against each. Stage 1 (26.05) beats both: **7.99% lower than persistence, 3.20% lower than
seasonal climatology**. This is the batch's honest answer to "how much does the backtest
resolve": enough to separate stage 1 from naive forecasting, with a modest margin over
climatology in particular.

## 2. Judgment calls logged, with agency

Both baselines are natively point forecasts; this project's CRPS pipeline requires a Gaussian
predictive distribution (mean, sigma) for every model. Rather than invent a free-parameter
sigma, each baseline's sigma is drawn from the same historical quantity its mean is built
from, so the distributional widening it costs the forecast is exactly what its own training
data supports — no more, no less:

- **Persistence sigma** = standard deviation of the training window's own one-step
  differences (`value[t] - value[t-1]`), computed fresh per province per split. Rejected
  alternatives: a fixed sigma across all cells (arbitrary), and sigma from the full-history
  variance (would leak information beyond what a persistence forecaster has seen at that
  split's cutoff). `agent-autonomous`.
- **Climatology sigma** = standard deviation of that same calendar month's training-window
  values — the spread the climatology mean is itself computed from. Rejected: a single
  project-wide sigma (discards seasonal spread differences); sigma from the full
  non-seasonal history (mixes months with different means, overstates spread for low-variance
  months). `agent-autonomous`.
- **Sigma floor of 1e-6** on both baselines, reused from stage 1's own floor, for the rare
  province/split with fewer than two same-quantity training observations (std undefined).
  `agent-autonomous`.
- **Comparison asserts exact cell-set equality**, not just equal counts, before computing
  means — a silent mismatch under equal counts (371 = 371 by coincidence, different cells)
  would have made the comparison look honest without being apples-to-apples. It matched
  exactly, so the comparison ran on the intended set. `agent-autonomous`.

## 3. Checks run

`.venv/bin/python AI-internal/useful-scripts/check_invariants.py`: all pass except `git`
(clean after this batch's final commit). Every provenance sha256 in this batch was verified
against the actual file on disk before committing — the check batch 2 had skipped and then
had to fix after the fact.

## 4. A stray observation, out of this batch's scope

`analysis/claim.md` (root)'s aim paragraph still names "the prior project's externally
reported reference" as something stage 2 is established against — that citation was settled
*not* to happen at all (plan §1, §4b, 2026-09-20, human-set). Looks like leftover phrasing
from before that decision was settled, not touched by batch 2 or this batch. Left as found;
flagged rather than corrected, since editing the root claim's aim paragraph was not this
batch's job.

## 5. What batch 4 inherits

Stage 1 (26.05) beats persistence (28.32) and seasonal climatology (26.91) on the same 371
cells — the backtest resolves. Batch 4 (plan ledger row 4) starts stage 2: the
residual-correction contract and its first concrete model family, as an alternatives node
under `analysis/`, scored end to end as a two-stage ensemble against the same 371 cells.
