Generated from [[26-09-20_sarimaxResidualBoostingCase]] — iteration 1 (batch 19)

# Batch 19 — the clean-room and outsider checks, and what they found

## 1. The line-ending item was not cosmetic

The plan had carried it since 2026-09-21 as a tidiness problem: nineteen CSVs are written with
Windows line endings, `core.autocrlf = input` normalises them on commit, so a fresh clone's
files hash differently from the working-copy digests in provenance records. Checking the actual
bytes turned it into something else:

```
analysis/01_data/01_prepare/results/holdout.csv
  working copy 389e4f4975980588   fresh clone e6d576431023b877
```

The phase-E freeze records `389e4f49…`, and `08_run_holdout.py` refuses to open a holdout file
whose digest is not the sealed one. **In a clean clone the runner would have correctly refused,
and phase E could not be reproduced at all.**

Settled once, tree-wide: `.gitattributes` marks `*.csv` as `-text` and `git add --renormalize`
re-stages the nineteen with their working-tree bytes. All 133 CSVs now hash identically in the
working copy, the repository and a real clone, and the sealed file agrees with its freeze
everywhere.

The alternative — adding `lineterminator="\n"` to the fifteen writers and re-running — is
recorded as rejected: it would change `holdout.csv`'s bytes, and re-freezing the phase-E seal
after the year has been opened is what the seal exists to prevent. The cost is that the writers
stay non-uniform; `.gitattributes` says so, and says not to "fix" one without re-hashing every
record that names its output. A new invariant now asserts that every `01_data` input the freeze
records still hashes to the recorded digest.

## 2. The clean-room check, which this repository did not have

`/validate cleanroom` described a check and nothing implemented it — the prior project's script
went with its analysis and only its `.gitignore` entries survived. `cleanroom.sh` now clones the
repository, builds both environments from nothing, runs `analysis/run.sh`, and compares every
tracked result byte for byte, refusing to start from a dirty tree. It compares the **checked-out
inputs before running anything**, which is the check that would have caught §1 on its own.

**The run: 88 minutes, exit 0, and the analysis reproduces from nothing.**

| | |
|---|---|
| Tracked inputs differing on checkout | **0** |
| Results byte-identical | **288** |
| Results declared-varying (wall-clock, timestamps) | 10 |
| Results genuinely differing | **1** |
| Results missing in the clone | 0 |

The one difference was `distribution_holdout.json`, and it diffed to exactly two fields:
`opening_number` (1 here, 2 in the clone) and `total_wall_seconds` (622.9 / 982.9). Both true,
neither scientific. The clone is a reproduction, and because `run_status_holdout.csv` is tracked,
row 1 travels with it and the reproduction writes row 2 — the behaviour the tracked/untracked
split was designed for.

The cause was that the report embedded `run_summary_holdout.json` whole, putting a stopwatch
inside a result file. It now embeds the opening's *identity* — phase, main path, manifest digest,
frozen commit, row counts, preflight results — and leaves the timings one file away. Verified
rather than argued: the corrected reporter was run here and in the clone, both reading only
stored files so neither reopens the year, and the two files are now byte-identical.

**Standing result: 289 of 289 comparable results reproduce byte for byte from a fresh clone**,
including all 33 held-out rows, all 26 development stability rows, every candidate and both
baselines.

## 3. The outsider test, which found more than the clean-room did

A fresh agent with no conversation history was given the repository and asked to *follow* its
instructions — read from the stated entry point, answer six questions from the instructions
alone, run the verification, trace one reported number to its raw file and command, and say what
the project concluded. It changed nothing.

It succeeded at the things this repository is built for. It found the main path two independent
ways that agreed. It traced 24.35 / −6.53% from `readme-at-start.md` through claim C31 to
`comparison.json` to the provenance record, verified all three recorded digests, and recomputed
the mean from the raw per-cell file to fifteen significant figures.

And it found twelve defects. **Ten are fixed, one is raised below, one is recorded.** The two
that matter most:

**`AGENTS.md` §8 named an interpreter that does not exist** — `environment/chapenv/bin/python`,
a prior-project path. `readme-at-start.md` and all eleven `run.sh` files were correct; the file
declared "the single source of truth" was the only one wrong, and no check can catch that. Batch
1 grepped for `chapenv`, fixed the `run.sh` template, and left this occurrence.

