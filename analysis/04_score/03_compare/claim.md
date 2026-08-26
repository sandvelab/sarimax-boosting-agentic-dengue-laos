# Claim

How do the models compare, and can the comparison separate them? The leaderboard from the stored scores, and the paired per-cell difference against the reference with its spread — the paired form because forecasting difficulty varies far more between periods than between models, and that variation is common to both sides.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The paired comparison is roughly three times tighter than the unpaired one, and it is
still not tight enough to separate a 2 CRPS difference.** That is the answer to the question
batch 4 left open, and it changes what phase C has to aim at.

The numbers, all in `results/main/paired_summary.csv` and `comparison_notes.json`:

- the unpaired standard error of the reference's own CRPS across splits is **5.68** — the
  figure batch 4 reported, recomputed here;
- pairing cell by cell brings the standard error of a model difference to **1.34** for
  climatology and **2.05** for persistence, if the 371 cells are treated as independent;
- clustering by split — which allows the cells inside a split to be correlated in any way,
  and they are — gives **1.92** and **2.99**;
- climatology is **2.24 CRPS worse** than the reference and persistence **2.78** worse. Both
  differences are inside two clustered standard errors of zero.

So the comparison's resolution on this dataset is about **4 CRPS at anything like
conventional confidence** — wider than the entire gap between the persistence baseline and
the reference. A candidate that beats the reference by one or two CRPS on the development
backtest will not have been shown to beat it.

Two further findings sharpen that. The per-cell win rate is **44 %** for climatology and
**47 %** for persistence: at the level of an individual province-month the baselines and the
reference are close to a coin flip, and the reference's advantage comes from a minority of
cells rather than from being broadly better. And the reference's own unseeded repeats differ
by up to **0.57 CRPS** in the same paired statistic, which is the floor below which nothing
can be attributed to a model at all.
