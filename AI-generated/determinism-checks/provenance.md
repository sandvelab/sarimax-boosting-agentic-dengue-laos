# Provenance — determinism checks

## `model_determinism.json`

```
result:              model_determinism.json
script:              AI-internal/useful-scripts/verify_model_determinism.sh
                     sha256:695017e2509ace86b1e19548b36cb1068f98c578e977b65ed8f581b29d47119b
invocation:          bash AI-internal/useful-scripts/verify_model_determinism.sh
                     (from the repository root)
inputs:              analysis/02_setup/run.sh and the two baseline nodes' run.sh, each
                     executed twice under a scratch COMBO; the scratch results are
                     removed when the check finishes
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0, and
                     each model's own uv environment built from its tracked lockfile
seeds:               none, which is the thing being checked
commit:              f13dba4
instructions-commit: cf97b81
node:                not a node — a check on the method, like check_invariants.py
produced:            2026-08-26
```

**What it establishes.** Two independent runs of each baseline produce identical per-cell
scores and an identical fitted model. The models claim to contain no randomness; this is the
evidence.

**Why it runs the real nodes rather than a copy of them.** The combination mechanism makes a
second run of a node an ordinary run under a different `COMBO`, so the check exercises the
same code path the reported analysis uses. A check that ran a copy would be checking the
copy.

alternatives-considered: the check could have compared the evaluation `.nc` files directly,
which would be the strongest possible statement. It cannot: chap-core stamps a timestamp
into them. It could also have been made a node inside the tree, so that `analysis/run.sh`
verified determinism on every run; that was rejected because it would double the cost of
every model run to re-establish something that changes only when a model changes.

agency: agent-autonomous. Rule 6's requirement to verify by running twice and diffing is the
project's; extending batch 6's single-model check to every model of ours, through the
combination mechanism, is this batch's.

---

## Addendum — the check was comparing a field that recorded its own scratch name, 2026-08-27

```
result:              model_determinism.json   (status `identical`, all three models)
script:              AI-internal/useful-scripts/verify_model_determinism.sh
                     sha256:ff8ceabf29e4d82c3211f22a9d8f8b14eb9a14ab90c6ebb1fc99a36bb9daabf7
invocation:          bash AI-internal/useful-scripts/verify_model_determinism.sh
inputs:              analysis/02_setup/run.sh, the two baseline nodes' and the candidate
                     node's run.sh, and 04_score/01_collect/run.sh — each executed twice
                     under one scratch COMBO per model; the scratch results are removed
                     when the check finishes
environment:         unchanged
seeds:               project seed 20260822 → component seed 849487747 for the candidate;
                     the baselines have nothing to seed, which is what is being checked
commit:              6a71a67   (the state the repaired check was run from)
instructions-commit: cf97b81
produced:            2026-08-27
```

**What was wrong.** Batch 9 added a `scored_under_combo` column to
`04_score/01_collect/results/<combo>/models.csv` — the column that makes `COMBO_BASE`
inheritance visible on the face of the file, and a good addition. The check ran its two
passes under `determinism_<model>_1` and `_2` and compared `models.csv` byte for byte, so
from that commit it was comparing a field whose value **is the pass's own scratch name**.
It reported `differs` for every model on every run, whatever the models did.

The history is dateable: `identical` at `a2cdad3` (batch 7) and `509d458` (batch 8),
`differs` at `dec4116` (batch 9) and unchanged since. Demonstrated rather than inferred —
two hand-run passes of the persistence model on 2026-08-27 differed in exactly one line of
one file, in exactly that field, while `metrics_cell.csv` (372 lines) and
`fitted_model.json` were byte-identical.

**Why this mattered more than the wrong word in a file.** Rule 6's only instrument was
stuck on red. A model that genuinely lost its seeding would have produced the same verdict
the check had been producing for two batches, so nothing about the output would have looked
wrong — which is the failure mode `AGENTS.md` §5 exists to guard against, arriving in the
guard itself.

**The repair, and why it is not adjusting a check to pass.** Nothing was excluded from the
comparison. Both passes now run under **one** combination name: pass 1's three files are
copied aside, pass 2 overwrites them in place, and the copy is compared with what replaced
it. `scored_under_combo` is then identical by construction rather than by exemption, and a
genuine difference in any of the three files still fails the check. The alternative —
comparing `models.csv` with that one column dropped — was rejected because an exemption
list is a place where a second exemption can be added later without anyone noticing.

**What the repaired check says.** `identical` for persistence, climatology and the
candidate: identical per-cell scores, identical model listings, identical fitted objects.
For the candidate this is the meaningful form of the check, because on the main path it
fits in `train` and therefore has a fitted object to compare.

alternatives-considered: leaving the check as it was and documenting the meaning of
`differs`; rejected because every future reader would have to re-derive it, and because a
check nobody can read at a glance is not a check. Dropping `models.csv` from the comparison
entirely; rejected because it is what verifies that both passes discovered and scored the
same set of models.

agency: agent-on-human-assessment. The defect and the three candidate repairs were the
agent's; the choice among them, and the decision to make it now rather than in phase E, was
the human's on 2026-08-27.

## 2026-08-28 — re-run with candidate 2, and the model list extended

```
result:              model_determinism.json
script:              AI-internal/useful-scripts/verify_model_determinism.sh
invocation:          bash AI-internal/useful-scripts/verify_model_determinism.sh
                     (from the repository root)
inputs:              the tree's own nodes, run twice each under a scratch combination
                     `determinism_<model>`, which the script removes when it finishes
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0; each
                     model's own environment is built by chap-core from the uv.lock beside
                     it
seeds:               project seed 20260822, read from readme-at-start.md by the script
                     rather than copied into it; component seeds 849487747 (candidate 1)
                     and 1877199108 (candidate 2), derived by each node's own path
commit:              95df846
instructions-commit: cf97b81
produced:            2026-08-28
```

**What changed in the script.** One line: `boosted:analysis/03_models/03_candidate/b_boosted`
added to the model list. The path matters and is commented in the file. Every other model of
ours is named by the node that routes to it — `03_models/03_candidate` for candidate 1 —
because that node's `run.sh` runs the main path. Candidate 2 is a **sibling alternative**, so
the same node routes *past* it; naming it that way would have run candidate 1 a second time
under a scratch combination called `determinism_boosted` and reported a true result about the
wrong model. That is a failure a green check would have hidden, which is the same shape as
the defect repaired on 2026-08-27, and it is why the entry names the leaf rather than the
switch.

**What it says.** `identical` for all four: persistence, climatology, `hier_nb` and
`boosted` — identical per-cell scores, identical model listings, identical fitted objects.

**Why candidate 2's fitted object is the interesting half of its check.** It is 71 trees
written out as JSON, and the model's own traversal of that stored form is a second prediction
path beside scikit-learn's. Two runs producing an identical file therefore verifies both that
the head's draw is seeded and that the same ensemble was fitted twice — and the fit's own
internal check, which compares the stored form against scikit-learn's `predict` and raises if
they differ, is what verifies that the stored form means what the ensemble meant.

alternatives-considered: naming candidate 2 by the family node for symmetry with candidate 1
(rejected, as above — it would have checked the wrong model and passed); making the model
list discover the leaves of `03_candidate` automatically (rejected for now — the list is four
lines and a discovery rule would have to encode which nodes are switches and which are
models, which is the tree's semantics restated in a shell script; worth revisiting if a third
candidate makes it four families).

agency: agent-autonomous.
