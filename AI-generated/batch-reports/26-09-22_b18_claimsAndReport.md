Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 18)

# Batch 18 — the claim collection built from the tree, and the report's drill-down rebuilt

## 1. What this batch did

Two deliverables, both of Rule 8 and Rule 9's kind rather than the analysis's: the claim
collection now covers every node in the tree, and the hierarchical report actually reaches the
raw values it promises. No number about dengue changed.

## 2. The claim collection

Before this batch the collection held 21 claims, of which 20 sat on `06_stability` and one on a
stage-2 candidate. Six nodes that produced results — the metric, the three data nodes, stage 1,
the baselines, the diagnostics, and `04_stage2` itself — had no claim at all, so their answers
existed in their own `claim.md` and nowhere the manuscript could be written from.

Twelve claims were added, **C21–C32**, one or two per uncovered node:

| Claim | Node | What it states |
|---|---|---|
| C21 | `00_metric` | The CRPS implementation matches `properscoring` to 1.11e-16 and a Monte-Carlo estimator within tolerance |
| C22 | `01_data/01_prepare` | 2,592 development and 216 sealed holdout rows from a complete grid whose checksum verifies |
| C23 | `01_data/02_characterise` | 17 of 18 provinces modelable; LA-VI excluded; LA-XN stops reporting mid-period |
| C24 | `01_data/03_backtest_scheme` | The fixed scheme resolves to 8 development splits and 4 held-out splits |
| C25 | `02_stage1` | Stage 1 alone: 26.05 over 371 cells, no fit failure, coverage 82.7% |
| C26 | `02_stage1` | Stage 1's six documented weaknesses and the forks not taken — recorded as `human-set` |
| C27 | `03_baselines` | Stage 1 beats persistence by 7.99% and climatology by 3.20% on development |
| C28 | `05_residualStructure` | The in-sample one-step residual is white (|ACF| ≤ 0.06 at every lag) |
| C29 | `05_residualStructure` | The out-of-sample error is skewed and concentrated; five provinces carry three quarters of the CRPS |
| C30 | `05_residualStructure` | Of 56 configurations, 10 beat a permutation null and 2 beat stage 1; the best is −0.84% |
| C31 | `04_stage2/h_levelOnlyBoosting` | The reported configuration's development result: 24.35, −6.53%, coverage 85.2% |
| C32 | `04_stage2` | All ten candidates ranked, with the selection rule that chose among them |

C26 carries `by: human-set` rather than the default: the statement exists because the human
decided stage 1 would be documented instead of repaired. The agency field records who made the
call the claim reports.

`claims.py audit` passes — all 32 claims resolve to files that exist.

## 3. The report's drill-down was pointing at nothing

Rule 8 asks that summaries link down to the values they aggregate, all the way to raw. The
generator's tree pages did that for nodes, claims, results, scripts and provenance. The level
*below* the tree did not: `_detail_pages` addressed the prior project's layout —
`analysis/04_score/01_collect/results/<combo>/metrics_cell.csv`, `crps_by_location.csv`,
`leaderboard.csv`, `analysis/results/<combo>/conclusion.json` — and none of those paths exists
here. The root page rendered the heading and then reported **"0 combination(s) scored"**.

This is the same shape of failure as the invariant that passed by looking in an empty place
(batch 16): a heading with nothing under it reads as "there is nothing below this level", not as
"this was never wired up". It was rebuilt rather than described.

The drill-down is now discovered from what is on disk. Every directory holding a
`per_cell_scores.csv` is a scored result — **103 of them**: stage 1, both baselines, the ten
stage-2 candidates, and every development and held-out stability combination. Each gets one page
carrying:

- the stored conclusion, displayed from `conclusion.json` or `comparison.json` as the file
  states it, with a link to that file;
- the `by_split` and `by_horizon` blocks the conclusion file already holds;
- the same cells grouped by province and by month;
- a link to the `per_cell_scores.csv` that every number above averages.

The report is now 127 pages and 1.8 MB: 23 node pages, 103 detail pages, and the root index.
Each node that owns scored results links its own; the root links all of them.

**One boundary, stated on every page that crosses it.** The by-province and by-month tables are
groupings the report computes for display. They are not separately stored results, and each
table says so. Storing an aggregate beside each of the 103 results would mean re-running the
analysis inside a reporting batch; that is recorded in the report's `provenance.md` as the
alternative not taken.

## 4. Decisions and their agency

- **Adding a claim for every uncovered node**: `agent-autonomous`, per Rule 9 and phase F.
- **C26 recorded as `human-set`**: the decision it reports is the human's.
- **Rebuilding the drill-down rather than noting it as broken**: `agent-autonomous`. A
  generated report that silently omits a rule's deliverable is worse than one that fails.
- **Computing the province and month groupings for display rather than storing them**:
  `agent-autonomous`, with the boundary written on the pages and in the provenance record.

## 5. Checks run

`/validate invariants`: all checks pass. `claims.py audit`: every one of the 32 claims resolves.
The report was regenerated from a clean tree and opens from `index.html` with no server.

## 6. What batch 19 inherits

A complete claim collection and a report that reaches the raw cells. Row 19 runs
`/validate cleanroom` and `/validate outsider`, and owes three things it should settle together:
the CSV line-ending mismatch between working copy and repository; the holdout completeness check
that records rows and months present but not whether `disease_cases` is populated (which is why
one province turned out unscoreable only when the year was opened); and the prior-project prose
that remains in `check_invariants.py`. The outsider check is the one most likely to find more of
the same, since two instances of it have now been found by hand.
