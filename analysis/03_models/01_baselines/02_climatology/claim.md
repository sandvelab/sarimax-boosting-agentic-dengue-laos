# Claim

How well does the seasonal average forecast the next three months? For each province and calendar month, the empirical distribution of the counts observed in that month across the training years — a baseline that knows the season and nothing else.

## Children

kind: alternatives
main-path: a_expandingWindow

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The seasonal climatology baseline scores **24.337 mean CRPS** over 371 cells, with 10-90
coverage 0.650 and 25-75 coverage 0.542. It is marginally the better of the two baselines
and the margin is inside what this evaluation can resolve.

Unlike the persistence baseline it needs no decision about how to wrap uncertainty around a
point — a set of past Julys is a distribution already. What it does need is a decision about
which window estimates that distribution, and the main path re-estimates from the expanding
historic frame at each split. The frozen-training-window sibling is not built yet;
`train.py` stores the table it would have used.

**The window does not matter.** Estimating the seasonal table once from the training frame
and holding it fixed scores **24.869** against the expanding window's **24.337**: 0.532 CRPS,
inside the 0.565 floor. The main path re-estimates from everything observed by forecast time
and gains nothing measurable by it, although the frozen table misses the last two years of a
twelve-year series.

Set beside its sibling fork — where the *construction* of the persistence baseline's
uncertainty is worth 4.181 CRPS — the pair says something the two rows do not say separately:
**on this dataset the shape of a baseline's predictive distribution matters and the window it
is estimated over does not.**
