# determinism-checks

Rule 6, verified rather than asserted. One file per run of
`AI-internal/useful-scripts/verify_model_determinism.sh`, which runs each of our models
twice under scratch combinations and compares what came out.

These are records of a check on the **method**, not analysis results, which is why they are
here and not in `analysis/`. The scratch combinations the check creates are removed when it
finishes; what survives is the verdict.

## Currently

- `model_determinism.json` — 2026-08-26, batch 7. **Both baselines are byte-identical
  across two independent runs**: the per-cell scores, the model listing and the fitted model
  all match. Neither contains randomness, so Rule 6 is satisfied by there being nothing to
  seed, and the project seed `20260822` has no surface in either.

The evaluation `.nc` is excluded from the comparison and that is not a loophole: batch 2
established that chap-core stamps `created_date` into it and serialises two set-valued
attributes in run-dependent order, so identical runs differ in those bytes while nothing
numeric moves. Everything computed *from* it is compared.

**The reference model cannot be checked this way and never will be.** It is unseeded and
exposes no seed; its spread is measured at `analysis/03_models/02_reference` instead, and
the asymmetry — our models bit-reproducible, the model we are measured against not — is one
of the project's findings.
