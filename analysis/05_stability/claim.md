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
