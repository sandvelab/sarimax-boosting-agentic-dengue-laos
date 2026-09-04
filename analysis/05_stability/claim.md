# Claim

How far does the project's conclusion survive the reasonable alternatives the main path did not take? The node enumerates every judgment call the tree carries as a fork, costs the analyses that take them instead, and runs that set so the reported result is a distribution over analyses that all looked defensible rather than the one that was run.

## Children

kind: -
main-path: -

## Environment

inherits: the project main environment (`environment/`)

## Answers

_(What this node's analysis yielded. Each answer belongs in the claim collection
under `Human-AI-collaboration/claims/` with a pointer to the result grounding it.)_

The tree carries **17 forks**, not the ten batch 5 counted by hand: phase C added five while
building the candidates, and two baseline forks were never on the hand-written list although
the plan's phase D names one of them. `results/forks.csv` is read from the tree, so the next
fork anyone adds is in the manifest without anyone remembering to add it — and
`/validate invariants` fails if it is not.

The manifest is **24 tier-1 combinations**, one per path not taken, plus **8 tier-2 pairs**
selected by a rule fixed and hashed before tier 1 ran, plus one combination that already
exists and perturbs nothing. Tier 1 costs **124 minutes on development and 75 on the
holdout**, against a 12-hour budget, so **nothing is cut** and the cut order is recorded
against the day something is (`results/manifest_notes.json`).

**Compute is not what binds, and it is not close.** Of the 124 development minutes, **89 are
the reference model** — five setup rows at four unseeded repeats each, through an amd64
image under emulation, for a model the plan forbids perturbing. Every model of ours, on
every combination in tier 1, costs 21 minutes together.

What binds is that **nine of the 24 rows have no scripts**: the tree named those children in
prose and did not carry them until this batch created them. And twelve of the fifteen that
do have scripts hold results produced around a main path that has since moved, so their
directories describe a different analysis from the one their manifest row now names.

**Batch 13 ran the seven setup and scoring rows.** `results/conclusions.csv` now has **8 of
33**, and the shape of the answer is already visible.

**The five `02_setup` forks do not move the conclusion.** Skill spans **+0.1266 to +0.1861**
around the main path's +0.1485, and every one of those gaps is smaller than the reference's
own 0.57 CRPS re-run spread. Three of the five move the score by moving *the reference*
rather than our model: dropping two unevaluable provinces costs the reference 1.05 CRPS and
our pool 0.03.

**The one scoring fork moves it four times as much as any of them.** Population weighting
gives +0.2288 and case weighting +0.2320, both about +0.08 of skill from the main path, from
re-weighting a stored file and re-running nothing. The cheapest fork in the manifest —
thirteen seconds against twenty minutes — is the one the conclusion is most sensitive to.

**The main path sits near the bottom of the range.** Six of the seven perturbations improve
the reported skill score. That is what a conservative main path looks like, and it is also
what a systematically flattering set of alternatives would look like; eight rows cannot tell
those apart, and the remaining sixteen tier-1 rows are what would.

**Under case weighting, persistence beats the reported model** (86.598 against 88.484) and
the pool's 10-90 coverage falls from 0.863 to 0.701. The pool is too wide on the quiet months
and too narrow on the outbreak months, which no single weighting shows on its own. This is
the most useful thing tier 1 has produced so far and it is not a skill score.

Sixteen tier-1 rows remain: two baseline children batch 22 builds, and fourteen candidate and
family rows batch 14 runs. Tier 2 stays unselected until every tier-1 row has been attempted —
`plan_manifest.py` now refuses to apply `tier2_rule.md` before then, which is a change to when
the rule is applied and not to the rule, whose sha256 is unchanged.

**Batch 22 ran the two baseline rows, and they are the widest pair in the set.**
`results/conclusions.csv` now has **10 of 33**.

**The persistence fork is the largest single-row move of the reported conclusion so far**, and
it is downward: skill **+0.1206** against the main path's +0.1485, from the pool's mean CRPS
rising to 19.434. **The climatology fork is the smallest move of any row**: +0.1460, 0.0025
of skill. Two forks of the same kind, on the two baselines the plan requires, an order of
magnitude apart in what they are worth.

**The main path is no longer at the bottom of the range.** After batch 13, six of seven
perturbations improved the reported skill and the honest reading was that a conservative main
path and a flattering set of alternatives look the same from there. Both new rows are below
the main path, which is the first evidence for conservatism rather than flattery — two rows,
which is not much, and the fourteen candidate rows are still the ones that would settle it.

**The most useful thing in the pair is not a skill score.** The alternative construction of
the persistence baseline scores 20.698 against the main path's 24.879 and beats the reference
model at 22.098. The reported analysis is built on the worse of two published constructions
of a model the plan's §4 requires, and the pool that contains it is *better off* for that,
because a linear opinion pool profits from its members disagreeing.

Fourteen tier-1 rows remain, all of them batch 14's, and tier 2 stays unselected until they
have been attempted.

