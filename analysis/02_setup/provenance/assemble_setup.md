# Provenance — the assembled common ground

```
result:              results/main/analysis_dataset.csv
                     results/main/setup_spec.json
                     results/main/setup_inputs.sha256
script:              scripts/assemble_setup.py
                     sha256:e76b34bf0f3420081c89c208ef5a4a8e7834f34b82ab0f3ba99104f7ea474f6a
invocation:          "$PYTHON" scripts/assemble_setup.py
                     (from the node directory, via run.sh, after all four child forks;
                     PYTHON is environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              the four stage specifications and the last stage's dataset, each
                     resolved by searching for the one child of that fork with results
                     under this combination:
                       01_population/a_static/results/main/setup_spec.json
                       02_trainingWindow/a_from1998/results/main/setup_spec.json
                       03_provinces/a_chapFilter/results/main/setup_spec.json
                       04_retrain/a_once/results/main/{setup_spec.json,analysis_dataset.csv}
                       sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
                     (the per-stage hashes as they were on the day are in
                     results/main/setup_inputs.sha256, which this script writes)
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. A copy and a merge of four JSON documents.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/02_setup
produced:            2026-08-26
```

**What it establishes.** One dataset and one set of evaluation flags for every model in the
project. On the main path the assembled dataset is **byte-identical to the archived
development file** — `identical_to_development_file: true` in `setup_spec.json` — which is
the check that the four identity stages really are identities and not re-formattings of the
file. Off the main path it will not be identical, and then the field says so.

The flags are `n_periods 3, n_splits 8, stride 3` read from batch 3's stored scheme file and
`n_retrain 1` from the fork that decides it. `setup_spec.json` records where each flag came
from, so a reader can see that no model script carries the backtest scheme as a constant of
its own — which is the failure mode that would let two models be evaluated under different
schemes with nothing in the record showing it.

**Why the assembly exists at all.** Without it every model would have to reach into the last
fork's directory and know how many stages the setup has. With it, the setup can grow a stage
and no model script changes. The cost is one more copy of the dataset per combination, about
220 KB, which is not a cost.

alternatives-considered: the fork children could have written only specification fragments
and this script could have applied all four transformations. That was rejected because it
puts the transformation logic in the parent, so adding a sibling would mean editing a shared
script — the coupling a fork exists to avoid. The chain could also have used a pointer file
per stage rather than resolving by search; the search was chosen because it needs no extra
artifact and fails loudly rather than silently if a combination somehow has two children's
results.

agency: agent-autonomous. The `results/$COMBO/` contract and the four forks' placement are
batch 5's design (agent-autonomous, recorded there); the assembly step is this batch's, and
was not in that design — it is what the design's file contract turned out to need once the
forks had to chain.

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
                     results/$COMBO/setup_inputs.sha256
script:              unchanged from the section(s) above; this batch changed no script at
                     this node
invocation:          unchanged, with COMBO set by
                     analysis/05_stability/scripts/run_manifest.py --batch 13, and
                     COMBO_BASE=main
combinations:        aggregate_caseWeighted, aggregate_populationWeighted, popColumn_backCast, provinces_mergeVientiane, provinces_reportingOnly, retrain_everySplit, trainingWindow_from2004
inputs:              unchanged in kind; each combination's own inputs and their sha256 are
                     recorded in the specification this step writes under that combination
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
commit:              ce0eb34, except rows provinces_reportingOnly and retrain_everySplit
                     which were re-run at 7035515 after the reference node gained a retry
instructions-commit: 030bee2 (AGENTS.md unchanged by this batch)
node:                analysis/02_setup
produced:            2026-08-29
```

**What it establishes.** Five of the seven rows moved a `02_setup` fork, so the assembled dataset differs per row: 2 592 rows and 18 locations on `popColumn_backCast`, 2 448 and 17 on `provinces_mergeVientiane`, 2 304 and 16 on `provinces_reportingOnly`, 1 296 on `trainingWindow_from2004`, and `n_retrain` 8 rather than 1 on `retrain_everySplit`. Each row's `setup_spec.json` records which child answered each of the four stages and the sha256 of what it produced. The two scoring rows re-ran no setup step and inherited it.

**Why one section covers seven combinations.** The artefacts are named by their
combination-invariant path, `results/$COMBO/…`, because one script produces the same artefact
under every combination from the same invocation — the combination is a parameter, and each
file records its own in a `combo` field. `/validate invariants` accepts that form only for
combinations the stability manifest names, and its `combos` check is what keeps that set
closed, so the two checks close over each other rather than either being weakened.

alternatives-considered: a section per combination, as batches 10 and 11 wrote for the family
rows — rejected here because seven near-identical sections at twenty-odd nodes is 150 sections
that say the same sentence, and the placeholder exists precisely so that a parameterised step
is recorded once. Where a combination made this node do something *different*, that is in the
paragraph above rather than in a section of its own.

agency: agent-autonomous.
information: agent-retrieved — every figure quoted above is read from the files this batch
produced.
