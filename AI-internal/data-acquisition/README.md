# data-acquisition

Scripts that bring external data into `Archive/`. One-off by nature: once a file is
archived and committed, the repository reproduces without network access, and re-running a
fetch script verifies rather than refetches.

These are not nodes in the claim tree. The tree analyses dengue in Laos and starts from the
archived file; how that file arrived is provenance, and it is kept beside the data in
`Archive/<dataset>/provenance.md`. The split between the two is the same one batch 2 made
for `AI-internal/reconnaissance/`: a fact about how the instrument or the input was obtained
does not belong on the same footing as a finding about the data.

## Currently here

- `fetch_lao_dataset.sh` — fetches the three Lao files (`chap_LAO_admin1_monthly.csv`,
  `.geojson`, `_schema.json`) from `dhis2/climate-health-data` at commit
  `af362d52…` into `Archive/lao-dataset/`, and writes `sha256sums.txt`. Refuses to
  overwrite an existing file, because `Archive/` is write-once; on a populated archive it
  checks the checksums instead. `--verify` fails rather than fetching if anything is
  missing.
- `fetch_lao_population.sh` — fetches the World Bank's annual national population series
  for Lao PDR (indicator `SP.POP.TOTL`, 1990–2021) into `Archive/lao-population/`, and
  writes `sha256sums.txt`. Same write-once behaviour and the same `--verify`. The archived
  dengue dataset carries one static population figure per province; this series is what
  `analysis/02_setup/01_population/b_backCast` scales it by. An API cannot be pinned by
  commit the way the dataset is, so the request fixes the year range and the response's
  own `lastupdated` vintage is recorded in the provenance file beside the checksum.
