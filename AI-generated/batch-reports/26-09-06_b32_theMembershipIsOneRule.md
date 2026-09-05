# Batch 32 — the pool's membership is one rule, not two

Generated from [[26-08-22_dengueForecastingCase]] — iteration 32

**State: done — produced.** The weighting child of candidate 3 no longer computes what the
pool will contain. It and `prepare_members.py` both call
`analysis/03_models/scripts/lib/pool_shape.py`, so the specification registered before the
pool runs and the pool that runs are one answer rather than two that agreed until batch 22
and not afterwards.

**Ninety-four documents rewritten, and nothing computed moved.** All 47
`model_option_spec.json` under `01_weighting/a_equal` and all 47 `candidate_spec.json` that
embed one as their `stages[0]`, produced by running the tree's own two steps under each
combination. **80 had the membership corrected; 14 already named the right four.** All 47
`model_configuration.yaml` are byte-identical to their committed versions, so
`configuration_sha256` — what `chap eval` was pointed at — is unchanged and **no model had to
be evaluated again**. `members.json`, whose digest the pool's own configuration carries, is
byte-identical too.

**The file contradicted itself, and the half that was right is the prediction.** Beneath a
premise saying *six members, two-thirds of the mass on required baselines* stood the
registered prediction that an equally weighted pool "puts half its mass on the two required
baselines" — which is four members with two baselines, the pool that ran. Nothing in the
project had read the two against each other.

**Fifth instance of the fork-blindness family, and the last one open.** Batch 33 — create the
remote and push — has no blocker left in the tree.

---

## 1. The defect, stated against a machine that never ran this repository

The pool is a linear opinion pool over the models the project already has. With equal weights
its *specification is its membership*: the member count is the weight each member carries, and
the share of members that are the plan's required baselines is the share of the pool's mass
sitting on the two worst models on the board. That statement is registered before the pool
runs, because a prediction registered afterwards is not one.

The child built it by globbing for Chap contract directories and counting them.
`prepare_members.py`, a few seconds later in the same node, built the pool by resolving every
alternatives fork above a contract to the child the combination takes. **Batch 22 gave the
persistence baseline and the climatology baseline a second published construction each**, and
from that day the two rules gave different answers.

The clean-room run of 2026-09-05 — a checkout that had never seen this machine — printed both,
three lines apart:

```
weighting/a_equal[main]: … 6 members at 0.167 each, 4 of them required baselines
  a_hierNB: configuration already assembled under 'main'
  b_boosted: configuration already assembled under 'main'
ensemble members[main]: 4 — persistence, climatology, hier_nb, boosted; … not on this
  combination's path: [b_negBinomialFloor, b_frozenWindow]
```

| | registered | ran |
|---|---|---|
| members | 6 | **4** |
| weight each | 0.167 | **0.250** |
| on the required baselines | 0.667 | **0.500** |

**40 of 47 combinations said six.** The seven that said four are the ones whose specification
was last written before batch 22 — `main` among them — so the reported analysis's own file was
right by the date on it and not by anything checking it.

**No score moved, then or now.** `user_option_values` is `{"weighting": "equal"}` and carries
no count; `model_configuration.yaml` is built from that, the covariates and the seed. What was
wrong is the premise a registered prediction rests on, and a main-path step that rewrites a
committed file on every run **for a reason that is not the unseeded reference** — which is the
property `/validate cleanroom` exists to test.

## 2. The rule, in one place

`03_models/scripts/lib/pool_shape.py` holds what the pool contains: every Chap contract
directory under `03_models` except the pool's own, with every alternatives fork above one
resolved to the child this combination takes, and the family fork excepted because pooling its
children is what the node is for. `prepare_members.py`'s three functions moved there unchanged;
`choose_weighting.py` calls the same `selection()`.

**A fork is resolved from what ran, not from the tree alone.** It could have been read off
`claim.md`'s main path and never touched a result, which would have made the membership a pure
function of the checkout. It is not done that way because the pool must contain the model the
combination actually scored: under `persistence_negBinomialFloor` the member is
`b_negBinomialFloor`, and no property of the tree says so — the combination does.

