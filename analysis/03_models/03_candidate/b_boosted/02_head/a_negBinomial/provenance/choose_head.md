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
commit:              PLACEHOLDER_COMMIT
instructions-commit: cf97b81
node:                02_head/a_negBinomial
produced:            2026-08-28
```

**What it establishes.** The main path's head, and the premise it is asked to carry: the target's variance-to-mean ratio runs from 2.9 to 842.4 across the provinces, against the 1.0 a Poisson would imply, so a single shared dispersion is spanning more than two orders of magnitude. The fitted dispersion is 0.313. It nevertheless yields the best-calibrated model of ours so far, because the width is `mu + mu^2/phi` around a mean the trees place per cell — a province the trees separate gets a different width by getting a different mean, which candidate 1's constant log-scale width could not do.

alternatives-considered: a Poisson head with no dispersion parameter (rejected before running by the premise this script computes — the ratio is nowhere near 1); squared-error loss on log1p(count) for the mean booster (rejected — its minimiser is a conditional median, which is not what a negative-binomial head is then built around); squared error on the raw count (rejected — it would fit Vientiane Capital and ignore the other fifteen provinces).
agency: agent-autonomous
