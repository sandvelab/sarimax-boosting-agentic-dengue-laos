# Claim

Adapting chap-models/rwanda_random_forest's design (a random forest pooled across locations rather than fit per location) to stage 2, on the same lag-12 residual + calendar + lag-12 climate input as d_linearClimate: does pooling across provinces improve mean CRPS over stage 1 alone and over the per-province candidates already tried?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Mean CRPS: yes. Earns its place overall: no.** Pooling a random forest across all 17
modelable provinces into one shared fit per split, on `d_linearClimate`'s exact input, scores
**mean CRPS 25.89** over the same 371 cells — the first stage-2 candidate to beat stage 1
alone (26.05, **-0.63%**) and a clear improvement over `d_linearClimate` on the identical
input (26.85, **-3.57%**), isolating pooling as a real, if modest, source of the gain.
`results/conclusion.json`, `results/comparison.json`.

But empirical interval coverage **collapses to 64.4%** against the nominal 90% (every other
candidate stayed near stage 1's own 82.7-86.8%) — plan §2 is explicit that a mean-CRPS win
under broken calibration is not a win. `results/coverage_collapse_diagnosis.json` traces the
mechanism: **27.5% of this candidate's corrected forecasts are negative** (impossible for a
case count), 2.4-2.5x every per-province sibling's rate (10.8% for `a_linearLags`, 11.6% for
`d_linearClimate`) and 6.8x stage 1 alone's own rate (4.0%), and these are concentrated in the
lowest-case-count provinces (Pearson r = -0.53 between a province's mean case count and its
negative-forecast rate; two provinces averaging under 1 case/month have 18/24 cells corrected
into negative territory). The pooled correction function is shaped by the mixed-scale training
pool — provinces from under 1 to over 150 mean monthly cases fit together — and overshoots on
the low-count provinces it was not specifically tuned to, exactly the failure mode a per-
province fit cannot produce (each of those sees only its own scale).

**Net verdict**: pooling across provinces is the first change tried in this project that moves
mean CRPS in the right direction, but this implementation of it is not a candidate this project
can recommend — it trades calibration for a small point-metric gain in a way that plan §2 rules
out. This does not close the pooling question: a version that pools while preserving each
province's own scale (e.g. a province-level offset or per-province target standardisation
before pooling, neither tried here) is a plausible fix, logged as an untried refinement rather
than a rejected one — the *idea* of pooling is not falsified, this specific implementation of
it is. `04_stage2/claim.md` records this alongside the family/input axes it already tracks.
