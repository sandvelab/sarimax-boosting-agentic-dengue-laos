# Provenance — thirty-two conclusions on one axis

```
result:              results/fig_skill_distribution.png
                     results/fig_skill_distribution.csv
script:              scripts/fig_skill_distribution.py
                     sha256:1340160350cb22c1e301b0cdf8db29ff02022afb05c1338e22ffa011eabcd80f
invocation:          "$PYTHON" scripts/fig_skill_distribution.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/05_stability/results/distribution_rows.csv
                     analysis/05_stability/results/distribution.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     matplotlib from the same environment
seeds:               none; a deterministic drawing of stored values.
commit:              9ad6578
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** The phase-D result as a picture, and the one figure in this project
whose subject is the set of analyses rather than the analysis. Each point is one combination
the frozen manifest named, at the skill score that combination concluded; the shaded band is
the reference model's own unseeded re-run spread; the dashed line is the analysis this
project reports.

**The reported line is not in the middle**, and the figure is arranged so that it cannot be
mistaken for a centre: twelve analyses conclude a better skill score than the reported one
and nineteen a worse. Colour is the fork's kind, and the reading it forces is that the
orange block — every choice made *inside* a candidate family — is packed inside the noise
band, while the points that scatter are the ones that change which model is ours or how the
mean is weighted.

**No pre-aggregation file, and that is not an omission.** Each point is one stored
conclusion, not a summary of several; the values those conclusions aggregate are the
per-cell scores under `04_score/01_collect/results/<combination>/metrics_cell.csv`, which
each conclusion file names and which no axis here averages. Rule 7 asks for the values
behind a summary, and this figure summarises nothing that the plotted file does not already
contain one row per.

alternatives-considered: a histogram of the thirty-two skill scores — rejected, because
binning thirty-two values loses which analysis each one is, and which analysis is the whole
content: the interesting fact about −0.0724 is that it is candidate 1, not that some
analysis reached it. A box plot for the same reason, with the additional objection that a
box plot asserts the set is a sample.

agency: agent-autonomous.
information: agent-retrieved — plotted from the two files named above.

---

## The phase-E half (batch 16)

```
result:              results/holdout_fig_skill_distribution.png
                     results/holdout_fig_skill_distribution.csv
script:              scripts/fig_skill_distribution.py
                     sha256:6256e74d89ab60d7afd82f514ae366025bbdd2c6fc786d23dbf1983a64a2279d
invocation:          "$PYTHON" scripts/fig_skill_distribution.py --dataset holdout
inputs:              analysis/05_stability/results/holdout_distribution_rows.csv
                     analysis/05_stability/results/holdout_distribution.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              609e1be
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: draw both datasets on one axis. Rejected: the skill scores are
                     comparable, but one cloud would read as a spread across analyses when
                     half of it is a spread across years. The paired figure is where the two
                     meet, one point per analysis.
agency:              agent-autonomous.
```

**What it establishes.** The same figure on the held-out year: 32 analyses, the reported one
eighteenth, six points below zero where development had none, and the band a third narrower.
The title now names the dataset and counts the analyses from the file rather than stating a
number.


---

## Batch 23 — the digest of the refactor, and the re-draw that verifies it

```
result:              results/fig_skill_distribution.png
                     results/fig_skill_distribution.csv
                     results/holdout_fig_skill_distribution.png
                     results/holdout_fig_skill_distribution.csv
script:              scripts/fig_skill_distribution.py
                     sha256:fdb776d1b325cf6cd28fe824294b0e4f653b958bf17ef330440a0a84bf087ba6
                     scripts/holdout_fig_skill_distribution.py
                     sha256:6ce0bc953496552b3ac35509b17cd49768150d52b28c5111d4d279c89e51be0f
                     scripts/lib/stability_figures.py
                     sha256:def0bc4a1c2fa9a82d5e73dd9fb3541b5b38dd79ca8bfcfcecdae4f63852ae69
invocation:          "$PYTHON" scripts/fig_skill_distribution.py
                     "$PYTHON" scripts/holdout_fig_skill_distribution.py
                     (from 05_stability/, via run.sh — the development figure in the
                     phase-D block, the held-out one in the phase-E block)
inputs:              unchanged from the section(s) above
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              48edaea
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31; recorded and re-verified 2026-09-01
```

**What changed in the script.** Batch 16 moved the drawing into
`scripts/lib/stability_figures.py`, because the same figure is drawn for the held-out year by
`holdout_fig_skill_distribution.py` and a copy per dataset is a copy that will drift. What is
left here is a one-screen runner; what the figure shows, and why each of its reference lines
is there, moved into that module's docstring with it.

**When it changed, and what that left standing.** The development figure — thirty-two
conclusions on one axis, the reported one thirteenth, against a band that is the reference's
own re-run noise — was drawn at `895a9f8`, *before* the refactor, and the refactor at
`48edaea` did not re-draw it. So the file on disk had been produced by a version of the script that no longer existed,
and the record named a third version again — this script is recorded in two sections and
was stale in both.

**Re-drawn, and byte-identical.** This batch ran `scripts/fig_skill_distribution.py` under
the pinned environment and `git status` reported no change — the PNG and the CSV alike. So the
refactor is output-identical where it matters most, on the figure that was already archived,
and the file on disk is now one this version of the script has actually produced rather than
one it is asserted to reproduce. The library is hashed beside the runner, because the runner
is five lines and everything the figure is lives in the library.

**And the phase-E half above is attributed to a script that no longer draws it.** That
section records `holdout_fig_skill_distribution.png` as the output of
`scripts/fig_skill_distribution.py --dataset holdout`. The refactor removed that flag and
gave the held-out figure its own runner, `scripts/holdout_fig_skill_distribution.py`, which
no section named until this one — so the digest block above carries both runners and the library they share. The
`hashes` invariant does not catch this on its own: it checks the files a record hashes, and a
result attributed to the wrong script is `check_provenance`'s question, which is satisfied
because the file *is* named. Two checks passing and the record still misleading is the same
gap batch 18 wrote up, one layer down.

alternatives-considered: recording the gap without re-drawing, as the root conclusion's
section does. Rejected here because the cost is different: a figure is drawn from stored
values in under a second, nothing upstream is re-run, and the result is evidence rather than
an argument. Where re-running would have meant re-running an analysis, this batch did not.

agency: agent-autonomous.
information: agent-retrieved — the digests are computed from the files, the change read from
the diff at `48edaea`, and the byte-identity from the re-draw this batch performed.
