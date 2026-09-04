# Batch 20 — the external check: the drop replicates in two more countries

Generated from [[26-08-22_dengueForecastingCase]] — iteration 20

**State: done — produced.** The reported model, unchanged, was run on the Thai and Vietnamese
files of the same harmonisation, in the same two arrangements Laos is reported in and on the
same months. **The development-to-final-year drop replicates in both**: Thailand +0.0856 →
+0.0197, Vietnam +0.0852 → **−0.0862**, against Laos's +0.1485 → +0.0868. All three drops are
larger than the two reference bands they are measured against, taken together.

**Phase E's largest open question has an answer, and it is not the comfortable one.** Batch
16 asked whether the holdout spread's width is about 2010, about one-year backtests, or about
an agent optimising against a development set, and said this batch was the only thing in the
plan that could bear on it. **2010 alone does not account for it**: the same year is harder
for the model relative to the reference in every country, including the two it never saw.

**And the model's Lao margin is partly about Laos.** Its development skill on the country it
was developed on, +0.1485, is **1.74 times** either sibling's — and the two siblings, which
have nothing to do with each other, agree to **0.0004**. That gap, 0.063, is about the size
of the whole development-to-final-year drop.

**One finding is about the evaluation rather than the model.** The reference model's own
unseeded re-run spread is **0.032 CRPS on Thailand's development backtest, 0.565 on Laos's
and 7.082 on Vietnam's** — a factor of **215** on one model at one configuration. Vietnam's
+0.0852 margin is *inside* its own noise floor and cannot be attributed to a model at all,
while Thailand's near-identical +0.0856 is thirty-five times its band. **A resolution
measured on one dataset says nothing about another**, and this project has been quoting one
number, 0.57 CRPS, as though it were a property of the method.

---

## 1. What was run

Four rows, planned and committed with their cost estimate before any of them ran
(`analysis/06_external/results/manifest_external.csv`, `external_plan.json`).

| combination | country | arrangement | provinces | cells | planned | actual |
|---|---|---|---|---|---|---|
| `main__vnm` | Vietnam | 3/8/3, evaluating 2008-01..2009-12 | 63 | 1 512 | 3 412 s | **1 325 s** |
| `main__vnmFinal` | Vietnam | 3/4/3, evaluating 2010 | 63 | 756 | 1 706 s | **853 s** |
| `main__tha` | Thailand | 3/8/3, evaluating 2008-01..2009-12 | 76 | 1 824 | 4 116 s | **1 866 s** |
| `main__thaFinal` | Thailand | 3/4/3, evaluating 2010 | 76 | 912 | 2 058 s | **2 473 s** |

Every row runs the reported analysis and nothing else: each setup fork at its main child, the
assembler, both required baselines, the reference model's four unseeded repeats, the linear
opinion pool and the scoring chain, then `conclude.py`. **No fork moves in any of them.** The
step lists are built by `05_stability/scripts/lib/driver.py` — the same library the 32
perturbation rows and the held-out year go through — because a check that ran a second
implementation of the pipeline would measure the code and not the model.

**Laos contributes 16 provinces over 371 and 192 cells; the siblings contribute 63 and 76
over 1 512 to 1 824.** The external check is measured on four to ten times as many cells as
the analysis it checks. That does not make it a better measurement of the Lao result — it is
a different country — but the sibling figures are not the thinner of the two.

## 2. The result

`analysis/06_external/results/external_conclusions.csv`, `external_vs_laos.json`,
`fig_external_skill.png`. Laos's two rows are read from the same `conclusion.json` the
headline is read from and are not recomputed here.

| country | arrangement | skill | CRPS ours / reference | 10–90 coverage | beats reference | beats both baselines | reference's own band |
|---|---|---|---|---|---|---|---|
| Laos | development | **+0.1485** | 18.817 / 22.098 | 0.863 | yes | yes | 0.565 |
| Laos | final year | **+0.0868** | 76.731 / 84.026 | 0.755 | yes | yes | 1.296 |
| Vietnam | development | **+0.0852** | 52.665 / 57.570 | 0.941 | yes | yes | **7.082** |
| Vietnam | final year | **−0.0862** | 83.913 / 77.252 | 0.893 | **no** | yes | 0.513 |
| Thailand | development | **+0.0856** | 12.521 / 13.693 | 0.967 | yes | yes | **0.032** |
| Thailand | final year | **+0.0197** | 25.605 / 26.120 | 0.875 | yes | yes | 0.124 |

