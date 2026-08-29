# Claim

Replace the single population snapshot with a per-province, per-year series back-cast from it, so the figure a model divides by is roughly right at both ends of the record instead of only at the end. The snapshot is a 2020 measurement applied to 1998-2010, and a decade of growth is not uniform across provinces.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The snapshot becomes a per-year series: `population(province, year) = snapshot x N(year)/N(2020)`, scaled from **0.7144** in 1998 to **0.8496** in 2009 (`results/popColumn_backCast/setup_spec.json`). The conclusion moves from +0.1485 to **+0.1347** — the pool still beats the reference, by slightly less.

**The archived column does not have the level its schema claims.** It sums to **4 961 076** across the eighteen provinces; the national total at the schema's stated reference year of 2020 is **7 346 533**, and the year whose total is nearest the snapshot's is **1995**. This is the third statement in that schema found not to describe the file. The anchor is used as declared anyway, and the discrepancy recorded: changing the reference year multiplies every population by one constant, which a log offset absorbs, so what the fork actually probes is the shape of the trend.

The series is national, so every province is scaled by the same factor. The fork probes a trend, not a provincial differential, and `Archive/lao-population/provenance.md` records why the censuses that would give one are not here.
