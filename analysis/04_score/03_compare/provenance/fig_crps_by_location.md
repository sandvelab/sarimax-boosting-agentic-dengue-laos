# Provenance — figure: per-province score and calibration

```
result:              results/main/fig_crps_by_location.png
                     results/main/fig_crps_by_location.csv
                     results/main/fig_crps_by_location_preaggregation.csv
script:              scripts/fig_crps_by_location.py
                     sha256:a2076299572146b7ff0fcaf6bf18c94f4596047475e61caf656dc50d4143d90f
invocation:          "$PYTHON" scripts/fig_crps_by_location.py
                     (from the node directory, via run.sh; PYTHON is
                     environment/chapenv/bin/python. COMBO unset, so `main`.)
inputs:              analysis/04_score/02_aggregate/a_unweighted/results/main/crps_by_location.csv
                     (resolved by searching for the one child of 02_aggregate with
                     results under this combination)
                     analysis/04_score/01_collect/results/main/metrics_cell.csv
environment:         environment/ (project main) — matplotlib 3.11.1, pandas 2.3.3
seeds:               none.
commit:              f13dba4
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-26
```

**What it shows.** Every model's mean CRPS per province on a log scale, provinces ordered by
the dengue burden that produced it, with 10–90 interval coverage beside it. This is the
figure batch 6 said batch 7 would draw once two models were in the tree, and it exists
because the headline number is an unweighted mean over provinces whose burdens differ by
four orders of magnitude: an aggregate coverage close to nominal can be an average of a
province covered every time and a province covered almost never, and batch 6 measured
exactly that on one model.

The reference's four repeats are not drawn individually; the row drawn for it is the
per-cell mean over them, which is what the conclusion divides by. The repeats are in the
pre-aggregation file.

**Plotted values** are in `fig_crps_by_location.csv`. **Pre-aggregation values** are in
`fig_crps_by_location_preaggregation.csv` — the per-cell scores the province means average.

**One thing the axis label had to be corrected about.** The count beside each province is the
cases in the **evaluated** cells, 2008-01 to 2009-12, not over the whole record — it is what
the score is averaged against, and the two orderings are not the same province ordering. The
first version said only "cases", which would have invited a reader to compare it with batch
3's per-province totals over twelve years.

alternatives-considered: a linear CRPS axis was rejected because Vientiane Capital's mean
is two orders of magnitude above Phongsaly's and everything but the capital would sit on the
axis. Ordering provinces alphabetically rather than by burden was rejected: the ordering is
what makes the relationship between burden and score legible, and it is the relationship the
figure exists to show.

agency: agent-autonomous.

---

## Batch 9 addendum — the fork sweep, 2026-08-27

```
commit:              15b8516   (round 2, and the promoted main path)
                     49825b5   (round 1, which round 2 replaced in the tree; its table
                                is kept at AI-generated/candidate-forks/round1_batch8Defaults/)
instructions-commit: cf97b81
produced:            2026-08-27
```

Regenerated on `main` after the promotion, from the promoted candidate's scores. The sweep
combinations do not reach this node: batch 9 stops at `02_aggregate`, because a conclusion
per sibling is the phase-D deliverable and producing nine of them here would report the
stability answer before the manifest that makes it honest has been frozen.

**What moved.** The candidate's paired difference against the reference fell from **4.002**
CRPS to **1.599**, and its split-clustered standard error is **1.551**, so the difference
is **1.03 standard errors** -- against 3.62 for the batch-8 configuration. The comparison
that batch 8 could resolve, this one cannot: on the development backtest our candidate and
the field's own model are not distinguishable. It wins 41 % of cells and 2 of 8 splits.

alternatives-considered: none new; the node's own choices are batch 7's.

agency: agent-autonomous.

## Batch 10 — drawn again, for `family_boosted` and for `main`

```
result:              family_boosted/fig_crps_by_location.png
                     family_boosted/fig_crps_by_location.csv
                     family_boosted/fig_crps_by_location_preaggregation.csv
                     (and main/fig_crps_by_location.png, redrawn)
script:              scripts/fig_crps_by_location.py
                     sha256:d707ac6065ef557b757addcb29d0c32d0d119e1f1abe5a0e9f7244dfed0d63ad
                     analysis/scripts/lib/palette.py
                     sha256:618fd723126e7aeb4c00524a148de0512567172908c42f8e1bbe38d57913401f
invocation:          bash analysis/04_score/03_compare/run.sh
                     with COMBO=family_boosted and COMBO_BASE=main, and again with
                     neither set, for `main`
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none; a deterministic summary of stored scores.
commit:              6cb1163
instructions-commit: cf97b81
produced:            2026-08-28
```

**The colour and marker maps moved out of this script.** Until batch 10 each figure built
its own by zipping the models it found against a list of four colours, which worked while
the project had four models and broke on the fifth: `zip` stops at the shorter argument, so
two of the three figures would have drawn the new model with no marker and no error, and the
third raised a `KeyError`. The silent half is the one worth naming — a figure missing a
series is a figure a reader believes.

`analysis/scripts/lib/palette.py` now assigns both, once, from the model's **own name**
rather than from its position among the models present. That is the property the per-script
versions lacked and the reason the fix is not simply a longer list: figures are drawn per
combination and different combinations hold different sets of models, so positional
assignment would re-colour every model whenever one was added, and two figures could not be
laid side by side.

`main`'s three figures were redrawn under the new code and **no plotted value changed** —
only the colours. The plotted-values and pre-aggregation CSVs under `main` are byte-identical
to what they were.

alternatives-considered: lengthening each script's colour list in place (rejected — it fixes
this batch and not the next one, and leaves three copies of a mapping that must agree for
two figures to be comparable); keying the palette off the leaderboard's rank so the best
model is always the same colour (rejected — the rank changes between combinations, which is
exactly the instability the fix is for).
agency: agent-autonomous

---

## Batch 11 — redrawn for `main` after the promotion, and for `family_ensemble`

```
result:              
script:              scripts/fig_crps_by_location.py
                     sha256:d707ac6065ef557b757addcb29d0c32d0d119e1f1abe5a0e9f7244dfed0d63ad
invocation:          bash analysis/04_score/03_compare/run.sh, or the step alone, with COMBO=<combination>
                     and COMBO_BASE=main
environment:         environment/ (project main)
commit:              2799be5
instructions-commit: cf97b81
node:                analysis/04_score/03_compare
produced:            2026-08-28
```

```
result:              main/fig_crps_by_location.png
                     main/fig_crps_by_location.csv
                     main/fig_crps_by_location_preaggregation.csv
                     family_ensemble/fig_crps_by_location.png
                     family_ensemble/fig_crps_by_location.csv
                     family_ensemble/fig_crps_by_location_preaggregation.csv
```

**What changed.** The figure's model set. Under `main` it now draws the ensemble in place of
candidate 1, because the promotion changed which models `analysis/run.sh` produces; under
`family_ensemble` it draws the same models plus the inherited `hier_nb` row. Each figure
carries its plotted values and its pre-aggregation values beside it, as Rule 7 asks.

The colours are unaffected by the change in membership, and that is batch 10's fix working as
intended: `analysis/scripts/lib/palette.py` derives a model's colour from its own name rather
than from its position among the models present, so the two combinations' figures can be laid
side by side and every model keeps its colour across the promotion.

alternatives-considered: none new.
agency: agent-autonomous
