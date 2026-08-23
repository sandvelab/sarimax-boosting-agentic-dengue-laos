# Batch 3 — reconnaissance: the data

Generated from [[26-08-22_dengueForecastingCase]] — iteration 3

**Phase A · Status: done — produced · Executed 2026-08-23**

---

The batch that separates the held-out year from everything else, and then describes what is
left. It is also the first batch to put anything in the claim tree: `analysis/01_data`, with
a partition child and a characterisation child, reproduced end to end by `bash
analysis/run.sh` in about fifteen seconds.

Every figure quoted below comes from a file under `analysis/01_data/*/results/`, each with a
provenance record beside it. Nothing here was read off a terminal.

## 1. The data, pinned

The three Lao files are in `Archive/lao-dataset/`, fetched at commit
`af362d5260c6e7de1739f3d05314a844bd272613` of `dhis2/climate-health-data` — the head of
`main` on 2026-08-23, whose subject is a rename of the boundary files for Chap compatibility.
`AI-internal/data-acquisition/fetch_lao_dataset.sh` fetched them and wrote
`sha256sums.txt`; the archive is write-once, so re-running the script verifies rather than
refetches, and the partition node re-checks the manifest on every run.

The `(IS_SHADOW)` marker of `AGENTS.md` §8 could not be applied. It inserts a line into the
document, and inserting a line into a CSV would edit imported data and break the checksums
that make the import verifiable. The folder's `README.md` and `provenance.md` carry the
statement instead. This is a small gap in the convention rather than an exception taken
quietly: the rule is written for text documents and the repository now holds data.

## 2. The partition, and why the obvious check is the wrong one

`analysis/01_data/01_partition` is the only thing in this project that reads the full file.
It writes the **development dataset** (1998-01 to 2009-12, 2 592 rows) and
`holdout_2010_SEALED.csv` (2010, 216 rows), and verifies that the two partition the source
exactly.

The obvious verification — concatenate the parts, hash, compare to the source — **fails on
this file, and not because anything is wrong**. The CSV is ordered by province and then by
month, so a cut on time is not a prefix and a suffix; the parts interleave. What is checked
instead, on the files as written to disk rather than on the lists held in memory:

| Property | Result |
|---|---|
| Row counts sum to the source | 2 592 + 216 = 2 808 ✓ |
| No line in both parts | ✓ |
| Sorted union byte-identical to the sorted source | `548d9231…` on both sides ✓ |
| Each part an order-preserving subsequence of the source | ✓ |
| Header preserved in both | ✓ |
| Observed period ranges match the declared spans | 1998-01…2009-12 and 2010-01…2010-12 ✓ |

The source is a **complete rectangular panel**: 18 provinces × 156 months, no missing months,
no duplicate primary keys, every column fully populated except `disease_cases`.

**The holdout was checked for structure and then left alone.** 216 rows, all 18 provinces,
all 12 months, 24 cells without a dengue count. Its case values were not read, plotted or
characterised. Where those 24 absent cells fall was *not* examined either, though phase E
will need it to know what the final validation can measure — that is 24 of 216 province-months
the holdout cannot score, and it is flagged here so phase E is not surprised by it.

## 3. The row-count discrepancy, resolved

[[chapOrientation]] §4 flagged it: the schema states 2 575 rows, the CSV carries 2 808. Both
numbers are right about different things.

```
rows in file                        2808   = 18 provinces x 156 months
rows with disease_cases not null    2575
rows with no null in any column     2575
```

`disease_cases` is the only column with missing values, so the two candidates coincide.
**The schema's `row_count` counts complete records, not rows.** It is a label error, not a
stale figure — nothing was added to the file after the schema was written. 233 rows carry a
missing target: 209 in development, 24 in the holdout.

