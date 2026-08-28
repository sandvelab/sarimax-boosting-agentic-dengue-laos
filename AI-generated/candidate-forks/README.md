# candidate-forks

What each alternative to a candidate's configuration scores on the development data, what
each candidate *family* scores at its own main path, and the rules by which one of each
becomes the main path. Produced by `AI-internal/useful-scripts/candidate_fork_sweep.py` — in
batch 9 for candidate 1, batch 10 for candidate 2 and batch 11 for candidate 3 — and by
`family_leaderboard.py`, new in batch 11 for the family fork itself.

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

- `boosted_round1/` — batch 10: candidate 2's two forks, swept around its own family
  combination `family_boosted`. Neither fork moved: the richer feature set is worth 0.396
  CRPS and the quantile head costs 0.189, both inside the 0.565 floor.

- `ensemble_round1/` — batch 11: candidate 3's one fork, swept around its own family
  combination `family_ensemble`. The fork does not move, and by the largest margin in the
  project: fitting the pool's weights on a validation year held back inside the training
  frame costs **4.021** CRPS, seven times the floor and in the wrong direction.
- `families/` — batch 11: what each of the three families scores at its own main path. **The
  table the family fork was promoted from.**

- `family_rule.md` — the rule deciding which *family* the main path takes, written after
  `families/family_leaderboard.csv` existed and committed before the promoted family was run
  under `main`. Batch 9's threshold unchanged, with one clause added that an internal fork
  does not need: a family that wins on mean CRPS while being badly calibrated has not won.
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
