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
- `provenance.md` — the record for all three, and for the batch-33 re-run.

Both JSON files were **re-run twice at batch 33**, the second time on `5da6e3875` — the commit
actually pushed, licences included. The first re-run read batch 32's head and so scanned a tree
without `LICENSE`, `LICENSE-CODE` or the `Licence` section of the root `README.md`; a scan is
only ever true of the tree it read, and the one that authorises a push has to be the pushed
tree's. **All three runs come back clean**, and every field that has moved across them is a
count of what was read — 4 854 tracked files against 4 852 and 4 840, 9 318 history blobs
against 9 289 and 8 969, zero credential hits in the working tree and zero in the history every
time, 8 of 8 Rule 10 items, 23 of 23 paths not taken with an entry point. `provenance.md`
records what no scan can cover: the commit that carries a scan is a child of the commit it
scanned, and it names which files are in that gap.

Re-run both with `.venv/bin/python AI-internal/useful-scripts/release_scan.py --root .` and
`… release_manifest.py --root .`. The scan's history half reads every blob and takes a few
minutes; `--skip-history` does the working tree only.
