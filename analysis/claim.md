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

- `01_data` — what the dataset contains, on what part of it development may happen, and,
  once, the file phase E evaluates on.
- `02_setup` — the common ground every model faces: one dataset and one set of evaluation
  flags, through four forks in sequence.
- `03_models` — the required baselines, the reference model, and our candidates.
- `04_score` — collecting the per-cell scores, aggregating them, and comparing the models.
- `05_stability` — the alternatives the main path did not take, run as a frozen set on both
  datasets, and reported as a distribution.

_(The decomposition was designed in batch 5 of
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md` and built in batch 7.
`01_data` was here ahead of that because the plan's §3 requires the held-out year to be cut
off before anything else looks at the data, and the script that cuts it is a node like any
other. `analysis/README.md` is the full map.)_

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What the analysis yielded. Each answer belongs in the claim collection under
`Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The forecasting half: yes, on both datasets, and by a margin the evaluation cannot
separate.** The reported model is candidate 3, a linear opinion pool over two candidate
families and both required baselines. On the development backtest it scores **18.817** mean
CRPS against the reference model's 22.098 — a skill score of **+0.1485** — and beats both
required baselines. On the held-out year, which was opened once and evaluated on a set of
analyses frozen beforehand, it scores **76.731** against the reference's **84.026**, a skill
score of **+0.0868**, and again beats both required baselines.
→ `results/main/conclusion.json`, `results/main__holdout/conclusion.json`

**Nothing here reaches significance and nothing pretends to.** The pool is 1.90 standard
errors from the reference on development and less than one on the holdout, where the
backtest is four splits rather than eight. The reference is unseeded, and below **0.57 CRPS**
on development and **1.30** on the holdout nothing can be attributed to a model at all,
because that is how far the reference moves against itself. "We cannot separate these two" is
the honest reading of the margin, and it is the reading. → `04_score/03_compare`

**The veridical half is the larger result, and it is a distribution rather than a number.**
Thirty-two analyses that all looked reasonable were fixed before either dataset was scored.
On development the skill score runs **−0.0724 to +0.2320** around the reported +0.1485, which
sits thirteenth of thirty-two. On the held-out year it runs **−0.5038 to +0.2026** around
+0.0868, eighteenth of thirty-two — **a spread more than twice as wide**.
→ `05_stability/results/distribution.json`, `holdout_distribution.json`

**Most of the effort went below the resolution of the evaluation.** Six of the seventeen
judgment calls the tree carries move the conclusion further than the reference model moves on
its own; eleven do not, and nine of those eleven are the candidate-internal forks phase C
spent three of its four batches choosing among.
→ `05_stability/results/sensitivity_by_fork.csv`

**The development set is a weak guide to the held-out year.** Twenty-eight of the thirty-two
analyses scored worse on 2010, and the rank correlation between the two skill scores is
**+0.396**. The fork ranking transfers better, at +0.679, with 14 of 17 forks agreeing on
whether they matter — but the largest single effect on the holdout, the province filter at
0.2696, was fourth and nearly negligible on development — and the analysis behind it ranked
fourth of thirty-two there, highest of every analysis that does not re-weight the headline
mean, against twenty-ninth on the held-out year.
→ `05_stability/results/holdout_vs_development.json`, `fork_sensitivity_both.csv`

**Calibration is reported beside the score and not under it**, because a badly calibrated
CRPS winner has not won. The reported model is the most over-dispersed in the project on
development — 10–90 coverage 0.863 against a nominal 0.80 — and 0.755 on the holdout; across
the frozen set, coverage runs 0.458 to 0.920 on development and 0.210 to 0.854 on 2010.

_(Every figure above is read from a file this tree produced. Nothing in this section states a
number that is not in `results/main/conclusion.json`, `results/main__holdout/conclusion.json`
or the files those name.)_
