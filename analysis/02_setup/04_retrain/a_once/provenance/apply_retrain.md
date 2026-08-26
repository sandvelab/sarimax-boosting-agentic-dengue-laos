# Provenance — the retrain policy, at the platform's default

```
result:              results/main/analysis_dataset.csv
                     results/main/setup_spec.json
script:              scripts/apply_retrain.py
                     sha256:fcf062fdf92ecebec845d38281505cd0933b650fb8e7a303d3ec3ae08b5e63fa
invocation:          "$PYTHON" scripts/apply_retrain.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/02_setup/03_provinces/a_chapFilter/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage sets a flag and passes the dataset through.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/02_setup/04_retrain/a_once
produced:            2026-08-26
```

**What it establishes.** `n_retrain = 1` reaches `chap eval` from a file. That is the whole
point of the stage: before it, the flag was a constant inside whichever script happened to
call the platform, and two model scripts could have disagreed about it without anything
noticing. Now every model reads it from the assembled setup, and a combination that changes
it changes it for all of them at once.

**What the flag does not guarantee.** `n_retrain` governs how often chap-core calls `train`.
A model that does its fitting inside `predict` refits at every split regardless — which is
what the reference model does, since its `train.R` is a placeholder and the INLA fit runs in
`predict.R` (batch 4). So this stage fixes the platform's behaviour and not the models', and
whether our own candidates refit at predict time is a separate, candidate-internal fork.
Recording that distinction here is the point: it would otherwise look as though one flag had
made all the models comparable in this respect, and it has not.

alternatives-considered: refitting at every split (`b_everySplit`) is the sibling, built in
phase D. It is the more expensive side — it multiplies every model's cost by the number of
splits — which is a reason to have measured it rather than to have assumed which side is
right. Making `n_retrain` part of batch 3's fixed triple was rejected in batch 5: the triple
fixes what is evaluated and this does not.

agency: agent-autonomous. That `n_retrain` was left at the default and flagged as a fork is
batch 3's; building it as a node so the flag travels in a file is the agent's.
