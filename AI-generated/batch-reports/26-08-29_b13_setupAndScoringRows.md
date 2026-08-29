# Batch 13 — `/perturb run`: the seven setup and scoring rows

Generated from [[26-08-22_dengueForecastingCase]] — iteration 13

**Phase D · Status: done — produced · Executed 2026-08-29**

---

The first batch of phase D that runs anything. Seven of the manifest's twenty-four tier-1
combinations now have conclusions, the seven children they need are built, and the external
population series one of them depended on is archived.

**The five `02_setup` forks do not move the conclusion.** Skill spans **+0.1266 to +0.1861**
around the main path's +0.1485, and every one of those gaps is smaller than the reference
model's own 0.57 CRPS re-run spread. Our pool's raw CRPS spans 18.552 to 19.011 across the
five — a range of 0.46 CRPS, which is less than the noise on the number it is compared
against.

**The one scoring fork moves it four times as much.** Population weighting gives **+0.2288**
and case weighting **+0.2320**, both about +0.08 of skill from the main path, produced by
re-weighting a stored file and re-running no model at all. The cheapest row in the manifest —
thirteen seconds against twenty minutes — is the one the conclusion is most sensitive to.

**Under case weighting, persistence beats the model this project reports.** 86.598 against the
pool's 88.484, on the months when dengue was actually happening. The pool's 10–90 coverage
falls from 0.863 to **0.701** there: it is too wide on the quiet months that dominate the
unweighted mean and too narrow on the outbreak months that dominate this one. This is the most
useful thing tier 1 has produced and it is not a skill score.

**Three defects and one measurement about the platform**, none of which planning could have
found. Two were in our own shared code; one is a property of the reference model; and the
fourth is that batch 12's cost model predicts the total to within 2 % and every individual row
wrongly.

## 1. What ran

| combination | kind | skill | Δ vs main | our CRPS | reference CRPS | seconds |
|---|---|---|---|---|---|---|
| `trainingWindow_from2004` | setup | +0.1266 | −0.0219 | 18.751 | 21.469 | 694 |
| `popColumn_backCast` | setup | +0.1347 | −0.0138 | 19.011 | 21.970 | 970 |
| **`main`** | — | **+0.1485** | — | 18.817 | 22.098 | — |
| `retrain_everySplit` | setup | +0.1651 | +0.0166 | 18.552 | 22.220 | 2 226 |
| `provinces_mergeVientiane` | setup | +0.1714 | +0.0229 | 19.006 | 22.937 | 1 148 |
| `provinces_reportingOnly` | setup | +0.1861 | +0.0376 | 18.843 | 23.150 | 836 |
| `aggregate_populationWeighted` | scoring | +0.2288 | +0.0803 | 28.577 | 37.055 | 13 |
| `aggregate_caseWeighted` | scoring | +0.2320 | +0.0835 | 88.484 | 115.216 | 14 |

From `analysis/05_stability/results/conclusions.csv` and `run_status.csv`. Raw CRPS is not
comparable down the scoring rows — a weighted mean of the same per-cell file is a different
summary, not a different analysis — which is exactly why the reported conclusion is a ratio.

**Six of the seven perturbations improve the reported skill score, and the main path sits near
the bottom of the range.** That is what a conservative main path looks like. It is also what a
systematically flattering set of alternatives would look like, and eight rows cannot tell those
apart. The sixteen remaining tier-1 rows are what would.

## 2. Three of the five setup rows move the reference, not us

| row | our pool moves | the reference moves |
|---|---|---|
| `provinces_reportingOnly` | +0.026 | **+1.052** |
| `provinces_mergeVientiane` | +0.189 | **+0.839** |
| `trainingWindow_from2004` | −0.066 | −0.629 |

Removing the two provinces that cannot be evaluated — LA-VI, which never reports, and LA-XN,
which stops in 2005 — leaves the 371 evaluated cells untouched and costs the reference more
than a standard error while costing our pool nothing measurable. EWARS pools across provinces
while fitting; our pool's members largely do not. **A setup choice that looks like data hygiene
is, for this comparison, a change to the opponent.**

This is the finding a single headline number hides completely, and it is an argument for the
project's decision to report a ratio with both terms visible rather than a raw score.

## 3. The scoring fork, and what a weighting hides

| | unweighted (`main`) | population | cases |
|---|---|---|---|
| pool CRPS | 18.817 | 28.577 | 88.484 |
| persistence CRPS | 24.879 | 33.744 | **86.598** |
| skill vs reference | +0.1485 | +0.2288 | +0.2320 |
| pool 10–90 coverage | 0.863 | 0.920 | **0.701** |
| cells with zero weight | 0 | 0 | **137 of 371** |
| effective sample (Kish) | 371 | 215 | **65** |
| share of weight in top decile of cells | — | 29.8 % | **62.3 %** |

