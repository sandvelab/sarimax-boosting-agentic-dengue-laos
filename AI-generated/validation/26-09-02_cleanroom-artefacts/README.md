# Clean-room artefacts — 2026-09-02, batch 25

What batch 25's clean-room run of `analysis/run.sh` wrote, copied out of the throwaway clone
before it was discarded. The clone lived in a scratch directory and is gone; these are the
files the findings in `../26-09-02_cleanroom.md` rest on, so that the numbers can be
re-checked without re-running four hours of analysis.

Nothing here is an analysis result. They are one run's outputs, kept as evidence about the
run, and they are **not** the archive — `analysis/05_stability/results/` is. Where a file
here has the same name as one there, the difference between them is the finding.

## What is here

- `conclusions.csv`, `manifest.csv`, `distribution.json`, `run_status.csv` — the clean-room's
  own stability outputs. `manifest.csv` carries the **tier-2 selection this run made**, which
  differs from the archived one in six of eight pairs and is why the run stopped.
- `holdout_freeze_check.json` — the freeze check that ended the run: `9 difference(s) the
  frozen set cannot absorb`. Batch 24's defence working as designed.
- `failedRow_*.log` and `failedRow_fitted_model.json` — the one row that crashed,
  `trainingWindow_from2004__weighting_crpsWeighted`, and the fitted model showing why: the
  weighting **fell back to equal** because the training window was too short to hold back a
  validation block, and `check_pool.py` asked for the validation block anyway. The
  `fitted_model.json` is kept whole rather than trimmed to the relevant block, because a
  trimmed copy would be a file that was edited after it was produced.
- `run.log`, `harness.log`, `install_env.log`, `run_exit_status.txt`, `run_seconds.txt` —
  the run itself: exit 1 after 13 669 s, and the environment reporting that it matched
  `environment/lock.txt` exactly (174 packages).

All of it is regenerable only by re-running the clean-room, and it would not regenerate
identically — the reference model is unseeded, which is the subject of the finding.
