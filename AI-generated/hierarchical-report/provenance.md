# provenance — `hierarchical-report/`

The append-only record of each build. The report itself is gitignored — it is regenerated from
the tree by one command and an untracked copy of generated HTML is of no use to anyone — so this
file is the tracked record that the build happened, from what, and at which commit.

Append a section per build; never overwrite one.

---

## Build 1 — 2026-09-22 (batch 18)

script: `AI-internal/useful-scripts/build_hierarchical_report.py`
        sha256:2536dbb50a793f4967768abbae4dca44e0dae5d98cab7b9452647dfcb6ad5fa5
invocation: `.venv/bin/python AI-internal/useful-scripts/build_hierarchical_report.py`
        (the repository's own machinery, so `.venv`, not the pinned analysis environment)
inputs: the tree itself — every `analysis/**/claim.md`, `run.sh`, `results/`, `scripts/` and
        `provenance/`; and `Human-AI-collaboration/claims/claims.md`, from which each node page
        lists the claims resting on it.
output: `AI-generated/hierarchical-report/` — 127 static HTML pages, 1.8 MB: one page per node
        (23), one detail page per scored result (103), and the root index.
commit: ed18384  (the generator as it ran; the page footers record
        the commit that was HEAD at build time, ed18384)
node: not a node; this is a view over the whole tree.
produced: 2026-09-22

**What changed in the generator this batch, and why.** The drill-down below the tree
(`_detail_pages`) was inherited from the prior project and addressed its layout —
`analysis/04_score/01_collect/results/<combo>/metrics_cell.csv`, `crps_by_location.csv`,
`leaderboard.csv`, `analysis/results/<combo>/conclusion.json`. None of those paths exist in this
project, so the root page reported "0 combination(s) scored" and Rule 8's requirement that
summaries link down to the values they aggregate was not being met: the tree rendered, and the
level below it was empty. That is the same failure as a check that passes by looking in an empty
place, and it is fixed rather than described.

The drill-down is now discovered from what is on disk: every directory holding a
`per_cell_scores.csv` is a scored result, labelled by where it sits (103 of them — stage 1, both
baselines, the ten stage-2 candidates, and every development and held-out stability
combination). Each gets one page carrying the stored conclusion as the file states it, the
`by_split` and `by_horizon` blocks the conclusion file already holds, the same cells grouped by
province and by month, and a link to the per-cell file every number above averages.
`_location_names` was repointed from the prior project's `evaluable_cells_by_province.csv` to
this project's `province_summary.csv`.

**One honest boundary.** The by-province and by-month tables are groupings of the per-cell file
shown on the same page, computed by the report for display. They are not separately stored
results, and each table says so on the page. Everything else on a detail page is read from a
stored file. The alternative — storing a per-province and per-month aggregate beside every one
of the 103 results — would mean re-running the analysis inside a reporting batch, which is a
larger change than this batch should make; it is recorded here as the alternative not taken.

alternatives-considered:
  - Leaving the drill-down pointing at the prior project's paths and noting it in the batch
    report: rejected. It rendered as a heading with nothing under it, which reads as "there is
    nothing below this level" rather than "this was never wired up".
  - A page per province per combination (the prior project's fourth level): rejected on size —
    about 1,700 pages for 103 combinations — with the per-province and per-month tables on the
    combination's own page instead, and the raw file one click away.
agency: agent-autonomous (the rewrite and the level design).
information: none retrieved; every input is a file in this repository.
