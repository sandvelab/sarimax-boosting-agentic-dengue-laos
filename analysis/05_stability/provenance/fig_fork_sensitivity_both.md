# Provenance — the fork ranking on both datasets

```
result:              results/fig_fork_sensitivity_both.png
                     results/fig_fork_sensitivity_both.csv
script:              scripts/fig_fork_sensitivity_both.py
                     sha256:0bb70d44d5379d14abb27c1471d2913a178c478fe7f3d77ea98154ed4d58e111
invocation:          "$PYTHON" scripts/fig_fork_sensitivity_both.py
                     (from 05_stability/, via run.sh)
inputs:              analysis/05_stability/results/fork_sensitivity_both.csv
                     analysis/05_stability/results/distribution.json
                     analysis/05_stability/results/holdout_distribution.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              609e1be
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: one noise band for both sets of bars. Rejected for the reason
                     report_distribution.py gives: each band is a measurement of the
                     reference's own sampler on one dataset, and the two are 0.0218 and
                     0.0140. The figure draws both lines.
agency:              agent-autonomous.
```

**What it establishes.** Fourteen of the seventeen forks fall on the same side of their own
dataset's band on both. The three that do not are the pool's weighting and the persistence
construction, which matter on development only, and the hierarchical model's covariate set,
which matters on 2010 only. The bar that grows is the province filter, from 0.0376 to
0.2696; the bar that shrinks most is the pool's weighting, from 0.1820 to 0.0121.

Plotted values are beside the image. The per-combination moves each bar takes a maximum over
are in `fig_fork_sensitivity_preaggregation.csv` and its holdout twin.
