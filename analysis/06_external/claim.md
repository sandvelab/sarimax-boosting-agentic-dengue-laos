# Claim

Does the reported model, run unchanged on two other countries' data from the same
harmonisation, hold the margin it holds on Laos — and does the drop from the development
backtest to the final year replicate?

The plan's §4 named `tha` and `vnm` as an optional external check and the human confirmed
it on 2026-08-31, ahead of the release, so that the case write-up could use it. It is here
because phase E's largest open question cannot be answered from inside this project: the
holdout spread is measured on one year through four splits, and nothing in the Lao data can
say whether its width is about 2010, about one-year backtests, or about an agent optimising
freely against a development set. Two more countries, on the same months under the same two
schemes, are two more measurements of the same difference.

**Nothing here is developed, tuned or selected.** No fork moves in any of these rows: each
runs the reported analysis — every setup fork at its main child, both required baselines,
the reference model's four unseeded repeats, the linear opinion pool and the scoring chain
— with the file underneath replaced. The step lists come from the same driver the
perturbation set runs through, because a check that ran different code would measure the
code and not the model.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Decisions taken here

| Decision | Basis | Agency |
|---|---|---|
| **The four rows are planned and committed before they run, with a budget and a cut order** | `AGENTS.md` §6. The Thai file carries 77 provinces against Laos's 18 and the reference runs four repeats through an emulated amd64 image, so this is the one part of the batch that could plausibly exceed its budget. The estimate is built from this project's own measured seconds per evaluated cell | agent-autonomous |
| **The budget is six hours, and rows are cut in whole country pairs** | Six hours is what `analysis/run.sh` already costs: an external check on the analysis should not cost more than the analysis. A country is the unit because what is measured is the *drop* between its two arrangements, and half a country measures nothing | agent-autonomous |
| **No external row is sealed or skipped on a second invocation** | Plan §3's seal protects the Lao 2010 because the model was developed against Lao 1998–2009. Nothing was developed on these files, so there is nothing to protect. Skipping a row that had already run is what stopped `analysis/run.sh` reproducing phase E from a clean checkout in batch 18, and the same shape is not reintroduced here | agent-autonomous |
| **The pool's independent reconstruction is not available on these datasets, and that is written down** | `check_pool.py` needs each member's own separate evaluation, which exists only under the family fork's own combination — a perturbation row. This check moves no fork, so no order of execution would produce one. It is recorded in `results/pool_reconstruction_external.json` rather than left blank | agent-autonomous |

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

_(Filled by `report_external.py` having run; see `results/external_vs_laos.json`.)_
