# Provenance — b_richCalendar's option specification

```
result:              features_richCalendar/model_option_spec.json
script:              scripts/choose_features.py
                     sha256:ca3bf44f0fc22e365cd407ea5b5caddfdbc726d9fd0754f1a60339f2c0f30c7c
invocation:          "$PYTHON" scripts/choose_features.py
                     (from the node directory, via run.sh; COMBO=features_richCalendar, COMBO_BASE=main)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     (inherited from combination `main`, recorded as `input_from_combo`)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; this node makes a choice and measures the premise for it.
commit:              PLACEHOLDER_COMMIT
instructions-commit: cf97b81
node:                01_features/b_richCalendar
produced:            2026-08-28
```

**What it establishes.** The sibling's feature set — twenty-seven columns — and, registered before the run, the two costs expected of it: sixteen provinces as an identifier are fifteen extra cuts available on about two thousand rows, and a year index is a feature every forecast month falls beyond, so trees can only lose by it. The run scored 20.375 against the main path's 20.771, better by less than the evaluation can resolve, with a worse point forecast and wider intervals — consistent with both expectations, and not separating them.

alternatives-considered: making each of the four additions its own fork (rejected — four forks whose siblings all re-run in phase D, to resolve a question this fork asks in one; if the fork had moved the model, splitting it would have been the next batch's work and it did not); one-hot rather than ordinal province coding (rejected — the boosters split on order and an ordinal code lets one cut separate a group of provinces, which is what a tree is for; a one-hot coding would have been sixteen columns saying the same thing).
agency: agent-autonomous
