# Provenance — whether two judgment calls add up

```
result:              results/fig_pair_interaction.png
                     results/fig_pair_interaction.csv
                     results/fig_pair_interaction_preaggregation.csv
script:              scripts/fig_pair_interaction.py
                     sha256:210a8789292e6c090380901cb0dfad8a4c3b1ef664203f49b78b25b4a902bd2f
invocation:          "$PYTHON" scripts/fig_pair_interaction.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/05_stability/results/conclusions.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     matplotlib from the same environment
seeds:               none; a deterministic drawing of stored values.
commit:              9ad6578
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** The answer to the question tier 2 was built to ask: can the
one-at-a-time table be added up? Each of the eight pairs is plotted at its additive
prediction against what taking both actually did, and the diagonal is where a pair would sit
if its two forks did not interact.

**None of the eight is on the diagonal**, and the largest departure — **−0.1033**, the
province filter with case weighting — is larger than either main effect behind it. Each
improves the reported skill alone, by +0.0376 and +0.0835, and together they come to +0.0177
against an additive +0.1211. Both work by re-weighting what the mean is over, and taking
both does not do it twice.

**The two pairs above the axis are the two that involve case weighting on a setup fork**,
and they are the two that fall furthest below the diagonal; the six below the axis sit
close to it, within +0.042 to −0.018. So the interaction is not a general property of the
set: it is concentrated where two forks reach the same mechanism.

**Pre-aggregation** is `fig_pair_interaction_preaggregation.csv`: the two tier-1 rows behind
each point, with the move each contributed, so the horizontal coordinate can be checked
against its two addends without recomputing anything.

alternatives-considered: **plotting the interaction directly against the pair index** —
rejected, because the quantity that matters is the interaction *relative to* the main
effects behind it, and a bar chart of interactions alone cannot show that the largest one
exceeds both of them. **Including the tier-1 rows on the same axes** — rejected: a tier-1
row has no additive prediction to be compared against, so it would sit on the diagonal by
construction and suggest a stability the figure is not measuring.

agency: agent-autonomous.
information: agent-retrieved — plotted from `conclusions.csv`, whose `interaction` column
`collect_conclusions.py` computes as a subtraction on its own columns.
