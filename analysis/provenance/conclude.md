# Provenance — the project's computed conclusion

```
result:              results/main/conclusion.json
script:              scripts/conclude.py
                     sha256:37aa72469d283a78d622a94f44a17b3f016b10d160fefe523336fb7946abac7b
invocation:          "$PYTHON" scripts/conclude.py
                     (from analysis/, via run.sh, after every other node; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/04_score/03_compare/results/main/leaderboard.csv
                     analysis/04_score/03_compare/results/main/paired_summary.csv
                     analysis/04_score/03_compare/results/main/comparison_notes.json
                     analysis/03_models/03_candidate/claim.md, if it exists — the tree
                     itself is what says which model is ours. It does not exist yet.
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis
produced:            2026-08-26
```

**What it establishes.** One file per combination stating what that analysis concluded: the
skill score `1 − CRPS_ours / CRPS_reference`, with raw CRPS, both coverage figures, the
paired difference and the resolvable-difference floor beside it. **Nothing anywhere else in
the repository states the conclusion**, which is what stops a sentence in a report drifting
from the file it came from. Phase D's stability driver calls this same script once per
combination, so the development spread will be a set of these files and not a second
implementation of the analysis.

**What it says at this batch, and what it does not.** The project has two baselines and no
candidate: `03_models/03_candidate` is built in phase C. So `candidate_exists` is **false**,
the headline model is the best-scoring model of ours, and its role is recorded in the file
as a placeholder. That is deliberate — promoting a baseline to a candidate quietly would make
the file readable and wrong, and the alternative of leaving the conclusion uncomputed until
phase C would mean the root's contract was first exercised at the moment it had to carry a
real result. The vertical slice's argument, one level up.

**Which model is "ours" is resolved from the tree, not chosen here.** Once
`03_models/03_candidate` exists, the script reads its `main-path` field and takes that
child's model. So promoting an alternative with `/node promote` changes the reported
conclusion, and the commit that promotes it is the record of when the reported model
changed — which is exactly the kind of decision that otherwise disappears.

alternatives-considered: the reported model could have been named in a configuration file at
`03_models`, which would be simpler to read. Rejected: it would be a second place where the
main path is declared, and two declarations of the same thing disagree eventually. Reporting
a raw CRPS as the conclusion rather than a skill score was settled against in §4b, on the
reasoning that development and holdout are different years and their raw scores are not
comparable. Falling back to the *persistence* baseline specifically, rather than to the best
of ours, was considered — it is more stable across batches — and rejected because it would
mean the conclusion file ignored a better model of ours that had actually been run.

agency: agent-autonomous, within a human-set frame. The skill score as the reported
conclusion is the human's choice from an agent proposal (§4b, 2026-08-23,
agent-on-human-assessment); computing it at the root, and how "our model" is resolved before
a candidate exists, are the agent's.

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

Re-run on `main` after the promotion. The project's reported skill score against the
reference moved from **−0.181** to **−0.072**, and `beats_all_baselines` became **true**
for the first time: the candidate's 23.698 is below climatology's 24.337 and persistence's
24.879. `beats_reference` remains false.

The file is unchanged in shape and the script is unchanged. What changed is the main path
through `03_models/03_candidate`, which is where `conclude.py` resolves our reported model
from -- so the conclusion moved because the tree moved, which is the property batch 7 built
the script to have.

alternatives-considered: none new.

agency: agent-autonomous.

---

## Batch 11 — the conclusion turns positive

```
result:              main/conclusion.json
script:              scripts/conclude.py
                     sha256:37aa72469d283a78d622a94f44a17b3f016b10d160fefe523336fb7946abac7b
invocation:          bash analysis/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis
produced:            2026-08-28
```

**What it establishes.** The project's reported conclusion, recomputed after the family fork
moved. `our_model` is now `ensemble`, resolved as always from the main path through
`03_models/03_candidate` rather than chosen here, and the skill score against the reference is
**+0.1485** — mean CRPS 18.817 against 22.098. `beats_reference` and `beats_all_baselines` are
both true for the first time in this project.

