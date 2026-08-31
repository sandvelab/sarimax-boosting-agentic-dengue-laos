# Provenance — what the manifest predicted a row would cost, against what it cost

```
result:              results/cost_planned_vs_actual.csv
                     results/cost_planned_vs_actual.json
script:              scripts/compare_planned_cost.py
                     sha256:ba7d8a857fcb26541a5e3a66747260092e6e25adcada61ee67320b78dd006135
invocation:          "$PYTHON" scripts/compare_planned_cost.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Not combination-scoped: it describes
                     every combination and belongs to none.)
inputs:              analysis/05_stability/results/manifest.csv **at commit 2e186f6**,
                     read with `git show` — the manifest as it stood before any tier-1
                     row had run
                     analysis/05_stability/results/run_status.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              6a68f23
instructions-commit: 030bee2
node:                analysis/05_stability
produced:            2026-08-29
```

**Why the prediction has to be read out of git.** `plan_manifest.py` re-reads every model's
`run_cost.json` on each run, so once a row has run, the manifest's estimate for that row
silently becomes a measurement of it. Comparing the current manifest to the current run
record would compare a number to itself. The only place the prediction survives is the
committed manifest, which is one of the things committing it before the run was for.

**What it establishes.** Over the seven batch-13 rows, planned **6 041 s** against actual
**5 901 s** — a ratio of **0.977**. The aggregate is good to two per cent and **every
individual row is wrong**: the ratios run from **0.577** on `trainingWindow_from2004` to
**1.851** on `retrain_everySplit`, and actual costs span 694 s to 2 226 s where the manifest
predicted **1 202.9 s for all five setup rows alike**.

**Why, and why it matters.** The frozen cost model summed a row's parts as measured under
`main`. Nothing in it knew that a row can change how much work a part does — and
`retrain_everySplit` does exactly that, setting `n_retrain` to the split count so the
reference model runs sixteen jobs per repeat instead of two. The manifest's cut order is
ranked on these estimates, so on this evidence **the cut order within a kind is ranked on a
constant** and carries no information. It has never been used, because nothing was cut; the
point is that it could not have been relied on if it had been.

alternatives-considered: **quoting the comparison in the batch report from the two tables** —
rejected under Rule 1: it is a reported figure, so it comes from a file that was executed.
**Re-costing the manifest now that seven rows have measurements** — deliberately not done
here. It would improve the remaining estimates and it would also overwrite the frozen
prediction, and the frozen prediction is the more interesting artifact. `plan_manifest.py`
re-costs on every run anyway; this file is what preserves what it replaced.

agency: agent-autonomous. That the cost model would be tested by the first rows to run is
implicit in batch 12's design; writing the test as a script rather than as a remark in a
report is the agent's.
information: agent-retrieved — both inputs are files, one of them via `git show`.


---

## Batch 15 — the comparison over the whole manifest

```
result:              results/cost_planned_vs_actual.csv
                     results/cost_planned_vs_actual.json
script:              scripts/compare_planned_cost.py — unchanged by this batch
invocation:          environment/chapenv/bin/python \
                       analysis/05_stability/scripts/compare_planned_cost.py
inputs:              results/manifest.csv (via git, at the commit that froze it),
                     results/run_status.csv
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none
commit:              f3904c5
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** The comparison batch 14 left stale: it ran twenty-three rows and
this file still described the nine batches 13 and 22 had run. Over the whole manifest the
**total is exact — 7 469 s planned against 7 469 s actual, a ratio of 1.00** — and the worst
row is now `weighting_crpsWeighted` at **1.91**, replacing `retrain_everySplit` at 1.85.

**The finding does not change and gets sharper.** A cost model that is right to three
significant figures in total and wrong by a factor of two on individual rows is a cost model
whose rank order carries no information, and the rank order is what the cut order would have
been drawn on. Nothing was cut, so nothing rests on it; what rests on it is the next
project that builds a manifest this way and does cut.

**The measured total for the whole development set is 13 172 s, or 3.66 h** — the sum of
`run_status.csv`, which covers all thirty-two rows including the two that failed on their
first attempt. That is the figure `distribution.json` carries. Batch 14's report and
`readme-at-start.md` said "about 3.2 hours"; this file is where the number comes from and
3.66 h is what it says.

alternatives-considered: none at this node. The script was written in batch 13 to be re-run
whenever more rows have run, and this is that.

agency: agent-autonomous.
information: agent-retrieved — read from the two files named above.