The schema is wrong in two further ways, both recorded in `Archive/lao-dataset/provenance.md`
so a reader who starts there is not misled. It names `LAO_ADM1.geojson` as its boundary file,
which the pinned commit had just renamed. And it declares `rainfall` as a total in
millimetres accumulated over the month, which the numbers do not support: read as declared, a
province's whole year comes to 50–78 mm; read as a **mean daily rate in mm/day** it comes to
1 518–2 383 mm, and the monthly profile peaks with the southwest monsoon. Nothing downstream
depends on which is true — the models see a monotone transform of the same column — but
anything importing an external rainfall threshold does, and would be wrong by a factor of
about thirty.

## 4. No conversion is needed

The plan asked for the data in whatever form `chap eval` expects, and for evidence that the
conversion is lossless. **There is no conversion.** `chap eval` reads a CSV with
`time_period`, `location`, `disease_cases` and covariate columns, which is what the archived
file already is.

What had to be shown instead is that chap-core's own reader takes it without altering
anything, and `chap_ingest_check.json` shows it does: both parts load through
`DataSet.from_csv` with every row, every province and every one of the missing target values
preserved. The loader adds a `parent` column and drops nothing — not even `location_name`,
which it carries through as a non-numeric field.

This check is worth more than it looks. A format conversion is where a silent coercion would
live, and a missing target quietly becoming a zero would change every count in this project
without raising an error anywhere.

## 5. The development period

2 592 rows, 18 provinces, 144 months, 77 031 reported cases.

**8.1% of target cells are missing and 56.3% of the observed ones are zero.**

### Seasonality is strong and stable

Cases peak in July–September at roughly fourteen times the February trough, on an annual
cycle that holds across the whole period. Rainfall peaks with the case peak; humidity rises
earlier and stays high through the season.
(`fig_cases_seasonality.png`, `seasonality_by_month.csv`)

Two large epidemics stand out — 2003 at 17 645 cases nationally and 1998 at 7 438 — against
years as low as 1 377 in 2000. (`fig_cases_timeline.png`, `cases_by_year.csv`)

### Climate leads dengue, consistently in sign and loosely in size

Spearman correlations computed within province and then pooled, so that a province being both
wetter and more affected than another does not enter as a climate signal:

| Covariate | Strongest lag | Mean ρ over provinces | Provinces positive |
|---|---|---|---|
| rainfall | 1 month | 0.32 | 17 / 17 |
| mean_temperature | 2–3 months | 0.32 | 16–17 / 17 |
| mean_relative_humidity | 0–1 months | 0.31 | 17 / 17 |

The min–max band across provinces runs roughly 0.0 to 0.7 — the association is consistent in
sign, not in size. The negative values at lags five and six are the far side of the annual
cycle, not a mechanism. (`fig_covariate_lag_correlation.png`, `lag_correlation.csv`)

### The burden is extremely uneven

Four orders of magnitude between Vientiane Capital (28 768 cases) and Phongsaly (4, all in a
single month of 2004). Six provinces report zero in more than 85% of their observed months.
(`fig_province_burden.png`, `cases_by_province.csv`)

### The zero rate is not stationary

| 1998 | 2000 | 2003 | 2006 | 2009 |
|---|---|---|---|---|
| 63.7% | 72.1% | 53.4% | 46.9% | **33.5%** |

Zeros fall steadily as the record goes on. The evaluated window under the fixed scheme,
2008–2009, is the *least* zero-heavy part of the whole development period, which makes the
development backtest an easier problem than an average year of the training data would be.
This is a reason to expect some development-to-holdout drop before any model exists.
(`zero_structure.csv`)

## 6. The backtest scheme, fixed here and not moved again

Verified against chap-core's own `train_test_generator` and
`validate_and_filter_dataset_for_evaluation`, called directly; the schedule is read off what
they return rather than recomputed from the formula in their docstrings.

| | `n_periods` | `n_splits` | `stride` | `n_retrain` | Evaluates | Trained through |
|---|---|---|---|---|---|---|
| **Development** | 3 | 8 | 3 | 1 | 2008-01 … 2009-12 | 2007-12 |
| **Phase E** | 3 | 4 | 3 | 1 | 2010-01 … 2010-12 | 2009-12 |