**What the file also says, and what must be read with it.** The paired difference is −3.282 at
a split-clustered standard error of 1.726: 1.90 standard errors, which does not separate the
two models. The reported coverage is 0.863 at the 10–90 level against a nominal 0.80 and 0.749
at 25–75 against 0.50, so the model that wins is also the most over-dispersed the project has
produced. The plan's §2 is explicit that a model winning on mean CRPS while badly calibrated
has not won; the honest reading of these two figures is that the 10–90 error is small and on
the conservative side, that the 25–75 error is large, and that
`03_models/03_candidate/c_ensemble/results/main/pool_check.json` rules out the zero-atom
artefact as its explanation.

**Nothing about this script changed.** Which model is ours is resolved from the tree, so the
promotion moved the conclusion without a line of this file being touched — which is the
property it was written to have.

alternatives-considered: none new.
agency: agent-autonomous

---

## Batch 13 — resolving our reported model through COMBO_BASE

```
result:              results/$COMBO/conclusion.json
script:              scripts/conclude.py
                     sha256:4d5c04b0c3d9384fbd4271db1f8a45c1cf19ea0568a0e102d108f3fafcc8e764
invocation:          "$PYTHON" analysis/scripts/conclude.py
                     (COMBO set by the stability driver; COMBO_BASE=main for every
                     batch-13 row)
inputs:              analysis/04_score/03_compare/results/$COMBO/leaderboard.csv
                     analysis/04_score/03_compare/results/$COMBO/paired_summary.csv
                     analysis/04_score/03_compare/results/$COMBO/comparison_notes.json
                     analysis/03_models/03_candidate/claim.md  (the main-path field)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              ce0eb34
instructions-commit: 030bee2
node:                analysis
produced:            2026-08-29
```

**The defect, found by running rather than by planning.** The script resolved our reported
model by globbing for a `model_spec.json` under `results/$COMBO/` only. A combination that
re-runs no model of ours has none — re-weighting a mean re-runs nothing — so both of batch 13's
scoring rows fell through to the fallback branch, reported `candidate_exists: false`, and took
"the best-scoring model of ours" instead. Under case weighting that is **persistence**, so
`aggregate_caseWeighted/conclusion.json` named a required baseline as the model this project
reports, with a skill score computed for it. The file was internally consistent and wrong.

**The fix.** The lookup falls back to `COMBO_BASE`, and the basis string records that it did.
It is deliberately narrow: it applies only when **no** child of the family fork produced a spec
under this combination, and only when the inherited model is on this combination's leaderboard.
A row that did move a family therefore still resolves against its own results — which is the
separate defect batch 12 recorded for batch 14, and this must not paper over it.

**Checked against the main path.** Re-run under `COMBO=main`, `results/main/conclusion.json` is
byte-identical, so the change cannot have moved the reported conclusion.

alternatives-considered: **resolving from `models.csv`'s `scored_under_combo`** rather than from
the family fork — rejected because that file says which combination scored a model, not which
model the project reports, and conflating the two is how a baseline became the answer in the
first place. **Failing loudly when no candidate spec is found under COMBO** — rejected because
the fallback branch has a legitimate use, from before `03_candidate` existed, and removing it
would break the record of the batches that ran then.

agency: agent-autonomous.
information: agent-retrieved — the defect was read out of the produced `conclusion.json` files,
not anticipated.


---

## Batch 22 — the two baseline-fork combinations

```
result:              results/$COMBO/conclusion.json
combinations:        climatology_frozenWindow, persistence_negBinomialFloor
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 22, and
                     COMBO_BASE=main
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; the step reads stored scores
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis
produced:            2026-08-29
```

**What it establishes.** Both rows resolve the reported model correctly — `candidate_exists:
true`, `our_model: ensemble`, resolved from the family fork's own results under the
combination rather than through the batch-13 fallback, because a baseline row does re-run a
model of ours. Skill **+0.1206** under `persistence_negBinomialFloor` and **+0.1460** under
`climatology_frozenWindow`, against the main path's +0.1485.

**`beats_all_baselines` stays true on both**, including the row where a required baseline is
4.181 CRPS better than the main path's version of it: the pool at 19.434 is still below the
parametric persistence at 20.698.

