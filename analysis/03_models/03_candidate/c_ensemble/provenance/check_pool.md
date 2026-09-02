# Provenance — the pool rebuilt by a second path, and its registered premise

```
result:              main/pool_check.json
                     family_ensemble/pool_check.json
                     weighting_crpsWeighted/pool_check.json
script:              scripts/check_pool.py
                     sha256:6f1155c05561ddff1ab7fc7c7a852f0440d1b2edf800cc693a3c710eb0a0835c
                     imports allocate() and pool() from scripts/ensemble_model/ensemble.py,
                     so the reconstruction uses the model's own allocation rule rather than
                     a second statement of it
invocation:          "$PYTHON" scripts/check_pool.py, with COMBO set
inputs:              results/<combo>/eval.nc, fitted_model.json, candidate_spec.json,
                     members.json, model_spec.json
                     and, for each member, the stored eval.nc of a run of that member whose
                     configuration_sha256, dataset_sha256 and eval_flags are the ones the
                     pool gave it — matched by those fields, never by combination name:
                       persistence   01_baselines/01_persistence/.../results/main
                       climatology   01_baselines/02_climatology/.../results/main
                       hier_nb       03_candidate/a_hierNB/results/family_hierNB
                       boosted       03_candidate/b_boosted/results/family_boosted
environment:         environment/ (project main); the CRPS and both coverage figures come
                     from chap-core's own registered metrics, asked for by id
seeds:               the pool's component seed 1648567750, so the reconstruction allocates
                     as the model does; the subsample it takes is a different one, which is
                     what the residual difference measures
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-28
```

**What it establishes.** That the pool is what it claims to be. Rebuilt from the members'
own stored evaluations and scored with chap-core's own CRPS, it gives **18.801** against the
**18.817** the model scored — a difference of **0.016**, the sampling error of the pool's
own allocation. The members' scores computed by that second path reproduce their leaderboard
rows to every printed digit, so the models inside the pool are the models on the leaderboard
and not versions of them.

**And that the registered premises were tested rather than remembered.** Each child of
`01_weighting` writes, before anything is fitted, what it expects to happen; this script
reads it back and measures it. `a_equal`'s prediction that the pool would score worse than
its best member is **false** — the pool beats it by 1.954 CRPS — and its prediction about
coverage is true. `b_crpsWeighted`'s two predictions about the shape of the fitted weights
are true and its prediction about the size of the loss understates it.

**One diagnostic exists to kill an explanation rather than to support one.** The pool's
25–75 coverage is 0.749 against a nominal 0.50, and the obvious innocent reading is that a
count distribution with a 56 % zero share has a degenerate central interval in which every
zero outcome falls. The share of cells where each model's own 25th and 75th percentiles
coincide is therefore measured: 24 % for the pool against 41 % to 55 % for three of its four
members. The pool over-covers while being *less* exposed to the artefact than they are, so
the artefact is not the explanation and the over-dispersion is real.

**Why it degrades rather than fails when a member has no matching run.** The reconstruction
needs each member to have been evaluated on its own under the configuration the pool gave
it, and which combinations have been run is a fact about the project's history rather than
about the pool. When one is missing the file records which member and why, and the premise
check still runs. Failing would make `analysis/run.sh` depend on results it does not itself
produce.

alternatives-considered: resolving the members' evaluations by combination name through
COMBO_BASE (rejected — candidate 2 has never run under `main` or under any base the pool
inherits from, and a name-based lookup would either fail or, worse, find a differently
configured run of the same member and compare against it silently); comparing the members'
draws inside the pool with their stored draws cell by cell (rejected for now — the pool does
not store its members' raw forecasts, only its own, and storing four more sample sets per
combination is 30 MB per run for a check the CRPS agreement already makes); reporting the
25–75 coverage without the flat-interval share (rejected — it would have left a plausible
excuse standing that the data disproves).
agency: agent-autonomous

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/pool_check.json
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 13, and
                     COMBO_BASE=main
combinations:        aggregate_caseWeighted, aggregate_populationWeighted, popColumn_backCast, provinces_mergeVientiane, provinces_reportingOnly, retrain_everySplit, trainingWindow_from2004
inputs:              unchanged in kind; each combination's own inputs are recorded in the
                     specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-29
