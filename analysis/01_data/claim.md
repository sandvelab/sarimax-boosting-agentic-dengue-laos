# Claim

What does the Lao admin-1 monthly dengue dataset contain, and on what part of it may development happen? The node separates the held-out final year from the development period before anything characterises the data, then describes the development period only.

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The held-out year is separated before anything looks at the data, and the separation is
verified rather than asserted; the development period is then described on its own. The
answers are at the two children — `01_partition` for the partition, the schema
reconciliation and the Chap ingest; `02_characterise` for what the development period
contains and for the backtest scheme, which is fixed here and does not move again.

**The data problems this node found, each a candidate fork for phase D**, are listed in the
batch-3 report `AI-generated/batch-reports/26-08-23_b03_dataCharacterisation.md` §6. The
three that change what the headline number means are: one province absent from the metric
entirely and a second contributing nothing; a static population figure that makes any rate
wrong by a decade of growth; and an unweighted mean over provinces whose burdens differ by
four orders of magnitude.
