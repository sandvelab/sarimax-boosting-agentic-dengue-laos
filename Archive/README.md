# Archive

Imported source material: papers, data descriptions, protocols, anything that came from
outside this project. **Never edited in place**, marked `(IS_SHADOW)` on line 2, with a
`provenance.md` beside it saying where it came from and how to re-obtain it.

Kept separate so that "what came from outside" is answerable at a glance. Anything that
needs modifying is copied out to `Human-AI-collaboration/` first; the original stays
untouched, because it may later be replaced by an updated import.

Where an import has a binary original and a markdown conversion, they go in `orig/` and
`md/` respectively; `md/` is the one to read.

## Currently here

- `plan-as-delivered/` — the current plan being executed, as it stood before the first batch
  ran. The live plan under `Human-input/` is edited as the project runs; this is the baseline
  the drift is measured against.
- `lao-dataset/` — the data itself: the three Lao files of the CHAP harmonized dataset, at a
  pinned commit, with a checksum manifest. The `(IS_SHADOW)` line marker does not apply to
  them — inserting a line into a CSV would be an edit — so the folder's README and
  `provenance.md` carry that statement instead. Carried over from the prior project in this
  repository; still Laos dengue surveillance data, re-usable as-is.
- `lao-population/` — the World Bank's annual national population series for Lao PDR, the
  one input the surveillance dataset does not carry. Same write-once treatment and the same
  reason the `(IS_SHADOW)` line marker is in the README rather than in the file.
- `sibling-datasets/` — the Thai and Vietnamese files of the same CHAP harmonized dataset, at
  the same pinned commit as the Lao ones. Not used by the prior project's main analysis; kept
  as a potential external check for whichever project needs one. Same write-once treatment,
  and the same reason the `(IS_SHADOW)` line marker is in the folder's README and
  `provenance.md` rather than in the files.
