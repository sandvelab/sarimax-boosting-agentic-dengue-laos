# Provenance — Vientiane province merged into Vientiane Capital

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
                     results/$COMBO/merge_weights.csv
script:              scripts/apply_provinces.py
                     sha256:439179088190ebd9db438a4a0972ce5a8529cc0164eb6462915f1d7e4e8d3bdd
invocation:          "$PYTHON" scripts/apply_provinces.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=provinces_mergeVientiane.)
inputs:              the analysis dataset produced by whichever child of 02_trainingWindow
                     ran in this combination — resolved by search, not by name, and its
                     sha256 recorded in results/$COMBO/setup_spec.json as `input_sha256`
                     Archive/lao-dataset/chap_LAO_admin1_monthly.geojson
                     sha256:cc823bf48dd3fc74f36bd8a652e03f51ca832e96ef42ebe5e098a94ca07e3389
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The merge is arithmetic on two rows and a pair of fixed weights.
commit:              40b6936
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/03_provinces/c_mergeVientiane
produced:            2026-08-29
```

**What it establishes.** LA-VI is folded into LA-VT: 2 592 rows in, 2 448 out, 17 provinces,
and the same **371** evaluable cells (`results/$COMBO/setup_spec.json`). The merged unit's
population is 1 308 736 against the capital's 960 194, and the two constituents' geodesic areas
put **78.1 %** of the merged polygon in the province and 21.9 % in the capital
(`results/$COMBO/merge_weights.csv`) — so the merged climate covariates are largely the
province's. In 1998-01 the capital's rainfall goes from 0.075 to 0.251 mm/day and its mean
temperature from 24.13 to 22.64 °C, which is what merging a small river-plain prefecture into
the large upland province around it should do.

**The cell count does not move, and the cells are not the same cells.** This is the child batch
12 flagged as possibly unscoreable because it changes what the metric is a mean over. It turns
out to change the *content* of the capital's 24 cells rather than the *number* of cells: LA-VI
contributed none to begin with. Raw CRPS across this row and the others is therefore comparable
in count and not in kind, which is the reason the project's headline is a ratio to a reference
run on the same cells rather than a raw score.

**Three merge rules, each a judgment.** Counts add, with a cell missing only when every
constituent is missing; population adds, per row rather than per province, so the rule survives
the population fork's per-year series unchanged; and the three climate columns are area-weighted
means, because they are ERA5-Land fields aggregated over the admin polygon and the mean over a
union of polygons is the area-weighted mean of the parts. The weights are geodesic areas
computed from the archived boundary file, and both the areas and the file's checksum are in the
specification.

alternatives-considered: **missing when any constituent is missing**, the conservative reading
of a merged count — rejected because the donor never reports at all, so it would erase the
capital's entire series and turn the fork into a deletion. **Population-weighted climate** —
rejected because it answers "what climate did the average person experience", which is a
different quantity from the one the column holds; mixing the two inside one column is exactly
the silent redefinition this repository exists to make visible. **Renaming the merged unit** to
"Vientiane Capital and Vientiane" — rejected as an untested change to a string column that
chap-core reads, for no gain the specification does not already provide: `merge` names the
constituents and `merged_unit_reported_under` says the row carries the receiver's code and name.
**Merging on the geojson's adjacency** rather than by a named pair — rejected because nothing in
the data says the capital lies inside the province; that is a geographic fact supplied by the
agent, and it belongs in the record as a declaration rather than dressed up as a derivation.

agency: agent-autonomous. The existence of the fork and its claim are batch 5's and batch 12's;
the pair to merge, all three merge rules, the use of geodesic polygon areas as weights and the
rejection of the alternatives above are the agent's.
information: agent-retrieved — the polygons come from the archived boundary file and the
evaluated span from the stored scheme. That Vientiane Capital is a prefecture carved out of
Vientiane province is general geographic knowledge the agent supplied and no file in this
repository states; it is the one input to this node that is not read from disk, and it is
declared here for that reason.
