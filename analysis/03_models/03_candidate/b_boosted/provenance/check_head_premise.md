# Provenance — the head fork's registered prediction, checked

```
result:              family_boosted/head_premise_check.json
                     features_richCalendar/head_premise_check.json
                     head_quantileEnsemble/head_premise_check.json
script:              scripts/check_head_premise.py
                     sha256:125617f17590f6add8097a12a7691080ba66c9f0837b385ad8aa4ff6eae7bf1a
                     scripts/boosted_model/boosted.py (imported for its own feature
                     construction and tree traversal)
                     sha256:fc2f86efbde8dbad1c697ca71969f36e4a1c9d5d3c8f824fa9f47dc451d7303b
invocation:          "$PYTHON" scripts/check_head_premise.py
                     (from the node directory, via run.sh, after the model has run)
inputs:              results/<combo>/fitted_model.json
                     02_head/<child>/results/<combo>/model_option_spec.json
                     analysis/02_setup/results/main/analysis_dataset.csv
environment:         environment/ (project main). scikit-learn is not imported: the check
                     evaluates the stored ensembles through boosted.py's own traversal,
                     which is what the storage format exists to make possible.
seeds:               none; a deterministic evaluation of a stored model.
commit:              6cb1163
instructions-commit: cf97b81
node:                analysis/03_models/03_candidate/b_boosted
produced:            2026-08-28
```

**What it establishes.** That the prediction `02_head/b_quantileEnsemble` registered before
it ran was very nearly right, and exactly where it was not. The premise named eight of the
fifteen ladder levels — every level below the target's 56.3 % zero share — as unable to move
off zero. **Seven of them are flat at zero across the whole file**: the largest count any of
those levels returns anywhere is 0.3. The eighth, 0.50, is not flat file-wide but is flat in
Vientiane Capital, the one province that never reports a zero and whose observed median is
109 cases. So the bottom 40 % of every forecast this head makes is a point mass at zero, and
in the province the prediction was about it is the bottom 50 %.

**Why the check exists as a script rather than as a paragraph.** A prediction registered
before a measurement is only worth registering if something afterwards compares the two, and
a comparison made by reading numbers off a screen is the thing `AGENTS.md` §1 forbids. Every
value here is read out of the premise the fork wrote or out of the fitted object the model
wrote; the script computes only the evaluation of the stored ladder.

**A weaker test was tried first and rejected.** Bounding each booster by its baseline plus
the largest leaf value of every tree needs no data at all, and is a statement about every
input the booster could ever be handed. One positive leaf reachable by no actual province
makes that bound non-zero, and it found nothing flat where seven levels plainly are. It
answers a different question than the premise asked, and the premise's question is about
provinces.

alternatives-considered: asserting the finding in the batch report from the fitted object's
round counts (rejected — a level that took one boosting round is evidence for the claim but
not the claim, and the claim is about what the level predicts); measuring flatness only on
the forecast rows rather than the whole file (rejected — the premise was about provinces, so
the population is the file; the forecast rows are 371 of 2 592 and would make the strongest
statement available the weakest one supportable).
agency: agent-autonomous

---

## The phase-E half (batch 16)

```
result:              results/$COMBO/head_premise_check.json
                     for every `<combination>__holdout` the frozen phase-E manifest names
                     that runs this family — here `family_boosted__holdout`,
                     `features_richCalendar__holdout` and `head_quantileEnsemble__holdout`
script:              unchanged; the same script, the same sha256, the same invocation
inputs:              unchanged, except that the family is fitted and scored on the phase-E
                     dataset and backtest scheme. Which of the two a combination faces is
                     decided by `analysis/scripts/lib/combos.py` from the `__holdout` suffix.
environment:         unchanged
seeds:               unchanged.
commit:              609e1be
instructions-commit: cf97b81
produced:            2026-08-31
alternatives-considered: none new. The premise the check tests is the one registered before
                     candidate 2 ran, and testing it again on a second year is what the
                     frozen set does to everything else as well.
agency:              agent-autonomous.
```

The artefact is named by its combination-invariant path, which is the form
`check_invariants` reads as covering every combination the manifests name.