That the lookup reads directories is the thing batch 28 removed one node over, so it is checked
rather than asserted. **The rule's answer is identical, for all 47 combinations, to the
membership `prepare_members.py` recorded when each of them ran** — 41 against a committed
`member_selection.json`, the other six against the `members.json` of pool runs that pre-date
that file — **and identical whether or not `COMBO_BASE` is set.** What `COMBO_BASE` moves is
the *sentence explaining* how a fork resolved, which is why no such sentence is registered in
the premise. A premise that changed when an unrelated variable was set would be the same class
of defect one field over.

## 3. What the premise says now

`members`, `member_count`, `weight_each_member_will_carry`,
`required_baselines_among_them` and `share_of_the_pool_on_the_required_baselines` are as
before, and now correct. One field is added and two are rewritten:

- **`contracts_not_on_this_combinations_path`** — the constructions the glob found and this
  combination did not take. A premise that says only what is in the pool cannot be read against
  what the tree holds, and reading those two against each other is what would have caught this
  in a day rather than in ten;
- **`source`** describes the rule that is there rather than the glob that is gone;
- **`nothing_downstream_is_read`** is narrowed honestly. Still no score, no leaderboard, no
  evaluation — resolving a fork reads the `model_spec.json` of models that run *before* this
  node, and the fork's own main path where none has run.

The run log now says what the pool's own line says, with the same two exclusions.

## 4. Two defences, because an imported rule holds only while both keep importing it

**In the run.** `prepare_members.py` refuses to build a pool whose registered premise names
other members, and refuses **before writing anything**. Within one run the two now come from
one call and cannot differ; what this catches is the way they actually did differ — a
*committed* specification, written when the tree had a different shape, describing a pool that
is not the one about to run. Only a specification found under this combination itself is
checked: one reached through `COMBO_BASE` was written for the base combination's pool, and a
combination that moved a baseline fork has a different membership by design.

**On the committed files.** `/validate invariants` gains an eleventh check, `pool`, in three
clauses ordered by how little each needs to know:

1. **no two members under one alternatives fork.** Two constructions of one baseline are one
   member, whichever this combination takes. This needs only the tree, so it holds for a
   combination that has never been run;
2. **the premise names the members `prepare_members.py` recorded** — `member_selection.json`
   where there is one, `members.json` for the six pool runs that pre-date that file, so no
   combination that has run is exempt;
3. **the copy embedded in `candidate_spec.json` is the child's own.** The family assembler
   copies the whole specification into `stages`, so a corrected premise that was not
   re-assembled leaves the contradiction one file further out — which is why this batch
   rewrote 94 documents and not 47.

## 5. The defence, built against the clean-room run's own output

Six situations, on the live tree, each restored and checked by digest, with `analysis/` left
clean by git's own account. **All six pass.** →
`AI-generated/validation/26-09-06_premiseDefence.json`

| | situation | required | result |
|---|---|---|---|
| 1 | **the clean-room's own two lines** | the fixed child prints what the cold run's pool line already said | 6 → **4**, same two exclusions |
| 2 | the record batch 22 left | four findings: the fork clause on both baseline forks, the record clause, the embedded clause | 4 |
| 3 | the structural clause alone, records out of reach | the fork clause still fires | 2 |
| 4 | a stale embedded copy | only the third clause | 1 |
| 5 | the runtime guard | exit non-zero, nothing written | exit 1, `members.json` and `member_selection.json` untouched |
| 6 | the tree as it stands | nothing | nothing |

Situation 1 is the one that matters most, and it is the only one whose evidence was produced
by a machine that had never run this repository. Situation 5 is staged on `covariates_rich`
rather than on `main`, because `main` is one of the seven whose specification pre-dates batch
22 and named the right four all along — the guard has nothing to catch there, which is a fact
about when that file was last written and not about the guard.

## 6. What the rewrite changed, measured

`AI-internal/useful-scripts/rewrite_weighting_premise.py` runs the tree's own two steps under
each of the 47 combinations — never editing a file — then flattens both versions of every
document to their leaves and classifies each differing key. →
`26-09-06_weightingPremiseRewrite.json`

| | |
|---|---|
| combinations | 47 |
| documents | 94 |
| changed in the premise only | **94** |
| of those, membership corrected | **80** (40 combinations × 2 files) |
| of those, added field and reworded source only | 14 (7 combinations × 2 files) |
| `model_configuration.yaml` byte-identical to `HEAD` | **47 of 47** |
| fields that should not have moved | **0** |
| documents reproduced byte-identically on a second pass | **102 of 102** |

