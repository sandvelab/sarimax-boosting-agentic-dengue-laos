"""Compare the models, and say what the comparison can and cannot distinguish.

Two products. The **leaderboard** is one row per model, assembled from the stored scores
and the stored run costs -- never typed, so a model reaches it by having run and no other
way. The **paired comparison** against the reference is the question batch 4 left open and
the reason this node exists before any candidate does.

Why paired. Batch 4 measured the split-to-split standard error of the reference's own CRPS
at 5.65, a quarter of its mean, and observed that a difference between two models would
have to be enormous to clear that. But that variation is mostly the difficulty of the
period, and difficulty is common to both models: 2009-07 is hard for everyone. Comparing
the two models cell by cell removes it. Whether what remains is small enough to separate
two models on 371 cells is not something anyone could answer by argument, so it is
computed here.

Four things are computed, because the naive answer is the wrong one:

  * the mean paired difference and its per-cell standard error, which assumes the 371
    cells are independent and therefore flatters the comparison -- three lead times of the
    same forecast, and neighbouring months of the same province, are not independent;
  * the same standard error clustered by province and by split, which is the honest
    version, because it lets the cells inside a cluster be arbitrarily correlated;
  * the difference computed at the split level, over eight paired numbers, which needs no
    independence assumption within a split at all;
  * **the noise floor**: the same paired statistic computed between two repeats of the
    reference against itself. The reference is unseeded, so re-running it produces a
    different set of forecasts on the identical cells, and the paired difference between
    two of its own repeats is a difference of exactly zero contaminated by nothing but its
    sampler. Whatever that comes to is the smallest difference this comparison can mean
    anything about, in the same units, computed rather than assumed.

No significance test is reported and none is implied. The project's success criterion says
the comparison is reported with its spread and a plain statement of what that spread can
distinguish, and "we cannot separate these two" is one of the answers it can return.

Writes, under results/$COMBO/:
  leaderboard.csv             one row per model
  paired_vs_reference.csv     one row per model per reference variant per cell
  paired_summary.csv          one row per model per reference variant
  paired_by_split.csv         the split-level paired differences behind that summary
  reference_repeat_noise.csv  the noise floor: the reference against its own repeats
  comparison_notes.json       what the above resolves, in machine-readable form
"""

from __future__ import annotations

import itertools
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

NODE = Path(__file__).resolve().parents[1]
SCORE = NODE.parent
COMBO = os.environ.get("COMBO", "main")
REFERENCE = "reference"
CELL_KEYS = ["location", "time_period", "horizon_distance"]


def repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


ROOT = repo_root(NODE)


def chosen_aggregate(combo: str) -> Path:
    """The one child of the weighting fork that ran in this combination."""
    found = sorted((SCORE / "02_aggregate").glob(f"*/results/{combo}/metrics_summary.csv"))
    if len(found) != 1:
        raise SystemExit(
            f"02_aggregate: expected exactly one child with results for combination "
            f"{combo!r}, found {[str(p.relative_to(SCORE)) for p in found]}")
    return found[0]


def clustered_se(differences: pd.DataFrame, by: str) -> float:
    """Standard error of the mean paired difference, clustering on `by`.

    Cells inside a cluster may be correlated in any way; between clusters they are
    treated as independent. With sixteen provinces or eight splits this is a small
    number of clusters and the figure is indicative rather than exact -- which is why
    the split-level comparison is reported beside it.
    """
    groups = differences.groupby(by)["diff"]
    totals, sizes = groups.sum(), groups.size()
    n = int(sizes.sum())
    mean = differences["diff"].mean()
    residuals = totals - sizes * mean
    return float(np.sqrt((residuals ** 2).sum()) / n) if n else float("nan")


def paired(cells: pd.DataFrame, model: str, against: str) -> tuple[pd.DataFrame, dict]:
    left = cells[cells.model == model].set_index(CELL_KEYS)
    right = cells[cells.model == against].set_index(CELL_KEYS)
    common = left.index.intersection(right.index)
    frame = pd.DataFrame({
        "model": model,
        "against": against,
        "crps_model": left.loc[common, "crps"],
        "crps_against": right.loc[common, "crps"],
        "split_first_period": left.loc[common, "split_first_period"],
    }).reset_index()
    frame["diff"] = frame["crps_model"] - frame["crps_against"]

    by_split = frame.groupby("split_first_period", as_index=False).agg(
        n_cells=("diff", "size"), mean_diff=("diff", "mean"),
        crps_model=("crps_model", "mean"), crps_against=("crps_against", "mean"))
    by_split.insert(0, "against", against)
    by_split.insert(0, "model", model)

    n_splits = len(by_split)
    summary = {
        "model": model,
        "against": against,
        "n_cells": int(len(frame)),
        "mean_crps_model": float(frame.crps_model.mean()),
        "mean_crps_against": float(frame.crps_against.mean()),
        "mean_diff": float(frame["diff"].mean()),
        "skill_score": float(1 - frame.crps_model.mean() / frame.crps_against.mean()),
        "sd_diff_cell": float(frame["diff"].std(ddof=1)),
        "se_cell_naive": float(frame["diff"].std(ddof=1) / np.sqrt(len(frame))),
        "se_cluster_location": clustered_se(frame, "location"),
        "se_cluster_split": clustered_se(frame, "split_first_period"),
        "mean_diff_by_split": float(by_split.mean_diff.mean()),
        "se_split_level": float(by_split.mean_diff.std(ddof=1) / np.sqrt(n_splits))
        if n_splits > 1 else float("nan"),
        "cells_model_better": int((frame["diff"] < 0).sum()),
        "cells_model_worse": int((frame["diff"] > 0).sum()),
        "cells_tied": int((frame["diff"] == 0).sum()),
        "splits_model_better": int((by_split.mean_diff < 0).sum()),
        "n_splits": n_splits,
    }
    summary["win_rate_cells"] = summary["cells_model_better"] / summary["n_cells"]
    return frame, summary, by_split


