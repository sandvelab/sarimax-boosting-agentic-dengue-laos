# Provenance — Lao dataset

Imported source data, **never edited**. Append; never overwrite an existing section.

---

## chap_LAO_admin1_monthly.csv · .geojson · _schema.json — 2026-08-23

```
source repository:   https://github.com/dhis2/climate-health-data
path within it:      lao/
commit:              af362d5260c6e7de1739f3d05314a844bd272613
commit date:         2026-04-22T13:57:28Z
commit subject:      chore: rename admin boundaries for Chap compatibility (#11)
resolved:            2026-08-23, as the head of `main`, via the GitHub API
fetched by:          AI-internal/data-acquisition/fetch_lao_dataset.sh
invocation:          bash AI-internal/data-acquisition/fetch_lao_dataset.sh
fetched from:        https://raw.githubusercontent.com/dhis2/climate-health-data/
                     af362d5260c6e7de1739f3d05314a844bd272613/lao/<file>
retrieved:           2026-08-23
licence/governance:  public and redistributable (plan §4). Nothing here is
                     access-restricted, so the release scan is about secrets, not
                     permissions.
```

Checksums as fetched, and re-verified on every partition run:

```
19488aa1fc4d961ae1a6aeb75b874789576877664fce47713628f497a06fff56  chap_LAO_admin1_monthly.csv
cc823bf48dd3fc74f36bd8a652e03f51ca832e96ef42ebe5e098a94ca07e3389  chap_LAO_admin1_monthly.geojson
ff750db4202c32fc187b26bb3566b4f981b94467664502e76cbd09977dd06210  chap_LAO_admin1_monthly_schema.json
```

**Why a commit and not a branch.** `chap eval` will happily take a URL, and the plan's §4b
already pins the reference model by commit for the same reason: a headline number computed
from a file fetched at run time depends on another repository's current state, which is the
objection `AGENTS.md` makes against running Chap as a hosted service, applied to the data.
The commit above was the head of `main` on the day of the fetch; it is recorded so a later
reader can tell whether the file has moved since.

**Two statements in the schema do not describe the file**, both established from the data by
`analysis/01_data`, both recorded here so that a reader who starts from the schema is not
misled:

- `row_count: 2575` against 2 808 rows in the CSV. The file is a complete rectangular panel
  of 18 provinces × 156 months; 2 575 is the number of rows carrying a non-missing
  `disease_cases`. The field counts complete records, not rows. Neither figure is wrong; the
  label is. See `analysis/01_data/01_partition/results/rowcount_reconciliation.json`.
- `rainfall`, declared as a total in millimetres accumulated over the month, is a **mean
  daily rate in mm/day**. Read as a monthly total it puts a province's whole year at 50–78 mm;
  read as a daily rate it puts it at 1 518–2 383 mm, and the monthly profile peaks with the
  southwest monsoon. See `analysis/01_data/02_characterise/results/covariate_units_check.json`.

The schema also names `LAO_ADM1.geojson` as its boundary file, which the pinned commit had
just renamed to `chap_LAO_admin1_monthly.geojson`. The rename is the subject of that commit.

**agency:** agent-autonomous. The dataset and its repository are the plan's (`human-set`);
the commit pin, the fetch script and the write-once archive convention are the agent's.
**information:** human-pointed — the repository and the three filenames come from
`Archive/case-source-material/chapOrientation.md` §4.

---
section appended 2026-09-23 (batch 19, `/validate outsider`) — **the paths above belong to the
prior project and do not exist in this repository.**

This folder's data is unchanged and its checksums still verify; what is stale is the prose
around them. An outsider following the instructions found that no archived dataset's provenance
record here can be re-enacted as written, because every `fetched by:` line names
`AI-internal/data-acquisition/fetch_*.sh` and that directory was removed with the prior
project's own material. The data was **not re-fetched** for this project: `readme-at-start.md`
and plan §4 record that it is reused from the archived, checksummed, commit-pinned copies, and
batch 1 re-verified the checksums rather than fetching anything.

So: to re-obtain this data, go to the prior project's released record at
`github.com/sandvelab/veridical-agentic-dengue-laos`, which holds the fetch scripts and their
own provenance. To verify the copy that is here, compare against the checksums above — which is
what `analysis/01_data/01_prepare` does on every run.

Appended rather than corrected in place: this file is append-only (`AGENTS.md` §8) and the
sections above are a true record of how the data was obtained *by the project that obtained it*.

---
section appended 2026-09-23 (batch 20, `/release` data-permission scan) — **what the upstream
terms actually are, checked rather than asserted.**

The `licence/governance:` line above says "public and redistributable (plan §4)"; that is the
plan's human-set governance decision, not a licence. Checked at release time (agent-retrieved,
via the GitHub API and the OpenDengue website, 2026-09-23):

- The source repository `github.com/dhis2/climate-health-data` carries **no licence file**
  (GitHub reports `license: null`; its top level holds `README.md`, `.gitignore` and the three
  country folders). Its README states that it "contains data only", publishes "final,
  model-ready data artifacts" that "can be downloaded and consumed directly by Chap", and that
  the datasets are "already harmonized (e.g. derived from OpenDengue)".
- The schema file in this folder names the provider of every field. `disease_cases` is
  attributed to **OpenDengue** (`https://opendengue.org/data.html`); the climate fields to
  ERA5-Land (Copernicus Climate Data Store); the boundaries and names to OCHA COD-AB via HDX;
  `population` to WorldPop.
- **OpenDengue's website states "Content licensed under CC BY 4.0"** (The Dengue Mapping and
  Modelling Group, LSHTM). Redistribution of the case counts is therefore permitted with
  attribution, and this section is that attribution: dengue case data from OpenDengue
  (opendengue.org, LSHTM, CC BY 4.0), harmonised and redistributed by the DHIS2 Chap project at
  the commit recorded above.
- The ERA5-Land, COD-AB and WorldPop terms were **not** checked here; those fields are carried
  in the archived file as received and are not used by any model on the main path (the
  climate-covariate candidates `d_linearClimate` and `e_pooledRandomForest`, and one stability
  row, read them on development data only).

This repository's own `LICENSE` (CC BY 4.0) applies to the derived results, not to the imported
files, which remain under their upstream terms.

**agency:** agent-autonomous (the check and its recording); the governance decision it
qualifies is the plan's (human-set, 2026-09-20). **information:** agent-retrieved.
