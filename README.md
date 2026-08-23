# Autonomously developed dengue forecasting for Laos, veridically

A spatio-temporal model forecasting monthly dengue case counts across the provinces of
Laos, developed as autonomously as the setup allows and evaluated by Chap's own
cross-validated backtest — together with the complete record of how it came about.

A repository for carrying out **one research project** and producing **one article** from
it, with full provenance. Read `readme-at-start.md` for what this particular project is,
and `MOTIVATION.md` for why the repository is shaped this way.

## Structure

| Path | Holds |
|---|---|
| `analysis/` | The claim tree. `analysis/run.sh` reproduces the whole reported analysis. |
| `environment/` | The one main environment; nodes override only where they must. |
| `Human-AI-collaboration/claims/` | The claim collection — every statement bound to its result. |
| `Human-AI-collaboration/manuscript/` | The article, written from the claims. |
| `Archive/` | Imported source material, never edited, marked `(IS_SHADOW)`. |
| `AI-generated/` | Derived documents: the hierarchical report, the reproducibility report. |
| `AI-internal/` | Scripts, skill references, the task log. |
| `Human-input/` | Plans that drive generation. |

## Reproducing this analysis

```bash
# build the environment
conda env create -f environment/environment.yml     # or: docker build environment/
# run everything
bash analysis/run.sh
# check the record is complete
python AI-internal/useful-scripts/check_invariants.py
```

The alternatives explored and not taken are in the tree alongside the main path, complete
and runnable. `AI-generated/hierarchical-report/index.html` is the way in.

## Currently here

Phase A, batch 1. The repository knows what it is and nothing has been analysed yet: the
source material is in `Archive/case-source-material/`, the plan being executed is
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`, and the batch
reports accumulate in `AI-generated/batch-reports/`. `analysis/` holds only the root node
scaffold. No data has been acquired and Chap is not yet installed.
