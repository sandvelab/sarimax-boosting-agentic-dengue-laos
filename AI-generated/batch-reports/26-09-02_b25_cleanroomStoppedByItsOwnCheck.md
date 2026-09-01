# Batch 25 — the clean-room, stopped by the project's own check

Generated from [[26-08-22_dengueForecastingCase]] — iteration 25

**State: blocked.** `/validate cleanroom` was to be run to completion and was not. It ran
**3 h 48 m**, completed the entire development half, and **exited 1** at the freeze check —
because the frozen phase-E set turns out to have a derivation that a clean checkout cannot
reproduce. The phase-E half has still never run from a clean checkout, and
`analysis/run.sh` does not currently run to the end from one.

What is missing and what would unblock it is in §6. A great deal was established on the way,
and none of it is the deliverable this batch was for.

The run itself was launched detached from the session, so the failure mode that ended batch
18's clean-room — the session being cut off — did not recur. It got further and stopped for a
reason.

---

## 1. What the run establishes, before the reason it stopped

`AI-generated/validation/26-09-02_cleanroom.md`, with figures in
`26-09-02_cleanroom_comparison.json` and `26-09-02_cleanroomTier2Drift.json`.

The harness and comparison scripts were **verified by digest against batch 18's provenance
record before the run started**, so this is the same check run further, not a new one.

The environment built from `environment/lock.txt` and reported **"matches
environment/lock.txt exactly (174 packages)"**. Of **4 306 tracked files, 3 458 came back
identical.**

**Every model this project wrote reproduced its CRPS exactly, in every combination.** Batch
18 could say this of the reported main path; this run says it of the whole development set.

| model | combinations identical | moved |
|---|---|---|
| persistence | 32 | **0** |
| climatology | 32 | **0** |
| ensemble (reported) | 27 | **0** |
| hier_nb | 4 | **0** |
| boosted | 1 | **0** |
| **reference** (unseeded) | 6 | **26** |

Ninety-six model-combination scores and not one of ours moved by a bit. On the main path the
reference moved 22.098446 → 22.383842 (**+0.285 CRPS**) and carried the skill score
+0.148498 → +0.159355 (**+0.0109**). `beats_reference` and `beats_all_baselines` stay true.

## 2. Why it stopped, and why that is the right outcome

**The frozen phase-E set has a derivation the analysis cannot re-run.**

`manifest.csv`'s 24 tier-1 rows are planned from the tree. Its **8 tier-2 rows are not** —
they are *selected from tier 1's own results* by `tier2_rule.md`: rank each tier-1 row by how
far its skill score sits from the main path's, take the top two `setup`, top two model and
top `scoring` rows, pair the groups.

**Skill score divides by the unseeded reference model.** So the ranking that picks tier 2
ranks numbers that do not reproduce, and on a second draw it picked differently:

| group | archived | clean-room |
|---|---|---|
| S (setup) | `provinces_reportingOnly`, **`provinces_mergeVientiane`** | `provinces_reportingOnly`, **`trainingWindow_from2004`** |
| M (model) | `family_hierNB`, `weighting_crpsWeighted` | unchanged |
| A (scoring) | **`aggregate_caseWeighted`** | **`aggregate_populationWeighted`** |

Two selected rows changed; because the groups are paired, **six of the eight tier-2 pairs
changed.**

**The margins show it was never stable.** The rule's deciding margin is how far the last row
admitted sits above the first excluded:

| group | archived margin | band = 0.043084 | flipped? |
|---|---|---|---|
| S | **0.001002** | 1/43 of it | **yes** |
| A | **0.003211** | 1/13 of it | **yes** |
| M | 0.093547 | 2× it | no |

The one group decided by a real difference is the one that survived. The other two were coin
tosses against the project's own acknowledged noise, and the record has been presenting all
three as the output of a rule.

The freeze check then did exactly what batch 24 built it for: `manifest_holdout.csv` is
intact — 33 rows, hashing to `fc9d1a16…` — and the script **refused to rewrite it**,
reporting `9 difference(s) the frozen set cannot absorb` (six frozen rows the tree no longer
carries, three whose rank moved) and exiting non-zero.

Batch 24 predicted this run would be the first to find its new failure mode, and named the
scenario: under the superseded script, **this run would have silently rewritten the frozen
development pairing with its own re-drawn reference numbers.** It did not, because batch 24
had already closed it.

