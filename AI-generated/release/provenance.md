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