```

**What it establishes.** The pool's own consistency check, re-run under each row.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`. `/validate invariants` accepts that form only
for combinations the stability manifest names, and its `combos` check keeps that set closed.

agency: agent-autonomous.
information: agent-retrieved.


---

## Batch 22 — the two baseline-fork combinations

```
result:              results/$COMBO/pool_check.json
combinations:        climatology_frozenWindow, persistence_negBinomialFloor
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 22, and
                     COMBO_BASE=main
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               unchanged
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-29
```

**What it establishes.** The pool rebuilt from its members' own stored evaluations reproduces
the pool that ran, on both rows: 19.455 against 19.434, and 18.854 against 18.872 — residuals
of 0.021 and 0.018, the sampling error of the pool's own allocation, the same size as the
main path's 0.016. The second path to the claim survives a member being swapped, which is the
case it was built for.

alternatives-considered: none at this node.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.

## The weighting fallback, and a defect left standing (batch 26)

```
result:              no result file changes. Every `results/*/pool_check.json` in the
                     repository is byte-identical after this change; the two new keys are
                     written only on a path no archived combination takes.
script:              analysis/03_models/03_candidate/c_ensemble/scripts/check_pool.py
                     sha256:6eec2ac3880068c31ee606f0039122f865bc716ef4b5a81387fca7d5da8dbc85
invocation:          COMBO=<combination> environment/chapenv/bin/python \
                       analysis/03_models/03_candidate/c_ensemble/scripts/check_pool.py
inputs:              results/$COMBO/{candidate_spec,fitted_model,model_spec,members}.json
                     and each member's stored eval.nc
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               the pool's own allocation seed, from candidate_spec.json
commit:              39cd60b
instructions-commit: 39cd60b
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-09-02, batch 26
```

**What changed.** The premise block branched on `stage["choice"] == "b_crpsWeighted"` — the
child the combination *asked for* — and then read `fitted["weighting"]["validation"]`. But
`run_ensemble.py` falls back to equal weights when the training frame is too short to hold a
validation block back, recording `fell_back` and its reason. So a combination that asked for
CRPS weighting and correctly got equal weighting died with `KeyError: 'validation'`.

Batch 25's clean-room run selected `trainingWindow_from2004__weighting_crpsWeighted`, where a
window starting in 2004 leaves 36 months to refit members that require 60, and lost the row —
31 of 33 development rows with a conclusion instead of 32. It is the fork-blindness family
batch 14 found four times: a script keyed on the configuration rather than on the outcome.

It now branches on what the weighting **did**. The fallback is recorded rather than passed
over, because a combination whose weighting fork could not take effect is a duplicate of its
other fork wearing a pair's name. Verified against the fitted model the failed row wrote,
preserved at `AI-generated/validation/26-09-02_cleanroom-artefacts/failedRow_fitted_model.json`:
`method: equal`, `fell_back: true`, and no `validation` key.

**A larger defect found here and deliberately left standing — batch 28.**
`matching_evaluation` globs sibling result directories and breaks ties with `found[0]`, so
**which** evaluation it names, and **whether it finds one at all**, depend on which
combinations exist on disk when it runs. Re-running the unmodified script today changes
**18 of the 51** `pool_check.json` files. The worst is `main__holdout`, whose archived copy
records the reconstruction as impossible — *"no stored evaluation of ['hier_nb', 'boosted']"* —
because batch 16 ran it before those directories existed; today it reconstructs and gets
**76.646** against the reported 76.731.

**No number inside any of the eighteen moves**; what moves is which evaluation each names and
whether the reconstruction happened at all. It was verified to pre-date this batch by
re-running `HEAD`'s own copy of the script, so it is not attributable to the change above.
A tie-break repair alone would rewrite eighteen archived files while leaving the
time-dependence in place, and what the headline holdout row's reconstruction should say is
not a decision to take in passing.

alternatives-considered: recording `weighting["method"]` unconditionally — rejected, because
it would have changed all 51 archived files to add a field already in `fitted_model.json`,
and batch 26 exists to make `analysis/run.sh` reproduce its archive.

agency: agent-autonomous.
information: agent-retrieved.
