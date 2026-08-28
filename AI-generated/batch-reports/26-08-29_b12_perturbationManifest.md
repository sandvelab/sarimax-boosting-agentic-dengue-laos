# Batch 12 — `/perturb plan`: the stability node and the perturbation manifest

Generated from [[26-08-22_dengueForecastingCase]] — iteration 12

**Phase D · Status: done — produced · Executed 2026-08-29**

---

The batch that opens phase D. `analysis/05_stability` exists, the perturbation manifest is
written and committed before any of it has run, and the nine paths not taken that the tree
had only described in prose are now nodes in it.

**Seventeen forks, not ten.** Batch 5 wrote the inventory by hand. The planner reads it off
the tree, and phase C had added five forks while building the candidates — plus two baseline
forks that were never on the hand-written list, one of which the plan's own phase D names.
That gap is the argument for computing it, and `/validate invariants` now fails if the
manifest and the tree ever disagree again.

**Twenty-four tier-1 combinations, eight tier-2 pairs, 124 minutes on development and 75 on
the holdout** against a 12-hour budget. Nothing is cut, and the cut order is recorded against
the day something is.

Three findings matter more than the counts.

**Compute is not what binds, and it is not close — 89 of the 124 development minutes are the
reference model.** Five setup rows, four unseeded repeats each, an amd64 image under
emulation, for the one model the plan forbids perturbing. Every model of ours, across all
twenty-three perturbations, costs 21 minutes together.

**Seven of the ten judgment calls phase D exists to perturb were sentences rather than
nodes.** Four `02_setup` forks, the scoring fork and both baseline forks each had exactly one
child. Their `claim.md` files said the sibling "is not built yet"; the tree did not carry it,
so there was nothing for a manifest to enumerate and nothing for `/validate invariants` to
notice. They are nodes now, with claims, scaffolded and unbuilt.

**Planning found two defects and twelve stale directories that running would have found
later and more expensively.** No row has been run to discover them.

## 1. What the tree looks like now

```
analysis/
├── 02_setup/                        four forks, each with a second child            NEW
│   ├── 01_population/    [-> a_static]        + b_backCast          not built  NEW
│   ├── 02_trainingWindow/[-> a_from1998]      + b_from2004          not built  NEW
│   ├── 03_provinces/     [-> a_chapFilter]    + b_reportingOnly     not built  NEW
│   │                                          + c_mergeVientiane    not built  NEW
│   └── 04_retrain/       [-> a_once]          + b_everySplit        not built  NEW
├── 03_models/01_baselines/
│   ├── 01_persistence/   [-> a_empiricalChange] + b_negBinomialFloor  not built NEW
│   └── 02_climatology/   [-> a_expandingWindow] + b_frozenWindow      not built NEW
├── 04_score/02_aggregate/[-> a_unweighted]    + b_populationWeighted not built NEW
│                                              + c_caseWeighted      not built  NEW
└── 05_stability/         "How far does the conclusion survive the alternatives?"  NEW
    ├── scripts/lib/inventory.py     the fork inventory, read off the tree
    ├── scripts/measure_step_costs.py
    ├── scripts/plan_manifest.py     forks.csv · manifest.csv · manifest_notes.json
    │                                · tier2_rule.md
    ├── scripts/run_manifest.py      the driver — not in run.sh until batch 15
    └── scripts/collect_conclusions.py  conclusions.csv, absences included
```

`05_stability` is a child of the root, so `analysis/run.sh` calls it. What it calls today is
the planner and the collector; the driver joins in batch 15, and §5 says why.

## 2. The fork inventory

Read from the tree by `lib/inventory.py`, which walks `analysis/` for alternatives nodes.
`results/forks.csv` is the file; this is its shape.

| Kind | Where | Forks | Non-main children | What re-runs |
|---|---|---|---|---|
| `setup` | `02_setup` | 4 | 5 | every model, the reference four times |
| `scoring` | `04_score/02_aggregate` | 1 | 2 | nothing — the stored per-cell scores are re-aggregated |
| `baseline` | `03_models/01_baselines` | 2 | 2 | that baseline, **and our reported model** |
| `family` | `03_models/03_candidate` | 1 | 2 | our model only |
| `candidate` | under a family | 9 | 12 | our model only |
| | | **17** | **23** | |

