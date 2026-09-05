# Provenance — the pool's weights, equal

```
result:              main/model_option_spec.json
                     family_ensemble/model_option_spec.json
script:              scripts/choose_weighting.py
                     sha256:ffeee4029729af7cf4fdff9f93c48804c61b37fe15dfb739f0be8c20293199b4
invocation:          "$PYTHON" scripts/choose_weighting.py, with COMBO set
inputs:              analysis/04_score/03_compare/results/<combo>/leaderboard.csv
                     — read for the premise only. **No number from it reaches the model**:
                     this child sets one option, `weighting: equal`, and every weight in
                     the pool is 1/M whatever the leaderboard says.
environment:         environment/ (project main)
seeds:               none — nothing here is estimated or drawn
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble/01_weighting/a_equal
produced:            2026-08-28
```

**What it establishes.** The main path's weighting, and the prediction it was tested
against. The pool it produces scores 18.817 against the sibling's 22.838.

**The premise registered here was half wrong.** It predicted that an equal pool would score
worse than its best member, because half its mass sits on the two required baselines and
they are the two worst-scoring models of ours; the pool beat its best member by 1.954 CRPS
(`../../results/main/pool_check.json`). The prediction reasoned about where the forecasts
sit and not about how wide they are, and CRPS is a function of both. Its other half — that
the pool would be wider than any member and would over-cover — held exactly.

**Why reading the leaderboard here is analysis and not fitting.** What the members scored is
already a reported result of this project. Reading it to write down what one expects to
happen is what a registered prediction is. Letting one of those numbers set a weight would
be something else entirely, and it is precisely what the sibling does — from a validation
period held back inside the training frame, never from these figures.

