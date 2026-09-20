# Claim

Do the required baselines (persistence, seasonal climatology), scored through the same native pipeline as stage 1, establish an honest sense of how much this project's backtest resolves?

## Children

kind: sub-analyses
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

Yes: on the identical 371-cell set stage 1 scores, persistence scores mean CRPS 28.32 and
seasonal climatology scores 26.91 (`01_persistence/claim.md`, `02_climatology/claim.md`).
Stage 1 alone (26.05) beats both: **7.99% lower mean CRPS than persistence, 3.20% lower than
seasonal climatology** — this backtest resolves enough for stage 1 to separate from both
required naive baselines, though the margin over climatology in particular is modest and its
robustness to reasonable alternative choices is not yet assessed (that is the stability
phase's job, plan §4). `results/comparison.json`.