**The kind is a property of where the fork sits, not a convention anyone applies.** That was
batch 5's design and it holds: a fork in the wrong subtree would produce a comparison in
which one side moved and the other did not, and the tree makes that visible as a
misplacement.

**One kind changed meaning without anyone moving a fork.** Batch 5 costed the persistence
fork as moving one leaderboard row. Batch 11's pool takes both required baselines as members,
so how persistence wraps a distribution around its point forecast is now a choice **inside
the model this project reports**. The plan's phase-D text has been corrected to say so. It is
the clearest instance in this project of a fork's reach being a property of the tree at the
moment you run it rather than of the fork.

**Two stage names are stated rather than derived**, in `STAGE_OVERRIDE` with the reason: the
family fork keeps `family_*` because thirteen files already point at those names, and
`02_setup/01_population` becomes `popColumn_*` because `population_*` is taken by
`a_hierNB/03_population` — the two questions batch 5 warned were different. `assert_unique_names`
fails the planner if any two forks ever claim one name, which is what actually protects the
scheme.

## 3. The manifest

`results/manifest.csv`, 33 rows.

**Tier 1 — 24 rows.** The main path, plus every one of the 23 non-main children taken alone.
Batch 5 said 20; its own components sum to 17. The planner counts from the tree.

**Tier 2 — 8 rows, and the rule is fixed and hashed now.** `results/tier2_rule.md`, sha256 in
`manifest_notes.json`: rank tier-1 rows by |Δ skill| from the main path, take the top two
`setup` rows, the top two of the three kinds that move our model, and the top `scoring` row,
and form every cross-group pair — 2×2 + 2×1 + 2×1 = 8. Batch 5 fixed the number and a phrase
whose arithmetic only closes under the cross-group reading; that reading is fixed here, with
the count it was chosen to preserve. The eight slots are empty and say so; running the planner
again once tier 1 has conclusions fills them from the file rather than from anyone's reading
of it.

**Tier 0 — 1 row.** `family_ensemble`: the reported model run under its own name so the three
families could be compared each at its own main path. Same analysis as `main`, perturbs
nothing, and it is in the register because §6's new invariant requires the register to be
complete. It was found by that invariant on its first run.

**Tier 2 is not cut, and two findings say so.** Batch 9 measured three fork effects
overstating their combined worth; batch 21 measured a fourth whose sign reverses when a
second fork moves. One-at-a-time effects do not compose on this problem, twice
demonstrated.

## 4. What it costs, measured

| | Development | Holdout (4 splits) |
|---|---|---|
| One setup row — dataset, four models, reference ×4, scores | 1203 s | 606 s |
| One baseline row — that baseline, the pool, scores | 98–101 s | 55–56 s |
| One family or candidate row — the pool, scores | 70–154 s | 41–82 s |
| One scoring row — re-aggregation only | 11 s | 11 s |
| **Tier 1, 24 rows** | **124 min** | **75 min** |
| Budget, both datasets | 12 h | |

**Nothing here is arithmetic on two numbers, which is what batch 5's table was and said it
was.** The model terms are each model's own `run_cost.json` — nineteen measured backtests.
The setup, scoring and conclusion steps are timed by `measure_step_costs.py`, which re-runs
them under `COMBO=main` and asks git whether anything changed: a step that is not idempotent
cannot be timed by re-running it, and the check is what says so rather than a comment. A fork
inside a member of the pool gets a fourth term, the member's own measured delta — which is
why `fitTime_refitAtPredict` is costed at 154 s and not 70.

**Where the time actually goes.**

| | Minutes of the 124 |
|---|---|
| The reference model, 5 setup rows × 4 unseeded repeats | **89** |
| Everything else on the setup rows | 11 |
| All 14 candidate, family and baseline rows | 24 |
| Both scoring rows | 0.4 |

The reference is re-scored four times wherever it is re-scored because it is unseeded and the
conclusion divides by it; batch 4 measured its re-run spread at sd 0.196 CRPS, and an
unaveraged denominator would put a wobble on every combination comparable to the fork effects
the manifest exists to measure. So the dominant cost of phase D is not our models and not the
perturbations: it is holding the denominator still.

