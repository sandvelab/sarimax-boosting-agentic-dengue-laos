# Claim

Can a spatio-temporal model of monthly dengue case counts across the admin-1 provinces of
Laos, developed as autonomously as this setup allows, forecast well enough under Chap's own
cross-validated backtest to beat a persistence and a seasonal-climatology baseline on mean
CRPS — and how far does that answer survive the reasonable alternatives to the judgment
calls made along the way?

The question has two halves and neither is subordinate. The forecasting half is settled on
a held-out year (2010) that is absent from the data development ever sees; the veridical
half is settled by the alternatives siblings in this tree and by the stability node that
runs them.

## Children

kind: sub-analyses
main-path: -

- `01_data` — what the dataset contains, and on what part of it development may happen.

_(The rest of the decomposition is designed in batch 5 of
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md` and built in batch 7.
`01_data` is here ahead of that because the plan's §3 requires the held-out year to be cut
off before anything else looks at the data, and the script that cuts it is a node like any
other.)_

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What the analysis yielded. Each answer belongs in the claim collection under
`Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The forecasting half, so far: no model of ours beats the field's own model, and the gap
is 2.2 CRPS.** `results/main/conclusion.json` records a skill score of **−0.101** for the
better of the two required baselines against the reference — 24.337 against 22.098 mean CRPS
over 371 cells in 16 provinces. The project has no candidate model yet, so that file records
`candidate_exists: false` and says in as many words that a baseline is standing in for one.

**The veridical half has produced its first substantive finding, and it constrains the
forecasting half.** The comparison this project's success criterion is written in can
resolve differences of about **4 CRPS** on the development backtest, which is wider than the
whole gap between the persistence baseline and the reference. Below **0.57 CRPS** nothing
can be attributed to a model at all, because that is how far the unseeded reference moves
against itself. A candidate that beats the reference by one or two CRPS here will not have
been shown to beat it. The evidence is at `04_score/03_compare`.

_(Every figure above is read from a file this tree produced. Nothing in this section states
a number that is not in `results/main/conclusion.json` or in the files it reads.)_
