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
