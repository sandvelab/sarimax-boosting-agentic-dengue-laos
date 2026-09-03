# Batch 30 — the frozen figure is reported, the moved pairing is fatal

Generated from [[26-08-22_dengueForecastingCase]] — iteration 30

**State: done — produced.** `pair_holdout_development.py` no longer requires a frozen
development figure to equal what the tree computes today. A drifted figure is reported
against the band the dataset's own repeats of the reference define; a **moved pairing** — a
frozen row whose development twin the table no longer concludes — is fatal, and stops the run
before anything is written.

**Nothing in the reported analysis moves.** `holdout_vs_development.csv` and
`fork_sensitivity_both.csv` are byte-identical; in `holdout_vs_development.json` every
reported number is unchanged. `manifest_holdout.csv` was not touched and still hashes to
`fc9d1a16…`.

A second defect was found three lines from the first, is the same class, and **is fixed
here** rather than deferred, because it moved a reported number.

---

## 1. What batch 27 ran into, stated against the data

The script took each frozen `development_skill_score` from `manifest_holdout.csv` — correctly
— and then asserted that each one still equalled `conclusions.csv` **today**, to `1e-9`, a
tolerance its own comment called "not a tolerance for drift".

The development skill score divides by the reference model, which is unseeded. **So the
assertion can hold only on a tree whose development half has not been re-run.** It passed
exactly where it was not needed, and on the one run that needed it — a clean-room run of
`analysis/run.sh` from a fresh checkout, with all 32 held-out analyses already scored — it
exited 1 at the last script in the tree.

Batch 27's data, re-measured here from the preserved artefacts rather than read out of its
report:

| | |
|---|---|
| frozen figures that drifted | **32** |
| rows whose *pairing* moved | **0** |
| largest absolute move | **0.025673** (`provinces_reportingOnly__weighting_crpsWeighted`) |
| the run's own development noise band | **0.034944** |
| `manifest_holdout.csv` between the two trees | byte-identical |

The message the script died with — *"The pairing this compares on is no longer the pairing
that was frozen"* — described a condition the data did not contain.

## 2. The two differences, separated

| Difference | What happens | Why |
|---|---|---|
| a frozen figure that drifted | **reported, not fatal** | the score divides by the unseeded reference, so any re-run of the development half re-draws it. The frozen figure is a record of what was paired and it stands |
| a frozen row whose development twin the table no longer concludes | **fatal, before anything is written** | the pairing itself is gone: the comparison would be against an analysis this tree can no longer produce a figure for |
| a twin still in the table but with no skill score | reported, not fatal | the frozen figure does not need re-deriving to stand |

The distinction is categorical rather than numeric, and that was deliberate. **Widening the
tolerance to the width of the noise band was considered and rejected**: the band is itself a
draw of the same unseeded model — 0.021778, 0.043084, 0.034944 over three draws — so the
threshold would be a number that moves, and a check whose threshold is redrawn on every run
is not a check.

`holdout_freeze_check.json` had already drawn exactly this line, minutes earlier in the same
run, under `drift_under_an_unchanged_set`. The tree now agrees with itself about what is
fatal.

## 3. The second defect, found three lines away and fixed here

`development_beats_reference` was read from **today's** `conclusions.csv`, not from the
freeze. `manifest_holdout.csv` does not carry the column.

On batch 27's clean-room conclusions, **one row flips** —
`provinces_reportingOnly__family_hierNB`, `False` → `True` — and the reported development
count in `holdout_vs_development.json` reads **28 of 32 rather than 27**. A reported phase-E
figure was following a re-derived table: the fourth member of the family batch 24 named, in
the same script as the third and three lines from it.

It is fixed rather than deferred because **it moved a reported number**, and because the fix
needs no new frozen data. `conclude.py` defines the field as `ours.mean_crps <
reference.mean_crps`, and both sides are frozen beside the row, so it is now derived from
`manifest_holdout.csv` — reproducing the archived value on **all 32 rows**, which is why the
output table is still byte-identical.

**`development_beats_all_baselines` cannot be fixed the same way.** It compares against the
baselines' own CRPS, which was never frozen beside the row, and freezing it now would rewrite
`manifest_holdout.csv` — which plan §3 binds and `holdout_freeze.json` records the digest of.
So it stays read from today's table, and the output now **says so in the file**: it is named
as the one development figure in the phase-E answer that is re-derived rather than read from
the freeze, and that a re-run can therefore move. Whether the frozen manifest should have
carried it is a question for the reader implementing this method, and it is written down
rather than left implicit.

## 4. The defence, built against the data that stopped the run

`AI-internal/useful-scripts/check_pairing_defence.py` →
`AI-generated/validation/26-09-03_pairingDefence.json`. **All five pass.**

