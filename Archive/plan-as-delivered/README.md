# The plan, as delivered

One file: `26-08-22_dengueForecastingCase_asDelivered.md`, the state of
`Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md` at the moment the
first batch was invoked, before anything in this repository had been executed or edited.
Read-only, marked `(IS_SHADOW)`, and never updated — that is the whole point of it.

**Why it is kept.** The live plan is edited as the project runs: its batch ledger fills in,
its sketched phases become concrete batches, and decisions reserved to the human get settled
into it. That evolution is a finding in its own right rather than bookkeeping. How much of
the original design survived contact with the work, which parts had to be revised and why,
and which revisions came from the human as opposed to being proposed by the agent, is
evidence about how far an agentic system can be handed a research plan and left to run it —
which is one of the questions this project exists to answer.

**How to see what changed.** This file is the baseline; the live plan is under version
control from the repository's first commit, so:

```bash
diff Archive/plan-as-delivered/26-08-22_dengueForecastingCase_asDelivered.md \
     "Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md"

git log -p --follow -- "Human-input/Plans for AI generation/26-08-22_dengueForecastingCase.md"
```

The first shows the total drift; the second shows it as a sequence, with each change's
reasoning in its commit message. The plan's own §4b carries the same decisions in prose,
with the agency recorded on each.

`provenance.md` beside this file records the copy and its checksum.
