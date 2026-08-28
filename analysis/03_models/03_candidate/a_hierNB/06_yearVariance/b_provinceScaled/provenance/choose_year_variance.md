# Provenance — the province-year effect's variance — one per province (main path from batch 9)

```
result:              results/main/model_option_spec.json
script:              scripts/choose_year_variance.py
                     sha256:331bea944b223a5aad0fcd9790c55af80bf8cfe3ec7c83ef61df1d9b260229b7
invocation:          "$PYTHON" scripts/choose_year_variance.py
                     (from the node directory, via run.sh, with COMBO unset, so the
                     combination is `main` and results go to results/main/. PYTHON is
                     environment/chapenv/bin/python.)
inputs:              analysis/02_setup/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage states a choice and computes summary statistics of
                     stored columns; project seed 20260822 has no surface here.
commit:              15b8516
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/06_yearVariance/b_provinceScaled
produced:            2026-08-27
```

**What it establishes.** Seventeen annual variances instead of one, and they differ by
far more than sampling: on the log-incidence scale the fitted spread runs from
**2.33** in Xaisomboun and **1.87** in Xayabury down to **0.12** in Phongsali and
Oudomxay (`results/main/fitted_model.json`, `sigma_province_year_by_province`).

**What the run of it established, and what it did not.** It is the structural half of
the repair batch 8's width diagnosis pointed at, and it half worked. Around the
batch-8 configuration it took the candidate from 26.100 to **24.230** and lifted
Vientiane Capital's 10–90 coverage off **1.000** — the interval that had covered every
outcome — which is the province the diagnosis named. It did **not** repair the other
side: Salavan's coverage, 0.125 under batch 8, reached only 0.17, and on the promoted
main path it is **0.12** still. A per-province variance widens the province whose
variance is genuinely large; it does nothing for a province whose epidemic years are
sharper than any log-scale variance can represent.

**And it turns out to be nearly redundant** with the hurdle. Measured from the
promoted configuration, reverting to a shared variance costs **0.051** CRPS
(`round2_promoted/fork_interaction.csv`), against the 1.870 it was worth alone.

**It stops the fit converging.** Every combination carrying this child runs to the
200-round cap; the shared-variance sibling converges in 48. The parameters are stable
long before — `sigma_province` moves from 1.265204 at round 197 to 1.265199 at round
200 — but the flag in the fitted object says `converged: false` and this record says
why rather than letting a reader discover it.

alternatives-considered: `a_shared`, which was the main path until this batch. Shrinking the per-province
    variances toward a common value instead of estimating them independently, which would
    steady the provinces with four or five years of record; not built, and it is the
    sibling this fork most obviously still wants. Relaxing the convergence tolerance so
    the flag reports what the parameters show; **not taken** — a criterion adjusted after
    seeing a run is a criterion adjusted to pass, and the honest record is the cap, the
    flag and this paragraph.

agency: agent-autonomous

---

## Batch 11 — the same choice under three further combinations

```
result:              family_hierNB/model_option_spec.json
                     family_ensemble/model_option_spec.json
                     weighting_crpsWeighted/model_option_spec.json
script:              scripts/choose_year_variance.py
                     sha256:331bea944b223a5aad0fcd9790c55af80bf8cfe3ec7c83ef61df1d9b260229b7
invocation:          bash analysis/03_models/03_candidate/a_hierNB/06_yearVariance/b_provinceScaled/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              PENDING
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/a_hierNB/06_yearVariance/b_provinceScaled
produced:            2026-08-28
```

**Why these combinations exist.** `family_hierNB` is candidate 1's own combination: batch 11
promoted the family fork to `c_ensemble`, so candidate 1 no longer runs under `main` and its
results live under a combination of its own, exactly as candidate 2's have since batch 10.
`family_ensemble` and `weighting_crpsWeighted` are the ensemble's two combinations, and this
step ran under them because **the pool configures its candidate-1 member from these same fork
nodes**: `c_ensemble/scripts/prepare_members.py` runs each family's fork main-path children
and that family's assembler under the running combination, rather than pointing the pool at a
configuration assembled somewhere else. That is what makes a perturbation of this fork move
the pool's member with it in phase D.

**Nothing here chose anything new.** The child that ran is the one this fork already declared
as its main path, and the specification it wrote under each of the three combinations differs
from the one it wrote under `main` in exactly one line — the `combo` field naming the
combination — because the step reads the dataset and nothing else. Verified by diff.

alternatives-considered: pointing the pool at the configuration stored under `main` instead of
assembling one under the running combination (rejected — the pool would then be configured
from a combination it is not running under, and a perturbation that moved this fork would
leave the pool's member behind).
agency: agent-autonomous
