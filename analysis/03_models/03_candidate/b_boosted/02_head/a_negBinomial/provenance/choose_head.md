# Provenance — a_negBinomial's option specification

```
result:              family_boosted/model_option_spec.json
                     features_richCalendar/model_option_spec.json
script:              scripts/choose_head.py
                     sha256:f21d06d93c95ddbf457d99ee8fda8499d7bcb35fd09f66bc3666e87762da4563
invocation:          "$PYTHON" scripts/choose_head.py
                     (from the node directory, via run.sh; COMBO=family_boosted, COMBO_BASE=main)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     (inherited from combination `main`, recorded as `input_from_combo`)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; this node makes a choice and measures the premise for it.
commit:              6cb1163
instructions-commit: cf97b81
node:                02_head/a_negBinomial
produced:            2026-08-28
```

**What it establishes.** The main path's head, and the premise it is asked to carry: the target's variance-to-mean ratio runs from 2.9 to 842.4 across the provinces, against the 1.0 a Poisson would imply, so a single shared dispersion is spanning more than two orders of magnitude. The fitted dispersion is 0.313. It nevertheless yields the best-calibrated model of ours so far, because the width is `mu + mu^2/phi` around a mean the trees place per cell — a province the trees separate gets a different width by getting a different mean, which candidate 1's constant log-scale width could not do.

alternatives-considered: a Poisson head with no dispersion parameter (rejected before running by the premise this script computes — the ratio is nowhere near 1); squared-error loss on log1p(count) for the mean booster (rejected — its minimiser is a conditional median, which is not what a negative-binomial head is then built around); squared error on the raw count (rejected — it would fit Vientiane Capital and ignore the other fifteen provinces).
agency: agent-autonomous

---

## Batch 11 — the same choice under the ensemble's three combinations

```
result:              main/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_head.py
                     sha256:f21d06d93c95ddbf457d99ee8fda8499d7bcb35fd09f66bc3666e87762da4563
invocation:          bash analysis/03_models/03_candidate/b_boosted/02_head/a_negBinomial/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              PENDING
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/b_boosted/02_head/a_negBinomial
produced:            2026-08-28
```

**Why these combinations exist.** All three are combinations of the ensemble, and this step
ran under them because **the pool configures its candidate-2 member from these same fork
nodes**. `main` is among them for the first time: batch 11 promoted `c_ensemble` to the main
path, so `analysis/run.sh` now reaches candidate 2 — as a member of the pool, through
`c_ensemble/scripts/prepare_members.py`, and not as a model on `main`'s leaderboard. There is
no `model_spec.json` under `main` at this node and there should not be: candidate 2 is a
sibling alternative and is evaluated on its own under `family_boosted`.

**Nothing here chose anything new.** The child that ran is the one this fork already declared
as its main path, and its specification under each combination differs from the one it wrote
under `family_boosted` in exactly one line — the `combo` field naming the combination.
Verified by diff.

alternatives-considered: as in the parallel record at candidate 1's forks.
agency: agent-autonomous