alternatives-considered: weights proportional to 1/CRPS on the leaderboard (rejected here
and not built at all — it would fit weights on the period the model is scored on, which is
the one construction this project cannot report); leaving the premise out and letting the
score speak (rejected — a prediction written after the number is not a prediction, and this
one turned out to be the batch's most informative wrong answer).
agency: agent-autonomous

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/model_option_spec.json
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 13, and
                     COMBO_BASE=main
combinations:        aggregate_caseWeighted, aggregate_populationWeighted, popColumn_backCast, provinces_mergeVientiane, provinces_reportingOnly, retrain_everySplit, trainingWindow_from2004
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/03_models/03_candidate/c_ensemble/01_weighting/a_equal
produced:            2026-08-29
```

**What it establishes.** The pool's main-path child, re-run under each row.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`, because one script produces the same artefact
under every combination from the same invocation — the combination is a parameter, and each
file records its own in a `combo` field. `/validate invariants` accepts that form only for
combinations the stability manifest names, and its `combos` check is what keeps that set
closed, so the two checks close over each other rather than either being weakened.

alternatives-considered: a section per combination, as batches 10 and 11 wrote for the family
rows — rejected here because seven near-identical sections at twenty-odd nodes is 150 sections
that say the same sentence, and the placeholder exists precisely so that a parameterised step
is recorded once. Where a combination made this node do something *different*, that is in the
paragraph above rather than in a section of its own.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.


---

## Batch 23 — the digest of the premise that stopped reading downstream

```
result:              results/$COMBO/model_option_spec.json
script:              scripts/choose_weighting.py
                     sha256:8078a6a3f4f6367b0fd748034e00ef2bfd13d2c794b0f88f590de99e9e372d24
invocation:          unchanged: "$PYTHON" scripts/choose_weighting.py, from the node
                     directory via the pool's run.sh
inputs:              the shape of the tree — every Chap contract directory under
                     analysis/03_models except the pool's own. Nothing downstream.
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble/01_weighting/a_equal
produced:            2026-08-28; recorded 2026-09-01
```

**What changed in the script.** The registered premise read `04_score`'s leaderboard, to say
what the members had scored. That is a model node depending on a scoring node, and it failed
the moment the node ran under a combination whose scoring chain had not. The premise now
reads the shape of the tree instead — how many Chap contract directories there are and which
of them are the plan's required baselines — and states in words what the pool is predicted to
do; `../../scripts/check_pool.py` measures it afterwards against the members' own stored
evaluations, which is where a number about a member belongs. `pandas` and the `combos`
import went with it.

**When it changed, and why the record missed it.** Within batch 11, after that batch's own
section was written: the fix is in `2799be5`, the commit that carries batch 11's report. So
the record has named the pre-fix version, `ffeee402…`, since the day the pool was built,
while every run from batch 13 onward — the seven `02_setup` rows, batch 22's two baseline
rows, batch 14's fourteen and tier 2, and the whole frozen phase-E set — used this one. The
spec on disk under `main` is this version's: it carries `members`, `member_count` and
`share_of_the_pool_on_the_required_baselines`, and no leaderboard figure at all.

alternatives-considered: none new; the weighting choice itself is unchanged and its
alternatives are in the first section.

agency: agent-autonomous.
information: agent-retrieved — the digest is computed from the file, the change read from the
diff at `2799be5`, and the spec's contents from the file on disk.

## Batch 32 — the membership comes from the pool's own rule, and the 47 specifications again

```
result:              results/$COMBO/model_option_spec.json, all 47 combinations
script:              scripts/choose_weighting.py
                     sha256:5fef20d06d9e1293b80b14fd110c1b74c6f0a165deb3620691030dfcd43da066
                     analysis/03_models/scripts/lib/pool_shape.py
                     sha256:f21b28fd9257e3ef9d4f8e52ae5e614335be021bca4dbd9d1446e3299f4d7e95
invocation:          unchanged: "$PYTHON" scripts/choose_weighting.py, from the node
                     directory via the pool's run.sh. For the 46 combinations that are not
                     on the main path, run once each with COMBO set and COMBO_BASE unset,
                     by AI-internal/useful-scripts/rewrite_weighting_premise.py
inputs:              the shape of the tree — every Chap contract directory under
                     analysis/03_models except the pool's own, with every alternatives fork
                     above one resolved to the child this combination takes. The
                     resolution reads the model_spec.json of models that run before this
                     node, and the fork's own main path where none has run. Nothing
                     downstream.
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              91bda84 (the scripts), 14165dd (the 47 specifications)
instructions-commit: 595c32d
node:                analysis/03_models/03_candidate/c_ensemble/01_weighting/a_equal
produced:            2026-09-06
```

**What changed in the script.** It computed the pool's membership itself, by globbing for
Chap contract directories and counting them. `prepare_members.py` computed it by resolving
every alternatives fork above a contract to the child the combination takes. The two agreed
until batch 22 gave the persistence baseline and the climatology baseline a second published
construction each, and from that day this file recorded a **six-member pool at 1/6 each with
two-thirds of its mass on the plan's required baselines** where **four members at 1/4** ran.
Both statements were printed by the same run, three lines apart, in every log the project
has — including the clean-room run of 2026-09-05, whose `run.log` says `6 members at 0.167
each` on one line and `ensemble members[main]: 4` on another.

Both now call `03_models/scripts/lib/pool_shape.py`. The premise gains
`contracts_not_on_this_combinations_path`, which names the constructions this combination did
not take, and `source` and `nothing_downstream_is_read` are rewritten to describe the rule
that is there rather than the glob that is gone.

**Nothing computed moved.** The premise reaches no model: `model_configuration.yaml` is
built from `user_option_values`, the covariates and the seed. All 47 configurations are
byte-identical to their previous versions, so `configuration_sha256` — what `chap eval` was
pointed at — is unchanged and no model had to be run again. 80 documents had the membership
corrected and 14 already named the right four; the measurement is
`AI-generated/validation/26-09-06_weightingPremiseRewrite.json`, and a second pass reproduced
all 102 documents byte for byte.

**`what_the_premise_implies` is unchanged, and was never wrong.** It predicts that an
equally weighted pool "puts half its mass on the two required baselines" — which is what
four members with two baselines does. The premise block beneath it said two-thirds on four.
The file contradicted itself, and the prediction was the half that was right.

alternatives-considered: resolving each fork from `claim.md`'s main path alone, which would
have made the membership a pure function of the checkout and never read a result. Rejected
because the pool must name the model the combination actually scored — under
`persistence_negBinomialFloor` the member is `b_negBinomialFloor`, and no property of the
tree says so. Recording *how* each fork resolved was also rejected: that sentence moves with
`COMBO_BASE` while the membership does not, and a premise that changed when an unrelated
variable was set would be the same class of defect one field over.

agency: agent-autonomous.
information: agent-retrieved — the digests are computed from the files, the cold-checkout
evidence read from `AI-generated/validation/26-09-05_cleanroom-artefacts/run.log`.
