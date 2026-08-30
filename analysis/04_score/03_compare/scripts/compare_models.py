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

**Every one of them is taken under the weighting the fork at `02_aggregate` chose**, which
is read off that child's own `weights.csv`. The leaderboard here has always followed the
fork, because it is that child's summary; the paired figures did not, so a weighted row
reported a weighted mean CRPS with an unweighted difference and standard error beside it
and nothing in the file said so. Two weightings in one conclusion is not a comparison, and
it is the same objection §4b already records against a fork that moves one side of one.

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


def weighting(summary_path: Path) -> tuple[str, pd.DataFrame | None]:
    """The weighting the headline mean is taken over, and the cell weights behind it.

    The leaderboard on this node is the summary that child produced, so its mean already
    follows the fork. Until batch 14 the **paired** comparison beside it did not: it
    averaged the per-cell differences with every cell counting once, whatever the fork
    said. On a weighted row `conclusion.json` then reported a weighted CRPS and an
    unweighted mean difference and standard error against it -- two weightings in one
    conclusion, and the reader has no way to see it from the file.

    The weights are read from the child's own `weights.csv` rather than recomputed here,
    for the reason `04_score/scripts/lib/aggregate.py` gives for having one
    implementation: a second place that knew what a cell is worth is a second place that
    can be wrong about it. The unweighted child writes no such file -- there is nothing
    to record for a plain mean -- and that absence is what selects the unweighted path.
    """
    name = str(pd.read_csv(summary_path)["weighting"].iloc[0])
    weights_path = summary_path.parent / "weights.csv"
    if not weights_path.exists():
        return name, None
    frame = pd.read_csv(weights_path, dtype={"time_period": str})
    return name, frame[["location", "time_period", "weight"]]


def wmean(frame: pd.DataFrame, column: str) -> float:
    """The mean of `column` over the cells of `frame`, under this row's weighting.

    **Unweighted is its own code path, not weights of one.** It is the same argument
    `aggregate.py` makes one node over: weighting by a vector of ones and taking a mean
    are the same number in arithmetic and not always the same float, and these are the
    figures the project reports.
    """
    if "weight" not in frame:
        return float(frame[column].mean())
    return float((frame[column] * frame["weight"]).sum() / frame["weight"].sum())


def wvar(frame: pd.DataFrame, column: str, mean: float) -> tuple[float, float, float]:
    """Weighted variance of `column`, with the two totals the standard errors need.

    Weights are reliability weights -- a cell's weight says how much of the headline mean
    it carries, not how many observations it stands for -- so the variance is
    `Σw(x−μ)² / (Σw − Σw²/Σw)`, which is algebraically the `ddof=1` sample variance when
    every weight is one. Returned with `Σw` and `Σw²` because the naive standard error is
    built from all three.
    """
    w = frame["weight"]
    total, square = float(w.sum()), float((w ** 2).sum())
    residual = float((w * (frame[column] - mean) ** 2).sum())
    return residual / (total - square / total), total, square


def clustered_se(differences: pd.DataFrame, by: str, mean: float) -> float:
    """Standard error of the mean paired difference, clustering on `by`.

    Cells inside a cluster may be correlated in any way; between clusters they are
    treated as independent. With sixteen provinces or eight splits this is a small
    number of clusters and the figure is indicative rather than exact -- which is why
    the split-level comparison is reported beside it.

    Weighted, this is the same estimator with each cell's residual scaled by its weight
    and the denominator the total weight rather than the cell count; with every weight
    one it is the expression it has always been.
    """
    frame = differences
    if "weight" not in frame:
        groups = frame.groupby(by)["diff"]
        totals, sizes = groups.sum(), groups.size()
        n = int(sizes.sum())
        residuals = totals - sizes * mean
        return float(np.sqrt((residuals ** 2).sum()) / n) if n else float("nan")
    scaled = frame["weight"] * (frame["diff"] - mean)
    residuals = scaled.groupby(frame[by]).sum()
    total = float(frame["weight"].sum())
    return float(np.sqrt((residuals ** 2).sum()) / total) if total else float("nan")


