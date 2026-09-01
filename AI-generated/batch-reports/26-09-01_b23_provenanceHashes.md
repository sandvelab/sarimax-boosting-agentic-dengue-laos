# Batch 23 — a record's digest must be the file's

Generated from [[26-08-22_dengueForecastingCase]] — iteration 23

**State: done — produced.** A new invariant, `hashes`, and the twenty appended provenance
sections that make it pass. They land in one commit because either alone is worse than
neither: the check without the sections is a failing check, and the sections without the
check are twenty corrections with nothing to stop the twenty-first.

Batch 18 scheduled this batch after finding that `analysis/provenance/conclude.md` — the
record of this project's headline result — named a version of `conclude.py` that had not
existed since batch 16. It estimated sixteen stale records from a scan of `script:` lines.
**The check as built reads the whole `script:` block and finds twenty**, and the four it adds
are the more interesting half of the batch.

---

## 1. What the invariant says

For every file a provenance record gives a `sha256:` for, that file must exist, and the
record must name its **current** digest somewhere.

Somewhere, not in the newest section. A record here is a running account: batch 13's section
names the version that ran at batch 13 and is right to keep it. The obligation is that the
record has caught up with the file, not that it has forgotten what came before. An
abbreviated digest — `sha256:cbd3158db12438ac…`, the form the model contract files are
recorded in — satisfies it as a prefix, because abbreviating is a formatting choice and not a
weaker claim.

`AI-internal/useful-scripts/check_invariants.py`, check `hashes`. It parses each `script:`
field with the continuation lines that belong to it, and pairs a named file with the digest
that is the next token after it — so `scripts/run_hier_nb.py   (unchanged)` followed by the
model files that did change claims none of their digests. 109 file-digest pairs across the 77
records satisfy it; twenty did not.

**What it does not check**, stated here because this file is a large part of why anyone
trusts the records: that a digest is *paired* with the run it sits beside, that a library a
script imports is named at all, or that anything in the record is true. It narrows where a
human has to look. It does not do the looking.

## 2. Nineteen of the twenty are one failure, repeated

**A batch appends its section when it runs the script, changes the script again later in the
same batch, and does not append again.**

That is not carelessness about the rule; it is the rule being satisfied at the moment it is
consulted and falsified afterwards, by the same batch, in the same hour. Nothing looks wrong
afterwards. No number moves. The record reads exactly as it should.

| what changed the script | when | records left stale |
|---|---|---|
| the `__holdout` switch: six setup scripts and `conclude.py` read the dataset, the scheme and the evaluated span from `combos` rather than hard-coding development | batch 16, `895a9f8` | 9 |
| the stability figures refactored into `scripts/lib/stability_figures.py`, and `freeze_holdout_manifest.py` reading `frozen_at_commit` from git | batch 16, `48edaea` | 3 |
| the two-condition holdout seal, and the marker moved to the node root | batch 18, `ae565fd`, `ad7e64f` | 1 |
| the tier-2 gate: selection waits until every tier-1 row has been *attempted* | batch 13, `40b6936` | 1 |
| a docstring saying the sibling window starts at 2003 when it starts at 2004 | batch 13, `40b6936` | 1 |
| the pool's registered premise stopping reading `04_score`'s leaderboard | batch 11, `2799be5` | 1 |
| the shared evaluation library, twice | batches 8 and 9, `4563baf`, `49825b5` | 4 |

**The worst is the headline result's own.** Batch 16 changed `conclude.py` so that the
`dataset` field is derived from the combination name rather than being the constant
`"development"`, ran it thirty-two times to produce phase E's conclusions, and appended
nothing. So that record described a version that had not existed since 2026-08-31, and **no
record anywhere named the invocation that wrote `results/main__holdout/conclusion.json`** —
where the reported held-out skill score of **+0.0868** is read from. It does now.

**The mildest is a docstring**, and it is recorded with the same weight. `a_from1998`'s
`apply_training_window.py` had one sentence corrected and no executable line touched; no
output of that node moved, before or after. It is in the record anyway, because the check
that would let it out is one that judges whether a diff matters, and there is no such check.
A reader who finds a digest that does not match cannot tell a corrected docstring from a
moved threshold without doing the diff themselves — which is the work the digest exists to
save them.

## 3. The twentieth: a library four records name and nobody checked

Four records — the two baselines, the reference model and candidate 1 — name
`analysis/03_models/scripts/lib/chap_eval.py` in their `script:` block, **with a digest of its
own**, below the runner they belong to. The library changed twice after those records were
written: at `4563baf` it gained the `--model-configuration-yaml` route and began hashing a
model's configuration file into its specification, and at `49825b5` it began resolving
`02_setup`'s output through `COMBO_BASE` and recording which combination answered.

The eight records written after batch 9 name the current digest. The four written before it
name a superseded one — and they are this project's whole first tranche of models.

This is why the check reads the block rather than the `script:` line. **A check on the runner
alone would have passed all four**, and batch 18's scan, which read the line, is what
produced the estimate of sixteen. The same shape as the finding batch 18 wrote up about its
own `commit:` pattern: a record being more informative than the pattern expected, and being
skipped for it.

