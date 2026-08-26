# Provenance — the leaderboard and the paired comparison against the reference

```
result:              results/main/leaderboard.csv
                     results/main/paired_vs_reference.csv
                     results/main/paired_summary.csv
                     results/main/paired_by_split.csv
                     results/main/reference_repeat_noise.csv
                     results/main/comparison_notes.json
script:              scripts/compare_models.py
                     sha256:6d6748b30ef2c185f6742f1e7586f3f85f4c5614f4dd6b200b94c97e2d8ae9d2
invocation:          "$PYTHON" scripts/compare_models.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/04_score/01_collect/results/main/metrics_cell.csv
                     analysis/04_score/01_collect/results/main/models.csv
                     analysis/04_score/02_aggregate/a_unweighted/results/main/metrics_summary.csv
                     (resolved by searching for the one child of 02_aggregate with
                     results under this combination)
                     analysis/03_models/**/results/main/run_cost.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every figure is a deterministic statistic of stored per-cell
                     scores. No resampling is used: the clustered standard errors are
                     computed in closed form, which is why there is nothing to seed.
                     Project seed 20260822 unused.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-26
```

**What it establishes.** Two things. The leaderboard, assembled from the stored scores and
the stored run costs, which is the file phase C adds candidates to and the one the plan
requires never to be typed. And the answer to the question batch 4 left open and batch 5
made this batch's reason for existing: **whether a paired per-cell comparison on 371 cells
can separate two models at all.**

**Why paired, and why four ways.** Batch 4 measured the split-to-split standard error of the
reference's own CRPS at 5.65, a quarter of its mean, and observed that no plausible model
difference clears that. But that variation is mostly the difficulty of the period, common to
both models, and it cancels cell by cell. What is left is what this node measures, and it
measures it four ways because the easy answer is the wrong one:

- the per-cell standard error, which assumes 371 independent observations. They are not
  independent — three lead times of the same forecast and neighbouring months of the same
  province move together — so this figure flatters the comparison and is reported as the
  optimistic bound rather than as the answer;
- the same standard error clustered by province and by split, which allows arbitrary
  correlation inside a cluster. With sixteen provinces and eight splits this is a small
  number of clusters, so it is indicative rather than exact;
- the comparison at the split level, over eight paired numbers, which needs no independence
  assumption inside a split at all;
- **the noise floor**: the identical paired statistic computed between two repeats of the
  reference against itself. Because the reference is unseeded, two of its repeats differ by
  its sampler and by nothing else, so the largest paired difference among its own repeats is
  a difference this evaluation demonstrably cannot attribute to a model. It is the
  comparison's resolution, computed in the same units as the comparison, on the same cells.

**No significance test is reported and none is implied.** The plan settled before any number
existed that statistical significance is not attainable here and is not to be suggested
(§4b, human-set). What is reported is the spread and a plain statement of what it can
distinguish; "we cannot separate these two" is one of the answers.

alternatives-considered: a paired bootstrap over provinces would give a confidence interval
without the closed-form clustering assumption and was not run — it would introduce
randomness into a node that currently has none, and with sixteen clusters it would be
resampling the same small set. It is the obvious extension if the clustered figures turn out
to be load-bearing, and it is recorded here as not run rather than not considered. A
Diebold-Mariano test was rejected: it is a significance test, and the plan forbids implying
significance. Comparing against each reference repeat separately *instead of* against their
mean was rejected in favour of doing both — the mean is the denominator the conclusion uses
and the per-repeat comparisons are what calibrate it.

agency: agent-autonomous. That the comparison must be paired rather than unpaired is batch
4's finding (agent-autonomous, recorded there); computing it, and computing the noise floor
from the reference's own repeats rather than assuming a resolution, is this batch's.
