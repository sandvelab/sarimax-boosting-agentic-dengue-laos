# Clean-room artefacts — 2026-09-04, batch 31

What batch 31's clean-room run of `analysis/run.sh` wrote, copied out of the throwaway clone
before it was discarded. The clone was 18 GB and is gone; these are the files the findings in
`../26-09-04_cleanroom.md` rest on, so the numbers can be re-checked without re-running the
analysis from cold.

This is the run in which **`analysis/run.sh` exited 0** — the whole analysis, both datasets,
from a clean checkout, to the end.

Nothing here is an analysis result. They are one run's outputs, kept as evidence about the
run, and they are **not** the archive — `analysis/05_stability/results/` is. Where a file
here has the same name as one there, the difference between them is the finding.

## What is here

**The development half**

- `manifest.csv`, `manifest_selection.json`, `conclusions.csv`, `run_status.csv`,
  `distribution.json`, `sensitivity_by_fork.csv`, `cost_planned_vs_actual.csv` — the
  clean-room's own stability outputs.
- `manifest_selection_check.json` — batch 26's machinery, after tier 1 re-ran. It says the
  rule *would* now choose six different pairs and that the recorded ones stand. That is the
  disagreement that killed batch 25, reported instead of acted on, for the third time.

**The holdout half**

- `holdout_conclusions.csv`, `run_status_holdout.csv`, `holdout_distribution.json`,
  `holdout_cost_planned_vs_actual.{csv,json}` — 32 held-out analyses scored from cold.
- `holdout_freeze_check.json` — batch 24's check, passing: *the frozen set is intact*.
- `conclusion_main.json`, `conclusion_main__holdout.json` — the two reported paths.

**The three files no clean-room run had written before**

- `holdout_vs_development.json`, `holdout_vs_development.csv`, `fork_sensitivity_both.csv` —
  what `pair_holdout_development.py` produces. Batch 27 exited 1 at that script, so its
  comparison reported these three unchanged when in truth they had never been written. These
  are the first clean-room copies that exist, and `../26-09-04_cleanroomPhaseEAnswer.json` is
  the comparison against the archive.

**The environment**

- `freeze_raw.txt` — what `uv pip freeze` returned in the clone, through batch 27's `freeze()`
  helper. No ANSI escapes, which is the point: the same session had colour forced and the
  comparison still reported an exact match.
- `lock.txt` — the clone's lockfile, for the comparison against it.

**The run itself**

- `run.log`, `harness.log`, `install_env.log`, `run_exit_status.txt` (**0**),
  `run_seconds.txt` (41 677, wall clock on a host held awake by `caffeinate`),
  `cleanroom_head.txt` (`c94e85f…`), `diff_status.txt`, `diff_stat.txt`.

**Two files kept as evidence rather than as outputs**

- `member_selection_provinces_reportingOnly.json` — one of the five `member_selection.json`
  files the clean-room wrote and the archive lacks, because those five setup combinations have
  not been re-run since batch 14 added the file. Nothing computed differs.
- `log_yearVariance_shared.log` — the one row that took 37× its archived duration (3 210.7 s
  against 85.6 s) while producing an identical CRPS of 18.840. Kept because the report says
  the record does not explain it, and a reader should be able to check that.

All of it is regenerable only by re-running the clean-room, and it would not regenerate
identically — the reference model is unseeded, which is the subject of several of the
findings.
