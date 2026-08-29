"""The one implementation of the headline mean, shared by every child of the weighting fork.

`02_aggregate` asks over what weighting the headline mean is taken, and its three children
answer it differently: every cell counts once, cells count in proportion to the people they
describe, or cells count in proportion to the cases observed in them. Those are three
weight vectors over one file. They are not three summaries computed three ways, and this
module exists so that they cannot become that.

It sits in `04_score/scripts/lib/` for the reason `03_models/scripts/lib/chap_eval.py`
sits where it does: a library is not a step -- `node.py` does not put a subdirectory of
`scripts/` into any node's `run.sh` -- and a copy per child is a set of copies that will
drift. The children are one-screen runners that say which weight they use and nothing
else, which is also what makes the fork readable: the diff between two children of this
fork is the weight and the reason for it.

**The unweighted case is not "weights of one".** It is the plain `groupby` mean, kept as
its own code path. Weighting by a vector of ones and taking the mean are the same number
in arithmetic and not always the same float, and `a_unweighted` produced the project's
reported result before this module existed. Its output has to stay byte-identical across
this refactor, and the check is git rather than an argument.

**What a weight is attached to.** Weights are a property of a cell -- a province in a
month -- not of a model, so every model is summarised over the same weights and the
comparison between two models is not a comparison of two weightings. A cell whose weight
is zero contributes nothing; a group all of whose weights are zero has no weighted mean
and is reported as missing rather than as zero.

Writes, under the calling node's results/$COMBO/:
  metrics_summary.csv        one row per model -- the headline figures
  crps_by_location.csv       per province, where the aggregate hides the most
  crps_by_split.csv          per backtest split
  crps_by_region_split.csv   per province and split, which is what a paired test needs
  crps_by_horizon.csv        per lead time
  weights.csv                the weight of every cell, and where it came from  (weighted
                             children only -- there is nothing to record for a mean)
  weighting_notes.json       what the weighting concentrated, and what it emptied
                             (weighted children only)
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

CELL_KEYS = ["location", "time_period"]

# One row per (model, ...) group; the value columns and how each is summarised.
VALUE_COLUMNS = {
    "mean_crps": "crps",
    "mae": "abs_error",
    "coverage_10_90": "in_10_90",
    "coverage_25_75": "in_25_75",
}


def cells_for(node: Path, combo: str) -> pd.DataFrame:
    """The per-cell scores this node's fork aggregates, from `01_collect`."""
    source = node.parents[1] / "01_collect" / "results" / combo / "metrics_cell.csv"
    return pd.read_csv(source, dtype={"time_period": str, "split_first_period": str})


def _weighted(frame: pd.DataFrame, keys: list[str], columns: dict[str, str],
              extra: dict[str, tuple[str, str]]) -> pd.DataFrame:
    """Weighted means of `columns` by `keys`, plus the plain aggregations in `extra`."""
    out = frame.groupby(keys, as_index=False).agg(
        **{name: (column, aggregation) for name, (column, aggregation) in extra.items()})
    totals = frame.groupby(keys)["weight"].sum()
    for name, column in columns.items():
        products = frame.assign(_p=frame[column] * frame["weight"]).groupby(keys)["_p"].sum()
        out[name] = (products / totals.where(totals != 0)).reset_index(drop=True)
    return out


