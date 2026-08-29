# Lao population series — what the population fork back-casts from

The annual national population of Lao PDR, imported from the World Bank's open data API
and **never edited here**. It exists for one purpose: the archived dengue dataset carries
a single static population figure per province, and `analysis/02_setup/01_population`'s
alternative child scales that snapshot by this series to get a per-year figure.

`provenance.md` records the indicator, the vintage, the retrieval date and the command
that re-obtains the file. `sha256sums.txt` is the manifest written when it was fetched;
the back-cast script re-checks the file against it on every run, so a silent replacement
fails loudly rather than propagating into a population column.

| File | What it is |
|---|---|
| `worldbank_SP.POP.TOTL_LAO_1990-2021.json` | The World Bank API response, as returned: 32 annual national totals, 1990–2021, no missing years. |
| `sha256sums.txt` | The checksum of that file as fetched. |

**The `(IS_SHADOW)` marker of `AGENTS.md` §8 cannot be applied to the JSON file.** The
convention inserts a line into the document, and inserting a line into JSON would edit
imported data and break the checksum that makes the import verifiable — the same reason
`lao-dataset/` gives. The whole folder is shadow; this README and `provenance.md` say so,
and nothing in the repository writes to it.

**This is a national series, not a provincial one.** It can say how much the country grew
between two years; it cannot say which provinces grew faster. What that costs the fork
that uses it is stated in that node's `claim.md` and in the script that reads the file,
because it is a limitation of the alternative rather than of the archive.
