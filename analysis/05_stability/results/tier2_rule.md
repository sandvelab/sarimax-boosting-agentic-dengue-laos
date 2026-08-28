# Tier 2 — how the eight pairs are selected

Fixed in batch 12, **before any tier-1 combination had been run**, and applied by
`plan_manifest.py` from `conclusions.csv` rather than by anyone reading it. Choosing which
pairs to explore after seeing tier 1's numbers is selection with extra steps, which is the
objection this plan makes to an unfrozen holdout manifest, applied one level down.

1. Rank every tier-1 row that has a conclusion by `|skill_score − skill_score(main)|`,
   largest first, read from `results/conclusions.csv`.
2. **Group S** — the two highest-ranked rows whose fork kind is `setup`.
3. **Group M** — the two highest-ranked rows whose fork kind is `candidate`, `family` or
   `baseline`: the three kinds that move our model and leave the dataset alone.
4. **Group A** — the one highest-ranked row whose fork kind is `scoring`.
5. Tier 2 is every pair drawn from **two different groups**: S×M gives four, S×A two,
   M×A two. Eight combinations.
6. No pair is ever formed from two children of the same fork. The three groups are
   disjoint by fork kind and no fork has two kinds, so this holds by construction rather
   than by a check.
7. If a group has fewer rows than it asks for, it contributes what it has and the
   shortfall is recorded in `manifest_notes.json`. The rule is not adjusted to reach eight.

Ties in step 1 are broken by combination name, ascending, so the rule is deterministic.
