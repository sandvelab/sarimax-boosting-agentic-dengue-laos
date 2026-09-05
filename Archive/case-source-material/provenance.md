# Provenance — case source material

All five files were assembled on **2026-08-22** in the vault where this project's plan was
written, and imported here as part of the example-case package. None has been edited beyond
the two mechanical changes noted below.

**Mechanical changes applied to every imported file:**

1. `(IS_SHADOW)` inserted on line 2.
2. Wiki links pointing at documents in the originating vault repointed to their counterparts
   in this folder, or replaced with plain text where no counterpart exists. Nothing else in
   the text was altered.

---

## chapOrientation.md

**Generated**, not imported. Written 2026-08-22 specifically for this package, so that
reconnaissance would start from checked facts rather than a search engine.

Sources, each consulted on that date:

- Chap documentation at `https://chap.dhis2.org/` — the top-level section structure and the
  three CLI pages (`chap-core-cli-setup/`, `evaluation-workflow/`, `eval-reference/`)
- `https://chap.dhis2.org/chap-modeling-platform/chap-cli/evaluation-workflow/` — the three
  commands quoted verbatim, the three backtest parameters, and the metric list
- `https://raw.githubusercontent.com/dhis2/climate-health-data/main/lao/chap_LAO_admin1_monthly_schema.json`
  — the dataset description, time range, primary key, stated row count, and every field
  definition with its source
- `https://raw.githubusercontent.com/dhis2/climate-health-data/main/lao/chap_LAO_admin1_monthly.csv`
  — the column header and the actual row count (2808 data rows against the schema's 2575,
  the discrepancy noted in §4)
- `https://api.github.com/repos/dhis2/climate-health-data/contents/` — the three country
  directories `lao`, `tha`, `vnm`
- The Chap team's terminology reference and `chap-core` endpoints guide (the `chap-infobase`
  repository), for §1's terminology table and the orchestrator/plugin description
- The Chap flagship manuscript drafts in the same repository, for the model-library and
  EWARS-csd pointers

To regenerate: re-fetch each URL above and rewrite. The document is a snapshot by design; §5
lists what was left unverified.

## reproAgenticAiManuscript.md

**Imported.** Iteration 3 of the manuscript draft *Ten simple rules for reproducible
computational research in the age of agentic AI*, dated 2026-08-22. Original filename
`26-08-20_reproAgenticAi_v3.md`, produced from the manuscript plan `A12_reproAgenticAi` in
the originating vault. Copied with `cp`; the `Generated from` line was replaced per the
mechanical changes above.

## tenSimpleRules2013.md

**Imported.** Sandve GK, Nekrutenko A, Taylor J, Hovig E. *Ten simple rules for reproducible
computational research.* PLoS Comput Biol 9(10): e1003285 (2013).
doi:10.1371/journal.pcbi.1003285. Open access (CC BY).

The markdown is a PDF conversion made previously in the originating vault. It carries
conversion artefacts — omitted-figure placeholders, and at least one paragraph that landed
out of order in the opening section. For the authoritative text, use the published article.
A title line and `(IS_SHADOW)` were prepended, since the conversion began at a section
heading rather than a title.

## trustAgenticProposal.md

**Imported.** Iteration 7 of the TrustAgentic project proposal, *Veridical agentic AI:
developing research autonomously on a real, representative case*, dated 2026-07-25. Original
filename `26-07-24_trustAgenticProject_v7.md`, produced from the grant plan `G4_trustAgentic`
in the originating vault.

## trustAgenticSupplementary.md

**Imported.** Supplementary material to the above, iteration 6, same project. Original
filename `26-07-24_trustAgenticProject_v6_supplementary.md`. Note the version mismatch with
the main text: the supplement was last revised at iteration 6 and the main text at 7. The
supplement's §S5 repeats the main text's references [1]–[8] alongside a fuller list.

---

## Licence and governance — settled 2026-09-05

```
licence/governance:  Creative Commons. Released with the repository under a standard
                     Creative Commons licence, set by the human on 2026-09-05 in answer to
                     batch 19's release scan (plan §4b).
```

**Why it had to be asked.** The scan found this the only directory besides
`../plan-as-delivered/` with no licence statement, and it holds documents that are the
human's and unpublished: the manuscript this project is the worked case for, the TrustAgentic
proposal and its supplement. `/release` forbids publishing a subset and mentioning it
afterwards, so nothing could be pushed until the question was answered. `tenSimpleRules2013.md`
is a markdown conversion of a published article and the note above it stands: for the
authoritative text, use the published article.

**agency:** human-set.
