# Autonomously developed dengue forecasting for Laos, veridically

A spatio-temporal model forecasting monthly dengue case counts across the provinces of
Laos, developed as autonomously as the setup allows and evaluated by Chap's own
cross-validated backtest — together with the complete record of how it came about.

A repository for carrying out **one research project** and producing **one article** from
it, with full provenance. Read `readme-at-start.md` for what this particular project is and
where it currently stands, `AGENTS.md` for how work is done here, and `MOTIVATION.md` for
why the repository is shaped this way.

## Structure

| Path | Holds |
|---|---|
| `analysis/` | The claim tree. `analysis/run.sh` reproduces the whole reported analysis. |
| `environment/` | The one main environment; nodes override only where they must. |
| `Human-AI-collaboration/claims/` | The claim collection — every statement bound to its result. |
| `Human-AI-collaboration/manuscript/` | The article, written from the claims. |
| `Archive/` | Imported source material, never edited, marked `(IS_SHADOW)`. |
| `AI-generated/` | Derived documents: batch reports, validation, the hierarchical report. |
| `AI-internal/` | Scripts, skill references, the task log. |
| `Human-input/` | Plans that drive generation. |

## Reproducing this analysis

Two environments, and they are not interchangeable. `environment/chapenv/` runs the
analysis; `.venv/` runs the repository's own machinery. Neither is tracked, and both are
built from a specification that is.

```bash
# 1. the analysis environment — CPython 3.13.0 and chap-core 2.1.0, installed from
#    environment/lock.txt (174 packages, exact versions). Needs `uv` on PATH.
bash environment/install-chap.sh

# 2. run everything
bash analysis/run.sh

# 3. check the record is complete
python3 -m venv .venv          # the machinery interpreter, stdlib only
.venv/bin/python AI-internal/useful-scripts/check_invariants.py
```

`environment/environment.yml` is the **declarative** half — what was asked for — and is not
a conda file; `environment/lock.txt` is what actually reproduces, and `install-chap.sh`
installs from it and reports any difference between what it built and what that file says.
`environment/Dockerfile` freezes the same package set into an image.

**`analysis/run.sh` is about six hours from cold**, because it reproduces the reported
result, the distribution of 32 analyses around it on the development period, and the same
set again on the held-out year. Most of that time is the reference model — an external
container, unseeded, re-run four times per dataset through an emulated amd64 image. **Docker
must be running**, and without it everything except the reference model and the comparisons
that divide by it will still run.

The alternatives explored and not taken are in the tree alongside the main path, complete
and runnable. `AI-generated/hierarchical-report/index.html` is the way in once it has been
built — it is generated and gitignored, and `/hierarchical-report` rebuilds it in about two
seconds.

## Where the project stands

**`readme-at-start.md` is the answer**, and it is the only place that answers it. This file
deliberately does not repeat the project's state: an overview that restates what is recorded
elsewhere goes stale silently, and this section did — it described the repository as it
stood at batch 1, with nothing analysed and Chap not yet installed, for the whole of phases
B, C and D. Batch 18's `/validate outsider` run found it by trying to follow it.

For the shape of the work rather than its state: the plan being executed is
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`, one batch per
invocation; each executed batch leaves a report in `AI-generated/batch-reports/`; and
`AI-generated/validation/` holds the checks on the method itself.

## Licence

Two licences, because this repository is both a record and a program.

- **`LICENSE` — CC BY 4.0** covers the documents, data, records and prose: the root-level
  documents, `AI-generated/`, `Human-AI-collaboration/`, `Human-input/`, `Archive/`, and
  under `analysis/` every `claim.md`, every `provenance/` record and every `results/` file.
- **`LICENSE-CODE` — MIT** covers the scripts: `analysis/**/scripts/`, every `run.sh`,
  `AI-internal/useful-scripts/`, `.claude/` and `environment/`.

Material under `Archive/` also carries the terms it came with, stated per directory in each
`provenance.md`; where an upstream licence applies, it governs and nothing here narrows it.
Third-party code built into the Chap model contract directories carries its own licence.

Use either half and cite the work; both permit commercial use.