**`n_periods = 3` was not a free choice.** Batch 2 found chap-core forcing `n_periods=3` for
the EWARS model and the chapkit EWARS service declaring `prediction_periods: 3`. A horizon the
reference model cannot run at would mean the plan's central comparison never happens.

**`stride = 3`, not 1.** With `stride < n_periods` successive splits overlap in the months they
predict, so the splits are strongly correlated, the design is unbalanced, and batch 2's
identity between the platform's mean over cells and a mean over regions × splits stops
holding. `stride = 3` also makes the phase-E arrangement come out even.

**`n_splits = 8`.** Seven candidate schemes were run and are stored in
`backtest_scheme_candidates.csv`. At `stride 3`: four splits evaluate only 2009, which makes
the development estimate a statement about one dengue season; twelve splits evaluate three
years but, with `n_retrain 1`, leave the single fit made on data ending 2006-12 while
predicting through 2009. Eight is the middle — ten years of training before the first split,
two complete seasonal cycles evaluated.

**Phase E puts the evaluated span exactly on 2010**, confirmed on a synthetic 1998–2010
calendar rather than on the archived original: a split schedule depends only on the period
range, so answering the question did not require opening the holdout. The first split trains
on everything through 2009-12 and predicts 2010-01…03; each later split rolls a quarter
forward. With `n_retrain 1` **no 2010 observation ever enters training** — later splits see
2010 only as expanding context at predict time, which is what a rolling-origin forecast is.

**Development and holdout differ in `n_splits`** (8 against 4) because the evaluated windows
differ in length by design, two years against one. `n_periods` and `stride` are identical and
the per-cell CRPS is identical, so the two are comparable through the skill score the plan's
§4b fixes at the root — a ratio computed within each dataset. Raw CRPS levels are not
comparable between them, and this project does not treat them as though they were.

## 7. What the headline metric is actually a mean over

**This is the most consequential thing batch 3 found, and it is a property of the plan's
chosen metric rather than of any model.**

`validate_and_filter_dataset_for_evaluation` drops a location whose target is entirely
missing over the **training** portion. On the development dataset it drops exactly one:

- **Vientiane province (LA-VI)** reports no dengue count in any of the 144 months. It is
  dropped, leaving 17 provinces and a nominal 17 × 8 × 3 = 408 cells.

But missing observations are also dropped before the metric is computed, and that removes
more:

- **Xaisomboun (LA-XN)** reports through 2005-12 and then stops. Its *training* period has
  data, so it survives the filter — and it contributes **zero** evaluable cells, because the
  evaluated span is 2008–2009.
- **Phongsaly (LA-PH)** contributes 11 of its 24 months.

**The headline mean is over 16 provinces and 371 cells, not 18 provinces and 408.**
(`evaluable_cells_by_province.csv`, `backtest_scheme_chosen.json`)

And of those 16, six report zero in more than 85% of their observed months. CRPS is averaged
unweighted over cells, so a province where predicting zero is almost always right carries the
same weight as the capital. A model can move the headline number by getting the easy
provinces slightly more confidently right. Saying so now, before any model exists, is the
only time it can be said without it looking like an excuse.

## 8. Data problems found — the phase-D fork candidates

The plan asked for this list to be built here. Each is a judgment call with reasonable
alternatives, so each is a candidate alternatives node rather than a preprocessing decision.