alternatives-considered: none at this node.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.

---

## Batch 14 — the reported model is read off the results, and the fourteen candidate and family combinations

```
result:              results/$COMBO/conclusion.json
combinations:        main, aggregate_caseWeighted, aggregate_populationWeighted,
                     family_hierNB, family_boosted, weighting_crpsWeighted,
                     autoregressive_lag3, covariates_lagged, covariates_rich,
                     features_richCalendar, fitTime_refitAtPredict,
                     head_quantileEnsemble, observation_negBinomial,
                     observation_zeroInflated, population_covariate, population_ignored,
                     yearVariance_shared
script:              scripts/conclude.py
                     sha256:3acf80d9c46bdbec096010c14864b6348dda11437411aab01c15ed26e73efd4a
invocation:          environment/chapenv/bin/python analysis/scripts/conclude.py, with
                     COMBO set by analysis/05_stability/scripts/run_manifest.py --batch 14
                     and COMBO_BASE=main; on `main`, neither set
inputs:              analysis/04_score/03_compare/results/$COMBO/leaderboard.csv
                     analysis/04_score/03_compare/results/$COMBO/paired_summary.csv
                     analysis/04_score/03_compare/results/$COMBO/comparison_notes.json
                     analysis/03_models/03_candidate/**/results/$COMBO/model_spec.json —
                     the tree's own results are what say which family this combination ran
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              87440bc (the script), 3fb1280 (the combinations)
instructions-commit: cf97b81
node:                analysis
produced:            2026-08-30
```

**What changed in the script.** Which model is ours was resolved from `claim.md`'s
`main-path` field at `03_models/03_candidate`. That field names the child the **reported**
analysis takes and does not move with the combination, so a family row — one that runs a
sibling family in place of the reported one — found no results under the child it named,
fell through to "the best-scoring model of ours", and would have written
`candidate_exists: false` on a row whose whole content is which candidate ran. Batch 12
predicted it from the manifest and batch 13's narrower fix for the scoring rows was written
so as not to paper over it.

The family fork is now read off the results, in the order every other combination-aware step
in this project reads a fork: the child with a model scored under this combination, else the
one under `COMBO_BASE`, else — only before any candidate has run — the placeholder. **Two
children with results under one combination is now a hard failure**, because exactly one
family is on any one combination's path and a project cannot report two models as its own.
That check is what caught the twelve phase-C directories this batch removed, had they been
left in place.

Verified on `main`: every value in `conclusion.json` is unchanged and only the wording of
`our_model_basis` moves, from naming the tree's main path to naming the family the
combination ran. On the two scoring rows the same holds, with the inherited-from-base clause
batch 13 added still applying and still saying so.

**What it establishes.** All 24 tier-1 rows now have a conclusion, and the two family rows
name `hier_nb` and `boosted` rather than falling back. `family_hierNB` is the only row in
the set where our model does not beat the reference: skill **−0.0724**, CRPS 23.698, and
`beats_reference: false` with `beats_all_baselines: true`.

alternatives-considered: keeping `claim.md` as the source and having the driver rewrite its
`main-path` per combination (rejected — that is a step editing the tree to describe the run
it is in the middle of, and it would leave the field wrong whenever a run failed midway);
resolving the family from the manifest row instead of from the tree (rejected — the manifest
would then be an input to the conclusion, and a conclusion that depends on the perturbation
plan cannot be produced by `analysis/run.sh` on its own).

agency: agent-autonomous.
information: agent-retrieved.

## Batch 18 correction — the batch-14 commit `9993d37` is not in the history; read `87440bc`

Appended rather than edited in place, because a provenance record that silently changes an
address it once gave is worth less than one that shows the address went bad.

The sections above named **`9993d37`** as batch 14's "before the run" commit. That commit is
not an ancestor of `HEAD` and is on no branch: batch 14's history was rewritten after it was
made, and the commit that survived is **`87440bc`** — same subject, same author timestamp,
and **the same tree**, `f473a16ee75d23f4483d3d101b18119cd224b6d7`. So the *state* those
sections describe is exactly right and only the address was dead.

