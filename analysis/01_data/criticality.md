# Criticality — what `01_data` stores, and what it would cost to lose

Written by `/annotate-criticality`. Four rough judgments per artifact, so that pruning later
is targeted rather than a panic. **This file proposes nothing and deletes nothing.**

Everything here is regenerable by `bash analysis/01_data/run.sh` from `Archive/lao-dataset/`
in **about fifteen seconds** on the machine this was built on. That figure is what makes most
of the table below unremarkable: the storage question barely binds at this node. It is
recorded anyway, because the point of annotating early is that the judgment is cheap now and
impossible later.

Total: **1.6 MB**, of which 0.5 MB is five PNGs and 0.3 MB is the two CSV parts.

## `01_partition/results/`

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `development_1998-01_2009-12.csv` | 224 KB | main result | yes, ~2 s | **highest** | The input to everything else in the project. A reader who checks one file checks this one. |
| `holdout_2010_SEALED.csv` | 19 KB | main result | yes, ~2 s | **highest** | The sealed year. Regenerable, but its *existence in the record from batch 3 onward* is what makes the seal auditable — a holdout produced in phase E could have been produced any way at all. **Never prune.** |
| `partition_check.json` | 1.2 KB | main result | yes, ~2 s | high | The evidence that the split is exact. Cheap and load-bearing. |
| `part_structure.csv` | 859 B | side result | yes, ~2 s | high | Structural description of all three parts, including the holdout's permitted completeness figures. |
| `rowcount_reconciliation.json` | 805 B | side result | yes, ~2 s | high | Answers a question [[chapOrientation]] raised by name. |
| `chap_ingest_check.json` | 1.9 KB | side result | yes, ~3 s | medium | Evidence that no silent coercion happens on load. |
| `partition_outputs.sha256` | 455 B | intermediate | yes, ~2 s | medium | Lets a clean-room run compare against archived outputs without re-deriving them. |

## `02_characterise/results/` — tables

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| `backtest_scheme_chosen.json` | 820 B | **main result** | yes, ~4 s | **highest** | The scheme every later number is computed under. It does not move again, so this file is the record of when it was fixed and to what. |
| `evaluable_cells_by_province.csv` | 665 B | **main result** | yes, ~4 s | **highest** | What the headline metric is a mean over — 16 provinces, 371 cells. The most consequential table in the batch. |
| `backtest_scheme_candidates.csv` | 676 B | main result | yes, ~4 s | high | The six schemes not taken, with their costs. This is the alternatives record for a decision that has no node. |
| `split_schedule.csv` | 985 B | main result | yes, ~4 s | high | The actual split windows, read from chap-core's own generator, including the phase-E arrangement. |
| `dev_overview.json` | 540 B | main result | yes, ~2 s | high | The headline counts. |
| `covariate_units_check.json` | 2.0 KB | side result | yes, ~2 s | high | The rainfall-unit finding. Small, and the only place it is written down with its evidence. |
| `cases_by_province.csv` | 1.6 KB | main result | yes, ~2 s | high | The burden distribution behind the metric-weighting warning. |
| `lag_correlation.csv` | 1.2 KB | main result | yes, ~3 s | high | Decides whether lagged covariates are worth a fork. |
| `completeness_by_province_year.csv` | 7.4 KB | side result | yes, ~2 s | high | Behind the region-filter finding. |
| `target_missing_cells.csv` | 6.6 KB | side result | yes, ~2 s | medium | Every absent province-month individually. |
| `zero_structure.csv` | 7.7 KB | side result | yes, ~2 s | high | The non-stationary zero rate, which is a stated expectation about phase E. |
| `cases_by_year.csv` | 486 B | side result | yes, ~2 s | medium | |
| `cases_national_monthly.csv` | 4.6 KB | side result | yes, ~2 s | medium | |
| `seasonality_by_month.csv` | 13 KB | side result | yes, ~2 s | medium | National and per-province profiles. |
| `covariate_summary.csv` | 5.5 KB | side result | yes, ~2 s | medium | |
| `population_static_check.csv` | 875 B | side result | yes, ~2 s | high | Confirms the schema's own note, and grounds a phase-D fork. |

## `02_characterise/results/` — figures and their data (Rule 7)

| Artifact | Size | Role | Regenerable | Transparency | Note |
|---|---|---|---|---|---|
| 5 × `fig_*.png` | 494 KB | side result | yes, ~6 s total | medium | The largest single block here. Regenerable from the tables in seconds, so the honest annotation is that these are the **first things to prune** if storage ever binds — the plotted values below are what a critical reader actually needs. |
| 5 × `fig_*.csv` (plotted values) | 9 KB | main result | yes, ~6 s | **highest** | The numbers behind each figure. Never prune: recovering values from a rendered image is approximate, fails silently on overlapping elements, and cannot recover what the figure aggregated away. |
| `fig_cases_timeline_preaggregation.csv` | 73 KB | intermediate | yes, ~2 s | medium | The province-month observations behind the national line. |
| `fig_province_burden_preaggregation.csv` | 73 KB | intermediate | yes, ~2 s | low | **Byte-identical in content to the file above** — both are the four relevant columns of the development file. Kept because Rule 7 asks each figure to carry its own pre-aggregation values, and a reader following one figure should not have to know which other figure happens to share them. If storage ever binds, this is the cheapest 73 KB in the repository to give up. |
| `fig_cases_seasonality_preaggregation.csv` | 143 KB | intermediate | yes, ~2 s | medium | Adds the two climate columns, so it is not a duplicate of the two above. |
| `fig_completeness_preaggregation.csv` | 6.6 KB | intermediate | yes, ~2 s | medium | A copy of `target_missing_cells.csv` under the figure's stem. |

## The one thing here that is not regenerable

Nothing at this node is irrecoverable while `Archive/lao-dataset/` survives, and that folder
is committed, checksummed, and pinned to an upstream commit. **The real single point of
failure is upstream**: if `dhis2/climate-health-data` were rewritten or removed, the archive
copy is the only remaining source, and it is 8.7 MB of which 8.4 MB is the GeoJSON. That is
the file to protect, and it is why the data is committed to the repository rather than
fetched on demand.

## Proposed pruning

**None.** At 1.6 MB against a fifteen-second regeneration, nothing here is worth deleting,
and `AGENTS.md` §6 is explicit that the decision is deferred rather than made up front. The
ordering above is what a later prune would follow if the volume ever changed: PNGs first,
then the duplicate pre-aggregation file, then the remaining intermediates — never the plotted
values, never the scheme, and never the sealed holdout.
