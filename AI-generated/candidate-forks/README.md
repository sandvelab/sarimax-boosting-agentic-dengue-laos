# candidate-forks

What each alternative to candidate 1's configuration scores on the development data, and the
rule by which one of them became the main path. Produced in batch 9 by
`AI-internal/useful-scripts/candidate_fork_sweep.py`.

**Every number here is copied from a file inside the tree.** Each combination is run by the
tree's own scripts and writes its results under `results/<combination>/` at the nodes that
produced them; only the cross-combination tables live here, and the driver copies them from
`analysis/04_score/02_aggregate/a_unweighted/results/<combo>/metrics_summary.csv` rather than
computing anything a second time.

**This is a phase-C selection aid, not the phase-D stability result.** The stability node
(batch 12) runs a frozen manifest through the whole scoring chain and reports a distribution
of conclusions; this sweep stops at `02_aggregate` and answers only which child of each fork
the main path should take. Producing a conclusion per sibling here would report the stability
answer before the manifest that makes it honest exists.

**A sweep is taken around one main path**, and promoting a fork moves it, so each round has
its own directory. `summarise` refuses to rebuild a table whose recorded base configuration
is no longer the tree's.

## Currently here

- `promotion_rule.md` — the rule deciding which forks move, written after round 1's numbers
  existed and committed **before** the promoted combination was run.
- `round1_batch8Defaults/` — the sweep around the batch-8 configuration (mean CRPS 26.100).
  **The record the promotion was decided from.** The tree no longer holds the
  per-combination results behind it; round 2 replaced them, and they are at commit `49825b5`.
- `round2_promoted/` — the sweep around the promoted main path (23.698): what the
  alternatives are worth from where the model now stands, and `fork_interaction.csv`, which
  is what one sweep says a fork is worth against what the next one says.

Each round holds `fork_leaderboard.csv` (one row per combination), `fork_sweep.json` (the
base, the ranking and the base configuration's hash), `sweep_runs.json` (what ran and for how
long) and one `sweep_<combination>.log` per combination, carrying every command line.
