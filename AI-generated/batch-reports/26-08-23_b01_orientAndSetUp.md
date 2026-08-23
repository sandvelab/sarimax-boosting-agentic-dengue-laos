# Batch 1 — orient and set up

Generated from [[26-08-22_dengueForecastingCase]] — iteration 1

**Phase A · Status: done — produced · Executed 2026-08-23**

---

## 1. What this project is, in my own words

A forecasting problem and a record-keeping problem are being run as one exercise, and the
record-keeping problem is the reason the forecasting problem is here.

The forecasting problem: monthly reported dengue counts for the admin-1 provinces of Laos,
1998 to 2010, alongside rainfall, mean temperature, mean relative humidity and one static
population figure per province. Build something that predicts the next months' counts better
than two things that are almost free to build — repeating last month's value, and repeating
the average of that calendar month in the training window — and do it as a *probabilistic*
forecast, because the platform doing the scoring requires a distribution rather than a
number. That requirement is what puts CRPS at the centre and it is what will kill several
model families before they start.

The scoring is not mine to do. Chap is an orchestrator: models are external plugins meeting
a fixed contract, and `chap eval` runs the cross-validated backtest, holds the data isolation
in place, and writes the metric to a NetCDF file. This is the single most useful property of
the setup for the question actually being asked. If I computed my own CRPS I would be both
the optimiser and the judge, and the number would be worth very little; because the platform
computes it, the metric is harder for me to bend without it being visible.

The record-keeping problem is the point. The claim is not *this model scores X*. The claim is
*here is exactly how an agentic system arrived at a model that scores X, including everything
it tried and abandoned, every judgment call it made and what the alternatives were, and how
far the conclusion moves when those alternatives are taken instead.* Three source documents
converge on why that is worth doing: the manuscript, because it needs a worked case for a set
of rules it proposes; the proposal, because it wants to know how far agentic AI gets on a
real problem rather than a flattering one; and the veridical-data-science literature both
draw on, because the specific danger of a freely optimising agent is that it fits the
available data and the chosen metric rather than the process generating them.

The plan's design follows from that danger rather than from good practice in general. The
2010 data is not merely excluded from a metric, it is **cut out of the file**, on the
reasoning that an agent cannot leak what it cannot open — which is a sharper statement about
me than about the data. Every judgment call becomes either a runnable sibling in the claim
tree or a logged decision, because a judgment call that stays in my context and never touches
disk is exactly the kind that a fluent report will smooth over. And the gap between the
development number and the held-out number is named in advance as *the most interesting
result the project has*, which correctly makes an embarrassing outcome a successful one. My
own reading is that this is the single most important design decision in the plan: it removes
my incentive to produce a good score, because a bad one is equally publishable and a
*concealed* bad one is the only failure.

What that means for how I should work: a negative result is a result, an install that would
not build belongs in the record, and the temptation to be worth reading is the temptation to
resist. The plan says a well-recorded mediocre model beats an excellent undocumented one, and
that ordering should govern every trade-off I make.

## 2. What this batch did

| | |
|---|---|
| Git | Initialised at the repository root, branch `main`, no remote (and none is to be created). The pre-existing `.gitignore` already covered `__pycache__/`, `*.pyc`, `.DS_Store`, `.venv/`, `.env`; `.obsidian/` was added to it. |
| `.venv` | Created with `python3 -m venv .venv`. **CPython 3.13.7**, macOS 26.6.2 (arm64). This is the interpreter for the repository's own machinery — `node.py`, `check_invariants.py`, `claims.py`, `build_hierarchical_report.py` — and is *not* the analysis environment. |
| `readme-at-start.md` | Template replaced. Carries the project description, the article's status, the fixed settings from the plan's §4, the five non-negotiables, and what is reserved to the human. The backtest scheme is marked *fixed in batch 3*. |
| `README.md` | Title and the two template passages replaced. |
| `analysis/claim.md` | The root node's analytical aim written from the plan's §1. The decomposition is left empty: it is batch 5's to design and batch 7's to build. |
| `AI-generated/batch-reports/` | Created, with a `README.md` stating the naming convention, the three permitted end states, and the never-overwrite rule. |

