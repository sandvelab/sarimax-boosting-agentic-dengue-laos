# Provenance — province inclusion, left to the platform's own region filter

```
result:              results/main/analysis_dataset.csv
                     results/main/setup_spec.json
script:              scripts/apply_provinces.py
                     sha256:388ecccc10396aba0ab51cf81c7f5a61c87cc4ee9582b7ba85a6a6ff0aeff0a2
invocation:          "$PYTHON" scripts/apply_provinces.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/02_setup/02_trainingWindow/a_from1998/results/main/analysis_dataset.csv
                     sha256:c9bf8b0849c768bfe6c65d54975dd08fa390204f8b59e76904170222a7a87d4c
                     analysis/01_data/02_characterise/results/backtest_scheme_chosen.json
                     sha256:33bad460aee95b67bd06edae2fca19e28d3a3e22c6a3fe5ecced7ac03689ff51
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none. A pass-through and two set differences; project seed unused.
commit:              959f63c
instructions-commit: cf97b81
node:                analysis/02_setup/03_provinces/a_chapFilter
produced:            2026-08-26
```

**What it establishes.** 18 provinces go to the platform. One (LA-VI, Vientiane) never
reports and the platform's own region filter drops it. One further province has no
observation inside the evaluated span 2008-01 to 2009-12 (LA-XN, Xaisomboun, which stops
reporting in 2005) and therefore contributes no cell even though the filter keeps it. The
script recomputes that from the dataset and the stored scheme: **16 provinces, 371
evaluable cells**, which is what batch 3 established and what the evaluation independently
produced.

That number is derived here rather than carried: the evaluated span comes from
`backtest_scheme_chosen.json`, and the cell count from the dataset, so nothing about the
metric's denominator is a constant typed into a script.

**Why this fork is different from the other three.** Its siblings change *what is
evaluated*, not only what the models learn from, so raw CRPS is not comparable between them.
That is survivable only because the project's reported conclusion is a skill score against
the reference computed on whatever cell set the child produced — a decision taken for a
different reason (§4b, comparing development against the holdout) that turns out to be what
lets a fork move the metric's denominator at all.

alternatives-considered: dropping LA-VI and LA-XN explicitly before evaluation
(`b_dropSilent`) and merging LA-VI into the prefecture that geographically contains it
(`c_mergeVientiane`) are the siblings, built in phase D. Deciding province inclusion by a
completeness threshold of our own was rejected outright: a threshold chosen by the party
whose score depends on it is the kind of judgment call this project exists to make visible,
and there is no principled place to put it. Imputing the missing province-months was
rejected because it invents target values, which is not a setup choice but a modelling one.

agency: agent-autonomous. Which provinces the metric is a mean over was settled in batch 3
and is not reopened; that the main path delegates the decision to the platform is the
agent's.

---

## Batch 13 — the seven setup and scoring combinations

```
result:
                     results/$COMBO/analysis_dataset.csv
                     results/$COMBO/setup_spec.json
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
node:                analysis/02_setup/03_provinces/a_chapFilter
produced:            2026-08-29
```

**What it establishes.** Ran under the rows that did not move this fork.

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
