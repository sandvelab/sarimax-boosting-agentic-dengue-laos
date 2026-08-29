# Claim

Estimate each province's calendar-month distribution once, from the training period alone, and hold it fixed across every split rather than re-estimating from the expanding historic frame. The baseline then knows only what it knew at fitting time, which is what a model fitted once and deployed actually has.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**Freezing the table costs 0.532 CRPS — 24.869 against the expanding window's 24.337**
(`analysis/04_score/03_compare/results/climatology_frozenWindow/leaderboard.csv`) — which is
*inside* the 0.565 floor below which nothing on this dataset can be attributed to a model.
Calibration moves as little: 10–90 coverage 0.639 against 0.650, 25–75 coverage 0.520 against
0.542.

**Two dengue seasons of data are worth nothing measurable to this baseline.** The training
frame ends 2007-12 and the evaluation runs through 2009-12, so this model forecasts two
seasons it has never seen, on a series whose reporting improved throughout — and the
difference does not clear the noise. The node's own claim argued before the run that the
choice mattered *because* of that gap. It does not, and that is the answer.

**Its effect on the reported model is smaller still**: the pool moves from 18.817 to 18.872,
skill +0.1485 to +0.1460. This is the smallest move of any tier-1 row run so far, and its
sibling fork's row is the largest.
