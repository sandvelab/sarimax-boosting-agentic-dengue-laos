Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 16)

# Batch 16 — the phase-E set frozen, and its machinery gated before the year opens

## 1. What this batch did

**No number about dengue changed in this batch.** What it fixes is what the held-out year will
be asked, before it is asked: the evaluation design, the set of configurations run across it,
the rule by which the answer is read — and the machinery that will run it, gated against
results this repository already has. Every figure below is read from files under
`06_stability/results/`: `manifest_holdout.csv`, `manifest_holdout_summary.json`,
`holdout_freeze.json`, `holdout_freeze_check.json` and `holdout_runner_verification.json`.

The batch's aim was widened from the ledger's "freeze the phase-E manifest" to include building
and gating the machinery (§4b, agent-autonomous). The reason is the one thing plan §3 exists to
prevent. Phase E opens 2010 once. If the code that opens it is also the code being debugged,
the first failure is repaired with a held-out number already on screen, and the second run is
not the first opening. So everything phase E will execute is written here, and the only thing
row 17 adds is the file.

## 2. The evaluation design

The project's fixed scheme — `n_periods 3`, `stride 3`, expanding window ending at the file's
last period — resolves over the combined 1998-01 to 2010-12 span to four splits:

| Split | Trains on | Months | Forecasts |
|---|---|---|---|
| 0 | 1998-01 – 2009-12 | 144 | 2010-01, 2010-02, 2010-03 |
| 1 | 1998-01 – 2010-03 | 147 | 2010-04, 2010-05, 2010-06 |
| 2 | 1998-01 – 2010-06 | 150 | 2010-07, 2010-08, 2010-09 |
| 3 | 1998-01 – 2010-09 | 153 | 2010-10, 2010-11, 2010-12 |

The twelve held-out months are each scored exactly once, at the horizons h = 1..3 that stage 2
is trained on. Each block after the first trains on the holdout months already forecast, which
is what a forecaster operating through 2010 would have had; the year is still read once, by one
script. The alternative — a single origin at 2009-12 forecasting twelve months — was rejected:
it scores the year at horizons no model here is built or evaluated for, and this project's
horizon coupling is to the scheme's `n_periods`, not to the length of the held-out file.

**The province set is development's seventeen**, derived from the development months alone. A
set re-derived from the combined file could move when the year opened — LA-VI is excluded on
development data and carries 2010 rows — and a cell set that moves when the year opens is a set
chosen after the fact. The base cell set is therefore 17 × 12 = 204 per row.

## 3. The gate

`lib/holdout_eval.py` was run in development mode — the development rows, the development
scheme — and compared value for value with results already stored in the tree:

| Reproduction | Rows | Mismatched values |
|---|---|---|
| Two-stage pipeline at the main path's configuration, vs. `04_stage2/h_levelOnlyBoosting` | 408 of 408 | 0 |
| Persistence, vs. `03_baselines/01_persistence` | 408 of 408 | 0 |
| Seasonal climatology, vs. `03_baselines/02_climatology` | 408 of 408 | 0 |

The two-stage row is the same gate the development combination runner passes, and it is
cheap: the pipeline is `lib/stage2_perturb.run_combination` unchanged, with the rows restricted
and the scheme supplied. **The baselines are the ones that matter.** `03_baselines`' scripts
read the development file and the stored split schedule and cannot take another file; they are
closed records of a produced result and were not edited. So the holdout baselines are a second
implementation of both forecasts, and nothing but this comparison says the two agree. Two
alternatives were rejected on the way: parameterising `03_baselines`' scripts (it would rewrite
the provenance of the development baseline scores) and adding a `provinces` parameter to
`lib/stage2_perturb.py` (it would change the `config` block every stored `conclusion.json`
carries).

The planner refuses to freeze a set this gate has not passed, refuses a manifest and a
configuration set that disagree in either direction, and on every later run verifies the frozen
file rather than rewriting it.

## 4. The frozen set

43 rows, 33 planned, an estimated 940 s against the 3,600 s ceiling carried over from phase D.
The line falls below every planned row: nothing is excluded for budget.

