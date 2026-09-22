Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 17)

# Batch 17 — the held-out year, opened once

## 1. The opening

2010 was opened at 19:59:33 on 2026-09-22, at commit `8eda4fd`, and the frozen set ran in full:
33 of 33 planned rows, 623 s against an estimate of 940 s. Four preflight refusals were evaluated
before a single held-out byte was parsed, and all four passed — the manifest still hashed to
`835bb52c…`, the sealed file still hashed to `389e4f49…`, the gate still recorded three exact
reproductions of stored development results over the frozen row and cell sets, and every planned
row had an executable configuration. Each refusal had been exercised against a deliberately
broken input first; each stopped the run.

The opening is a row in `results/run_status_holdout.csv`, a file the runner appends to and never
overwrites, so a second opening would be a second row rather than a silently replaced first one.
**Opening number: 1.** Nothing was added, dropped, re-tuned, re-run or promoted afterwards.

## 2. The primary answer: the second stage earns its place

By the rule frozen in batch 16, before any of this existed:

| On the 192 scored cells of 2010 | Mean CRPS | 90% coverage |
|---|---|---|
| Stage 1 alone (SARIMAX) | 128.51 | 57.3% |
| **Two-stage ensemble (`h_levelOnlyBoosting`)** | **99.20** | **61.5%** |
| Margin | **−22.81%** | **+4.2 points** |

Both of plan §2's bars are cleared: lower mean CRPS, and coverage not worse. All 4 splits
improve, 75% of cells improve, and every horizon improves (h1 102.40 → 82.10, h2 126.99 → 94.06,
h3 156.14 → 121.44). The margin is **16.3 percentage points larger** than the development margin
of −6.53%, not smaller; of the 31 rows paired by name across the two datasets, 29 gain more on
the held-out year (median shift −15.6 points).

The sign survives every frozen perturbation. All 26 tier-2 rows keep the ensemble ahead with
coverage not worse, from −29.25% to −4.18%, median −20.89%, quartiles −22.81% to −17.82%, no
sign flips and no row improving fewer than half its splits.

**This is the question the project was built to answer, and the answer is yes.**

## 3. The finding that qualifies it

On the same cells, scored through the same pipeline and the same CRPS implementation:

| Required baseline | Mean CRPS | 90% coverage |
|---|---|---|
| Seasonal climatology | **77.29** | 54.7% |
| Persistence | 127.58 | 56.2% |

**Seasonal climatology beats the two-stage ensemble by 22% and stage 1 alone by 40%.** On the
development backtest the ranking was the other way round — stage 1 (26.05) ahead of climatology
(26.91) by 3.2%, which is what batch 3 reported and what every subsequent batch built on.

Coverage collapses for everything: 54.7% to 61.5% against a nominal 90%, where development gave
82.7% for stage 1 and 85.2% for the ensemble. The correction improves calibration here exactly as
it did on development, by 4.2 points — but from a level at which no configuration in the frozen
set is adequately calibrated.

So the honest statement of the result is two sentences, not one: *a residual-correction stage
trained on stage 1's multi-step out-of-sample error earns its place robustly and by a wide margin
on held-out data — on top of a first stage that is itself the wrong model for the year it was
tested on.* Plan §2 asks for exactly this: a model that wins on mean CRPS while being badly
calibrated has not won, and a naive baseline that beats the reported model is reported.

## 4. Why every number is five times larger

2010 is an epidemic year unlike anything in the development test span
(`results/holdout_year_context.json`, written after the opening and recorded as a description of
the data rather than a row of the frozen set):

| | Held-out 2010 | Development backtest span (2008-01 – 2009-12) |
|---|---|---|
| Scored cells | 192 (12 months) | 371 (24 months) |
| Total cases | 22,903 | 12,291 |
| Mean cases per cell | 119.3 | 33.1 |
| Mean monthly national total | 1,909 | 512 |
| Largest monthly national total | **5,649** (2010-09) | 1,410 (2009-09) |

The epidemic runs from June to October 2010 and peaks at four times the largest month the models
were ever fitted through. A SARIMAX on raw counts with a Gaussian predictive interval does not
follow that, which is what the coverage figures say; the residual correction recovers a large
part of the level error, which is what the CRPS margin says; and the seasonal mean of the same
calendar month, which carries no trend at all, does better than either.

## 5. What the held-out year turns on

The input given to stage 2, far more sharply than development showed:

| Configuration | Held out | Development |
|---|---|---|
| `h_levelOnlyBoosting` (the main path) | **−22.81%** | −6.53% |
| `j_levelOnlyBoundedBoosting` | −22.70% | −6.78% |
| `f_oosErrorRidge` | −3.89% | −1.64% |
| `i_boundedBoosting` | −2.27% | −5.85% |
| `g_oosErrorBoosting` | −2.25% | −3.41% |
| main path + recent-residual and cross-province features | −4.18% | −3.32% |