**Batch 14 ran the twelve candidate rows, the two family rows and all eight tier-2 pairs.**
`results/conclusions.csv` now has **32 of 33** — the thirty-third is `family_ensemble`, the
main path's own choice under its own name, which perturbs nothing.

**The choice of model family moves the conclusion twenty-seven times further than any choice
inside a family.** Swapping the reported pool for candidate 1 costs **0.2209** of skill, for
candidate 2 **0.0884**. The eight forks inside those two families span **18.638 to 18.933
CRPS** over the eleven combinations they perturb — a range of 0.295, about half the reference's own 0.57 re-run spread — so nothing in
that block can be attributed to a model at all. The mechanism is the pool. Phase C's own sweeps
record candidate 1's observation model as a 0.601 CRPS swing to candidate 1 alone; the same
fork is a 0.102 swing to the pool, because three of its four members did not move. And
candidate 2's quantile head makes candidate 2 worse on its own while making the pool better,
so the damping is not simple scaling — the same fact batch 22 found when a sharper
persistence member made a worse pool.

**The exception is the one candidate-internal fork that is not inside a member.** Fitting the
pool's weights by minimising its CRPS on a year held back inside the training frame is worth
**0.1820** of skill and takes the reported model to 22.838 CRPS, *behind* the reference, with
its paired comparison falling to 0.48 standard errors. It is the second-largest single-fork
move in the set.

**The pairs are not the sum of their parts.** `conclusions.csv` now carries
`delta_skill_additive` and `interaction` for every tier-2 row. Across the eight the
interaction runs from **−0.1033 to +0.0424**, and the extreme is larger than either main
effect behind it: removing the two provinces with no evaluable cell is worth +0.0376 alone,
weighting the headline mean by cases +0.0835 alone, and together they come to **+0.0177**
against an additive +0.1211. Both work by re-weighting what the mean is over, so taking both
does not do it twice. This is the third demonstration that fork effects do not compose —
batches 9 and 21 were the first two — and the first on the reported conclusion. It is why
tier 2 was not cut.

**Case weighting is the one condition under which a required baseline beats the reported
model**, and it does so in every combination it appears in: five rows of the 32, all five
case-weighted. The five rows where our model does not beat the reference are the five that
replace it or refit its weights. No choice about the data, the evaluation, the scoring or the
baselines takes our model below the reference on any row.

**Calibration moves far more than the score does.** 10–90 coverage runs from **0.458 to
0.920** against a nominal 0.80 while the skill score stays positive on 27 of 32 rows. Both
extremes involve a re-weighted mean: the pool under population weighting is badly
over-dispersed and candidate 1 under case weighting badly under-dispersed. §2's rule that a
badly calibrated CRPS winner has not won bites hardest exactly where the CRPS looks best.

The development set is complete. Batch 15 turns it into the reported distribution, puts the
driver into `analysis/run.sh` now that every row can run, and freezes the holdout manifest.

**Batch 15 reported the distribution, and the answer has two halves.**

**The conclusion survives, and the reported number is not the middle of the range it
survives across.** Skill runs **−0.0724 to +0.2320** around the reported +0.1485, which sits
**thirteenth of thirty-two**; our model beats the reference on 27 and both required
baselines on 27; 10–90 coverage runs 0.458 to 0.920 against a nominal 0.80. The failures are
structured rather than scattered: the five rows the reference wins are the five that replace
our model or refit its weights, and the five a required baseline wins are the five that
weight the headline mean by cases. → `results/distribution.json`

**Six of the seventeen forks move the conclusion further than the reference model moves on
its own, and eleven do not.** The yardstick is measured, not chosen: the reference is
unseeded and was scored four times, and our model's skill against those four spans
**0.0218**. Above it: the model family (0.2209), the pool's weighting (0.1820), the
weighting of the headline mean (0.0835), the province filter (0.0376), the persistence
construction (0.0279), the training window (0.0219, which is the band itself to within
0.0001). Below it: everything else, including eight of the nine candidate-internal forks
phase C spent three batches selecting among — eight of the eleven below the line,
the other three being two `02_setup` forks and one baseline fork. → `results/sensitivity_by_fork.csv`

**The manifest was re-planned and did not move.** `manifest.csv` came back byte-identical
now that every row has been attempted and the frozen pair rule reads a complete tier 1 —
which is what made it safe to put the driver into `run.sh`. `analysis/run.sh` now reproduces
the stability result as well as the reported one, at about four hours rather than twenty
minutes, and the node's own script order is the phase's: cost, plan, run tier 1, collect,
re-plan so the frozen rule can pick tier 2 from a tier 1 that exists, run those, collect,
report.

**The whole set cost 3.66 h against a 12 h budget** (`results/run_status.csv`, summed) and
nothing was cut. The frozen cost model predicted the total to within one part in a thousand
— 7 469 s against 7 469 s — and individual rows by ratios from 0.51 to 1.91, so the cut
order it ranks would have carried no information had anything been cut.

**The phase-E set is frozen.** Thirty-three rows under `__holdout` names, an estimated
2.07 h, each carrying the development conclusion it is to be reported beside, so the pairing
is fixed with the set rather than assembled after the seal comes off.
→ `results/manifest_holdout.csv`, `results/holdout_freeze.json`

