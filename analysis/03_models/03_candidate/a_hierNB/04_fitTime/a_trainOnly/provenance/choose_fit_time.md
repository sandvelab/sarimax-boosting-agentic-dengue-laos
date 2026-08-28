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

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

This fork did not move in batch 9: its best sibling stayed inside the 0.57 CRPS floor, so
this child is still the main path. `results/main/model_option_spec.json` was regenerated
anyway, because every combination re-runs the whole candidate and because the
specification gained an `input_from_combo` field -- which records, for a combination that
inherits the common ground it did not move, where that ground came from. On `main` it
reads `main`, because `analysis/run.sh` sets no base and can inherit nothing.

The siblings built and run in batch 9 are named in their own records. Their scores from
the promoted main path: `b_refitAtPredict` +0.873, the best combination in the second sweep and outside the floor
(`AI-generated/candidate-forks/round2_promoted/fork_interaction.csv`).

script sha256: 55205731fdb2cf1e963cd991d25d18aa2ba44a04322f145bb7d65f8b2e7b69eb

agency: agent-autonomous.

---

## Batch 11 — the same choice under three further combinations

```
result:              family_hierNB/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_fit_time.py
                     sha256:55205731fdb2cf1e963cd991d25d18aa2ba44a04322f145bb7d65f8b2e7b69eb
invocation:          bash analysis/03_models/03_candidate/a_hierNB/04_fitTime/a_trainOnly/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              PENDING
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/04_fitTime/a_trainOnly
produced:            2026-08-28
```

**Why these combinations exist.** `family_hierNB` is candidate 1's own combination: batch 11
promoted the family fork to `c_ensemble`, so candidate 1 no longer runs under `main` and its
results live under a combination of its own, exactly as candidate 2's have since batch 10.
`family_ensemble` and `weighting_crpsWeighted` are the ensemble's two combinations, and this
step ran under them because **the pool configures its candidate-1 member from these same fork
nodes**: `c_ensemble/scripts/prepare_members.py` runs each family's fork main-path children
and that family's assembler under the running combination, rather than pointing the pool at a
configuration assembled somewhere else. That is what makes a perturbation of this fork move
the pool's member with it in phase D.

**Nothing here chose anything new.** The child that ran is the one this fork already declared
as its main path, and the specification it wrote under each of the three combinations differs
from the one it wrote under `main` in exactly one line — the `combo` field naming the
combination — because the step reads the dataset and nothing else. Verified by diff.

alternatives-considered: pointing the pool at the configuration stored under `main` instead of
assembling one under the running combination (rejected — the pool would then be configured
from a combination it is not running under, and a perturbation that moved this fork would
leave the pool's member behind).
agency: agent-autonomous
