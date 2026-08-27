# Claim

Fit once, in train, on the training period Chap supplies; predict applies the stored fit and reads the expanded history only for the covariate lags it needs.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Under the assembled flags — `n_retrain 1`, eight splits at stride 3 — one fit serves every
split, and by the last split there are **21 months** of observed history the fit never saw
(`results/main/model_option_spec.json`). The figure is read from the flag file rather than
assumed, so a combination that moved `n_retrain` would record that this child no longer means
what it says.
