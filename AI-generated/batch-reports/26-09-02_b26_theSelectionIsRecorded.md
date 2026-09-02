# Batch 26 — the selection is recorded, not re-decided

Generated from [[26-08-22_dengueForecastingCase]] — iteration 26

**State: done — produced.** The development manifest's tier-1 order and tier-2 pairing are
now decisions recorded in `results/manifest_selection.json` and replayed, rather than
re-derived from numbers that do not reproduce. `check_pool.py` no longer crashes when a
weighting fork cannot take effect. **Nothing in the reported analysis moves**: `manifest.csv`,
`manifest_notes.json`, `forks.csv`, `tier2_rule.md` and all 51 `pool_check.json` files are
byte-identical, and `manifest_holdout.csv` still hashes to `fc9d1a16…`.

A third defect was found on the way, is larger than either of these, and is **left standing**
as batch 28 rather than repaired in passing.

---

## 1. What batch 25 ran into, stated exactly

`analysis/run.sh` exited 1 at the freeze check because two things `plan_manifest.py`
*derives* had moved:

**The tier-1 order** breaks its ties on `est_seconds_dev` — a **measured wall-clock
duration**, summed from each model's `run_cost.json`. The five `setup` rows have no
informativeness prior and equal reach, so their order is that tiebreak alone.
`provinces_reportingOnly` took 821 s in this tree and 1 039 s in the clean room, and moved
from rank 5 to rank 7. The order was sorted by how long rows happened to take.

**The tier-2 pairing** ranks tier-1 rows by skill score, and skill divides by the **unseeded**
reference model. The clean room re-selected **six of the eight pairs**.

Both are recorded now. Which combinations *exist* is still read from the tree on every run,
because `combos` requires the manifest and the tree to agree and §3 — as clarified on
2026-09-01 — lets the development manifest grow.

| Difference | What happens | Why |
|---|---|---|
| a combination the tree has, the record does not | **appended and reported** | §3's clarification: a late alternative gets a row at the end, not a place in an order fixed before it existed |
| a combination the record has, the tree does not | **fatal** | the record would describe a manifest this repository can no longer produce |
| a recorded pair whose halves are gone | **fatal** | these eight pairs are what phase D ran and phase E was frozen against |
| the rule would now choose differently | **reported, not fatal** | the reference is unseeded, so any re-run re-draws it. A check a correct clean-room run cannot pass is a check that gets weakened the first time it fires |

The rule still runs on every invocation and now decides nothing. It exists so
`manifest_selection_check.json` can say whether it *would* still choose the recorded pairs.

## 2. Five situations, one of them driven by the data that broke batch 25

`AI-internal/useful-scripts/check_selection_defence.py` →
`AI-generated/validation/26-09-02_selectionDefence.json`. **All five pass.**

The one that matters is `drifted_conclusions`, which swaps in **the clean-room run's own
`conclusions.csv`** rather than a synthetic perturbation — the defence is tested against the
data that defeated the old version:

- the rule, applied to those numbers, chooses **the same six different pairs** it chose in
  batch 25 — `trainingWindow_from2004__*` and the `aggregate_populationWeighted` pairs;
- **the recorded eight stand**, `manifest.csv` comes back byte-identical, exit 0;
- the disagreement is written to `manifest_selection_check.json`: *"the rule would now choose
  6 different pair(s); the recorded ones stand"*.

The other four: a recorded combination the tree cannot produce is **fatal**; a recorded pair
whose halves are missing is **fatal**; two runs leave the record byte-identical; and
`refreeze_from_cold` — the record deleted and the freeze path run again — returns **the same
order and the same eight pairs**, which is the regression test that this refactor did not
change what phase E was frozen against.

Each scenario restores from git unconditionally, so the tree is as it was found.

## 3. `check_pool.py`: branch on what happened, not on what was asked for

The premise block branched on `stage["choice"] == "b_crpsWeighted"` and then read
`fitted["weighting"]["validation"]`. But `run_ensemble.py` has a deliberate fallback: when the
training frame is too short to hold a validation block back it uses equal weights and records
why. So a combination that asked for CRPS weighting and *correctly* got equal weighting died
with `KeyError: 'validation'`.

That is how batch 25 lost `trainingWindow_from2004__weighting_crpsWeighted` — a window from
2004 leaves 36 months to refit members that require 60 — and finished with 31 of 33 rows
concluded instead of 32. Fork-blindness: a script keyed on the configuration rather than the
outcome, the family batch 14 found four times.

It now branches on what the weighting did, and records the fallback rather than passing over
it, because **a combination whose weighting fork could not take effect is a duplicate of its
other fork wearing a pair's name**.

Verified against the fitted model the failed row actually wrote, preserved by batch 25:
`method: equal`, `fell_back: true`, no `validation` key. **The two new keys are written only
on the fallback path**, which no archived combination takes, so all 51 `pool_check.json` files
stay byte-identical — batch 26 exists to make `run.sh` reproduce its archive, and spending
that on an extra field in 51 unrelated files would have been a poor trade.

## 4. The defect this batch found and did not fix

`matching_evaluation` pairs each pool member with a stored evaluation by globbing sibling
result directories and breaking ties with `found[0]`. So **which** evaluation it names — and
**whether it finds one at all** — depends on which combinations happen to exist on disk when
it runs.

