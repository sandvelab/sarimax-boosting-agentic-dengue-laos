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
scope: the development backtest, 1998-01 to 2009-12, eight splits; the holdout half of this set ran in batch 16 and is C15
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

## C13
The held-out year was opened once, and the set of analyses evaluated on it was fixed before it was opened. Thirty-two rows -- every row of the development set that has a conclusion -- ran on 2010 through the same scripts their development twins ran, none failed, and each row's development conclusion was frozen into the manifest beside it so the pairing could not be assembled after the seal came off.
grounds: analysis/05_stability/results/manifest_holdout.csv · analysis/05_stability/results/holdout_freeze.json · analysis/05_stability/results/run_status_holdout.csv · analysis/01_data/01_partition/results/phase_e_opening.json
node: analysis/05_stability
scope: the manifest was committed at 937fd5c and the first file under analysis/results/*__holdout/ appears at 895a9f8, which is the evidence that the set predates the opening
alternatives: freezing which analyses run and assembling the development half of the comparison afterwards, which would have left the comparison selectable even though neither half was
by: agent-autonomous

## C14
The reported model beats the reference model and both required baselines on the held-out year as well as on the development period, at a skill score of +0.0868 against +0.1485. The gap between the two is -0.0617, and it is a gap in a ratio rather than in a raw score: 2010 was a much harder year, and the reference model, which nobody here tuned, scores 84.026 mean CRPS on it against 22.098 on development.
grounds: analysis/results/main__holdout/conclusion.json · analysis/results/main/conclusion.json · analysis/05_stability/results/holdout_vs_development.json
node: analysis
scope: four splits over 2010-01 to 2010-12, 192 cells in 16 provinces, against eight splits and 371 cells on development; the two raw CRPS figures are not comparable and the skill scores are
alternatives: reporting the raw CRPS gap, which would have confounded a model that flattered itself on development with 2010 simply being harder
by: agent-autonomous

## C15
The distribution of conclusions over the frozen set is more than twice as wide on the held-out year as on the development period: -0.5038 to +0.2026 against -0.0724 to +0.2320. Six of the thirty-two analyses fall below zero on 2010, where none did on development, and the reported analysis moves from thirteenth of thirty-two to eighteenth.
grounds: analysis/05_stability/results/holdout_distribution.json · analysis/05_stability/results/distribution.json · analysis/05_stability/results/holdout_vs_development.json
node: analysis/05_stability
scope: the same thirty-two analyses on both datasets; each dataset's noise band is measured on that dataset, 0.0218 on development and 0.0140 on the holdout
by: agent-autonomous

## C16
Twenty-eight of the thirty-two analyses scored worse on the year they had not seen, with a median drop of 0.056 in skill. The four that scored better were all analyses that had been below the reference model on development.
grounds: analysis/05_stability/results/holdout_vs_development.csv · analysis/05_stability/results/holdout_vs_development.json · analysis/05_stability/results/fig_holdout_vs_development.csv
node: analysis/05_stability
scope: skill scores, so each is already relative to a reference model that faced the same year
by: agent-autonomous

## C17
Ranking these analyses on the development set is a weak guide to how they rank on a year they have not seen. The Spearman rank correlation between the development and holdout skill scores across the thirty-two is +0.396. The ranking of the judgment calls transfers better, at +0.679, with fourteen of seventeen forks agreeing on whether they move the conclusion beyond their own dataset's noise band.
grounds: analysis/05_stability/results/holdout_vs_development.json · analysis/05_stability/results/fork_sensitivity_both.csv
node: analysis/05_stability
scope: thirty-two analyses and seventeen forks; the three forks that disagree are the pool's weighting and the persistence construction, which matter on development only, and the hierarchical model's covariate set, which matters on 2010 only
by: agent-autonomous

## C18
The analysis the development set ranked highest among those that change the data or the models is twenty-ninth of thirty-two on the held-out year, and the fork behind it moved the reference model rather than ours. Removing the two provinces that contribute no evaluable cell before the platform sees them takes the reported skill from +0.1485 to +0.1861 on development and to -0.1828 on 2010; across that change our pool moves from 76.73 to 76.56 mean CRPS, inside the noise, while the reference model moves from 84.03 to 64.72.
grounds: analysis/results/provinces_reportingOnly__holdout/conclusion.json · analysis/results/provinces_reportingOnly/conclusion.json · analysis/results/main__holdout/conclusion.json · analysis/05_stability/results/holdout_vs_development.csv
node: analysis/02_setup/03_provinces
scope: the same sixteen provinces and 192 cells are scored either way; what the fork changes is what every model is fitted on, not what the metric averages over. The row ranks fourth of thirty-two on development and twenty-ninth on the holdout; the three development rows above it all re-weight the headline mean, and its own case-weighted pair is the worst of all thirty-two on 2010
alternatives: reading the row as evidence that our model is sensitive to the province filter, which the per-model CRPS shows it is not
by: agent-autonomous

## C19
The province filter is the largest single judgment call in the project on the held-out year, at 0.2696 of skill, having been fourth at 0.0376 on development. Over the same change the model family halves, from 0.2209 to 0.0949, and the pool's own weighting fork collapses from 0.1820 to 0.0121 and falls below the noise band.
grounds: analysis/05_stability/results/fork_sensitivity_both.csv · analysis/05_stability/results/holdout_sensitivity_by_fork.csv · analysis/05_stability/results/fig_fork_sensitivity_both.csv
node: analysis/05_stability
scope: each dataset's band measured on that dataset; five forks clear the holdout's band against six on development
by: agent-autonomous

## C20
The reported model's over-dispersion on development does not survive the change of year. Its 10-90 interval coverage is 0.863 against a nominal 0.80 on the development backtest, the widest in the project, and 0.755 on the held-out year; across the frozen set coverage runs 0.458 to 0.920 on development and 0.210 to 0.854 on 2010.
grounds: analysis/05_stability/results/holdout_distribution.json · analysis/05_stability/results/distribution.json · analysis/results/main__holdout/conclusion.json
node: analysis/05_stability
scope: 10-90 nominal 0.80; calibration is reported beside the score because a badly calibrated CRPS winner has not won
by: agent-autonomous

## C21
The forks do not compose on the held-out year either. Across the eight frozen pairs the largest interaction is -0.2876, on the same row that carries the largest single move, and it is larger than either main effect behind it.
grounds: analysis/05_stability/results/holdout_distribution.json · analysis/05_stability/results/holdout_conclusions.csv
node: analysis/05_stability
scope: eight pairs selected by a rule fixed and hashed before tier 1 ran; the development set's largest interaction was -0.1033
by: agent-autonomous

## C22
On the development backtest the model this project reports beats the reference model and both required baselines: mean CRPS 18.817 against the reference's 22.098, a skill score of +0.1485, and the lower CRPS in six of the eight splits. The model is a linear opinion pool over two candidate families and the two required baselines.
grounds: analysis/results/main/conclusion.json · analysis/04_score/03_compare/results/main/leaderboard.csv
node: analysis
scope: 371 evaluated cells in 16 provinces over eight splits, 2008-01 to 2009-12, from a training set ending 2007-12; the same model on the held-out year is C14
alternatives: the eleven configuration forks inside the two member families move this score by at most 0.0081 of skill (C3), so it is not sensitive to how the members were configured
by: agent-autonomous

## C23
The margin is not large enough to separate the two models. The paired difference is 3.282 CRPS per cell against a split-clustered standard error of 1.726, and our model has the lower mean while winning only 43.1 % of the individual cells. This is the largest margin the project produced against the reference, and a comparison at this resolution still cannot say the two models differ.
grounds: analysis/04_score/03_compare/results/main/comparison_notes.json · analysis/04_score/03_compare/results/main/paired_summary.csv
node: analysis/04_score/03_compare
scope: development; the standard error is clustered at the split, which is the level the eight numbers are exchangeable at
alternatives: the naive per-cell standard error is 0.948 and would have made the margin look nearly twice as decisive; it assumes 371 independent cells, which a panel of 16 provinces over eight quarters is not
by: agent-autonomous

## C24
The reference model cannot be seeded, and its own re-run spread is the floor on what this backtest can attribute to a model at all. Four repeats score 21.820, 21.917, 22.272 and 22.385 mean CRPS, and the largest paired difference between two of them is 0.565 CRPS. Anything smaller than that belongs to the reference's sampler rather than to any model.
grounds: analysis/04_score/03_compare/results/main/reference_repeat_noise.csv · analysis/03_models/02_reference/results/main/model_spec.json · analysis/04_score/03_compare/results/main/comparison_notes.json
node: analysis/03_models/02_reference
scope: development; the reported reference figure is the per-cell mean of the four repeats, so no reported ratio divides by a single draw
alternatives: running the reference once, which is what batch 4's reconnaissance figure of 21.9 was, and which would have put an unmeasured share of the sampler's noise into every number reported against it
by: agent-autonomous

## C25
Pooling beats every model that goes into it. The pool scores 18.817 mean CRPS against its best member's 20.771 and the mean of its members' 23.421, with half its weight on the two required baselines, which are the two worst-scoring models in the comparison. The premise registered before the run -- that a pool would land between the best member and the members' mean -- is wrong: it beat the best member by 1.954 CRPS. The half of that premise about spread holds, and the pool over-covers because of it.
grounds: analysis/03_models/03_candidate/c_ensemble/results/main/pool_check.json · analysis/results/main/conclusion.json
node: analysis/03_models/03_candidate/c_ensemble
scope: development, equal weights over four members
alternatives: a pool over the two candidate families only, which was not built; what the manifest perturbs instead is the weighting (C26) and each member's own configuration
by: agent-autonomous

## C26
Fitting the pool's weights costs far more than it buys. Weights chosen by minimising the pool's CRPS on a validation period held back inside the training frame score 22.838 mean CRPS against equal weights' 18.817 -- 4.021 CRPS worse, and enough to lose to the reference model that equal weighting beats.
grounds: analysis/results/weighting_crpsWeighted/conclusion.json · analysis/results/main/conclusion.json
node: analysis/03_models/03_candidate/c_ensemble/01_weighting
scope: development; the same fork is worth 0.1820 of skill there and collapses to 0.0121 on the held-out year, below that year's noise band (C19)
alternatives: equal weighting, which is the main path and the reported model
by: agent-autonomous

## C27
The model family the project built first never beat the reference model. The hierarchical negative-binomial GLM scores 23.698 mean CRPS against 22.098, a skill score of -0.0724, and it is the lowest of the thirty-two analyses in the development distribution. It does beat both required baselines, and it stays in the reported model as a pool member.
grounds: analysis/results/family_hierNB/conclusion.json · analysis/05_stability/results/distribution_rows.csv
node: analysis/03_models/03_candidate/a_hierNB
scope: development, at the configuration batch 9 promoted after sweeping its six forks over two rounds
alternatives: dropping the family once candidate 2 beat it, which would have removed a member the pool is measurably better with (C25)
by: agent-autonomous

## C28
The second family beat the reference model on its own, before any pooling. Gradient-boosted trees with a probabilistic head score 20.771 mean CRPS against 22.098, a skill score of +0.0601, at 10-90 interval coverage of 0.825 against a nominal 0.80 -- the closest to nominal of any single model of ours.
grounds: analysis/results/family_boosted/conclusion.json · analysis/04_score/03_compare/results/main/leaderboard.csv
node: analysis/03_models/03_candidate/b_boosted
scope: development; neither of its two forks moves it beyond the noise band (C3, C4)
by: agent-autonomous

## C29
The reported model is cheaper to run than the model it beats. One eight-split evaluation of the pool takes 59.5 seconds natively; one repeat of the reference takes between 241 and 285 seconds through an amd64 image under emulation, and the reported reference figure needs four of them, at 1 070 seconds.
grounds: analysis/03_models/03_candidate/c_ensemble/results/main/run_cost.json · analysis/03_models/02_reference/results/main/run_cost.json
node: analysis/03_models
scope: this machine, Darwin arm64; the emulation penalty is a property of the host, not of the reference model, and the repeats are needed because it is unseeded (C24)
by: agent-autonomous

## C30
On this dataset the 25-75 coverage figures are not a clean reading of calibration and the 10-90 figures are. 56 % of observed province-months are exactly zero, and at 24 % to 55 % of evaluated cells a member's 25-75 quantiles coincide, so its interval is the single point zero and every zero outcome falls inside it whatever the model believes. At 10-90 that share is under 27 % for the members and 0.3 % for the pool.
grounds: analysis/03_models/03_candidate/c_ensemble/results/main/pool_check.json · analysis/01_data/02_characterise/results/dev_overview.json
node: analysis/03_models/03_candidate/c_ensemble
scope: development; every coverage figure this project reports beside a score is the 10-90 one
by: agent-autonomous

## C31
Both required baselines lose to the reference model, so beating the baselines is not the bar that binds. Persistence scores 24.879 and seasonal climatology 24.337 against the reference's 22.098, skill scores of -0.126 and -0.101. The reference is the harder bar by about 2.5 CRPS, and it is the one every reported ratio is taken against.
grounds: analysis/04_score/03_compare/results/main/leaderboard.csv · analysis/results/main/conclusion.json
node: analysis/04_score/03_compare
scope: development, at the baselines' main-path constructions; the alternative persistence construction does beat the reference (C9)
by: agent-autonomous

## C32
The headline mean is over 16 provinces and 371 cells, not the 18 provinces the file contains. Chap's own region filter rejects Vientiane province, which reports nothing anywhere in the record, and keeps Xaisomboun, which stops reporting after 2005 and contributes no evaluable cell to the evaluated span; Phongsaly contributes 11 cells of a possible 24. Of the 408 province-months in the span, 371 are scored.
grounds: analysis/01_data/02_characterise/results/backtest_scheme_chosen.json · analysis/01_data/02_characterise/results/evaluable_cells_by_province.csv
node: analysis/01_data/02_characterise
scope: development; the held-out year is 192 cells in the same 16 provinces over four splits
alternatives: removing the silent provinces before the platform sees them, or folding Vientiane into the capital; both are alternatives nodes rather than a silent cleaning step, and the first turns out to be the largest judgment call in the project on the held-out year (C18, C19)
by: agent-autonomous

## C33
Three statements in the dataset's own schema do not describe the file it ships with. The schema states 2 575 rows where the file carries 2 808 -- the stated figure is the count of rows whose target is not null. It declares rainfall as a monthly total in millimetres, which would put a province's whole year at a few tens of millimetres; read as a mean daily rate the same column puts the year in the thousands, a factor of 30.4 apart, and the second reading is the one the file supports. And the population column, declared against a 2020 reference, sums to 4.96 million where the national total that year was 7.35 million, matching the country around 1995.
grounds: analysis/01_data/01_partition/results/rowcount_reconciliation.json · analysis/01_data/02_characterise/results/covariate_units_check.json · analysis/02_setup/01_population/b_backCast/results/popColumn_backCast/setup_spec.json
node: analysis/01_data
scope: nothing downstream turns on the rainfall reading, because every model sees a monotone transform of the same column; anything importing an external rainfall threshold would be wrong by about thirty
alternatives: taking the schema at its word, which is what a pipeline reading the metadata rather than the data would do
by: agent-autonomous

## C34
The target is mostly zeros, and the record gets less complete as it goes on. Of the 2 383 observed province-months in the development period 56.3 % are exactly zero and a further 8.1 % of the grid is missing; reporting completeness holds at 94.4 % through 2005 and falls to 83.3 % by 2008, so the evaluated span is the least complete part of the record.
grounds: analysis/01_data/02_characterise/results/dev_overview.json · analysis/01_data/02_characterise/results/cases_by_year.csv · analysis/01_data/02_characterise/results/zero_structure.csv
node: analysis/01_data/02_characterise
scope: the development period, 1998-01 to 2009-12; the holdout was not characterised
by: agent-autonomous

## C35
The development file and the sealed holdout partition the archived source exactly, and this was verified rather than assumed: 2 592 and 216 lines against the source's 2 808, no line in both, and the sorted union byte-identical to the source under sha256. The check runs again on every run of the analysis, against the archive's own checksum manifest.
grounds: analysis/01_data/01_partition/results/partition_check.json · analysis/01_data/01_partition/results/partition_outputs.sha256
node: analysis/01_data/01_partition
scope: this is what made batch 16's reassembly of the full file legitimate rather than a second import of the data (C13)
by: agent-autonomous

## C36
The evaluation scheme was fixed before any model ran and never moved: three-month horizons, eight splits, stride three, retrained once, evaluating 2008-01 to 2009-12 from a training set ending 2007-12. The schedule was read out of chap-core's own splitter rather than reimplemented, and the phase-E arrangement -- same horizon and stride, four splits -- evaluates exactly 2010 from training that never reaches into it.
grounds: analysis/01_data/02_characterise/results/split_schedule.csv · analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
node: analysis/01_data/02_characterise
scope: fixed in batch 3; a horizon changed midway would make every earlier number incomparable
alternatives: the schemes considered and rejected are kept, with their span and split counts, in backtest_scheme_candidates.csv beside the chosen one
by: agent-autonomous

## C37
Every model this project wrote reproduces byte-identically when it is run again -- per-cell scores, model listing and fitted object, for all seven of them. The reference model cannot be made to do this: it calls its sampler without ever setting a seed and the service exposes no seed, so its variability is quantified by repetition instead of removed.
grounds: AI-generated/determinism-checks/model_determinism.json · analysis/03_models/02_reference/results/main/model_spec.json
node: analysis/03_models
scope: the evaluation NetCDF is excluded from the comparison because chap-core stamps a creation date into it; everything computed from it is compared
alternatives: making the check a node inside the tree, so that every run re-verified determinism; rejected because it would double the cost of every model run to re-establish something that changes only when a model changes
by: agent-autonomous

## C38
The pool holds no model code of its own, and that is checkable rather than asserted. Each member runs through its own Chap entry points, read out of that member's own contract directory with every file's hash recorded; and the pool rebuilt independently from its members' stored evaluations scores 18.801 against the 18.817 it scored as run, a difference of 0.016 CRPS, which is the sampling error of which draws each member contributed.
grounds: analysis/03_models/03_candidate/c_ensemble/results/main/pool_check.json · analysis/03_models/03_candidate/c_ensemble/results/main/members.json
node: analysis/03_models/03_candidate/c_ensemble
scope: development, main path; the reconstruction is computed from the members' own stored forecasts and is independent of the ensemble's
by: agent-autonomous

## C39
The cost model was tested as a prediction for the first time on the held-out half and it held at the total: 8 602 seconds actual against 7 468 planned, a ratio of 1.15 over 32 rows, where the development half's 1.00 was measured over runs that had already happened. The worst row is again the one that changes how much work a part does -- refitting at every split, at 1.97 -- so the total being right a second time does not make any individual estimate right, and the cut order those estimates rank still carries no information.
grounds: analysis/05_stability/results/holdout_cost_planned_vs_actual.json · analysis/05_stability/results/cost_planned_vs_actual.json
node: analysis/05_stability
scope: the 32 phase-E rows, costed by the same model against the same parts and read out of the manifest at the commit that froze it, 937fd5c, before the year was opened
alternatives: re-costing the phase-E half after seeing the development half's per-row errors, which the freeze forbids and which would have made the comparison a fit rather than a prediction
by: agent-autonomous