**Five of six beat the reference; six of six beat both required baselines**, including the
row that loses to the reference. On Vietnam's final year the pool is beaten by EWARS-csd by
6.661 CRPS while beating persistence by 20.6 and climatology by 15.4 — it is not that the
model collapsed, it is that the reference did well on a year the model found hard.

### The drop

| country | development | final year | drop | the two bands together | outside them |
|---|---|---|---|---|---|
| Laos | +0.1485 | +0.0868 | **−0.0617** | 0.0410 | yes |
| Thailand | +0.0856 | +0.0197 | **−0.0659** | 0.0072 | yes |
| Vietnam | +0.0852 | −0.0862 | **−0.1714** | 0.1297 | yes |

Three countries of one harmonisation are not a sample, and no confidence statement is made
from them. What they say is that the drop is a thing that happens repeatedly rather than a
thing that happened once — which is exactly the distinction phase E could not draw from
inside a single held-out year.

**What this does not establish, and the file says so in its own text.** The two sibling final
years were not held out from anything: no model was developed on those files, so there was
nothing to hold them out from. The drop replicating there is therefore evidence that the
*year* is harder in the same way in three countries, not a second measurement of optimisation
inflation. The measurement that does bear on inflation is the development-arrangement gap in
§3.

## 3. The country it was developed on

On the development arrangement the model scores +0.1485 on Laos, +0.0856 on Thailand and
+0.0852 on Vietnam. **The two countries it never saw agree with each other to 0.0004 and sit
0.063 below the one it did.**

The design cannot attribute that 0.063 to development alone, and the claim says so: the three
countries differ in more than whether the model was tuned against them — 16, 76 and 63
provinces, mean monthly case counts differing by a factor of four, and three different
reporting systems. Nothing here varies development while holding the country fixed. What can
be said is that the only figure the project reports as its headline development result is
also the largest of the three, by about the size of its own held-out drop, and that the two
independent countries landing within 0.0004 of each other makes "Laos is simply an easier
country for this model" harder to hold than it would be with one comparison.

## 4. The finding that is about the evaluation

The reference model is unseeded and is scored four times on every dataset. The largest paired
difference between two of those repeats is what a dataset cannot resolve:

| dataset | reference mean CRPS | its own re-run spread | in skill |
|---|---|---|---|
| Thailand, development | 13.693 | **0.032** | 0.0024 |
| Thailand, final year | 26.120 | 0.124 | 0.0048 |
| Vietnam, final year | 77.252 | 0.513 | 0.0066 |
| Laos, development | 22.098 | 0.565 | 0.0256 |
| Laos, final year | 84.026 | 1.296 | 0.0154 |
| Vietnam, development | 57.570 | **7.082** | 0.1230 |

**A factor of 215 between the extremes, on one model at one configuration.** Vietnam's
development repeats run 55.683, 55.787, 56.045 and 62.766 — one repeat 12 % above the other
three. Thailand's run 13.680 to 13.712.

The consequence is direct. **Vietnam's +0.0852 margin is inside the reference's own re-run
spread**, so on that dataset the comparison this project is built on cannot be made at all;
Thailand's +0.0856, which is the same number to three decimals, is thirty-five times its
band. `readme-at-start.md` has been carrying "nothing below 0.57 CRPS can be attributed to a
model at all" as though it were a property of the method. It is a property of the Lao
dataset, and the same sentence written from Thailand would say 0.03 and from Vietnam 7.08.

## 5. Calibration does not travel either

10–90 interval coverage against a nominal 0.80: **0.863 on Lao development, 0.941 on
Vietnam's and 0.967 on Thailand's**; 0.755, 0.893 and 0.875 on the three final years. The
over-dispersion the project reports beside its Lao score is not a Lao artefact, and it does
not shrink when the model meets four times as many provinces — it grows. The rule that a
badly calibrated CRPS winner has not won applies more sharply abroad than at home.

