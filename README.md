# Autonomously developed two-stage SARIMAX/residual-boosting dengue forecasting for Laos, veridically

A spatio-temporal model forecasting monthly dengue case counts across the provinces of
Laos, built as a two-stage ensemble — a SARIMAX-family model producing a baseline forecast,
and a second model, of a family chosen on the evidence, trained to correct its residuals —
developed as autonomously as the setup allows, together with the complete record of how it
came about.

A repository for carrying out **one research project** and producing **one article** from
it, with full provenance. Read `readme-at-start.md` for what this particular project is and
where it currently stands, `AGENTS.md` for how work is done here, and `MOTIVATION.md` for
why the repository is shaped this way.

This repository previously carried a different, now-completed and separately released
project (an EWARS-comparison case for the same dataset); that work lives on at
`github.com/sandvelab/veridical-agentic-dengue-laos` and has been removed from here so this
repository can hold one project at a time, per `AGENTS.md` §1 and §9.

## Structure

| Path | Holds |
|---|---|
| `analysis/` | The claim tree. `analysis/run.sh` reproduces the whole reported analysis. |
| `environment/` | The one main environment; nodes override only where they must. |
| `Human-AI-collaboration/claims/` | The claim collection — every statement bound to its result. |
| `Human-AI-collaboration/manuscript/` | The article, written from the claims. |
| `Archive/` | Imported source material, never edited, marked `(IS_SHADOW)`. |
| `AI-generated/` | Derived documents: batch reports, validation and release-scan findings, the hierarchical report, the reproducibility report. |
| `AI-internal/` | Scripts, skill references, the task log. |
| `Human-input/` | Plans that drive generation. |

## Where the project stands

**`readme-at-start.md` is the answer**, and it is the only place that answers it. For the
shape of the work rather than its state: the plan being executed is
`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md`, one batch per
invocation; each executed batch leaves a report in `AI-generated/batch-reports/`.

## Licence

Two licences, because this repository is both a record and a program.

- **`LICENSE` — CC BY 4.0** covers the documents, data, records and prose: the root-level
  documents, `AI-generated/`, `Human-AI-collaboration/`, `Human-input/`, `Archive/`, and
  under `analysis/` every `claim.md`, every `provenance/` record and every `results/` file.
- **`LICENSE-CODE` — MIT** covers the scripts: `analysis/**/scripts/`, every `run.sh`,
  `AI-internal/useful-scripts/`, `.claude/` and `environment/`.

Material under `Archive/` also carries the terms it came with, stated per directory in each
`provenance.md`; where an upstream licence applies, it governs and nothing here narrows it.

Use either half and cite the work; both permit commercial use.
