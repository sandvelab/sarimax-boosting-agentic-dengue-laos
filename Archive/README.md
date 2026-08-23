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

- `case-source-material/` — the five documents this project starts from: the Chap orientation
  note, the manuscript this analysis is the worked case for, the 2013 rules it updates, the
  TrustAgentic proposal and its supplement.
- `plan-as-delivered/` — the plan being executed, as it stood before the first batch ran. The
  live plan under `Human-input/` is edited as the project runs; this is the baseline the drift
  is measured against, and the drift is a reported result.
- `lao-dataset/` — the data itself: the three Lao files of the CHAP harmonized dataset, at a
  pinned commit, with a checksum manifest the partition node re-verifies on every run. The
  `(IS_SHADOW)` line marker does not apply to them — inserting a line into a CSV would be an
  edit — so the folder's README and `provenance.md` carry that statement instead.
