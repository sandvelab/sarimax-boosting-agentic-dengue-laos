# Provenance — Lao population series

Imported source data, **never edited**. Append; never overwrite an existing section.

---

## worldbank_SP.POP.TOTL_LAO_1990-2021.json — 2026-08-29

```
source:              World Bank Open Data
indicator:           SP.POP.TOTL — "Population, total"
country:             LAO (Lao PDR)
years requested:     1990:2021
vintage:             lastupdated 2026-07-13, as reported in the response's own header
underlying source:   United Nations World Population Prospects, redistributed by the
                     World Bank
fetched by:          AI-internal/data-acquisition/fetch_lao_population.sh
invocation:          bash AI-internal/data-acquisition/fetch_lao_population.sh
fetched from:        https://api.worldbank.org/v2/country/LAO/indicator/SP.POP.TOTL
                     ?format=json&per_page=200&date=1990:2021
retrieved:           2026-08-29
licence/governance:  CC BY 4.0. Public and redistributable, like everything else here,
                     so the release scan is about secrets, not permissions.
```

Checksum as fetched, and re-verified on every run of the node that reads it:

```
b86c1fa0da08ce671c42ff0353f53432e5fb447b0f001333b77894046cbe85b1  worldbank_SP.POP.TOTL_LAO_1990-2021.json
```

**Why this is pinned more weakly than the dengue data, and what stands in.** The Lao
dataset is pinned by a repository commit; an API has no commit. The World Bank revises
this series, and the same URL will return different numbers after a revision. Three
things substitute. The request fixes the year range, so the rows cannot move for reasons
of coverage. The response carries its own `lastupdated` field, which names the vintage
and is recorded above. And **the analysis reads the archived file, never the API** — so
the project reproduces from `Archive/` whatever the World Bank does later, and a
re-fetch that disagrees fails against the checksum rather than replacing the numbers.

**What the file does and does not support.** It is a national annual total: 5 248 266 in
1998 rising to 6 334 194 in 2010, with no missing years across the requested range. It
supports scaling a snapshot by how much the country grew between two years. It does not
support any statement about one province growing faster than another, and the node that
uses it says so rather than letting a national ratio look like provincial detail.

**Why the World Bank rather than the Lao Statistics Bureau's censuses.** The censuses of
1995, 2005 and 2015 are the only provincial-level measurements of Lao population in this
period, and a provincial series interpolated between them would be the better input. They
were not used: there is no machine-readable, stably addressable release of the provincial
tables that this script could pin the way it pins the file above, and an input transcribed
by hand from a PDF is exactly the manual data manipulation step `AGENTS.md` Rule 2 exists
to keep out of the record. The national series is the alternative that can be fetched,
checksummed and re-obtained, and the loss — that the back-cast moves every province by the
same factor — is stated where it bites rather than buried here.

**agency:** agent-autonomous. That the static population column is a problem was
established from the data by batch 3; that the alternative to it is a back-cast was fixed
by batch 5's fork design and by batch 12's `claim.md` for the child. The choice of the
World Bank series as the thing to back-cast from, and the decision not to chase the
provincial censuses, are the agent's.
**information:** agent-retrieved — the series is fetched from the API, and the schema's
attribution of the population column to WorldPop is read from
`Archive/lao-dataset/chap_LAO_admin1_monthly_schema.json`.

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
