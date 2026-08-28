# Provenance — b_quantileEnsemble's option specification

```
result:              head_quantileEnsemble/model_option_spec.json
script:              scripts/choose_head.py
                     sha256:6aa1100e84d0ac836b7c79f813d5e63fb8939e30c07cbbf77303af1b2f6fece6
invocation:          "$PYTHON" scripts/choose_head.py
                     (from the node directory, via run.sh; COMBO=head_quantileEnsemble, COMBO_BASE=main)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     (inherited from combination `main`, recorded as `input_from_combo`)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; this node makes a choice and measures the premise for it.
commit:              PLACEHOLDER_COMMIT
instructions-commit: cf97b81
node:                02_head/b_quantileEnsemble
produced:            2026-08-28
```

**What it establishes.** The sibling head, and the prediction registered before it ran: that every ladder level below the target's 56.3 % zero share cannot move off zero, because a pinball loss at those levels begins at the marginal quantile — zero — and finds a residual of exactly zero at the majority of rows, which is its kink. Eight of the fifteen levels were named. Seven turned out flat at zero across the whole file and the eighth in the province the prediction was about (`../../results/head_quantileEnsemble/head_premise_check.json`).

**This is the fork child that answers batch 4's open question**, and the answer is that the plain construction cannot be given a calibrated probabilistic head on this data — not because the boosters are weak but because the target is 56 % ties at zero and quantile regression has nothing to descend there. The failure is kept rather than repaired, per the plan's §3.

alternatives-considered: fitting the ladder only to the months that report, with a separate model for whether the month reports at all (rejected here — that is the hurdle construction candidate 1's `01_observation` fork promoted, and it would be a third child of this fork rather than a change to this one; a child quietly rebuilt until it worked would leave the tree with no record that the plain construction does not); a ladder stopping at 0.95 (rejected — the upper tail is where a dengue count model is most easily wrong, and stopping there would leave the top of every forecast to the extrapolation rule rather than to a fitted value); more levels (rejected on cost — fifteen boosters are already the most expensive thing in the batch, and the head loses on the middle of the distribution rather than on its resolution).
agency: agent-autonomous
