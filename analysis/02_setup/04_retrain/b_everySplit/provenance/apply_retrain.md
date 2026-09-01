# Provenance — refit at every split

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_retrain.py
                     sha256:09459e8d742ae2916e7950d1d2a92c30819463456eb6cfd5139e7318d999998d
invocation:          "$PYTHON" scripts/apply_retrain.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. Run by the stability driver with
                     COMBO=retrain_everySplit.)
inputs:              the analysis dataset produced by whichever child of 03_provinces ran
                     in this combination — resolved by search, not by name, and its
                     sha256 recorded in results/$COMBO/setup_spec.json as `input_sha256`
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. The stage passes the dataset through and writes one flag.
commit:              40b6936
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup/04_retrain/b_everySplit
produced:            2026-08-29
```

**What it establishes.** `n_retrain` is set to **8**, the scheme's `n_splits`, so chap-core
retrains the estimator at every split instead of once
(`results/$COMBO/setup_spec.json`). The dataset is unchanged; the flag reaches `chap eval`
through `02_setup/scripts/assemble_setup.py` and `03_models/scripts/lib/chap_eval.py`, the
same route the main path's `n_retrain = 1` takes, so no model script carries a retrain policy
of its own.

**The value is read, not typed.** chap-core rejects a parameter set with `n_retrain > n_splits`,
so the number has to be the split count of the scheme in force. It is read from
`development_scheme.n_splits` in the stored scheme file — the same key and the same file
`assemble_setup.py` reads `n_periods`, `n_splits` and `stride` from — and the source is
recorded in the specification as `n_retrain_source`. **Phase E moves both lookups together**:
when the holdout scheme replaces the development one in `assemble_setup.py`, this stage has to
follow, or the backtest would run four splits and refit eight times.

**What the fork does and does not reach.** It governs how often chap-core calls `train`. A
model that fits inside its own `predict` refits at every split whatever this flag says, which
is what the reference model does — so this fork moves the platform's behaviour and our models',
and leaves the reference where it was. The candidate-internal fork `04_fitTime` is the one that
moves ours the other way, and the two are separate rows in the manifest for that reason.

alternatives-considered: **an intermediate value**, retraining at two or four evenly spaced
points — rejected because the fork is about whether the backtest measures a model forecasting
or a model going stale, and the two ends of that answer it; intermediate values trace a curve
phase D does not report. **Leaving the flag to each model** — rejected on the grounds
`a_once` already gives: a flag set per model is a flag two models can silently disagree about,
and the comparison would then be between models evaluated differently.

agency: agent-autonomous. That `n_retrain` was an acknowledged fork rather than part of batch 3's
fixed triple is recorded in `a_once`; the value taken here, the decision to read it from the
scheme rather than type it, and the phase-E coupling note are the agent's.
information: agent-retrieved — the split count comes from the stored scheme file, and
`n_retrain`'s semantics from chap-core's own `prediction_evaluator`, which spaces the retrain
points evenly across the splits and rejects `n_retrain > n_splits`.


---

## Batch 23 — the digest batch 16's switch left behind

```
result:              results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
script:              scripts/apply_retrain.py
                     sha256:1512e07ef5e15efbf460ecfcb4f05d3183036493054ba79e7c130036dc47ca2f
invocation:          unchanged: "$PYTHON" scripts/apply_retrain.py, from the node
                     directory via run.sh, with COMBO set by the driver where a
                     combination is being run
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              895a9f8
instructions-commit: cf97b81
node:                analysis/02_setup/04_retrain/b_everySplit
produced:            2026-08-31; recorded 2026-09-01
```

**What changed in the script.** `n_retrain` stopped being read from a module constant naming the development scheme
and became `scheme[combos.scheme_key()]["n_splits"]`. Refitting at every split means every
split of *this* backtest, which is eight on development and four on the holdout, so a
constant would have made the holdout row refit more often than it has splits. The field
`n_retrain_source` in the written spec now names the key it used, so the file says which
scheme answered it.

**What ran on it.** Every development combination this node takes part in was re-derived at
`895a9f8` and this node's specifications came back byte-identical — the fields that moved
are the assembled ones at `02_setup`, which gained `evaluated_on`, `source_dataset`,
`identical_to_source_dataset` and a scheme key on each `eval_flags_source` entry. The
holdout combinations of the frozen phase-E set then ran on this version and nothing else
has.

**Why the record did not say so.** Batch 16 changed the script and ran it, and appended no
section anywhere in `02_setup`. Nothing looked wrong: the development numbers had not moved,
which is exactly the case in which a stale digest is invisible. The `hashes` invariant this
batch added is what makes it visible, and it found the same omission at twenty records.

alternatives-considered: writing one section at `02_setup` covering the whole fork chain
rather than one per node. Rejected because a provenance record belongs to the node whose
script it describes, and a reader checking `apply_provinces.py` would have to know to look
one level up — which is the kind of indirection that makes a record go unread. Correcting
the earlier sections' digests in place was rejected on the standing rule: those sections
describe runs that happened under that version, and the version they name is right.

agency: agent-autonomous.
information: agent-retrieved — the digest is computed from the file and the commit read from
`git log`; what moved in the specs is read from batch 16's report and from the diff.
