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