From `02_aggregate/*/results/*/weighting_notes.json`.

**Case weighting is not a better summary than the unweighted mean; it has the opposite blind
spot.** It silences 37 % of the evaluated cells and shrinks the effective sample to 65, because
its weight is a function of the outcome. Reporting either alone would be a choice about which
months matter, made silently. That is precisely what this fork exists to expose, and it cost
fourteen seconds to find out.

**A known gap, recorded rather than fixed.** `03_compare` computes the paired difference, the
clustered standard errors and the split-level comparison from the *unweighted* per-cell file,
while the leaderboard's mean comes from whichever aggregation child ran. So on a weighted row
`conclusion.json` carries a re-weighted skill score beside an unweighted spread — the headline
is weighted and its uncertainty is not. Fixing it means teaching `compare_models.py` to read
`weights.csv`, including a weighted clustered standard error, which is a change to shared code
every combination runs. It is assigned to batch 14 and recorded in three places.

## 4. The seven children

Five under `02_setup`, two under `04_score/02_aggregate`. Each is a path the tree had named in
prose since batch 5 and carried as an empty node since batch 12.

- **`01_population/b_backCast`** — the snapshot scaled per year by an archived national series,
  0.7144 in 1998 to 0.8496 in 2009.
- **`02_trainingWindow/b_from2004`** — the calendar midpoint, deliberately *not* a zero-rate
  threshold: a cut fitted to the quantity the fork probes would let the alternative be tuned.
  The script asserts the cut leaves the evaluated span untouched rather than assuming it.
- **`03_provinces/b_reportingOnly`** — the two unevaluable provinces removed by a *rule* (no
  non-missing case inside the evaluated span) rather than by name.
- **`03_provinces/c_mergeVientiane`** — counts and population summed, the three climate columns
  **area-weighted** from the archived polygons, because they are ERA5-Land fields aggregated
  over the admin polygon and the mean over a union is the area-weighted mean of the parts.
  Population weighting was rejected as answering a different question.
- **`04_retrain/b_everySplit`** — `n_retrain` set to the scheme's own `n_splits`, read from the
  file `assemble_setup.py` reads it from rather than typed.
- **`02_aggregate/b_populationWeighted`, `c_caseWeighted`** — and `a_unweighted` was moved onto
  the same library, `04_score/scripts/lib/aggregate.py`, so the fork's three children differ in
  the weight and nothing else. The unweighted case is kept as its own code path inside it:
  weighting by ones and taking a mean are the same number in arithmetic and not always the same
  float, and this child produced the reported result. **Re-run, `results/main/` is
  byte-identical**, which is the check that the refactor moved no reported number.

**Batch 12's open question about `c_mergeVientiane` is answered.** It can be scored: it changes
the *content* of the capital's 24 cells, not the number of cells, because the province it
absorbs contributed none. The merged polygon is 78.1 % province, so the capital's 1998-01
rainfall goes from 0.075 to 0.251 mm/day and its mean temperature from 24.13 to 22.64 °C.

## 5. The population series, and a third wrong statement in the schema

`Archive/lao-population/` holds the World Bank's annual national series for Lao PDR
(`SP.POP.TOTL`, 1990–2021), fetched by a script, checksummed, and provenanced. An API cannot be
pinned by commit the way the dataset is, so the request fixes the year range, the response's own
`lastupdated` vintage is recorded, and **the analysis reads the archived file rather than the
API** — which is what makes the project reproduce from `Archive/` whatever the World Bank does
later.

**The archived population column does not have the level its schema claims.** It sums to
**4 961 076** across the eighteen provinces. The national total at the schema's stated reference
year of 2020 was **7 346 533**; the year whose national total is nearest the snapshot's is
**1995**. Either the column is not a 2020 level or it is a WorldPop total that does not
reconcile with the UN's, and the file cannot say which. This is the **third** statement in that
schema found not to describe the file — the row count and the rainfall unit were the first two.

The anchor is used as declared and the discrepancy recorded, because changing the reference year
multiplies every population by one constant, which a log offset absorbs. What the fork actually
probes is the *shape* of the trend, and that survives the doubt about its level.

**The series is national.** Every province is scaled by the same factor, so the fork does not
probe whether the capital grew faster than Phongsaly. The provincial censuses that would answer
that have no pinnable machine-readable release, and an input transcribed by hand from a PDF is
the manual step Rule 2 exists to keep out. The loss is stated where it bites.

## 6. What running found that planning could not

Batch 12 found two defects by planning and said so. These four were found by running, which is
the honest complement to that claim.

