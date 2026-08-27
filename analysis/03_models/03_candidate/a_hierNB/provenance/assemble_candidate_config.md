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
