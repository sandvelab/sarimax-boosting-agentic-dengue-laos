# Provenance — the headline mean weighted by observed cases

```
result:              results/$COMBO/metrics_summary.csv
                     results/$COMBO/crps_by_location.csv
                     results/$COMBO/crps_by_split.csv
                     results/$COMBO/crps_by_region_split.csv
                     results/$COMBO/crps_by_horizon.csv
                     results/$COMBO/weights.csv
                     results/$COMBO/weighting_notes.json
script:              scripts/aggregate_caseWeighted.py
                     sha256:c320eb5e47918b2a098752f919942dd9c0a839af43e023cf3999833c317380b6
                     analysis/04_score/scripts/lib/aggregate.py
                     sha256:93dfb354e605db7bd7f281de89e66b06a8bc3201e4454f34aa4c2d45e502cef0
invocation:          "$PYTHON" scripts/aggregate_caseWeighted.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=aggregate_caseWeighted and COMBO_BASE=main.)
inputs:              analysis/04_score/01_collect/results/$COMBO/metrics_cell.csv
                     — the weights and the scores come from the same file, so the weight
                     is the value the models were scored against and not a second
                     extraction of the data
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. Every figure is a weighted groupby of a stored file.
commit:              ce0eb34
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/04_score/02_aggregate/c_caseWeighted
produced:            2026-08-29
```

**What it establishes.** Under case weighting the pool scores **88.484** against the
reference's **115.216** — a skill score of **+0.2320**, the largest in tier 1 so far
(`analysis/results/aggregate_caseWeighted/conclusion.json`). But the row's substantive result
is not that number, it is what stands beside it: **persistence scores 86.598**, better than
the pool. On the months where dengue was actually happening, the simplest baseline in the
project forecasts better than the model this project reports.

**And the calibration inverts.** Our pool is over-dispersed everywhere else — 10–90 coverage
0.863 against nominal 0.80 on the main path. Weighted by cases it is **0.701**, under-dispersed.
The pool is too wide on the quiet months that dominate the unweighted mean and too narrow on
the outbreak months that dominate this one, and neither summary alone shows that.

**What the weighting does to the sample.** **137 of 371 cells carry zero weight** — 37 % of the
evaluated cells are silenced because nothing was observed in them. The Kish effective sample
size falls to **65**, the top decile of cells carries **62.3 %** of the weight, and 8
model-by-province groups and 240 model-by-province-by-split groups have no weighted mean at all
and are reported missing rather than zero (`results/$COMBO/weighting_notes.json`). This is the
opposite blind spot to the unweighted mean's, not a correction of it, and the file says so in
numbers.

alternatives-considered: **a floor on the weight**, so that zero-case cells still count for
something — rejected because any floor is a second free parameter that decides how much of the
answer comes from the quiet months, and choosing it is the judgment the fork exists to expose
rather than to settle. **Weighting by observed cases plus one** — the same objection in a
tidier form. **Weighting by the reference's forecast rather than the outcome**, which would
avoid conditioning on the thing being predicted — rejected because it makes the summary depend
on a model, and a weighting that depends on one of the models being compared is not a
comparison. That the weight is a function of the outcome is a real cost of this child and it is
stated in the script rather than defended away. **Weighting the paired comparison as well** —
not done; the same gap as the sibling records, and for the same reason.

agency: agent-autonomous. The fork and its claim are batch 5's and batch 12's; the choice to
take the weight from the scored file, the treatment of zero-weight groups as missing, the
rejection of a weight floor and the concentration diagnostics are the agent's.
information: agent-retrieved — both the weights and the scores are read from `01_collect`'s
per-cell file at run time.
