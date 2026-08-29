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
commit:              2799be5
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

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/candidate_spec.json
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 13, and
                     COMBO_BASE=main
combinations:        aggregate_caseWeighted, aggregate_populationWeighted, popColumn_backCast, provinces_mergeVientiane, provinces_reportingOnly, retrain_everySplit, trainingWindow_from2004
inputs:              unchanged in kind; each combination's own inputs are recorded in the
                     specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-29
```

**What it establishes.** The pool's configuration under each row. No fork of the pool moved in batch 13.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`. `/validate invariants` accepts that form only
for combinations the stability manifest names, and its `combos` check keeps that set closed.

agency: agent-autonomous.
information: agent-retrieved.