`prepare_members.py` is deliberately not among the steps re-run. Its output is unchanged by
this batch — verified by digest under `main` before and after — and `members.json`'s digest is
carried inside the pool's own configuration, so rewriting that file at all is a thing to avoid
rather than a thing to check afterwards.

## 7. What was decided, and by whom

- **Lifting the rule rather than fixing the count** — `agent-autonomous`. A corrected glob
  would have been two rules that happened to agree, which is what the last ten days were.
- **Resolving forks from results rather than from `claim.md` alone** — `agent-autonomous`,
  and against the instinct batch 28 left. The pool must name the model the combination scored;
  the disk-dependence that instinct guards against is measured here and is nil.
- **Not recording how each fork resolved** — `agent-autonomous`. That sentence moves with
  `COMBO_BASE`; the membership does not.
- **Re-assembling the 47 `candidate_spec.json`** — `agent-autonomous`. `check_pool.py` reads
  the registered prediction from the assembled copy, so leaving it stale would have left the
  contradiction where it is read.
- **Not re-running `/validate cleanroom`** — `agent-autonomous`, and the one open question
  this batch hands on. See §9.

## 8. The ten rules

| Rule | This batch |
|---|---|
| 1 — track results | Sections appended to `choose_weighting.md`, `prepare_members.md` and the pool's `assemble_candidate_config.md`, each naming `pool_shape.py` with its digest; and to `AI-generated/validation/provenance.md` for both artefacts |
| 2 — no manual manipulation | Nothing edited by hand. All 94 documents produced by running the tree's own steps; the defence restores every staged file by digest |
| 3 — environment | Unchanged; the two analysis steps ran under `environment/chapenv` |
| 4 — version control | Four commits, before and after the run. No change to `AGENTS.md`, `CLAUDE.md` or `.claude/` |
| 5 — intermediates | The rewrite's key-by-key comparison and the defence's six situations are stored as JSON, not read off a diff |
| 6 — seeds | Untouched; the pool's component seed is derived from its node path and is byte-identical in all 47 configurations |
| 7 — plots | None produced |
| 8 — hierarchical report | Not rebuilt; no reported value moved |
| 9 — claims | No claim moves. No claim cited the member count |
| 10 — release | Batch 33's only blocker in the tree is removed |
| `/validate invariants` | Passes, **all eleven** |

## 9. What is next, and the question that goes with it

**Batch 33** — create the remote and push. Both human answers batch 19 waited on are recorded,
and this batch removes the defect that stopped it.

**One question belongs to whoever opens it.** Batch 31's clean-room run, and batch 19's after
it, ran on a tree that wrote the wrong premise; 94 committed documents have changed since. The
case for not re-running is that the change is provably score-free — 47 byte-identical
configurations, zero fields that should not have moved, and a second pass reproducing 102
documents byte for byte — so a further 15 hours would confirm documents that are deterministic
functions of the checkout. The case for re-running is the project's own standard, which is that
a release must not claim more than its checks support, and the last full-tree check was run on
a tree that no longer exists. **It is a budget decision, and it is the human's.**

## 10. Files

**Added**

- `analysis/03_models/scripts/lib/pool_shape.py` — what the pool contains, decided once.
- `AI-internal/useful-scripts/rewrite_weighting_premise.py` — the rewrite and its measurement.
- `AI-internal/useful-scripts/check_premise_defence.py` — six situations put to both defences.
- `AI-generated/validation/26-09-06_weightingPremiseRewrite.json`,
  `26-09-06_premiseDefence.json` — what each found.

**Changed**

- `analysis/03_models/03_candidate/c_ensemble/01_weighting/a_equal/scripts/choose_weighting.py`
  — the membership comes from the library; one field added, two reworded.
- `analysis/03_models/03_candidate/c_ensemble/scripts/prepare_members.py` — three functions
  lifted out, `check_the_registered_premise` added. Output byte-identical.
- `AI-internal/useful-scripts/check_invariants.py` — the `pool` check.
- 47 `model_option_spec.json` and 47 `candidate_spec.json`, re-produced.
- Three provenance records, `AI-generated/validation/provenance.md`, and the READMEs of
  `AI-internal/useful-scripts/` and `AI-generated/validation/` — sections appended.

**Unchanged, and checked to be so**

- All 47 `model_configuration.yaml`, and with them every `configuration_sha256`.
- `members.json` and `member_selection.json`, under every combination.
- Every evaluation, every score, every reported number.
