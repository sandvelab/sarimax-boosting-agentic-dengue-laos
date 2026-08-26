# Claim

What does the field's own model score on this dataset? WHO EWARS-csd as published at chapkit_ewars_model, at its own default configuration, pinned by image digest and never tuned by us. It is unseeded, so it is run repeatedly and its spread carried rather than hidden.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The reference model scores **22.098 mean CRPS** over the same 371 cells, taken as the
per-cell mean of four repeats. The four individual repeats score 21.820, 21.917, 22.272 and
22.385 — a range of 0.57, or 2.6 % of the mean, from a model that is unseeded and cannot be
seeded. Batch 4 measured the same spread at sd 0.196 on a different set of four runs, so
this is a stable property of the model rather than an unlucky day.

It is well calibrated in the tails (10-90 coverage 0.804 against a nominal 0.80) and
materially too wide in the middle (25-75 coverage 0.602 against 0.50) — the mirror image of
our baselines, which are almost exact in the middle and far too thin in the tails.

**The asymmetry Rule 6 runs into is now demonstrated at both ends**: the models this project
builds are bit-reproducible, and the model it is measured against moves by half a CRPS
between identical runs. That is not a defect to be worked around but the quantity that sets
what the comparison can resolve.