**What is and is not in question.** The phase-E results stand: the set was frozen in batch 15,
committed before 2010 was opened, and batch 16 ran exactly it. What is not reproducible is the
*derivation* — a reader re-running the analysis gets a different eight pairs and cannot reach
the frozen set from the inputs. The eight pairs are a **decision**, correctly recorded, that
the project has been treating as a **derivation**. That is batch 24's own lesson standing one
file away from where batch 24 applied it: *a value that records history must not be derived at
run time.*

## 3. The band is a random variable, and the headline moves with it

Batch 18 flagged that the resolvable-difference floor moved 0.565 → 0.449 and that the
project quotes it as a constant. This run makes it much harder to leave alone.

| | archived | clean-room |
|---|---|---|
| skill against the four repeats | 0.1376, 0.1415, 0.1551, 0.1594 | 0.1448, 0.1512, 0.1521, **0.1879** |
| **skill band** (max − min) | **0.021778** | **0.043084** |
| CRPS floor | 0.565 | 1.167 |
| **forks moving more than the band** | **6 of 17** | **3 of 17** |

The band is a **max minus a min over four draws** — close to the least stable statistic that
could serve as a yardstick. One high draw doubled it.

Three forks crossed from above the band to below it — `02_setup/02_trainingWindow`,
`02_setup/03_provinces`, `03_models/01_baselines/01_persistence` — and **none of them moved**
(0.021875→0.037047, 0.037553→0.041809, 0.027933→0.027576). The yardstick moved.

So batch 15's headline — *"six of the seventeen judgment calls move the conclusion further
than the reference model moves on its own, and eleven do not"*, carried into
`readme-at-start.md` and into the claim collection — **reads "three and fourteen" on a second
draw of the same unseeded model.** Only `family`, `weighting` and `aggregate` are clear of the
band on both draws.

This is not a defect to fix; it is a property of measuring against four draws of an unseeded
model, and it needs saying in the manuscript rather than repairing in code. It is carried to
the human in §6.

## 4. A row that crashed, and a pair that could not have meant what it says

The drifted selection ran seven of its eight pairs and crashed on the eighth,
`trainingWindow_from2004__weighting_crpsWeighted`, at `check_pool.py`:
`fitted["weighting"]["validation"]`, `KeyError: 'validation'`.

**The pipeline was right and the check was wrong.** `run_ensemble.py` has a deliberate
fallback and it fired and recorded itself: *"holding back 12 months would leave 36 to refit
the members on, below the 60 this model requires"*, `"method": "equal"`, `"fell_back": true`.
`check_pool.py` branches on the **configured** choice, `stage["choice"] == "b_crpsWeighted"`,
rather than on what the weighting actually did — the fork-blindness family batch 14 found four
times.

Two things follow, the second more interesting than the first.

**It was unreachable until the selection drifted.** One run of a differently-drawn ranking
found a latent crash in a combination the archived tier 2 never chose.

**And that pair is degenerate.** It is supposed to perturb the weighting fork under a
shortened training window, and under that window the weighting fork *cannot take effect* —
the CRPS-weighted child silently becomes the equal-weighted one. Had it run, it would have
duplicated the training-window row under another row's name. That is a property of the pair,
not of this run, and it is worth knowing about a rule that can select it.

## 5. What was decided, and by whom

| Decision | Agency |
|---|---|
| The batch is reported **blocked** rather than "done — produced": it established a lot, and it did not do the one thing it was for | agent-autonomous |
| The clean-room is run detached from the session, so an interrupted check cannot be mistaken for a finished one | agent-autonomous |
| The harness and comparison scripts are verified by digest against batch 18's record before running, so "the same check, run further" is a checked claim | agent-autonomous |
| Nothing is fixed in this batch — not the manifest derivation, not `check_pool.py` — because a fix needs a design and a four-hour re-run to verify, and §5 says a blocked batch stops | agent-autonomous |
| The clean-room's own outputs are copied into the repository before the scratch clone is discarded, so the numbers survive the evidence | agent-autonomous |
| `26-09-02_cleanroom_comparison.json`'s holdout half is recorded as **absent, not verified**, in the file's own provenance record | agent-autonomous |
| Whether the noise band should stay a max-minus-min over four draws | **carried to the human** |

## 6. What is missing, and what would unblock this batch

**Missing:** the phase-E half has never been executed from a clean checkout, so the holdout
distribution is unverified from cold, and `analysis/run.sh` does not run to completion from a
clean checkout at all.

