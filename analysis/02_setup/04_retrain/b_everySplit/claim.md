# Claim

Refit every model at every split rather than once, by setting chap-core's n-retrain to the number of splits. A forecast made in 2009 is then made by a model that has seen 2008, which is more like how a forecasting system is actually operated and is what the reference model does inside its own predict.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

`n_retrain` is set to **8**, the scheme's own `n_splits`, read from the file `assemble_setup.py` reads it from rather than typed. Skill rises to **+0.1651**: refitting at every split helps our pool a little (18.817 to 18.552) and does not help the reference (22.098 to 22.220).

**That asymmetry is the point of the row.** The reference fits inside its own `predict`, so it was already refitting at every split whatever this flag said; `n_retrain` only governs how often chap-core calls `train`. The fork therefore buys the reference no different forecast and charges it **eight times the compute** — 64 jobs against 8 — which is how this row became the most expensive in tier 1 at 2 226 s and the one that exposed the reference's intermittent crash.