def write(node: Path, combo: str, weighting: str, weights: pd.DataFrame | None,
          weight_basis: str = "") -> pd.DataFrame:
    """Aggregate `01_collect`'s per-cell file and write this child's five tables.

    `weights` is `None` for the unweighted child, or a frame of `location`,
    `time_period`, `weight` for a weighted one. Cells the weight frame does not name are
    an error rather than a silent drop: a weighting that cannot say what a cell is worth
    has not been specified for this dataset.
    """
    out = node / "results" / combo
    out.mkdir(parents=True, exist_ok=True)
    cells = cells_for(node, combo)

    if weights is None:
        summary = cells.groupby("model", as_index=False).agg(
            n_cells=("crps", "size"),
            mean_crps=("crps", "mean"),
            mae=("abs_error", "mean"),
            coverage_10_90=("in_10_90", "mean"),
            coverage_25_75=("in_25_75", "mean"),
            n_locations=("location", "nunique"),
            n_splits=("split_first_period", "nunique"),
            observed_total=("observed", "sum"),
        )
        resolutions = {
            "crps_by_location": cells.groupby(["model", "location"], as_index=False).agg(
                n_cells=("crps", "size"), mean_crps=("crps", "mean"),
                mae=("abs_error", "mean"), coverage_10_90=("in_10_90", "mean"),
                coverage_25_75=("in_25_75", "mean"), observed_total=("observed", "sum")),
            "crps_by_split": cells.groupby(
                ["model", "split_first_period"], as_index=False).agg(
                n_cells=("crps", "size"), mean_crps=("crps", "mean")),
            "crps_by_region_split": cells.groupby(
                ["model", "location", "split_first_period"], as_index=False).agg(
                n_cells=("crps", "size"), mean_crps=("crps", "mean")),
            "crps_by_horizon": cells.groupby(
                ["model", "horizon_distance"], as_index=False).agg(
                n_cells=("crps", "size"), mean_crps=("crps", "mean")),
        }
    else:
        merged = cells.merge(weights, on=CELL_KEYS, how="left")
        unweighted_cells = merged[merged["weight"].isna()]
        if len(unweighted_cells):
            missing = unweighted_cells[CELL_KEYS].drop_duplicates()
            raise SystemExit(
                f"{len(missing)} scored cells have no weight under the {weighting!r} "
                f"weighting, for example {missing.head(3).to_dict('records')}. A "
                f"weighting that cannot price a cell is not specified for this dataset.")

        summary = _weighted(
            merged, ["model"], VALUE_COLUMNS,
            {"n_cells": ("crps", "size"), "n_locations": ("location", "nunique"),
             "n_splits": ("split_first_period", "nunique"),
             "observed_total": ("observed", "sum")})
        summary = summary[["model", "n_cells", "mean_crps", "mae", "coverage_10_90",
                           "coverage_25_75", "n_locations", "n_splits", "observed_total"]]
        resolutions = {
            "crps_by_location": _weighted(
                merged, ["model", "location"],
                VALUE_COLUMNS, {"n_cells": ("crps", "size"),
                                "observed_total": ("observed", "sum")})[
                ["model", "location", "n_cells", "mean_crps", "mae", "coverage_10_90",
                 "coverage_25_75", "observed_total"]],
            "crps_by_split": _weighted(
                merged, ["model", "split_first_period"], {"mean_crps": "crps"},
                {"n_cells": ("crps", "size")}),
            "crps_by_region_split": _weighted(
                merged, ["model", "location", "split_first_period"], {"mean_crps": "crps"},
                {"n_cells": ("crps", "size")}),
            "crps_by_horizon": _weighted(
                merged, ["model", "horizon_distance"], {"mean_crps": "crps"},
                {"n_cells": ("crps", "size")}),
        }

        cell_weights = merged[[*CELL_KEYS, "weight"]].drop_duplicates().sort_values(CELL_KEYS)
        cell_weights.insert(0, "weighting", weighting)
        cell_weights.to_csv(out / "weights.csv", index=False)

        # What the weighting did, in the terms a reader would want to check it on: how
        # concentrated the weight is, and how much of the cell set it silences.
        share = (cell_weights["weight"] / cell_weights["weight"].sum()).sort_values(
            ascending=False)
        by_location = (cell_weights.groupby("location")["weight"].sum()
                       / cell_weights["weight"].sum()).sort_values(ascending=False)
        notes = {
            "combo": combo,
            "weighting": weighting,
            "weight_basis": weight_basis,
            "n_cells": int(len(cell_weights)),
            "weight_total": float(cell_weights["weight"].sum()),
            "cells_with_zero_weight": int((cell_weights["weight"] == 0).sum()),
            "effective_sample_size_kish": float(
                cell_weights["weight"].sum() ** 2 / (cell_weights["weight"] ** 2).sum()),
            "share_of_weight_in_largest_cell": float(share.iloc[0]),
            "share_of_weight_in_top_decile_of_cells": float(
                share.head(max(1, len(share) // 10)).sum()),
            "share_of_weight_by_location": {k: float(v) for k, v in by_location.items()},
            "groups_with_no_weight": {
                name: int(frame["mean_crps"].isna().sum())
                for name, frame in resolutions.items() if "mean_crps" in frame},
        }
        (out / "weighting_notes.json").write_text(
            json.dumps(notes, indent=1, sort_keys=True) + "\n")

    summary.insert(1, "weighting", weighting)
    summary.sort_values("mean_crps").to_csv(out / "metrics_summary.csv", index=False)
    for name, frame in resolutions.items():
        frame.insert(1, "weighting", weighting)
        frame.to_csv(out / f"{name}.csv", index=False)

    best = summary.sort_values("mean_crps").iloc[0]
    print(f"aggregate/{node.name}[{combo}]: {len(summary)} models over "
          f"{int(best.n_cells)} cells, {weighting}; "
          f"best {best.model} at CRPS {best.mean_crps:.3f}")
    return summary
