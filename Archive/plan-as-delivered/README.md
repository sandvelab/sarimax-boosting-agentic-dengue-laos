# The plan, as delivered

One file: `26-09-20_sarimaxResidualBoostingCase_asDelivered.md`, the state of
`Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md` at the moment
the first batch was invoked, before anything in this iteration of the repository had been
executed or edited. Read-only, marked `(IS_SHADOW)`, and never updated — that is the whole
point of it.

**Why it is kept.** The live plan is edited as the project runs: its batch ledger fills in,
its sketched phases become concrete batches, and decisions reserved to the human get settled
into it — the same discipline the prior project in this repository followed for its own plan.
How much of the original design survives contact with the work is itself a finding.

**How to see what changed.**

```bash
diff Archive/plan-as-delivered/26-09-20_sarimaxResidualBoostingCase_asDelivered.md \
     "Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md"

git log -p --follow -- "Human-input/Plans for AI generation/26-09-20_sarimaxResidualBoostingCase.md"
```

`provenance.md` beside this file records the copy and its checksum.