**`conclude.py` named a baseline as the project's model.** It resolved our reported model by
globbing for a `model_spec.json` under `results/$COMBO/` only. A combination that re-runs no
model of ours — the entire scoring class — has none, so it fell through to "the best-scoring
model of ours". Under case weighting that is **persistence**, and
`aggregate_caseWeighted/conclusion.json` reported a required baseline as our model with a skill
score computed for it. The file was internally consistent and wrong. The lookup now falls back
to `COMBO_BASE`, narrowly: only when *no* child of the family fork produced a spec under the
combination, so batch 14's separate family-row defect is not papered over. `results/main/` is
byte-identical after the change.

**The reference model crashes about once every hundred jobs.** `Prediction failed: Prediction
script did not create output file` — the R process exits without writing. A `02_setup` row asks
it for 36 jobs, so about a third of rows failed; `retrain_everySplit` asks for 64 and failed
twice. Four failures were observed, at repeats 1, 2 and twice at 4, in rows that succeeded on
other attempts. **It is a property of the model, not of any row.** Each repeat now gets up to
three attempts and `attempts_per_repeat` is recorded; the model is unseeded, so a retry replaces
a *crashed* draw rather than an unfavourable one, and recording the count is what keeps those
distinguishable. Both re-run rows needed one attempt per repeat, so no figure here rests on a
retry.

**One container was serving all four repeats.** Under `retrain_everySplit` that is 64 jobs in
one service; it slowed monotonically — 3.6, 5.6, then 7.5 minutes per repeat — and disconnected.
Each repeat now gets its own container, which is what the repeats were always meant to be.

**A failed re-run left a results directory that looked complete.** Three repeats from the new
run, one `.nc` from the old, and the *previous* run's `model_spec.json` and `run_cost.json`
beside them — a set whose per-cell reference mean spans two commits and two container
lifecycles, with nothing downstream able to detect it. `provinces_reportingOnly` was in that
state, with a `conclusion.json` describing inputs that had been partly overwritten. The node now
clears `results/$COMBO/` before writing. **This is the most dangerous thing this batch found**,
because it produces a wrong number that no check was looking for.

## 7. The cost model predicts the total and not the rows

| | planned | actual | ratio |
|---|---|---|---|
| all seven rows | 6 041 s | 5 901 s | **0.977** |
| `trainingWindow_from2004` | 1 202.9 s | 694 s | 0.577 |
| `retrain_everySplit` | 1 202.9 s | 2 226 s | **1.851** |

From `results/cost_planned_vs_actual.json`, which reads the manifest **at commit `2e186f6`** —
before any row ran — because `plan_manifest.py` re-costs from measured runs, so comparing the
current manifest to the current run record would compare a number to itself. Committing the
manifest before the run is what makes this checkable.

The frozen model gave all five setup rows the same figure, summing each row's parts as measured
under `main`. Nothing in it knew that a row can change how much work a part does, and
`retrain_everySplit` does exactly that. **The cut order within a kind is therefore ranked on a
constant and carries no information.** Nothing was cut, so nothing rests on it; the point is
that it could not have been relied on if it had been.

## 8. Decisions taken in this batch

Full table in the plan's §4b, dated 2026-08-29 (batch 13). The four worth arguing with:

| Decision | Basis |
|---|---|
| The reference's crashed repeats are retried rather than recorded as holes | The crash carries no information about the row, and two holes in a frozen manifest would have to be re-run in phase E anyway. Legitimate only because the model is unseeded and `attempts_per_repeat` is recorded |
| `plan_manifest.py` will not apply the tier-2 rule until every tier-1 row has been attempted | After batch 13 the rule would have filled group A and half of group S, selected two pairs instead of eight, and recorded a shortfall that is an artefact of the running order. `tier2_rule.md` is untouched and its sha256 unchanged: what changed is *when* a rule about the ranking of tier 1 may read a tier 1 |
| The back-cast is anchored where the schema says, not where the data suggests | Under a log offset the anchor is a constant the intercept absorbs, so the two anchors are the same analysis; using our own inference in place of the archive's statement would trade a recorded discrepancy for a silent correction |
| Climate columns are merged area-weighted, not population-weighted | They are area means already; a population-weighted merge answers "what climate did the average person experience", which is a different quantity inside the same column name |

## 9. Compliance for this batch

