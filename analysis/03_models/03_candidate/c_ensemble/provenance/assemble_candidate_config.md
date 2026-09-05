# Provenance — candidate 3's configuration

```
result:              main/model_configuration.yaml
                     main/candidate_spec.json
                     family_ensemble/model_configuration.yaml
                     family_ensemble/candidate_spec.json
                     weighting_crpsWeighted/model_configuration.yaml
                     weighting_crpsWeighted/candidate_spec.json
script:              scripts/assemble_candidate_config.py
                     sha256:a5ced6a7d145153bde58c6aa7c34ea35576587b56adc2aa799e9da5ef6004919
                     analysis/scripts/lib/combos.py, analysis/scripts/lib/project_seed.py
invocation:          "$PYTHON" scripts/assemble_candidate_config.py, with COMBO set
inputs:              01_weighting/<child>/results/<combo>/model_option_spec.json
                     results/<combo>/members.json
environment:         environment/ (project main)
seeds:               component seed 1648567750, derived from project seed 20260822 as
                     int(blake2b('20260822:analysis/03_models/03_candidate/c_ensemble',
                     digest_size=8), 16) % 2**32, by analysis/scripts/lib/project_seed.py.
                     A third component, distinct from candidate 1's 849487747 and
                     candidate 2's 1877199108, so no two models of ours share a stream.
                     It governs the pool's own draw only; the members draw from their own.
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-28
```

**What it establishes.** The one file `chap eval --model-configuration-yaml` is pointed at,
and the specification recording what went into it: the choice taken at the fork, the
combination that choice was taken under, the four members with the configuration each of
them was given, the union of the members' covariates, and the seed with its derivation.

**Why the membership is a path and a hash rather than an option value.** Four contract
directories with their entry points, configurations and file hashes do not fit in a scalar,
and `chap_eval.py` argues for a stored artifact over a command line nobody kept. So the
configuration carries `members_file` and `members_sha256`, and `ensemble.py` refuses to
pool anything if the file it finds is not the file the configuration names.

**On the duplication with the other two families' assemblers.** Batch 10 logged that the
shared part belongs in `03_models/scripts/lib/` and named batch 11 as where the lift
belongs. It is **scheduled rather than skipped**, and the reason is batch 9's own rule:
rewriting `a_hierNB/scripts/assemble_candidate_config.py` changes its sha256, and that hash
is in the provenance record of every combination those two assemblers configured — thirteen
of them — whose results would then name a script that never produced them. Batches 13 and
14 re-run every combination in the frozen manifest, which is the moment when regenerating
those records costs nothing extra. Recorded here, in the node's claim, in the script's
docstring and in the plan's §4b.

alternatives-considered: lifting the shared assembler into a library in this batch
(deferred, see above, with the batch it belongs to named); putting the members inline in the
configuration as an array of objects (rejected — chap-core parses the configuration into
ModelConfiguration and a nested structure there is a shape the platform does not promise to
carry, and the hash of a separate file is a stronger record than a copy inside another one);
deriving the pool's seed from the members' (rejected — Rule 6 asks for one project seed
derived per component, and the pool is a component).
agency: agent-autonomous

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/candidate_spec.json
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

**What it establishes.** The pool's configuration under each row. No fork of the pool moved in batch 13.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`. `/validate invariants` accepts that form only
for combinations the stability manifest names, and its `combos` check keeps that set closed.

agency: agent-autonomous.
information: agent-retrieved.


---

## Batch 22 — the two baseline-fork combinations

```
result:              results/$COMBO/model_configuration.yaml · candidate_spec.json
combinations:        climatology_frozenWindow, persistence_negBinomialFloor
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 22, and
                     COMBO_BASE=main
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               unchanged: the pool's component seed enters here
commit:              d8f93ca
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-29
```

**What it establishes.** The configuration under each row carries a different
`members_sha256`, because the membership moved — which is what makes a perturbation of a
member visible in the model's own record rather than only in the leaderboard.

alternatives-considered: none at this node.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.

---

## Batch 14 — the assembler lifted into a shared library

```
result:              results/$COMBO/model_configuration.yaml · candidate_spec.json
combinations:        main and every combination in which the pool is our model — this
                     batch re-ran twelve of them
script:              scripts/assemble_candidate_config.py
                     sha256:d2f1bbae36e3385d4ad702ed2bf0c218340f2793f0552450b203d8dc64b06fc7
                     analysis/03_models/scripts/lib/assemble_config.py
                     sha256:8b97f2d78063051ce7b3e1ad74dc3300b1ccf106d0654c68962045044a2af46b
invocation:          "$PYTHON" scripts/assemble_candidate_config.py, via this node's
                     run.sh, with COMBO set
inputs:              results/$COMBO/members.json, written by prepare_members.py, whose
                     path and sha256 this step puts into the configuration
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               component seed derived from project seed 20260822 from this node's
                     own path; unchanged by the lift
commit:              87440bc
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-08-30
```