No analysis was run, no data acquired, and Chap was not touched — as the batch specifies.

### Decisions taken in this batch

Small, but each is a judgment call and none should be silent.

| Decision | Basis | Agency |
|---|---|---|
| `.obsidian/` added to `.gitignore` | Obsidian's UI state — pane layout, appearance — is churn, and is not part of the method the way `AGENTS.md` and `.claude/` are (Rule 4). | agent-autonomous |
| `.claude/settings.local.json` **kept tracked**, over a machine-level exclude | The opposite call, and deliberately. The file grants the agent permissions, so it changes what the agent may do without asking; under Rule 4 that is method, not machine configuration, and the `.local` naming convention does not override that. Tracking it required `git add -f` — see §3.9. | agent-autonomous |
| Root `analysis/claim.md` written now rather than in batch 7 | The root *question* is settled by the plan's §1 and is not batch 5's to choose; only the decomposition beneath it is. Leaving a template at the root of the tree while `readme-at-start.md` describes a real project would be exactly the mismatch the plan warns against. | agent-on-human-assessment |
| Report filename dated 26-08-23, not 26-08-22 | The plan is dated the 22nd and was executed on the 23rd. Report dates are execution dates. | agent-autonomous |
| Branch named `main` | No instruction either way. | agent-autonomous |

## 3. What looks inconsistent, or that I did not understand

The batch asks for this list explicitly, as the first evidence about whether the instructions
work for someone arriving cold. Ordered by how much they would cost to discover late.

### 3.1 The manuscript's Appendix specifies a *different* illustrating case

The plan says to read `reproAgenticAiManuscript.md` because "its Appendix specifies what the
case must demonstrate". Its Appendix *§An illustrating case* has two paragraphs. The second,
*What the case is meant to demonstrate*, transfers to this project cleanly — affordability,
the value of the negative space, whether the checks catch real problems, and where the setup
was more trouble than it was worth. The first, *Full specification*, does not transfer at
all:

> The case is a co-occurrence analysis on public genomic region sets: given two sets of
> genomic regions, do they overlap more than expected by chance?

The same case runs through the manuscript's worked skeleton of the claim tree
(`root/ "Do region sets A and B co-occur more than expected by chance?"`, with
`02_measure/a_jaccard`, `03_null/a_uniform`), and through the perturbation families named
there.

This is not a detail. Phase E requires a case write-up "that could be lifted into the
manuscript's *An illustrating case* section", and that section currently reads "To be written
later" while its own Appendix specifies a genomics analysis. Either the manuscript is stale
with respect to the decision to use dengue, or two cases are intended and this is the second.
**I have assumed the manuscript is stale and that the dengue case replaces the genomics one**,
because the plan, the proposal and the Chap orientation note all point one way and only the
manuscript's appendix points the other. If that assumption is wrong, phase E's write-up will
be aimed at the wrong slot, and the cost of finding out then is much higher than the cost of
correcting it now.

### 3.2 "Within reach of the best already-integrated Chap model" is not operationalised

The plan's §2 defines "decent" as three conditions. Two are sharp: below persistence, below
seasonal climatology. The third — "within reach of the best already-integrated Chap model
that can be run on this dataset" — has no threshold. Ten percent worse? A factor of two?
Within the spread across splits?

§10 reserves "any change to §2's success criterion" to the human, so I do not think I may
simply pick a number. My reading is that the honest resolution is to *not* pick one: report
the reference model's mean CRPS beside the candidate's, with the per-split spread that says
whether the difference is distinguishable at all, and let the comparison stand without a
verdict. A threshold invented after seeing the numbers would be worthless anyway. **I will
proceed on that reading unless told otherwise**, and batch 4 is where it first bites, since
that is where the reference model gets run.

### 3.3 §3's "nothing else is ever pointed at anything but that file" versus batch 3's final-validation route

