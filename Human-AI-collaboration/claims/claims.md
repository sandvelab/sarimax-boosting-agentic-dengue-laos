# Claim collection

Everything the analysis supports, each statement bound to the result grounding it. The
manuscript is written from this file; nothing enters the manuscript that is not here.

Format — one block per claim, appended by `/claims add`:

```
## C1
The statement, in one or two sentences.
grounds: analysis/02_measure/a_jaccard/results/summary.tsv
node: analysis/02_measure/a_jaccard
scope: holds for the strict filtering convention only
alternatives: the base-pair measure gives a weaker effect (see C9)
by: agent-autonomous
```

`by:` is the agency field — `human-set`, `agent-on-human-assessment` or `agent-autonomous`.
Claims about **stability** are claims like any other and belong here too: what the
perturbation set showed, and which choices the conclusion turned out to be sensitive to.

## C1
The conclusion this project reports is one member of a distribution over thirty-two analyses that all looked reasonable, fixed before any of them ran. The reported skill score against the reference model is +0.1485; across the set it runs from -0.0724 to +0.2320, with a median of +0.1469, and the reported analysis sits thirteenth of thirty-two.
grounds: analysis/05_stability/results/distribution.json · analysis/05_stability/results/distribution_rows.csv
node: analysis/05_stability
scope: the development backtest, 1998-01 to 2009-12, eight splits; the holdout half of this set is frozen and not yet run
alternatives: reporting the main path alone with a robustness footnote, which would have hidden that twelve reasonable analyses conclude a better score and nineteen a worse one
by: agent-autonomous

## C2
Our model beats the reference model on 27 of the 32 analyses and both required baselines on 27, and the failures are structured rather than scattered. The five analyses where the reference wins are exactly the five that replace our model or refit its weights; the five where a required baseline wins are exactly the five that weight the headline mean by cases.
grounds: analysis/05_stability/results/distribution.json · analysis/05_stability/results/distribution_rows.csv
node: analysis/05_stability
scope: development; no choice about the data, the evaluation, the scoring or the baselines takes our model below the reference on any row
by: agent-autonomous

## C3
The choice of model family is what the conclusion is sensitive to, and the choices made inside a family are not. Swapping the reported linear opinion pool for candidate 1 costs 0.2209 of skill and for candidate 2 0.0884, while the eleven forks inside those two families move it by at most 0.0081 and span 18.638 to 18.933 mean CRPS -- a range of 0.295 against the reference model's own 0.565 re-run spread.
grounds: analysis/05_stability/results/sensitivity_by_fork.csv · analysis/05_stability/results/fig_fork_sensitivity.csv
node: analysis/05_stability
scope: development; the exception is the pool's own weighting fork, which is not inside a member and is worth 0.1820
alternatives: phase C selected among those eleven forks over three batches, on differences this evaluation cannot resolve
by: agent-autonomous

## C4
Six of the tree's seventeen judgment calls move the reported conclusion further than the reference model moves on its own, and eleven do not. The yardstick is measured rather than chosen: the reference is unseeded and was scored four times, and our model's skill score against those four repeats spans 0.0218. Above that band sit the model family (0.2209), the pool's weighting (0.1820), the weighting of the headline mean (0.0835), the province filter (0.0376), the persistence construction (0.0279) and the training window (0.0219, which is the band itself).
grounds: analysis/05_stability/results/sensitivity_by_fork.csv · analysis/05_stability/results/distribution.json
node: analysis/05_stability
scope: development; a fork whose largest move is inside the band has not been shown to move the conclusion, which is weaker than showing that it does not
alternatives: a fixed threshold for what counts as a move, rejected because it would be a silent judgment call inside the node whose job is to make judgment calls visible
by: agent-autonomous

## C5
The cheapest analysis in the perturbation manifest is the one the conclusion is most sensitive to among the choices that leave our model alone. Re-weighting the headline mean re-runs no model at all -- thirteen seconds against twenty minutes -- and moves the reported skill by 0.0835, four times as far as any of the five setup forks that re-run every model on the leaderboard.
grounds: analysis/05_stability/results/sensitivity_by_fork.csv · analysis/05_stability/results/manifest.csv
node: analysis/05_stability
scope: development; the mean is over sixteen provinces whose burdens differ by four orders of magnitude, which is why the weighting has this much leverage
by: agent-autonomous

## C6
Under case weighting a required baseline beats the model this project reports, and it does so in every combination where case weighting appears -- five of the thirty-two analyses, all five case-weighted. The pool is too wide on the quiet months and too narrow on the outbreak months, which no single weighting of the mean shows on its own.
grounds: analysis/05_stability/results/distribution.json · analysis/05_stability/results/distribution_rows.csv
node: analysis/05_stability
scope: development; the persistence baseline is the winner in those five rows, and it is the construction batch 6 rejected in one of them
by: agent-autonomous