Every configuration carrying the recent-residual and cross-province features gains 4% or less;
both level-only configurations gain about 23%. On development that gap was about 3 percentage
points; here it is about 19. **Had `g_oosErrorBoosting` remained the main path, as it was until
batch 14, the held-out margin reported here would have been −2.25%.** The pre-registered choice
was made on development evidence by a rule written before the results were seen, and it happened
to be the configuration that generalised.

Sixteen of the 26 tier-2 rows move the margin beyond the two-point threshold, against eight of 26
on development — so the *size* is less stable on the held-out year, not more, even though the
sign is unanimous. The gain is also less concentrated by province than on development: eight of
the sixteen provinces improve in every combination and none never improves, where development had
one province (Oudomxay) that never improved.

## 6. What was not promoted, and what is not covered

Three tier-2 rows beat the main path on the held-out year — no winsorisation (−29.25%), the
looser winsorisation bound (−28.72%), a higher learning rate (−25.77%). **None is promoted.** The
holdout measures a pre-registered configuration; selecting on it would spend the only unused data
this project has and would turn the reported margin into a maximum.

Not run, with the reasons recorded in the frozen manifest: the five in-sample-residual siblings
(`a`–`e`), and the five tier-3 alternatives. The largest of those is the one the held-out
calibration result now points straight at — **a count or heavier-tailed predictive family at
stage 1**, which batch 10's diagnostics identified as the only change that could repair coverage,
and which was recorded as not run by the human-set decision of 2026-09-21 that stage 1 is not
repaired.

One province, **LA-XN, reports no cases for any month of 2010**, so its 12 cells carry no actual
to score against and the held-out evaluation is 16 provinces, not 17 — 192 of the 204 frozen cell
slots. Batch 1's completeness check recorded rows and months present, which they are, and did not
record whether `disease_cases` was populated; that gap belongs to row 19. Four
`Mean of empty slice` warnings came from the same province's all-missing window in the rows that
carry trailing-incidence features; the expression is guarded, the feature degrades to 0, and the
province contributes no scored cell. Recorded rather than silenced.

## 7. One correction, made with the year still shut

The first version of the runner required the gate file to hash to the digest the freeze recorded
for it. It refused to open the year — correctly by its own rule and wrongly as a rule, because
that file carries the wall-clock of its own three checks. Its digest had already moved inside
batch 16 (the freeze recorded `c9882891…`; the next run of the gate script wrote `44dac8fc…`,
which is what was committed) with nothing about the gate having changed, and from a clean clone
the precondition could never have been satisfied.

`holdout_freeze.json` is explicit about what binds: the manifest is the frozen artefact and the
other `frozen_inputs` digests are context recorded at the freeze. The runner had promoted a
context digest to a precondition. It now asserts the gate's *verdict* — three reproductions, zero
mismatched values — and its *scope*, checked against the frozen manifest's own `n_expected_cells`
rather than against itself. The correction is its own commit, made before the year was opened,
which is the whole reason batch 16 wrote this code in advance.

A second, smaller one: the collector left every row that ran carrying the manifest's `planned`
status, so its first table reported zero rows run. Fixed and re-run before anything was read from
it; the faulty version wrote only status strings and produced no held-out number.

## 8. Decisions and their agency

- **Running the frozen set exactly as frozen, and promoting nothing afterwards**:
  `agent-autonomous`, per plan §3 and the rule frozen in batch 16.
- **Correcting the runner's gate precondition before opening**: `agent-autonomous`.
- **Characterising the opened year as its own result, explicitly not a row of the set**:
  `agent-autonomous`.
- **Reporting the baseline comparison as the finding rather than a footnote**:
  `agent-autonomous`, per plan §2.
- **The main path and the fixed stage 1 the whole evaluation rests on**: `human-set`
  (plan §4b, 2026-09-21 and 2026-09-22).

## 9. Checks run

`/validate invariants`: all checks pass. `claims.py audit`: every pointer resolves. Claims
C14–C20 are in the collection. The four preflight refusals were each exercised against a broken
input before the run and each stopped it.

## 10. Two things for the human

**Does the held-out calibration collapse reopen stage 1?** The decision not to repair it was
yours, twice, on development evidence. The held-out year says that the fixed stage 1 is beaten by
a seasonal mean and that no model in the frozen set is adequately calibrated on an epidemic year.
The fork that addresses it — a negative-binomial or zero-truncated-normal predictive family —
is built into the record as not run. Building it now would be a new development-side batch, and
it could not be evaluated on 2010 without opening the year a second time.

**May anything further be evaluated on 2010?** Plan §3 allows one opening, and it has been used.
The manuscript can be written from what is now in hand. A second opening is possible and would be
recorded as a second row in `run_status_holdout.csv`, but it is a cost only you should decide to
pay.

Batch 18 builds the claim collection from the tree and generates the hierarchical report. The
line-ending item and the clean-room and outsider checks (row 19) stand, and the holdout
completeness gap above joins them.
