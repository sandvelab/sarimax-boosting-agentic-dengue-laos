# Provenance — whether fitting happens in train or in predict

```
result:              results/main/model_option_spec.json
script:              scripts/choose_fit_time.py
                     sha256:6b3d30a6c52d9f6691a8af529d25979390fcc4b6a16277e4b6908590c3220b1d
invocation:          "$PYTHON" scripts/choose_fit_time.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so the combination is
                     `main` and results go to results/main/.)
inputs:              analysis/02_setup/results/main/setup_spec.json — the assembled
                     evaluation flags, from which the stage reads n_retrain rather than
                     assuming it
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and reads four flags; project seed
                     20260822 has no surface here.
commit:              4563baf
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/04_fitTime/a_trainOnly
produced:            2026-08-27
```

**What it establishes.** Under the assembled flags — `n_retrain 1`, eight splits at stride
3 — one fit serves every split, and by the last split there are **21 months** of observed
history the fit never saw. That figure is read from the flag file rather than assumed,
because "fit once" only means what it says while `n_retrain` is 1, and `02_setup/04_retrain`
is a fork that can move it. A combination that moved it would leave this specification
recording `one_fit_serves_every_split: false` rather than quietly claiming otherwise.

**What is given up.** Chap hands `predict` an expanding historic window at every split, and
this child ignores it. The reference model refits inside predict, which is one reason its
score and ours are not comparable in the way two fits of one model would be — and is why
this is a fork rather than a convention.

alternatives-considered: `b_refitAtPredict`, retained as an unbuilt sibling until batch 9. It
costs a fit per split — about eight times this model's fitting time, which is two seconds —
and it makes the model a different model at each split, which is a property the stability
work should measure rather than a cost to avoid.

agency: agent-autonomous. Batch 4 raised refitting-at-predict as an open question (§9.2) and
batch 5 made it a fork; taking the cheaper child as the main path at the defaults is this
batch's.
