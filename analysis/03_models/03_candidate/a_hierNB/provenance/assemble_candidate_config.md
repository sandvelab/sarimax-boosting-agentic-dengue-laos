# Provenance — the candidate's assembled configuration

```
result:              results/main/model_configuration.yaml
                     results/main/candidate_spec.json
script:              scripts/assemble_candidate_config.py
                     sha256:8848dd758d52ec9167db064f740384b3554679ef3a623afb5494a12ca2f62ac0
                     analysis/scripts/lib/project_seed.py
                     sha256:997093e941aa7eb09539d20192932c7537ab7b63a6b11c1be61988d26f778bfb
invocation:          "$PYTHON" scripts/assemble_candidate_config.py
                     (from the node directory, via run.sh, after the four fork children
                     have run; PYTHON is environment/chapenv/bin/python. COMBO unset, so
                     the combination is `main`.)
inputs:              01_observation/a_negBinomial/results/main/model_option_spec.json
                     02_covariates/a_lagged/results/main/model_option_spec.json
                     03_population/a_offset/results/main/model_option_spec.json
                     04_fitTime/a_trainOnly/results/main/model_option_spec.json
                     (found by searching each fork for the one child with results under
                     this combination — never by naming a child)
                     readme-at-start.md — the project seed
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               this script is where the project seed enters the analysis for the
                     first time. Project seed 20260822, read from readme-at-start.md;
                     component 03_models/03_candidate/a_hierNB; derivation
                     int(blake2b('<project_seed>:<component>', digest_size=8), 16) %
                     2**32; component seed 849487747. Written into the configuration
                     file, so the number the model used is beside the model's results.
                     The script itself draws nothing.
commit:              4563baf
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB
produced:            2026-08-27
```

**What it establishes.** The route model configuration takes into an `MLproject` model,
which batches 2, 4 and 7 all left open because no model had needed it. It is chap-core's own
and it is a file at every step: `chap eval --model-configuration-yaml` parses the file into
a `ModelConfiguration` (`user_option_values` and `additional_continuous_covariates`, extra
fields forbidden), writes it back out as `model_configuration_for_run.yaml` in the run
directory, and substitutes that filename for the `{model_config}` placeholder declared in the
model's entry points. The model reads its own configuration from disk. Nothing about a run's
configuration lives only in a command line.

**Why the assembler exists rather than a configuration file checked in beside the model.** A
checked-in file would be a fifth place where the four forks' decisions are recorded, and the
one the model actually read. Assembling it means the forks are the only source: change which
child of a fork runs and the configuration changes with it, without an edit anywhere. It is
the same mechanism `02_setup/scripts/assemble_setup.py` uses for the dataset, and for the same
reason.

**The clash check.** Two forks setting the same option would mean two nodes owning one
property of the model, which is a design error in the tree rather than a value to resolve at
merge time. The script raises instead of merging.

alternatives-considered: passing the options as command-line flags to `chap eval` (there is
no such interface, and inventing one would take the model off the platform's own route);
writing the seed into the model's source (it would then be a constant of the model rather
than a derivation of the project seed, and Rule 6's "one seed derived downward" would be
satisfied only by inspection). Also considered: deriving the component seed from the node
name alone rather than from the project seed. Rejected — that is a second independent seed
wearing the project seed's name.

agency: agent-autonomous. The mechanism is chap-core's (`agent-retrieved`, read from
chap_core/runners/helper_functions.py and confirmed against
chap-models/ewars_plus_template's own MLproject); the assembler's shape follows batch 5's
file contract, which is the human-approved design.

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