**What would unblock it** is one change, and it is the same shape as batch 24's:

**Batch 26 — the development manifest stops being re-derived.** The tier-1 rank order and the
tier-2 selection are decisions taken once, from one draw of tier 1; they must be *recorded*
and verified, not recomputed. The freeze path already exists for exactly this and can be
reused. The `combos` invariant must keep working, so the tree still has to supply the rows —
what stops being re-derived is the *ordering and the pairing*, not the membership.
`check_pool.py`'s fork-blindness belongs in the same batch, since it is reachable only through
tier-2 selections and is a two-line fix.

Note this does **not** touch §3: the clarification of 2026-09-01 binds `manifest_holdout.csv`
and nothing else, and that file is intact and stays byte-identical. It is recorded here rather
than assumed, because the change is adjacent to the freeze machinery.

**Batch 27 — `/validate cleanroom` to completion**, on the fixed tree. What this batch was for.

Then **20** (the external check on `tha` and `vnm`) and **19** (write-up, reproducibility
report, release) as before. **Batch 19 must not claim that `analysis/run.sh` reproduces this
analysis from nothing** until batch 27 says so — it reproduces the development half and stops.

**One thing is carried to the human**, because it is a question about what the project
reports rather than about how it works:

> **The reference noise band is a max minus a min over four draws of an unseeded model, and
> two draws of it differ by a factor of two — 0.0218 and 0.0431.** Every "N of 17 forks move
> the conclusion more than the reference moves on its own" is a statement about one such
> draw, and N is 6 or 3 depending which. Options are to quote it with its own uncertainty, to
> re-estimate it from more repeats, or to state it as an order of magnitude and stop ranking
> forks against it. All three change what phase D reports, so none is the agent's.

## 7. What this batch says about the method

Batch 18's summary was that `/validate invariants` **verifies shape and never content**.
Batch 24 added a third thing: a script that re-derives a frozen artefact is caught by neither.
This batch is the demonstration that the third thing is not rare — the *same defect* was
sitting in the file the fixed one is derived from, and neither batch 18 nor batch 24 found it,
because both were reading code and only a cold run of the whole thing puts a second draw of an
unseeded model through a selection rule.

The sharper point is about the selection rule itself. It is a good rule: written before tier 1
ran, hashed into `manifest_notes.json`, applied once. Everything the method asks for was done.
And it still produced an unreproducible artefact, because **nobody asked whether the quantity
it ranks on is stable enough to rank on.** The margins were 0.001 and 0.003 against a noise
band of 0.02–0.04 that the project had already measured and was already quoting. The
information needed to predict this was in the repository, in a file the rule's own output sits
next to.

One thing about this batch's own record, kept because the project is about exactly this. While
writing the provenance record for `26-09-02_cleanroomTier2Drift.json` I wrote a **fabricated
sha256** for `plan_manifest.py` — a plausible 64-hex string that was not any file's digest. It
was caught before the commit by hashing every digest in the new records against the files they
name, and the record now carries `ffb398e8…`, which is the file's. It is worth recording that
the failure mode this repository is built to prevent is one its agent will commit unprompted,
in the middle of a document about provenance, and that the thing that caught it was running a
check rather than re-reading.

## 8. Files

**Added**

- `AI-internal/useful-scripts/cleanroom_tier2_drift.py` — why the run stopped: the per-model
  reproduction table, the tier-2 selection both ways with its deciding margins, and the band.
  Carries a self-check — applying its copy of the rule to the archived conclusions must return
  the frozen eight pairs, and does.
- `AI-generated/validation/26-09-02_cleanroom.md` — the check.
- `AI-generated/validation/26-09-02_cleanroom_comparison.json` — by `cleanroom_compare.py`.
- `AI-generated/validation/26-09-02_cleanroomTier2Drift.json` — by the new script.
- `AI-generated/validation/26-09-02_cleanroom-artefacts/` — what the run wrote, copied out
  before the clone was discarded, with a README.

**Unchanged, and checked to be so**

- `analysis/` — nothing in the analysis was run, edited or re-run by this batch. The clean-room
  ran in a throwaway clone.
- `analysis/05_stability/results/manifest_holdout.csv` — `fc9d1a16…`, as batch 15 froze it.

**Records appended** — `AI-generated/validation/provenance.md`, two sections.
