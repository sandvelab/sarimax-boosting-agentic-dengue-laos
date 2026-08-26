# Provenance — per-cell scores for every model that ran

```
result:              results/main/metrics_cell.csv
                     results/main/models.csv
script:              scripts/collect_metrics.py
                     sha256:1b9e3e5028e142ed03d27a2624b6c74a79c2cf5a933394ecd96cb562e21b6422
invocation:          "$PYTHON" scripts/collect_metrics.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              every model node's evaluation for this combination, discovered by
                     globbing analysis/03_models/**/results/main/model_spec.json rather
                     than by being listed:
                       01_baselines/01_persistence/a_empiricalChange/results/main/eval.nc
                       01_baselines/02_climatology/a_expandingWindow/results/main/eval.nc
                       02_reference/results/main/eval_repeat_{1,2,3,4}.nc
                     with the per-model input hashes in each node's own model_spec.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0.
                     The metrics are chap-core's own registered metrics, asked for by
                     id; pinning chap-core pins them.
seeds:               none. Every value is read out of a stored evaluation file; the
                     script computes no statistic of its own beyond a mean over the
                     reference's repeats. Project seed 20260822 unused.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/04_score/01_collect
produced:            2026-08-26
```

**What it establishes.** One file at the platform's finest resolution — one row per model,
province, target month and lead time, carrying CRPS, absolute error, both interval
indicators and the observed value — from which every reported figure in the project is an
aggregation. Nothing downstream re-derives a score, so no two reported numbers can disagree
about what a model scored.

**This node implements no metric.** Every value comes from chap-core's own registered metric
class, asked for by id (`crps`, `mae`, `coverage_10_90`, `coverage_25_75`) at its detailed
resolution. The only things the script chooses are the level of aggregation — the finest one
available — and the split label, recovered by the arithmetic batch 2 established,
`split = time_period − (horizon_distance − 1)`. A metric of our own would be the one we
could most easily bend without it being visible, which is why §4b rules it out for this
project.

**Models are discovered, not listed.** A model reaches this file by having run, and by no
other route. That is what makes the node indifferent to which child of a fork produced a
model — exactly one child has results under any one combination — and it is what will let
phase C add a candidate without editing the scoring node.

**The unseeded reference is carried twice over.** Each of its four repeats becomes its own
row (`reference_r1` … `reference_r4`), and a further row (`reference`) holds the per-cell
mean over them. Every repeat scored the identical cells, so the mean is an average over
draws of the same quantity rather than over different evaluations. Downstream, the mean is
the denominator of the skill score, which stops a 2 % wobble in an external model's sampler
being read as an effect of one of our own choices; the individual repeats are what say how
large that wobble was here.

alternatives-considered: the reference's repeats could have been reduced to a mean here and
the repeats discarded, which would have halved this file. Rejected — the repeat-to-repeat
spread is the noise floor of the entire comparison and it has to be recomputable from stored
scores rather than quoted from batch 4. Aggregating to province level in this node was also
rejected: the paired comparison needs per-cell rows, and an aggregation that cannot be
undone is a decision taken at the wrong time. Accumulating rows into an existing file, which
is what the vertical slice's version did, was replaced by rebuilding from the discovered
specs, because an accumulating file can hold a row from a model that no longer exists.

agency: agent-autonomous. That the metric is always chap-core's is §4b's decision from batch
2; the discovery mechanism and the treatment of the reference's repeats are this batch's,
implementing batch 5's design.
information: agent-retrieved — chap-core's metric API surface was established in batch 2.
