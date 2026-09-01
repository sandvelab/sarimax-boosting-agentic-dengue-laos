# Batch 18 — the clean-room, the outsider check, and the plan's own drift

Generated from [[26-08-22_dengueForecastingCase]] — iteration 18

**State: done — produced.** With one deliverable incomplete and split out rather than
claimed: the clean-room run was interrupted, and finishing it is batch 25.

Phase E's three verification obligations. Two of them had never been run in this repository
at all — `/validate outsider` not once, and `/validate cleanroom` not since batch 7, when the
tree had no stability node, no phase E and no candidate models. Between them they found
**nine defects, three wrong numbers in the record, and a broken link in the provenance chain
of the headline result**, none of which `/validate invariants` could see and none of which
any amount of re-reading would have found.

The pattern is worth stating up front, because every finding below is an instance of it:
**each was a statement that is true on the page and false when executed.** That is the class
of error this project's own checks were built to catch, and the two checks that catch it are
the two that had not been run.

---

## 1. The clean-room found its largest defect before it ran a single line

`/validate cleanroom` clones the repository, builds the environment from nothing and runs
`analysis/run.sh`. The first thing the clone did was ask the driver what it would do, and the
answer was: **nothing.**

**A fresh clone skipped all 32 phase-E rows.** The seal that plan §3 requires — the year is
opened once, and the unseeded reference is not redrawn beneath numbers already reported —
rested on `05_stability/results/run_status_holdout.csv`, which is **versioned**. A versioned
seal ships with every copy of the repository and seals copies that have never opened
anything. `collect_conclusions.py --dataset holdout` then re-read the committed conclusions,
and the phase-E half of `analysis/run.sh` reproduced `holdout_distribution.json`
**byte-identically while running none of the analysis behind it**.

A false reproduction indistinguishable from a true one, and the only kind of failure that
gets *more* convincing the more carefully you check it by reading. Three places asserted the
opposite in so many words, `run_manifest.py`'s docstring most explicitly: *"From a clean
checkout that file does not exist and the whole set runs, so `analysis/run.sh` still
reproduces phase E from nothing."*

**The fix keeps both properties the old design was trying to hold at once.** The seal now
takes two conditions and needs both: the row recorded as `ran` in the versioned status file,
so that forcing a re-run by deleting a row still leaves a trace in git; **and**
`05_stability/.holdout_opened`, gitignored, so the flag says whether *this working tree* is
the one that opened the year. Verified in both directions before anything else ran. The
marker moved out of `results/` when `/validate invariants` correctly objected that everything
there needs a provenance record — it is working-tree state, not a result, and giving it a
provenance record would have been the wrong repair.

## 2. What the clean-room established, and where it stopped

`AI-generated/validation/26-09-01_cleanroom.md`, with its figures in
`26-09-01_cleanroom_comparison.json`.

The environment built from `environment/lock.txt` and reported **"matches
environment/lock.txt exactly (174 packages)"** — the mechanism batch 7 had to repair,
exercised for the first time on a machine with no prior state. Of **4 284 tracked files,
3 994 came back byte-identical.**

**Every model this project wrote reproduced its mean CRPS to the last digit.**

| model | archived | clean-room | |
|---|---|---|---|
| persistence | 24.879338288409706 | 24.879338288409706 | identical |
| climatology | 24.336908636118597 | 24.336908636118597 | identical |
| **ensemble** (reported) | **18.816872064690028** | **18.816872064690028** | **identical** |
| reference (mean of 4) | 22.098446493261456 | 22.269520428571430 | +0.171 |

The reference is unseeded and cannot reproduce; its four repeats redrew from
{21.917, 22.272, 22.385, 21.820} to {22.436, 22.473, 22.024, 22.145}. **Everything that moved
in `conclusion.json` moved because of that and nothing else**, and the reported skill score
moved **+0.1485 → +0.1550**, a difference of 0.0065 whose 0.171 CRPS is a quarter of the
floor below which this project already declines to attribute anything to a model.
`beats_reference` and `beats_all_baselines` remain true. Sixteen of the twenty-six fields in
`conclusion.json` are unchanged, `crps_ours` among them.

**One thing that deserves more attention than it will get.** The resolvable-difference floor
itself moved, 0.565 → 0.449. Every statement of the form *"nothing below 0.57 CRPS can be
attributed to a model"* is a statement about **one sample of four repeats of an unseeded
model**, and a second sample of four moved it by 0.12. The floor is a random variable and the
project has been quoting it as a constant.

**And the archive is not quite what `run.sh` produces.** The clean-room wrote four
`member_selection.json` files the repository does not have. Five combinations — batch 13's
`02_setup` rows — were produced before `prepare_members.py` was given the fix that writes it.
Their scores are not in question; the claim that re-running reproduces the archive is
slightly false, and only a clean run says so.

