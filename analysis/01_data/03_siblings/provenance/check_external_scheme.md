# Provenance — where the two fixed schemes land on the sibling calendars

```
result:              results/backtest_scheme_external.json
                     results/split_schedule_external.csv
                     results/evaluable_cells_external.csv
script:              scripts/check_external_scheme.py
                     sha256:83da82634be1837e04401c4cf8aa8b51deed02d935b375e2cb66619c015f7059
invocation:          "$PYTHON" scripts/check_external_scheme.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     (the two schemes, which are read and not re-chosen)
                     results/THA_development_1998-01_2009-12.csv
                     results/THA_full_1998-01_2010-12.csv
                     results/VNM_development_1998-01_2009-12.csv
                     results/VNM_full_1998-01_2010-12.csv
                     (each named through analysis/scripts/lib/combos.py, so a dataset
                     cannot be checked under one file and run under another)
                     sha256s of all four in results/sibling_outputs.sha256
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0.
                     chap_core.assessment.dataset_splitting.train_test_generator and
                     chap_core.rest_api.db_worker_functions.
                     validate_and_filter_dataset_for_evaluation are called directly, as
                     02_characterise calls them for Laos
seeds:               none. The splitter is a deterministic index calculation.
commit:              bfbc096
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                analysis/01_data/03_siblings
produced:            2026-09-04
alternatives-considered: choosing a scheme per country from its own record length, which
                     would have used Thailand's thirty years better and made the three
                     countries incomparable. Rejected on batch 3's own argument: a horizon
                     changed midway makes every earlier number incomparable, and a horizon
                     changed per country makes the countries incomparable in the same way.
agency:              agent-autonomous
```

**What it establishes.** Applied to the sibling files, the two schemes batch 3 fixed evaluate
**2008-01 to 2009-12** and **exactly 2010** on both countries — the same months Laos is
scored on — from training sets ending 2007-12 and 2009-12, so training never reaches the
evaluated span. Read off what chap-core's own splitter returns, not recomputed from a
formula.

| dataset | scheme | provinces evaluated | cells |
|---|---|---|---|
| `tha` | 3/8/3 | 76 of 77 (TH-38 dropped: never reports) | 1 824 |
| `thaFinal` | 3/4/3 | 76 of 77 | 912 |
| `vnm` | 3/8/3 | 63 of 63 | 1 512 |
| `vnmFinal` | 3/4/3 | 63 of 63 | 756 |

Laos contributes 16 provinces over 371 and 192 cells, so the external check is measured on
between four and ten times as many cells as the analysis it is checking. That does not make
it a better measurement of the Lao result — it is a different country — but it does mean the
sibling figures are not the thinner of the two.

**Why this file exists rather than a constant.** The spans are properties of the files they
were read off. `analysis/scripts/lib/combos.py` points each dataset at the scheme file that
answers for it, which is why the constant six setup scripts each carried became
`combos.scheme_path()` in the same batch.

sha256 of `backtest_scheme_external.json` as produced: `17ecf4c4ad9257aa8680046190985fc18ab750fd0f7c41325eb64eee98510ea9`
