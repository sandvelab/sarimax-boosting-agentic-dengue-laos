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