def paired(cells: pd.DataFrame, model: str, against: str,
           weights: pd.DataFrame | None, name: str) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """One model against one other, cell by cell, under this row's weighting.

    Within a split the cells carry their weights, so a split's number sits on the same
    footing as the headline mean. **Across splits the eight numbers count equally**, as
    they always have: the splits are the replicate units of the split-level comparison,
    which is the figure that assumes nothing about independence within a split, and
    weighting them by their totals would turn it back into the cell-level statistic it
    exists to stand beside.
    """
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

    if weights is not None:
        frame = frame.merge(weights, on=["location", "time_period"], how="left")
        unpriced = frame[frame["weight"].isna()]
        if len(unpriced):
            raise SystemExit(
                f"{len(unpriced)} paired cells have no weight under the {name!r} "
                f"weighting; 02_aggregate priced a different cell set than 01_collect "
                f"produced, and the comparison would silently drop them.")

    if weights is None:
        by_split = frame.groupby("split_first_period", as_index=False).agg(
            n_cells=("diff", "size"), mean_diff=("diff", "mean"),
            crps_model=("crps_model", "mean"), crps_against=("crps_against", "mean"))
    else:
        by_split = frame.groupby("split_first_period", as_index=False).agg(
            n_cells=("diff", "size"), weight=("weight", "sum"))
        for column in ("diff", "crps_model", "crps_against"):
            products = frame.assign(_p=frame[column] * frame["weight"]).groupby(
                "split_first_period")["_p"].sum()
            by_split["mean_diff" if column == "diff" else column] = (
                products / by_split.set_index("split_first_period")["weight"]).to_numpy()
        by_split = by_split[["split_first_period", "n_cells", "mean_diff",
                             "crps_model", "crps_against"]]
    by_split.insert(0, "weighting", name)
    by_split.insert(0, "against", against)
    by_split.insert(0, "model", model)

    mean_diff = wmean(frame, "diff")
    if weights is None:
        sd = float(frame["diff"].std(ddof=1))
        se_naive = float(sd / np.sqrt(len(frame)))
    else:
        variance, total_weight, square_weight = wvar(frame, "diff", mean_diff)
        sd = float(np.sqrt(variance))
        se_naive = float(sd * np.sqrt(square_weight) / total_weight)

    n_splits = len(by_split)
    summary = {
        "model": model,
        "against": against,
        "weighting": name,
        "n_cells": int(len(frame)),
        "mean_crps_model": wmean(frame, "crps_model"),
        "mean_crps_against": wmean(frame, "crps_against"),
        "mean_diff": mean_diff,
        "skill_score": float(1 - wmean(frame, "crps_model") / wmean(frame, "crps_against")),
        "sd_diff_cell": sd,
        "se_cell_naive": se_naive,
        "se_cluster_location": clustered_se(frame, "location", mean_diff),
        "se_cluster_split": clustered_se(frame, "split_first_period", mean_diff),
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
    aggregated = chosen_aggregate(COMBO)
    summary = pd.read_csv(aggregated)
    # Every figure on this node is taken under the weighting the fork chose, the paired
    # ones included. Read once here and carried into every comparison below.
    weighting_name, weights = weighting(aggregated)

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
            frame, stats, by_split = paired(cells, model, against, weights, weighting_name)
            frames.append(frame)
            summaries.append(stats)
            splits.append(by_split)

    # --- the noise floor: the reference against its own repeats ---------------------
    # Under the same weighting as everything above it, because the floor is what the
    # figures above are read against and a floor in other units cannot be.
    noise = []
    for a, b in itertools.combinations(repeats, 2):
        _, stats, _ = paired(cells, a, b, weights, weighting_name)
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
    reference_cells = cells[cells.model == REFERENCE]
    if weights is not None:
        reference_cells = reference_cells.merge(weights, on=["location", "time_period"],
                                                how="left")
        unpaired = (reference_cells.assign(_p=reference_cells.crps * reference_cells.weight)
                    .groupby("split_first_period")[["_p", "weight"]].sum()
                    .eval("_p / weight"))
    else:
        unpaired = reference_cells.groupby("split_first_period")["crps"].mean()
    notes = {
        "combo": COMBO,
        "weighting": weighting_name,
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
          f"{reference_crps:.3f} over {notes['n_cells']} cells, {weighting_name}")
    for s in against_mean:
        print(f"  {s['model']:14s} diff {s['mean_diff']:+8.3f}  "
              f"se(split-clustered) {s['se_cluster_split']:.3f}  "
              f"skill {s['skill_score']:+.3f}  wins {s['win_rate_cells']:.0%} of cells")
    print(f"  noise floor (reference vs its own repeats): "
          f"largest |mean diff| {floor:.3f}")


if __name__ == "__main__":
    main()