## C7
Fork effects do not compose, so a one-at-a-time stability report cannot be added up. Across the eight pairs the interaction runs from -0.1033 to +0.0424, and the extreme is larger than either main effect behind it: dropping the two provinces with no evaluable cell is worth +0.0376 alone and weighting the mean by cases +0.0835 alone, and together they come to +0.0177 against an additive +0.1211, because both work by re-weighting what the mean is over.
grounds: analysis/05_stability/results/fig_pair_interaction.csv · analysis/05_stability/results/conclusions.csv
node: analysis/05_stability
scope: development; eight pairs selected by a rule fixed and hashed before tier 1 ran, not chosen after seeing tier 1
alternatives: cutting tier 2 for budget, which was the manifest's first cut and was not taken; on this evidence it would have removed the finding
by: agent-autonomous

## C8
Calibration moves much further across the perturbation set than the score does. Interval coverage at 10-90 runs from 0.458 to 0.920 against a nominal 0.80 while the skill score stays positive on 27 of the 32 analyses, and both extremes involve a re-weighted mean. The rule that a badly calibrated CRPS winner has not won therefore bites hardest exactly where the CRPS looks best.
grounds: analysis/05_stability/results/distribution.json · analysis/05_stability/results/distribution_rows.csv
node: analysis/05_stability
scope: development; coverage is averaged over provinces, which cannot see an interval far too wide in one and far too narrow in another
by: agent-autonomous

## C9
The reported analysis stands on the worse of two published constructions of a baseline the plan requires, and the model it reports is better off for that. Wrapping the persistence point in a fitted negative binomial scores 20.698 mean CRPS against the main path's 24.879 and beats the reference model at 22.098; with that sharper member in the pool, the pool's margin over its own best member falls from 1.954 to 1.264 CRPS. It was not promoted, because phase C was closed and the manifest frozen before the row ran.
grounds: analysis/05_stability/results/conclusions.csv · analysis/05_stability/results/sensitivity_by_fork.csv
node: analysis/05_stability
scope: development; the fork moves the reported conclusion by -0.0279 of skill, the largest downward move of any single row
alternatives: promoting the sharper construction onto the main path, which the freeze forbids and which would have made the reported pool weaker relative to its members
by: agent-autonomous

## C10
Compute was not the constraint on the stability work and was not close to it. The whole development manifest -- twenty-four one-at-a-time analyses and eight pairs -- ran in 3.66 hours against a 12-hour budget, nothing was cut, and most of the time was the reference model's four unseeded repeats running through an amd64 image under emulation for the one model the plan forbids perturbing. What bound the work was implementation effort: nine of the twenty-four alternatives were sentences in a claim file rather than paths in the tree when the manifest was planned.
grounds: analysis/05_stability/results/cost_planned_vs_actual.json · analysis/05_stability/results/run_status.csv · analysis/05_stability/results/manifest_notes.json
node: analysis/05_stability
scope: the machine this project runs on, Darwin arm64, with the reference under emulation
by: agent-autonomous

## C11
A cost model that predicts the total to within a per cent can be uninformative about every individual row. Over the whole manifest the planned total is 7469 seconds against an actual 7469, a ratio of 1.00, while per-row ratios run from 0.52 to 1.91 -- because the model summed each row's parts as measured under the main path and could not know that a row changes how much work a part does. The manifest's cut order is ranked on those estimates, so it carries no information; nothing was cut, so nothing rests on it.
grounds: analysis/05_stability/results/cost_planned_vs_actual.json · analysis/05_stability/results/cost_planned_vs_actual.csv
node: analysis/05_stability
scope: the twenty-three rows the frozen manifest costed; the comparison reads the manifest through git at the commit that froze it
by: agent-autonomous

## C12
The set of analyses to be run on the held-out year is fixed before the year is opened: thirty-three rows, each the development row under a holdout name, with the development conclusion it is to be reported beside carried row by row. Freezing the set but assembling the development half of the comparison afterwards would leave the comparison selectable after the fact even though neither half was.
grounds: analysis/05_stability/results/manifest_holdout.csv · analysis/05_stability/results/holdout_freeze.json
node: analysis/05_stability
scope: the plan's non-negotiable 3 requires the freeze; what is in it is the agent's
alternatives: freezing only tier 1 and running the pairs on the holdout if budget allowed, rejected because development has already shown the forks do not compose
by: agent-on-human-assessment
