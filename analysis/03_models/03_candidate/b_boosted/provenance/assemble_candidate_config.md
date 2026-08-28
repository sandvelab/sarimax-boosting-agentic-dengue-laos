# Provenance — candidate 2's assembled configuration

```
result:              family_boosted/model_configuration.yaml
                     family_boosted/candidate_spec.json
                     features_richCalendar/model_configuration.yaml
                     features_richCalendar/candidate_spec.json
                     head_quantileEnsemble/model_configuration.yaml
                     head_quantileEnsemble/candidate_spec.json
script:              scripts/assemble_candidate_config.py
                     sha256:95b9b004ba7f5761b58d20087e8046a38d45a08a96969669fabda5004c1c7f44
                     analysis/scripts/lib/project_seed.py
                     sha256:997093e941aa7eb09539d20192932c7537ab7b63a6b11c1be61988d26f778bfb
invocation:          "$PYTHON" scripts/assemble_candidate_config.py
                     (from the node directory, via run.sh, after the two fork children
                     have run; PYTHON is environment/chapenv/bin/python. COMBO is
                     family_boosted with COMBO_BASE=main for the main path of this
                     candidate, and the sibling combination name for each of the two
                     swept rows.)
inputs:              01_features/<child>/results/<combo>/model_option_spec.json
                     02_head/<child>/results/<combo>/model_option_spec.json
                     (found by searching each fork for the one child with results under
                     this combination — never by naming a child)
                     readme-at-start.md — the project seed
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               project seed 20260822, read from readme-at-start.md; component
                     analysis/03_models/03_candidate/b_boosted; derivation
                     int(blake2b('<project_seed>:<component>', digest_size=8), 16) %
                     2**32; component seed 1877199108. A different component from
                     candidate 1 and therefore a different number, which is what Rule 6's
                     "one seed derived downward" means when a project has two models that
                     draw. Written into the configuration file, so the number the model
                     used sits beside the model's results. The script itself draws nothing.
commit:              6cb1163
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/b_boosted
produced:            2026-08-28
```

**What it establishes.** That the configuration route batch 8 opened for candidate 1 carries
a second model unchanged: two forks rather than six, a different option vocabulary, and the
same chain of files from fork child to `{model_config}` in the entry points. Nothing about
a run's configuration lives only in a command line.

**Why this is a second script and not a shared one.** It is a near-copy of
`a_hierNB/scripts/assemble_candidate_config.py`, differing in the candidate's name and in
nothing else that matters. Lifting the shared part into `03_models/scripts/lib/` is the
right end state — the argument `chap_eval.py` makes about a copy per model being a set of
copies that will drift — and doing it in this batch would have rewritten the script that
produced the reported main path's configuration, whose hash is in a provenance record and
whose results would then have to be regenerated to keep that record true. Batch 11 adds a
third candidate and is where the lift belongs.

alternatives-considered: checking a configuration file in beside the model (rejected for the
reason batch 8 rejected it: it would be a third record of what the forks decided and the one
the model actually read); giving candidate 2 the same component seed as candidate 1 so the
two families draw alike (rejected — the seed is derived from the node path precisely so that
two components cannot silently share a stream, and two models whose draws are correlated
would make the family comparison depend on the correlation); deriving the seed from the
candidate's name rather than its path (rejected, the path is what is unique in the tree).
agency: agent-autonomous
