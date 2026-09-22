# Follow-up to the clean-room run

`summary.json` and `differences.txt` are the record of the run as it happened and are not
rewritten. This is what was done about the one genuine difference it found.

**The run.** `analysis/run.sh` completed in the clone in 5,256 s (88 minutes) at exit 0, having
built both environments from nothing. Of 299 tracked result files: **288 byte-identical**, 10
declared-varying (wall-clock logs, run summaries, freeze-check timestamps), **1 genuinely
differing**, 0 missing. Zero tracked inputs differed on checkout — the check that would have
caught this batch's line-ending defect, now passing because `.gitattributes` fixes the bytes.

**The one difference: `distribution_holdout.json`.** Diffed to exactly two fields:

    opening_number:      1   here   /  2   in the clone
    total_wall_seconds:  622.9      /  982.9

Both are true. The clone is a reproduction, and because `run_status_holdout.csv` is tracked, row
1 travels with it and the reproduction writes row 2 — which is the behaviour the tracked/untracked
split was designed for, and which batch 19 had already reworded the runner's note to describe
correctly. **No scientific value differed anywhere in the file**, or in any of the other 288.

**What was fixed.** The report was embedding `run_summary_holdout.json` whole, so a result file
carried a stopwatch. It now embeds the opening's *identity* — phase, main path, manifest digest,
frozen commit, row counts, the four preflight results — and leaves the timings one file away.

**How the fix was verified**, rather than argued: the corrected reporter was run in this tree and
in the clone. It reads only stored files, so neither run reopens the held-out year. The two
`distribution_holdout.json` files are now byte-identical.

**The clone's own invariants** passed on everything except `git`, which failed on the eleven
files the run had just written and not committed — expected, and the same tension `validate.md`
now documents.

**Standing result: the analysis reproduces from nothing.** 289 of 289 comparable results
byte-identical, including all 33 held-out rows, all 26 development stability rows, every
candidate and both baselines.