```
result:              results/main/model_configuration.yaml
                     results/main/candidate_spec.json
                     autoregressive_lag3/model_configuration.yaml
                     autoregressive_lag3/candidate_spec.json
                     covariates_lagged/model_configuration.yaml
                     covariates_lagged/candidate_spec.json
                     covariates_rich/model_configuration.yaml
                     covariates_rich/candidate_spec.json
                     fitTime_refitAtPredict/model_configuration.yaml
                     fitTime_refitAtPredict/candidate_spec.json
                     observation_negBinomial/model_configuration.yaml
                     observation_negBinomial/candidate_spec.json
                     observation_zeroInflated/model_configuration.yaml
                     observation_zeroInflated/candidate_spec.json
                     population_covariate/model_configuration.yaml
                     population_covariate/candidate_spec.json
                     population_ignored/model_configuration.yaml
                     population_ignored/candidate_spec.json
                     yearVariance_shared/model_configuration.yaml
                     yearVariance_shared/candidate_spec.json
script:              scripts/assemble_candidate_config.py
                     sha256:d8937abc233899a222ca45643766eeb4c2eb1e9b6f38680a17cb6a9b6430bfd9
```

**Two changes to the assembler, both so that it stops having to be told things.** The fork
list is now discovered from the node's own children rather than named, because batch 9
added a fifth and a sixth fork and a script carrying the count would have had to be edited
to notice them -- a script that can be wrong about what the model is while still running.
And each fork's chosen child is resolved through `COMBO_BASE`: a combination that moves one
fork has no child with results under it at the other five, and inherits their choices from
the base. Which combination answered each fork is written into `candidate_spec.json` as
`choice_combos`, so a configuration assembled partly from another combination's choices
says so on its face.

**The main path's configuration changed** with the promotion: `observation: hurdle`,
`covariates: []`, `year_variance: province_scaled`, with `population: offset`,
`fit_time: train` and `autoregressive: none` unchanged. The component seed is unchanged at
**849487747**, derived as before from project seed 20260822 by
`analysis/scripts/lib/project_seed.py` -- promoting a fork changes what the model is, not
which component it is.

alternatives-considered: deriving a fresh component seed for the promoted configuration, so
that two configurations of one model never share a draw sequence; rejected, because the
seed is a property of the node and re-deriving it on every promotion would mean a
configuration change and a seed change arriving together, with no way to attribute a score
difference to either.

agency: agent-autonomous.

---

## Batch 11 — candidate 1's configuration under three further combinations

```
result:              family_hierNB/candidate_spec.json
                     family_hierNB/eval.log
                     family_hierNB/eval.nc
                     family_hierNB/fitted_model.json
                     family_hierNB/model_configuration.yaml
                     family_hierNB/model_spec.json
                     family_hierNB/run_cost.json
                     family_ensemble/candidate_spec.json
                     family_ensemble/model_configuration.yaml
                     weighting_crpsWeighted/candidate_spec.json
                     weighting_crpsWeighted/model_configuration.yaml
script:              scripts/assemble_candidate_config.py
                     sha256:d8937abc233899a222ca45643766eeb4c2eb1e9b6f38680a17cb6a9b6430bfd9
invocation:          bash analysis/03_models/03_candidate/a_hierNB/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB
produced:            2026-08-28
```

**What it establishes.** The same configuration, assembled three more times: once for
candidate 1's own combination after the family fork moved, and twice as the configuration the
ensemble gives its candidate-1 member. In every one the assembled `model_configuration.yaml`
is **byte-identical** to the one this node wrote under `main` — the same options, the same
covariate list and the same component seed **849487747**, reached through a different
combination. That was checked by diff rather than assumed, and it is the property that lets
`c_ensemble/scripts/check_pool.py` match a member to a stored evaluation by configuration hash
instead of by combination name.

**This script was not changed in this batch**, and that is a decision rather than an omission.
Batch 10 logged that the shared part of the two candidates' assemblers belongs in
`03_models/scripts/lib/`, and batch 11 adds a third. Lifting it would change this file's
sha256, which is named in the record above for every one of the combinations it configured,
and their results would then name a script that never produced them. The lift is scheduled for
batches 13–14, where the frozen manifest re-runs every combination anyway.

alternatives-considered: as above, and in the plan's §4b.
agency: agent-autonomous

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/candidate_spec.json
                     results/$COMBO/model_configuration.yaml
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
node:                analysis/03_models/03_candidate/a_hierNB
produced:            2026-08-29
```

**What it establishes.** Assembled as a pool member under each row. No fork of this family moved in batch 13, so the configuration is the family's main path throughout; what differs is the dataset it is pointed at.

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
