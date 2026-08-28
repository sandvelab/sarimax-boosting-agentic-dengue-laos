# Batch reports

One report per executed batch of
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`. The plan is run one
batch per invocation of `/do`; each batch writes its report here and links it from the plan's
batch ledger.

Named `YY-MM-DD_bNN_camelCaseName.md`, where `NN` is the batch number. **A report is never
overwritten.** If a batch is redone, the new report is a new file and both stay.

Every batch ends in exactly one of three states, stated at the top of its report:

- **done — produced** — it created or changed something in the analysis, and the report says
  what and where;
- **done — expanded** — it produced no analysis output but replaced itself with more concrete
  batches, and the report says what made those possible;
- **blocked** — it could not proceed, and the report says exactly what is missing and what
  would unblock it.

These reports are the project's own running account of itself, so they are not regenerable
in the way the rest of `AI-generated/` is: they record what happened at a point in time, and
re-running a batch produces a different report rather than the same one.

## Currently here

- `26-08-23_b01_orientAndSetUp.md` — batch 1, phase A: orientation and repository set-up.
- `26-08-23_b02_chapSetup.md` — batch 2, phase A: installing and pinning `chap-core`, the
  model contract, and what `chap eval` actually computes.
- `26-08-23_b03_dataCharacterisation.md` — batch 3, phase A: pinning the Lao data, cutting
  off the held-out year, describing the development period, and fixing the backtest scheme.
- `26-08-23_b04_methodSurvey.md` — batch 4, phase A: running the reference model to get the
  score the project is measured against, and ranking the candidate model families against
  what the data will carry.
- `26-08-26_b05_bootstrapPlan.md` — batch 5, phase A: the claim-tree design, the fork
  inventory and the perturbation manifest, and the concrete batches for phases C, D and E.
- `26-08-26_b06_verticalSlice.md` — batch 6, phase B: the persistence baseline implemented
  against the Chap contract and run end to end on the development file, exercising every
  link in the chain once and giving the project its first CRPS from a model of its own.
- `26-08-26_b07_erectTheTree.md` — batch 7, phase B: the claim tree built from batch 5's
  design, the vertical slice routed through it and reproduced exactly, the seasonal
  climatology baseline and the reference model added as nodes, and the paired per-cell
  comparison that measures what the evaluation can and cannot resolve.
- `26-08-27_b08_candidateContract.md` — batch 8, phase C: the candidate subtree and its four
  configuration forks, the route model configuration takes into an `MLproject` model, the
  project seed's derivation into component seeds, and candidate 1 — a hierarchical
  negative-binomial GLM with the best point forecast in the project and the worst CRPS.

- `26-08-27_b09_candidateForks.md` — batch 9, phase C: every remaining child of candidate 1's
  forks built and run, two new forks for the structural choices batch 8 declined to make
  silently, three forks promoted by a rule committed before the combination it chose was run,
  and the finding that one-at-a-time fork effects do not add — three forks worth 4.632 CRPS
  separately delivered 2.402 together, and two of nine children reversed sign.
- `26-08-28_b10_boostedCandidate.md` — batch 10, phase C: candidate 2, gradient-boosted trees
  with a probabilistic head, and its two forks. The first model of ours to beat the reference
  on development — 20.771 against 22.098, ahead of each of its four repeats individually — and
  the first whose intervals are too wide rather than too narrow. Neither internal fork moved,
  and the family fork is left to batch 11 by batch 5's design. Its methodological centre is a
  prediction the head fork registered before it ran and a script that measured it afterwards:
  seven of eight named quantile levels flat at zero, the eighth flat in the one province that
  never reports one.
- `26-08-28_b11_ensembleCandidate.md` — batch 11, phase C and its close: candidate 3, a linear
  opinion pool over the two candidate families and both required baselines, holding no member
  code of its own — each member runs through its own Chap entry points. It scores **18.817**
  against the reference's 22.098, the family fork is promoted to it, and the project's
  reported conclusion turns positive for the first time at skill **+0.148**. Its two most
  useful results are both negative: a prediction registered before the run — that an equal
  pool would score worse than its best member — was **wrong** by 1.954 CRPS, and fitting the
  pool's weights on a year held back inside the training frame **cost 4.021 CRPS**, because
  the member that was best on that year is the worst on the years the backtest scores.
- `26-08-29_b12_perturbationManifest.md` — batch 12, phase D: the stability node, the
  perturbation manifest written and committed before any of it runs, the nine paths not
  taken created as nodes, and a new `combos` invariant that closes the combination space.
  Seventeen forks where batch 5 counted ten; 124 development minutes against a 12-hour
  budget, 89 of them re-running the reference model.
