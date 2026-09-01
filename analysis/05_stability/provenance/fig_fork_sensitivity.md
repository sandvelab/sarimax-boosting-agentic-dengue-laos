# Provenance — which judgment calls the conclusion is sensitive to

```
result:              results/fig_fork_sensitivity.png
                     results/fig_fork_sensitivity.csv
                     results/fig_fork_sensitivity_preaggregation.csv
script:              scripts/fig_fork_sensitivity.py
                     sha256:947d5889d93a5b8113c4e53ea1ee9e9433f8a487349e6e5fc781772e0e15d77b
invocation:          "$PYTHON" scripts/fig_fork_sensitivity.py
                     (from 05_stability/, via run.sh; PYTHON is
                     environment/chapenv/bin/python)
inputs:              analysis/05_stability/results/sensitivity_by_fork.csv
                     analysis/05_stability/results/distribution_rows.csv
                     analysis/05_stability/results/distribution.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0,
                     matplotlib from the same environment
seeds:               none; a deterministic drawing of stored values.
commit:              9ad6578
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
```

**What it establishes.** One bar per fork, ranked by how far the reported conclusion moves
when that choice is taken differently, against a dashed line at the reference model's own
re-run noise. The plan calls this the most valuable single output of the project and it is
the figure the manuscript's stability section is written from.

**Six bars clear the line and eleven do not.** The two largest are the model family and the
pool's own weighting, and the gap between the family bar and the largest fork inside a
family is a factor of twenty-seven. The third is the weighting of the headline mean, which
re-runs no model at all: it re-aggregates a stored file in thirteen seconds and moves the
conclusion four times as far as any of the five `02_setup` forks that re-run everything.

**The open circles are the fork's individual children**, so a bar taken over two or three
children shows which one the maximum came from and how far the others fell short. The
`provinces` fork has two and they differ by half the bar; `population` under `a_hierNB` has
two that are indistinguishable at this scale, which is the finding for that fork.

**Pre-aggregation** is `fig_fork_sensitivity_preaggregation.csv`: every tier-1 analysis's own
move, keyed by the fork it moved, which is the set each bar takes a maximum over. Tier-2 rows
are deliberately absent from it — a pair moves two forks and its move cannot be attributed to
either, which is what `fig_pair_interaction` is for.

alternatives-considered: **ranking forks by the span across their children rather than by
the largest absolute move** — rejected, because the conclusion the project reports is one
number and the question is how far *that* number moves, not how far the children spread
around each other; the span is carried in `sensitivity_by_fork.csv` as
`skill_span_over_children` for the reader who wants it. **Signed rather than absolute bars**
— rejected for the ranking, because a fork that moves the conclusion down by 0.03 and one
that moves it up by 0.03 are equally strong evidence about stability; the sign is in the
data file and in `sensitivity_by_fork.csv`.

agency: agent-autonomous.
information: agent-retrieved — plotted from the three files named above.

---

## The phase-E half (batch 16)

```
result:              results/holdout_fig_fork_sensitivity.png
                     results/holdout_fig_fork_sensitivity.csv
                     results/holdout_fig_fork_sensitivity_preaggregation.csv
script:              scripts/fig_fork_sensitivity.py
                     sha256:cfd1a61597187a74fb9a665bc0cd39c2845b2ada94985850f1dcec0ce002cd0c
invocation:          "$PYTHON" scripts/fig_fork_sensitivity.py --dataset holdout
inputs:              analysis/05_stability/results/holdout_sensitivity_by_fork.csv
                     analysis/05_stability/results/holdout_distribution_rows.csv
                     analysis/05_stability/results/holdout_distribution.json
environment:         environment/ (project main) — CPython 3.13.0, chap-core==2.1.0
seeds:               none.
commit:              609e1be
instructions-commit: cf97b81
node:                analysis/05_stability
produced:            2026-08-31
alternatives-considered: none for the method. The title's count is now computed from the
                     bars rather than written into the string, because the figure has to say
                     the same thing on both datasets and a number nothing computes is the
                     transcription AGENTS.md §1 is about. The development figure's title
                     changed with it, from "Six of seventeen" to the same count read from
                     the file.
agency:              agent-autonomous.
```

**What it establishes.** Five of seventeen forks clear the holdout's own band, against six
on development, and the ranking is reordered: the province filter is first at 0.2696 where
it was fourth at 0.0376.


---

## Batch 23 — the digest of the refactor, and the re-draw that verifies it

```
result:              results/fig_fork_sensitivity.png
                     results/fig_fork_sensitivity.csv
                     results/holdout_fig_fork_sensitivity.png
                     results/holdout_fig_fork_sensitivity.csv
script:              scripts/fig_fork_sensitivity.py
                     sha256:1bd39712d658218907c52eb5559c04a141e72dcf65579082f45d2b9b44dce65c
                     scripts/holdout_fig_fork_sensitivity.py
                     sha256:a81d104be1909e1dd0be3a6b35a07c33af948213615f0c73052d66d0211272fb
                     scripts/lib/stability_figures.py
                     sha256:def0bc4a1c2fa9a82d5e73dd9fb3541b5b38dd79ca8bfcfcecdae4f63852ae69
invocation:          "$PYTHON" scripts/fig_fork_sensitivity.py
                     "$PYTHON" scripts/holdout_fig_fork_sensitivity.py
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
`holdout_fig_fork_sensitivity.py` and a copy per dataset is a copy that will drift. What is
left here is a one-screen runner; what the figure shows, and why each of its reference lines
is there, moved into that module's docstring with it.

**When it changed, and what that left standing.** The development figure — how far each of
the seventeen forks moves the conclusion, against the same measured band — was drawn at
`895a9f8`, *before* the refactor, and the refactor at `48edaea` did not re-draw it. So the file on disk had been produced by a version of the script that no longer existed,
and the record named a third version again — this script is recorded in two sections and
was stale in both.

**Re-drawn, and byte-identical.** This batch ran `scripts/fig_fork_sensitivity.py` under
the pinned environment and `git status` reported no change — the PNG and the CSV alike. So the
refactor is output-identical where it matters most, on the figure that was already archived,
and the file on disk is now one this version of the script has actually produced rather than
one it is asserted to reproduce. The library is hashed beside the runner, because the runner
is five lines and everything the figure is lives in the library.

**And the phase-E half above is attributed to a script that no longer draws it.** That
section records `holdout_fig_fork_sensitivity.png` as the output of
`scripts/fig_fork_sensitivity.py --dataset holdout`. The refactor removed that flag and gave
the held-out figure its own runner, `scripts/holdout_fig_fork_sensitivity.py`, which no
section named until this one — so the digest block above carries both runners and the library they share. The
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
