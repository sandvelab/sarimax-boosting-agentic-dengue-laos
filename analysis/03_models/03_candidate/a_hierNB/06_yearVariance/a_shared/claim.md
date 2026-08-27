# Claim

One province-year variance for the whole country, estimated by pooling every province's annual effects. Every province's forecast is then equally wide in relative terms.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**23.749** mean CRPS, **0.051** from the promoted main path -- so from where the model
     now stands, one shared annual variance and seventeen separate ones are indistinguishable.
     Around the batch-8 configuration the same fork was worth 1.870. It is also the only
     combination in the second sweep whose fit **converged**, in 48 rounds against the
     200-round cap every province-scaled fit reaches.
