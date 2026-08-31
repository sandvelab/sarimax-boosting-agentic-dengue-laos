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
