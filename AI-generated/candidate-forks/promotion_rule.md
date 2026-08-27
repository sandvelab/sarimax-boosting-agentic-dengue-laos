# The rule by which batch 9 promotes a main path

Written after `fork_leaderboard.csv` existed and **before** the promoted combination was
run, and committed in that state, so that what it decides cannot have been fitted to what
it decided. The one number it could have been fitted to is the sweep's own ranking, which
is why the rule is expressed in a threshold fixed by an earlier batch rather than in
positions on that ranking.

## The rule

1. **A fork moves only if its best child beats the current main path by more than 0.57
   CRPS.** That is the resolvable-difference floor batch 7 measured from the unseeded
   reference model's own repeats: below it, a difference cannot be attributed to a model
   at all. A fork whose best sibling is inside the floor stays where it is, however it
   happens to be ranked.
2. **Where a fork moves, it takes its best-scoring child**, even if the gap between that
   child and the next is itself inside the floor. Something has to be taken, and the
   ranking is the only ordering available; that the fork could not separate its top two is
   recorded rather than resolved.
3. **The promoted combination is then run and scored.** Promoting several forks at once
   asserts that their effects combine, and nothing in a one-at-a-time sweep tests that.
4. **If the promoted combination is worse than the best single-fork combination by more
   than 0.57 CRPS, the promotion is backed off** to that single fork alone, and the
   interaction is recorded as the finding it would be.

## What the rule is not

It is not the phase-C stopping rule, which is a different threshold (0.4 CRPS, fixed in
batch 5) answering a different question -- whether a further *candidate* batch is
admissible. This rule governs which child of a fork the main path takes inside one
candidate.

It is also not a claim that the promoted configuration is the right one. Every rejected
sibling stays in the tree and is re-run in phase D and on the held-out year, which is what
turns a selection made on development CRPS into a measured cost rather than an argued one.
Selecting hard on development CRPS is precisely the failure the plan's phase C warns
about, and the rule above does not avoid it -- it only makes it visible and bounded.

## What it selects, on the sweep as run

The sweep's base is the batch-8 configuration, mean CRPS **26.100**. Against it:

| fork | best child | mean CRPS | moves the main path by | clears 0.57? |
|---|---|---|---|---|
| `01_observation` | `c_hurdle` | 23.985 | 2.115 | yes |
| `06_yearVariance` | `b_provinceScaled` | 24.230 | 1.870 | yes |
| `02_covariates` | `c_climateFree` | 25.452 | 0.648 | yes |
| `04_fitTime` | `b_refitAtPredict` | 25.692 | 0.408 | no |
| `03_population` | `c_ignored` | 26.150 | −0.050 | no |
| `05_autoregressive` | `b_lag3` | 26.175 | −0.075 | no |

So three forks move and three stay. The best single-fork combination, against which
clause 4 is checked, is `observation_hurdle` at **23.985**.