**Storage.** 575 MB for tier 1 on development, 1.15 GB across both datasets, against 234 MB
of stored results today — measured part by part in `manifest_notes.json["storage"]`, not
assumed. Annotated in `05_stability/criticality.md` and, for the files it lands on, in an
addendum at `03_models`. One `eval.nc` is 9.4 MB and the per-cell CSV derived from it is
0.18 MB, so the prune target is unambiguous — with the standing exception that the
reference's evaluations cannot be regenerated at all, because the model is unseeded.

**Ranked, but not selected.** Rows are ordered by reach, then by what phase C measured that
fork to be worth, then cheapest first. The prior is read from the fork sweeps and **only from
a sweep whose recorded base configuration still matches the family's current one** — the same
test `candidate_fork_sweep.py` applies to itself, which correctly excluded
`round1_batch8Defaults` and admitted the other four. With the whole manifest inside budget the
order decides what runs first, not what runs.

## 5. What planning found that running would have found later

**Nine of twenty-four rows have no scripts.** `02_setup`'s four forks, the scoring fork and
both baseline forks each had one child. Their claims said the sibling was "not built yet",
which is true and was invisible to every check in the repository, because a fork with one
child is a well-formed alternatives node. Creating them costs nothing and changes three
things: the paths not taken are in the tree as `/perturb` asks; the manifest enumerates them;
and `run_manifest.py --dry-run` prints the ordered step list each one has to satisfy, so
batches 13 and 22 work to a specification written by the driver that will call them rather
than to a paragraph in a report.

**Twelve rows have results on disk that their row would replace.** `observation_negBinomial`
meant "our model is candidate 1 with a plain negative binomial" in phase C. It means "our
model is the pool, whose candidate-1 member has a plain negative binomial" now. Same name,
different analysis. Which is which is not guessed from the name: `01_collect` writes a
`models.csv` naming every model it scored, and the planner compares that against what the row
would produce. `family_hierNB` and `weighting_crpsWeighted` correctly come back clean;
`family_boosted` does not, because batch 10 ran candidate 1 alongside candidate 2 under it.
Batch 14 removes them before re-running, as batch 11 removed candidate 1's `results/main/`,
with git as the witness.

**Two defects block every built candidate and family row.**

*The pool's member assembler runs too much.* `prepare_members.ensure_configuration` runs
**every** fork's main-path child when a member family has no configuration under the running
combination. A combination that has already run a sibling of one of those forks then leaves
two children of one fork with results, and `assemble_candidate_config.py` fails by design —
"expected exactly one child". The fix is to run a fork's main child only when no child of it
has results under this combination, which is the `resolve_glob` semantics the rest of the
tree already uses.

*The root resolves our model from a file that does not move with the combination.*
`conclude.py` reads `main-path` out of `03_candidate/claim.md`. Under `family_hierNB` the
reported model is candidate 1, but the claim file still says `c_ensemble`, so the script would
find no `model_spec.json`, fall back to "the best-scoring model of ours" and write
`candidate_exists: false` on a row where a candidate certainly exists. The tree's own README
already states the contract this violates: the next stage finds a fork's output "by searching
for the one child of that fork with results under this combination, never by naming a child".

Both are batch 14's, alongside the assembler lift batch 11 deferred there — the batch that
re-runs those rows anyway, so regenerating their provenance costs nothing extra. Neither is
fixed here: changing `prepare_members.py` would change its sha256, which is in the provenance
of three combinations' results.

## 6. A new invariant, and what it caught

`/validate invariants` gains `combos`, in two parts.

**Every `results/<name>/` directory is a combination the manifest names.** A scratch run, a
renamed combination, a typo that created a second directory beside the real one — each is a
set of numbers in the repository and not in the reported distribution.

**The manifest's tier-1 rows agree exactly with the tree's non-main children.** A fork added
after the manifest was written is a reasonable alternative the stability run does not know
about, which is the silent absence `AGENTS.md` §4 forbids. The planner keeps them in step;
the check is what says so when it has not been re-run.