**Their `commit:` lines have therefore been corrected in place**, from `9993d37` to
`87440bc`, and this section is the record that it happened. Appending alone was not enough:
a provenance record exists so a reader can check out what it names, and one that keeps a
dead hash and a footnote saying to read a different one has not been repaired. Nothing else
in those sections is touched, and no result was recomputed — the two commits have the same
tree, so the state they describe is byte-identical either way.

It looked fine for eight days for two compounding reasons, both now closed in
`AI-internal/useful-scripts/check_invariants.py`. The check tested `git cat-file -e`, which
answers whether an object is in the store — and an orphaned object stays in the store of the
tree that orphaned it, and is copied wholesale by a *local* `git clone`, which hardlinks the
object directory. It would have vanished on the first push, which is batch 19. The check now
requires ancestry of `HEAD`. And the pattern was anchored to a `commit:` line carrying one
bare hash, so a line like `commit: 9993d37 (the script), 3fb1280 (the combinations)` was
skipped entirely — a record that annotated its hashes was the one the check never read. It
now takes every hash on every `commit:` line.

Found by batch 18's `/validate outsider` run, which walked the headline result's chain from
`conclusion.json` back to the archived dataset and tested each link rather than reading it.

agency: agent-autonomous.
information: agent-retrieved — `git merge-base --is-ancestor`, `git rev-parse <c>^{tree}`.


---

## Batch 23 — the digest this record has been missing since batch 16

```
result:              results/main__holdout/conclusion.json, and the thirty-one other
                     results/*__holdout/conclusion.json
script:              scripts/conclude.py
                     sha256:2838a897690841bb7c634f656150c6cf4d83dbb9be312c7c5e9861b926efad09
invocation:          "$PYTHON" analysis/scripts/conclude.py, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --dataset holdout and
                     COMBO_BASE=main
inputs:              analysis/04_score/03_compare/results/$COMBO/leaderboard.csv
                     analysis/04_score/03_compare/results/$COMBO/paired_summary.csv
                     analysis/04_score/03_compare/results/$COMBO/comparison_notes.json
                     analysis/03_models/03_candidate/**/results/$COMBO/model_spec.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              895a9f8 (the change), 609e1be (the rows that ran on it)
instructions-commit: cf97b81
node:                analysis
produced:            2026-08-31; recorded 2026-09-01
```

**What changed in the script.** The `dataset` field stopped being the constant
`"development"` and became `combos.dataset()`, derived from the combination name by the same
function the setup chain uses to pick the file — so a conclusion cannot say it is a
development number while the analysis behind it read the holdout. The printed line names the
dataset with it. Nothing else moved.

**Why this is the worst of the twenty this batch found.** Batch 16 changed the script, ran it
thirty-two times to produce phase E's conclusions, and appended no section. So this record —
the record of the project's headline result — described a version of `conclude.py` that had
not existed since 2026-08-31, and **no record anywhere named the invocation that wrote
`results/main__holdout/conclusion.json`**, which is where the reported held-out skill score
of +0.0868 is read from. It is now this section.

**What the development conclusion was produced by, and why it is not re-run here.**
`results/main/conclusion.json` was last written at `87440bc` by the batch-14 version,
`3acf80d9…`. This batch does not re-run it. The current script derives `dataset` from the
combination name, which is `development` for `main`, so it writes the same file — and that
is an argument rather than evidence, so here is the evidence: batch 18's clean-room run
rebuilt the main path from a fresh clone at `ad7e64f` with this version of the script, and
every field of `conclusion.json` that does not divide by the unseeded reference came back
identical (`AI-generated/validation/26-09-01_cleanroom.md`).

alternatives-considered: re-running `conclude.py` under `COMBO=main` so that the reported
development conclusion and the current script share a commit. Rejected on two counts — it
would be a re-run made for a record's benefit rather than for the analysis's, and the
clean-room run is stronger evidence than it would be, having rebuilt every input as well as
the script. Correcting the earlier sections' digests in place was rejected on the standing
rule: each of them names the version that ran then, and is right to.

agency: agent-autonomous.
information: agent-retrieved — the digest is computed from the file, the commits from
`git log`, and the reproduction from the clean-room comparison.
