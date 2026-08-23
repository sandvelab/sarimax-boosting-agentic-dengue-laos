# Lao dataset — the data this project analyses

The three files of the CHAP harmonized dataset for Laos, fetched at a pinned commit and
**never edited here**. Monthly reported dengue counts for the eighteen admin-1 provinces,
1998-01 to 2010-12, with rainfall, mean temperature, mean relative humidity and a static
population figure.

`provenance.md` records the repository, the commit, the date, and the command that
re-obtains them. `sha256sums.txt` is the manifest written when they were fetched; every
run of the partition node re-checks the files against it, so a silent replacement fails
loudly rather than propagating.

| File | What it is |
|---|---|
| `chap_LAO_admin1_monthly.csv` | The data. 2 808 rows = 18 provinces × 156 months, a complete rectangular panel. |
| `chap_LAO_admin1_monthly.geojson` | Admin-1 boundary polygons, for models that declare `requires_geo`. |
| `chap_LAO_admin1_monthly_schema.json` | Field-level schema with per-field sources. Two of its statements do not describe the file — see `provenance.md`. |
| `sha256sums.txt` | Checksums of the three files as fetched. |

**The `(IS_SHADOW)` marker of `AGENTS.md` §8 cannot be applied to these files.** The
convention inserts a line into the document, and inserting a line into a CSV would edit
imported data, which `Archive/` forbids and which would break the checksums that make the
import verifiable. The whole folder is shadow; this README and `provenance.md` say so, and
nothing in the repository writes to it.

**Read the whole file only through `analysis/01_data/01_partition`.** That node is the one
place licensed to open `chap_LAO_admin1_monthly.csv` end to end; it writes the development
period and the sealed 2010 holdout, and everything downstream reads those. See the plan's
§3.
