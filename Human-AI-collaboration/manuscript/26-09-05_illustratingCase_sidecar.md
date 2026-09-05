# Provenance sidecar — `26-09-05_illustratingCase.md`

Rule 9's second step, made checkable: every statement in the write-up that asserts something
about the analysis, mapped to the claim it rests on. Claims are in
`../claims/claims.md`; each of them names the stored result grounding it, and that result
names the script, the commit and the environment that produced it. The chain from a sentence
to a command therefore runs sentence → claim → result → provenance record → commit.

A sidecar rather than inline annotations: it survives format conversion, it can be published
as supporting material, and it can be read as a table rather than hunted for in prose.

**How to read the `claims` column.** A row lists every claim the passage draws on. Where a
row lists none, the `basis` column says what kind of statement it is instead — the three
kinds are *design*, which describes how the project was set up and is grounded in the plan
and `AGENTS.md` rather than in a result; *record*, which describes the project's own history
and is grounded in the batch reports and validation records; and *judgment*, which is the
agent's opinion and is grounded in nothing but is labelled as such.

**Two statements in the write-up deliberately have no claim and say so in their own text**:
that three countries are not a sample, and that the development-arrangement gap is not
attributable to optimisation alone. Both are limits on what the claims support, and the
scope fields of C42 and C43 carry them.

---

## The case, and why this one

| passage | claims | basis |
|---|---|---|
| The problem, the dataset, the covariates and the calendar | — | design (plan §1, §4) |
| The evaluation is the platform's own; the metric is mean CRPS across regions and splits | C36 | |
| The reference model is EWARS-csd at its published default, pinned and never tuned | C24 | design (plan §4) |
| The data are public and redistributable | — | design (plan §4) |
| Seventeen judgment calls carried as forks; the spread is wider than the margin | C1, C4, C23 | |
| The final year was cut out of the data before any work began | C35 | design (plan §3) |

## What the analysis did

| passage | claims | basis |
|---|---|---|
| 2 592 and 216 lines against 2 808; the partition verified rather than asserted | C35 | |
| Three-month horizons, eight splits, stride three, refitted once, evaluating 2008-01 to 2009-12 | C36 | |
| The headline mean is over 16 provinces and 371 cells, not 18 | C32 | |
| 56.3 % of observed province-months are zero; the record gets less complete | C34 | |
| Three schema statements do not describe the file; two are the harmonisation's | C33, C46 | |
| Two required baselines, implemented as platform-compatible models | C31 | design (plan §4) |

## The result

| passage | claims | basis |
|---|---|---|
| 18.817 against 22.098, skill +0.1485, ahead of each repeat, six of eight splits | C22 | |
| 3.282 CRPS against a split-clustered SE of 1.726 — 1.90 standard errors | C23 | |
| Four repeats at 21.820, 21.917, 22.272, 22.385; nothing below ~0.57 CRPS | C24 | |
| The pool beats its best member (20.771) and its members' mean (23.421) | C25 | |
| Fitting the weights scores 22.838 — 4.021 CRPS worse | C26 | |
| The first family never beat the reference: 23.698 against 22.098 | C27 | |
| The second family beat it on its own: 20.771 | C28 | |
| 10–90 coverage 0.863 against nominal 0.80 | C20, C30 | |
| The 25–75 figures are not a clean reading of calibration here | C30 | |
| Both baselines lose to the reference: 24.879 and 24.337 | C31 | |

## The stability result

| passage | claims | basis |
|---|---|---|
| Thirty-two analyses fixed before any ran; −0.0724 to +0.2320; thirteenth of thirty-two | C1 | |
| 27 of 32 beat the reference and 27 both baselines; the failures are structured | C2 | |
| Family costs 0.2209; the eight internal forks move at most 0.0081 and span 18.638–18.933 | C3 | |
| Re-weighting the mean: thirteen seconds, 0.0835 of skill, four times any setup fork | C5 | |
| Under case weighting a required baseline wins, in every combination it appears in | C6 | |
| Interactions run −0.1033 to +0.0424; the largest exceeds either main effect | C7 | |
| Six of seventeen forks clear the band; the band is a draw at 0.0218/0.0431/0.0349/0.0483 | C4 | |
| Only family, pool weighting and headline-mean weighting clear it every time | C4 | |

## The held-out year