**What produced the results those four records describe.** For persistence, climatology and
the reference, `results/main/` was written at `a2cdad3`, batch 7 — before both library
changes. Nothing here argues from the diff that the current version reproduces them. Batch
18's clean-room run rebuilt the main path from a fresh clone at `ad7e64f` with the current
library, and persistence came back at 24.879338288409706 against an archived
24.879338288409706, climatology at 24.336908636118597 against 24.336908636118597. The
reference cannot be an identity check — it is unseeded, and its four repeats moved by 0.171
CRPS, a quarter of the floor this project already declines to attribute anything below.
Candidate 1's `results/main/` was written at batch 11, after both changes, so there the gap
was in the record alone.

## 4. Two things verified rather than asserted

**The stability figures were re-drawn and came back byte-identical.** Batch 16's refactor
moved the drawing into `scripts/lib/stability_figures.py` *after* the development figures had
been drawn, so `fig_skill_distribution.png` and `fig_fork_sensitivity.png` on disk had been
produced by a version that no longer existed. This batch ran both scripts under
`environment/chapenv` and `git status` reported no change — PNG and CSV alike. The files on
disk are now ones this version of the script has actually produced, rather than ones it is
asserted to reproduce.

**The reported development conclusion was not re-run, and says so.** `results/main/
conclusion.json` was written at `87440bc` by the batch-14 version of `conclude.py`. Re-running
it would make the digest and the file agree, and it is not done: it would be a re-run made
for a record's benefit rather than for the analysis's. What covers it instead is batch 18's
clean-room rebuild, which is stronger evidence than the re-run would have been, having
rebuilt every input as well as the script. The section records the gap and names what closes
it.

The distinction between those two is the batch's own rule about when to run something. A
figure is drawn from stored values in under a second and nothing upstream moves; an analysis
is not, and one of them is under a freeze. **Where re-running would have meant re-running an
analysis, this batch did not.**

## 5. A gap this batch found and closed, which the check does not catch

The `hashes` check verifies the files a record hashes. It says nothing about a result
attributed to the wrong script — that is `check_provenance`'s question, and it is satisfied
as long as *some* record names the file.

Both stability figure records fall into that gap. Their phase-E sections record
`holdout_fig_skill_distribution.png` and `holdout_fig_fork_sensitivity.png` as the output of
`fig_*.py --dataset holdout`. **The refactor removed that flag** and gave each held-out figure
its own runner, `holdout_fig_*.py`, which no section named. Two checks passing, and the record
still pointing at an invocation that would fail if a reader typed it. The new sections carry
both runners and the library they share.

Recorded rather than fixed by a further check, because the check it wants is one that runs
the invocation a record names — which is `/validate cleanroom`, at a different cost, on a
different schedule.

## 6. What was decided, and by whom

| Decision | Agency |
|---|---|
| The check reads the whole `script:` block, not the `script:` line — which is what turned batch 18's sixteen into twenty | agent-autonomous |
| A record satisfies the check by naming the current digest **anywhere**, so earlier sections keep the version that ran under them | agent-autonomous |
| An abbreviated digest satisfies it as a prefix, so the model contract files are covered as they are recorded rather than being reformatted | agent-autonomous |
| The development stability figures are re-drawn to verify the refactor; the reported conclusion is **not** re-run, and rests on batch 18's clean-room instead | agent-autonomous |
| A docstring-only change gets a section like any other, because the alternative is a check that judges whether a diff matters | agent-autonomous |
| Records are appended to, never edited: the stale digests stay where they are, each naming the version that ran under it | agent-autonomous, on the standing rule (`AGENTS.md` §1) |
| Hashing every transitively imported module is **not** adopted — a record that names a library hashes it, and one that does not is less precise rather than wrong | agent-autonomous |

## 7. What this batch says about the method

Batch 18's summary of `/validate invariants` was that **it verifies shape and never content**.
This batch moves exactly one thing across that line: a digest is now checked against the file
it describes rather than merely being present. That is worth doing and it is a small line to
have moved.

What the twenty records show is where the remaining risk is. Nineteen of them were written by
a batch that was following the rule, at the moment it consulted the rule, and were falsified
by that same batch an hour later. The obligation "record the provenance of what you produce"
is discharged at a point in time; the property "the record describes what is there" is
continuous, and nothing continuous was watching it. **A standing rule honoured at every
moment it is consulted is not the same as a property that holds** — and the gap between them
is invisible from the inside, because at each moment the rule was met.

The twentieth record shows the second-order version: batch 18 estimated sixteen by scanning
for the pattern it had in mind, and the four it missed are the four whose records were more
detailed than the scan expected. That is the same failure batch 18 itself diagnosed in the
`commit:` check, found again one batch later in the diagnosis of it.

## 8. Files

| file | what it holds |
|---|---|
| `AI-internal/useful-scripts/check_invariants.py` | the `hashes` check, and what it deliberately does not verify |
| twenty records under `analysis/**/provenance/` | one appended section each: the current digest, the commit that changed the file, what changed, and what the results on disk were produced by |
| `AI-internal/skill-references/provenance-record.md` | the digest is a required part of `script:`, and a changed script gets an appended section |
| `.claude/commands/track-result.md`, `.claude/commands/validate.md` | the same obligation where it is read during work |

`/validate invariants` passes on all nine checks. Nothing in `analysis/results/` moved: the
only files this batch wrote outside `provenance/` are the two development figures, and they
came back byte-identical.