The one that matters is `drifted_frozen_figures`, which swaps in the clean-room run's own
`conclusions.csv` **and its own `distribution.json`** rather than a synthetic perturbation.
Both come from the same run deliberately: the band the drift is measured against has to be
the one that run drew for itself (0.034944), because measuring batch 27's drift against batch
15's band (0.021778) would compare two different draws of the same unseeded model and mean
nothing.

Against that input the fixed script **exits 0**, reports **32 drifted figures and 0 moved
pairings**, records the largest move as **0.025673 inside a band of 0.034944**, and is
verified to have compared on the frozen figures — by hashing the `development_skill_score`
column of the output table before and after the swap.

The other four: `pairing_moved` removes a development twin and confirms the run **exits 1 and
writes nothing** — `holdout_vs_development.json` byte-identical after the attempt, which is
what makes "fatal" mean something; `beats_reference_comes_from_the_freeze` inverts
`beats_reference` on every development row and confirms the output does not move;
`twin_without_a_conclusion` confirms a blanked twin is reported rather than fatal; and
`the_output_is_stable` confirms two runs on the archived tree produce byte-identical files.

Each scenario restores from git unconditionally, so the tree is as it was found. Nothing
touches `manifest_holdout.csv`.

## 5. What was decided, and by whom

| Decision | Agency |
|---|---|
| A drifted frozen figure is reported; a moved pairing is fatal. The distinction is categorical, not a widened tolerance | agent-autonomous |
| The noise band is reported beside the drift as context and is **not** used as a threshold, because it is itself a draw | agent-autonomous |
| `development_beats_reference` is derived from the frozen CRPS columns rather than read from today's table | agent-autonomous |
| `development_beats_all_baselines` is left re-derived and **named as such in the output**, rather than freezing it — that would rewrite `manifest_holdout.csv`, which §3 binds | agent-autonomous, inside the human-set §3 |
| The second defect is fixed in this batch rather than becoming a new one, because it moved a reported number and needed no new frozen data — the opposite of the call batch 27 made about this script | agent-autonomous |
| The defence swaps in the clean-room's `distribution.json` alongside its `conclusions.csv`, so the scenario reconstructs that run's tree rather than a mixture of two draws | agent-autonomous |

## 6. What this batch says about the method

Batch 24 found a frozen artefact recomputed at run time. Batch 26 found a recorded selection
re-derived at run time. Batch 27 found a recorded figure re-asserted against a recomputed one.
This batch fixed the third — and found the fourth **in the same file, three lines from the
third**, where batch 27 had looked and not seen it.

That is the sharpest version of the point these batches keep making. Batch 27 read this
script closely enough to diagnose its assertion exactly, write the fix into the ledger, and
explain why it was not fixing it that day. It still did not notice that the line below took a
reported development count from a table the same argument said could not be trusted. **The
defect class is not found by reading; it is found by running the thing from nothing and
looking at what moved.** Here it took a defence script that swapped in the real drifted input
and asserted on a number nobody had thought to check.

The second, smaller point: the fix that mattered was available because `conclude.py` defines
`beats_reference` as a comparison between two figures that *were* frozen. Nothing was
re-derived that could not be read — the freeze happened to carry enough. Where it did not,
for `beats_all_baselines`, the honest move was to say so in the output file rather than to
widen what the freeze covers after the year has been opened.

## 7. What is next

**Batch 31 — `/validate cleanroom` to completion**, on this tree. What batches 25 and 27 were
for. It is now the only thing standing between this project and a statement that
`analysis/run.sh` reproduces the analysis from a clean checkout.

Then **28** (`check_pool.py`'s disk-dependent member matching), **20** (the external check on
`tha` and `vnm`), and **19** (write-up, reproducibility report, release).

**Batch 19 still must not claim that `analysis/run.sh` reproduces this analysis from
nothing** until a run gets past the last script. This batch removed the reason the last run
did not; it did not run one.

**Nothing is carried to the human.** The noise-band question batches 25, 26 and 27 carried was
settled on 2026-09-03: the finding keeps being stated as a count.

## 8. Files

**Added**

- `AI-internal/useful-scripts/check_pairing_defence.py` — five situations put to the rebuilt
  check, driven by batch 27's preserved outputs.
- `AI-generated/validation/26-09-03_pairingDefence.json` — what it found.

**Changed**

- `analysis/05_stability/scripts/pair_holdout_development.py` — the drift/pairing split, and
  `development_beats_reference` from the freeze.
- `analysis/05_stability/results/holdout_vs_development.json` — the
  `frozen_pairing_verified` block, and two lines naming where each development count comes
  from. No reported number moves.
- `analysis/05_stability/provenance/pair_holdout_development.md` — a section appended.
- `AI-generated/validation/provenance.md` — a section appended.

**Unchanged, and checked to be so**

- `analysis/05_stability/results/holdout_vs_development.csv`,
  `analysis/05_stability/results/fork_sensitivity_both.csv` — byte-identical.
- `analysis/05_stability/results/manifest_holdout.csv` — `fc9d1a16…`, as batch 15 froze it.
  No scenario and no change in this batch touches it.