| passage | claims | basis |
|---|---|---|
| Thirty-two rows frozen with their development conclusions, before the year was opened | C12, C13 | |
| +0.0868; 76.731 against 84.026 over 192 cells; raw CRPS about four times development's | C14 | |
| The spread is more than twice as wide: −0.5038 to +0.2026 | C15 | |
| Twenty-eight of thirty-two scored worse, median 0.056 | C16 | |
| Rank correlation +0.396 for analyses, +0.679 for forks, 14 of 17 agreeing | C17 | |
| The 14-of-17 count is reported with its names beside it | C17 | record (`26-09-04_b31_cleanroomToCompletion.md`) |
| Fourth on development at +0.1861, twenty-ninth on 2010 at −0.1828; pair worst at −0.5038 | C18 | |
| The fork moves the reference: 84.03 → 64.72 while our pool goes 76.73 → 76.56 | C18 | |
| The province filter: 0.0376 → 0.2696; the pool's weighting 0.1820 → 0.0121 | C19 | |
| Coverage 0.863 → 0.755; across the set 0.458–0.920 and 0.210–0.854 | C8, C20 | |

## The external check

| passage | claims | basis |
|---|---|---|
| Thailand +0.0856 → +0.0197, Vietnam +0.0852 → −0.0862, Laos +0.1485 → +0.0868 | C42 | |
| All three drops exceed the two reference bands together | C42 | |
| Three countries are not a sample; no confidence statement is made | — | C42's scope field |
| 1.74 times either sibling's; the siblings agree to 0.0004 and sit 0.063 below Laos | C43 | |
| The gap is not attributable to development alone | — | C43's scope field |
| 0.032 / 0.565 / 7.082 CRPS — a factor of 219; Vietnam's margin inside its own floor | C44 | |
| Coverage 0.941 and 0.967 on the sibling development backtests | C45 | |

## What the evaluation can separate

| passage | claims | basis |
|---|---|---|
| The six standard-error figures, and the 1.03 line | C48, C23 | |
| Five of six on the wrong side of it | C48 | |
| The two yardsticks disagree on Vietnam's development row | C44, C48 | |
| No paired test against the baselines anywhere in the project | — | C48's scope field |

## The claim tree, worked · The perturbation families

| passage | claims | basis |
|---|---|---|
| The tree's shape, the two relationship types, and the node contents | — | design (`AGENTS.md` §2) |
| Every node's question, as quoted | — | the nodes' own `claim.md` files |
| The three properties a stability analysis requires of the tree | — | design (manuscript Appendix) |
| Seventeen forks in four families, computed from the tree rather than listed | C4 | |
| The baseline forks became candidate forks when the pool took both as members | C9 | |
| Eight of the eleven forks below the noise floor are the candidate-internal ones | C3, C4 | |
| The manifest is two tiers: 24 one-at-a-time and 8 pairs, on both datasets | C12 | |

## What the case demonstrates

| passage | claims | basis |
|---|---|---|
| The development manifest ran in 3.66 hours; compute was not the constraint | C10 | |
| The held-out half took 2.39 hours | C39 | |
| The external check took 1.81 hours | C47 | |
| The three results a winner-only paper would not contain | C26, C27, C6 | |
| Twenty provenance records named script versions that no longer existed | — | record (`26-09-01_b23_provenanceHashes.md`) |
| The seal sealed every clone; a fresh checkout reproduced phase E without running it | — | record (`26-09-01_b18_validationAndDrift.md`) |
| The outsider test found the freeze rule and the `combos` invariant contradicting | — | record (`26-09-01_b18_validationAndDrift.md`, plan §4b 2026-09-01) |
| Four places recorded a decision by re-deriving it at run time | — | record (batches 24, 26, 30, 20) |
| Four attempts to make the root script run from a clean checkout | — | record (`26-09-04_b31_cleanroomToCompletion.md`) |
| Every model we wrote returns identical scores; the reference does not | C37 | |

## Where this setup was more trouble than it was worth

| passage | claims | basis |
|---|---|---|
| The whole section | — | **judgment**, `agent-autonomous` (plan §4b, 2026-08-31) |
| 1 387 pages, four levels, 69 scored combinations | — | record (`AI-generated/hierarchical-report/README.md`, built 2026-09-05) |
| Storage was not a constraint; nothing was pruned | — | design (plan §4b, human-set 2026-08-29) |
| Thirty-one batch reports | — | record (the ledger) |
| The stability work cost four batches and about eight hours of compute | C10, C39 | |
| The counterfactual had to run on a branch outside the tree | — | record (`26-08-27_b21_greedyBranch.md`, on branch `greedy`) |

## Limitations

| passage | claims | basis |
|---|---|---|
| 1.90 standard errors is the largest margin; resolution is a property of the pair | C23, C24 | |
| One held-out year, four splits, roughly 216 province-months | C13 | design (plan §3) |
| Every reported ratio is a draw; our models are bit-identical | C24, C37 | |
| Three countries are not a sample; the siblings were not held out from anything | — | C42's scope field |
| The development gap is not attributable to optimisation alone | — | C43's scope field |
| The checks verify shape, never content | — | record (`26-09-01_b18_validationAndDrift.md`) |
| A figure reproduced byte-identically while what it counts went from four to one | — | record (`26-09-04_b31_cleanroomToCompletion.md`) |
