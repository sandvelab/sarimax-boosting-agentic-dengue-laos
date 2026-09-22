# Sibling datasets — Thailand and Vietnam

The two other country folders of the CHAP harmonized dataset, fetched at the same pinned
commit as the Lao files in `../lao-dataset/`. **Imported source data, never edited**
(`AGENTS.md` §8); `provenance.md` records where each file came from and what was found in it.

They are **not** part of the headline analysis and no model is developed on them. They are
the external check the plan's §4 names: the reported model, unchanged, run on two other
countries, to see whether anything measured on Laos holds anywhere else. Batch 20 does that,
in `analysis/06_external/`.

Currently here:

- `tha/` — `chap_THA_admin1_monthly.csv`, its boundary `.geojson` and its `_schema.json`.
  77 provinces, 1993-01 to 2022-12, 27 720 rows.
- `vnm/` — the same three files for Vietnam. 63 provinces, 1998-01 to 2010-12, 9 828 rows —
  the same calendar as the Lao file.
- `sha256sums.txt` — checksums as fetched, re-verified by the fetch script and by
  `analysis/06_external/01_ingest` on every run.

Fetched by `AI-internal/data-acquisition/fetch_sibling_datasets.sh`, which is write-once:
run against a populated archive it verifies rather than refetches.

---

## Correction, 2026-09-23 (batch 19)

**Everything above describes the prior project.** It is left in place because `Archive/` is
read-only, and corrected here.

- `analysis/06_external/` and `analysis/06_external/01_ingest` **do not exist in this
  repository**, and neither does `analysis/01_data/03_siblings`, which an earlier correction in
  `provenance.md` offered as the real name. Nothing re-verifies these checksums on every run.
- **This project does not use the sibling datasets at all.** Its plan §4 lists them as
  "available as an optional external check, **not required**", and its ledger row 20 is Release,
  not an external check. No node reads this folder.
- The data and its checksums are unchanged and still verify; what was stale is the prose.

The files here are kept because raw data is a re-usable resource and not the prior project's
output (plan §4). If a future batch does build an external check, it gets a node of its own and
this section is superseded by that node's `claim.md`.