| Rule | What was done |
|---|---|
| 1 — track results | Nine new provenance records and twenty-eight appended sections, each naming its script sha256, inputs, environment, commit, alternatives-considered and agency. Every figure in this report is read from `conclusions.csv`, `run_status.csv`, `setup_spec.json`, `weighting_notes.json`, `merge_weights.csv` or `cost_planned_vs_actual.json`; the cost comparison was made a script **because** it was going to be a reported figure |
| 2 — no manual manipulation | No file produced by this batch was edited. The two scoring rows were re-concluded by re-running `conclude.py`, and the two failed rows by re-running the driver, never by patching a result |
| 3 — pinned environments | No change. One gap **recorded, not closed**: `image_pin()` records the reference image's digest rather than asserting it, and re-pulls `:latest` when absent, so an evicted image could substitute a different reference model silently. This is why Docker images were not pruned while the memory hypothesis was live |
| 4 — version control | Four commits: the children and driver fixes; the container and `conclude.py` fixes; the results and records; this report and the plan. Rows produced at `ce0eb34` except the two re-run at `7035515`, and each record says which |
| 5 — intermediates | Every stage of every row stored, plus three artifacts that did not exist before: `population_series.csv`, `merge_weights.csv`, and `weights.csv`/`weighting_notes.json` per weighted child |
| 6 — seeds | Our models seeded as before. **Persistence and climatology reproduced bit-identically across all five setup datasets** — 24.879 and 24.337 everywhere — which is a determinism signal the batch got for free, and correct: neither uses population, and merging a province that never reports cannot change the series they read |
| 7 — plots | The three figures were drawn under each row by the existing scripts, with plotted values and pre-aggregation values beside them. No new figure was written; the distribution of conclusions is batch 15's plot and it has eight of twenty-four rows |
| 8 — hierarchical report | Not due |
| 9 — claims | Answers written into all seven children's `claim.md`, into the five parent forks, and into `05_stability`. `/claims add` is batch 17's |
| 10 — release | Not due |
| `/annotate-criticality` | Appended at `02_setup` and `04_score` for the new artifacts, with sizes measured rather than estimated |
| `/validate invariants` | **All invariants hold.** The `provenance` check failed on 377 artifacts first and was satisfied by writing records, not by weakening it |

## 10. What went wrong, kept

**I diagnosed the second round of failures as host memory pressure, and was wrong.** The
evidence was `vm_stat` showing 67 MB free during a run, plus a row that had previously
succeeded failing 22 seconds in. The retry disproved it: the same row then ran three clean
repeats and died in the fourth, on an idle machine, 602 seconds in. The correct reading — an
intermittent per-job crash at about 1 % — only became visible after counting failures across
every attempt. A plausible mechanism and one confirming observation are not a diagnosis.

**`node.py rebuild` silently re-added the driver to `run.sh`.** Adding
`compare_planned_cost.py` to the stability node meant regenerating its `run.sh`, and the
generator lists every script in `scripts/` alphabetically — which put `run_manifest.py` back
into the file batch 12 had deliberately kept it out of, and reordered the other four out of
dependency order. Caught by reading the generated file. The block now carries a warning that
says what to do when it happens again, because it will.

**The first driver run was killed mid-row** by the session, not by anything in the analysis, and
the second was launched detached for that reason. `run_status.csv` is written once at the end of
an invocation, so a killed run leaves no record of itself — which is how the mixed reference
directory went unnoticed for an hour.

## 11. What is still unknown

1. **Whether the main path's position near the bottom of the range is conservatism or
   flattery.** Six of seven perturbations improve the score. Sixteen tier-1 rows remain and
   they are the ones that move our own model rather than the dataset.
2. **Whether the weighted rows' paired statistics matter.** Their spread is currently
   unweighted, so nothing yet says whether the +0.08 skill move is large against a weighted
   standard error. Batch 14.
3. **Whether the reference's 1 % crash rate is stable.** It was measured over roughly 400 jobs
   in one day on one machine. If it is higher on a slower machine, phase E's holdout run — which
   is the one that must not be repeated — is the place it would hurt most.
4. **Whether `retrain_everySplit` belongs in the holdout manifest at all.** It costs the
   reference eight times the compute for a forecast the reference was already making, and it is
   the row most likely to fail. It stays, because the manifest is frozen and dropping a row
   after seeing its number is exactly what freezing forbids.

## 12. For the human

- **The conclusion survives every dataset choice we identified, and moves most under the
  cheapest one.** The five `02_setup` forks span less than the reference's own re-run noise;
  re-weighting the mean moves it four times as much.
- **Under case weighting, persistence beats our reported model.** I would not report the pool
  without that sentence beside it. It does not overturn the headline — the headline is defined
  against the unweighted mean, which is Chap's own — but it is the sharpest thing the stability
  work has produced so far.
- **A wrong number was produced, sat on disk, and was caught by reading it.** The case-weighted
  row reported persistence as "our model". The check that found it was me looking at the output,
  not any invariant, and the fix is in shared code that batch 14 will touch again.
- **I made a wrong diagnosis under time pressure and corrected it.** It is in §10 rather than
  smoothed out, because how an agentic system behaves when its first explanation is wrong is
  part of what this case is meant to show.
- **One thing I did not fix and think you should know about**: the reference image's digest is
  recorded rather than asserted, so an evicted image could be replaced by a different `latest`
  without anything failing. It is a small change and it touches the model the whole project is
  measured against, which is why I have not made it unasked.
