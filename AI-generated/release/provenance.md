# Provenance — release

One section per document. Append; never overwrite an existing section.

---

## `release_scan.json`, `release_manifest.json` and `26-09-05_release.md` — 2026-09-05, batch 19

```
result:              AI-generated/release/release_scan.json
                     AI-generated/release/release_manifest.json
                     AI-generated/release/26-09-05_release.md
script:              AI-internal/useful-scripts/release_scan.py
                     sha256:2d95b56f0277aa40756644d35b6403284bd5e8070ac3f81f694da4c3d6f40ba1
                     AI-internal/useful-scripts/release_manifest.py
                     sha256:4c447ce3cadbc5daa784b9189d2c76608289d9759449167759b7e4388b47e0a6
invocation:          .venv/bin/python AI-internal/useful-scripts/release_scan.py --root .
                     .venv/bin/python AI-internal/useful-scripts/release_manifest.py --root .
inputs:              every tracked file, every blob in the git history, and every
                     provenance.md under Archive/
environment:         .venv (repository machinery) — CPython 3.13.7
seeds:               none. Both are walks and pattern matches.
commit:              (batch 19's closing commit)
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                not a node — a check on the repository rather than a result of it
produced:            2026-09-05
alternatives-considered: reading the tree for secrets rather than scanning it, which is what
                     "scan the whole tree, history included" would have meant in practice on
                     4 840 files and 8 875 blobs, and which cannot be re-run by a reader.
                     Also considered: staging a release directory. Rejected — the release is
                     the repository, and a second copy would drift from the first.
agency:              agent-autonomous for both scripts and for the readings; the licence
                     answer they record is human-set (2026-09-05, plan §4b).
```

**What the scan reports and what it cannot decide.** It reports what matched; it does not
decide whether a licence permits redistribution or whether the author wants their
home-directory path published. Both were put to the human and both were answered, and the
answers are in the plan's §4b and in the two archive provenance files that had no statement.

**The match excerpts are truncated to twelve characters.** A report that prints a secret in
full has published it a second time.

---

## `release_scan.json` and `release_manifest.json` re-run — 2026-09-06, batch 33

```
result:              AI-generated/release/release_scan.json
                     AI-generated/release/release_manifest.json
script:              AI-internal/useful-scripts/release_scan.py
                     sha256:2d95b56f0277aa40756644d35b6403284bd5e8070ac3f81f694da4c3d6f40ba1
                     AI-internal/useful-scripts/release_manifest.py
                     sha256:4c447ce3cadbc5daa784b9189d2c76608289d9759449167759b7e4388b47e0a6
                     — both unchanged since batch 19
invocation:          .venv/bin/python AI-internal/useful-scripts/release_scan.py --root .
                     .venv/bin/python AI-internal/useful-scripts/release_manifest.py --root .
inputs:              every tracked file, every blob in the git history, and every
                     provenance.md under Archive/, at commit f4c1b7c
environment:         .venv (repository machinery) — CPython 3.13.7
seeds:               none. Both are walks and pattern matches.
commit:              f4c1b7c
instructions-commit: 595c32d (AGENTS.md, CLAUDE.md, .claude/)
node:                not a node — a check on the repository rather than a result of it
produced:            2026-09-06
alternatives-considered: pushing on batch 19's scan. Rejected: 122 files changed between
                     that scan's commit and this one, and a scan is a statement about a
                     tree rather than about a project. It costs five minutes.
agency:              agent-autonomous.
```

**Why it was run again.** A safety scan is only ever true of the tree it read. Batch 19
scanned at `046a2db2`; batch 32 rewrote 94 documents and added six files after that, and
batch 33 added the two licences. **The push must be authorised by a scan of the commit being
pushed**, not of an ancestor.

**Both come back clean, and almost identical.** Three fields moved in the scan and two in the
manifest, all of them counts of what was scanned rather than of what was found:

| | batch 19 | batch 33 |
|---|---|---|
| tracked files | 4 840 | **4 852** |
| history blobs | 8 969 | **9 289** |
| credential hits, working tree | 0 | **0** |
| credential hits, history | 0 | **0** |
| home-directory path, in source files | 0 | **0** |
| Rule 10 items present | 8 of 8 | **8 of 8** |
| paths not taken, with an entry point | 23 of 23 | **23 of 23** |

The home-directory path still appears 3 965 times, in 348 files — **341 `.log`, 4 `.json`,
2 `.txt`, 1 `.csv`, and no source file at all**, which is the shape the human's decision of
2026-09-05 was made about: the logs record commands that genuinely contained absolute paths,
and the two scripts that hardcoded one were fixed rather than excused.

**The two e-mail addresses are institutional and unchanged**: one in an archived published
paper, one belonging to the maintainer of the reference service, carried in the
`service_info.json` that service returns.

information: agent-retrieved — both artefacts, and the field-by-field comparison against the
copies batch 19 committed.
