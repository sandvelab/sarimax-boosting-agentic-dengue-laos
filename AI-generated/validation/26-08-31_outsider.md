# Outsider check — 2026-08-31, batch 18

`/validate outsider`: start a fresh agent with no context, give it only what a reader would
have, and ask it to **follow** the instructions rather than judge them. A system asked
whether instructions are clear says yes; a system asked to follow them fails visibly at the
ambiguous step.

This is the first outsider run in this repository. It was owed from the moment the
instructions stopped being small, and phase E asks for it late enough that there is
something real to reproduce and early enough that fixing the instructions is still cheap.

## How it was run

Two agents, each given a throwaway `git clone` of the repository at `ad7e64f` and nothing
else — no conversation history, no summary, no hint about what was known to be weak. Each
was told to work only inside its own clone, to run nothing costing more than about five
minutes, and to report where following the instructions was hard. The clones are disposable
and nothing either agent did reaches the record.

**Two tasks, chosen to exercise different halves of the repository.**

- **A — write into the tree.** *"Add a new alternative to the training-window fork: a
  training window that starts in 2001. Take it as far as the repository's own instructions
  say it should be taken, and tell me what remains before it could be reported."* This
  exercises the tree semantics, the naming rules, `/node`, the manifest machinery and the
  commit discipline.
- **B — read the record.** *"Establish, from the repository alone, what the headline result
  is; which file it is read from; which script wrote that file; what command produced it, in
  what environment, from what inputs, at what commit. Verify as much of that chain as you
  can actually execute."* This exercises Rule 1 end to end.

Both were asked, in the same words, for every point where the instructions were silent,
ambiguous or contradictory; every point where they did something and the repository told
them it was wrong; and every belief formed by reading that turned out false on checking.
That third category is what this check exists to produce.

## What it cost, and what it caught

About forty minutes of wall-clock and two agent sessions. It found **six defects, three
wrong numbers in the record, and one broken link in the provenance chain of the headline
result** — none of which `/validate invariants` could see, and none of which any amount of
re-reading would have found, because every one of them is a statement that is true on the
page and false when executed.

---

## The findings that changed the repository

### 1. Three wrong counts, one of them in the claim collection

**"The eleven forks inside the two member families" — there are eight.** The two member
families hold eight forks between them; their eleven non-main children are where the eleven
comes from. It is a count of perturbed *combinations*, and the label came from a table in
batch 14's report whose column was a row count. From there it was copied into
`readme-at-start.md`, `analysis/05_stability/claim.md`, the `03_compare` provenance record,
and **claim C3 of the collection the manuscript is written from**.

**"Nine of the eleven forks below the line are candidate-internal" — eight are.** The eleven
below the noise band are eight candidate-internal forks, two `02_setup` forks and one
baseline fork. The ninth candidate fork is the pool's own weighting, which is second of
seventeen and *above* the line — as the adjacent sentence in every one of those documents
says.

**"Per-row ratios from 0.52 to 1.91" — the file says 0.514**, which rounds to 0.51.

Agent B found all three by counting the rows of `sensitivity_by_fork.csv` and
`cost_planned_vs_actual.csv` rather than reading any of the sentences that describe them.
Nothing computed changes; all three are the noun or the rounding. The live records are
corrected. **The batch reports and the plan's §4b keep what they said**, because they are
accounts of what was established at the time and rewriting them would hide that this
happened.

The lesson is narrow and worth stating: **a number can be right and its noun wrong, and no
check in this repository looks at nouns.** `claims.py` and the `claims` invariant confirm
that a claim's `grounds:` path exists; neither reads the file. That gap is exactly where all
three of these lived.

### 2. The provenance chain of the headline result named a commit that is not in the history

Six records, including `analysis/provenance/conclude.md`, named `9993d37` as batch 14's
before-the-run commit. It is not an ancestor of `HEAD` and is on no branch — batch 14's
history was rewritten and `87440bc` survived, with the same subject, the same author
timestamp and the **same tree**. So the state the records describe is exactly right and only
the address was dead.

Two compounding weaknesses in `check_invariants.py` hid it for eight days:

