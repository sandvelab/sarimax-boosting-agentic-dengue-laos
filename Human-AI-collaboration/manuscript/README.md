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

- `26-09-05_illustratingCase.md` — batch 19. The document that could be lifted into the
  manuscript's *An illustrating case* section: what the analysis did, the main results, the
  stability result, the held-out year and the external check, followed by the worked
  claim-tree skeleton and the perturbation families in dengue terms — which is what the
  archived manuscript's Appendix supplies for the case this one replaces — and the agent's
  judgment about where this setup was more trouble than it was worth.
- `26-09-05_illustratingCase_sidecar.md` — its provenance sidecar: every passage mapped to
  the claims it rests on, or to what kind of statement it is instead where it rests on none.
- `provenance.md` — one section per document.