| Tier | Rows | What they are |
|---|---|---|
| 0 | 3 planned | The pre-registered main path `h_levelOnlyBoosting`, and the two required baselines. Stage 1 alone needs no row — every two-stage row's `conclusion.json` scores it on the same cells, which is plan §2's primary comparison |
| 1 | 4 planned, 5 not run | The not-taken `04_stage2` siblings. `f`, `g`, `i`, `j` are configurations of the verified pipeline and run; `a`–`e` are not, and say so |
| 2 | 26 planned | The development v2 perturbations under holdout names, so every judgment call measured on development is measured again on the held-out year, and the two pair by row name |
| 3 | 5 not run | The alternatives needing machinery this project has not built, carried forward unchanged |

**Why `a`–`e` are not run, recorded as a visible absence rather than dropped.** Each is trained
on stage 1's in-sample one-step residual, a construction the parametrised pipeline does not
express, so running it on the holdout means a holdout-capable rewrite of that node's own script.
All five lose to stage 1 alone on development (+0.78% to +7.73%, with `e`'s −0.63% failing plan
§2's calibration bar at 64.4% coverage), and batch 10's diagnostics explain the failure
mechanically: the target they are trained on is white. The held-out year is spent on the
configurations whose margin is in question.

**Costs are estimated, not guessed.** Each row carries its measured development wall-clock
(`run_log_v2.csv`) scaled by 0.569 — the ratio of total training months between the two
schedules, 594 against 1,044 — since a run's cost is dominated by fitting stage 1 once per
province per split over its training window. The rolling refit dominates at an estimated 440 s
of the 940. The baselines carry their own measured cost (0.1 s and 0.0 s on development).

## 5. What binds afterwards

`holdout_freeze.json` records the manifest's sha256
(`835bb52cab2e91cc630d420f59b07691cf8a7ddb0990e5079bfbba25d9080ab0`), 43 rows, and the commit it
was frozen at (`67f998c`) — a commit that carries every script the set will be run by and no
holdout result, which is what `/validate invariants`' `freeze` check asserts against git. It
also records the sealed holdout file's own digest, so the file phase E opens is the file that
was sealed; the digest is of the whole file and no case value was read to compute it. Every row
carries a `config_digest`, so a row cannot keep its name while its meaning moves —
`holdout_freeze_check.json` recomputes them on every run of `analysis/run.sh`.

**The reporting rule is frozen with the set**, because a frozen set without a frozen rule leaves
the choice of what to emphasise to be made after the numbers are seen:

- **Primary**: `main@h__holdout`'s mean CRPS and 90% coverage against stage 1 alone on the same
  cells. The two-stage ensemble earns its place on the held-out year if and only if it clears
  both of plan §2's bars there.
- **Secondary**: both stages against persistence and seasonal climatology on the same cells.
- **The spread**: the distribution over the tier-2 rows — how many beat stage 1 alone, how many
  with coverage not worse, min/quartiles/median/max, the rows more than two percentage points
  from the main path's margin (the same threshold as v1 and v2), splits improved, province and
  horizon concentration. Reported as a distribution, never as a best row.
- **Pairing**: every holdout row read beside its development v2 counterpart.
- **Binding**: nothing added, dropped, re-tuned or re-run once a holdout number has been seen;
  nothing promoted on held-out evidence; a result contradicting the development conclusion is
  the finding and is reported as such.

## 6. A check that was reading as evidence and was not

`check_invariants.py`'s `freeze` check asserts that the freeze predates the opening, by looking
for holdout result files at the frozen commit. It named `analysis/results/*__holdout/` — the
prior project's layout. This project's stability node writes to
`analysis/06_stability/results/`, so the check was looking in an empty place and passing. That
is worse than a check that fails, and it was fixed **before** the freeze it exists to protect: it
now matches any tracked path under `analysis/` carrying the `__holdout` suffix. A methodological
change (AGENTS.md §3, Rule 4), committed with this batch's "Before" commit and stated in those
terms. Two stale script names in its messages were corrected at the same time.

The check was then exercised rather than assumed: appending one row to the frozen manifest makes
it fail on all three of its testable branches (digest, row count, stale verification), and
restoring the file makes it pass.

## 6b. And a frozen set that was not staying frozen

Building the phase-E freeze surfaced a real defect in the development one, in the same node.
`02_plan_manifest.py` rewrote `manifest.csv` unconditionally, and its `est_cost_s` column is
wall-clock that `01_measure_run_costs.py` re-measures on every run. So **every full run of
`analysis/run.sh` moved the development manifest's bytes**, and `manifest_freeze.json`'s digest
became a record of a file that no longer existed — while nothing noticed, because the `freeze`
invariant covered only phase E's set. The cost columns change nothing the manifest plans, which
is precisely why it was invisible; the frozen digest is what the batch-13 and batch-15 reports
and claims C2–C13 rest on.

It was caught in the most ordinary way: a full re-run of the node was started as a
reproduction check, and stopping to think about what it would overwrite was what found it.

The fix is the same shape as phase E's. With a freeze present and the tree's main path still the
one it was written for, the script re-plans in memory, compares, writes
`manifest_freeze_check.json` and returns without touching the file; it fails if the manifest no
longer hashes to its freeze, and fails if re-planning would change anything beyond the two cost
columns. A change of main path still plans a new version, because that is a recorded decision
rather than a re-run — the path batch 14 took from v1 to v2 is unchanged. The `freeze` invariant
now asserts the development freeze as well as phase E's, and both refusals were exercised:
appending one row makes the script raise and the invariant report it; restoring makes both pass.

**`manifest.csv` is unchanged** — still `d2c5e813…`, the v2 digest frozen at `cef9a18`. Nothing
about the development stability results moves.

## 7. Decisions and their agency

- **The main path stays `h_levelOnlyBoosting`**, and the three v2 rows that scored better on
  development are not promoted: `human-set`, at the freeze. They lie within the alternative-seed
  row's own distance from `h`, so they separate it by less than the seed does; a change now would
  make the held-out year evaluate a fourth round of selection on the same 371 development cells.
- **Stage 1 is not reopened** after the no-differencing finding: `human-set`, reaffirming the
  2026-09-21 decision at the last moment it could be revised. `stage1=nodiff_101x100@h__holdout`
  is in the frozen set either way, so the year still measures how much of the margin survives a
  better stage 1 — as a perturbation, not as the main path.
- **The evaluation design** (four blocks, development's province set): `agent-autonomous`.
- **Building and gating phase E's machinery in this batch**: `agent-autonomous`; the ledger row's
  aim was widened and the reason recorded in §4b.
- **Not running `a`–`e` on the holdout**: `agent-autonomous`, with the reason in the manifest.
- **The reporting rule, the tiering, the cost model and the freeze mechanism**:
  `agent-autonomous`.
- **The invariant-checker fixes** (the phase-E leak path; the development freeze now asserted):
  `agent-autonomous`, methodological changes.
- **Making `02_plan_manifest.py` verify rather than rewrite**: `agent-autonomous`. It changes no
  result; it makes the development freeze hold what it claimed to hold.

## 8. Checks run

`/validate invariants`: all checks pass. The `crossing` check caught one real thing on the way —
a reporting threshold whose comment read as a value carried from another step — and the comment
was reworded; re-planning under the reworded script produced the manifest byte for byte
(recorded in the provenance record and in `holdout_freeze_check.json`). `.idea/`, which had
failed the `git` check every batch since it appeared, is now gitignored.

One thing to record rather than hide: while checking the holdout file's column layout, the first
data row of `holdout.csv` was displayed, so one held-out value was seen (Attapeu, 2010-01). No
decision in this batch rests on it — the set, the design and the rule were all fixed from
development data and the month labels — but plan §3 asks that the holdout not be characterised
before it opens, and this is the record that one cell was.

## 9. What batch 17 inherits

A frozen, hashed, executable set and a rule for reading it, with every row's machinery already
proven against this repository's own development results. Batch 17 opens 2010 once, runs exactly
the 33 planned rows, and reports by the frozen rule. Two things belong to that batch: recording
the opening itself, so that a second opening would be visible (plan §3's third consequence — a
tracked `run_status_holdout.csv` written when the year is read), and settling the `.gitignore`
entry for the working-tree seal marker, which still names the prior project's
`analysis/05_stability/`. The line-ending item (row 19) stands.
