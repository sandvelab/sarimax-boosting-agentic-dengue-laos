"""The two ranked figures of this node, each drawn for either dataset.

Both are drawn twice — once for the development perturbation set and once for the frozen
phase-E set on the held-out year — from the same rows under different names. The drawing
therefore lives here and the steps are one-screen runners, which is the shape this project
already uses for `chap eval` at `03_models/scripts/lib/chap_eval.py` and for the same
reason: a copy per dataset is a copy that will drift, and the whole point of the two
figures is that they are the same figure.

Each dataset is judged against **its own** noise band, read from that dataset's
`distribution.json`. The reference model is unseeded and was re-scored four times on each,
so the band is a measurement of that dataset and importing one into the other would let one
analysis decide what counts as a move in another.

Not a step: `scripts/lib/` is a subdirectory, so `node.py` does not put it in any node's
`run.sh`, and `check_invariants` does not look for a figure named after it. The steps are
`fig_skill_distribution.py`, `holdout_fig_skill_distribution.py`,
`fig_fork_sensitivity.py` and `holdout_fig_fork_sensitivity.py`, and each writes the
plotted values beside its image.

Seeds: none.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "lib"))
from palette import assign, PALETTE  # noqa: E402

RESULTS = Path(__file__).resolve().parents[2] / "results"


def _load(prefix: str, name: str) -> list[dict]:
    with (RESULTS / f"{prefix}{name}").open() as handle:
        return list(csv.DictReader(handle))


def _summary(prefix: str) -> dict:
    return json.loads((RESULTS / f"{prefix}distribution.json").read_text())


def skill_distribution(dataset: str) -> None:
    """Every analysis the manifest named, on one axis, with the reported one marked.

    Thirty-two conclusions, each from an analysis that looked as reasonable as the one
    this project reports, ranked by the number the project reports. Three reference lines
    carry the reading.

    **Zero** is where our model and the reference model score the same. A point above it
    is an analysis in which we beat the reference; the question the project asks is not
    where the best point is but how many are on which side.

    **The main path** is a line, not a highlight, because it is one member of the set and
    not its centre — thirteenth of thirty-two on development, eighteenth on the holdout,
    which is the fact a single headline number would hide.

    **The band** is the reference's own re-run noise on *this* dataset, measured rather
    than assumed: the reference model is unseeded and was scored four times, and the band
    spans our model's skill score against each of those four. A point inside it differs
    from the main path by less than the reference's sampler moves it on its own.

    Colour is the fork's kind, which is what the figure is really about: the block that
    scatters is the one that changes which model is ours, and the block that does not is
    the one phase C spent three batches choosing inside.

    Plotted values: results/[holdout_]fig_skill_distribution.csv -- one row per point.
    Pre-aggregation: none. Each point is one stored conclusion, not a summary of several;
    the values these conclusions aggregate are the per-cell scores under
    `04_score/01_collect/results/<combination>/metrics_cell.csv`, which the conclusion
    files name and which no axis here averages.
    """
    holdout = dataset == "holdout"
    prefix = "holdout_" if holdout else ""
    stem = f"{prefix}fig_skill_distribution"
    rows = _load(prefix, "distribution_rows.csv")
    summary = _summary(prefix)
    band = summary["reference_noise_band"]["skill_against_each_repeat"]
    main_skill = summary["reported_conclusion"]["skill_score"]

    shown = [{"combination": r["combination"], "tier": r["tier"], "kind": r["kind"],
              "skill_score": float(r["skill_score"]),
              "delta_skill_vs_main": float(r["delta_skill_vs_main"]),
              "inside_reference_noise_band": r["inside_reference_noise_band"]}
             for r in rows]
    shown.sort(key=lambda r: r["skill_score"])
    with (RESULTS / f"{stem}.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(shown)

    colour = assign(sorted({r["kind"] for r in shown}), PALETTE)

    fig, ax = plt.subplots(figsize=(9.5, 9.0), constrained_layout=True)
    ax.axvspan(min(band), max(band), color="0.85", zorder=0,
               label="the reference's own re-run spread")
    ax.axvline(0.0, color="black", linewidth=1.0, zorder=1)
    ax.axvline(main_skill, color="0.35", linestyle="--", linewidth=1.2, zorder=2)

    for y, row in enumerate(shown):
        ax.scatter(row["skill_score"], y, s=95, color=colour[row["kind"]],
                   marker="D" if row["tier"] == "2" else "o",
                   edgecolor="white", linewidth=1.0, zorder=3)
    ax.set_yticks(range(len(shown)))
    ax.set_yticklabels([r["combination"] for r in shown], fontsize=8)
    ax.set_ylim(-0.8, len(shown) - 0.2)
    ax.set_xlabel("skill score against the reference model,  1 − CRPS(ours) / CRPS(reference)")
    ax.annotate("the reference\nscores the same", (0.0, len(shown) - 0.6), fontsize=8,
                ha="center", va="top", color="black")
    ax.annotate("reported", (main_skill, -0.7), fontsize=8, ha="center", va="bottom",
                color="0.35")
    ax.set_title(f"{len(shown)} analyses that all looked reasonable, on the "
                 f"{'held-out year' if holdout else 'development period'}\n"
                 f"Diamonds move two forks at once; circles move one",
                 fontsize=11, loc="left")
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=c, label=k)
               for k, c in sorted(colour.items())]
    ax.legend(handles=handles, loc="lower right", fontsize=9, frameon=False,
              title="fork kind", title_fontsize=9)
    ax.grid(axis="x", alpha=0.25, zorder=0)

    fig.savefig(RESULTS / f"{stem}.png", dpi=160)
    print(f"{stem}.png -> {RESULTS}")


def fork_sensitivity(dataset: str) -> None:
    """Which judgment calls the conclusion is sensitive to, and which it is not.

    The plan calls this the most valuable single output of the project, and it is one bar
    per fork: how far the reported conclusion moves when that choice is taken differently,
    largest first. Everything below the dashed line moves it by less than the reference
    model's own unseeded re-run noise on this dataset, and is therefore a choice this
    evaluation cannot see.

    Two readings the development ranking makes hard to avoid. The choice of **model
    family** is worth an order of magnitude more than any choice made inside a family --
    so the eleven forks phase C spent three batches selecting among sit below the line
    together. And the largest move that touches no model at all is **how the headline mean
    is weighted**, which re-runs nothing and re-aggregates a stored file.

    On the held-out year the ranking is reordered, and `fig_fork_sensitivity_both` is
    where the two are put side by side.

    Plotted values: results/[holdout_]fig_fork_sensitivity.csv -- one row per bar.
    Pre-aggregation: results/[holdout_]fig_fork_sensitivity_preaggregation.csv -- the
    per-combination moves each bar takes a maximum over, so a fork whose two children
    disagree can be seen to.
    """
    holdout = dataset == "holdout"
    prefix = "holdout_" if holdout else ""
    stem = f"{prefix}fig_fork_sensitivity"
    forks = _load(prefix, "sensitivity_by_fork.csv")
    analyses = _load(prefix, "distribution_rows.csv")
    summary = _summary(prefix)
    floor = summary["reference_noise_band"]["skill_band"]

    shown = [{"fork": f["fork"], "stage": f["stage"], "kind": f["kind"],
              "owner": f["owner"],
              "largest_abs_delta_skill": float(f["largest_abs_delta_skill"]),
              "signed_delta_skill": float(f["signed_delta_skill"]),
              "largest_move_combination": f["largest_move_combination"],
              "moves_more_than_reference_noise": f["moves_more_than_reference_noise"],
              "sensitivity_rank": f["sensitivity_rank"]}
             for f in forks if f["largest_abs_delta_skill"] != ""]
    shown.sort(key=lambda f: f["largest_abs_delta_skill"])
    with (RESULTS / f"{stem}.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(shown[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(shown)

    # The per-row moves behind each bar: every tier-1 analysis, keyed by the fork it moved.
    pre = [{"fork": r["fork"], "combination": r["combination"], "child": r["child"],
            "kind": r["kind"], "delta_skill_vs_main": r["delta_skill_vs_main"]}
           for r in analyses if r["tier"] == "1" and r["fork"] != "-"]
    pre.sort(key=lambda r: (r["fork"], r["combination"]))
    with (RESULTS / f"{stem}_preaggregation.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pre[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(pre)

    behind = {}
    for row in pre:
        behind.setdefault(row["fork"], []).append(float(row["delta_skill_vs_main"]))

    colour = assign(sorted({f["kind"] for f in shown}), PALETTE)

    fig, ax = plt.subplots(figsize=(9.5, 6.4), constrained_layout=True)
    positions = range(len(shown))
    ax.barh(list(positions), [f["largest_abs_delta_skill"] for f in shown],
            color=[colour[f["kind"]] for f in shown], height=0.66, zorder=3)
    for y, entry in enumerate(shown):
        for value in behind.get(entry["fork"], []):
            ax.scatter(abs(value), y, s=16, color="white", edgecolor="0.25",
                       linewidth=0.8, zorder=4)
    ax.axvline(floor, color="black", linestyle="--", linewidth=1.2, zorder=5)
    ax.annotate("  the reference's own re-run noise", (floor, -0.4), fontsize=8.5,
                rotation=90, ha="left", va="bottom")
    ax.set_yticks(list(positions))
    ax.set_yticklabels([f"{f['stage']}" + (f"  ({f['owner']})" if f["owner"] != "-" else "")
                        for f in shown], fontsize=9)
    ax.set_xlabel("largest move in the reported skill score when this fork is taken differently")
    # Counted from the bars, not stated. The figure has to say the same thing on both
    # datasets, and a number in a title that nothing computes is exactly the transcription
    # `AGENTS.md` §1 is about.
    above = sum(1 for f in shown if f["moves_more_than_reference_noise"] == "True")
    ax.set_title(f"{above} of {len(shown)} judgment calls move the conclusion\n"
                 f"further than the reference model moves on its own, on the "
                 f"{'held-out year' if holdout else 'development period'}",
                 fontsize=11, loc="left")
    handles = [plt.Line2D([], [], marker="s", linestyle="", color=c, label=k)
               for k, c in sorted(colour.items())]
    handles.append(plt.Line2D([], [], marker="o", linestyle="", color="white",
                              markeredgecolor="0.25", label="one child of the fork"))
    ax.legend(handles=handles, loc="lower right", fontsize=9, frameon=False,
              title="fork kind", title_fontsize=9)
    ax.grid(axis="x", alpha=0.25, zorder=0)

    fig.savefig(RESULTS / f"{stem}.png", dpi=160)
    print(f"{stem}.png -> {RESULTS}")
