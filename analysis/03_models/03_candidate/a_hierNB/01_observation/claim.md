# Claim

What observation model do the counts get? Monthly province counts on this dataset are heavily over-dispersed and about a third of them are zero, and whether that is one distribution stretched wide or a mixture of two processes is a modelling choice rather than something the data settles.

## Children

kind: alternatives
main-path: c_hurdle

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

**The zeros and the large counts are two processes, and modelling them as one was the
candidate's largest single defect.** The hurdle -- a logistic model for whether a month
reports at all and a count model for how much it reports given that it does -- took the
candidate from **26.100** to **23.985** mean CRPS around the batch-8 configuration, past
both required baselines, and it is the main path from batch 9
(`AI-generated/candidate-forks/round1_batch8Defaults/fork_leaderboard.csv`).

**A mixture is not the same answer and is a much weaker one.** `b_zeroInflated` fitted a
mixing weight of **0.035** and scored **24.129** from the promoted main path, worse than
doing nothing. The negative binomial's variance function was already absorbing almost all
of the zeros; what it could not absorb was that the reporting months and the silent months
have different mean functions, which is what the hurdle gives them and the mixture does not.

**How much the hurdle is worth depends where you measure it from**: 2.115 CRPS around the
batch-8 configuration, **0.601** around the promoted one
(`round2_promoted/fork_interaction.csv`).
