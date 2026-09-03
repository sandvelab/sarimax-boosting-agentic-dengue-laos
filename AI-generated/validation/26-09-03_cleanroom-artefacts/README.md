# Clean-room artefacts — 2026-09-03, batch 27

What batch 27's clean-room run of `analysis/run.sh` wrote, copied out of the throwaway clone
before it was discarded. The clone was 18 GB and is gone; these are the files the findings in
`../26-09-03_cleanroom.md` rest on, so the numbers can be re-checked without re-running the
analysis from cold.

Nothing here is an analysis result. They are one run's outputs, kept as evidence about the
run, and they are **not** the archive — `analysis/05_stability/results/` is. Where a file
here has the same name as one there, the difference between them is the finding.

## What is here

**The development half**

- `manifest.csv`, `manifest_selection.json`, `conclusions.csv`, `run_status.csv`,
  `distribution.json`, `cost_planned_vs_actual.csv` — the clean-room's own stability outputs.
  `manifest.csv` carries the recorded eight tier-2 pairs, and differs from the archived copy
  in its two cost columns only, which are measured durations.
- `manifest_selection_check.after_tier1.json` and `manifest_selection_check.json` — batch
  26's machinery, before and after tier 1 re-ran. The second says the rule *would* now choose
  six different pairs and that the recorded ones stand. That is the disagreement that killed
  batch 25, reported instead of acted on.

**The holdout half, from a clean checkout for the first time**

- `holdout_conclusions.csv`, `run_status_holdout.csv`, `holdout_distribution.json`,
  `holdout_cost_planned_vs_actual.{csv,json}` — 32 held-out analyses scored from cold.
- `holdout_freeze_check.json` — batch 24's check, passing: *the frozen set is intact*, 33
  rows, no fatal differences, 32 rows whose numbers drifted.
- `conclusion_main.json`, `conclusion_main__holdout.json` — the two reported paths.

**The environment**

- `freeze_raw.txt` — what `uv pip freeze` returned in the clone, with the ANSI colour codes
  that made `install-chap.sh` report `DOES NOT MATCH`. Kept unedited, escapes and all,
  because the escapes *are* the finding.
- `lock.txt` — the clone's lockfile, for the comparison against it.

**The run itself**

- `run.log`, `harness.log`, `install_env.log`, `run_exit_status.txt` (1),
  `run_seconds.txt` (81 335, wall clock across a host that slept), `cleanroom_head.txt`
  (`80276f3…`), `diff_status.txt`, `diff_stat.txt`.

**One file the archive does not have**

- `member_selection_provinces_reportingOnly.json` — one of five `member_selection.json` files
  the clean-room wrote and the archive lacks, because those five setup combinations have not
  been re-run since batch 14 added the file. Nothing computed differs.

All of it is regenerable only by re-running the clean-room, and it would not regenerate
identically — the reference model is unseeded, which is the subject of several of the
findings.
