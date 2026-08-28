# Provenance — candidate 3's configuration

```
result:              main/model_configuration.yaml
                     main/candidate_spec.json
                     family_ensemble/model_configuration.yaml
                     family_ensemble/candidate_spec.json
                     weighting_crpsWeighted/model_configuration.yaml
                     weighting_crpsWeighted/candidate_spec.json
script:              scripts/assemble_candidate_config.py
                     sha256:a5ced6a7d145153bde58c6aa7c34ea35576587b56adc2aa799e9da5ef6004919
                     analysis/scripts/lib/combos.py, analysis/scripts/lib/project_seed.py
invocation:          "$PYTHON" scripts/assemble_candidate_config.py, with COMBO set
inputs:              01_weighting/<child>/results/<combo>/model_option_spec.json
                     results/<combo>/members.json
environment:         environment/ (project main)
seeds:               component seed 1648567750, derived from project seed 20260822 as
                     int(blake2b('20260822:analysis/03_models/03_candidate/c_ensemble',
                     digest_size=8), 16) % 2**32, by analysis/scripts/lib/project_seed.py.
                     A third component, distinct from candidate 1's 849487747 and
                     candidate 2's 1877199108, so no two models of ours share a stream.
                     It governs the pool's own draw only; the members draw from their own.
commit:              5e1de04
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-28
```

**What it establishes.** The one file `chap eval --model-configuration-yaml` is pointed at,
and the specification recording what went into it: the choice taken at the fork, the
combination that choice was taken under, the four members with the configuration each of
them was given, the union of the members' covariates, and the seed with its derivation.

**Why the membership is a path and a hash rather than an option value.** Four contract
directories with their entry points, configurations and file hashes do not fit in a scalar,
and `chap_eval.py` argues for a stored artifact over a command line nobody kept. So the
configuration carries `members_file` and `members_sha256`, and `ensemble.py` refuses to
pool anything if the file it finds is not the file the configuration names.

**On the duplication with the other two families' assemblers.** Batch 10 logged that the
shared part belongs in `03_models/scripts/lib/` and named batch 11 as where the lift
belongs. It is **scheduled rather than skipped**, and the reason is batch 9's own rule:
rewriting `a_hierNB/scripts/assemble_candidate_config.py` changes its sha256, and that hash
is in the provenance record of every combination those two assemblers configured — thirteen
of them — whose results would then name a script that never produced them. Batches 13 and
14 re-run every combination in the frozen manifest, which is the moment when regenerating
those records costs nothing extra. Recorded here, in the node's claim, in the script's
docstring and in the plan's §4b.

alternatives-considered: lifting the shared assembler into a library in this batch
(deferred, see above, with the batch it belongs to named); putting the members inline in the
configuration as an array of objects (rejected — chap-core parses the configuration into
ModelConfiguration and a nested structure there is a shape the platform does not promise to
carry, and the hash of a separate file is a stronger record than a copy inside another one);
deriving the pool's seed from the members' (rejected — Rule 6 asks for one project seed
derived per component, and the pool is a component).
agency: agent-autonomous