- The check asked `git cat-file -e`, which answers whether an object is **in the store**. An
  object orphaned by a rewritten commit stays in the store of the tree that orphaned it, and
  is copied wholesale by a *local* `git clone`, which hardlinks the object directory — so it
  looked present here and in both outsider clones. **It would have vanished on the first
  push, which is batch 19.**
- The pattern was anchored to a `commit:` line carrying one bare hash. `conclude.md` reads
  `commit: 9993d37 (the script), 3fb1280 (the combinations)`, which matched nothing at all.
  **The provenance record for this project's headline result was the one record the check
  never read**, and it was skipped for annotating its hashes — that is, for being more
  informative than the pattern expected.

Both are fixed: every hash on every `commit:` line, and ancestry of `HEAD` rather than mere
existence. The six records' `commit:` lines are corrected, each with an appended section
recording that they were and why.

### 3. The root `README.md` described the repository as it stood at batch 1

Through the whole of phases B, C and D it said *"nothing has been analysed yet… `analysis/`
holds only the root node scaffold. No data has been acquired and Chap is not yet
installed."* And its build command —
`conda env create -f environment/environment.yml` — **does not work and never did**. Agent B
ran it: `PackagesNotFoundError`. That file is the declarative half, says so in its own
header, carries `python:` and `build:` keys conda ignores, and names a PyPI-only package.
The working command was two directories away in `environment/README.md` all along.

The README now gives `bash environment/install-chap.sh`, distinguishes the two environments,
states that the run is six hours from cold and needs Docker — and **stops restating project
state altogether**, which is the actual fix. `readme-at-start.md` answers that question, and
a second document answering it is a document that will go stale without anyone noticing. It
did, for four phases.

### 4. Four instruction-file findings

Fixed and logged rather than brought back for approval, per the human's ruling of
2026-08-31.

| Finding | Fix |
|---|---|
| `AGENTS.md` §8's **"README per folder"** is violated by every node directory in the tree, which carries `claim.md` instead and is right to. Agent A followed the convention and reported having broken the stated rule. | The exemption was convention; it is now instruction. |
| §8 named `.venv` and **left node scripts ambiguous**. Agent A ran two stability scripts under the wrong interpreter, got identical output, and could not tell which one a provenance record should name. | The rule is now by location, not by what a script imports. |
| **Nothing said where work arriving outside `/do` is recorded.** Agent A invented a ledger row and said so. | The guess is now the rule. |
| `commit-run.md` names **`.claude/agents/`** as versioned method. It is an empty directory, so git does not track it and it is absent from every checkout. `readme-at-start.md` gave `/node new <parent> <name> "<claim>"`; the script requires `--claim`. | Both corrected. |

---

## The findings that are deferred, and why

Two of agent A's findings and one of agent B's are real, are not small, and touch machinery
that phase E has frozen. They are ledger rows rather than edits, because a fix written in a
hurry against a frozen manifest is a worse outcome than a fix scheduled.

### The frozen phase-E manifest is recomputed on every run

`freeze_holdout_manifest.py` is line 37 of `05_stability/run.sh` and rebuilds
`manifest_holdout.csv` from `manifest.csv` **every time `analysis/run.sh` runs**. It comes
back byte-identical, which batch 15 checked and this clean-room run checks again — but that
is a property of the tree not having changed, not a property anything enforces. Agent A
added one fork child and `bash analysis/run.sh` produced a **34-row** phase-E set including a
row for it, rewriting `holdout_freeze.json` from 33 rows to 34. That is plan §3 broken
silently, by a script re-deriving what it had derived before, with no batch and no decision.

Its one guard, `refuse_if_development_is_unfinished()`, does not catch it: the guard looks
for rows whose `conclusions.csv` entry has an empty skill score *and* a `why_not` naming a
run that has not happened, and a combination absent from that file altogether has neither.

**Not reachable today** — the tree cannot grow while phase E is closed — and the fix belongs
with someone who can re-run the freeze and check byte-identity afterwards. Batch 24.

### Sixteen provenance records name a script version that no longer exists

A scan of every `script:`/`sha256:` pair under `analysis/**/provenance/` gives **61 current
and 16 stale**. The most consequential is `analysis/provenance/conclude.md`, whose newest
section names `3acf80d9…` while `conclude.py` hashes to `2838a897…`: **batch 16 changed the
script** — `"dataset": "development"` became `"dataset": dataset()` — **ran it to produce the
holdout conclusion, and appended no section.** So the provenance record for the headline
result describes a version of the script that has not existed since batch 16, and there is
no record at all naming the invocation that wrote `main__holdout/conclusion.json`.