def main() -> None:
    out = NODE / "results" / COMBO
    out.mkdir(parents=True, exist_ok=True)

    collected = SCORE / "01_collect" / "results" / COMBO
    cells = pd.read_csv(collected / "metrics_cell.csv",
                        dtype={"time_period": str, "split_first_period": str})
    models = pd.read_csv(collected / "models.csv").fillna({"repeat_of": ""})
    summary = pd.read_csv(chosen_aggregate(COMBO))

    if REFERENCE not in set(cells.model):
        raise SystemExit(f"no {REFERENCE!r} rows in {collected}/metrics_cell.csv; "
                         f"the comparison this node exists for cannot be made")

    # --- the leaderboard -----------------------------------------------------------
    costs = {}
    for spec_path in sorted((ROOT / "analysis/03_models").glob(f"**/results/{COMBO}/run_cost.json")):
        cost = json.loads(spec_path.read_text())
        costs[cost["model"]] = cost
    board = summary.merge(models[["model", "origin", "kind", "node", "seeded"]],
                          on="model", how="left")
    board["wall_clock_seconds"] = [costs.get(m, {}).get("wall_clock_seconds")
                                   for m in board.model]
    board["seconds_per_split"] = [costs.get(m, {}).get("seconds_per_split")
                                  for m in board.model]
    reference_crps = float(summary.loc[summary.model == REFERENCE, "mean_crps"].iloc[0])
    board["skill_vs_reference"] = 1 - board["mean_crps"] / reference_crps
    board = board.sort_values("mean_crps")
    board.to_csv(out / "leaderboard.csv", index=False)

    # --- the paired comparison -----------------------------------------------------
    repeats = sorted(models.loc[models.repeat_of == REFERENCE, "model"])
    ours = [m for m in board.loc[board.origin == "ours", "model"]]

    frames, summaries, splits = [], [], []
    for model in ours:
        for against in [REFERENCE, *repeats]:
            frame, stats, by_split = paired(cells, model, against)
            frames.append(frame)
            summaries.append(stats)
            splits.append(by_split)

    # --- the noise floor: the reference against its own repeats ---------------------
    noise = []
    for a, b in itertools.combinations(repeats, 2):
        _, stats, _ = paired(cells, a, b)
        noise.append(stats)
    noise_frame = pd.DataFrame(noise)

    pd.concat(frames, ignore_index=True).to_csv(out / "paired_vs_reference.csv", index=False)
    pd.DataFrame(summaries).to_csv(out / "paired_summary.csv", index=False)
    pd.concat(splits, ignore_index=True).to_csv(out / "paired_by_split.csv", index=False)
    noise_frame.to_csv(out / "reference_repeat_noise.csv", index=False)

    # --- what it resolves ------------------------------------------------------------
    floor = float(noise_frame["mean_diff"].abs().max()) if len(noise_frame) else float("nan")
    floor_se = float(noise_frame["se_cluster_split"].max()) if len(noise_frame) else float("nan")
    against_mean = [s for s in summaries if s["against"] == REFERENCE]
    unpaired = cells[cells.model == REFERENCE].groupby("split_first_period")["crps"].mean()
    notes = {
        "combo": COMBO,
        "reference": REFERENCE,
        "reference_repeats": repeats,
        "n_cells": int(against_mean[0]["n_cells"]) if against_mean else 0,
        # The unpaired figure, for comparison with the paired ones above it. Batch 4
        # reported the standard error; both are given here so the two are not confused.
        "unpaired_sd_across_splits_reference": float(unpaired.std(ddof=1)),
        "unpaired_se_across_splits_reference": float(
            unpaired.std(ddof=1) / np.sqrt(len(unpaired))),
        "noise_floor_largest_repeat_pair_mean_diff": floor,
        "noise_floor_largest_repeat_pair_se_cluster_split": floor_se,
        "resolvable_difference_note":
            "The largest mean paired difference between two repeats of the same unseeded "
            "reference model is the size of a difference this comparison cannot attribute "
            "to anything but the reference's own sampler.",
        "models": {s["model"]: {k: s[k] for k in (
            "mean_crps_model", "mean_crps_against", "mean_diff", "skill_score",
            "se_cell_naive", "se_cluster_location", "se_cluster_split", "se_split_level",
            "win_rate_cells", "splits_model_better", "n_splits")}
            for s in against_mean},
    }
    (out / "comparison_notes.json").write_text(json.dumps(notes, indent=1, sort_keys=True) + "\n")

    print(f"compare[{COMBO}]: {len(board)} leaderboard rows; reference CRPS "
          f"{reference_crps:.3f} over {notes['n_cells']} cells")
    for s in against_mean:
        print(f"  {s['model']:14s} diff {s['mean_diff']:+8.3f}  "
              f"se(split-clustered) {s['se_cluster_split']:.3f}  "
              f"skill {s['skill_score']:+.3f}  wins {s['win_rate_cells']:.0%} of cells")
    print(f"  noise floor (reference vs its own repeats): "
          f"largest |mean diff| {floor:.3f}")


if __name__ == "__main__":
    main()
