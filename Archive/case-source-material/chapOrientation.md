# Chap orientation — platform, data and evaluation

(IS_SHADOW)

A starting map of the Chap platform, the Lao dataset and the evaluation workflow this project
is measured by. It exists so that reconnaissance starts from verified ground rather than from
a search engine, and it is deliberately **incomplete**: everything below was checked on
22 August 2026 and nothing here substitutes for the documentation itself. Where this file and
the live documentation disagree, the documentation wins — and the discrepancy is worth
recording, because a stale orientation note is exactly the failure mode this project is
about.

---

## 1. What Chap is

Chap is an open-source platform for climate-informed disease forecasting, developed at the
HISP Centre (University of Oslo) with Wellcome Trust funding. It connects climate data to
disease forecasting and, through DHIS2, to routine operational use in national health
systems.

Chap does **not** implement forecasting models itself. It is an **orchestrator**: it manages
data, coordinates model execution, evaluates models against held-out history, and presents
results. The forecasting logic lives in **external model plugins**, developed separately and
potentially by different research groups, which communicate with Chap through a fixed
contract. That contract is what makes this project possible at all — a new model is a plugin
honouring the contract, not a fork of the platform.

### Terminology that matters here

| Term | Meaning |
|---|---|
| **Chap** / *Chap Modeling Platform* | The platform as a whole, conceptually. Written *Chap*, not *CHAP* — the all-caps form is outdated. |
| **`chap-core`** | The Python codebase implementing the backend: model execution, backtesting, evaluation, data ingestion, REST API. Narrower than "Chap". |
| **Model template** | A model specification with selectable options (covariates, hyperparameters). A recipe with choosable ingredients; not trainable as it stands. |
| **Configured model** | A model template with the choices made. Trainable. Always untrained until `train` is called. |
| **Covariate** | An input variable, typically climate — rainfall, temperature — named conceptually. |
| **Backtest** / **evaluation** | Evaluating on historical data by repeatedly standing at a past point, predicting forward, and comparing to what happened. Used interchangeably in `chap-core`. |
| **Pretended prediction time** | The historical point the model pretends is "now". Nothing after it may be seen. Strict data isolation is the design principle. |
| **Probabilistic forecast** | A distribution over outcomes, delivered as samples, not a point estimate. Chap *requires* this. |
| **Calibration** | Whether stated uncertainty matches reality — a 90% interval should cover the truth 90% of the time. Measured explicitly by Chap's evaluation framework. |

The requirement that forecasts be probabilistic is not a detail. It is why the headline
metric is CRPS rather than an error on a point prediction, and it constrains every model
family considered.

## 2. Where things are

| Resource | Location |
|---|---|
| Documentation | `https://chap.dhis2.org/` |
| Backend source | `https://github.com/dhis2-chap/chap-core` |
| Organisation (Climate App, tools, apps) | `https://github.com/dhis2-chap` |
| Library of integrated models | `https://github.com/chap-models` |
| `chapkit` — library for model services | `https://github.com/dhis2-chap/chapkit` |
| Minimal worked model example (R) | `https://github.com/dhis2-chap/minimalist_example_r` |
| Harmonised country datasets | `https://github.com/dhis2/climate-health-data` |

Documentation sections seen at the top level: *Chap Modeling Platform* (implementation and
development), *Climate Data*, *Community*, *Research*, *About*. Three pages matter most for
this project, under `chap-modeling-platform/chap-cli/`:

- `chap-core-cli-setup/` — installing `chap-core` locally
- `evaluation-workflow/` — running a backtest and comparing models
- `eval-reference/` — the `eval` command's full argument list

There is also a section *Make your model Chap compatible*, with subsections on data
preparation, the train/predict functions, and model configuration. That section is the
specification a new model must satisfy.

The **model library** at `github.com/chap-models` is the single most useful starting point
for modelling inspiration: it holds models already integrated through collaborations with
groups in the field, among them the WHO EWARS-csd early-warning model for dengue
(doi:10.3389/fpubh.2024.1323618). These are working, Chap-compatible implementations of
published methods, and reading them answers both "what does the contract look like in
practice" and "what has the field already tried on this kind of data".

## 3. The evaluation workflow

Evaluation is three steps: run the backtest, plot it, export the metrics. Verified against
the documentation on 22 August 2026:

