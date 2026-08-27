# Claim

Which climate covariates enter the mean, and at which lags? The file carries rainfall, mean temperature and mean relative humidity, and a transmission signal reaches reported cases only after a delay, so the covariate set and the lag are one joint choice.

## Children

kind: alternatives
main-path: c_climateFree

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**This fork cannot be settled on this dataset, and that is the answer.** Around the batch-8
configuration, dropping the climate covariates entirely *improved* the candidate by
**0.648** CRPS and adding all three at three lags improved it by 0.461 -- both better than
the reference family's own published Lao pair at lag 2. Measured again from the promoted
main path the ordering changes: the rich set is worth **+0.821**, and putting the two
lagged covariates back is worth **+0.112**, so the climate-free choice the promotion took
is now marginally the worse one (`round2_promoted/fork_interaction.csv`).

Two of those four numbers are inside the 0.57 CRPS resolvable floor and the ordering
reverses between sweeps, so no child of this fork is established as better than another.

**What is established** is why. In `b_rich` the fitted seasonal harmonic `sin1` collapses
from −1.235 to **−0.027** as nine climate columns enter, while mean temperature at lag 1
takes **+0.653**: the climate columns and the calendar are substituting for each other
rather than adding. On this dataset the annual cycle can be carried by either, and the
model scores about the same whichever carries it.
