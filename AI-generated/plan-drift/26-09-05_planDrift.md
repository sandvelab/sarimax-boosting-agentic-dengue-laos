# The plan's own drift — 2026-09-05, batch 19

The same measurement batch 18 made, remade at the end of the project. Batch 18 ran it with
eighteen batches complete; this run has all thirty-one, the external check among them, and it
is the figure the release carries.

Every figure below is read from `plan_drift.json` and the four CSVs beside it, written by
`AI-internal/useful-scripts/plan_drift.py` at commit `ff29c1c4f`. Nothing here was counted by
eye. **Those files hold this run**, and `26-08-31_planDrift.md` beside this one holds the
measurement as it stood at batch 18 — the script writes to fixed filenames, so the earlier
narrative's figures are no longer in the JSON that sits next to it. That is a real gap in
this repository's own record-keeping and it is reported as one in the reproducibility report
rather than tidied away here.

---

## The short answer, unchanged in shape and larger in scale

**The plan did not drift. It grew.** 89.1 % of the delivered plan's lines are still in the
live file byte for byte, and 94.4 % of its words. What changed is scale: 468 lines became
**1 354** and 4 614 words became **32 962**, so the document is seven times its delivered
length while having deleted 51 lines and 258 words of what it originally said.

| | delivered | live | survived | deleted | added | survival |
|---|---|---|---|---|---|---|
| lines | 468 | 1 354 | 417 | 51 | 937 | **0.891** |
| words | 4 614 | 32 962 | 4 356 | 258 | 28 606 | **0.944** |

Batch 18 measured 0.891 and 0.946 on a document of 1 116 lines. **Thirteen more batches added
238 lines and retracted seven words**, which is the same finding with a longer lever: a
specification that held, with an execution record accreting under it.

## Which parts moved

All twelve sections the delivered plan had are still present under their own headings and
none was dropped. One section is new and was new at batch 18 as well: **§4b, *Decisions
settled during execution***, which did not exist at delivery. The section that survived least
is the **batch ledger**, which is the section whose whole purpose is to be rewritten.

Four sections are byte-identical to what was delivered: the preamble, **§1 The aim**, **§4
Decisions already made**, and the reports index. The aim of the project was never revised.

## The ledger

| | |
|---|---|
| batches named in the delivered plan | 7 |
| placeholders in the delivered plan | 3 |
| batches in the live ledger | **31** |
| added since delivery | **24** |
| delivered aims still worded identically | 5 |
| delivered aims reworded | 2 |

The delivered plan named seven batches and left three placeholders, one of which — batch 5 —
had as its entire job the replacement of the sketched later phases with concrete batches. It
did that, and the twenty-four batches added since are what "as autonomously as the setup
allows" produced in practice.

## Who decided what

§4b now logs **247 decisions** across **36 settling occasions**.

| agency | decisions | share |
|---|---|---|
| `agent-autonomous` | 211 | **85.4 %** |
| `human-set` | 17 | 6.9 % |
| `agent-on-human-assessment` | 9 | 3.6 % |

Seven of the thirty-six occasions were opened by the human rather than by a batch, and
fourteen decisions were taken at those occasions.

**Read this honestly and in both directions.** 85 % of the logged decisions being the agent's
is the point of the exercise and not a boast: the plan's §3 says the default is
`agent-autonomous`, so the entries that carry information are the exceptions. And the
seventeen `human-set` decisions are not seventeen small ones — they include the success
criterion, the reference model, the seal on the held-out year, the storage budget, the
repository name, the target venue, and the instruction that the perturbation set stops at 32.
The agent decided far more things; the human decided the things that determine what the
project is.

**The agency vocabulary drifted, and the counter says so rather than hiding it.**
`AGENTS.md` §4 names three values, and §4b now contains ten entries whose agency field is
something else — compound labels like *agent-autonomous, inside the human-set §3* and
*agent-autonomous, on the standing rule*, and two entries reading **carried to the human**.
Every one of them is more informative than the three-value vocabulary allows, and every one
of them falls out of the counts above, which are therefore over 247 rather than 257 entries.
The right fix is a richer vocabulary rather than a stricter one, and it is left as a finding
rather than applied at the end of the project.

## How the plan was revised

Forty-four commits touched the live plan between 2026-08-23 and 2026-09-04, adding 1 498
lines and removing 144. The largest single revision is **batch 5's bootstrap** — 104 lines
added, 22 removed — which is the batch whose job was to turn sketched phases into concrete
ones. That the largest revision to the plan is the revision the plan asked for is the
cleanest single piece of evidence here that the document was executed rather than
overwritten.

---

**Agency:** agent-autonomous. The measurement, its script and this reading are the agent's;
that the drift is a reported result rather than bookkeeping is the plan's (§ phase E).
