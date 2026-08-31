# The plan's own drift — 2026-08-31, batch 18

How much of the research plan this project was handed survived being executed, what had to
change, and who changed it. The plan as delivered is in
`Archive/plan-as-delivered/26-08-22_dengueForecastingCase_asDelivered.md`; the live plan is
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md`.

Every figure below is read from `plan_drift.json` and the four CSVs beside it, written by
`AI-internal/useful-scripts/plan_drift.py` at commit `ad7e64f5f`. Nothing here was counted by
eye.

---

## The short answer

**The plan did not drift. It grew.** 89.1% of the delivered plan's lines are still in the
live file byte-for-byte, and 94.6% of its words. What changed is scale: 468 lines became
1 116 and 4 614 words became 24 355, so the document is five times its delivered length
while having deleted 51 lines and 251 words of what it originally said.

That shape — heavy addition, almost no retraction — is the finding. A plan that was being
overwritten as the work went would show deletions; this one shows a specification that held
and an execution record accreting under it.

| | delivered | live | survived | deleted | added | survival |
|---|---|---|---|---|---|---|
| lines | 468 | 1 116 | 417 | 51 | 699 | **0.891** |
| words | 4 614 | 24 355 | 4 363 | 251 | 19 992 | **0.946** |

The gap between the two rows is the reworded-but-not-rewritten part: a line counts as
surviving only if it is identical, so 89.1% is the fraction nobody touched at all.

## Which parts moved

All twelve sections the delivered plan had are still there under the same headings, and
none was dropped. One section is new: **§4b, *Decisions settled during execution***, which is
308 lines — a quarter of the live document — and did not exist at delivery.

| section | delivered | live | survival |
|---|---|---|---|
| (preamble) | 20 | 20 | 1.000 |
| 1. The aim | 23 | 23 | 1.000 |
| 2. What "decently" means | 18 | 47 | 0.611 |
| 3. Non-negotiables | 53 | 61 | 0.943 |
| 4. Decisions already made | 20 | 23 | 1.000 |
| 4b. Decisions settled during execution | — | 308 | new |
| 5. How this plan is executed | 39 | 41 | 0.974 |
| 6. Batch ledger | 20 | 32 | **0.500** |
| 7. Phase A | 133 | 140 | 0.977 |
| 8. Phases B–E | 112 | 304 | 0.839 |
| 9. Budget | 16 | 23 | 0.563 |
| 10. Left to me, not to you | 11 | 13 | 0.818 |
| Batch ledger — reports | 3 | 81 | 1.000 |

Four sections survive **entirely**: the preamble, §1 *The aim*, §4 *Decisions already made*,
and the reports index, which only ever gained rows. **The aim was never revised.** What the
project was for on 2026-08-22 is what it was for on 2026-08-31, and that is the single most
load-bearing line in this document, because everything else here is only interesting if the
target held still.

Three sections took real damage, and each for a different reason.

**§6, the batch ledger, at 0.500 — the lowest.** This is not drift at all; it is the ledger
doing its job. The delivered plan named **seven** batches and left **three placeholder rows**
for phases C, D and E with the note that batch 5 would write them. It now names **twenty-two**,
of which **fifteen were added after delivery**. Of the seven that were named up front, **five
kept their aim word for word** and two were reworded. A ledger that had survived intact would
mean batch 5 had failed at the one thing it was for.

**§9, the budget, at 0.563.** The delivered budget was explicitly provisional — "rough, and
to be revised by batch 5 once the cost of a `chap eval` run is actually known" — and it
guessed wrong about which phase was elastic. It allowed **~6–10 batches for model development
and ~4–6 for stability**; both came in at **four**. The revision that replaced them also
replaced the premise: the delivered plan assumed compute would be what bound, and the live
§9 says the unit is implementation effort, because a full eight-split backtest turned out to
cost 149 seconds. Phase C then acquired the stopping rule it had been missing, and phase D
acquired a named thing to cut first.

**§2, what "decently" means, at 0.611.** The delivered criterion was comparative but
unnamed: below both required baselines, and "within reach of the best already-integrated Chap
model *that can be run on this dataset, if such a model exists and can be run*". Batch 2
found out that one does, and §2 was settled the same day into something falsifiable — below
`chapkit_ewars_model` specifically, on the development backtest **and** on the held-out year,
with a spread rather than a point on both. The conditional clause became a named reference
model and a route to follow if it could not be run. The section grew from 18 lines to 47 and
kept 11 of them, and the surviving 11 are the calibration rule and the negative-result rule —
the two statements that did not depend on knowing what the reference would be.

**§3, the non-negotiables, at 0.943 across 53 delivered lines.** The five things that must
not happen were not renegotiated. What was added to them is enforcement detail, most of it
about the holdout seal.

## Who changed it

§4b records **169 decisions** across **23 settling occasions**, each with its agency in
`AGENTS.md` §4's vocabulary.

| agency | decisions | share |
|---|---|---|
| `agent-autonomous` | 145 | **85.8%** |
| `human-set` | 15 | 8.9% |
| `agent-on-human-assessment` | 8 | 4.7% |

One further row carries a compound agency — `agent-on-human-assessment; the configuration
was agent-retrieved` — and is counted in none of the three rather than being folded into the
nearest one.

**Five of the 23 occasions were the human settling something**, carrying 11 decisions between
them. The other **six `human-set` decisions sit inside batches' own tables**: the batch
reported, the human ruled, and the ruling was written up where that batch's other decisions
were. Counting occasions rather than decisions would have attributed those six to the agent,
which is the direction this project is most at risk of erring in.

So the division of labour, measured rather than described: **the human set the aim, the
success criterion, the non-negotiables and about one decision in eleven thereafter; the agent
settled the other ten.** The 15 human-set decisions are not uniformly small — they include
the reference model, the requirement to beat it on both datasets, the refusal to imply
significance, the storage budget, the target venue, the git remote, and the ruling that a
claim may state a ratio of two figures it cites. They are, characteristically, the decisions
about *what counts as success* and *what is allowed*, and almost none of them are about how
to do anything.

## How the change arrived

**27 commits** touched the live plan between 2026-08-23 and 2026-08-31. The first is the
delivered file arriving in the repository; the **26 revisions after it** added 730 lines and
removed 86.

The three largest revisions are **batch 5, the bootstrap** (`bd33f715e`, 2026-08-26,
+104 −22), whose entire job was to replace the sketched phases C–E with concrete batches;
the **settling of §2** (`15b4ba96d`, 2026-08-23, +87 −24); and **batch 21 entering the
ledger** (`782be5f07`, 2026-08-27, +56 −0), the counterfactual branch, which is the only
revision of any size that added work rather than describing work already done.

**Twenty of the 26 revisions name a batch in their subject line** — that batch adding its
own §4b table and filling in its ledger row after it had run. The six that do not are worth
listing, because they are the whole of what moved the plan for any other reason:

| date | revision |
|---|---|
| 2026-08-23 | Settle §2's success criterion and extend the stability spread to the holdout |
| 2026-08-23 | Archive the plan as delivered; log the settled decisions with their agency |
| 2026-08-27 | Repair the determinism check: both passes under one combination name |
| 2026-08-29 | A wrong zero-share figure in a comment, and the plan, readme and report for batch 22 |
| 2026-08-31 | C23 states the 1.90 standard errors, on the human's ruling |
| 2026-08-31 | Phase E's remaining decisions, settled by the human |

Two of those are corrections, two are the human ruling, and two are 2026-08-23's opening
settlement. **The plan was not re-planned. It was annotated.**

## What this is evidence for

The proposal this project belongs to asks how far an agentic system gets when handed a real
research plan and left to run it. On this one:

- **The specification held.** The aim, the non-negotiables and the pre-fixed decisions
  survived at 1.000, 0.943 and 1.000. Nothing the human fixed in advance had to be taken
  back, and the one section that was deliberately left conditional (§2's reference model) was
  closed on day one by reconnaissance rather than by negotiation.
- **The parts written as guesses were wrong in the expected direction.** The budget
  mis-identified which phase was elastic and by how much; the ledger's placeholders were
  three rows standing in for fifteen batches. Both were labelled as provisional at delivery,
  and both were revised by the batch that was told to revise them. This is a plan that knew
  what it did not know.
- **The agent decided most things and the human decided the load-bearing ones.** 85.8% of
  169 recorded decisions were the agent's alone. That number is only meaningful because the
  other 14.2% are where they are: on the criterion, the constraints and the definition of
  success.
- **The record of the change cost about as much as the change.** §4b is 308 of the live
  plan's 1 116 lines. A quarter of the plan is now the log of how the other three quarters
  were interpreted, which is the overhead this method asks for, stated as a fraction rather
  than as an impression.

One caution about all of the above. **Survival is measured against a plan that was written by
the same human who then supervised it, for an agent whose habits they had already seen.** It
is not evidence that an arbitrary research plan would survive at 89%; it is evidence about
this plan, and the honest comparator — the same plan handed to a different system, or a plan
written by someone with no such expectations — does not exist here.

## Files

| file | what it holds |
|---|---|
| `plan_drift.json` | every figure quoted above |
| `sections.csv` | one row per section, delivered and live line counts and survival |
| `ledger.csv` | one row per batch, whether it was delivered or added, and whether its aim moved |
| `decisions.csv` | all 169 §4b decisions, with date, settling occasion and agency |
| `commits.csv` | the 27 commits that touched the plan, with dates, subjects and churn |