§3 states that everything happens on the development dataset "and nothing else is ever
pointed at anything but that file". Batch 3 then specifies the preferred final-validation
route as `chap eval` **on the full dataset**, with splits arranged so every evaluated period
falls inside 2010. Both are clearly intended — §3's next sentence says the holdout is touched
once, at the end — but the absolute phrasing and the route contradict each other on a first
reading, and an agent arriving cold could reasonably refuse the phase-E route on the strength
of §3.

Related and unaddressed: that route needs a *full* file, which after batch 3 exists only as
the pinned original under `Archive/`. Whether phase E re-reads the archived original or
concatenates the two split files is unspecified. Concatenating is the better option — it
proves the partition was lossless as a side effect — but it is a decision batch 3 should make
and record while the splitting script is being written, not one phase E should improvise.

### 3.4 Batch 3 creates a tree node before batch 7 "erects the tree"

Batch 3 says the splitting script "is a node in the tree like anything else". Batch 7 is the
batch that builds the claim tree from batch 5's design, and until then `analysis/` has only
its root. So either batch 3 creates a node ahead of the design that is meant to place it, or
its script lives outside the tree for four batches and is retro-fitted — and phase B states
that "a result produced outside it does not exist".

The workable reading is that batch 3 creates the one node it needs with `/node`, batch 5's
design accommodates it, and batch 7 re-annotates rather than rebuilds. Worth settling in
batch 3 rather than discovering in batch 7.

### 3.5 The agency vocabulary differs between the source documents and the instructions

The supplement's §S3 names the graded field *human-set*, *AI-on-human-assessment*,
*AI-autonomous*, with *AI-retrieved* / *human-pointed* for information gathering. `AGENTS.md`
§4, the plan's §3 and `/track-result` all use *agent-on-human-assessment*, *agent-autonomous*,
*agent-retrieved*. It is plainly the same scheme with AI renamed to agent, and I have used the
`AGENTS.md` spelling throughout, since that file is the source of truth here. Recording it so
that a reader comparing the two documents does not conclude there are two schemas.

### 3.6 The stability budget is stated in batches, and batches are not a measure of compute

`readme-at-start.md`'s template asks what `/perturb` may spend before stopping; the plan's §9
budgets in *batches*, which measure my context and wall-clock rather than CPU. Since the cost
of a single `chap eval` run is unknown until batch 2 or 3, no compute figure can be honest
yet. I have recorded the budget as the plan states it, in batches, and flagged that §9 itself
says batch 5 revises it once a run's cost is known. The number that will actually bind is
*evaluation runs per perturbation × perturbations*, and batch 5 should express it that way.

### 3.7 `environment/environment.yml` pins Python 3.12; `.venv` is 3.13.7

Not a conflict — `environment/README.md` says explicitly that the two are different things,
one a tool and one part of the result. Flagging it because a reader will notice, and because
the 3.12 in `environment.yml` is placeholder text from the repository template rather than a
decision: `chap-core`'s actual Python requirement is unknown, and batch 2 may have to change
it. Changing the analysis environment *after* results exist is a methodological change, so
batch 2 should settle it deliberately and run `/pin-environment` at that point.

### 3.8 `/do`'s iteration-marking convention does not fit this plan

`/do` says that from iteration 2 the passages changed in that iteration should be bolded and
the previous iteration's marks removed. That assumes iterations are successive revisions of
one document. Here batch *N* is iteration *N*, and each batch writes a *different* report about
different work — there is nothing to mark as changed. I have taken the instruction as
inapplicable rather than as something to satisfy formally. The plan's own §5 is the governing
convention.

### 3.9 A git exclude outside the repository was removing part of the method record

Staging the batch's work, `.claude/settings.local.json` silently did not appear. The cause is
a user-level exclude file at `~/.config/git/ignore` carrying `**/.claude/settings.local.json`
— a machine-wide setting, entirely outside this repository, which no clone of the repository
would carry and which nothing inside the repository records.

The file itself is innocuous: three permission entries. The mechanism is not. Rule 4 makes
`.claude/` part of the method, and here a configuration file belonging to the user's machine
rather than to the project was deciding what the method record contains — the exact shape of
failure this project exists to study, arriving unprompted in its first batch. It is also
invisible in the ordinary way: `git status` says nothing, `git add -A` reports success, and
the omission shows up only if you go looking for a file you expected to see.