**It failed on its first run**, on fifteen `family_ensemble` directories. The fix was to make
the manifest complete — tier 0 — rather than to exempt the directory, which is what batch 5
asked for in those words.

One change to `check_provenance` comes with it: a record may name an artefact by its
combination-invariant path, `results/$COMBO/eval.nc`, and cover every combination of it. One
script produces that artefact under every combination, from the same inputs, by the same
invocation, and each file records its own combination in a `combo` field — so the invariant
path is what the record of a combination-parameterised step actually says, and thirty-two
copies of it would be thirty-two things to keep in step. **It is not an exemption**: some
record still has to name the artefact, and the placeholder satisfies only files whose
combination the manifest names, which the first check is what makes closed. The two checks
close over each other.

## 7. The budget, and the one number the human may want to move

No compute budget had ever been fixed in figures: the plan and `readme-at-start.md` say only
that compute does not bind. The manifest needs a line to record a cut against, so this batch
sets one — **12 wall-clock hours for the manifest run twice** — as roughly one unattended
overnight run on this machine. It is four times the estimate, so it constrains nothing today.

The cut order, recorded now rather than decided under pressure later:

1. **Tier 2, from the bottom of the rank order upward.** Pairs are the least informative rows
   per second and the manifest is designed so they go first.
2. **The reference's four repeats on tier-2 setup rows, reduced to two.** This doubles the
   noise on those rows' denominators and would be recorded as such on the row.
3. **Tier-1 rows below the rank line, in rank order, never by kind.** Cutting a kind would
   answer a different question; cutting the tail answers the same question less completely.

## 8. Decisions taken in this batch

The full table is in the plan's §4b, dated 2026-08-29. The four that would be worth arguing
with:

| Decision | Basis |
|---|---|
| The inventory is computed from the tree rather than listed | The hand-written list was seven forks short and the same omission would recur. A missing fork is now a missing node, which a check can see |
| The nine unbuilt children are created as nodes now, in the planning batch | `/perturb` prefers a judgment call to be an alternatives node so the path not taken survives. Creating them is what makes the manifest enumerable and gives batches 13 and 22 a machine-written specification |
| Batch 22 is appended between 13 and 14 | Batch 13 already has seven children to write and five twenty-minute rows to run; the two baseline children are new Chap-contract models that move the reported model, not a footnote on someone else's batch |
| The driver is written and deliberately kept out of `run.sh` | Twenty-one of twenty-four rows cannot yet produce what their row says. It joins in batch 15, recorded in three places so it cannot be forgotten |

## 9. Compliance for this batch

| Rule | What was done |
|---|---|
| 1 — track results | Four provenance records at the new node, one per script, each naming its sha256, its inputs, its environment, its commit, its alternatives-considered and its agency. Every figure in this report is read from `manifest.csv`, `manifest_notes.json`, `forks.csv`, `step_costs.json` or `conclusions_notes.json`; none was carried out of terminal output |
| 2 — no manual manipulation | No file produced by this batch was edited. The nine new nodes were made by `node.py new`, and the only change to their parents' `run.sh` is the generated `# Not taken:` comment — the main path line is untouched, which is what keeps `analysis/run.sh` reproducing the same analysis it did yesterday |
| 3 — pinned environments | No change. Every script here runs under `environment/chapenv`, the project main environment |
| 4 — version control | Two commits: the node, the manifest and the invariant extension; then the records, annotations and this report. `check_invariants.py` and the plan are both part of the method and are versioned in the same commits as the code they govern |
| 5 — intermediates | Ten files at the new node, each one a stage rather than a summary: the measured step costs, the fork inventory, the manifest, its notes, the tier-2 rule, the driver's status and log, the conclusions table and its notes |
| 6 — seeds | No surface. The manifest is enumerated, never sampled, and the driver draws nothing of its own — every model it invokes seeds itself through `analysis/scripts/lib/project_seed.py` |
| 7 — plots | No figure was drawn. The distribution of conclusions is what phase D plots, and it has one row |
| 8 — hierarchical report | Not due |
| 9 — claims | An answer written into `05_stability/claim.md`, citing the files each figure comes from. The nine new children have claims and **no** answers, which is correct: a node that has not run has yielded nothing, and an answer written in advance of the analysis is the thing this repository is built to prevent. `/claims add` is batch 17's |
| 10 — release | Not due |
| `/annotate-criticality` | `05_stability/criticality.md` written, covering the node's own outputs **and** the storage the manifest implies, from measured parts; an addendum at `03_models` for the ~1 GB of NetCDF the manifest will land there |
| `/validate invariants` | **All invariants hold**, including the new `combos` check, which failed on its first run and was satisfied rather than weakened |

