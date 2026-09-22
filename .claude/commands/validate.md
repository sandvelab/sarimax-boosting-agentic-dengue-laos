# Validate

Check that the rules were actually followed — with code, not with memory.

**Usage:** `/validate invariants` · `/validate cleanroom` · `/validate outsider` · `/validate all`

No argument: print this list and run nothing.

---

## Why this skill exists

You will follow the instructions in `AGENTS.md` most of the time. A standing rule can be
honoured for twenty steps and quietly dropped at the twenty-first, and nothing about the
output looks wrong. The party being reminded is not the party who cares about the result,
so the remedy cannot be another reminder.

**If a check fails, fix the cause. Never adjust the check so it passes.** That converts the
one honest signal here into decoration.

## invariants — every commit, every analysis end

```bash
.venv/bin/python AI-internal/useful-scripts/check_invariants.py
```

Deterministic code asserting what the rules imply: tree semantics hold; every result has a
provenance record; **every digest a record gives is the file's current one**; every plot has
its data and script; every stochastic script has a seed; every claim resolves; **the frozen
phase-E set is still the set that was frozen, and no holdout result exists at the commit
that added it**; the working tree is clean; and no value looks transcribed between steps by
hand. Ordinary code, no attention budget.

## cleanroom — before release, and on a schedule during a long project

```bash
bash AI-internal/useful-scripts/cleanroom.sh          # clone, build, run, compare
SKIP_RUN=1 bash AI-internal/useful-scripts/cleanroom.sh   # clone, build, compare inputs only
```

Clones the repository, builds both environments from nothing, runs `analysis/run.sh` and
compares every tracked result byte for byte, reporting differences rather than announcing
success. It refuses to start from a dirty tree. Findings go to
`AI-generated/validation/<date>_cleanroom-artefacts/`.

It compares the **checked-out inputs** against the repository before running anything, which is
what caught batch 19's line-ending defect: a fresh clone received `holdout.csv` with different
bytes from the ones the phase-E freeze recorded, so the holdout runner would have refused it and
phase E was not reproducible from a clone at all. Files whose content measures this machine or
this moment — wall-clock logs, run summaries, freeze-check timestamps — are declared in the
script's `VARYING` list and reported separately, so that a real difference is never lost in
noise. Run it on a schedule, not only at submission: it is how you find out an upstream
dependency changed while you were still writing.

## outsider — after any substantial change to the instructions, and before release

Start a **fresh agent with no context** — a subagent is enough — give it only what a reader
would have (the repository and its instructions, no conversation history), and ask it to
**follow** the instructions, not to judge them. Give it concrete tasks with checkable answers
(which interpreter runs what; what the main path is; how to add a competing variant; what may
be done with the holdout right now; trace one reported number to its raw file and command) and
ask it to report every point where it guessed, and every statement that is false about the
repository as it actually is. Tell it to change nothing. A system asked whether instructions are
clear will say yes; a system asked to follow them fails visibly at the ambiguous step.

Record what it got wrong, fix the documentation, repeat. What it misunderstands is what an
outsider would misunderstand — and the failures are almost always assumptions nobody knew
they were making. This is the closest thing here to an objective check, and it replaces a
judgment that was never reliable.

## What validation cannot do

These checks confirm the record is structurally **complete**, not that it is **true**. A
provenance record can name the wrong script; a claim can point at a result that does not
support it. Structural checking narrows where a human must look. It does not remove the
need to look.

The prior project's batch 18 put it more sharply, after `/validate outsider` found five
statements that were true as prose and false as behaviour: **these checks verify shape and never content.** Batch
23 moved one thing across that line — a record's digest is now checked against the file
rather than merely being present — and the rest of the line is where it was. A number can be
right and its noun wrong, and nothing here looks at nouns.
