# The rule by which batch 11 chooses the family main path

`03_models/03_candidate` is an alternatives node whose children are the model families, and
batch 5's design assigns the choice of which one the main path takes to this batch. This is
the rule it is chosen by. Written after `families/family_leaderboard.csv` existed and
**before the promoted family was run under `main`**, and committed in that state, so that
what it decides cannot have been fitted to what it decided.

It is deliberately not a new rule. Batch 9 fixed one for the forks *inside* a candidate and
batch 10 applied it unchanged to a second candidate, which is what made its verdict there
evidence rather than a choice. The same threshold governs here, from the same measured
floor, with one addition that the family fork needs and an internal fork does not.

## The rule

1. **The family fork moves only if the best family beats the family currently on the main
   path by more than 0.57 CRPS** — the resolvable-difference floor batch 7 measured from
   the unseeded reference model's own repeats. Below it a difference cannot be attributed
   to a model at all.
2. **Each family is compared at its own main path**, in the combination where it ran with
   every one of its internal forks at the child that fork declares. A family compared at
   some other configuration is a different model.
3. **The moved family is then run under `main`** and the whole scoring chain re-run there,
   because the reported conclusion is `analysis/run.sh`'s and nothing else.
4. **A family that wins on mean CRPS while being badly calibrated has not won** (the plan's
   §2). So the promotion is checked against interval coverage as well: if the winner's
   10–90 coverage is further from nominal than the current main path's, the promotion is
   **not** taken on CRPS alone and the case is put to the human rather than decided here.
   Calibration is read at the 10–90 level, not the 25–75 level, and the reason is measured
   rather than asserted: 56 % of this dataset's observed province-months are exactly zero,
   so a model with a large atom at zero has a 25–75 interval of [0, 0] in a large share of
   cells and its coverage there is bounded below by the target's shape.
   `c_ensemble/results/<combo>/pool_check.json` records that share for every model, so
   whether the artefact is what a 25–75 figure is showing is a number in a file.

## What the rule is not

It is not the phase-C stopping rule, which is a different threshold (0.4 CRPS, fixed in
batch 5) answering a different question — whether a further *candidate* batch is admissible.

It is not a claim that the promoted family is the right one. The two rejected families stay
in the tree, complete and runnable, and both are re-run in phase D and on the held-out year.
Selecting on development CRPS is the failure the plan's phase C warns about, and this rule
does not avoid it; it bounds it and makes it visible.

## What it selects, on the leaderboard as run

Each family at its own main path, over the same 371 cells, against the reference's 22.098
(`families/family_leaderboard.csv`):

| family | combination | mean CRPS | MAE | 10–90 | 25–75 | skill |
|---|---|---|---|---|---|---|
| `c_ensemble` | `family_ensemble` | **18.817** | 23.214 | 0.863 | 0.749 | +0.1485 |
| `b_boosted` | `family_boosted` | 20.771 | 26.953 | 0.825 | 0.693 | +0.0601 |
| `a_hierNB` | `main` | 23.698 | 27.569 | 0.701 | 0.582 | −0.0724 |

Clause 1: the best family beats the main path by **4.881** CRPS, which is 8.6 times the
floor. The fork moves, to `c_ensemble`.

Clause 4: the winner's 10–90 coverage is 0.863 against nominal 0.80, an error of +0.063;
the current main path's is 0.701, an error of −0.099. The winner is **closer** to nominal,
so the clause does not fire. It is worth naming what it does not say: `b_boosted` at 0.825
is closer to nominal than either, and the rule ranks on CRPS with calibration as a veto
rather than as a second score, so the promotion goes to the pool. The pool is nonetheless
the most over-dispersed model in the project and that is reported beside its score, not
under it.