**Then the run was interrupted, at 8 of 32 development rows.** It never reached tier 2 or the
phase-E half. So the reported main path is verified from cold and **the two distributions are
not**, and the phase-E half has still never been executed from a clean checkout — the seal
defect is why it could not have been before today. `readme-at-start.md`'s first invariant now
says so explicitly, and **batch 19's release must not claim more than the check supports.**
Finishing it is **batch 25**.

An interrupted check reported as complete would have been the worst single thing this batch
could produce, since the entire argument for these checks is that they do not take anyone's
word for it.

## 3. The outsider check, run for the first time

`AI-generated/validation/26-08-31_outsider.md`. Two fresh agents, each given a throwaway
clone and nothing else — no history, no summary, no hint about what was known to be weak.
One was told to **write into the tree** (add a training-window alternative and take it as far
as the instructions say); the other to **read the record** (establish what the headline result
is and verify every link back to the archived data). Both were asked, in the same words, for
every point where the instructions were silent or contradictory, and every belief formed by
reading that turned out false on checking.

They failed in disjoint places, which is the argument for having run two.

**The reader found three wrong counts and a dead commit.**

*"The eleven forks inside the two member families"* are **eight** forks; the eleven is a count
of the perturbed *combinations*. The label came from a table in batch 14's report whose column
was a row count, and was copied into `readme-at-start.md`, the stability node's `claim.md`,
the `03_compare` provenance record, and **claim C3 — the collection batch 19 writes the
manuscript from**. *"Nine of the eleven forks below the noise band are candidate-internal"* is
**eight**; the ninth candidate fork is the pool's own weighting, which is above the line, as
the adjacent sentence in every one of those documents says. And a per-row cost ratio was
rounded up from 0.514 to 0.52.

Nothing computed changes — all three are the noun or the rounding. But the lesson is exact
and uncomfortable: **a number can be right and its noun wrong, and no check here looks at
nouns.** `claims.py` and the `claims` invariant confirm that a claim's `grounds:` path
exists; neither opens the file.

**Six provenance records named a commit that is not in the history.** `9993d37` was orphaned
by a history rewrite in batch 14; `87440bc` survived, with the same subject, timestamp and
**tree**. Two compounding weaknesses hid it. The check asked `git cat-file -e`, which answers
whether an object is *in the store* — and an orphan stays in the store of the tree that
orphaned it, and is copied wholesale by a **local** `git clone`, which hardlinks the object
directory. It looked present here and in both outsider clones. **It would have vanished on
batch 19's push.** Separately, the pattern was anchored to a `commit:` line carrying one bare
hash, so `commit: 9993d37 (the script), 3fb1280 (the combinations)` matched nothing at all —
**the provenance record for this project's headline result was the one record the check never
read, and it was skipped for being more informative than the pattern expected.**

Both are fixed. The check now takes every hash on every `commit:` line and requires ancestry
of `HEAD`.

**The writer found three defects in the frozen machinery**, none of them reachable until a
fork child was added this late. The worst: `freeze_holdout_manifest.py` is line 37 of
`05_stability/run.sh` and **rebuilds the frozen phase-E manifest on every run of
`analysis/run.sh`**. It returns byte-identical because the tree has not changed, not because
anything enforces it — with one added fork child it produced a **34-row** frozen set and
rewrote `holdout_freeze.json`. Plan §3 broken silently, by a script re-deriving what it had
derived before, with no batch and no decision. Deferred to batch 24, because it is not
reachable while phase E is closed and the fix needs someone who can re-freeze and check
byte-identity afterwards.

**And the root `README.md` described batch 1** — *"nothing has been analysed yet… Chap is not
yet installed"* — through the whole of phases B, C and D, while its build command,
`conda env create -f environment/environment.yml`, **does not work and never did**. The
outsider ran it and got `PackagesNotFoundError`: that file is the declarative half, says so
in its own header, and names a PyPI-only package. The working command was two directories
away the entire time. The README now gives it, and **stops restating project state
altogether** — which is the actual repair, because a second document answering a question
`readme-at-start.md` already answers is a document that will rot unwatched. It did, for four
phases.

Four instruction-file findings were fixed and logged rather than brought back for approval,
per the human's ruling of 2026-08-31: `AGENTS.md` §8's "README per folder" is violated by
every node in the tree and the exemption is now written down; §8 left it ambiguous which
interpreter a node script gets, and the rule is now by location rather than by imports;
nothing said where work arriving outside `/do` is recorded; `commit-run.md` names
`.claude/agents/`, which is an empty directory git does not track and no checkout has.

## 4. The plan's own drift

`AI-generated/plan-drift/26-08-31_planDrift.md`, measured by a script because §1 does not
allow a figure in prose to have been counted by eye.

**The plan did not drift. It grew.** 89.1% of the delivered plan's lines survive
byte-for-byte and 94.6% of its words, while the document is five times its delivered length —
468 lines became 1 116, and 51 lines were deleted. Heavy addition, almost no retraction.