Handled by tracking the file explicitly with `git add -f`, which overrides the exclude for
this path in this repository only and leaves the user's global setting alone. Recording it
because the override is a small liberty taken with a machine-level preference that is the
user's and not mine, and because a reproducer on another machine should know the file is
tracked here deliberately rather than by accident.

The general lesson is worth carrying into `/validate cleanroom`: a clean-room check that
clones the repository would not have caught this either, because the file would be *present*
in the clone. What catches it is asking whether everything expected to be tracked actually
is, and `check_invariants.py`'s git check currently asserts only that the working tree is
clean — which it was, precisely because the file was excluded.

### 3.10 A lead on the row-count discrepancy, explicitly not a finding

`chapOrientation.md` §4 flags that the schema states 2575 rows and the CSV carries 2808, and
batch 3 must resolve it from the data. I noticed while reading that the stated time range
(1998-01 to 2010-12, 156 months) divides into 2808 exactly if there are 18 provinces, which
would make 2808 a complete province × month grid. **This is arithmetic on two numbers I read
in a prose document, not a result, and it is not evidence of anything.** It is recorded here
as a hypothesis for batch 3 to test against the file, and as a worked instance of the rule it
would otherwise violate: had I written "the CSV has a complete 18 × 156 grid" into a report,
that sentence would have had no provenance and would have looked exactly like a finding.

## 4. What I did not need but expected to

Two things went better than the source material suggested they might. The repository scaffold
was already complete and internally consistent — every folder had its README, the skill files
matched `AGENTS.md`, and `check_invariants.py` implements the invariants the manuscript's
appendix lists rather than a subset. And `chapOrientation.md` §5's list of what it deliberately
did *not* verify is precisely the list batch 2 needs, which made this batch's reading cheaper
than it would have been.

## 5. Compliance for this batch

- **Rule 4** — repository initialised; the batch's work committed with the instruction files
  tracked as part of the method.
- **Rule 1** — no results were produced, so there is nothing for `/track-result` to bind. The
  decisions taken are logged in §2 above with their basis and agency, per `AGENTS.md` §4.
- **`/validate invariants`** — run at the end of the batch; outcome recorded in the ledger
  entry and in the session's task log.
- Rules 2, 3, 5, 6 and 7 have no surface in this batch: nothing was edited that I produced,
  no external program was pinned, no intermediate, no randomness, no plot.

## 6. What batch 2 needs from this one

Nothing blocking. Batch 2 starts from `chapOrientation.md` §5's five unverified points, and
should treat these as its acceptance criteria:

1. Whether `chap eval` accepts a **local model directory** as `--model-name`, or only a URL —
   this settles whether development can happen locally at all.
2. The **exact form of the reported CRPS**: over what it is computed, how aggregated, and
   whether per-region and per-split values are recoverable from the `.nc`. The plan's §2 is
   not operational until this is answered.
3. Whether `n-splits` and `stride` can be configured so that every evaluated period falls
   inside a chosen window — which decides whether phase E's validation can use Chap's own
   path or needs a script-computed CRPS validated against Chap's (§3.3 above).
4. The install recipe, including what went wrong, and `chap-core`'s Python requirement — which
   feeds back into `environment/environment.yml` (§3.7 above).
5. The model contract, read from `minimalist_example_r` and at least one model in
   `github.com/chap-models` rather than from the prose description.

Batch 2 is the largest unknown in the plan and everything else waits on it, so it is worth
splitting the moment it runs long rather than pushing through — per §5, a batch that ran out
of context without a report is the one unrecoverable failure here.

## 7. For the human

Two things I would rather have answered than assume, neither blocking:

- **§3.1** — is the dengue case replacing the genomics case in the manuscript's Appendix, or
  sitting beside it? I have assumed replacing.
- **§3.2** — is "report the reference model's CRPS beside the candidate's, with the spread,
  and draw no threshold" an acceptable reading of §2's third condition? Since §10 reserves
  changes to §2, I have not treated this as mine to settle.
