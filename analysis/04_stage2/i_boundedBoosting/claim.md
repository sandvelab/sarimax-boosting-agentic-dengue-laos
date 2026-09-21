# Claim

g_oosErrorBoosting with its correction additionally bounded relative to stage 1's forecast level (|correction| <= max(stage-1 mean, 10)), the refinement the Savannakhet loss motivated: does bounding the correction where stage 1's spread is miscalibrated earn its place, and does it turn the large-province losses around?

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

**Yes, and it turns the Savannakhet loss around.** Mean CRPS **24.53** against stage 1
alone's 26.05 (**−5.85%**) and against `g_oosErrorBoosting`'s 25.16 (−2.52%, the bound being
the only change), coverage 85.7% (unchanged from g; stage 1: 82.7%), **7 of 8 splits**
improved (the most of any candidate) and 57.1% of cells (`results/conclusion.json`,
`results/comparison.json`). Stage 1 verified cell for cell against `02_stage1` (408/408).

Bounding the correction at max(stage-1 mean, 10) does what the batch-10 diagnosis said it
would: Savannakhet goes from +211 CRPS-units summed under g to +25, and Vientiane Capital from
+127 to +104, while the provinces that gained keep their gains (Khammouane −292, Salavan −275,
Bokeo unchanged). By horizon 18.75 / 23.71 / 31.12 — better than g at every horizon,
including one month ahead, where g lost to stage 1. The floor of 10 cases is a judgment call
(a correction must remain possible where the forecast is near zero) and a perturbation for
the v2 stability manifest.

Not the main path: `h_levelOnlyBoosting` scores lower on the pre-registered rule's first
criterion (24.35 vs 24.53). The bound's own contribution on top of the minimal input is small
(`j_levelOnlyBoundedBoosting`: −0.26% against h), because the minimal input already removes
most of the Savannakhet correction.
