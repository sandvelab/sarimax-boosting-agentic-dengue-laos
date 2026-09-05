# release

Rule 10's safety scan and assembly, as files rather than as assurances.

**The release is the repository itself** — Rule 10 says the release is the whole tree,
alternatives included — so assembly here is a verification and not a copy. Nothing is staged
into a separate directory; a second copy of a 2.6 GB tree is a second thing to keep in step
with the first.

## Currently here

- `26-09-05_release.md` — what the scan and the manifest found, and what is and is not
  cleared to be pushed.
- `release_scan.json` — credentials in the working tree and in every blob the history holds,
  credential files by name, personal information that is not a credential, and what each
  archived dataset says about its own licence. Written by
  `AI-internal/useful-scripts/release_scan.py`.
- `release_manifest.json` — every item Rule 10 says goes into the release, checked against
  what git tracks, with the paths not taken counted and checked for entry points. Written by
  `AI-internal/useful-scripts/release_manifest.py`.
- `provenance.md` — the record for all three.

Re-run both with `.venv/bin/python AI-internal/useful-scripts/release_scan.py --root .` and
`… release_manifest.py --root .`. The scan's history half reads every blob and takes a few
minutes; `--skip-history` does the working tree only.