**What changed.** The lift this script's own docstring scheduled. What is particular to
candidate 3 stays here and is passed into the shared assembler as data: the membership
document's path and hash, which are not option values any fork owns, and the union of the
members' covariates, which goes into the merge before any fork of this node speaks. The
other two families pass none of it, and that is the whole of what distinguishes the three.

Re-run under `main` before anything else in this batch, `model_configuration.yaml` and
`candidate_spec.json` came out byte-identical — which matters more here than at the
siblings, because this configuration's sha256 is what the reported model's `model_spec.json`
records.

alternatives-considered: as recorded at candidate 1.

agency: agent-autonomous.

## Batch 18 correction — the batch-14 commit `9993d37` is not in the history; read `87440bc`

Appended rather than edited in place, because a provenance record that silently changes an
address it once gave is worth less than one that shows the address went bad.

The sections above named **`9993d37`** as batch 14's "before the run" commit. That commit is
not an ancestor of `HEAD` and is on no branch: batch 14's history was rewritten after it was
made, and the commit that survived is **`87440bc`** — same subject, same author timestamp,
and **the same tree**, `f473a16ee75d23f4483d3d101b18119cd224b6d7`. So the *state* those
sections describe is exactly right and only the address was dead.

**Their `commit:` lines have therefore been corrected in place**, from `9993d37` to
`87440bc`, and this section is the record that it happened. Appending alone was not enough:
a provenance record exists so a reader can check out what it names, and one that keeps a
dead hash and a footnote saying to read a different one has not been repaired. Nothing else
in those sections is touched, and no result was recomputed — the two commits have the same
tree, so the state they describe is byte-identical either way.

It looked fine for eight days for two compounding reasons, both now closed in
`AI-internal/useful-scripts/check_invariants.py`. The check tested `git cat-file -e`, which
answers whether an object is in the store — and an orphaned object stays in the store of the
tree that orphaned it, and is copied wholesale by a *local* `git clone`, which hardlinks the
object directory. It would have vanished on the first push, which is batch 19. The check now
requires ancestry of `HEAD`. And the pattern was anchored to a `commit:` line carrying one
bare hash, so a line like `commit: 9993d37 (the script), 3fb1280 (the combinations)` was
skipped entirely — a record that annotated its hashes was the one the check never read. It
now takes every hash on every `commit:` line.

Found by batch 18's `/validate outsider` run, which walked the headline result's chain from
`conclusion.json` back to the archived dataset and tested each link rather than reading it.

agency: agent-autonomous.
information: agent-retrieved — `git merge-base --is-ancestor`, `git rev-parse <c>^{tree}`.

## Batch 32 — the 47 `candidate_spec.json` re-assembled; the script unchanged

```
result:              results/$COMBO/candidate_spec.json, the 47 combinations whose
                     weighting is a_equal
script:              scripts/assemble_candidate_config.py
                     sha256:d2f1bbae36e3385d4ad702ed2bf0c218340f2793f0552450b203d8dc64b06fc7
                     analysis/03_models/scripts/lib/assemble_config.py
                     sha256:8b97f2d78063051ce7b3e1ad74dc3300b1ccf106d0654c68962045044a2af46b
                     — both unchanged by this batch
invocation:          "$PYTHON" scripts/assemble_candidate_config.py, once per combination
                     with COMBO set and COMBO_BASE unset, by
                     AI-internal/useful-scripts/rewrite_weighting_premise.py
inputs:              results/$COMBO/members.json — unchanged — and the weighting child's
                     corrected results/$COMBO/model_option_spec.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               unchanged; the component seed is derived from the node path
commit:              14165dd
instructions-commit: 595c32d
node:                analysis/03_models/03_candidate/c_ensemble
produced:            2026-09-06
```

`assemble` copies each fork child's whole specification into `stages`, so a weighting premise
corrected at the child and not re-assembled here would leave the contradiction one file
further out. That is why these 47 were re-run: nothing about the assembler changed.

**`model_configuration.yaml` is byte-identical for all 47.** The premise is not an option
value, so it never reached the configuration; `configuration_sha256`, `user_option_values`,
`members_sha256` and the seed are unchanged, and no model had to be evaluated again. Measured
key by key in `AI-generated/validation/26-09-06_weightingPremiseRewrite.json`, which lists
zero fields that should not have moved.

alternatives-considered: leaving `candidate_spec.json` as it stood, on the grounds that the
authoritative copy is the child's. Rejected — the assembled document is what
`check_pool.py` reads the registered prediction from, and two copies of one specification
that disagree is the shape of defect this batch exists to remove.

agency: agent-autonomous.
information: agent-retrieved — digests computed from the files.