**The aim survives at 1.000 and was never revised**, as does §4, *Decisions already made*.
What moved is exactly what was labelled provisional at delivery: **§9, the budget** (0.563),
which allowed ~6–10 batches for model development and ~4–6 for stability and got four and
four, and whose premise was wrong too — it assumed compute would bind, and a full backtest
turned out to cost 149 seconds; and **§6, the ledger** (0.500), whose seven named batches and
three placeholders became twenty-two. A ledger that had survived intact would mean batch 5
failed at the one thing it was for. **§2** (0.611) was settled on day one, when reconnaissance
found that a named reference model existed, turning "within reach of the best
already-integrated Chap model, if such a model exists" into something falsifiable.

**Of 169 recorded decisions, 145 are `agent-autonomous` and 15 `human-set`** (plus 8
`agent-on-human-assessment` and one compound). Five of the 23 settling occasions were the
human's, carrying 11 decisions; **six further `human-set` decisions sit inside batches' own
tables**, and counting occasions rather than decisions would have attributed those six to the
agent — the direction this project is most at risk of erring in. The human's decisions cluster
on *what counts as success* and *what is allowed*, and almost none are about how to do
anything.

**Twenty of the 26 revisions after the first name a batch in their subject line** — that batch
adding its own §4b table after it had run. The plan was not re-planned; it was annotated.

One caution the report states and this one repeats: survival is measured against a plan
written by the same human who then supervised it, for an agent whose habits they had already
seen. It is evidence about *this* plan, and the honest comparator does not exist here.

## 5. What was decided, and by whom

| Decision | Agency |
|---|---|
| The holdout seal takes two conditions and needs both; the versioned half stays as evidence and the working-tree half is gitignored | agent-autonomous |
| The wrong counts are corrected in the live records and **left standing in the batch reports and in §4b** — those are accounts of what was established at the time, and correcting them in place would hide that the project carried a wrong noun through four batches, which is itself a result about this method | agent-autonomous |
| `check_invariants.py` requires ancestry and reads every hash on a `commit:` line | agent-autonomous |
| The root `README.md` stops restating project state rather than being given a fresher copy of it | agent-autonomous |
| The provenance-hash gap, the recomputed freeze and the unfinished clean-room become batches 23, 24 and 25 rather than edits made in a hurry against a frozen manifest | agent-autonomous |
| The outsider check is two agents on two tasks rather than one | agent-autonomous |
| **The perturbation set stays at 32; no further reasonable alternative is added** | **human-set**, 2026-09-01 |

## 6. What is left, and what is carried to the human

**Three new batches**, all phase E:

- **23** — the provenance records' script hashes. A scan gives **61 current and 16 stale**.
  The worst is `analysis/provenance/conclude.md`, whose newest section names `3acf80d9…`
  while `conclude.py` hashes to `2838a897…`: **batch 16 changed the script, ran it to produce
  the holdout conclusion, and appended no section.** So the headline result's provenance
  describes a version that has not existed since batch 16, and no record anywhere names the
  invocation that wrote `main__holdout/conclusion.json`. The fix is an invariant plus sixteen
  appended sections, and they must land together or the check fails.
- **24** — `freeze_holdout_manifest.py`'s recomputation of the frozen set.
- **25** — the clean-room, run to completion.

Batch 19 comes last, because a release must not claim more than its own checks support.

**One question is carried to the human and is not the agent's:** plan §3 says *"nothing is
added, dropped, re-tuned or re-run after a holdout number has been seen"* and **does not say
which artefact that binds.** The outsider hit it head-on — the `combos` invariant requires a
new fork child to enter the *development* manifest while §3 forbids adding to the *frozen
phase-E set*. It took the narrow reading, said so in three places rather than deciding
quietly, and it is almost certainly right. §3 is a non-negotiable and `AGENTS.md` §10
reserves changes to those, so the reading wants confirming in the text rather than inferring
from context.

The connected question — what happens to a distribution over 32 analyses if a thirty-third
reasonable alternative is found after the freeze — **was answered on 2026-09-01: the 32 are
sufficient and nothing further is added.** That also settles batch 24's practical urgency:
the tree does not grow again before release, so the defect is fixed for the reader rather
than for this project.

## 7. What this batch says about the method

The two checks that had never been run found more than the sixteen batches before them
reported between them, and everything they found is the same shape: **a statement about the
repository that was true as prose and false as behaviour.** The seal that sealed clones. The
docstring asserting the opposite of what the code did. The README whose build command had
never worked. The provenance record pointing at a commit no reader could fetch. A noun that
had been wrong through four batches while every number beside it was right.

`/validate invariants` passed throughout all of it, and was not wrong to — it checks that a
record exists, a path resolves, a commit object is present. **It verifies shape and never
content**, which is the outsider's own summary and the most useful sentence either agent
produced. Batch 18 closed the commit half of that gap and scheduled the hash half. The noun
half is not closable by code, and the honest thing to say is that it was caught by a stranger
counting rows in a CSV, which is not a mechanism — it is a check that has to be paid for
each time.
