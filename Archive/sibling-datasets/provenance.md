# Provenance — sibling datasets (Thailand, Vietnam)

Imported source data, **never edited**. Append; never overwrite an existing section.

---

## tha/ · vnm/ — six files — 2026-09-04

```
source repository:   https://github.com/dhis2/climate-health-data
paths within it:     tha/, vnm/
commit:              af362d5260c6e7de1739f3d05314a844bd272613
commit date:         2026-04-22T13:57:28Z
commit subject:      chore: rename admin boundaries for Chap compatibility (#11)
resolved:            2026-08-23, as the head of `main`, via the GitHub API; reused here
                     unchanged, so all three countries come from one state of one dataset
fetched by:          AI-internal/data-acquisition/fetch_sibling_datasets.sh
invocation:          bash AI-internal/data-acquisition/fetch_sibling_datasets.sh
fetched from:        https://raw.githubusercontent.com/dhis2/climate-health-data/
                     af362d5260c6e7de1739f3d05314a844bd272613/<tha|vnm>/<file>
retrieved:           2026-09-04
licence/governance:  public and redistributable (plan §4), on the same terms as the Lao
                     files. Nothing here is access-restricted.
```

Checksums as fetched, and re-verified on every run of `analysis/06_external/01_ingest`:

```
423d8b73b6e42bc90db8fea2db77463af77f8c30b6b02b66825acd51b83a1e42  tha/chap_THA_admin1_monthly.csv
f65e32f0e172ca27aa3af13f95ed1dabd6992d019fb868f3280e5cea78bde2e0  tha/chap_THA_admin1_monthly.geojson
65666180c84f774d1c285de3a71a63c37701124439cc9dcac4b7f56662ae6b97  tha/chap_THA_admin1_monthly_schema.json
a36ac87b936bd8ceee8d47eaeb798aae4988b4bfb921d68970096c534ae9b919  vnm/chap_VNM_admin1_monthly.csv
d640c90a9201098296e2897b4f1d86453f9112ec462b4e8c563bd2157898082d  vnm/chap_VNM_admin1_monthly.geojson
6ffa19e0a6c0b543d9e1801c3dfa1f2086e72df0adef89bd346d184857971e2a  vnm/chap_VNM_admin1_monthly_schema.json
```

**Why the same commit as the Lao files.** The external check compares three countries. If a
sibling were fetched at a later commit, a difference between countries would also be a
difference between harmonisations, and neither could be separated from the other.

**What the two schemas say, and what the files say.** Established by
`analysis/06_external/01_ingest`, whose `schema_reconciliation.json` is the executed record
of it; repeated here because a reader who starts from a schema should not be misled.

- `row_count` **does not mean the same thing in the three files.** Vietnam declares 9 612
  against 9 828 rows and Laos 2 575 against 2 808 — in both, the figure is the number of
  rows carrying a non-missing `disease_cases`. Thailand declares 27 720, which is its row
  count exactly, while only 27 024 of those rows carry a case value. So the field counts
  complete records in two files of this harmonisation and rows in the third.
- `rainfall`, declared in all three as a total in millimetres accumulated over the month, is
  a **mean daily rate in mm/day** in all three. Summing the monthly values over a year gives
  23–103 mm; multiplying by the days in a month puts the same years at roughly
  1 500–2 000 mm. Batch 3 established this for Laos from the monsoon profile; the siblings
  carry the same error, so it is the harmonisation's and not the Lao file's.
- **Thailand's `population` is not a static snapshot.** Its schema describes annual WorldPop
  values interpolated between the 2000, 2010 and 2020 anchors and expanded to months, and
  the file matches: all 77 provinces carry a varying series. Vietnam's schema declares a
  static snapshot and its file carries one, as Laos's does. The judgment call the Lao
  analysis had to make between the archived static column and a back-cast series
  (`analysis/02_setup/01_population`) is therefore one the harmonisation itself answers
  differently for different countries.

**agency:** agent-autonomous. That these two datasets are the external check is the plan's
(`human-set`, §4, confirmed 2026-08-31); the fetch, the shared commit pin and the three
schema findings above are the agent's.
**information:** human-pointed — the two country codes come from
`Archive/case-source-material/chapOrientation.md` §4.

---

## Correction — 2026-09-05, batch 19, from the outsider check

Two sentences above name **`analysis/06_external/01_ingest`** as the node that re-verifies
these checksums and holds `schema_reconciliation.json`. **That node does not exist.**
`analysis/06_external` has no children; the node is **`analysis/01_data/03_siblings`**, as
`analysis/README.md` and the node's own `claim.md` say, and it is where both the checksum
verification and the schema reconciliation live.

The error is the agent's, made when this file was written before the node was placed. It is
appended rather than applied above because `AGENTS.md` §8 makes `Archive/` read-only and this
file's own header says to append and never overwrite an existing section.

Found by `/validate outsider` on 2026-09-05, which followed the path and found nothing there
— the shape of finding this check exists to produce, and one no invariant looks for: a path
in a provenance record is prose until somebody walks it.

**agency:** agent-autonomous.

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