Phase D is complete.

## Phase E — the same set, on the year it had never seen

**The holdout was opened once and the frozen set ran on it.** Thirty-two of the thirty-three
rows — every one with a development twin — ran, none failed, in **2.39 h** against the 2.07 h
they were frozen at. The thirty-third is the main path under a second name and was not run on
development either. → `results/run_status_holdout.csv`, `results/holdout_conclusions.csv`

**The reported analysis scores +0.0868 on 2010 against +0.1485 on development**, a gap of
**−0.0617**. It still beats the reference model and both required baselines. **2010 was a much
harder year**: the reference, which nobody here tuned, scores 84.026 mean CRPS on it against
22.098 on development — which is why the conclusion is a ratio and why raw CRPS is not
compared across the two. → `results/holdout_vs_development.json`

**The spread more than doubles.** −0.5038 to +0.2026 on the holdout, a range of 0.706,
against −0.0724 to +0.2320 and 0.304 on development. Six analyses fall below zero where
development had none. The reported analysis sits **eighteenth of thirty-two** where it sat
thirteenth. → `results/holdout_distribution.json`

**Twenty-eight of the thirty-two analyses did worse on the year they had not seen**, median
gap −0.056. Four did better, and all four are analyses that were *below* the reference on
development. → `results/holdout_vs_development.csv`

**The ranking of the analyses barely transfers.** Spearman rank correlation between the two
skill scores across the 32 is **+0.396**. A development set used to choose between these
analyses would have been choosing on something only weakly related to what it was choosing
for.

**The ranking of the forks transfers better than the ranking of the analyses**: +0.679, and
**14 of 17 forks agree** on whether they move the conclusion beyond their own dataset's noise
band. But the order changes at the top. The **province filter goes from 0.0376 to 0.2696**,
the largest fork effect anywhere in this project; the **model family halves**, to 0.0949; the
**pool's own weighting collapses** from 0.1820 to 0.0121 and falls below the band. The
hierarchical model's covariate set, worth 0.0081 on development, clears it here.
→ `results/fork_sensitivity_both.csv`

**The fork that moved most moved the reference, not our model.** Under
`provinces_reportingOnly` — removing the two provinces that contribute no evaluable cell
before the platform sees them — our pool scores 76.56 against 76.73 on the main path, a
change inside the noise; the reference model goes from 84.03 to **64.72**. The row that was
**fourth** of the thirty-two on development at +0.1861 — and the best of the analyses that
do not re-weight the headline mean, the three above it all being weighting rows — and
**twenty-ninth** on the holdout at −0.1828. Its case-weighted pair is the **worst of all
thirty-two** at −0.5038. What development ranked highest among the analyses that change the
data or the models is a denominator that happened to be large.

**Calibration moved the other way from the score.** The reported model's 10–90 coverage was
0.863 against a nominal 0.80 on development — the most over-dispersed model in the project —
and is **0.755** on the holdout. Across the set it runs 0.210 to 0.854.

**The forks still do not compose.** Eight pairs, largest interaction **−0.2876**, on the same
row that carries the largest single move.

## Batch 24 — the frozen set stops being rebuilt

**The set is verified on every run and rewritten on none.** `freeze_holdout_manifest.py` is
the last step of the development half of this node's `run.sh`, so every run of
`analysis/run.sh` re-derived the frozen
phase-E manifest from the development manifest, which may legitimately grow. It returned the
same bytes because the tree had not changed, not because anything made it: with one fork
child added, thirty-three rows became **thirty-four**. The frozen file is now authoritative —
a development row with no twin is reported as unpaired and never added, a frozen row the tree
no longer carries or whose structure moved stops the run, and a development conclusion that
drifted under the unseeded reference is recorded rather than absorbed.
→ `results/holdout_freeze_check.json`

**Eleven situations were put to it and to the new `freeze` invariant, and all eleven behaved
as specified.** Deleting the frozen file with no trace of an opening and letting the script
freeze from cold returns the manifest **byte-identical** to the one frozen in batch 15, which
is what says the restructuring did not restructure the set. Against the superseded version,
six of the seven script scenarios fail and every one of them exits 0.
→ `AI-generated/validation/26-09-01_freezeDefence.json`

**And one answer that belongs to another node's claim but can only be settled here (batch
28).** The ensemble node rebuilds each pool from its members' **own** separate evaluations,
and a candidate family is evaluated separately only under the family fork's own combination —
a row of this manifest. So on a run from nothing every pool is checked before its members
exist, records truthfully that the reconstruction could not be done, and nothing revisits it:
the headline holdout row carried that record from batch 16 and it read as a statement that
the reconstruction was impossible. The last step of this node's `run.sh` now settles every
pool row once the whole set has run. **Eleven of the 51 rows reconstruct, at residuals of
0.016 to 0.136 CRPS against the pool that ran; forty cannot, and the reason is structural** —
they move a fork inside one of the members, and no run of this analysis produces that
member's separate evaluation under that configuration
(`results/pool_reconstruction.json`).