## 6. What the batch had to build, and what it deliberately did not

**`Archive/sibling-datasets/`** — six files at the same pinned commit as the Lao ones. One
pin for all three countries, so that a difference between countries is not also a difference
between harmonisations.

**`analysis/01_data/03_siblings`** — the only node licensed to read them, as `01_partition`
is for the Lao file. It cuts each country onto the Lao calendar in the two arrangements and
checks against chap-core's own splitter that they land on **2008-01..2009-12 and exactly
2010**, from training sets ending 2007-12 and 2009-12. Thailand is truncated from its own
1993–2022 record; that is a judgment call, it is the node's, and its basis is in `claim.md`
— the check asks whether the Lao result holds in another *place*, so the years are held
fixed. **Thailand's other twenty-two years are left unspent, which is a decision and not an
oversight**: they are the material for the question of whether 2010 in particular was hard,
and this batch does not open it.

**`analysis/06_external`** — four rows, a budget, a cut order, and the report.

Three pieces of existing machinery moved rather than being copied, each verified
behaviour-preserving before anything ran:

- **`combos.py`** gained the four sibling datasets as *dataset suffixes* on the mechanism
  `__holdout` already uses — the analysis does not move, the country does — and with them the
  **scheme file became a property of the dataset**. That constant had been repeated in six
  setup scripts. Each was re-run under a combination it had already produced and returned
  every file byte-identical.
- **`05_stability/scripts/lib/driver.py`** — the step-list construction and row execution,
  moved out of `run_manifest.py`. The `--dry-run` output for all 32 development rows and for
  the holdout set is byte-identical before and after.
- **`reconstruct_pools.py`** now reads the rows it settles off the two manifests rather than
  off the directories in `c_ensemble/results/`. Without that, a node running *after*
  `05_stability` would have made its output depend on whether that node had run yet — the
  defect batch 28 removed, reintroduced one node further out. Verified: with all four
  external pools on disk, `pool_reconstruction.json` comes back at `977f3302…`, the same
  digest batch 28 produced, and no `pool_check.json` was rewritten.

**`/validate invariants` gained a third planned manifest rather than an exemption.** The
`combos` check closes the combination space; four external directories at every node had to
be *named* by something, and a directory the check is told to excuse is a check that has
stopped meaning anything. Its manifest-node exclusion is now derived from where the manifests
are rather than listed.

**What was not built, and is recorded as not built.** The pool's independent reconstruction
is unavailable on these four datasets: a member is evaluated on its own only under the family
fork's own combination, which is a perturbation row, and this check moves no fork. That is a
different thing from the ordering defect batch 28 removed — no order of execution would
produce the missing runs — and
`analysis/06_external/results/pool_reconstruction_external.json` says which it is, what it
would have cost (two more model evaluations per dataset) and why it was not bought.

## 6b. A fourth instance of batch 24's family, found before a clean-room run found it

The plan this batch committed at `bfbc096` carries an estimate, and that estimate divides a
**measured wall-clock duration** — the seconds the held-out `main` row took, read from
`05_stability/results/run_status_holdout.csv`. That file is rewritten by every run of
`05_stability/run.sh`, which on `analysis/run.sh` is the step immediately before this node.

So `plan_external.py` as first written would have come back from a clean checkout with a
different estimate in every row, and **the claim that the plan was committed before the rows
ran would have been a claim about a file that had since been rewritten**. It is the same
defect batch 24 found in the frozen manifest, batch 26 in the tier-1 order and the tier-2
selection, and batch 30 in the frozen development figure — a value that records a decision,
derived at run time from numbers that do not reproduce. The three before it were each found
by a clean-room run that exited non-zero; this one was found by asking what the next one
would do.

The repair is theirs. **The rows are structural** — they come from the tree and the sibling
scheme — so a disagreement means the record describes an analysis this tree cannot produce,
and it is fatal before anything is written. **The estimate is a measurement**, so a drift is
written into `results/external_plan_check.json` and the run carries on. The manifest and
`external_plan.json` are read and verified, never rewritten.

