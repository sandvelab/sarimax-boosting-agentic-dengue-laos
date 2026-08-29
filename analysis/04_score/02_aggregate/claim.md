# Claim

Over what weighting is the headline mean taken? The provinces differ in burden by four orders of magnitude, so an unweighted mean over cells and a mean weighted by population or by cases are three different summaries of the same per-cell file.

## Children

kind: alternatives
main-path: a_unweighted

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The headline figures under the unweighted mean, and the four resolutions beside it. The
per-province file is where the aggregate's weakness shows: mean CRPS per province spans four
orders of magnitude, from 0.01 in Phongsaly to 84 in Vientiane Capital, so the unweighted
mean over cells is very nearly a statement about the largest few provinces.

**Both siblings are built and run, and this is the fork the conclusion is most sensitive to.** Population weighting gives **+0.2288** and case weighting **+0.2320**, against the main path's +0.1485 — moves of about **+0.08 of skill**, where the five `02_setup` forks move it by at most 0.038. Re-weighting the same per-cell file, re-running no model, moves the headline four times as much as changing the dataset. They cost thirteen seconds each.

**Under case weighting persistence beats our pool** (86.598 against 88.484), and our pool's 10-90 coverage falls from 0.863 to 0.701 — over-dispersed on the quiet months that dominate the unweighted mean, under-dispersed on the outbreak months that dominate this one. Neither summary alone shows that.

**One known gap.** `03_compare` computes the paired difference, the clustered standard errors and the split-level comparison from the unweighted per-cell file. So under a weighted row, `conclusion.json` carries a re-weighted `skill_score` beside paired statistics that are still unweighted: the headline is weighted and the spread is not. Teaching `compare_models.py` to read `weights.csv`, including a weighted clustered standard error, is a change to shared code every combination runs, and it is recorded here and assigned to batch 14 rather than done quietly.
