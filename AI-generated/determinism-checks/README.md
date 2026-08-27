# determinism-checks

Rule 6, verified rather than asserted. One file per run of
`AI-internal/useful-scripts/verify_model_determinism.sh`, which runs each of our models
twice under scratch combinations and compares what came out.

These are records of a check on the **method**, not analysis results, which is why they are
here and not in `analysis/`. The scratch combinations the check creates are removed when it
finishes; what survives is the verdict.

## Currently

- `model_determinism.json` — 2026-08-27. **All three of our models are byte-identical across
  two independent runs**: the per-cell scores, the model listing and the fitted model all
  match, for persistence, climatology and the candidate. The two baselines contain no
  randomness, so Rule 6 is satisfied for them by there being nothing to seed. The candidate
  does draw — from a Laplace posterior, from a prior on the province-year effect, and from
  the negative binomial on top — and its claim is that one generator seeded with component
  seed `849487747`, derived from the project seed `20260822`, serves all three; two runs and
  a diff are what test it.

**One thing to know about this file's history.** Between batch 9 and 2026-08-27 it reported
`status: differs` for every model, and that was a defect in the check rather than in the
models. The two passes ran under scratch combinations named `…_1` and `…_2`, and batch 9 had
added a `scored_under_combo` column to `models.csv` — so the check was comparing a field
whose value is the pass's own scratch name, and could not pass. The per-cell scores and the
fitted objects matched throughout, which is what batch 9's report claims in words; its
citation of the file's status word does not hold, and that report carries a dated correction
saying so. The check now runs both passes under **one** combination name and compares pass
1's saved outputs with what pass 2 wrote over them, so nothing is exempted from the
comparison. `provenance.md` has the detail.

The evaluation `.nc` is excluded from the comparison and that is not a loophole: batch 2
established that chap-core stamps `created_date` into it and serialises two set-valued
attributes in run-dependent order, so identical runs differ in those bytes while nothing
numeric moves. Everything computed *from* it is compared.

**The reference model cannot be checked this way and never will be.** It is unseeded and
exposes no seed; its spread is measured at `analysis/03_models/02_reference` instead, and
the asymmetry — our models bit-reproducible, the model we are measured against not — is one
of the project's findings.
