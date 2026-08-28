# Provenance — the pool's weights, equal

```
result:              main/model_option_spec.json
                     family_ensemble/model_option_spec.json
script:              scripts/choose_weighting.py
                     sha256:ffeee4029729af7cf4fdff9f93c48804c61b37fe15dfb739f0be8c20293199b4
invocation:          "$PYTHON" scripts/choose_weighting.py, with COMBO set
inputs:              analysis/04_score/03_compare/results/<combo>/leaderboard.csv
                     — read for the premise only. **No number from it reaches the model**:
                     this child sets one option, `weighting: equal`, and every weight in
                     the pool is 1/M whatever the leaderboard says.
environment:         environment/ (project main)
seeds:               none — nothing here is estimated or drawn
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble/01_weighting/a_equal
produced:            2026-08-28
```

**What it establishes.** The main path's weighting, and the prediction it was tested
against. The pool it produces scores 18.817 against the sibling's 22.838.

**The premise registered here was half wrong.** It predicted that an equal pool would score
worse than its best member, because half its mass sits on the two required baselines and
they are the two worst-scoring models of ours; the pool beat its best member by 1.954 CRPS
(`../../results/main/pool_check.json`). The prediction reasoned about where the forecasts
sit and not about how wide they are, and CRPS is a function of both. Its other half — that
the pool would be wider than any member and would over-cover — held exactly.

**Why reading the leaderboard here is analysis and not fitting.** What the members scored is
already a reported result of this project. Reading it to write down what one expects to
happen is what a registered prediction is. Letting one of those numbers set a weight would
be something else entirely, and it is precisely what the sibling does — from a validation
period held back inside the training frame, never from these figures.

alternatives-considered: weights proportional to 1/CRPS on the leaderboard (rejected here
and not built at all — it would fit weights on the period the model is scored on, which is
the one construction this project cannot report); leaving the premise out and letting the
score speak (rejected — a prediction written after the number is not a prediction, and this
one turned out to be the batch's most informative wrong answer).
agency: agent-autonomous