`/validate invariants` passes because `check_provenance` tests that the strings `script:`,
`commit:` and `environment:` are present and that some record names the result path. It
hashes nothing. `/track-result` is honest about this — *"It cannot check that the record is
true — that part is on you"* — and the `sha256` field is not even in its template, so it is a
self-imposed extra that drifted unwatched.

The fix is two halves that must land together: an invariant requiring a script's current
hash to appear in its own provenance record, and the sixteen appended sections that make it
pass. Doing the first without the second leaves a failing check; doing the second without
the first leaves it to drift again. Batch 23.

### Smaller, and folded into batch 23

- `plan_manifest.py`'s docstring documents a `--freeze-check` flag. The file has no
  `argparse` at all and the flag is silently ignored.
- `inventory.py`'s docstring says the tree has sixteen forks; it has had seventeen since
  batch 12, and the planner it feeds prints seventeen.
- `stability_figures.py` carries the "eleven forks" error in a comment.
- `AI-internal/ai_task_history.md` states **"9 046 links, none broken"** for the hierarchical
  report. The builder emits no link count and no file stores one; agent B counted 9 048.
  Either the builder records it or the sentence goes.

Each of these changes a script's bytes, and therefore its provenance record — which is why
they belong in the batch that is fixing script hashes anyway rather than being scattered
across this one.

---

## What the outsiders got right, unprompted

Both were asked not to flatter, and neither did, so this is worth recording in their terms.

Agent A: `node.py new` wrote the scaffold correctly and rebuilt the parent's `run.sh` with
the not-taken children listed; the lettered-versus-numbered naming rule is enforced and was
obeyed first time; `inventory.py` picked the new child off the tree with no edit anywhere;
`run_manifest.py --dry-run` produced a correct thirteen-step list with no change to the
driver; the `__holdout` suffix mechanism meant no dataset-switching logic had to be written
at all. And `check_invariants.py` "earned its keep" — it caught the manifest damage within
seconds and is the reason a broken repository was not committed.

Agent B: the chain from `conclusion.json` back to the archived CSV is complete and every
intermediate is on disk in a standard format; every `model_spec.json` carries the sha256 of
the dataset it was given, so the data link is verifiable without running anything; the
reference model's non-seedability is measured rather than asserted and the resulting noise
floor is carried into the conclusion file as a field; the seed derivation reproduced exactly;
three scripts regenerated their outputs byte-identically on a substitute interpreter.

## The one thing an outsider could not check, and it is the important one

Agent B could verify every link in the chain except the one where the scores are computed.
`collect_metrics.py` imports `chap_core`, and building that environment and running the
pipeline is the six-hour job. So the outsider confirmed the *record* and could not confirm
the *result*; `/validate cleanroom` is what does that, and it is the other half of this
batch.

Agent B's own summary of the structural weakness is the sentence this check exists to
produce, and it is right: **the automated checks verify shape — a record exists, a path
resolves, a commit object is present — and never content.** Both of its §5 findings and all
three of its §7 findings live in exactly that gap. Batch 18 closed the commit half of it and
scheduled the hash half.

## What was raised and is the human's, not the agent's

**Plan §3 says "nothing is added, dropped, re-tuned or re-run after a holdout number has
been seen", and does not say which artefact that binds.** Agent A hit it head-on: the task
it was given required adding a fork child, `check_invariants.py`'s `combos` check requires
the child to enter the *development* manifest, and §3 forbids adding to the *frozen phase-E
set*. It took the narrow reading — the tree and the development manifest may grow, the
frozen set may not — and said so in three places rather than deciding quietly.

That reading is almost certainly right, and it is not the agent's to confirm: §3 is a
non-negotiable and `AGENTS.md` §10 reserves changes to those. The connected question agent A
raised and could not answer is what happens to a reported distribution over 32 analyses if a
thirty-third reasonable alternative is discovered after the freeze — reported separately,
admitted, or not run. Nothing in the plan covers growth; it covers only cutting for budget.
**Both are carried to the human in batch 18's report.**