`AI-internal/useful-scripts/check_external_plan_defence.py` puts four situations to it, all
passing (`AI-generated/validation/26-09-04_externalPlanDefence.json`): the record as
committed; the cost unit changed by the size and direction batch 31's clean-room run changed
it, which reports four drifted estimates and leaves the manifest byte-identical; a structural
field moved, which exits 1 naming `main__tha.cells` and writes nothing; and no record at all,
which writes the plan. Every file is restored from git after each scenario, and the harness
refuses to start against an uncommitted one.

## 7. The budget, and where the estimate went

**Planned 3.14 hours against a six-hour budget; nothing was cut.** The budget was set before
anything was costed, at what `analysis/run.sh` already costs, on the argument that an external
check should not cost more than the analysis it checks. The cut order — whole country pairs
from the bottom, Thailand first — is recorded although it never bit, because a cut order
decided after the numbers arrive is not a cut order.

**Actual: 1.81 hours, a ratio of 0.58.** Phase D's two halves came out at 1.00 and 1.15; this
one is out by a factor of about two, and per row it runs 0.39 to 1.20. The unit is seconds
per evaluated cell measured on the Lao holdout, and it does not transfer to datasets four to
ten times the size. **So the total being right twice was a property of estimating a set
against itself**, which is the third form of batch 13's finding: the total can be right while
no individual row is, and here the total is wrong while the ranking it would have produced
was never needed.

## 8. The ten rules

| Rule | This batch |
|---|---|
| 1 — track results | Six provenance records written: two at `01_data/03_siblings`, four at `06_external`. Nine existing records gained appended sections for scripts that changed |
| 2 — no manual manipulation | Nothing edited by hand. The sibling files are cut by a script and verified as subsets of their sources line by line |
| 3 — environment | Unchanged and unre-pinned; the same `environment/chapenv` and the same pinned reference image digest |
| 4 — version control | Committed before the run (`bfbc096`) with the plan and the estimate in it, and again after. **§6b matters here**: the plan is now read and verified rather than recomputed, so what that commit carries stays what a later run compares against. No change to `AGENTS.md`, `CLAUDE.md` or `.claude/` |
| 5 — intermediates | Every external row stores its `eval.nc`, per-cell CSV, model spec, members and cost, exactly as its Lao twin does |
| 6 — seeds | Unchanged. Component seeds derive from the project seed and the component's name; no part of that derivation is the dataset. The reference is unseeded and is run four times on each of the four datasets |
| 7 — plots | One figure, with its plotted values beside it and its own script; the pre-aggregation values are the per-cell scores, which no axis here averages |
| 8 — hierarchical report | Not re-run this batch; `/hierarchical-report` rebuilds in seconds and batch 19 rebuilds it |
| 9 — claims | **Six added**, C42–C47 |
| 10 — release | Batch 19 |
| `/validate invariants` | Passes, all ten |

## 9. What is still unknown

- **Whether the drop is about the year or about one-year backtests.** This batch separates
  "2010 was hard in Laos" from "the final year is hard", but not "a four-split backtest is
  noisier than an eight-split one". Thailand's 1993–2022 record is the material that would
  answer it — the same pair of arrangements at several different end years, on one country —
  and it was not spent here.
- **How much of the 0.063 development gap is optimisation.** Nothing in this design varies
  development while holding the country fixed, and nothing can be built that does without
  developing a second model against a second country.
- **Why the reference model's re-run spread is 215 times larger on one country than another.**
  Measured, not explained. Vietnam's fourth repeat is 12 % above its other three; nothing
  here says why, and nothing was re-run to find out.

## 10. For the human

- **The case write-up now has its external check, and it says something sharper than "the
  model generalises".** It half generalises: the margin holds on both countries' development
  backtests and on one of the two final years, the drop replicates in all three, and the
  country the model was developed on is the one it scores highest on by about the size of
  that drop.
- **One sentence in `readme-at-start.md` was wrong in a way this batch found.** "Nothing
  below 0.57 CRPS can be attributed to a model at all" reads as a property of the method; it
  is a property of the Lao dataset, and the same measurement on Thailand gives 0.03 and on
  Vietnam 7.08. It is corrected there.
- **Batch 19 is the only open row.** The write-up, the reproducibility report and the release,
  which asks before the push.
