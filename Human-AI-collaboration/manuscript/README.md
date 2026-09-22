# manuscript

The article. Written from `../claims/claims.md`, never directly from results.

Alongside each draft:

- `provenance.md` — what generated it, from which plan, on what date;
- a **provenance sidecar** keyed by paragraph or sentence identifier, mapping each statement
  to the claim it rests on. A sidecar rather than inline comments: more robust, survives
  format conversion, and can be published as supporting material.

Iterations accumulate as `_v2`, `_v3`; earlier ones are never overwritten.

Before submission, run `/claims check-text` over the draft. Sentences it flags are either
unsupported or point at a claim nobody recorded — both worth knowing, and the exercise is
meant to be slightly uncomfortable.

## Currently here

- `26-09-22_twoStageDengueLaos.md` — a short overview article (1–2 pages) of the whole study:
  design, development results, held-out results, what the conclusion turns on, implications and
  limitations. Written from claims C1–C20.
- `26-09-22_twoStageDengueLaos_claims.md` — its provenance sidecar, every statement mapped to
  the claim it rests on or to the file that fixes the design fact.
- `provenance.md` — one section per document.