| # | Problem | Why it is a fork |
|---|---|---|
| 1 | **Vientiane province never reports.** 144 of 144 months absent. | Drop it (Chap already does), or treat the absence as informative, or aggregate it with Vientiane Capital, which is geographically inside it. Each gives a different denominator for the headline mean. |
| 2 | **Xaisomboun stops reporting in 2006.** It was dissolved as an administrative unit during the period. | Exclude it from training as well as evaluation, keep it as a truncated series, or model it as censored. It affects training even though it contributes no evaluated cell. |
| 3 | **`population` is a single 2020 snapshot** applied to all thirteen years — confirmed, one distinct value per province. | Offset, rate, or ignored. Over 1998–2010 the implied error is a decade of growth, and it is not uniform across provinces. |
| 4 | **56% of observed months are zero**, and 6 of 16 evaluated provinces are above 85%. | The observation model for the counts: Poisson, negative binomial, zero-inflated, or hurdle. Also whether near-zero provinces are modelled at all. |
| 5 | **The zero rate falls monotonically** from 64% to 34% across the period. | A reporting-intensity trend confounded with incidence. Model it, ignore it, or restrict the training window — and the last of these changes what every model is scored on. |
| 6 | **Unweighted mean CRPS across provinces** weights a province with four cases in twelve years like the capital. | Population weighting, case weighting, or reporting the per-province spread and refusing to aggregate. §2 fixes the headline; the alternatives belong beside it. |
| 7 | **The lag structure** — rainfall at 1, temperature at 2–3, humidity at 0–1, with a wide band across provinces. | Which covariates, at which lags, and whether the lag is shared across provinces or fitted per province. |
| 8 | **`n_retrain = 1`.** The model is fitted once, on data up to the first split point. | Retraining at every split is more realistic and more expensive. Left at chap-core's default and flagged, not tuned. |
| 9 | **The `rainfall` unit contradicts the schema.** | Not a modelling fork — but it is a trap for any knowledge-informed prior taken from the literature, which is one of the model families [[trustAgenticSupplementary]] §S2 names. |
| 10 | **The evaluated window is the least zero-heavy part of the record.** | Not a fork either, but a stated expectation: some development-to-holdout drop is predicted by the data, independently of anything the agent does. |

Items 1, 2, 3, 5 and 6 change the **data or the evaluation**, so under the plan's §4b rule
they re-score every model including the reference. Items 4, 7 and 8 are internal to our
candidates and move only ours. Batch 5 writes the manifest; this is the list it starts from.

## 9. Decisions taken in this batch

| Decision | Basis | Agency |
|---|---|---|
| Development `n_periods 3`, `n_splits 8`, `stride 3`, `n_retrain 1`; phase E `3, 4, 3` | §6 above. `n_periods` follows from the human's choice of reference model; the rest is the agent's, from seven costed candidates. | agent-autonomous (`n_periods`: agent-on-human-assessment) |
| The data is pinned by commit, fetched by a script, and the archive is write-once with a checksum manifest | The same objection §3 of the plan makes against a hosted Chap service, applied to the data: a headline number computed from a file fetched at run time depends on another repository's current state. | agent-autonomous |
| Data acquisition is **not** a node in the claim tree; the fetch script lives in `AI-internal/data-acquisition/` and its record beside the data | The same split batch 2 made for reconnaissance. The tree analyses dengue in Laos and starts from the archived file; how that file arrived is provenance. A node writing into `Archive/` would also break the read-only rule. | agent-autonomous |
| `(IS_SHADOW)` is recorded in the folder's README and `provenance.md` rather than in the data files | The marker inserts a line into the document. Inserting a line into a CSV is an edit to imported data and breaks the checksums. | agent-autonomous |
| The holdout is written to `01_partition/results/` with the seal in its filename, rather than kept outside the tree | It is an output of a node like any other, and it is verified where it is made. The filename carries the seal so no glob can pick it up unremarked. | agent-autonomous |
| The partition is verified on the text lines, and by sorted-content equality plus subsequence rather than by concatenation | A parser round trip re-formats floats, so a pandas-based check would be a claim about a formatter. And the file's ordering makes concatenation the wrong test — see §2. | agent-autonomous |
| Where the holdout's 24 missing target cells fall was not examined | The plan's §3 permits row counts, provinces present and missing months, "and nothing further". Their positions are a pattern in the target. Phase E will need them; phase E can have them. | agent-autonomous |
| Node scripts run under `environment/chapenv`, and `node.py` now generates `run.sh` accordingly | `node.py` emitted `../.venv/bin/python`, which resolves to nothing below the first level of the tree and named the repository's own machinery rather than the pinned analysis environment. A node's declared environment and its generated main script now agree. A change to how every node's main script is generated is a methodological change (Rule 4). | agent-autonomous |
| Correlations are Spearman, computed within province and then pooled | More than half the observed months are zero, and a rank statistic does not depend on how the ties are transformed. Pearson on `log1p` is equally defensible and is a phase-D perturbation, not a settled question. | agent-autonomous |