**Adding a new alternatives child was a deadlock, of this project's own making.** The `combos`
invariant fails on a child with no manifest row and told the contributor to re-run the planner;
the planner — made to verify rather than rewrite in batch 18 — refused; the only unblocked branch
was changing the main path, which plan §4b forbids now the holdout is open. Following the error
message in good faith ends in hand-editing a frozen artefact, which is precisely what the freeze
exists to prevent. Both messages now name the situation, the recorded-decision route, and the
fact that after the holdout opens a new path cannot enter the phase-E set at all.

The rest: `folder-structure.md` described a different repository (ten absent paths, a Docker
image, a `$COMBO` convention no node follows, and a closing line stating node directories are
numbered — false for alternatives children and enforced against by `/validate invariants`; the
outsider reports it nearly created a numbered alternatives child on that basis). `Archive/`
READMEs and provenance records named non-existent nodes and fetch scripts, so no archived
dataset's provenance could be re-enacted as written — corrected by appending, since those files
are append-only. `readme-at-start.md`'s settings table still called the holdout sealed and the
line-ending item open. Prior-project batch numbers were cited as this project's own history in
three skill docs. `validate.md` and `useful-scripts/README.md` under-described the checks and
gave no command for either of the two checks this batch ran. Every `run.sh` cited "AGENTS.md §2"
for a rule in §8. Rule 3 promised a Docker image the project does not use. Three tracked folders
had no README.

Full findings: `AI-generated/validation/2026-09-23_outsider-test.md`.

## 4. One thing for the human, not changed

**`.claude/settings.json` still contains the literal placeholders `<PARENT_DIR>` and `<HOME>`,
and the safeguard they exist for has failed.** `setup-guide.md` §2 says to replace them, and
says why: they exist "to stop a parent directory's `CLAUDE.md` leaking into this project's
instructions, **which would silently change the method**."

The outsider confirmed from inside its own session that the parent directory's `CLAUDE.md` — an
Obsidian multi-vault instruction telling agents to scan sibling vaults and copy "generalizable
insights" between `CLAUDE.md` files, and to maintain a `skills.md` this vault does not have — is
loaded alongside this project's instructions. By this repository's own Rule 4, *the instruction
files are part of the method*, and on that standard every session here has run under an
instruction set that includes a file nobody intended.

I have not changed it. Editing what instructions govern the repository is not a change to make
on an agent's report, and it bears on the published record of the method, which is yours. What
it would take: substituting the two real paths in `.claude/settings.json`, and a §4b entry
recording that sessions up to this point ran with the parent file in context.

## 5. Decisions and their agency

- **`.gitattributes` over re-running the writers**: `agent-autonomous`, and forced — re-running
  would break the phase-E seal.
- **Writing `cleanroom.sh`, and its `VARYING` list**: `agent-autonomous`. Declaring which files
  measure the machine rather than the analysis is what keeps a real difference visible.
- **Embedding the opening's identity and not its stopwatch**: `agent-autonomous`.
- **Fixing ten outsider findings, appending rather than rewriting in `Archive/`**:
  `agent-autonomous`.
- **Not touching `.claude/settings.json`**: deliberate; raised for the human.

## 6. Checks run

`/validate invariants`: all checks pass. `/validate cleanroom`: 289 of 289 comparable results
byte-identical after the one fix. `/validate outsider`: twelve findings, ten fixed, one raised,
one recorded. The clone's own `/validate invariants` passed on everything except `git`, which
failed on the files its run had just written — the tension `validate.md` now documents.

## 7. What batch 20 inherits

A repository that reproduces from nothing and whose instruction files have been walked by
someone who had never seen them. Row 20 writes the manuscript sections the project supports,
runs the release scan and pushes. Two things go with it: the settings-file decision above, and
the lesson this batch is really about — **a project that inherits a repository inherits its
prose, and prose does not fail.** Eleven of the twelve outsider findings were stale text from
the prior project. A grep for `chapenv`, `06_external`, `data-acquisition`, `$COMBO`,
`05_stability` and `batch [23][0-9]` would have found nearly all of them mechanically, and is
worth running before the release scan.