```bash
chap eval \
    --model-name https://github.com/dhis2-chap/minimalist_example_r \
    --dataset-csv ./data/vietnam_data.csv \
    --output-file ./results/model_a_eval.nc \
    --backtest-params.n-periods 3 \
    --backtest-params.n-splits 7

chap plot-backtest \
    --input-file ./results/model_a_eval.nc \
    --output-file ./results/model_a_plot.html \
    --plot-type evaluation_plot

chap export-metrics \
    --input-files example_data/example_evaluation.nc \
    --input-files example_data/example_evaluation_2.nc \
    --output-file ./comparison.csv
```

Three parameters control the cross-validation:

- `--backtest-params.n-periods` — the forecast horizon, in time periods
- `--backtest-params.n-splits` — how many train/test splits
- `--backtest-params.stride` — the step between successive splits

Metrics available include **CRPS** (continuous ranked probability score), RMSE, MAE, and
coverage ratios for the uncertainty intervals. Backtest results are written as NetCDF
(`.nc`); `export-metrics` converts them to CSV with one row per evaluation, carrying the
filename, model metadata and the metric values.

Two consequences for this project. First, the metric this project optimises is produced by
the platform, not by the analysis — which is the property that makes it hard to
accidentally game. Second, `.nc` and the exported `.csv` are the natural stored intermediate
at every model evaluation, and they are small.

## 4. The Lao dataset

`https://github.com/dhis2/climate-health-data/tree/main/lao`, three files:

- `chap_LAO_admin1_monthly.csv` — the data
- `chap_LAO_admin1_monthly.geojson` — admin-1 boundaries
- `chap_LAO_admin1_monthly_schema.json` — field-level schema with sources

From the schema (`CHAP Harmonized Dataset (LAO)`): country Laos, admin level 1, monthly
resolution, time range **1998-01 to 2010-12**, primary key `(location, time_period)`,
generated 2026-02-11.

| Field | Unit | Meaning | Source |
|---|---|---|---|
| `time_period` | — | `YYYY-MM` | derived during temporal aggregation |
| `location` | — | stable admin-unit identifier (`shapeISO`) | OCHA COD-AB / HDX |
| `location_name` | — | admin-unit name (`shapeName`) | OCHA COD-AB / HDX |
| `rainfall` | mm | total precipitation over the bucket, within the polygon | ERA5-Land (CDS) |
| `mean_temperature` | °C | mean 2 m temperature over the bucket | ERA5-Land (CDS) |
| `mean_relative_humidity` | % | derived from 2 m temperature and dewpoint via August–Roche–Magnus (a = 6.112 hPa, b = 17.67, c = 243.5 °C), applied to monthly means then aggregated | ERA5-Land (derived) |
| `disease_cases` | cases | **reported dengue cases**, aggregated to bucket and admin unit | OpenDengue |
| `population` | persons | static snapshot, applied to every period | WorldPop |

The target is therefore dengue, and the covariates on offer are rainfall, temperature,
humidity and population.

**Two things in this dataset are already analytic problems, and both belong in the tree
rather than in a footnote.**

*The schema's row count does not match the file.* `row_count` is stated as 2575; the CSV
carries 2808 data rows. One of the two is stale, or rows were added after the schema was
written. Establish which, from the data, and record the answer — it is the first thing in
this project that a reader would want to know was checked.

*`population` is a static snapshot applied to all thirteen years.* Any per-capita rate
computed from it inherits that, and over 1998–2010 the error is not small. Whether to model
counts with population as an offset, or rates, or to ignore population entirely, is a genuine
judgment call with reasonable alternatives — which makes it a candidate alternatives node,
not a preprocessing detail.

Two sibling datasets exist in the same repository, **`tha`** (Thailand) and **`vnm`**
(Vietnam), presumably in the same harmonised format. They are not part of the headline
analysis. They are the obvious external check on whether anything learned on Laos
generalises, and the plan treats them that way.

## 5. What was *not* verified here

- Whether `chap eval` accepts a local model directory as `--model-name` or only a URL.
- The exact form of the CRPS the platform reports — over what, averaged how, and whether the
  per-region and per-split values are recoverable from the `.nc` or only the aggregate from
  `export-metrics`. **This matters more than anything else in this file**, because the
  project's success criterion is an average across regions and splits, and an average is not
  a result until you know what it averages.
- Installation specifics: Python version, whether Docker is required, what the model runner
  needs.
- Whether the model contract requires R, Python, or is language-agnostic via the plugin
  mechanism.
- Whether any model in `github.com/chap-models` has already been run on the Lao dataset, and
  with what score. If one has, that is the baseline this project should be compared against,
  and finding out is cheap.

---

*Compiled 22 August 2026 from the Chap documentation, the dataset's own schema, and the
Chap team's terminology and architecture notes. Every URL and command above was checked
against its source on that date.*
