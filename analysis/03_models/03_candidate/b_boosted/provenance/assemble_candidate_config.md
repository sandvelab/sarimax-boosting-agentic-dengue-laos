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

---

## Batch 11 — candidate 2's configuration under the ensemble's three combinations

```
result:              main/candidate_spec.json
                     main/model_configuration.yaml
                     family_ensemble/candidate_spec.json
                     family_ensemble/model_configuration.yaml
                     weighting_crpsWeighted/candidate_spec.json
                     weighting_crpsWeighted/model_configuration.yaml
script:              scripts/assemble_candidate_config.py
                     sha256:95b9b004ba7f5761b58d20087e8046a38d45a08a96969669fabda5004c1c7f44
invocation:          bash analysis/03_models/03_candidate/b_boosted/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/b_boosted
produced:            2026-08-28
```

**What it establishes.** The configuration the ensemble gives its candidate-2 member, under
each of the pool's three combinations — `main` among them, because batch 11 promoted
`c_ensemble` and `analysis/run.sh` now reaches candidate 2 as a member of the pool. Each is
**byte-identical** to the one this node wrote under `family_boosted`: the same two choices,
the same three covariates and the same component seed **1877199108**. Checked by diff.

**A configuration under `main` is not an evaluation under `main`.** There is no
`model_spec.json` at this node under `main` and there should not be: candidate 2 is a sibling
alternative under an alternatives node, it is evaluated on its own under `family_boosted`, and
`04_score` collects models by the `model_spec.json` they write. What `main` holds here is the
configuration the pool handed to one of its members, and the pool's own `members.json` names
the file and its hash.

alternatives-considered: as in the parallel record at candidate 1.
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
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/03_models/03_candidate/b_boosted
produced:            2026-08-29
```

**What it establishes.** Assembled as a pool member under each row; no fork of this family moved in batch 13.

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

## Batch 14 — the assembler lifted into a shared library

```
result:              results/$COMBO/model_configuration.yaml · candidate_spec.json
combinations:        main, family_boosted, and every combination this batch re-ran that
                     configures candidate 2 as a pool member
script:              scripts/assemble_candidate_config.py
                     sha256:1708e780c1e4bea6bd535a3239a6adb76006cbbd4b820bda316af9645ba60bdf
                     analysis/03_models/scripts/lib/assemble_config.py
                     sha256:8b97f2d78063051ce7b3e1ad74dc3300b1ccf106d0654c68962045044a2af46b
invocation:          "$PYTHON" scripts/assemble_candidate_config.py, via this node's
                     run.sh or by the pool's prepare_members.py, with COMBO set
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               component seed derived from project seed 20260822 from this node's
                     own path; unchanged by the lift
commit:              9993d37
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/b_boosted
produced:            2026-08-30
```

**What changed.** The same lift as at candidate 1, and for the same reason: this script's
own docstring named `03_models/scripts/lib/` as the right end state and batch 11 as the
place, and batch 11 moved it here because this is the batch that re-runs what these scripts
configured. Re-run under `main` before anything else, both files came out byte-identical.

alternatives-considered: as recorded at candidate 1.

agency: agent-autonomous.