## 10. Compliance for this batch

- **Rule 1** — every figure in this report comes from a file under `analysis/01_data/*/results/`,
  each with a provenance record naming its script, invocation, input hashes, environment,
  commit and agency. Nine records, one per script.
- **Rule 2** — nothing produced was edited. The two scripts whose first version was wrong were
  corrected at the source and the tree re-run; no output file was patched.
- **Rule 4** — committed before the run (`1ae2649`, which is the commit recorded in every
  provenance record) and after it, with the run named.
- **Rule 5** — the development file, the sealed holdout, twelve characterisation tables, four
  scheme tables and five pre-aggregation files are all stored, in CSV and JSON. 1.6 MB in
  total, annotated by `/annotate-criticality` in `analysis/01_data/criticality.md`.
- **Rule 6** — no randomness anywhere in this batch, and that is verified rather than asserted:
  `analysis/run.sh` was run twice in succession and every output file, PNGs included, came
  back byte-identical.
- **Rule 7** — five figures, each with its plotted values, its pre-aggregation values where
  the figure aggregates, its own plotting script and its own provenance record.
- **`/validate invariants`** — passes: tree, provenance, plots, seeds, claims, git, crossing.
- Rules 3, 8, 9 and 10 have no surface here: the environment did not change, no report was
  generated, no claim was entered, nothing was released.

## 11. What is still unknown, and what batch 4 needs

Ordered by what it would cost to discover late.

1. **Whether `chapkit_ewars_model` runs at all on this machine.** Unchanged from batch 2 and
   still the single most important open question — §2 of the plan has no criterion until it
   is answered. **Docker Desktop must be running before batch 4 starts.** The image is
   amd64-only on an arm64 machine, so emulated R-INLA speed is the risk, and how many splits
   an EWARS run costs at `n_splits 8` is now a concrete number rather than a guess.
2. **What a real model costs per evaluation run.** Batch 2's 42 seconds was process overhead
   with a linear regression attached. With the scheme fixed at 8 splits, batch 4 can give
   batch 5 a per-run figure in the units the budget needs.
3. **Whether `chap-models-checker` publishes scores**, and whether any are on Lao data.
4. **Whether the Docker layer of `environment/` builds.** Unverifiable while the daemon is
   down; cheap once it is up.
5. **How model configuration reaches a model in practice** — `--model-configuration-yaml` and
   `user_options` are documented but have not been exercised.

Batch 4 needs nothing from batch 3 that is not now on disk: the development file, the fixed
scheme, and the knowledge that the metric covers 16 provinces.

## 12. For the human

- **The metric covers 16 of 18 provinces**, and six of those sixteen are near-permanently
  zero. This is not a defect introduced by any choice made here — it is what the plan's
  headline metric computes on this dataset. It is worth knowing before the first number
  arrives, and it is the strongest argument yet for §2's insistence on reporting the
  per-region spread beside the mean.
- **Some development-to-holdout drop is predicted by the data itself.** The zero rate falls
  from 64% to 34% across the record, so 2008–2009 is the easiest stretch of the development
  period. When phase E reports a gap, part of it will be this, and it will not be evidence of
  the agent inflating its own performance. Saying so now, with no numbers in hand, is what
  makes the distinction credible later.
- **Docker Desktop before batch 4**, as batch 2 already flagged.