Re-running the **unmodified** script today changes **18 of the 51** `pool_check.json` files.
The worst is the headline holdout row:

| `main__holdout` reconstruction | archived | re-run today |
|---|---|---|
| `not_done_because` | *"no stored evaluation of ['hier_nb', 'boosted']"* | `null` |
| `mean_crps_rebuilt` | `null` | **76.646** |

Batch 16 ran `main__holdout` before `family_hierNB__…__holdout` and `family_boosted__holdout`
existed, so the pool's independent reconstruction of the reported holdout result was recorded
as impossible. It is not impossible; it was early. Today it reconstructs and gets 76.646
against the reported 76.731 — a residual of 0.085, the same order as the 0.016–0.021 residuals
the check reports on the development rows.

**No number inside any of the eighteen moves.** What moves is which evaluation each names and
whether the reconstruction happened.

**It pre-dates this batch**, and that was checked rather than assumed: `HEAD`'s own copy of
the script was restored and re-run, and it produces the same change. So it is not attributable
to anything here.

It is **batch 28**. A tie-break repair alone would rewrite eighteen archived files while
leaving the time-dependence in place, and deciding what the headline holdout row's
reconstruction should say is not something to do in passing at the end of another batch.

## 5. What was decided, and by whom

| Decision | Agency |
|---|---|
| The tier-1 order and tier-2 pairing are recorded and replayed, never re-decided | agent-autonomous |
| Membership still comes from the tree; a late row is appended and reported, a missing recorded row is fatal | agent-autonomous, following the human's clarification of 2026-09-01 |
| A drifted selection is reported, never absorbed and never fatal | agent-autonomous |
| The change does not touch §3, and the reading is written down rather than assumed | agent-autonomous, inside the human-set §3 |
| The tier-2 `status` column keeps `select_tier2`'s wording, so a reported artefact is not rewritten to say what belongs in the record beside it | agent-autonomous |
| `check_pool.py` branches on the outcome; its new keys appear only on the fallback path | agent-autonomous |
| The eighteen drifting `pool_check.json` files are left alone and become batch 28 | agent-autonomous |

## 6. What this batch says about the method

Batch 24 fixed a script that re-derived a frozen artefact. Batch 25 found the same defect one
file upstream. This batch fixed that one — and found a third instance in a different node
while doing so. Three for three, and the general form has not changed since batch 24 named
it: **a value that records history must not be derived at run time.**

What is new is the second half of the pattern, which the `pool_check` defect shows more
clearly than the manifest did: **a derivation over the filesystem is a claim about when it
ran.** `matching_evaluation` is not obviously a recording of history at all — it looks like a
lookup — and it silently encodes the order in which batches happened to execute. The archived
`main__holdout` says a reconstruction was impossible, and what it actually records is that
batch 16 ran the rows in manifest order. Nothing in the file says so, and every number in it
is right.

The reason all three were found by running rather than by reading is worth stating plainly.
Each is a difference between two executions, and there is only one execution in front of you
when you read the code.

## 7. Files

**Changed**

- `analysis/05_stability/scripts/plan_manifest.py` — the order and the pairing are recorded
  and replayed; the rule now only reports. Docstring rewritten to say what is decided once.
- `analysis/03_models/03_candidate/c_ensemble/scripts/check_pool.py` — branches on the
  weighting as run; the batch-28 defect documented in place, not repaired.

**Added**

- `analysis/05_stability/results/manifest_selection.json` — the record. Written once.
- `analysis/05_stability/results/manifest_selection_check.json` — what the tree would decide
  now, against what is recorded. Written on every run after the first.
- `AI-internal/useful-scripts/check_selection_defence.py` — the five situations.
- `AI-generated/validation/26-09-02_selectionDefence.json`.

**Unchanged, and checked to be so**

- `analysis/05_stability/results/manifest.csv`, `manifest_notes.json`, `forks.csv`,
  `tier2_rule.md` — byte-identical across a freeze run and repeated replay runs.
- `analysis/05_stability/results/manifest_holdout.csv` — `fc9d1a16…`, as batch 15 froze it.
- All 51 `analysis/03_models/03_candidate/c_ensemble/results/*/pool_check.json`.

**Records appended** — `analysis/05_stability/provenance/plan_manifest.md`,
`analysis/03_models/03_candidate/c_ensemble/provenance/check_pool.md`.

`/validate invariants`: all ten pass.

## 8. What is left

**Batch 27** — `/validate cleanroom` to completion, which is what batch 25 was for and what
this batch unblocks. It is the first run that exercises the record from a clean checkout, and
it will produce a `manifest_selection_check.json` reporting a drifted selection — which is the
expected outcome, not a failure.

**Batch 28** — the `pool_check` reconstruction's dependence on what is on disk.

**Batch 20** — the external check on `tha` and `vnm`. **Batch 19** — the write-up, the
reproducibility report, the release, last.

Batch 27 should be expected to find something else. Batch 18's clean-room found the seal,
batch 25's found the manifest; each ran further than the last and stopped at the next thing
that had never been executed from cold.

Nothing is carried to the human. The noise-band question raised by batch 25 is still open and
is unaffected by this batch.
