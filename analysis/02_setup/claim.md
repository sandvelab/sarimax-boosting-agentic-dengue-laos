# Claim

What dataset and evaluation setting do all models — ours, the baselines and the reference — face in common? Everything decided here moves every model together, so a choice taken differently re-scores the whole comparison rather than one side of it.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

Every model in the project — the two baselines and the external reference — is evaluated on
**one dataset of 2 592 rows over 18 provinces, 1998-01 to 2009-12**, at
`n_periods 3, n_splits 8, stride 3, n_retrain 1`. The dataset is
`results/main/analysis_dataset.csv` and the flags are in `results/main/setup_spec.json`,
which also records where each flag came from: the first three from batch 3's stored scheme
file, the fourth from the fork that decides it.

On the main path all four choices are the identity on the data, and that is checked rather
than claimed: `identical_to_development_file` is **true**, so the file every model faces is
the archived development file byte for byte. It will not be true off the main path, and then
the field says so.

The four choices are `a_static` (population as the archive supplies it), `a_from1998` (the
whole development period), `a_chapFilter` (province inclusion left to the platform) and
`a_once` (one fit per backtest). Each is a fork whose siblings are built when the stability
manifest needs them; each of those siblings re-scores **every** model, which is a property
of where the node sits rather than a rule anyone has to remember.