## 10. What went wrong, kept

**The cost model was wrong three times before it was right, and each error was visible in the
file.** The main path's holdout cost came out at 5.6 s because the estimator scaled a
development cost of 0.3 s that stood for "already computed" — on the held-out year nothing is
computed and the main path is the most expensive row there. The member-delta term silently did
nothing, because it looked for candidate 1's cost under a combination it named
`family_a_hierNB` when the combination is `family_hierNB`; every candidate row therefore
carried the pool's flat 70 s. And the first stale-directory test flagged rows by kind, which
put `weighting_crpsWeighted` on the list although it had been run around the pool and is
current. All three were caught by reading the produced table against what it should say —
which is an argument for the manifest being a file rather than a paragraph.

**`family_ensemble` was invisible until a check looked for it.** Fifteen directories holding a
real analysis with no row in any register. It had been there since batch 11 and nothing in the
repository could have said so.

## 11. What is still unknown

1. **Whether the nine unbuilt children are as cheap as they look.** Eight are filters and
   flags. `popColumn_backCast` needs an annual Lao population series the repository does not
   hold, so batch 13 has to find, archive and provenance an external source before that row
   can run — recorded in `manifest_notes.json` under `not_costed`, because it is an
   acquisition rather than a compute cost.
2. **Whether `c_mergeVientiane` can be scored at all.** It changes the cell set, so its raw
   CRPS is not comparable with any other row's. The conclusion is a ratio to the reference on
   whatever cells that child produced, which is exactly why batch 5 argued for a relative
   headline — but the reference has never been run on a merged map and may filter differently.
3. **Whether the pool survives having two persistence members.** `prepare_members.py` finds
   its members by globbing for `MLproject` under `03_models`. Once `b_negBinomialFloor` has a
   model directory, the glob finds two persistence models and the pool would take both. Batch
   22 has to teach the glob to respect each fork's main path, and it is on that batch's face
   rather than waiting to be discovered.
4. **How much tier 2 will cost.** Six of its eight pairs will probably involve a setup fork,
   which would put it near two hours on development — comparable to all of tier 1. The
   manifest leaves the figure unresolved rather than guessing, because the pairs are chosen
   from tier 1's results.

## 12. For the human

- **Phase D has a manifest, and it is committed before anything in it has run.** That is the
  property the whole phase rests on, and the commit date is the evidence.
- **Compute is not the constraint and it is not close.** 3.3 hours of tier 1 across both
  datasets, of which 1.5 hours is re-running the reference model four times on each of five
  setup rows. I set a 12-hour budget so that the cut order has something to be a cut against;
  it is a number I chose and you can move it, and nothing currently sits near it.
- **The plan's fork list was seven short and I have replaced it with a script.** Five forks
  phase C added, and two baseline forks the hand-written list omitted although your phase D
  names one of them. I have corrected the plan's phase-D text rather than leaving the list
  and the tree disagreeing.
- **The batch that changed most about phase D is batch 11, not this one.** Promoting the pool
  put both required baselines inside the reported model, so the baseline forks now move our
  model too, and a perturbation of candidate 1's observation model now perturbs a member of
  the model we report rather than a model we demoted. That makes tier 1 more informative than
  it was designed to be, and it is why twelve combination directories from phase C now
  describe a different analysis from the one their name will mean.
- **I added batch 22 to the ledger**, between 13 and 14: the two baseline forks' children are
  new Chap-contract models and they move the reported model, so they need a batch rather than
  a corner of one. Say if you would rather they went into 13.
- **Nothing has been run.** One row — the main path — went through the driver to exercise it,
  and its conclusion came back byte-identical.
